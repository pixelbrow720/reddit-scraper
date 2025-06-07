"""Post data processing and filtering."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class PostProcessor:
    """Process and filter Reddit posts."""
    
    def __init__(self, min_score: int = 1, max_age_days: int = 365, 
                 exclude_nsfw: bool = True, exclude_deleted: bool = True):
        """Initialize post processor.
        
        Args:
            min_score: Minimum post score to include
            max_age_days: Maximum age in days for posts
            exclude_nsfw: Whether to exclude NSFW posts
            exclude_deleted: Whether to exclude deleted posts
        """
        self.min_score = min_score
        self.max_age_days = max_age_days
        self.exclude_nsfw = exclude_nsfw
        self.exclude_deleted = exclude_deleted
        
        logger.info(f"Post processor initialized with filters: min_score={min_score}, "
                   f"max_age_days={max_age_days}, exclude_nsfw={exclude_nsfw}, "
                   f"exclude_deleted={exclude_deleted}")
    
    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter posts based on configured criteria.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Filtered list of posts
        """
        filtered_posts = []
        current_time = datetime.utcnow().timestamp()
        max_age_seconds = self.max_age_days * 24 * 3600
        
        for post in posts:
            # Check score filter
            if post.get('score', 0) < self.min_score:
                continue
            
            # Check age filter
            post_age = current_time - post.get('created_utc', 0)
            if post_age > max_age_seconds:
                continue
            
            # Check NSFW filter
            if self.exclude_nsfw and post.get('is_nsfw', False):
                continue
            
            # Check deleted filter
            if self.exclude_deleted and (
                post.get('author') == '[deleted]' or 
                post.get('selftext') == '[deleted]' or
                post.get('selftext') == '[removed]'
            ):
                continue
            
            filtered_posts.append(post)
        
        logger.info(f"Filtered {len(posts)} posts down to {len(filtered_posts)} posts")
        return filtered_posts
    
    def deduplicate_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate posts based on ID.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Deduplicated list of posts
        """
        seen_ids = set()
        unique_posts = []
        
        for post in posts:
            post_id = post.get('id')
            if post_id and post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)
        
        duplicates_removed = len(posts) - len(unique_posts)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate posts")
        
        return unique_posts
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove Reddit markdown
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'\^(.*?)\^', r'\1', text)      # Superscript
        
        # Clean up URLs in text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
        
        return text.strip()
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text content.
        
        Args:
            text: Text content
            
        Returns:
            List of URLs found in text
        """
        if not text:
            return []
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def categorize_post(self, post: Dict[str, Any]) -> str:
        """Categorize post based on content and metadata.
        
        Args:
            post: Post dictionary
            
        Returns:
            Category string
        """
        title = post.get('title', '').lower()
        selftext = post.get('selftext', '').lower()
        flair = post.get('flair', '').lower() if post.get('flair') else ''
        
        # Question posts
        if any(word in title for word in ['how', 'what', 'why', 'when', 'where', '?']):
            return 'question'
        
        # Discussion posts
        if any(word in title for word in ['discussion', 'thoughts', 'opinion', 'what do you think']):
            return 'discussion'
        
        # News/Article posts
        if not post.get('is_self') and any(domain in post.get('domain', '') for domain in 
                                         ['news', 'article', 'blog', 'medium', 'reuters', 'bbc']):
            return 'news'
        
        # Tutorial/Guide posts
        if any(word in title for word in ['tutorial', 'guide', 'how to', 'step by step']):
            return 'tutorial'
        
        # Show and tell posts
        if any(word in title for word in ['show', 'made', 'built', 'created', 'my project']):
            return 'showcase'
        
        # Meme/Humor posts
        if any(word in flair for word in ['meme', 'humor', 'funny', 'joke']):
            return 'meme'
        
        # Default category
        if post.get('is_self'):
            return 'text'
        else:
            return 'link'
    
    def add_derived_fields(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add derived fields to posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Posts with additional derived fields
        """
        for post in posts:
            # Clean text fields
            post['title_clean'] = self.clean_text(post.get('title', ''))
            post['selftext_clean'] = self.clean_text(post.get('selftext', ''))
            
            # Extract URLs from text
            post['extracted_urls'] = self.extract_urls(post.get('selftext', ''))
            
            # Categorize post
            post['category'] = self.categorize_post(post)
            
            # Add engagement metrics
            score = post.get('score', 0)
            num_comments = post.get('num_comments', 0)
            post['engagement_ratio'] = num_comments / max(score, 1)
            
            # Add time-based fields
            created_utc = post.get('created_utc', 0)
            if created_utc:
                created_dt = datetime.fromtimestamp(created_utc)
                post['created_date'] = created_dt.strftime('%Y-%m-%d')
                post['created_hour'] = created_dt.hour
                post['created_weekday'] = created_dt.weekday()
        
        logger.info(f"Added derived fields to {len(posts)} posts")
        return posts