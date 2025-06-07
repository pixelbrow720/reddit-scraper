"""Reddit API client using PRAW."""

import praw
import logging
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedditClient:
    """Reddit API client wrapper."""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize Reddit client.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.reddit.read_only = True
        logger.info("Reddit client initialized successfully")
    
    def test_connection(self) -> bool:
        """Test Reddit API connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to access a simple endpoint
            list(self.reddit.subreddit("python").hot(limit=1))
            logger.info("Reddit API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Reddit API connection test failed: {e}")
            return False
    
    def get_subreddit_posts(self, subreddit_name: str, sort_type: str = "hot", 
                           limit: int = 100, time_filter: str = "all") -> List[Dict[str, Any]]:
        """Get posts from a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            sort_type: Sort type (hot, new, top, rising)
            limit: Number of posts to retrieve
            time_filter: Time filter for top posts (hour, day, week, month, year, all)
            
        Returns:
            List of post dictionaries
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            if sort_type == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort_type == "new":
                submissions = subreddit.new(limit=limit)
            elif sort_type == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_type == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid sort_type: {sort_type}")
            
            for submission in submissions:
                post_data = self._extract_post_data(submission)
                posts.append(post_data)
                
            logger.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting posts from r/{subreddit_name}: {e}")
            return []
    
    def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile information.
        
        Args:
            username: Reddit username
            
        Returns:
            User profile dictionary or None if error
        """
        try:
            user = self.reddit.redditor(username)
            
            # Check if user exists and is accessible
            try:
                user_created = user.created_utc
            except Exception:
                logger.warning(f"User {username} not found or inaccessible")
                return None
            
            profile_data = {
                "username": user.name,
                "id": user.id,
                "created_utc": int(user.created_utc),
                "comment_karma": getattr(user, 'comment_karma', 0),
                "link_karma": getattr(user, 'link_karma', 0),
                "is_verified": getattr(user, 'verified', False),
                "has_premium": getattr(user, 'is_gold', False),
                "profile_description": getattr(user, 'subreddit', {}).get('public_description', '') if hasattr(user, 'subreddit') else '',
                "metadata": {
                    "scraped_at": datetime.utcnow().isoformat() + "Z"
                }
            }
            
            logger.debug(f"Retrieved profile for user {username}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting profile for user {username}: {e}")
            return None
    
    def _extract_post_data(self, submission) -> Dict[str, Any]:
        """Extract data from a Reddit submission.
        
        Args:
            submission: PRAW submission object
            
        Returns:
            Post data dictionary
        """
        return {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": str(submission.subreddit),
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "created_utc": int(submission.created_utc),
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}",
            "selftext": submission.selftext,
            "link_url": submission.url if not submission.is_self else None,
            "flair": submission.link_flair_text,
            "is_nsfw": submission.over_18,
            "is_spoiler": submission.spoiler,
            "is_self": submission.is_self,
            "domain": submission.domain,
            "metadata": {
                "scraped_at": datetime.utcnow().isoformat() + "Z",
                "content_type": self._determine_content_type(submission)
            }
        }
    
    def _determine_content_type(self, submission) -> str:
        """Determine the content type of a submission.
        
        Args:
            submission: PRAW submission object
            
        Returns:
            Content type string
        """
        if submission.is_self:
            return "text"
        elif any(ext in submission.url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return "image"
        elif any(domain in submission.domain.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
            return "video"
        else:
            return "link"