#!/usr/bin/env python3
"""
Basic Usage Examples for Reddit Scraper
This file demonstrates common usage patterns and examples.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.cli.config import Config
from src.core.reddit_client import RedditClient
from src.core.rate_limiter import RateLimiter
from src.processors.post_processor import PostProcessor
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter


def example_basic_scraping():
    """Basic scraping example."""
    print("=== Basic Scraping Example ===")
    
    # Load configuration
    config = Config("../config/settings.yaml")
    
    if not config.validate_reddit_config():
        print("Please configure Reddit API credentials first!")
        print("Run: python run.py setup")
        return
    
    # Initialize components
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Test connection
    if not client.test_connection():
        print("Failed to connect to Reddit API")
        return
    
    # Scrape posts
    print("Scraping r/python...")
    posts = client.get_subreddit_posts(
        subreddit_name="python",
        sort_type="hot",
        limit=10
    )
    
    print(f"Retrieved {len(posts)} posts")
    
    # Display sample post
    if posts:
        post = posts[0]
        print(f"\nSample post:")
        print(f"Title: {post['title'][:50]}...")
        print(f"Author: {post['author']}")
        print(f"Score: {post['score']}")
        print(f"Comments: {post['num_comments']}")


def example_filtered_scraping():
    """Filtered scraping example."""
    print("\n=== Filtered Scraping Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts
    posts = client.get_subreddit_posts("datascience", "top", 50, "week")
    print(f"Retrieved {len(posts)} posts from r/datascience")
    
    # Filter posts
    processor = PostProcessor(
        min_score=20,           # Minimum 20 upvotes
        exclude_nsfw=True,      # No NSFW content
        exclude_deleted=True    # No deleted posts
    )
    
    filtered_posts = processor.filter_posts(posts)
    print(f"After filtering: {len(filtered_posts)} posts")
    
    # Add derived fields
    enhanced_posts = processor.add_derived_fields(filtered_posts)
    
    # Show categories
    categories = {}
    for post in enhanced_posts:
        cat = post.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nPost categories:")
    for category, count in categories.items():
        print(f"  {category}: {count}")


def example_user_profiles():
    """User profile scraping example."""
    print("\n=== User Profile Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    rate_limiter = RateLimiter(requests_per_second=0.5)  # Slower for user profiles
    
    # Get some posts first
    posts = client.get_subreddit_posts("AskReddit", "hot", 5)
    
    # Get user profiles
    users = []
    for post in posts:
        author = post.get('author')
        if author and author != '[deleted]':
            print(f"Getting profile for u/{author}...")
            
            user_data = rate_limiter.retry_with_backoff(
                client.get_user_profile, author
            )
            
            if user_data:
                users.append(user_data)
                print(f"  Karma: {user_data['comment_karma']} comment, {user_data['link_karma']} link")
    
    print(f"\nRetrieved {len(users)} user profiles")


def example_export_data():
    """Data export example."""
    print("\n=== Data Export Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts
    posts = client.get_subreddit_posts("programming", "hot", 20)
    
    # Process posts
    processor = PostProcessor(min_score=5)
    posts = processor.filter_posts(posts)
    posts = processor.add_derived_fields(posts)
    
    # Export to JSON
    json_exporter = JSONExporter(output_dir="../output/examples")
    json_file = json_exporter.export_posts(posts, "example_posts.json")
    print(f"Exported to JSON: {json_file}")
    
    # Export to CSV
    csv_exporter = CSVExporter(output_dir="../output/examples")
    csv_file = csv_exporter.export_posts(posts, "example_posts.csv")
    print(f"Exported to CSV: {csv_file}")
    
    # Export summary statistics
    summary_file = csv_exporter.export_summary_stats(posts, "example_summary.csv")
    print(f"Exported summary: {summary_file}")


def example_multi_subreddit():
    """Multi-subreddit scraping example."""
    print("\n=== Multi-Subreddit Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    rate_limiter = RateLimiter(requests_per_second=1.0)
    
    subreddits = ["python", "datascience", "MachineLearning"]
    all_posts = []
    
    for subreddit in subreddits:
        print(f"Scraping r/{subreddit}...")
        
        posts = rate_limiter.retry_with_backoff(
            client.get_subreddit_posts,
            subreddit, "hot", 15
        )
        
        if posts:
            all_posts.extend(posts)
            print(f"  Got {len(posts)} posts")
    
    print(f"\nTotal posts collected: {len(all_posts)}")
    
    # Analyze subreddit distribution
    subreddit_counts = {}
    for post in all_posts:
        sub = post.get('subreddit', '')
        subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
    
    print("\nSubreddit distribution:")
    for sub, count in subreddit_counts.items():
        print(f"  r/{sub}: {count} posts")


def example_advanced_filtering():
    """Advanced filtering example."""
    print("\n=== Advanced Filtering Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    
    # Get posts
    posts = client.get_subreddit_posts("technology", "top", 100, "week")
    print(f"Retrieved {len(posts)} posts")
    
    # Custom filtering
    def custom_filter(posts):
        filtered = []
        for post in posts:
            # Only posts with high engagement
            engagement = post.get('num_comments', 0) / max(post.get('score', 1), 1)
            
            # Filter criteria
            if (post.get('score', 0) >= 50 and 
                engagement >= 0.1 and 
                len(post.get('title', '')) >= 20):
                filtered.append(post)
        
        return filtered
    
    custom_filtered = custom_filter(posts)
    print(f"After custom filtering: {len(custom_filtered)} posts")
    
    # Show top posts by engagement
    custom_filtered.sort(key=lambda p: p.get('num_comments', 0) / max(p.get('score', 1), 1), reverse=True)
    
    print("\nTop posts by engagement ratio:")
    for i, post in enumerate(custom_filtered[:5]):
        engagement = post.get('num_comments', 0) / max(post.get('score', 1), 1)
        print(f"{i+1}. {post['title'][:60]}...")
        print(f"   Score: {post['score']}, Comments: {post['num_comments']}, Ratio: {engagement:.3f}")


def example_error_handling():
    """Error handling example."""
    print("\n=== Error Handling Example ===")
    
    config = Config("../config/settings.yaml")
    reddit_config = config.get_reddit_config()
    client = RedditClient(**reddit_config)
    rate_limiter = RateLimiter(requests_per_second=1.0, max_retries=2)
    
    # Try to scrape from various subreddits, some might fail
    test_subreddits = ["python", "nonexistentsubreddit123", "programming", "privatetestsubreddit"]
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for subreddit in test_subreddits:
        print(f"Trying r/{subreddit}...")
        
        try:
            posts = rate_limiter.retry_with_backoff(
                client.get_subreddit_posts,
                subreddit, "hot", 5
            )
            
            if posts:
                print(f"  ✓ Success: {len(posts)} posts")
                successful_scrapes += 1
            else:
                print(f"  ✗ No posts retrieved")
                failed_scrapes += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_scrapes += 1
    
    print(f"\nResults: {successful_scrapes} successful, {failed_scrapes} failed")


if __name__ == "__main__":
    print("Reddit Scraper - Usage Examples")
    print("=" * 40)
    
    try:
        example_basic_scraping()
        example_filtered_scraping()
        example_user_profiles()
        example_export_data()
        example_multi_subreddit()
        example_advanced_filtering()
        example_error_handling()
        
        print("\n" + "=" * 40)
        print("All examples completed!")
        print("\nNext steps:")
        print("1. Try running: python run.py scrape --subreddit python --posts 50")
        print("2. Check the output/ directory for exported files")
        print("3. Explore the configuration options in config/settings.yaml")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have:")
        print("1. Installed all dependencies: pip install -r requirements.txt")
        print("2. Configured Reddit API: python run.py setup")
        print("3. Valid internet connection")