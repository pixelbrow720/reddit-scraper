#!/usr/bin/env python3
"""
Showcase All Features - Reddit Scraper
Demonstrates all advanced features including HTML export, parallel processing,
content extraction, and performance monitoring.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.cli.config import Config
from src.core.reddit_client import RedditClient
from src.core.parallel_scraper import ParallelScraper, AsyncScraper
from src.core.performance_monitor import PerformanceMonitor, performance_monitor, MemoryOptimizer
from src.processors.post_processor import PostProcessor
from src.processors.content_extractor import ContentExtractor
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.html_exporter import HTMLExporter


def showcase_html_export():
    """Showcase HTML export with dark theme and interactive charts."""
    print("=== HTML Export Showcase ===")
    
    # Sample data for demonstration
    sample_posts = [
        {
            'id': f'post_{i}',
            'title': f'Sample Post {i}: {"AI and Machine Learning" if i % 3 == 0 else "Python Programming" if i % 3 == 1 else "Data Science"}',
            'author': f'user_{i % 10}',
            'subreddit': ['python', 'MachineLearning', 'datascience'][i % 3],
            'score': 50 + i * 10,
            'upvote_ratio': 0.8 + (i % 5) * 0.04,
            'num_comments': 10 + i * 3,
            'created_utc': 1640995200 + i * 3600,
            'url': f'https://reddit.com/r/test/comments/post_{i}',
            'permalink': f'/r/test/comments/post_{i}',
            'selftext': f'This is sample content for post {i}. It demonstrates various features.',
            'flair': ['Discussion', 'Tutorial', 'Question', 'News'][i % 4],
            'is_nsfw': False,
            'is_spoiler': False,
            'is_self': i % 2 == 0,
            'domain': 'self.test' if i % 2 == 0 else 'example.com',
            'category': ['text', 'link', 'discussion', 'tutorial'][i % 4],
            'engagement_ratio': (10 + i * 3) / (50 + i * 10),
            'created_date': '2024-01-01',
            'created_hour': (i * 2) % 24,
            'created_weekday': i % 7
        }
        for i in range(50)
    ]
    
    sample_users = [
        {
            'username': f'user_{i}',
            'id': f'user_id_{i}',
            'created_utc': 1234567890 + i * 86400,
            'comment_karma': 1000 + i * 100,
            'link_karma': 500 + i * 50,
            'is_verified': i % 5 == 0,
            'has_premium': i % 7 == 0,
            'profile_description': f'Sample user {i} description'
        }
        for i in range(10)
    ]
    
    # Export HTML report
    html_exporter = HTMLExporter(output_dir="../output/showcase", dark_theme=True)
    html_file = html_exporter.export_posts_report(
        sample_posts, 
        sample_users, 
        "showcase_report.html"
    )
    
    print(f"✓ Generated interactive HTML report: {html_file}")
    print("  Features included:")
    print("    • Dark theme design")
    print("    • Interactive charts (Chart.js)")
    print("    • Responsive layout")
    print("    • Summary statistics")
    print("    �� Top posts analysis")
    print("    • Subreddit breakdown")
    print("    • User analysis")
    
    return html_file


def showcase_parallel_processing():
    """Showcase parallel processing capabilities."""
    print("\n=== Parallel Processing Showcase ===")
    
    config = Config("../config/settings.yaml")
    
    if not config.validate_reddit_config():
        print("⚠️  Reddit API not configured. Using mock data for demonstration.")
        return
    
    reddit_config = config.get_reddit_config()
    
    # Test subreddits
    test_subreddits = ['python', 'programming', 'datascience', 'MachineLearning', 'technology']
    
    print(f"Testing parallel scraping with {len(test_subreddits)} subreddits...")
    
    # Initialize parallel scraper
    parallel_scraper = ParallelScraper(
        reddit_config=reddit_config,
        max_workers=3,
        rate_limit=1.0,
        use_processes=False  # Use threads for this demo
    )
    
    # Add progress callback
    def progress_callback(completed, total):
        print(f"  Progress: {completed}/{total} subreddits completed")
    
    parallel_scraper.add_progress_callback(progress_callback)
    
    try:
        # Execute parallel scraping
        results = parallel_scraper.scrape_multiple_subreddits(
            subreddits=test_subreddits,
            sort_type='hot',
            posts_per_subreddit=10,  # Small number for demo
            time_filter='day'
        )
        
        # Display results
        successful = sum(1 for r in results if r.success)
        total_posts = sum(len(r.posts) for r in results if r.success)
        
        print(f"✓ Parallel scraping completed:")
        print(f"    • Success rate: {successful}/{len(results)} subreddits")
        print(f"    • Total posts collected: {total_posts}")
        
        # Get summary statistics
        summary = parallel_scraper.get_summary_statistics()
        print(f"    • Average duration per task: {summary.get('avg_duration_per_task', 0):.2f}s")
        print(f"    • Posts per second: {summary.get('posts_per_second', 0):.2f}")
        
        return results
        
    except Exception as e:
        print(f"⚠️  Parallel processing demo failed: {e}")
        return []


def showcase_content_extraction():
    """Showcase content extraction from external links."""
    print("\n=== Content Extraction Showcase ===")
    
    # Sample posts with external links
    sample_posts = [
        {
            'id': 'post_1',
            'title': 'Interesting GitHub Repository',
            'url': 'https://github.com/python/cpython',
            'is_self': False,
            'domain': 'github.com'
        },
        {
            'id': 'post_2',
            'title': 'Great Article on Medium',
            'url': 'https://medium.com/@example/article',
            'is_self': False,
            'domain': 'medium.com'
        },
        {
            'id': 'post_3',
            'title': 'Self Post',
            'url': 'https://reddit.com/r/test',
            'is_self': True,
            'domain': 'reddit.com'
        }
    ]
    
    # Initialize content extractor
    content_extractor = ContentExtractor(timeout=10, max_workers=2, rate_limit=0.5)
    
    print("Extracting content from external links...")
    print("Note: This is a demonstration - actual extraction depends on website availability")
    
    try:
        # Extract content
        enhanced_posts = content_extractor.extract_content_from_posts(sample_posts)
        
        # Display results
        extracted_count = sum(1 for post in enhanced_posts if post.get('extracted_content'))
        
        print(f"✓ Content extraction completed:")
        print(f"    • Posts processed: {len(enhanced_posts)}")
        print(f"    • Content extracted: {extracted_count} posts")
        
        # Show extracted content examples
        for post in enhanced_posts:
            if post.get('extracted_content'):
                content = post['extracted_content']
                print(f"    • {post['id']}: {content.get('title', 'No title')[:50]}...")
        
        return enhanced_posts
        
    except Exception as e:
        print(f"⚠️  Content extraction demo failed: {e}")
        return sample_posts


def showcase_performance_monitoring():
    """Showcase performance monitoring capabilities."""
    print("\n=== Performance Monitoring Showcase ===")
    
    # Initialize performance monitor
    monitor = PerformanceMonitor(
        enable_memory_tracking=True,
        enable_cpu_tracking=True,
        save_to_file=True,
        output_dir="../logs"
    )
    
    print("Running performance-monitored operations...")
    
    # Demonstrate performance monitoring with decorator
    @performance_monitor(monitor, "data_processing_demo")
    def process_large_dataset():
        """Simulate data processing."""
        import time
        import random
        
        # Simulate processing
        data = [random.randint(1, 1000) for _ in range(10000)]
        
        # Simulate some work
        result = []
        for i, item in enumerate(data):
            if i % 1000 == 0:
                time.sleep(0.01)  # Simulate I/O
            result.append(item * 2)
        
        return result
    
    # Run monitored operations
    result = process_large_dataset()
    
    # Manual monitoring example
    op_id = monitor.start_operation("manual_operation_demo", data_size=len(result))
    
    # Simulate more work
    import time
    time.sleep(0.1)
    
    monitor.end_operation(op_id, success=True, result_size=len(result))
    
    # Get performance summary
    summary = monitor.get_summary_statistics()
    
    print("✓ Performance monitoring completed:")
    print(f"    • Total operations monitored: {summary.get('overall', {}).get('total_operations', 0)}")
    print(f"    • Success rate: {summary.get('overall', {}).get('success_rate', 0):.1f}%")
    print(f"    • Average duration: {summary.get('overall', {}).get('avg_duration', 0):.3f}s")
    
    # Check for slow operations
    slow_ops = monitor.get_slow_operations(threshold_seconds=0.05)
    if slow_ops:
        print(f"    • Slow operations detected: {len(slow_ops)}")
    
    # Export performance metrics
    perf_file = monitor.export_metrics("showcase_performance.json")
    print(f"    • Performance metrics exported: {perf_file}")
    
    # Memory optimization demo
    print("\n  Memory Optimization Demo:")
    memory_info = MemoryOptimizer.get_memory_info()
    print(f"    • Current memory usage: {memory_info['rss_mb']:.1f} MB")
    print(f"    • Memory percentage: {memory_info['percent']:.1f}%")
    
    # Demonstrate chunk processing
    large_data = list(range(1000))
    
    def process_chunk(chunk):
        return [x * 2 for x in chunk]
    
    results = MemoryOptimizer.process_in_chunks(large_data, chunk_size=100, processor=process_chunk)
    print(f"    • Processed {len(large_data)} items in {len(results)} chunks")
    
    return monitor


async def showcase_async_scraping():
    """Showcase async scraping capabilities."""
    print("\n=== Async Scraping Showcase ===")
    
    config = Config("../config/settings.yaml")
    
    if not config.validate_reddit_config():
        print("⚠️  Reddit API not configured. Skipping async demo.")
        return
    
    reddit_config = config.get_reddit_config()
    
    # Initialize async scraper
    async_scraper = AsyncScraper(
        reddit_config=reddit_config,
        max_concurrent=5,
        rate_limit=2.0
    )
    
    test_subreddits = ['python', 'programming', 'datascience']
    
    print(f"Testing async scraping with {len(test_subreddits)} subreddits...")
    
    try:
        # Execute async scraping
        results = await async_scraper.scrape_subreddits_async(
            subreddits=test_subreddits,
            sort_type='hot',
            limit=5,  # Small number for demo
            time_filter='day'
        )
        
        # Display results
        successful = sum(1 for r in results if r.success)
        total_posts = sum(len(r.posts) for r in results if r.success)
        
        print(f"✓ Async scraping completed:")
        print(f"    • Success rate: {successful}/{len(results)} subreddits")
        print(f"    • Total posts collected: {total_posts}")
        
        return results
        
    except Exception as e:
        print(f"⚠️  Async scraping demo failed: {e}")
        return []


def showcase_advanced_filtering():
    """Showcase advanced filtering and processing."""
    print("\n=== Advanced Filtering Showcase ===")
    
    # Generate sample data with various characteristics
    sample_posts = []
    for i in range(100):
        post = {
            'id': f'post_{i}',
            'title': f'Sample Post {i}',
            'author': f'user_{i % 20}' if i % 10 != 0 else '[deleted]',
            'score': i * 5 + (i % 3) * 10,
            'num_comments': i * 2,
            'created_utc': 1640995200 + i * 3600,
            'is_nsfw': i % 15 == 0,
            'selftext': f'Content for post {i}' if i % 5 != 0 else '[deleted]',
            'subreddit': ['python', 'datascience', 'MachineLearning'][i % 3]
        }
        sample_posts.append(post)
    
    print(f"Starting with {len(sample_posts)} sample posts")
    
    # Initialize processor with strict filtering
    processor = PostProcessor(
        min_score=50,
        max_age_days=30,
        exclude_nsfw=True,
        exclude_deleted=True
    )
    
    # Apply filtering
    filtered_posts = processor.filter_posts(sample_posts)
    print(f"After filtering: {len(filtered_posts)} posts")
    
    # Deduplicate (add some duplicates first)
    sample_posts.extend(sample_posts[:5])  # Add duplicates
    deduplicated = processor.deduplicate_posts(sample_posts)
    print(f"After deduplication: {len(deduplicated)} posts (removed {len(sample_posts) - len(deduplicated)} duplicates)")
    
    # Add derived fields
    enhanced_posts = processor.add_derived_fields(filtered_posts)
    
    # Analyze categories
    categories = {}
    for post in enhanced_posts:
        cat = post.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("✓ Advanced filtering completed:")
    print(f"    • Final posts: {len(enhanced_posts)}")
    print("    • Categories found:")
    for category, count in categories.items():
        print(f"      - {category}: {count} posts")
    
    # Show engagement analysis
    if enhanced_posts:
        avg_engagement = sum(post.get('engagement_ratio', 0) for post in enhanced_posts) / len(enhanced_posts)
        print(f"    • Average engagement ratio: {avg_engagement:.3f}")
    
    return enhanced_posts


def main():
    """Run all feature showcases."""
    print("🚀 Reddit Scraper - All Features Showcase")
    print("=" * 60)
    
    try:
        # Create output directories
        os.makedirs("../output/showcase", exist_ok=True)
        os.makedirs("../logs", exist_ok=True)
        
        # Run showcases
        html_file = showcase_html_export()
        parallel_results = showcase_parallel_processing()
        extracted_posts = showcase_content_extraction()
        monitor = showcase_performance_monitoring()
        filtered_posts = showcase_advanced_filtering()
        
        # Run async showcase
        print("\nRunning async showcase...")
        try:
            async_results = asyncio.run(showcase_async_scraping())
        except Exception as e:
            print(f"⚠️  Async showcase failed: {e}")
            async_results = []
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 All Features Showcase Completed!")
        print("\nFeatures demonstrated:")
        print("  ✓ HTML Export with dark theme and interactive charts")
        print("  ✓ Parallel processing for multiple subreddits")
        print("  ✓ Content extraction from external links")
        print("  ✓ Performance monitoring and optimization")
        print("  ✓ Advanced filtering and data processing")
        print("  ✓ Async scraping capabilities")
        
        print(f"\nGenerated files:")
        if html_file and os.path.exists(html_file):
            print(f"  📊 HTML Report: {os.path.abspath(html_file)}")
        
        # List other generated files
        output_dir = "../output/showcase"
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file != "showcase_report.html":
                    print(f"  📄 {file}: {os.path.abspath(os.path.join(output_dir, file))}")
        
        logs_dir = "../logs"
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if file.endswith('.json'):
                    print(f"  📈 Performance: {os.path.abspath(os.path.join(logs_dir, file))}")
        
        print("\nTo view the HTML report, open it in your web browser:")
        if html_file:
            print(f"  file://{os.path.abspath(html_file)}")
        
        print("\n🔧 Next steps:")
        print("  1. Configure Reddit API credentials: python run.py setup")
        print("  2. Try parallel scraping: python run.py scrape --subreddit 'python,datascience' --parallel")
        print("  3. Generate HTML reports: python run.py scrape --output html --subreddit python")
        print("  4. Enable performance monitoring: python run.py scrape --performance-monitor")
        
    except Exception as e:
        print(f"\n❌ Showcase failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()