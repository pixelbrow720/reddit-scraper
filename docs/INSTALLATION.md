# Installation Guide

This guide will walk you through installing and setting up Reddit Scraper on your system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Reddit API Setup](#reddit-api-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 500MB for installation, additional space for data output
- **Internet:** Stable internet connection for Reddit API access

### Recommended Requirements

- **Python:** 3.9 or higher
- **RAM:** 8GB or more for large-scale scraping
- **Storage:** 10GB+ for extensive data collection
- **CPU:** Multi-core processor for better performance

## Installation Methods

### Method 1: Git Clone (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pixelbrow720/reddit-scraper.git
   cd reddit-scraper
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Method 2: Download ZIP

1. **Download the ZIP file** from GitHub
2. **Extract** to your desired location
3. **Open terminal/command prompt** in the extracted folder
4. **Follow steps 2-3** from Method 1

### Method 3: pip install (Future)

*This method will be available when the package is published to PyPI:*

```bash
pip install reddit-scraper
```

## Reddit API Setup

### Step 1: Create Reddit Account

If you don't have a Reddit account:
1. Go to [reddit.com](https://www.reddit.com)
2. Click "Sign Up"
3. Create your account

### Step 2: Create Reddit App

1. **Go to Reddit Apps page:**
   - Visit: https://www.reddit.com/prefs/apps
   - Log in to your Reddit account

2. **Create a new app:**
   - Click "Create App" or "Create Another App"
   - Fill in the form:
     - **Name:** `Reddit Scraper` (or any name you prefer)
     - **App type:** Select "script"
     - **Description:** `Data scraping tool` (optional)
     - **About URL:** Leave blank
     - **Redirect URI:** `http://localhost:8080` (required but not used)

3. **Save your credentials:**
   - **Client ID:** Found under the app name (short string)
   - **Client Secret:** The longer string labeled "secret"

### Step 3: Configure Reddit Scraper

Run the setup command:

```bash
python run.py setup
```

You'll be prompted to enter:
- **Reddit Client ID:** Your app's client ID
- **Reddit Client Secret:** Your app's client secret
- **User Agent:** (optional) Custom user agent string

Example:
```
Reddit Client ID: abc123def456
Reddit Client Secret: xyz789uvw012_secretkey
User Agent [RedditScraper/1.0]: MyRedditScraper/1.0 by /u/yourusername
```

## Configuration

### Basic Configuration

The setup command creates a configuration file at `config/settings.yaml`. You can edit this file to customize the scraper's behavior:

```yaml
reddit_api:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  user_agent: "RedditScraper/1.0 by /u/yourusername"

scraping:
  rate_limit: 1.0  # requests per second
  max_retries: 3
  timeout: 30

filtering:
  min_score: 1
  exclude_nsfw: true
  exclude_deleted: true

output:
  formats: ["json", "csv"]
  include_metadata: true
```

### Advanced Configuration

For advanced users, you can customize:

- **Rate limiting:** Adjust `rate_limit` (0.5-2.0 recommended)
- **Filtering:** Set minimum scores, age limits, content filters
- **Output:** Choose export formats and options
- **Logging:** Configure log levels and file locations

### Environment Variables (Optional)

For enhanced security, you can use environment variables:

```bash
# Windows
set REDDIT_CLIENT_ID=your_client_id
set REDDIT_CLIENT_SECRET=your_client_secret

# macOS/Linux
export REDDIT_CLIENT_ID=your_client_id
export REDDIT_CLIENT_SECRET=your_client_secret
```

## Verification

### Test Installation

1. **Test Reddit API connection:**
   ```bash
   python run.py test-connection
   ```

2. **Run a small test scrape:**
   ```bash
   python run.py scrape --subreddit python --posts 10
   ```

3. **Check output files:**
   - Look in the `output/` directory
   - Verify JSON and CSV files were created

### Expected Output

Successful installation should show:
```
✓ Reddit API connection successful!
✓ Retrieved 10 posts from r/python
✓ Exported 10 posts to output/json/reddit_posts_20240101_120000.json
✓ Exported 10 posts to output/csv/reddit_posts_20240101_120000.csv
```

## Troubleshooting

### Common Issues

#### 1. Python Version Error
```
Error: Python 3.8+ required
```
**Solution:** Install Python 3.8 or higher from [python.org](https://python.org)

#### 2. Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** 
- Use virtual environment
- Run with appropriate permissions
- Check file/folder permissions

#### 3. Module Not Found
```
ModuleNotFoundError: No module named 'praw'
```
**Solution:**
```bash
pip install -r requirements.txt
```

#### 4. Reddit API Connection Failed
```
✗ Reddit API connection failed!
```
**Solutions:**
- Verify your client ID and secret
- Check internet connection
- Ensure Reddit is accessible
- Try regenerating Reddit app credentials

#### 5. Rate Limit Exceeded
```
Rate limit exceeded
```
**Solutions:**
- Reduce `rate_limit` in configuration
- Wait before retrying
- Check if you're making too many requests

### Platform-Specific Issues

#### Windows

1. **PowerShell Execution Policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Long Path Support:**
   - Enable long path support in Windows settings
   - Or use shorter directory names

#### macOS

1. **Xcode Command Line Tools:**
   ```bash
   xcode-select --install
   ```

2. **Homebrew Python:**
   ```bash
   brew install python@3.9
   ```

#### Linux

1. **Python Development Headers:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev python3-pip
   
   # CentOS/RHEL
   sudo yum install python3-devel python3-pip
   ```

### Getting Help

If you encounter issues:

1. **Check the logs:**
   ```bash
   cat logs/scraper.log  # Linux/macOS
   type logs\scraper.log  # Windows
   ```

2. **Search existing issues:**
   - Check [GitHub Issues](https://github.com/pixelbrow720/reddit-scraper/issues)

3. **Create a new issue:**
   - Include error messages
   - Specify your operating system
   - Include Python version
   - Attach relevant log files

4. **Contact maintainer:**
   - GitHub: [@pixelbrow720](https://github.com/pixelbrow720)
   - Twitter: [@BrowPixel](https://twitter.com/BrowPixel)

## Next Steps

After successful installation:

1. **Read the main README** for usage examples
2. **Explore configuration options** in `config/settings.yaml`
3. **Try different scraping scenarios** with various subreddits
4. **Check the documentation** in the `docs/` folder

## Uninstallation

To remove Reddit Scraper:

1. **Deactivate virtual environment:**
   ```bash
   deactivate
   ```

2. **Remove the directory:**
   ```bash
   rm -rf reddit-scraper  # Linux/macOS
   rmdir /s reddit-scraper  # Windows
   ```

3. **Remove any global installations:**
   ```bash
   pip uninstall reddit-scraper
   ```

---

**Need help?** Contact [@pixelbrow720](https://github.com/pixelbrow720) or [@BrowPixel](https://twitter.com/BrowPixel)