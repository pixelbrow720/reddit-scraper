# Blueprint Proyek Reddit Scraper

## 1. Overview Proyek

### Tujuan
Membuat tool scraping Reddit berbasis terminal untuk mengumpulkan posts, konten, dan user profiles dari subreddit tertentu atau secara general untuk keperluan analisis sentimen, penelitian, dan analisa tren.

### Target Output
- **Volume**: Ratusan ribu hingga jutaan posts
- **Format**: JSON, CSV, HTML
- **Sifat**: One-time scraping
- **Interface**: Terminal/Command Line

## 2. Arsitektur Sistem

### Komponen Utama
```
Reddit Scraper
├── Core Engine
│   ├── Reddit API Client
│   ├── Web Scraper (Fallback)
│   └── Rate Limiter
├── Data Processing
│   ├── Post Processor
│   ├── User Profile Processor
│   └── Content Extractor
├── Storage Manager
│   ├── JSON Exporter
│   ├── CSV Exporter
│   └── HTML Generator
└── CLI Interface
    ├── Configuration Manager
    ├── Progress Monitor
    └── Error Handler
```

## 3. Teknologi Stack

### Bahasa Pemrograman
- **Python 3.8+** (Recommended)
  - Rich ecosystem untuk scraping
  - Excellent data processing libraries
  - Strong CLI framework support

### Libraries Utama
```python
# Core Scraping
- praw (Python Reddit API Wrapper)
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)

# Data Processing
- pandas (Data manipulation)
- json (JSON handling)
- csv (CSV handling)

# CLI Interface
- click atau argparse (Command line interface)
- rich (Beautiful terminal output)
- tqdm (Progress bars)

# Utility
- time (Rate limiting)
- concurrent.futures (Parallel processing)
- logging (Error tracking)
```

## 4. Struktur Proyek

```
reddit-scraper/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── reddit_client.py
│   │   ├── scraper.py
│   │   └── rate_limiter.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── post_processor.py
│   │   ├── user_processor.py
│   │   └── content_extractor.py
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── json_exporter.py
│   │   ├── csv_exporter.py
│   │   └── html_generator.py
│   └── cli/
│       ├── __init__.py
│       ├── main.py
│       └── config.py
├── config/
│   ├── settings.yaml
│   └── subreddits.txt
├── output/
│   ├── json/
│   ├── csv/
│   └── html/
├── logs/
├── requirements.txt
├── setup.py
├── README.md
└── run.py
```

## 5. Fitur Utama

### CLI Commands
```bash
# Scraping subreddit spesifik
python run.py scrape --subreddit "technology,programming" --posts 1000

# Scraping general (popular/all)
python run.py scrape --mode general --posts 5000

# Scraping dengan filter
python run.py scrape --subreddit "python" --posts 1000 --min-score 10 --time-range "week"

# Export ke format tertentu
python run.py scrape --subreddit "datascience" --posts 500 --output json,csv

# Scraping dengan user profiles
python run.py scrape --subreddit "AskReddit" --posts 1000 --include-users
```

### Configuration Options
```yaml
reddit_api:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  user_agent: "RedditScraper/1.0"

scraping:
  rate_limit: 1  # requests per second
  max_retries: 3
  timeout: 30
  concurrent_workers: 5

output:
  formats: ["json", "csv", "html"]
  include_metadata: true
  compress_output: false

filtering:
  min_score: 1
  max_age_days: 365
  exclude_nsfw: true
  exclude_deleted: true
```

## 6. Data Structure

### Post Data Structure
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
  "url": "https://reddit.com/r/subreddit/comments/...",
  "selftext": "Post content",
  "link_url": "https://external-link.com",
  "link_title": "External content title",
  "link_content": "Extracted content (if possible)",
  "flair": "Discussion",
  "is_nsfw": false,
  "is_spoiler": false,
  "metadata": {
    "scraped_at": "2024-01-01T00:00:00Z",
    "content_type": "text/link/image"
  }
}
```

### User Profile Structure
```json
{
  "username": "reddit_user",
  "id": "user_id",
  "created_utc": 1234567890,
  "comment_karma": 5678,
  "link_karma": 1234,
  "is_verified": false,
  "has_premium": false,
  "profile_description": "User bio",
  "total_posts": 100,
  "total_comments": 500,
  "active_subreddits": ["sub1", "sub2"],
  "metadata": {
    "scraped_at": "2024-01-01T00:00:00Z",
    "last_activity": "2024-01-01T00:00:00Z"
  }
}
```

## 7. Implementation Plan

### Phase 1: Core Setup (Week 1)
- [ ] Setup project structure
- [ ] Implement Reddit API client
- [ ] Basic CLI interface
- [ ] Configuration management
- [ ] Rate limiting mechanism

### Phase 2: Data Collection (Week 2)
- [ ] Post scraping functionality
- [ ] User profile collection
- [ ] Content extraction (links)
- [ ] Error handling & logging
- [ ] Basic filtering options

### Phase 3: Data Processing (Week 3)
- [ ] JSON export functionality
- [ ] CSV export functionality
- [ ] HTML report generation
- [ ] Data validation
- [ ] Duplicate detection

### Phase 4: Enhancement (Week 4)
- [ ] Advanced filtering options
- [ ] Parallel processing
- [ ] Progress monitoring
- [ ] Performance optimization
- [ ] Testing & documentation

## 8. Technical Specifications

### Reddit API Setup
```python
# Reddit API Requirements
1. Reddit account
2. Create app at https://www.reddit.com/prefs/apps
3. Get client_id and client_secret
4. Set appropriate user_agent
```

### Rate Limiting Strategy
```python
# Conservative approach
- 1 request per second for API calls
- 2-3 seconds delay for web scraping
- Exponential backoff for failed requests
- Respect Reddit's rate limits (60 requests/minute)
```

### Content Extraction
```python
# Link content extraction
- Detect content type (article, video, image)
- Extract readable text from articles
- Get metadata (title, description, author)
- Handle common domains (YouTube, Medium, etc.)
- Fallback to basic URL info if extraction fails
```

## 9. Usage Examples

### Basic Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Reddit API
python run.py config --setup

# Scrape specific subreddit
python run.py scrape --subreddit "python" --posts 1000

# Scrape multiple subreddits
python run.py scrape --subreddit "python,datascience,MachineLearning" --posts 500

# Scrape with user profiles
python run.py scrape --subreddit "AskReddit" --posts 1000 --include-users

# Export to specific formats
python run.py scrape --subreddit "technology" --posts 2000 --output json,html
```

### Advanced Usage
```bash
# Time-based filtering
python run.py scrape --subreddit "news" --posts 5000 --time-range "month"

# Score-based filtering
python run.py scrape --subreddit "funny" --posts 1000 --min-score 100

# Comprehensive scraping
python run.py scrape --mode general --posts 10000 --include-users --extract-links
```

## 10. Output Examples

### JSON Output
```json
{
  "metadata": {
    "scraped_at": "2024-01-01T00:00:00Z",
    "total_posts": 1000,
    "subreddits": ["python", "datascience"],
    "scraping_duration": "00:15:30"
  },
  "posts": [...],
  "users": [...],
  "statistics": {
    "avg_score": 25.5,
    "total_comments": 12345,
    "top_authors": ["user1", "user2"]
  }
}
```

### CSV Columns
```
id,title,author,subreddit,score,num_comments,created_utc,url,selftext,link_url,flair
```

### HTML Report
- Summary statistics
- Top posts by score
- Author activity analysis
- Subreddit distribution
- Time-based trends
- Interactive charts (optional)

## 11. Monitoring & Logging

### Log Levels
```python
INFO: Scraping progress, successful operations
WARNING: Rate limit warnings, minor errors
ERROR: Failed requests, data processing errors
DEBUG: Detailed operation logs (development)
```

### Progress Monitoring
```python
# Real-time progress display
[██████████████████████████████] 1000/1000 posts (100%)
Rate: 15 posts/min | ETA: 00:00:00 | Errors: 2
```

## 12. Error Handling

### Common Scenarios
- Reddit API rate limits
- Network connection issues
- Deleted/removed posts
- Private subreddits
- Banned users
- Invalid URLs

### Recovery Strategies
- Automatic retry with exponential backoff
- Checkpoint system for large scraping jobs
- Resume functionality for interrupted operations
- Graceful degradation for partial failures

## 13. Performance Considerations

### Optimization Techniques
- Concurrent request processing
- Efficient data structures
- Memory-conscious processing for large datasets
- Chunked file writing for large outputs
- Connection pooling for HTTP requests

### Scalability
- Modular design for easy extension
- Configuration-driven behavior
- Plugin architecture for new exporters
- Support for distributed scraping (future)

## 14. Security & Compliance

### Best Practices
- Respect robots.txt
- Implement proper rate limiting
- Use appropriate user agents
- Handle personal data responsibly
- Provide data deletion capabilities
- Document data usage policies

### Reddit Terms of Service
- Follow Reddit's API terms
- Don't overload Reddit's servers
- Respect user privacy
- Don't use data for spam/harassment
- Comply with content policies

## 15. Deliverables

### Final Package
1. **Source Code**: Complete Python package
2. **Documentation**: Setup guide, usage examples
3. **Configuration**: Templates and examples
4. **Sample Outputs**: Example JSON, CSV, HTML files
5. **Requirements**: Dependencies and system requirements
6. **Tests**: Unit tests for core functionality

### Support Materials
- Installation guide
- Configuration tutorial
- Troubleshooting guide
- API setup instructions
- Usage examples and recipes