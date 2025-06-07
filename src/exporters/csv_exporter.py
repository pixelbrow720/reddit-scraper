"""CSV export functionality."""

import csv
import logging
import os
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export data to CSV format."""
    
    def __init__(self, output_dir: str = "output/csv"):
        """Initialize CSV exporter.
        
        Args:
            output_dir: Output directory for CSV files
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"CSV exporter initialized with output directory: {output_dir}")
    
    def export_posts(self, posts: List[Dict[str, Any]], filename: str = None) -> str:
        """Export posts to CSV file.
        
        Args:
            posts: List of post dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if not posts:
            logger.warning("No posts to export")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_posts_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Define CSV columns
        columns = [
            'id', 'title', 'author', 'subreddit', 'score', 'upvote_ratio',
            'num_comments', 'created_utc', 'created_date', 'url', 'permalink',
            'selftext', 'link_url', 'flair', 'is_nsfw', 'is_spoiler', 'is_self',
            'domain', 'category', 'engagement_ratio', 'created_hour', 'created_weekday'
        ]
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
                writer.writeheader()
                
                for post in posts:
                    # Clean data for CSV export
                    cleaned_post = self._clean_post_for_csv(post)
                    writer.writerow(cleaned_post)
            
            logger.info(f"Exported {len(posts)} posts to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting posts to CSV: {e}")
            raise
    
    def export_users(self, users: List[Dict[str, Any]], filename: str = None) -> str:
        """Export user profiles to CSV file.
        
        Args:
            users: List of user profile dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if not users:
            logger.warning("No users to export")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_users_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Define CSV columns for users
        columns = [
            'username', 'id', 'created_utc', 'comment_karma', 'link_karma',
            'is_verified', 'has_premium', 'profile_description', 'scraped_at'
        ]
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
                writer.writeheader()
                
                for user in users:
                    # Flatten user data for CSV
                    flattened_user = self._flatten_user_for_csv(user)
                    writer.writerow(flattened_user)
            
            logger.info(f"Exported {len(users)} user profiles to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting users to CSV: {e}")
            raise
    
    def export_summary_stats(self, posts: List[Dict[str, Any]], filename: str = None) -> str:
        """Export summary statistics to CSV.
        
        Args:
            posts: List of post dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if not posts:
            logger.warning("No posts for summary statistics")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_summary_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate summary statistics
        stats = self._generate_summary_stats(posts)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                
                for metric, value in stats.items():
                    writer.writerow([metric, value])
            
            logger.info(f"Exported summary statistics to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting summary statistics: {e}")
            raise
    
    def export_subreddit_breakdown(self, posts: List[Dict[str, Any]], filename: str = None) -> str:
        """Export subreddit breakdown to CSV.
        
        Args:
            posts: List of post dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if not posts:
            logger.warning("No posts for subreddit breakdown")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_subreddits_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate subreddit statistics
        subreddit_stats = self._calculate_subreddit_stats(posts)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Subreddit', 'Post Count', 'Avg Score', 'Total Comments', 'Avg Comments'])
                
                for subreddit, stats in sorted(subreddit_stats.items(), 
                                             key=lambda x: x[1]['post_count'], reverse=True):
                    writer.writerow([
                        subreddit,
                        stats['post_count'],
                        round(stats['avg_score'], 2),
                        stats['total_comments'],
                        round(stats['avg_comments'], 2)
                    ])
            
            logger.info(f"Exported subreddit breakdown to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting subreddit breakdown: {e}")
            raise
    
    def _clean_post_for_csv(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Clean post data for CSV export.
        
        Args:
            post: Post dictionary
            
        Returns:
            Cleaned post dictionary
        """
        cleaned = post.copy()
        
        # Clean text fields (remove newlines and excessive whitespace)
        text_fields = ['title', 'selftext', 'flair']
        for field in text_fields:
            if field in cleaned and cleaned[field]:
                cleaned[field] = str(cleaned[field]).replace('\n', ' ').replace('\r', ' ')
                cleaned[field] = ' '.join(cleaned[field].split())
        
        # Convert boolean fields to strings
        bool_fields = ['is_nsfw', 'is_spoiler', 'is_self', 'is_verified', 'has_premium']
        for field in bool_fields:
            if field in cleaned:
                cleaned[field] = str(cleaned[field])
        
        # Handle None values
        for key, value in cleaned.items():
            if value is None:
                cleaned[key] = ''
        
        return cleaned
    
    def _flatten_user_for_csv(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten user data for CSV export.
        
        Args:
            user: User dictionary
            
        Returns:
            Flattened user dictionary
        """
        flattened = user.copy()
        
        # Extract metadata fields
        if 'metadata' in flattened:
            metadata = flattened.pop('metadata')
            flattened['scraped_at'] = metadata.get('scraped_at', '')
        
        # Clean text fields
        if 'profile_description' in flattened and flattened['profile_description']:
            flattened['profile_description'] = str(flattened['profile_description']).replace('\n', ' ')
        
        # Convert boolean fields to strings
        bool_fields = ['is_verified', 'has_premium']
        for field in bool_fields:
            if field in flattened:
                flattened[field] = str(flattened[field])
        
        # Handle None values
        for key, value in flattened.items():
            if value is None:
                flattened[key] = ''
        
        return flattened
    
    def _generate_summary_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Summary statistics dictionary
        """
        if not posts:
            return {}
        
        scores = [post.get('score', 0) for post in posts]
        comments = [post.get('num_comments', 0) for post in posts]
        
        # Count by content type
        content_types = {}
        for post in posts:
            content_type = post.get('category', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Count NSFW posts
        nsfw_count = sum(1 for post in posts if post.get('is_nsfw', False))
        
        return {
            'Total Posts': len(posts),
            'Average Score': round(sum(scores) / len(scores), 2) if scores else 0,
            'Max Score': max(scores) if scores else 0,
            'Min Score': min(scores) if scores else 0,
            'Total Comments': sum(comments),
            'Average Comments': round(sum(comments) / len(comments), 2) if comments else 0,
            'NSFW Posts': nsfw_count,
            'Unique Subreddits': len(set(post.get('subreddit', '') for post in posts)),
            'Unique Authors': len(set(post.get('author', '') for post in posts if post.get('author') != '[deleted]')),
            'Text Posts': content_types.get('text', 0),
            'Link Posts': content_types.get('link', 0),
            'Image Posts': content_types.get('image', 0),
            'Video Posts': content_types.get('video', 0)
        }
    
    def _calculate_subreddit_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by subreddit.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Dictionary of subreddit statistics
        """
        subreddit_data = {}
        
        for post in posts:
            subreddit = post.get('subreddit', '')
            if not subreddit:
                continue
            
            if subreddit not in subreddit_data:
                subreddit_data[subreddit] = {
                    'posts': [],
                    'scores': [],
                    'comments': []
                }
            
            subreddit_data[subreddit]['posts'].append(post)
            subreddit_data[subreddit]['scores'].append(post.get('score', 0))
            subreddit_data[subreddit]['comments'].append(post.get('num_comments', 0))
        
        # Calculate statistics
        stats = {}
        for subreddit, data in subreddit_data.items():
            scores = data['scores']
            comments = data['comments']
            
            stats[subreddit] = {
                'post_count': len(data['posts']),
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'total_comments': sum(comments),
                'avg_comments': sum(comments) / len(comments) if comments else 0
            }
        
        return stats