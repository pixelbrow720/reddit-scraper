"""Parallel scraping functionality for multiple subreddits."""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import threading
from dataclasses import dataclass
from queue import Queue
import multiprocessing as mp

from .reddit_client import RedditClient
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class ScrapeTask:
    """Represents a scraping task."""
    subreddit: str
    sort_type: str
    limit: int
    time_filter: str
    task_id: str


@dataclass
class ScrapeResult:
    """Represents a scraping result."""
    task_id: str
    subreddit: str
    posts: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None
    duration: float = 0.0


class ParallelScraper:
    """Parallel scraper for multiple subreddits."""
    
    def __init__(self, reddit_config: Dict[str, str], max_workers: int = 5, 
                 rate_limit: float = 1.0, use_processes: bool = False):
        """Initialize parallel scraper.
        
        Args:
            reddit_config: Reddit API configuration
            max_workers: Maximum number of concurrent workers
            rate_limit: Global rate limit (requests per second)
            use_processes: Whether to use processes instead of threads
        """
        self.reddit_config = reddit_config
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.use_processes = use_processes
        
        # Global rate limiter
        self.global_rate_limiter = RateLimiter(rate_limit)
        
        # Results storage
        self.results: List[ScrapeResult] = []
        self.failed_tasks: List[ScrapeTask] = []
        
        # Progress tracking
        self.total_tasks = 0
        self.completed_tasks = 0
        self.progress_callbacks: List[Callable] = []
        
        logger.info(f"Parallel scraper initialized with {max_workers} workers, "
                   f"rate limit: {rate_limit} req/sec, processes: {use_processes}")
    
    def add_progress_callback(self, callback: Callable[[int, int], None]):
        """Add progress callback function.
        
        Args:
            callback: Function that takes (completed, total) as arguments
        """
        self.progress_callbacks.append(callback)
    
    def scrape_multiple_subreddits(self, subreddits: List[str], sort_type: str = "hot",
                                  posts_per_subreddit: int = 100, time_filter: str = "all",
                                  retry_failed: bool = True) -> List[ScrapeResult]:
        """Scrape multiple subreddits in parallel.
        
        Args:
            subreddits: List of subreddit names
            sort_type: Sort type for posts
            posts_per_subreddit: Number of posts per subreddit
            time_filter: Time filter for top posts
            retry_failed: Whether to retry failed tasks
            
        Returns:
            List of scrape results
        """
        # Create tasks
        tasks = []
        for i, subreddit in enumerate(subreddits):
            task = ScrapeTask(
                subreddit=subreddit,
                sort_type=sort_type,
                limit=posts_per_subreddit,
                time_filter=time_filter,
                task_id=f"task_{i}_{subreddit}"
            )
            tasks.append(task)
        
        self.total_tasks = len(tasks)
        self.completed_tasks = 0
        self.results = []
        self.failed_tasks = []
        
        logger.info(f"Starting parallel scraping of {len(tasks)} subreddits")
        
        # Execute tasks
        if self.use_processes:
            results = self._scrape_with_processes(tasks)
        else:
            results = self._scrape_with_threads(tasks)
        
        # Retry failed tasks if requested
        if retry_failed and self.failed_tasks:
            logger.info(f"Retrying {len(self.failed_tasks)} failed tasks")
            retry_results = self._retry_failed_tasks()
            results.extend(retry_results)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_posts = sum(len(r.posts) for r in results if r.success)
        
        logger.info(f"Parallel scraping completed: {successful} successful, "
                   f"{failed} failed, {total_posts} total posts")
        
        return results
    
    def _scrape_with_threads(self, tasks: List[ScrapeTask]) -> List[ScrapeResult]:
        """Scrape using thread pool.
        
        Args:
            tasks: List of scrape tasks
            
        Returns:
            List of scrape results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_scrape_task, task): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result.success:
                        self.failed_tasks.append(task)
                    
                    self.completed_tasks += 1
                    self._notify_progress()
                    
                except Exception as e:
                    logger.error(f"Task {task.task_id} failed with exception: {e}")
                    error_result = ScrapeResult(
                        task_id=task.task_id,
                        subreddit=task.subreddit,
                        posts=[],
                        success=False,
                        error=str(e)
                    )
                    results.append(error_result)
                    self.failed_tasks.append(task)
                    self.completed_tasks += 1
                    self._notify_progress()
        
        return results
    
    def _scrape_with_processes(self, tasks: List[ScrapeTask]) -> List[ScrapeResult]:
        """Scrape using process pool.
        
        Args:
            tasks: List of scrape tasks
            
        Returns:
            List of scrape results
        """
        results = []
        
        # Create process pool
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(_execute_scrape_task_process, task, self.reddit_config): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result.success:
                        self.failed_tasks.append(task)
                    
                    self.completed_tasks += 1
                    self._notify_progress()
                    
                except Exception as e:
                    logger.error(f"Process task {task.task_id} failed with exception: {e}")
                    error_result = ScrapeResult(
                        task_id=task.task_id,
                        subreddit=task.subreddit,
                        posts=[],
                        success=False,
                        error=str(e)
                    )
                    results.append(error_result)
                    self.failed_tasks.append(task)
                    self.completed_tasks += 1
                    self._notify_progress()
        
        return results
    
    def _execute_scrape_task(self, task: ScrapeTask) -> ScrapeResult:
        """Execute a single scrape task.
        
        Args:
            task: Scrape task to execute
            
        Returns:
            Scrape result
        """
        start_time = time.time()
        
        try:
            # Wait for rate limit
            self.global_rate_limiter.wait_if_needed()
            
            # Create client for this task
            client = RedditClient(**self.reddit_config)
            
            # Execute scraping
            posts = client.get_subreddit_posts(
                subreddit_name=task.subreddit,
                sort_type=task.sort_type,
                limit=task.limit,
                time_filter=task.time_filter
            )
            
            duration = time.time() - start_time
            
            result = ScrapeResult(
                task_id=task.task_id,
                subreddit=task.subreddit,
                posts=posts,
                success=True,
                duration=duration
            )
            
            logger.debug(f"Task {task.task_id} completed: {len(posts)} posts in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"Task {task.task_id} failed: {e}")
            
            return ScrapeResult(
                task_id=task.task_id,
                subreddit=task.subreddit,
                posts=[],
                success=False,
                error=str(e),
                duration=duration
            )
    
    def _retry_failed_tasks(self) -> List[ScrapeResult]:
        """Retry failed tasks with exponential backoff.
        
        Returns:
            List of retry results
        """
        if not self.failed_tasks:
            return []
        
        retry_results = []
        
        # Use single-threaded retry with longer delays
        for i, task in enumerate(self.failed_tasks):
            # Exponential backoff delay
            delay = min(2 ** i, 30)  # Max 30 seconds
            time.sleep(delay)
            
            logger.info(f"Retrying task {task.task_id} (attempt 2)")
            result = self._execute_scrape_task(task)
            retry_results.append(result)
            
            if result.success:
                logger.info(f"Retry successful for {task.subreddit}")
            else:
                logger.warning(f"Retry failed for {task.subreddit}: {result.error}")
        
        return retry_results
    
    def _notify_progress(self):
        """Notify progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(self.completed_tasks, self.total_tasks)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for completed scraping.
        
        Returns:
            Summary statistics dictionary
        """
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        total_posts = sum(len(r.posts) for r in successful_results)
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / len(self.results) if self.results else 0
        
        return {
            'total_tasks': len(self.results),
            'successful_tasks': len(successful_results),
            'failed_tasks': len(failed_results),
            'success_rate': len(successful_results) / len(self.results) * 100 if self.results else 0,
            'total_posts': total_posts,
            'avg_posts_per_subreddit': total_posts / len(successful_results) if successful_results else 0,
            'total_duration': total_duration,
            'avg_duration_per_task': avg_duration,
            'posts_per_second': total_posts / total_duration if total_duration > 0 else 0
        }


class AsyncScraper:
    """Async scraper for high-performance scraping."""
    
    def __init__(self, reddit_config: Dict[str, str], max_concurrent: int = 10,
                 rate_limit: float = 2.0):
        """Initialize async scraper.
        
        Args:
            reddit_config: Reddit API configuration
            max_concurrent: Maximum concurrent requests
            rate_limit: Rate limit (requests per second)
        """
        self.reddit_config = reddit_config
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0
        
        logger.info(f"Async scraper initialized with {max_concurrent} concurrent requests")
    
    async def scrape_subreddits_async(self, subreddits: List[str], 
                                     sort_type: str = "hot", limit: int = 100,
                                     time_filter: str = "all") -> List[ScrapeResult]:
        """Scrape multiple subreddits asynchronously.
        
        Args:
            subreddits: List of subreddit names
            sort_type: Sort type for posts
            limit: Number of posts per subreddit
            time_filter: Time filter for top posts
            
        Returns:
            List of scrape results
        """
        tasks = []
        
        for i, subreddit in enumerate(subreddits):
            task = asyncio.create_task(
                self._scrape_subreddit_async(subreddit, sort_type, limit, time_filter, f"async_{i}")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ScrapeResult(
                    task_id=f"async_{i}",
                    subreddit=subreddits[i],
                    posts=[],
                    success=False,
                    error=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _scrape_subreddit_async(self, subreddit: str, sort_type: str,
                                     limit: int, time_filter: str, task_id: str) -> ScrapeResult:
        """Scrape a single subreddit asynchronously.
        
        Args:
            subreddit: Subreddit name
            sort_type: Sort type
            limit: Number of posts
            time_filter: Time filter
            task_id: Task identifier
            
        Returns:
            Scrape result
        """
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # Rate limiting
                await self._async_rate_limit()
                
                # Execute in thread pool (PRAW is not async)
                loop = asyncio.get_event_loop()
                posts = await loop.run_in_executor(
                    None,
                    self._sync_scrape_subreddit,
                    subreddit, sort_type, limit, time_filter
                )
                
                duration = time.time() - start_time
                
                return ScrapeResult(
                    task_id=task_id,
                    subreddit=subreddit,
                    posts=posts,
                    success=True,
                    duration=duration
                )
                
            except Exception as e:
                duration = time.time() - start_time
                return ScrapeResult(
                    task_id=task_id,
                    subreddit=subreddit,
                    posts=[],
                    success=False,
                    error=str(e),
                    duration=duration
                )
    
    async def _async_rate_limit(self):
        """Async rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _sync_scrape_subreddit(self, subreddit: str, sort_type: str,
                              limit: int, time_filter: str) -> List[Dict[str, Any]]:
        """Synchronous subreddit scraping for use in thread pool.
        
        Args:
            subreddit: Subreddit name
            sort_type: Sort type
            limit: Number of posts
            time_filter: Time filter
            
        Returns:
            List of posts
        """
        client = RedditClient(**self.reddit_config)
        return client.get_subreddit_posts(subreddit, sort_type, limit, time_filter)


def _execute_scrape_task_process(task: ScrapeTask, reddit_config: Dict[str, str]) -> ScrapeResult:
    """Execute scrape task in separate process.
    
    Args:
        task: Scrape task
        reddit_config: Reddit API configuration
        
    Returns:
        Scrape result
    """
    start_time = time.time()
    
    try:
        # Create client in this process
        client = RedditClient(**reddit_config)
        
        # Execute scraping
        posts = client.get_subreddit_posts(
            subreddit_name=task.subreddit,
            sort_type=task.sort_type,
            limit=task.limit,
            time_filter=task.time_filter
        )
        
        duration = time.time() - start_time
        
        return ScrapeResult(
            task_id=task.task_id,
            subreddit=task.subreddit,
            posts=posts,
            success=True,
            duration=duration
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return ScrapeResult(
            task_id=task.task_id,
            subreddit=task.subreddit,
            posts=[],
            success=False,
            error=str(e),
            duration=duration
        )