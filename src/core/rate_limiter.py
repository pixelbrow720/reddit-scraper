"""Rate limiting functionality for Reddit API requests."""

import time
import logging
from typing import Optional
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter to control request frequency."""
    
    def __init__(self, requests_per_second: float = 1.0, max_retries: int = 3):
        """Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            max_retries: Maximum number of retries for failed requests
        """
        self.requests_per_second = requests_per_second
        self.max_retries = max_retries
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        self.lock = Lock()
        
        logger.info(f"Rate limiter initialized: {requests_per_second} req/sec, {max_retries} max retries")
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def exponential_backoff(self, attempt: int, base_delay: float = 1.0) -> float:
        """Calculate exponential backoff delay.
        
        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            
        Returns:
            Delay time in seconds
        """
        delay = base_delay * (2 ** attempt)
        logger.debug(f"Exponential backoff: attempt {attempt + 1}, delay {delay:.2f}s")
        return delay
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with retry and exponential backoff.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.wait_if_needed()
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.exponential_backoff(attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed. Last error: {e}")
        
        return None