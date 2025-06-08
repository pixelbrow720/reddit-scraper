"""Thread-safe and process-safe rate limiter implementation."""

import time
import threading
import multiprocessing as mp
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ThreadSafeRateLimiter:
    """Thread-safe rate limiter using threading primitives."""
    
    def __init__(self, rate_limit: float):
        """Initialize rate limiter.
        
        Args:
            rate_limit: Maximum requests per second
        """
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_request_time = 0.0
        self._lock = threading.Lock()
        
        logger.info(f"Thread-safe rate limiter initialized: {rate_limit} req/sec")
    
    def wait_if_needed(self) -> float:
        """Wait if needed to respect rate limit.
        
        Returns:
            Time waited in seconds
        """
        if self.rate_limit <= 0:
            return 0.0
        
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
                self.last_request_time = time.time()
                return sleep_time
            else:
                self.last_request_time = current_time
                return 0.0


class ProcessSafeRateLimiter:
    """Process-safe rate limiter using multiprocessing primitives."""
    
    def __init__(self, rate_limit: float):
        """Initialize process-safe rate limiter.
        
        Args:
            rate_limit: Maximum requests per second
        """
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        
        # Shared memory for last request time
        self._last_request_time = mp.Value('d', 0.0)
        self._lock = mp.Lock()
        
        logger.info(f"Process-safe rate limiter initialized: {rate_limit} req/sec")
    
    def wait_if_needed(self) -> float:
        """Wait if needed to respect rate limit.
        
        Returns:
            Time waited in seconds
        """
        if self.rate_limit <= 0:
            return 0.0
        
        with self._lock:
            current_time = time.time()
            
            with self._last_request_time.get_lock():
                time_since_last = current_time - self._last_request_time.value
                
                if time_since_last < self.min_interval:
                    sleep_time = self.min_interval - time_since_last
                    time.sleep(sleep_time)
                    self._last_request_time.value = time.time()
                    return sleep_time
                else:
                    self._last_request_time.value = current_time
                    return 0.0


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on API responses."""
    
    def __init__(self, initial_rate: float, min_rate: float = 0.1, max_rate: float = 10.0):
        """Initialize adaptive rate limiter.
        
        Args:
            initial_rate: Initial rate limit
            min_rate: Minimum rate limit
            max_rate: Maximum rate limit
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.base_limiter = ThreadSafeRateLimiter(initial_rate)
        self._lock = threading.Lock()
        
        # Tracking for adaptation
        self.success_count = 0
        self.error_count = 0
        self.last_adaptation = time.time()
        self.adaptation_interval = 60.0  # Adapt every minute
        
        logger.info(f"Adaptive rate limiter initialized: {initial_rate} req/sec")
    
    def wait_if_needed(self) -> float:
        """Wait if needed and adapt rate if necessary."""
        self._adapt_if_needed()
        return self.base_limiter.wait_if_needed()
    
    def record_success(self):
        """Record a successful request."""
        with self._lock:
            self.success_count += 1
    
    def record_error(self, is_rate_limit_error: bool = False):
        """Record an error.
        
        Args:
            is_rate_limit_error: Whether this was a rate limit error
        """
        with self._lock:
            self.error_count += 1
            
            # Immediate slowdown for rate limit errors
            if is_rate_limit_error:
                self._decrease_rate(factor=0.5)
    
    def _adapt_if_needed(self):
        """Adapt rate limit based on recent performance."""
        current_time = time.time()
        
        with self._lock:
            if current_time - self.last_adaptation < self.adaptation_interval:
                return
            
            total_requests = self.success_count + self.error_count
            if total_requests < 10:  # Not enough data
                return
            
            error_rate = self.error_count / total_requests
            
            if error_rate > 0.1:  # More than 10% errors
                self._decrease_rate()
            elif error_rate < 0.02:  # Less than 2% errors
                self._increase_rate()
            
            # Reset counters
            self.success_count = 0
            self.error_count = 0
            self.last_adaptation = current_time
    
    def _increase_rate(self, factor: float = 1.2):
        """Increase rate limit."""
        new_rate = min(self.current_rate * factor, self.max_rate)
        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self.base_limiter = ThreadSafeRateLimiter(new_rate)
            logger.info(f"Rate limit increased to {new_rate:.2f} req/sec")
    
    def _decrease_rate(self, factor: float = 0.8):
        """Decrease rate limit."""
        new_rate = max(self.current_rate * factor, self.min_rate)
        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self.base_limiter = ThreadSafeRateLimiter(new_rate)
            logger.info(f"Rate limit decreased to {new_rate:.2f} req/sec")


class DistributedRateLimiter:
    """Distributed rate limiter using Redis (optional dependency)."""
    
    def __init__(self, rate_limit: float, redis_url: Optional[str] = None, 
                 key_prefix: str = "reddit_scraper_rate_limit"):
        """Initialize distributed rate limiter.
        
        Args:
            rate_limit: Maximum requests per second
            redis_url: Redis connection URL (if None, falls back to local)
            key_prefix: Redis key prefix
        """
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.key_prefix = key_prefix
        
        # Try to import and connect to Redis
        self.redis_client = None
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Test connection
                logger.info(f"Distributed rate limiter using Redis: {redis_url}")
            except ImportError:
                logger.warning("Redis not available, falling back to local rate limiting")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to local")
        
        # Fallback to local rate limiter
        if not self.redis_client:
            self.local_limiter = ThreadSafeRateLimiter(rate_limit)
            logger.info("Using local thread-safe rate limiter as fallback")
    
    def wait_if_needed(self) -> float:
        """Wait if needed to respect distributed rate limit."""
        if self.rate_limit <= 0:
            return 0.0
        
        if self.redis_client:
            return self._redis_rate_limit()
        else:
            return self.local_limiter.wait_if_needed()
    
    def _redis_rate_limit(self) -> float:
        """Implement rate limiting using Redis."""
        try:
            current_time = time.time()
            key = f"{self.key_prefix}:last_request"
            
            # Use Redis transaction for atomic operation
            pipe = self.redis_client.pipeline()
            pipe.get(key)
            pipe.set(key, current_time, ex=60)  # Expire after 1 minute
            results = pipe.execute()
            
            last_request_time = float(results[0] or 0)
            time_since_last = current_time - last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
                
                # Update with actual time after sleep
                self.redis_client.set(key, time.time(), ex=60)
                return sleep_time
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Redis rate limiting failed: {e}, using local fallback")
            return self.local_limiter.wait_if_needed()
