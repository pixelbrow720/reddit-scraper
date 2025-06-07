# 🚀 Reddit Scraper v2.0 - Enterprise Edition

A comprehensive, production-ready Reddit scraping platform with modern React.js dashboard, advanced analytics, and enterprise-grade features.

![Reddit Scraper Dashboard](https://img.shields.io/badge/Dashboard-React.js-61DAFB?style=for-the-badge&logo=react)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

## ✨ **What's New in v2.0**

### 🎨 **Modern React.js Dashboard**
- **Beautiful dark theme** with Material-UI components
- **Real-time WebSocket updates** for live monitoring
- **Interactive charts** with Chart.js and Recharts
- **Responsive design** that works on all devices
- **Modern color palette** with gradients and animations

### 🗄️ **Database Integration**
- **SQLite database** for persistent storage
- **Data versioning** and backup capabilities
- **Advanced querying** with filtering and pagination
- **Performance optimization** with indexing
- **Automatic cleanup** of old data

### 🧠 **Advanced Analytics**
- **Sentiment analysis** with VADER and TextBlob
- **Trend prediction** with machine learning
- **Viral potential scoring** algorithm
- **Content categorization** and insights
- **Subreddit growth analysis**

### ⚡ **Enhanced Performance**
- **Parallel processing** with up to 10x speed improvement
- **Memory optimization** for large datasets
- **Intelligent caching** system
- **Performance monitoring** with detailed metrics
- **Resource usage tracking**

### 🐳 **Production Deployment**
- **Docker containerization** with multi-stage builds
- **Docker Compose** for easy orchestration
- **Nginx reverse proxy** with load balancing
- **Health checks** and monitoring
- **SSL/TLS support** ready

## 📋 **Table of Contents**

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 **Features**

### **Core Scraping Capabilities**
- ✅ Multi-subreddit parallel scraping
- ✅ Flexible sorting options (hot, new, top, rising)
- ✅ User profile collection
- ✅ Content extraction from external links
- ✅ Rate limiting with intelligent backoff
- ✅ Error handling and retry mechanisms

### **Data Processing & Analytics**
- ✅ Sentiment analysis (VADER + TextBlob + Custom patterns)
- ✅ Trend prediction with ML algorithms
- ✅ Viral potential scoring
- ✅ Content categorization
- ✅ Engagement analysis
- ✅ Time-based pattern recognition

### **Modern Dashboard**
- ✅ Real-time monitoring with WebSocket
- ✅ Interactive charts and visualizations
- ✅ Data browser with advanced filtering
- ✅ Session management
- ✅ Performance metrics
- ✅ Export capabilities

### **Enterprise Features**
- ✅ Database persistence with SQLite
- ✅ RESTful API with FastAPI
- ✅ Docker containerization
- ✅ Nginx reverse proxy
- ✅ Health checks and monitoring
- ✅ Comprehensive logging

### **Export Formats**
- ✅ **JSON** - Structured data with metadata
- ✅ **CSV** - Multiple files with breakdowns
- ✅ **HTML** - Interactive reports with charts
- ✅ **Database** - Persistent storage with querying

## 🚀 **Quick Start**

### **Option 1: Docker (Recommended)**

```bash
# Clone the repository
git clone https://github.com/your-username/reddit-scraper-v2.git
cd reddit-scraper-v2

# Start with Docker Compose
docker-compose up -d

# Access the dashboard
open http://localhost:3000
```

### **Option 2: Local Development**

```bash
# Clone and setup backend
git clone https://github.com/your-username/reddit-scraper-v2.git
cd reddit-scraper-v2

# Install Python dependencies
pip install -r requirements.txt

# Setup Reddit API credentials
python run.py setup

# Start the API server
uvicorn src.api.dashboard_api:create_app --reload --factory

# In another terminal, setup frontend
cd frontend
npm install
npm start

# Access the dashboard
open http://localhost:3000
```

## 📦 **Installation**

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (for containerized deployment)
- Reddit API credentials

### **Backend Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/reddit-scraper-v2.git
   cd reddit-scraper-v2
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Reddit API:**
   ```bash
   python run.py setup
   ```

### **Frontend Setup**

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

## ⚙️ **Configuration**

### **Reddit API Setup**

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new app (script type)
3. Note your `client_id` and `client_secret`
4. Run the setup command:
   ```bash
   python run.py setup
   ```

### **Configuration File**

Edit `config/settings.yaml`:

```yaml
reddit_api:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  user_agent: "RedditScraper/2.0"

scraping:
  rate_limit: 1.0  # requests per second
  max_retries: 3
  timeout: 30
  parallel_workers: 5

filtering:
  min_score: 1
  max_age_days: 365
  exclude_nsfw: true
  exclude_deleted: true

database:
  path: "data/reddit_scraper.db"
  cleanup_interval_days: 30

performance:
  cache_enabled: true
  cache_duration: 3600
  memory_limit_mb: 1024
```

## 🎮 **Usage**

### **Web Dashboard**

1. **Start the application:**
   ```bash
   # Backend
   uvicorn src.api.dashboard_api:create_app --factory

   # Frontend (in another terminal)
   cd frontend && npm start
   ```

2. **Access dashboard:** http://localhost:3000

3. **Features available:**
   - **Dashboard:** Real-time metrics and monitoring
   - **Scraping:** Start and manage scraping sessions
   - **Analytics:** Sentiment analysis and trend prediction
   - **Data:** Browse and export scraped data
   - **Settings:** Configure API and preferences

### **Command Line Interface**

```bash
# Basic scraping
python run.py scrape --subreddit python --posts 100

# Advanced scraping with all features
python run.py scrape \
  --subreddit "python,datascience,MachineLearning" \
  --posts 200 \
  --parallel \
  --extract-content \
  --include-users \
  --performance-monitor \
  --output "json,csv,html"

# Analytics
python run.py analyze --sentiment --trends --subreddit python

# Database management
python run.py db --stats
python run.py db --cleanup --days 30
```

### **API Usage**

```python
import requests

# Start scraping session
response = requests.post('http://localhost:8000/scrape/start', json={
    'subreddits': ['python', 'datascience'],
    'posts_per_subreddit': 100,
    'parallel': True,
    'extract_content': True
})

session_id = response.json()['session_id']

# Check status
status = requests.get(f'http://localhost:8000/scrape/status/{session_id}')
print(status.json())

# Get analytics
analytics = requests.get('http://localhost:8000/analytics/summary?days=7')
print(analytics.json())
```

## 📚 **API Documentation**

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/config` | Get configuration |
| `POST` | `/scrape/start` | Start scraping session |
| `GET` | `/scrape/status/{id}` | Get session status |
| `GET` | `/scrape/sessions` | List all sessions |
| `DELETE` | `/scrape/stop/{id}` | Stop session |

### **Data Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/data/posts` | Get posts with filtering |
| `GET` | `/analytics/summary` | Get analytics summary |
| `POST` | `/analytics/sentiment` | Run sentiment analysis |
| `POST` | `/analytics/trends` | Run trend analysis |
| `GET` | `/analytics/realtime` | Get real-time metrics |

### **WebSocket**

Connect to `ws://localhost:8000/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## 🛠️ **Development**

### **Project Structure**

```
reddit-scraper-v2/
├── src/                    # Backend source code
│   ├── api/               # FastAPI application
│   ├── core/              # Core scraping logic
│   ├── database/          # Database management
│   ├── analytics/         # Analytics and ML
│   ├── processors/        # Data processing
│   └── exporters/         # Export functionality
├── frontend/              # React.js dashboard
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   └── public/            # Static files
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Documentation
├── docker/                # Docker configurations
└── monitoring/            # Monitoring configs
```

### **Running Tests**

```bash
# Run all tests
python run_tests.py --all

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Run with coverage
python run_tests.py --coverage

# Frontend tests
cd frontend && npm test
```

### **Code Quality**

```bash
# Format code
python run_tests.py --format

# Lint code
python run_tests.py --lint

# Security scan
python run_tests.py --security

# Type checking
mypy src/
```

### **Development Workflow**

1. **Create feature branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes and test:**
   ```bash
   python run_tests.py --all
   ```

3. **Format and lint:**
   ```bash
   python run_tests.py --format --lint
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

## 🐳 **Deployment**

### **Docker Deployment**

1. **Build and run:**
   ```bash
   docker-compose up -d
   ```

2. **Scale services:**
   ```bash
   docker-compose up -d --scale reddit-scraper-api=3
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

### **Production Deployment**

1. **Setup environment:**
   ```bash
   # Copy production config
   cp config/settings.example.yaml config/settings.yaml
   
   # Edit with production values
   nano config/settings.yaml
   ```

2. **SSL Configuration:**
   ```bash
   # Generate SSL certificates
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
   ```

3. **Deploy with monitoring:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### **Monitoring**

- **Application:** http://localhost:3000
- **API Health:** http://localhost:8000/health
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (admin/admin)

## 🎨 **Design System**

### **Color Palette**

```css
/* Primary Colors */
--primary: #4a9eff;        /* Blue */
--secondary: #ff4500;      /* Reddit Orange */

/* Background */
--bg-primary: #0f0f0f;     /* Dark */
--bg-secondary: #1a1a1a;   /* Card Background */
--bg-tertiary: #2d2d2d;    /* Surface */

/* Text */
--text-primary: #ffffff;    /* Primary Text */
--text-secondary: #b0b0b0;  /* Secondary Text */

/* Status Colors */
--success: #4caf50;        /* Green */
--warning: #ff9800;        /* Orange */
--error: #f44336;          /* Red */
--info: #2196f3;           /* Blue */
```

### **Typography**

- **Font Family:** Inter, Roboto, Helvetica, Arial
- **Headings:** 700 weight, varied sizes
- **Body:** 400 weight, 1rem base size
- **Captions:** 300 weight, 0.875rem

## 📈 **Performance Benchmarks**

### **Scraping Performance**
- **Sequential:** ~100 posts/minute
- **Parallel (5 workers):** ~500 posts/minute
- **Memory usage:** <100MB for 10k posts
- **Database queries:** <50ms average

### **Dashboard Performance**
- **Initial load:** <2 seconds
- **Real-time updates:** <100ms latency
- **Chart rendering:** <500ms for 1k data points
- **API response:** <200ms average

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Development Setup**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### **Code Standards**

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write comprehensive tests
- Document new features
- Update CHANGELOG.md

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **PRAW** - Python Reddit API Wrapper
- **FastAPI** - Modern web framework
- **React.js** - Frontend framework
- **Material-UI** - React components
- **Chart.js** - Data visualization
- **Docker** - Containerization

## 📞 **Support**

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/your-username/reddit-scraper-v2/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/reddit-scraper-v2/discussions)
- **Email:** support@reddit-scraper.com

---

**Built with ❤️ by [@pixelbrow720](https://github.com/pixelbrow720)**

*Reddit Scraper v2.0 - Enterprise Edition*