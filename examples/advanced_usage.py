#!/usr/bin/env python3
"""
Advanced Usage Examples for Reddit Scraper
This file demonstrates advanced usage patterns and custom implementations.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.cli.config import Config
from src.core.reddit_client import RedditClient
from src.core.rate_limiter import RateLimiter
from src.processors.post_processor import PostProcessor
from src.exporters.json_exporter import JSONExporter


class AdvancedAnalyzer:
    """Advanced analysis tools for Reddit data."""
    
    def __init__(self, posts: List[Dict[str, Any]]):
        self.posts = posts
        self.df = pd.DataFrame(posts) if posts else pd.DataFrame()
    
    def analyze_posting_patterns(self):
        """Analyze posting time patterns."""
        if self.df.empty:
            return
        
        # Convert timestamps
        self.df['created_datetime'] = pd.to_datetime(self.df['created_utc'], unit='s')
        self.df['hour'] = self.df['created_datetime'].dt.hour
        self.df['day_of_week'] = self.df['created_datetime'].dt.day_name()
        
        # Hourly posting pattern
        hourly_posts = self.df.groupby('hour').size()
        print("Posting patterns by hour:")
        for hour, count in hourly_posts.items():
            print(f"  {hour:02d}:00 - {count} posts")
        
        # Daily posting pattern
        daily_posts = self.df.groupby('day_of_week').size()
        print("\nPosting patterns by day:")
        for day, count in daily_posts.items():
            print(f"  {day}: {count} posts")
    
    def analyze_engagement_metrics(self):
        """Analyze engagement patterns."""
        if self.df.empty:
            return
        
        # Calculate engagement metrics
        self.df['engagement_ratio'] = self.df['num_comments'] / self.df['score'].replace(0, 1)
        self.df['comments_per_hour'] = self.df['num_comments'] / (
            (datetime.now().timestamp() - self.df['created_utc']) / 3600
        )
        
        # Top engaging posts
        top_engaging = self.df.nlargest(5, 'engagement_ratio')
        print("Top posts by engagement ratio (comments/score):")
        for _, post in top_engaging.iterrows():
            print(f"  {post['engagement_ratio']:.3f} - {post['title'][:50]}...")
        
        # Correlation analysis
        numeric_cols = ['score', 'num_comments', 'upvote_ratio']
        if all(col in self.df.columns for col in numeric_cols):
            correlation = self.df[numeric_cols].corr()
            print(f"\nCorrelation between score and comments: {correlation.loc['score', 'num_comments']:.3f}")
    
    def analyze_content_types(self):
        """Analyze content type distribution."""
        if self.df.empty:
            return
        
        # Content type analysis
        content_types = self.df['category'].value_counts() if 'category' in self.df.columns else {}
        print("Content type distribution:")
        for content_type, count in content_types.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {content_type}: {count} posts ({percentage:.1f}%)")
        
        # NSFW analysis
        if 'is_nsfw' in self.df.columns:
            nsfw_count = self.df['is_nsfw'].sum()
            nsfw_percentage = (nsfw_count / len(self.df)) * 100
            print(f"\nNSFW posts: {nsfw_count} ({nsfw_percentage:.1f}%)")
    
    def find_trending_topics(self):
        """Find trending topics from titles."""
        if self.df.empty:
            return
        
        # Simple keyword extraction
        all_titles = ' '.join(self.df['title'].astype(str)).lower()
        
        # Common programming/tech keywords
        keywords = ['python', 'javascript', 'react', 'machine learning', 'ai', 'data', 
                   'api', 'web', 'app', 'code', 'programming', 'software', 'tech']
        
        keyword_counts = {}
        for keyword in keywords:
            count = all_titles.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("Trending keywords in titles:")
        for keyword, count in sorted_keywords[:10]:
            print(f"  {keyword}: {count} mentions")


class CustomProcessor(PostProcessor):
    """Custom post processor with additional functionality."""
    
    def filter_by_engagement(self, posts: List[Dict[str, Any]], min_engagement: float = 0.1) -> List[Dict[str, Any]]:
        """Filter posts by engagement ratio."""
        filtered = []
        for post in posts:
            engagement = post.get('num_comments', 0) / max(post.get('score', 1), 1)
            if engagement >= min_engagement:
                filtered.append(post)
        return filtered
    
    def filter_by_keywords(self, posts: List[Dict[str, Any]], keywords: List[str], 
                          exclude: bool = False) -> List[Dict[str, Any]]:
        """Filter posts by keywords in title or text."""
        filtered = []
        for post in posts:
            title = post.get('title', '').lower()
            text = post.get('selftext', '').lower()
            content = f"{title} {text}"
            
            has_keyword = any(keyword.lower() in content for keyword in keywords)
            
            if (has_keyword and not exclude) or (not has_keyword and exclude):
                filtered.append(post)
        
        return filtered
    
    def add_sentiment_score(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add simple sentiment analysis (placeholder for real implementation)."""
        # This is a simplified example - in practice, you'd use a proper sentiment analysis library
        positive_words = ['good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'sucks']
        
        for post in posts:
            title = post.get('title', '').lower()
            text = post.get('selftext', '').lower()
            content = f"{title} {text}"
            
            positive_count = sum(1 for word in positive_words if word in content)
            negative_count = sum(1 for word in negative_words if word in content)
            
            # Simple sentiment score
            sentiment_score = positive_count - negative_count
            post['sentiment_score'] = sentiment_score
            
            if sentiment_score > 0:
                post['sentiment'] = 'positive'
            elif sentiment_score < 0:
                post['sentiment'] = 'negative'
            else:
                post['sentiment'] = 'neutral'
        
        return posts


def example_advanced_filtering():
    """Advanced filtering techniques."""
    print("=== Advanced Filtering Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts
    posts = client.get_subreddit_posts("technology", "top", 100, "week")
    print(f"Retrieved {len(posts)} posts")
    
    # Use custom processor
    processor = CustomProcessor(min_score=10)
    
    # Filter by engagement
    engaging_posts = processor.filter_by_engagement(posts, min_engagement=0.2)
    print(f"High engagement posts: {len(engaging_posts)}")
    
    # Filter by keywords
    ai_posts = processor.filter_by_keywords(posts, ['AI', 'artificial intelligence', 'machine learning'])
    print(f"AI-related posts: {len(ai_posts)}")
    
    # Add sentiment analysis
    posts_with_sentiment = processor.add_sentiment_score(posts)
    
    # Analyze sentiment distribution
    sentiment_counts = {}
    for post in posts_with_sentiment:
        sentiment = post.get('sentiment', 'neutral')
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    print("Sentiment distribution:")
    for sentiment, count in sentiment_counts.items():
        print(f"  {sentiment}: {count} posts")


def example_data_analysis():
    """Advanced data analysis example."""
    print("\n=== Data Analysis Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Collect data from multiple subreddits
    subreddits = ["datascience", "MachineLearning", "statistics"]
    all_posts = []
    
    for subreddit in subreddits:
        posts = client.get_subreddit_posts(subreddit, "top", 50, "month")
        all_posts.extend(posts)
    
    print(f"Collected {len(all_posts)} posts for analysis")
    
    # Perform advanced analysis
    analyzer = AdvancedAnalyzer(all_posts)
    analyzer.analyze_posting_patterns()
    analyzer.analyze_engagement_metrics()
    analyzer.analyze_content_types()
    analyzer.find_trending_topics()


def example_custom_export():
    """Custom export format example."""
    print("\n=== Custom Export Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts
    posts = client.get_subreddit_posts("programming", "hot", 30)
    
    # Custom export to Excel with multiple sheets
    try:
        import pandas as pd
        
        # Create DataFrames
        posts_df = pd.DataFrame(posts)
        
        # Summary statistics
        summary_stats = {
            'Total Posts': len(posts),
            'Average Score': posts_df['score'].mean() if not posts_df.empty else 0,
            'Average Comments': posts_df['num_comments'].mean() if not posts_df.empty else 0,
            'Unique Authors': posts_df['author'].nunique() if not posts_df.empty else 0
        }
        
        summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
        
        # Export to Excel
        output_file = "../output/examples/advanced_export.xlsx"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            posts_df.to_excel(writer, sheet_name='Posts', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Exported to Excel: {output_file}")
        
    except ImportError:
        print("pandas and openpyxl required for Excel export")
        
        # Fallback to custom JSON export
        custom_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_posts': len(posts),
                'subreddit': 'programming'
            },
            'posts': posts,
            'summary': {
                'avg_score': sum(p.get('score', 0) for p in posts) / len(posts) if posts else 0,
                'top_authors': list(set(p.get('author', '') for p in posts))[:10]
            }
        }
        
        output_file = "../output/examples/custom_export.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(custom_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported custom JSON: {output_file}")


def example_batch_processing():
    """Batch processing example for large-scale scraping."""
    print("\n=== Batch Processing Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    rate_limiter = RateLimiter(requests_per_second=0.8)  # Conservative rate
    
    # Define batch job
    batch_config = {
        'subreddits': ['python', 'datascience', 'MachineLearning', 'programming', 'technology'],
        'posts_per_subreddit': 100,
        'sort_type': 'top',
        'time_filter': 'week'
    }
    
    all_posts = []
    failed_subreddits = []
    
    print(f"Starting batch job: {len(batch_config['subreddits'])} subreddits")
    
    for i, subreddit in enumerate(batch_config['subreddits']):
        print(f"[{i+1}/{len(batch_config['subreddits'])}] Processing r/{subreddit}...")
        
        try:
            posts = rate_limiter.retry_with_backoff(
                client.get_subreddit_posts,
                subreddit,
                batch_config['sort_type'],
                batch_config['posts_per_subreddit'],
                batch_config['time_filter']
            )
            
            if posts:
                all_posts.extend(posts)
                print(f"  ✓ Retrieved {len(posts)} posts")
            else:
                failed_subreddits.append(subreddit)
                print(f"  ✗ No posts retrieved")
                
        except Exception as e:
            failed_subreddits.append(subreddit)
            print(f"  ✗ Error: {e}")
    
    print(f"\nBatch job completed:")
    print(f"  Total posts: {len(all_posts)}")
    print(f"  Successful subreddits: {len(batch_config['subreddits']) - len(failed_subreddits)}")
    print(f"  Failed subreddits: {failed_subreddits}")
    
    # Process and export batch results
    if all_posts:
        processor = PostProcessor(min_score=5)
        processed_posts = processor.filter_posts(all_posts)
        processed_posts = processor.add_derived_fields(processed_posts)
        
        # Export batch results
        exporter = JSONExporter(output_dir="../output/examples")
        batch_file = exporter.export_combined(processed_posts, filename="batch_results.json")
        print(f"  Exported batch results: {batch_file}")


def example_real_time_monitoring():
    """Real-time monitoring example (simplified)."""
    print("\n=== Real-time Monitoring Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Monitor specific subreddits for new posts
    monitor_subreddits = ['python', 'programming']
    seen_posts = set()
    
    print(f"Starting monitoring for: {', '.join(monitor_subreddits)}")
    print("(This is a simplified example - in practice, you'd run this continuously)")
    
    for subreddit in monitor_subreddits:
        # Get latest posts
        latest_posts = client.get_subreddit_posts(subreddit, "new", 10)
        
        new_posts = []
        for post in latest_posts:
            post_id = post.get('id')
            if post_id not in seen_posts:
                seen_posts.add(post_id)
                new_posts.append(post)
        
        if new_posts:
            print(f"\nNew posts in r/{subreddit}:")
            for post in new_posts:
                print(f"  • {post['title'][:60]}... (Score: {post['score']})")
        else:
            print(f"\nNo new posts in r/{subreddit}")


def example_visualization_data():
    """Prepare data for visualization."""
    print("\n=== Visualization Data Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts for visualization
    posts = client.get_subreddit_posts("datascience", "top", 100, "month")
    
    if not posts:
        print("No posts retrieved for visualization")
        return
    
    # Prepare visualization data
    viz_data = {
        'scores': [p.get('score', 0) for p in posts],
        'comments': [p.get('num_comments', 0) for p in posts],
        'hours': [datetime.fromtimestamp(p.get('created_utc', 0)).hour for p in posts],
        'title_lengths': [len(p.get('title', '')) for p in posts]
    }
    
    # Save visualization data
    output_file = "../output/examples/visualization_data.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(viz_data, f, indent=2)
    
    print(f"Visualization data saved: {output_file}")
    
    # Basic statistics
    print("\nBasic statistics:")
    print(f"  Score range: {min(viz_data['scores'])} - {max(viz_data['scores'])}")
    print(f"  Average comments: {sum(viz_data['comments']) / len(viz_data['comments']):.1f}")
    print(f"  Most active hour: {max(set(viz_data['hours']), key=viz_data['hours'].count)}")


if __name__ == "__main__":
    print("Reddit Scraper - Advanced Usage Examples")
    print("=" * 50)
    
    try:
        example_advanced_filtering()
        example_data_analysis()
        example_custom_export()
        example_batch_processing()
        example_real_time_monitoring()
        example_visualization_data()
        
        print("\n" + "=" * 50)
        print("Advanced examples completed!")
        print("\nThese examples demonstrate:")
        print("1. Custom filtering and processing")
        print("2. Advanced data analysis techniques")
        print("3. Custom export formats")
        print("4. Batch processing workflows")
        print("5. Real-time monitoring concepts")
        print("6. Data preparation for visualization")
        
    except Exception as e:
        print(f"\nError running advanced examples: {e}")
        print("Make sure you have:")
        print("1. All dependencies installed")
        print("2. Reddit API configured")
        print("3. Optional: pandas, openpyxl for Excel export")
        print("4. Optional: matplotlib, seaborn for visualization")