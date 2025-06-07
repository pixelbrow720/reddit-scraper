"""JSON export functionality."""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class JSONExporter:
    """Export data to JSON format."""
    
    def __init__(self, output_dir: str = "output/json", indent: int = 2, 
                 ensure_ascii: bool = False):
        """Initialize JSON exporter.
        
        Args:
            output_dir: Output directory for JSON files
            indent: JSON indentation level
            ensure_ascii: Whether to ensure ASCII encoding
        """
        self.output_dir = output_dir
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"JSON exporter initialized with output directory: {output_dir}")
    
    def export_posts(self, posts: List[Dict[str, Any]], filename: str = None, 
                    include_metadata: bool = True) -> str:
        """Export posts to JSON file.
        
        Args:
            posts: List of post dictionaries
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to include metadata
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_posts_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data structure
        data = {}
        
        if include_metadata:
            data["metadata"] = self._generate_metadata(posts)
        
        data["posts"] = posts
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=self.ensure_ascii, 
                         default=self._json_serializer)
            
            logger.info(f"Exported {len(posts)} posts to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting posts to JSON: {e}")
            raise
    
    def export_users(self, users: List[Dict[str, Any]], filename: str = None) -> str:
        """Export user profiles to JSON file.
        
        Args:
            users: List of user profile dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_users_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data structure
        data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "total_users": len(users),
                "export_type": "user_profiles"
            },
            "users": users
        }
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=self.ensure_ascii,
                         default=self._json_serializer)
            
            logger.info(f"Exported {len(users)} user profiles to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting users to JSON: {e}")
            raise
    
    def export_combined(self, posts: List[Dict[str, Any]], users: List[Dict[str, Any]] = None,
                       filename: str = None) -> str:
        """Export combined posts and users data.
        
        Args:
            posts: List of post dictionaries
            users: List of user profile dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_combined_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data structure
        data = {
            "metadata": self._generate_combined_metadata(posts, users),
            "posts": posts
        }
        
        if users:
            data["users"] = users
        
        # Add statistics
        data["statistics"] = self._generate_statistics(posts, users)
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=self.ensure_ascii,
                         default=self._json_serializer)
            
            logger.info(f"Exported combined data ({len(posts)} posts, "
                       f"{len(users) if users else 0} users) to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting combined data to JSON: {e}")
            raise
    
    def _generate_metadata(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate metadata for posts export.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Metadata dictionary
        """
        subreddits = list(set(post.get('subreddit', '') for post in posts if post.get('subreddit')))
        
        return {
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "total_posts": len(posts),
            "subreddits": sorted(subreddits),
            "export_type": "reddit_posts",
            "date_range": self._get_date_range(posts)
        }
    
    def _generate_combined_metadata(self, posts: List[Dict[str, Any]], 
                                  users: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate metadata for combined export.
        
        Args:
            posts: List of post dictionaries
            users: List of user profile dictionaries
            
        Returns:
            Metadata dictionary
        """
        metadata = self._generate_metadata(posts)
        metadata["export_type"] = "reddit_combined"
        metadata["total_users"] = len(users) if users else 0
        
        return metadata
    
    def _generate_statistics(self, posts: List[Dict[str, Any]], 
                           users: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate statistics for the data.
        
        Args:
            posts: List of post dictionaries
            users: List of user profile dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not posts:
            return {}
        
        scores = [post.get('score', 0) for post in posts]
        comments = [post.get('num_comments', 0) for post in posts]
        
        # Top authors by post count
        author_counts = {}
        for post in posts:
            author = post.get('author', '')
            if author and author != '[deleted]':
                author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Subreddit distribution
        subreddit_counts = {}
        for post in posts:
            subreddit = post.get('subreddit', '')
            if subreddit:
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        return {
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "total_comments": sum(comments),
            "avg_comments": sum(comments) / len(comments) if comments else 0,
            "top_authors": [{"username": author, "post_count": count} for author, count in top_authors],
            "subreddit_distribution": dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True))
        }
    
    def _get_date_range(self, posts: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get date range of posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Date range dictionary
        """
        if not posts:
            return {}
        
        timestamps = [post.get('created_utc', 0) for post in posts if post.get('created_utc')]
        
        if not timestamps:
            return {}
        
        min_timestamp = min(timestamps)
        max_timestamp = max(timestamps)
        
        return {
            "earliest": datetime.fromtimestamp(min_timestamp).isoformat() + "Z",
            "latest": datetime.fromtimestamp(max_timestamp).isoformat() + "Z"
        }
    
    def _json_serializer(self, obj):
        """JSON serializer for non-standard types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")