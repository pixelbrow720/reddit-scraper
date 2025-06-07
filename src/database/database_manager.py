"""Database management for persistent storage."""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
import threading

from .connection_pool import SQLiteConnectionPool, DatabaseTransaction, BatchProcessor

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for Reddit scraper data."""
    
    def __init__(self, db_path: str = "data/reddit_scraper.db", max_connections: int = 10):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
            max_connections: Maximum number of database connections
        """
        self.db_path = db_path
        
        # Use connection pool for better concurrency
        self.connection_pool = SQLiteConnectionPool(
            db_path=db_path,
            max_connections=max_connections,
            check_same_thread=False  # Allow sharing connections between threads
        )
        
        # Batch processor for efficient operations
        self.batch_processor = BatchProcessor(self.connection_pool)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database manager initialized with database: {db_path}, max_connections: {max_connections}")
    
    def _init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    subreddit TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    upvote_ratio REAL DEFAULT 0.0,
                    num_comments INTEGER DEFAULT 0,
                    created_utc INTEGER NOT NULL,
                    url TEXT,
                    permalink TEXT,
                    selftext TEXT,
                    link_url TEXT,
                    flair TEXT,
                    is_nsfw BOOLEAN DEFAULT FALSE,
                    is_spoiler BOOLEAN DEFAULT FALSE,
                    is_self BOOLEAN DEFAULT FALSE,
                    domain TEXT,
                    content_type TEXT,
                    category TEXT,
                    engagement_ratio REAL DEFAULT 0.0,
                    extracted_content TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_utc INTEGER,
                    comment_karma INTEGER DEFAULT 0,
                    link_karma INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT FALSE,
                    has_premium BOOLEAN DEFAULT FALSE,
                    profile_description TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Scraping sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    subreddits TEXT NOT NULL,
                    posts_count INTEGER DEFAULT 0,
                    users_count INTEGER DEFAULT 0,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    status TEXT DEFAULT 'running',
                    error_message TEXT,
                    configuration TEXT,
                    performance_metrics TEXT
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    operation_name TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES scraping_sessions (session_id)
                )
            """)
            
            # Analytics cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    cache_type TEXT
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts (subreddit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_utc ON posts (created_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_score ON posts (score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_scraped_at ON posts (scraped_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_scraped_at ON users (scraped_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON scraping_sessions (start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_session_id ON performance_metrics (session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON analytics_cache (expires_at)")
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        with self.connection_pool.get_connection() as conn:
            yield conn
    
    def store_posts(self, posts: List[Dict[str, Any]], session_id: str = None) -> int:
        """Store posts in database.
        
        Args:
            posts: List of post dictionaries
            session_id: Optional session ID for tracking
            
        Returns:
            Number of posts stored
        """
        if not posts:
            return 0
        
        stored_count = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for post in posts:
                try:
                    # Prepare post data
                    post_data = {
                        'id': post.get('id'),
                        'title': post.get('title'),
                        'author': post.get('author'),
                        'subreddit': post.get('subreddit'),
                        'score': post.get('score', 0),
                        'upvote_ratio': post.get('upvote_ratio', 0.0),
                        'num_comments': post.get('num_comments', 0),
                        'created_utc': post.get('created_utc'),
                        'url': post.get('url'),
                        'permalink': post.get('permalink'),
                        'selftext': post.get('selftext'),
                        'link_url': post.get('link_url'),
                        'flair': post.get('flair'),
                        'is_nsfw': post.get('is_nsfw', False),
                        'is_spoiler': post.get('is_spoiler', False),
                        'is_self': post.get('is_self', False),
                        'domain': post.get('domain'),
                        'content_type': post.get('metadata', {}).get('content_type'),
                        'category': post.get('category'),
                        'engagement_ratio': post.get('engagement_ratio', 0.0),
                        'extracted_content': json.dumps(post.get('extracted_content')) if post.get('extracted_content') else None,
                        'sentiment_score': post.get('sentiment_score'),
                        'sentiment_label': post.get('sentiment_label'),
                        'metadata': json.dumps(post.get('metadata', {}))
                    }
                    
                    # Insert or replace post
                    cursor.execute("""
                        INSERT OR REPLACE INTO posts (
                            id, title, author, subreddit, score, upvote_ratio, num_comments,
                            created_utc, url, permalink, selftext, link_url, flair,
                            is_nsfw, is_spoiler, is_self, domain, content_type, category,
                            engagement_ratio, extracted_content, sentiment_score, sentiment_label, metadata
                        ) VALUES (
                            :id, :title, :author, :subreddit, :score, :upvote_ratio, :num_comments,
                            :created_utc, :url, :permalink, :selftext, :link_url, :flair,
                            :is_nsfw, :is_spoiler, :is_self, :domain, :content_type, :category,
                            :engagement_ratio, :extracted_content, :sentiment_score, :sentiment_label, :metadata
                        )
                    """, post_data)
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing post {post.get('id', 'unknown')}: {e}")
                    continue
            
            conn.commit()
        
        logger.info(f"Stored {stored_count} posts in database")
        return stored_count
    
    def store_users(self, users: List[Dict[str, Any]]) -> int:
        """Store users in database.
        
        Args:
            users: List of user dictionaries
            
        Returns:
            Number of users stored
        """
        if not users:
            return 0
        
        stored_count = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for user in users:
                try:
                    user_data = {
                        'username': user.get('username'),
                        'user_id': user.get('id'),
                        'created_utc': user.get('created_utc'),
                        'comment_karma': user.get('comment_karma', 0),
                        'link_karma': user.get('link_karma', 0),
                        'is_verified': user.get('is_verified', False),
                        'has_premium': user.get('has_premium', False),
                        'profile_description': user.get('profile_description'),
                        'metadata': json.dumps(user.get('metadata', {}))
                    }
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO users (
                            username, user_id, created_utc, comment_karma, link_karma,
                            is_verified, has_premium, profile_description, metadata
                        ) VALUES (
                            :username, :user_id, :created_utc, :comment_karma, :link_karma,
                            :is_verified, :has_premium, :profile_description, :metadata
                        )
                    """, user_data)
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing user {user.get('username', 'unknown')}: {e}")
                    continue
            
            conn.commit()
        
        logger.info(f"Stored {stored_count} users in database")
        return stored_count
    
    def get_posts(self, subreddit: str = None, limit: int = 100, 
                  min_score: int = None, start_date: datetime = None,
                  end_date: datetime = None) -> List[Dict[str, Any]]:
        """Retrieve posts from database.
        
        Args:
            subreddit: Filter by subreddit
            limit: Maximum number of posts to return
            min_score: Minimum score filter
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of post dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM posts WHERE 1=1"
            params = {}
            
            if subreddit:
                query += " AND subreddit = :subreddit"
                params['subreddit'] = subreddit
            
            if min_score is not None:
                query += " AND score >= :min_score"
                params['min_score'] = min_score
            
            if start_date:
                query += " AND created_utc >= :start_date"
                params['start_date'] = int(start_date.timestamp())
            
            if end_date:
                query += " AND created_utc <= :end_date"
                params['end_date'] = int(end_date.timestamp())
            
            query += " ORDER BY created_utc DESC LIMIT :limit"
            params['limit'] = limit
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                post = dict(row)
                # Parse JSON fields
                if post['metadata']:
                    post['metadata'] = json.loads(post['metadata'])
                if post['extracted_content']:
                    post['extracted_content'] = json.loads(post['extracted_content'])
                posts.append(post)
            
            return posts
    
    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics summary dictionary
        """
        start_date = datetime.now() - timedelta(days=days)
        start_timestamp = int(start_date.timestamp())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_posts,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    SUM(num_comments) as total_comments,
                    AVG(num_comments) as avg_comments,
                    COUNT(DISTINCT subreddit) as unique_subreddits,
                    COUNT(DISTINCT author) as unique_authors
                FROM posts 
                WHERE created_utc >= ?
            """, (start_timestamp,))
            
            stats = dict(cursor.fetchone())
            
            # Top subreddits
            cursor.execute("""
                SELECT subreddit, COUNT(*) as post_count, AVG(score) as avg_score
                FROM posts 
                WHERE created_utc >= ?
                GROUP BY subreddit 
                ORDER BY post_count DESC 
                LIMIT 10
            """, (start_timestamp,))
            
            stats['top_subreddits'] = [dict(row) for row in cursor.fetchall()]
            
            # Posting patterns by hour
            cursor.execute("""
                SELECT 
                    strftime('%H', datetime(created_utc, 'unixepoch')) as hour,
                    COUNT(*) as post_count
                FROM posts 
                WHERE created_utc >= ?
                GROUP BY hour 
                ORDER BY hour
            """, (start_timestamp,))
            
            stats['hourly_patterns'] = [dict(row) for row in cursor.fetchall()]
            
            # Content type distribution
            cursor.execute("""
                SELECT content_type, COUNT(*) as count
                FROM posts 
                WHERE created_utc >= ? AND content_type IS NOT NULL
                GROUP BY content_type
            """, (start_timestamp,))
            
            stats['content_types'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
    
    def create_session(self, session_id: str, subreddits: List[str], 
                      configuration: Dict[str, Any]) -> str:
        """Create a new scraping session.
        
        Args:
            session_id: Unique session identifier
            subreddits: List of subreddits being scraped
            configuration: Scraping configuration
            
        Returns:
            Session ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scraping_sessions (
                    session_id, subreddits, start_time, configuration
                ) VALUES (?, ?, ?, ?)
            """, (
                session_id,
                json.dumps(subreddits),
                datetime.now().isoformat(),
                json.dumps(configuration)
            ))
            
            conn.commit()
        
        logger.info(f"Created scraping session: {session_id}")
        return session_id
    
    def update_session(self, session_id: str, posts_count: int = None,
                      users_count: int = None, status: str = None,
                      error_message: str = None, performance_metrics: Dict = None):
        """Update scraping session.
        
        Args:
            session_id: Session identifier
            posts_count: Number of posts scraped
            users_count: Number of users scraped
            status: Session status
            error_message: Error message if failed
            performance_metrics: Performance metrics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if posts_count is not None:
                updates.append("posts_count = ?")
                params.append(posts_count)
            
            if users_count is not None:
                updates.append("users_count = ?")
                params.append(users_count)
            
            if status:
                updates.append("status = ?")
                params.append(status)
                
                if status in ['completed', 'failed']:
                    updates.append("end_time = ?")
                    params.append(datetime.now().isoformat())
            
            if error_message:
                updates.append("error_message = ?")
                params.append(error_message)
            
            if performance_metrics:
                updates.append("performance_metrics = ?")
                params.append(json.dumps(performance_metrics))
            
            if updates:
                query = f"UPDATE scraping_sessions SET {', '.join(updates)} WHERE session_id = ?"
                params.append(session_id)
                cursor.execute(query, params)
                conn.commit()
    
    def store_performance_metric(self, session_id: str, operation_type: str,
                               operation_name: str, start_time: datetime,
                               end_time: datetime, memory_usage: float = None,
                               cpu_usage: float = None, success: bool = True,
                               error_message: str = None, metadata: Dict = None):
        """Store performance metric.
        
        Args:
            session_id: Session identifier
            operation_type: Type of operation
            operation_name: Name of operation
            start_time: Operation start time
            end_time: Operation end time
            memory_usage: Memory usage in MB
            cpu_usage: CPU usage percentage
            success: Whether operation succeeded
            error_message: Error message if failed
            metadata: Additional metadata
        """
        duration = (end_time - start_time).total_seconds()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics (
                    session_id, operation_type, operation_name, start_time, end_time,
                    duration_seconds, memory_usage_mb, cpu_usage_percent, success,
                    error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, operation_type, operation_name,
                start_time.isoformat(), end_time.isoformat(),
                duration, memory_usage, cpu_usage, success,
                error_message, json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
    
    def get_cached_analytics(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cache_data FROM analytics_cache 
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > ?)
            """, (cache_key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['cache_data'])
            
            return None
    
    def set_cached_analytics(self, cache_key: str, data: Dict[str, Any],
                           expires_in_hours: int = 1, cache_type: str = 'analytics'):
        """Set cached analytics data.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            expires_in_hours: Expiration time in hours
            cache_type: Type of cache
        """
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO analytics_cache (
                    cache_key, cache_data, expires_at, cache_type
                ) VALUES (?, ?, ?, ?)
            """, (cache_key, json.dumps(data), expires_at.isoformat(), cache_type))
            
            conn.commit()
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data from database.
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean old posts
            cursor.execute("DELETE FROM posts WHERE created_utc < ?", (cutoff_timestamp,))
            posts_deleted = cursor.rowcount
            
            # Clean old sessions
            cursor.execute("DELETE FROM scraping_sessions WHERE start_time < ?", 
                          (cutoff_date.isoformat(),))
            sessions_deleted = cursor.rowcount
            
            # Clean expired cache
            cursor.execute("DELETE FROM analytics_cache WHERE expires_at < ?",
                          (datetime.now().isoformat(),))
            cache_deleted = cursor.rowcount
            
            conn.commit()
        
        logger.info(f"Cleaned up old data: {posts_deleted} posts, "
                   f"{sessions_deleted} sessions, {cache_deleted} cache entries")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Database statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Table counts
            for table in ['posts', 'users', 'scraping_sessions', 'performance_metrics', 'analytics_cache']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size_bytes'] = cursor.fetchone()[0]
            
            # Date ranges
            cursor.execute("SELECT MIN(created_utc), MAX(created_utc) FROM posts")
            min_date, max_date = cursor.fetchone()
            if min_date and max_date:
                stats['data_date_range'] = {
                    'start': datetime.fromtimestamp(min_date).isoformat(),
                    'end': datetime.fromtimestamp(max_date).isoformat()
                }
            
            return stats