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
@click.option('--output', '-o', default='json,csv', help='Output formats (comma-separated)')
@click.option('--include-users', is_flag=True, help='Include user profile data')
@click.option('--min-score', default=None, type=int, help='Minimum post score')
@click.option('--exclude-nsfw', is_flag=True, default=True, help='Exclude NSFW posts')
@click.pass_context
def scrape(ctx, subreddit, posts, sort, time_filter, output, include_users, min_score, exclude_nsfw):
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
    
    # Initialize exporters
    json_exporter = JSONExporter() if 'json' in output_formats else None
    csv_exporter = CSVExporter() if 'csv' in output_formats else None
    
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
    
    # Scrape each subreddit
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
            
            # Get posts with rate limiting
            posts_data = rate_limiter.retry_with_backoff(
                client.get_subreddit_posts,
                sub, sort, posts, time_filter
            )
            
            if posts_data:
                console.print(f"[green]✓[/green] Retrieved {len(posts_data)} posts from r/{sub}")
                all_posts.extend(posts_data)
                
                # Get user profiles if requested
                if include_users:
                    user_task = progress.add_task(f"Getting user profiles from r/{sub}...", 
                                                total=len(posts_data))
                    
                    for post in posts_data:
                        author = post.get('author')
                        if author and author != '[deleted]':
                            user_data = rate_limiter.retry_with_backoff(
                                client.get_user_profile, author
                            )
                            if user_data:
                                all_users.append(user_data)
                        
                        progress.advance(user_task)
                    
                    progress.remove_task(user_task)
                    console.print(f"[green]✓[/green] Retrieved {len(all_users)} user profiles")
            else:
                console.print(f"[red]✗[/red] Failed to retrieve posts from r/{sub}")
            
            progress.advance(main_task)
    
    if not all_posts:
        console.print("[red]No posts retrieved. Exiting.[/red]")
        return
    
    # Process posts
    console.print("[yellow]Processing posts...[/yellow]")
    all_posts = processor.filter_posts(all_posts)
    all_posts = processor.deduplicate_posts(all_posts)
    all_posts = processor.add_derived_fields(all_posts)
    
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
    
    # Display results
    _display_results(all_posts, all_users, exported_files)


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