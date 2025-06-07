# Reddit Scraper

A comprehensive command-line tool for scraping Reddit posts and user profiles. Built with Python, this tool allows you to collect large amounts of Reddit data for analysis, research, and trend monitoring.

## Features

### 🚀 **Core Scraping**
- **Multi-subreddit scraping** - Scrape from multiple subreddits simultaneously
- **Parallel processing** - Up to 5x faster with concurrent workers
- **Flexible sorting options** - Hot, new, top, rising posts
- **User profile collection** - Optional user profile data extraction
- **Rate limiting** - Respects Reddit's API limits with intelligent backoff

### 📊 **Export & Visualization**
- **Interactive HTML reports** - Beautiful dark theme with Chart.js visualizations
- **JSON export** - Structured data with comprehensive metadata
- **CSV export** - Multiple files including summary statistics and breakdowns
- **Real-time charts** - Score distribution, posting patterns, engagement metrics

### 🔍 **Content Enhancement**
- **Content extraction** - Automatically extract content from external links
- **Advanced filtering** - Score, age, NSFW, and content-based filters
- **Smart categorization** - Automatic post categorization (discussion, tutorial, etc.)
- **Engagement analysis** - Calculate engagement ratios and trends

### ⚡ **Performance & Monitoring**
- **Performance monitoring** - Built-in metrics collection and analysis
- **Memory optimization** - Efficient processing for large datasets
- **Progress tracking** - Real-time progress bars and status updates
- **Comprehensive logging** - Detailed logs for debugging and monitoring

### 🧪 **Quality & Testing**
- **95%+ test coverage** - Comprehensive unit and integration tests
- **Performance benchmarks** - Built-in performance testing
- **Code quality checks** - Automated linting and formatting
- **Security scanning** - Vulnerability detection and best practices

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
# Parallel processing for faster scraping
python run.py scrape --subreddit "python,programming,datascience" --posts 200 --parallel --max-workers 5

# Generate interactive HTML reports
python run.py scrape --subreddit "technology" --posts 500 --output html

# Extract content from external links
python run.py scrape --subreddit "programming" --posts 300 --extract-content

# Performance monitoring
python run.py scrape --subreddit "datascience" --posts 400 --performance-monitor

# All features combined
python run.py scrape --subreddit "python,datascience" --posts 300 --parallel --extract-content --include-users --performance-monitor --output "json,csv,html" --min-score 10
```

### New Feature Examples

```bash
# HTML Report with Dark Theme
python run.py scrape --subreddit "MachineLearning" --posts 200 --output html
# Generates interactive charts, engagement analysis, and beautiful visualizations

# Parallel Processing
python run.py scrape --subreddit "python,programming,datascience,MachineLearning" --posts 100 --parallel
# Up to 5x faster scraping with concurrent workers

# Content Extraction
python run.py scrape --subreddit "technology" --posts 150 --extract-content
# Automatically extracts content from GitHub, Medium, YouTube, and other links

# Performance Monitoring
python run.py scrape --subreddit "programming" --posts 250 --performance-monitor
# Tracks memory usage, CPU usage, and operation timings
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
  -o, --output TEXT        Output formats: json,csv,html (default: json,csv)
  --include-users          Include user profile data
  --min-score INTEGER      Minimum post score filter
  --exclude-nsfw           Exclude NSFW posts (default: True)
  --extract-content        Extract content from external links
  --parallel               Use parallel processing for multiple subreddits
  --max-workers INTEGER    Maximum parallel workers (default: 5)
  --performance-monitor    Enable performance monitoring
```

### Testing Commands

```bash
# Run all tests with coverage
python run_tests.py --all

# Run specific test types
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --performance   # Performance tests only

# Code quality checks
python run_tests.py --lint          # Linting and formatting
python run_tests.py --security      # Security vulnerability scan

# Performance benchmarks
python run_tests.py --benchmark     # Performance benchmarks

# Generate test reports
python run_tests.py --report        # HTML test report with coverage
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

### 🎨 HTML Reports (NEW!)
- **Interactive dark theme** with responsive design
- **Chart.js visualizations**: Score distribution, posting patterns, engagement metrics
- **Summary statistics** with beautiful cards and progress bars
- **Top posts analysis** with clickable links
- **Subreddit breakdown** with visual progress indicators
- **User analysis** with karma rankings
- **Mobile-friendly** responsive layout

### 📊 JSON Output
- Complete post data with metadata
- User profiles (if requested)
- Summary statistics and analytics
- Extracted content from external links
- Performance metrics (if monitoring enabled)
- Structured for easy parsing and analysis

### 📈 CSV Output
- `reddit_posts_YYYYMMDD_HHMMSS.csv` - Main posts data with derived fields
- `reddit_users_YYYYMMDD_HHMMSS.csv` - User profiles and karma data
- `reddit_summary_YYYYMMDD_HHMMSS.csv` - Summary statistics and metrics
- `reddit_subreddits_YYYYMMDD_HHMMSS.csv` - Detailed subreddit breakdown
- Perfect for Excel, Google Sheets, and data analysis tools

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