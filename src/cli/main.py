"""Main CLI interface for Reddit scraper."""

import click
import logging
import os
import sys
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.config import Config, create_default_config_file
from src.core.reddit_client import RedditClient
from src.core.rate_limiter import RateLimiter
from src.processors.post_processor import PostProcessor
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.html_exporter import HTMLExporter
from src.processors.content_extractor import ContentExtractor
from src.core.parallel_scraper import ParallelScraper
from src.core.performance_monitor import PerformanceMonitor, performance_monitor

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', default='config/settings.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Reddit Scraper - A comprehensive tool for scraping Reddit data."""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    
    # Load configuration
    config_obj = Config(config)
    config_obj.setup_logging()
    ctx.obj['config'] = config_obj


@cli.command()
@click.option('--client-id', prompt='Reddit Client ID', help='Reddit app client ID')
@click.option('--client-secret', prompt='Reddit Client Secret', hide_input=True, 
              help='Reddit app client secret')
@click.option('--user-agent', default='RedditScraper/1.0', help='User agent string')
@click.pass_context
def setup(ctx, client_id, client_secret, user_agent):
    """Setup Reddit API configuration."""
    config = ctx.obj['config']
    
    # Setup Reddit configuration
    config.setup_reddit_config(client_id, client_secret, user_agent)
    config.save_config()
    
    # Test connection
    console.print("[yellow]Testing Reddit API connection...[/yellow]")
    
    try:
        reddit_config = config.get_reddit_config()
        client = RedditClient(**reddit_config)
        
        if client.test_connection():
            console.print("[green]✓ Reddit API connection successful![/green]")
            console.print(f"Configuration saved to {config.config_file}")
        else:
            console.print("[red]✗ Reddit API connection failed![/red]")
            console.print("Please check your credentials and try again.")
            
    except Exception as e:
        console.print(f"[red]Error testing connection: {e}[/red]")


@cli.command()
@click.option('--subreddit', '-s', help='Subreddit name(s), comma-separated')
@click.option('--posts', '-p', default=100, help='Number of posts to scrape')
@click.option('--sort', default='hot', type=click.Choice(['hot', 'new', 'top', 'rising']),
              help='Sort type for posts')
@click.option('--time-filter', default='all', 
              type=click.Choice(['hour', 'day', 'week', 'month', 'year', 'all']),
              help='Time filter for top posts')
@click.option('--output', '-o', default='json,csv', help='Output formats (comma-separated: json,csv,html)')
@click.option('--include-users', is_flag=True, help='Include user profile data')
@click.option('--min-score', default=None, type=int, help='Minimum post score')
@click.option('--exclude-nsfw', is_flag=True, default=True, help='Exclude NSFW posts')
@click.option('--extract-content', is_flag=True, help='Extract content from external links')
@click.option('--parallel', is_flag=True, help='Use parallel processing for multiple subreddits')
@click.option('--max-workers', default=5, type=int, help='Maximum parallel workers')
@click.option('--performance-monitor', is_flag=True, help='Enable performance monitoring')
@click.pass_context
def scrape(ctx, subreddit, posts, sort, time_filter, output, include_users, min_score, exclude_nsfw, 
           extract_content, parallel, max_workers, performance_monitor):
    """Scrape Reddit posts and data."""
    config = ctx.obj['config']
    
    # Validate Reddit configuration
    if not config.validate_reddit_config():
        console.print("[red]Reddit API not configured. Run 'setup' command first.[/red]")
        return
    
    # Parse subreddits
    if subreddit:
        subreddits = [s.strip() for s in subreddit.split(',')]
    else:
        console.print("[red]Please specify at least one subreddit with --subreddit[/red]")
        return
    
    # Parse output formats
    output_formats = [f.strip().lower() for f in output.split(',')]
    
    # Setup components
    reddit_config = config.get_reddit_config()
    scraping_config = config.get_scraping_config()
    filtering_config = config.get_filtering_config()
    
    # Override filtering config with CLI options
    if min_score is not None:
        filtering_config['min_score'] = min_score
    filtering_config['exclude_nsfw'] = exclude_nsfw
    
    client = RedditClient(**reddit_config)
    rate_limiter = RateLimiter(
        requests_per_second=scraping_config['rate_limit'],
        max_retries=scraping_config['max_retries']
    )
    processor = PostProcessor(**filtering_config)
    
    # Initialize performance monitor if requested
    perf_monitor = None
    if performance_monitor:
        perf_monitor = PerformanceMonitor(save_to_file=True)
        console.print("[yellow]Performance monitoring enabled[/yellow]")
    
    # Initialize exporters
    json_exporter = JSONExporter() if 'json' in output_formats else None
    csv_exporter = CSVExporter() if 'csv' in output_formats else None
    html_exporter = HTMLExporter() if 'html' in output_formats else None
    
    # Initialize content extractor if requested
    content_extractor = None
    if extract_content:
        content_extractor = ContentExtractor(max_workers=max_workers)
        console.print("[yellow]Content extraction enabled[/yellow]")
    
    console.print(Panel.fit(
        f"[bold]Reddit Scraper[/bold]\n"
        f"Subreddits: {', '.join(subreddits)}\n"
        f"Posts per subreddit: {posts}\n"
        f"Sort: {sort}\n"
        f"Output formats: {', '.join(output_formats)}",
        title="Scraping Configuration"
    ))
    
    all_posts = []
    all_users = []
    
    # Choose scraping method based on parallel flag
    if parallel and len(subreddits) > 1:
        console.print(f"[yellow]Using parallel processing with {max_workers} workers[/yellow]")
        
        # Use parallel scraper
        parallel_scraper = ParallelScraper(
            reddit_config=reddit_config,
            max_workers=max_workers,
            rate_limit=scraping_config['rate_limit']
        )
        
        # Add progress callback
        def progress_callback(completed, total):
            console.print(f"Progress: {completed}/{total} subreddits completed")
        
        parallel_scraper.add_progress_callback(progress_callback)
        
        # Start performance monitoring if enabled
        scrape_op_id = None
        if perf_monitor:
            scrape_op_id = perf_monitor.start_operation("parallel_scraping", subreddits=len(subreddits))
        
        # Execute parallel scraping
        results = parallel_scraper.scrape_multiple_subreddits(
            subreddits=subreddits,
            sort_type=sort,
            posts_per_subreddit=posts,
            time_filter=time_filter
        )
        
        # End performance monitoring
        if perf_monitor and scrape_op_id:
            perf_monitor.end_operation(scrape_op_id, success=True)
        
        # Collect results
        for result in results:
            if result.success:
                all_posts.extend(result.posts)
                console.print(f"[green]✓[/green] Retrieved {len(result.posts)} posts from r/{result.subreddit}")
            else:
                console.print(f"[red]✗[/red] Failed to retrieve posts from r/{result.subreddit}: {result.error}")
        
        # Get summary statistics
        summary = parallel_scraper.get_summary_statistics()
        console.print(f"\n[bold]Parallel Scraping Summary:[/bold]")
        console.print(f"Success rate: {summary.get('success_rate', 0):.1f}%")
        console.print(f"Total posts: {summary.get('total_posts', 0)}")
        console.print(f"Average duration per task: {summary.get('avg_duration_per_task', 0):.2f}s")
        
    else:
        # Use sequential scraping
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Scraping subreddits...", total=len(subreddits))
            
            for sub in subreddits:
                progress.update(main_task, description=f"Scraping r/{sub}...")
                
                # Start performance monitoring if enabled
                sub_op_id = None
                if perf_monitor:
                    sub_op_id = perf_monitor.start_operation("scrape_subreddit", subreddit=sub)
                
                # Get posts with rate limiting
                posts_data = rate_limiter.retry_with_backoff(
                    client.get_subreddit_posts,
                    sub, sort, posts, time_filter
                )
                
                # End performance monitoring
                if perf_monitor and sub_op_id:
                    perf_monitor.end_operation(sub_op_id, success=bool(posts_data), posts_count=len(posts_data) if posts_data else 0)
                
                if posts_data:
                    console.print(f"[green]✓[/green] Retrieved {len(posts_data)} posts from r/{sub}")
                    all_posts.extend(posts_data)
                else:
                    console.print(f"[red]✗[/red] Failed to retrieve posts from r/{sub}")
                
                progress.advance(main_task)
    
    # Get user profiles if requested (sequential for now)
    if include_users and all_posts:
        console.print("[yellow]Collecting user profiles...[/yellow]")
        
        # Start performance monitoring if enabled
        users_op_id = None
        if perf_monitor:
            users_op_id = perf_monitor.start_operation("collect_user_profiles")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Get unique authors
            unique_authors = list(set(post.get('author', '') for post in all_posts 
                                    if post.get('author') and post.get('author') != '[deleted]'))
            
            user_task = progress.add_task("Getting user profiles...", total=len(unique_authors))
            
            for author in unique_authors:
                user_data = rate_limiter.retry_with_backoff(
                    client.get_user_profile, author
                )
                if user_data:
                    all_users.append(user_data)
                
                progress.advance(user_task)
        
        # End performance monitoring
        if perf_monitor and users_op_id:
            perf_monitor.end_operation(users_op_id, success=True, users_count=len(all_users))
        
        console.print(f"[green]✓[/green] Retrieved {len(all_users)} user profiles")
    
    if not all_posts:
        console.print("[red]No posts retrieved. Exiting.[/red]")
        return
    
    # Process posts
    console.print("[yellow]Processing posts...[/yellow]")
    
    # Start performance monitoring if enabled
    process_op_id = None
    if perf_monitor:
        process_op_id = perf_monitor.start_operation("process_posts", posts_count=len(all_posts))
    
    all_posts = processor.filter_posts(all_posts)
    all_posts = processor.deduplicate_posts(all_posts)
    all_posts = processor.add_derived_fields(all_posts)
    
    # End performance monitoring
    if perf_monitor and process_op_id:
        perf_monitor.end_operation(process_op_id, success=True, final_posts_count=len(all_posts))
    
    # Extract content from external links if requested
    if extract_content and content_extractor and all_posts:
        console.print("[yellow]Extracting content from external links...[/yellow]")
        
        # Start performance monitoring if enabled
        extract_op_id = None
        if perf_monitor:
            extract_op_id = perf_monitor.start_operation("extract_content", posts_count=len(all_posts))
        
        all_posts = content_extractor.extract_content_from_posts(all_posts)
        
        # End performance monitoring
        if perf_monitor and extract_op_id:
            perf_monitor.end_operation(extract_op_id, success=True)
        
        # Count posts with extracted content
        extracted_count = sum(1 for post in all_posts if post.get('extracted_content'))
        console.print(f"[green]✓[/green] Extracted content from {extracted_count} posts")
    
    # Remove duplicate users
    if all_users:
        seen_users = set()
        unique_users = []
        for user in all_users:
            username = user.get('username')
            if username and username not in seen_users:
                seen_users.add(username)
                unique_users.append(user)
        all_users = unique_users
    
    # Export data
    console.print("[yellow]Exporting data...[/yellow]")
    exported_files = []
    
    # Start performance monitoring if enabled
    export_op_id = None
    if perf_monitor:
        export_op_id = perf_monitor.start_operation("export_data", formats=len(output_formats))
    
    if json_exporter:
        if include_users and all_users:
            json_file = json_exporter.export_combined(all_posts, all_users)
        else:
            json_file = json_exporter.export_posts(all_posts)
        exported_files.append(json_file)
    
    if csv_exporter:
        csv_file = csv_exporter.export_posts(all_posts)
        exported_files.append(csv_file)
        
        if include_users and all_users:
            users_csv = csv_exporter.export_users(all_users)
            exported_files.append(users_csv)
        
        # Export summary statistics
        summary_file = csv_exporter.export_summary_stats(all_posts)
        exported_files.append(summary_file)
        
        # Export subreddit breakdown
        breakdown_file = csv_exporter.export_subreddit_breakdown(all_posts)
        exported_files.append(breakdown_file)
    
    if html_exporter:
        html_file = html_exporter.export_posts_report(all_posts, all_users)
        exported_files.append(html_file)
        console.print(f"[green]✓[/green] Generated interactive HTML report")
    
    # End performance monitoring
    if perf_monitor and export_op_id:
        perf_monitor.end_operation(export_op_id, success=True, files_exported=len(exported_files))
    
    # Display results
    _display_results(all_posts, all_users, exported_files)
    
    # Display performance summary if monitoring was enabled
    if perf_monitor:
        console.print("\n[bold]Performance Summary:[/bold]")
        summary = perf_monitor.get_summary_statistics()
        
        if 'overall' in summary:
            overall = summary['overall']
            console.print(f"Total operations: {overall.get('total_operations', 0)}")
            console.print(f"Success rate: {overall.get('success_rate', 0):.1f}%")
            console.print(f"Total time: {overall.get('total_time', 0):.2f}s")
            console.print(f"Operations per second: {overall.get('operations_per_second', 0):.2f}")
        
        # Export performance metrics
        perf_file = perf_monitor.export_metrics()
        console.print(f"Performance metrics exported to: {perf_file}")


@cli.command()
@click.pass_context
def create_config(ctx):
    """Create default configuration file."""
    config_file = ctx.obj['config_file']
    create_default_config_file(config_file)


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test Reddit API connection."""
    config = ctx.obj['config']
    
    if not config.validate_reddit_config():
        console.print("[red]Reddit API not configured. Run 'setup' command first.[/red]")
        return
    
    console.print("[yellow]Testing Reddit API connection...[/yellow]")
    
    try:
        reddit_config = config.get_reddit_config()
        client = RedditClient(**reddit_config)
        
        if client.test_connection():
            console.print("[green]✓ Reddit API connection successful![/green]")
        else:
            console.print("[red]✗ Reddit API connection failed![/red]")
            
    except Exception as e:
        console.print(f"[red]Error testing connection: {e}[/red]")


def _display_results(posts: List, users: List, exported_files: List[str]):
    """Display scraping results.
    
    Args:
        posts: List of scraped posts
        users: List of scraped users
        exported_files: List of exported file paths
    """
    # Summary table
    table = Table(title="Scraping Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Posts", str(len(posts)))
    table.add_row("Total Users", str(len(users)))
    table.add_row("Exported Files", str(len(exported_files)))
    
    if posts:
        avg_score = sum(p.get('score', 0) for p in posts) / len(posts)
        total_comments = sum(p.get('num_comments', 0) for p in posts)
        table.add_row("Average Score", f"{avg_score:.1f}")
        table.add_row("Total Comments", str(total_comments))
        
        # Subreddit breakdown
        subreddits = {}
        for post in posts:
            sub = post.get('subreddit', '')
            subreddits[sub] = subreddits.get(sub, 0) + 1
        
        top_subreddits = sorted(subreddits.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (sub, count) in enumerate(top_subreddits):
            table.add_row(f"Top Subreddit #{i+1}", f"r/{sub} ({count} posts)")
    
    console.print(table)
    
    # Exported files
    if exported_files:
        console.print("\n[bold]Exported Files:[/bold]")
        for file_path in exported_files:
            if file_path:
                console.print(f"  • {file_path}")


if __name__ == '__main__':
    cli()