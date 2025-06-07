"""Database connection pool for better concurrency handling."""

import sqlite3
import threading
import queue
import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class SQLiteConnectionPool:
    """Connection pool for SQLite with better concurrency support."""
    
    def __init__(self, db_path: str, max_connections: int = 10, 
                 timeout: float = 30.0, check_same_thread: bool = False):
        """Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            max_connections: Maximum number of connections in pool
            timeout: Timeout for getting connection from pool
            check_same_thread: SQLite check_same_thread parameter
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        
        # Create data directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connection pool
        self._pool = queue.Queue(maxsize=max_connections)
        self._all_connections = set()
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'connections_created': 0,
            'connections_reused': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'timeouts': 0
        }
        
        # Initialize pool with one connection to test
        self._create_initial_connection()
        
        logger.info(f"SQLite connection pool initialized: {db_path}, max_connections: {max_connections}")
    
    def _create_initial_connection(self):
        """Create initial connection to test database."""
        try:
            conn = self._create_connection()
            self._setup_connection(conn)
            self._pool.put(conn)
            logger.info("Initial database connection created successfully")
        except Exception as e:
            logger.error(f"Failed to create initial database connection: {e}")
            raise
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=self.check_same_thread,
            isolation_level=None  # Autocommit mode for better concurrency
        )
        
        with self._lock:
            self._all_connections.add(conn)
            self.stats['connections_created'] += 1
        
        return conn
    
    def _setup_connection(self, conn: sqlite3.Connection):
        """Setup connection with optimal settings."""
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Optimize for concurrency and performance
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety and speed
        conn.execute("PRAGMA cache_size=10000")  # Larger cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second busy timeout
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup."""
        conn = None
        start_time = time.time()
        
        try:
            # Try to get connection from pool
            try:
                conn = self._pool.get_nowait()
                self.stats['pool_hits'] += 1
                self.stats['connections_reused'] += 1
            except queue.Empty:
                self.stats['pool_misses'] += 1
                
                # Create new connection if under limit
                with self._lock:
                    if len(self._all_connections) < self.max_connections:
                        conn = self._create_connection()
                        self._setup_connection(conn)
                    else:
                        # Wait for connection from pool
                        try:
                            conn = self._pool.get(timeout=self.timeout)
                            self.stats['pool_hits'] += 1
                            self.stats['connections_reused'] += 1
                        except queue.Empty:
                            self.stats['timeouts'] += 1
                            raise TimeoutError(f"Timeout waiting for database connection after {self.timeout}s")
            
            # Test connection
            try:
                conn.execute("SELECT 1")
            except sqlite3.Error:
                # Connection is bad, create new one
                self._close_connection(conn)
                conn = self._create_connection()
                self._setup_connection(conn)
            
            yield conn
            
        finally:
            # Return connection to pool
            if conn:
                try:
                    # Check if connection is still good
                    conn.execute("SELECT 1")
                    self._pool.put_nowait(conn)
                except (sqlite3.Error, queue.Full):
                    # Connection is bad or pool is full, close it
                    self._close_connection(conn)
    
    def _close_connection(self, conn: sqlite3.Connection):
        """Close and remove connection from tracking."""
        try:
            conn.close()
        except Exception:
            pass
        
        with self._lock:
            self._all_connections.discard(conn)
    
    def close_all(self):
        """Close all connections in pool."""
        with self._lock:
            # Close connections in pool
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    self._close_connection(conn)
                except queue.Empty:
                    break
            
            # Close any remaining connections
            for conn in list(self._all_connections):
                self._close_connection(conn)
            
            logger.info("All database connections closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self._lock:
            return {
                **self.stats,
                'active_connections': len(self._all_connections),
                'pool_size': self._pool.qsize(),
                'max_connections': self.max_connections
            }


class DatabaseTransaction:
    """Context manager for database transactions with retry logic."""
    
    def __init__(self, connection_pool: SQLiteConnectionPool, max_retries: int = 3):
        """Initialize transaction manager.
        
        Args:
            connection_pool: Connection pool to use
            max_retries: Maximum number of retries for failed transactions
        """
        self.pool = connection_pool
        self.max_retries = max_retries
        self.conn = None
        self.in_transaction = False
    
    def __enter__(self):
        """Start transaction."""
        for attempt in range(self.max_retries + 1):
            try:
                self.conn = self.pool.get_connection().__enter__()
                self.conn.execute("BEGIN IMMEDIATE")
                self.in_transaction = True
                return self.conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 0.1  # Exponential backoff
                    time.sleep(wait_time)
                    logger.warning(f"Database locked, retrying in {wait_time}s (attempt {attempt + 1})")
                    continue
                else:
                    raise
        
        raise sqlite3.OperationalError("Failed to acquire database lock after retries")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction."""
        if self.conn and self.in_transaction:
            try:
                if exc_type is None:
                    self.conn.execute("COMMIT")
                else:
                    self.conn.execute("ROLLBACK")
            except Exception as e:
                logger.error(f"Error ending transaction: {e}")
                try:
                    self.conn.execute("ROLLBACK")
                except Exception:
                    pass
            finally:
                self.in_transaction = False
                # Connection will be returned to pool by connection manager


class BatchProcessor:
    """Batch processor for efficient database operations."""
    
    def __init__(self, connection_pool: SQLiteConnectionPool, batch_size: int = 1000):
        """Initialize batch processor.
        
        Args:
            connection_pool: Connection pool to use
            batch_size: Number of items to process in each batch
        """
        self.pool = connection_pool
        self.batch_size = batch_size
    
    def execute_batch(self, query: str, data_list: list, 
                     progress_callback: Optional[callable] = None) -> int:
        """Execute query in batches.
        
        Args:
            query: SQL query with placeholders
            data_list: List of data tuples/dicts
            progress_callback: Optional callback for progress updates
            
        Returns:
            Total number of rows affected
        """
        if not data_list:
            return 0
        
        total_affected = 0
        total_batches = (len(data_list) + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(data_list))
            batch_data = data_list[start_idx:end_idx]
            
            with DatabaseTransaction(self.pool) as conn:
                cursor = conn.cursor()
                
                if isinstance(batch_data[0], dict):
                    cursor.executemany(query, batch_data)
                else:
                    cursor.executemany(query, batch_data)
                
                total_affected += cursor.rowcount
            
            if progress_callback:
                progress_callback(batch_num + 1, total_batches, len(batch_data))
        
        return total_affected