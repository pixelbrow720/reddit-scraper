# API Documentation

This document provides detailed information about Reddit Scraper's internal API and components.

## Table of Contents

- [Core Components](#core-components)
- [Data Structures](#data-structures)
- [Configuration API](#configuration-api)
- [Export API](#export-api)
- [Error Handling](#error-handling)
- [Extension Points](#extension-points)

## Core Components

### RedditClient

The main interface for Reddit API interactions.

```python
from src.core.reddit_client import RedditClient

client = RedditClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="YourApp/1.0"
)
```

#### Methods

##### `test_connection() -> bool`
Tests the Reddit API connection.

**Returns:**
- `bool`: True if connection successful, False otherwise

**Example:**
```python
if client.test_connection():
    print("Connected to Reddit API")
```

##### `get_subreddit_posts(subreddit_name, sort_type, limit, time_filter) -> List[Dict]`
Retrieves posts from a subreddit.

**Parameters:**
- `subreddit_name` (str): Name of the subreddit
- `sort_type` (str): Sort type ('hot', 'new', 'top', 'rising')
- `limit` (int): Number of posts to retrieve
- `time_filter` (str): Time filter for top posts

**Returns:**
- `List[Dict[str, Any]]`: List of post dictionaries

**Example:**
```python
posts = client.get_subreddit_posts(
    subreddit_name="python",
    sort_type="hot",
    limit=100,
    time_filter="all"
)
```

##### `get_user_profile(username) -> Optional[Dict]`
Retrieves user profile information.

**Parameters:**
- `username` (str): Reddit username

**Returns:**
- `Optional[Dict[str, Any]]`: User profile dictionary or None

**Example:**
```python
user = client.get_user_profile("spez")
if user:
    print(f"User karma: {user['comment_karma']}")
```

### RateLimiter

Manages API request rate limiting.

```python
from src.core.rate_limiter import RateLimiter

limiter = RateLimiter(
    requests_per_second=1.0,
    max_retries=3
)
```

#### Methods

##### `wait_if_needed() -> None`
Waits if necessary to respect rate limits.

##### `retry_with_backoff(func, *args, **kwargs)`
Executes function with retry and exponential backoff.

**Parameters:**
- `func`: Function to execute
- `*args`: Function arguments
- `**kwargs`: Function keyword arguments

**Returns:**
- Function result or None if all retries failed

**Example:**
```python
result = limiter.retry_with_backoff(
    client.get_subreddit_posts,
    "python", "hot", 100, "all"
)
```

### PostProcessor

Processes and filters Reddit posts.

```python
from src.processors.post_processor import PostProcessor

processor = PostProcessor(
    min_score=10,
    max_age_days=30,
    exclude_nsfw=True,
    exclude_deleted=True
)
```

#### Methods

##### `filter_posts(posts) -> List[Dict]`
Filters posts based on configured criteria.

##### `deduplicate_posts(posts) -> List[Dict]`
Removes duplicate posts based on ID.

##### `add_derived_fields(posts) -> List[Dict]`
Adds derived fields to posts.

**Example:**
```python
filtered_posts = processor.filter_posts(raw_posts)
unique_posts = processor.deduplicate_posts(filtered_posts)
enhanced_posts = processor.add_derived_fields(unique_posts)
```

## Data Structures

### Post Data Structure

```python
{
    "id": str,                    # Reddit post ID
    "title": str,                 # Post title
    "author": str,                # Author username
    "subreddit": str,             # Subreddit name
    "score": int,                 # Post score (upvotes - downvotes)
    "upvote_ratio": float,        # Ratio of upvotes (0.0-1.0)
    "num_comments": int,          # Number of comments
    "created_utc": int,           # Creation timestamp (UTC)
    "url": str,                   # Post URL
    "permalink": str,             # Reddit permalink
    "selftext": str,              # Post text content
    "link_url": Optional[str],    # External link URL
    "flair": Optional[str],       # Post flair
    "is_nsfw": bool,              # NSFW flag
    "is_spoiler": bool,           # Spoiler flag
    "is_self": bool,              # Self post flag
    "domain": str,                # Link domain
    "metadata": {
        "scraped_at": str,        # ISO timestamp
        "content_type": str       # "text", "link", "image", "video"
    },
    # Derived fields (added by PostProcessor)
    "title_clean": str,           # Cleaned title
    "selftext_clean": str,        # Cleaned text
    "extracted_urls": List[str],  # URLs found in text
    "category": str,              # Post category
    "engagement_ratio": float,    # Comments/score ratio
    "created_date": str,          # Date string (YYYY-MM-DD)
    "created_hour": int,          # Hour of day (0-23)
    "created_weekday": int        # Day of week (0-6)
}
```

### User Profile Structure

```python
{
    "username": str,              # Reddit username
    "id": str,                    # Reddit user ID
    "created_utc": int,           # Account creation timestamp
    "comment_karma": int,         # Comment karma
    "link_karma": int,            # Link karma
    "is_verified": bool,          # Verified account flag
    "has_premium": bool,          # Reddit Premium flag
    "profile_description": str,   # Profile description
    "metadata": {
        "scraped_at": str         # ISO timestamp
    }
}
```

## Configuration API

### Config Class

```python
from src.cli.config import Config

config = Config("config/settings.yaml")
```

#### Methods

##### `get(key, default=None) -> Any`
Gets configuration value by key (supports dot notation).

**Example:**
```python
rate_limit = config.get('scraping.rate_limit', 1.0)
client_id = config.get('reddit_api.client_id')
```

##### `set(key, value) -> None`
Sets configuration value by key.

**Example:**
```python
config.set('scraping.rate_limit', 0.5)
config.set('filtering.min_score', 20)
```

##### `validate_reddit_config() -> bool`
Validates Reddit API configuration.

##### `get_reddit_config() -> Dict[str, str]`
Gets Reddit API configuration dictionary.

##### `get_scraping_config() -> Dict[str, Any]`
Gets scraping configuration dictionary.

##### `get_filtering_config() -> Dict[str, Any]`
Gets filtering configuration dictionary.

## Export API

### JSONExporter

```python
from src.exporters.json_exporter import JSONExporter

exporter = JSONExporter(
    output_dir="output/json",
    indent=2,
    ensure_ascii=False
)
```

#### Methods

##### `export_posts(posts, filename=None, include_metadata=True) -> str`
Exports posts to JSON file.

##### `export_users(users, filename=None) -> str`
Exports user profiles to JSON file.

##### `export_combined(posts, users=None, filename=None) -> str`
Exports combined posts and users data.

### CSVExporter

```python
from src.exporters.csv_exporter import CSVExporter

exporter = CSVExporter(output_dir="output/csv")
```

#### Methods

##### `export_posts(posts, filename=None) -> str`
Exports posts to CSV file.

##### `export_users(users, filename=None) -> str`
Exports user profiles to CSV file.

##### `export_summary_stats(posts, filename=None) -> str`
Exports summary statistics to CSV.

##### `export_subreddit_breakdown(posts, filename=None) -> str`
Exports subreddit breakdown to CSV.

## Error Handling

### Exception Types

The scraper uses standard Python exceptions with descriptive messages:

- `ValueError`: Invalid configuration or parameters
- `ConnectionError`: Network or API connection issues
- `FileNotFoundError`: Missing configuration or output files
- `PermissionError`: File system permission issues

### Error Handling Patterns

```python
try:
    posts = client.get_subreddit_posts("python", "hot", 100)
except Exception as e:
    logger.error(f"Failed to get posts: {e}")
    # Handle error appropriately
```

### Logging

The scraper uses Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

# Log levels used:
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

## Extension Points

### Custom Processors

Create custom post processors by extending the base functionality:

```python
from src.processors.post_processor import PostProcessor

class CustomProcessor(PostProcessor):
    def custom_filter(self, posts):
        # Your custom filtering logic
        return filtered_posts
    
    def add_custom_fields(self, posts):
        # Add your custom derived fields
        for post in posts:
            post['custom_field'] = self.calculate_custom_metric(post)
        return posts
```

### Custom Exporters

Create custom exporters for different output formats:

```python
import os
from typing import List, Dict, Any

class CustomExporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_posts(self, posts: List[Dict[str, Any]], filename: str = None) -> str:
        # Your custom export logic
        filepath = os.path.join(self.output_dir, filename)
        # Write data in your custom format
        return filepath
```

### Custom CLI Commands

Extend the CLI with custom commands:

```python
import click
from src.cli.main import cli

@cli.command()
@click.option('--custom-option', help='Custom option')
def custom_command(custom_option):
    """Custom command description."""
    # Your custom command logic
    pass
```

## Performance Considerations

### Memory Usage

For large datasets:

```python
# Process data in chunks
def process_large_dataset(posts, chunk_size=1000):
    for i in range(0, len(posts), chunk_size):
        chunk = posts[i:i + chunk_size]
        # Process chunk
        yield process_chunk(chunk)
```

### Async Operations (Future)

The architecture supports future async implementations:

```python
import asyncio

async def async_scrape_subreddit(client, subreddit):
    # Async scraping implementation
    pass
```

## Testing

### Unit Tests

```python
import unittest
from src.core.reddit_client import RedditClient

class TestRedditClient(unittest.TestCase):
    def setUp(self):
        self.client = RedditClient("test_id", "test_secret", "test_agent")
    
    def test_connection(self):
        # Test connection functionality
        pass
```

### Integration Tests

```python
def test_full_scraping_workflow():
    # Test complete scraping workflow
    config = Config("test_config.yaml")
    client = RedditClient(**config.get_reddit_config())
    posts = client.get_subreddit_posts("test", "hot", 10)
    assert len(posts) <= 10
```

## API Versioning

The internal API follows semantic versioning:

- **Major version**: Breaking changes to public API
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

Current API version: `1.0.0`

---

**Maintainer:** [@pixelbrow720](https://github.com/pixelbrow720)  
**Twitter:** [@BrowPixel](https://twitter.com/BrowPixel)