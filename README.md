# Reddit Scraper

A comprehensive command-line tool for scraping Reddit posts and user profiles. Built with Python, this tool allows you to collect large amounts of Reddit data for analysis, research, and trend monitoring.

## Features

- **Multi-subreddit scraping** - Scrape from multiple subreddits simultaneously
- **Flexible sorting options** - Hot, new, top, rising posts
- **User profile collection** - Optional user profile data extraction
- **Multiple export formats** - JSON, CSV, and HTML reports
- **Advanced filtering** - Score, age, NSFW, and content-based filters
- **Rate limiting** - Respects Reddit's API limits with intelligent backoff
- **Progress monitoring** - Real-time progress bars and status updates
- **Comprehensive logging** - Detailed logs for debugging and monitoring

## Installation

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Reddit API credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Create a new app (script type)
   - Note down your client_id and client_secret

4. **Configure the scraper:**
   ```bash
   python run.py setup
   ```

## Quick Start

### Basic Usage

```bash
# Scrape 100 posts from r/python
python run.py scrape --subreddit python --posts 100

# Scrape from multiple subreddits
python run.py scrape --subreddit "python,datascience,MachineLearning" --posts 500

# Include user profiles
python run.py scrape --subreddit "AskReddit" --posts 1000 --include-users
```

### Advanced Usage

```bash
# Filter by score and time
python run.py scrape --subreddit "technology" --posts 2000 --min-score 50 --sort top --time-filter week

# Custom output formats
python run.py scrape --subreddit "funny" --posts 1000 --output json,csv

# Exclude NSFW content
python run.py scrape --subreddit "all" --posts 5000 --exclude-nsfw
```

## Command Reference

### Setup Commands

```bash
# Initial setup with Reddit API credentials
python run.py setup

# Test API connection
python run.py test-connection

# Create default configuration file
python run.py create-config
```

### Scraping Commands

```bash
python run.py scrape [OPTIONS]

Options:
  -s, --subreddit TEXT     Subreddit name(s), comma-separated
  -p, --posts INTEGER      Number of posts to scrape (default: 100)
  --sort [hot|new|top|rising]  Sort type for posts (default: hot)
  --time-filter [hour|day|week|month|year|all]  Time filter for top posts
  -o, --output TEXT        Output formats: json,csv (default: json,csv)
  --include-users          Include user profile data
  --min-score INTEGER      Minimum post score filter
  --exclude-nsfw           Exclude NSFW posts (default: True)
```

## Configuration

The scraper uses a YAML configuration file at `config/settings.yaml`:

```yaml
reddit_api:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  user_agent: "RedditScraper/1.0"

scraping:
  rate_limit: 1.0  # requests per second
  max_retries: 3
  timeout: 30

filtering:
  min_score: 1
  max_age_days: 365
  exclude_nsfw: true
  exclude_deleted: true

output:
  formats: ["json", "csv"]
  include_metadata: true
```

## Output Formats

### JSON Output
- Complete post data with metadata
- User profiles (if requested)
- Summary statistics
- Structured for easy parsing

### CSV Output
- `reddit_posts_YYYYMMDD_HHMMSS.csv` - Main posts data
- `reddit_users_YYYYMMDD_HHMMSS.csv` - User profiles
- `reddit_summary_YYYYMMDD_HHMMSS.csv` - Summary statistics
- `reddit_subreddits_YYYYMMDD_HHMMSS.csv` - Subreddit breakdown

## Data Structure

### Post Data
```json
{
  "id": "post_id",
  "title": "Post title",
  "author": "username",
  "subreddit": "subreddit_name",
  "score": 1234,
  "upvote_ratio": 0.85,
  "num_comments": 56,
  "created_utc": 1640995200,
  "url": "https://reddit.com/...",
  "selftext": "Post content",
  "flair": "Discussion",
  "is_nsfw": false,
  "category": "discussion",
  "engagement_ratio": 0.045
}
```

### User Profile Data
```json
{
  "username": "reddit_user",
  "comment_karma": 5678,
  "link_karma": 1234,
  "created_utc": 1234567890,
  "is_verified": false,
  "has_premium": false
}
```

## Rate Limiting & Best Practices

- **Default rate limit**: 1 request per second
- **Automatic retries**: Exponential backoff for failed requests
- **Respects Reddit's limits**: 60 requests per minute maximum
- **Connection pooling**: Efficient HTTP request handling
- **Graceful error handling**: Continues scraping despite individual failures

## Troubleshooting

### Common Issues

1. **"Reddit API not configured"**
   - Run `python run.py setup` to configure API credentials

2. **"Connection failed"**
   - Check your internet connection
   - Verify Reddit API credentials
   - Ensure Reddit is accessible

3. **"Rate limit exceeded"**
   - Reduce the rate_limit in configuration
   - The scraper will automatically retry with backoff

4. **"No posts retrieved"**
   - Check if subreddit exists and is accessible
   - Verify filtering criteria aren't too restrictive
   - Some subreddits may be private or banned

### Logging

Logs are saved to `logs/scraper.log` and include:
- Scraping progress and statistics
- API errors and retry attempts
- Configuration and setup issues
- Performance metrics

## Legal and Ethical Considerations

- **Respect Reddit's Terms of Service**
- **Don't overload Reddit's servers** - Use appropriate rate limiting
- **Respect user privacy** - Handle personal data responsibly
- **Follow subreddit rules** - Some communities may prohibit scraping
- **Use data responsibly** - Don't use for spam or harassment

## Examples

### Research Use Case
```bash
# Collect data for sentiment analysis
python run.py scrape --subreddit "politics,worldnews" --posts 5000 --min-score 10 --output json
```

### Content Analysis
```bash
# Analyze popular content patterns
python run.py scrape --subreddit "datascience" --posts 2000 --sort top --time-filter month --include-users
```

### Trend Monitoring
```bash
# Monitor trending topics
python run.py scrape --subreddit "technology,programming" --posts 1000 --sort hot --output csv
```

## Project Structure

```
reddit-scraper/
├── src/
│   ├── core/           # Core scraping functionality
│   ├── processors/     # Data processing and filtering
│   ├── exporters/      # Export functionality
│   └── cli/           # Command line interface
├── config/            # Configuration files
├── output/            # Generated output files
├── logs/              # Log files
├── requirements.txt   # Python dependencies
├── run.py            # Main entry point
└── README.md         # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with Reddit's Terms of Service and applicable laws in your jurisdiction.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/scraper.log`
3. Ensure your configuration is correct
4. Verify Reddit API credentials are valid

---

**Note**: This tool is for educational and research purposes. Always respect Reddit's Terms of Service and rate limits.