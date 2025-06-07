# 🚀 Reddit Scraper v2.0 - Deployment Guide

Complete deployment guide for Reddit Scraper v2.0 with React.js dashboard.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Local Development](#-local-development)
- [Docker Deployment](#-docker-deployment)
- [Production Deployment](#-production-deployment)
- [Cloud Deployment](#-cloud-deployment)
- [Monitoring & Maintenance](#-monitoring--maintenance)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Option 1: One-Click Start (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/reddit-scraper-v2.git
cd reddit-scraper-v2

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Start dashboard
python start_dashboard.py
```

### Option 2: Docker (Production Ready)

```bash
# Clone repository
git clone https://github.com/your-username/reddit-scraper-v2.git
cd reddit-scraper-v2

# Start with Docker Compose
docker-compose up -d

# Access dashboard
open http://localhost:3000
```

## 💻 Local Development

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Git**
- **Reddit API credentials**

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Reddit API:**
   ```bash
   python run.py setup
   ```

4. **Start backend server:**
   ```bash
   # Development mode
   uvicorn src.api.dashboard_api:create_app --factory --reload

   # Or using CLI
   python run.py serve --reload
   ```

### Frontend Setup

1. **Navigate to frontend:**
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

4. **Access dashboard:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Workflow

```bash
# Terminal 1: Backend
uvicorn src.api.dashboard_api:create_app --factory --reload

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: CLI operations
python run.py scrape --subreddit python --posts 100 --use-database
```

## 🐳 Docker Deployment

### Development with Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Docker

1. **Create production environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build production images:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
   ```

3. **Start production services:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `reddit-scraper-api` | 8000 | FastAPI backend |
| `reddit-scraper-frontend` | 3000 | React.js frontend |
| `nginx` | 80, 443 | Reverse proxy |
| `redis` | 6379 | Caching (optional) |
| `prometheus` | 9090 | Metrics (optional) |
| `grafana` | 3001 | Monitoring (optional) |

## 🏭 Production Deployment

### Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 20.04+ / CentOS 8+

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 50GB SSD storage
- Load balancer

### Production Setup

1. **Server preparation:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clone and configure:**
   ```bash
   git clone https://github.com/your-username/reddit-scraper-v2.git
   cd reddit-scraper-v2

   # Create production config
   cp config/settings.example.yaml config/settings.yaml
   # Edit with production values

   # Setup environment
   cp .env.example .env
   # Edit with production values
   ```

3. **SSL Certificate setup:**
   ```bash
   # Create SSL directory
   mkdir -p nginx/ssl

   # Option 1: Self-signed (development)
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem

   # Option 2: Let's Encrypt (production)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
   ```

4. **Start production services:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Production Configuration

**Environment Variables (.env):**
```bash
# Database
DATABASE_PATH=/app/data/reddit_scraper.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Frontend
REACT_APP_API_URL=https://your-domain.com/api
REACT_APP_WS_URL=wss://your-domain.com/ws

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Redis (optional)
REDIS_URL=redis://redis:6379/0

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=secure-password
```

**Nginx Configuration (nginx/nginx.conf):**
```nginx
# Enable HTTPS redirect
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Your location blocks here...
}
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **EC2 Instance:**
   ```bash
   # Launch EC2 instance (t3.medium recommended)
   # Security groups: 22 (SSH), 80 (HTTP), 443 (HTTPS)
   
   # Connect and setup
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Follow production setup steps
   ```

2. **RDS Database (optional):**
   ```bash
   # Create PostgreSQL RDS instance
   # Update DATABASE_URL in environment
   ```

3. **Load Balancer:**
   ```bash
   # Create Application Load Balancer
   # Configure health checks: /health
   # Setup SSL certificate
   ```

### Google Cloud Platform

1. **Compute Engine:**
   ```bash
   # Create VM instance
   gcloud compute instances create reddit-scraper \
     --machine-type=e2-medium \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud
   ```

2. **Cloud SQL (optional):**
   ```bash
   # Create PostgreSQL instance
   gcloud sql instances create reddit-scraper-db \
     --database-version=POSTGRES_13 \
     --tier=db-f1-micro
   ```

### DigitalOcean

1. **Droplet:**
   ```bash
   # Create droplet via web interface or API
   # Choose Ubuntu 20.04, 2GB RAM minimum
   
   # Setup Docker and deploy
   ```

2. **Managed Database:**
   ```bash
   # Create managed PostgreSQL database
   # Update connection string
   ```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reddit-scraper
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reddit-scraper
  template:
    metadata:
      labels:
        app: reddit-scraper
    spec:
      containers:
      - name: api
        image: reddit-scraper:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: reddit-scraper-secrets
              key: database-url
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Database check
python run.py db --stats

# Frontend check
curl http://localhost:3000
```

### Monitoring Setup

1. **Prometheus metrics:**
   ```bash
   # Access Prometheus
   open http://localhost:9090
   
   # Key metrics to monitor:
   # - API response time
   # - Database connections
   # - Memory usage
   # - Error rates
   ```

2. **Grafana dashboards:**
   ```bash
   # Access Grafana
   open http://localhost:3001
   # Login: admin/admin
   
   # Import dashboard from monitoring/grafana/
   ```

3. **Log monitoring:**
   ```bash
   # View application logs
   docker-compose logs -f reddit-scraper-api
   
   # View Nginx logs
   docker-compose logs -f nginx
   ```

### Backup Strategy

```bash
# Database backup
python run.py db --export backup_$(date +%Y%m%d).db

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec reddit-scraper-api python run.py db --export $BACKUP_DIR/db_$DATE.db

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Maintenance Tasks

```bash
# Daily maintenance
python run.py db --cleanup --days 30

# Update dependencies
pip install -r requirements.txt --upgrade
cd frontend && npm update

# Security updates
docker-compose pull
docker-compose up -d
```

## 🔧 Troubleshooting

### Common Issues

1. **API not starting:**
   ```bash
   # Check logs
   docker-compose logs reddit-scraper-api
   
   # Common fixes:
   # - Check Reddit API credentials
   # - Verify database permissions
   # - Check port conflicts
   ```

2. **Frontend not loading:**
   ```bash
   # Check Node.js version
   node --version  # Should be 18+
   
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Database connection issues:**
   ```bash
   # Check database file permissions
   ls -la data/reddit_scraper.db
   
   # Reset database
   rm data/reddit_scraper.db
   python run.py scrape --subreddit test --posts 1 --use-database
   ```

4. **Memory issues:**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

### Performance Optimization

1. **Database optimization:**
   ```bash
   # Vacuum database
   sqlite3 data/reddit_scraper.db "VACUUM;"
   
   # Analyze query performance
   sqlite3 data/reddit_scraper.db ".timer on"
   ```

2. **API optimization:**
   ```bash
   # Increase worker processes
   uvicorn src.api.dashboard_api:create_app --workers 4
   
   # Enable caching
   # Set REDIS_URL in environment
   ```

3. **Frontend optimization:**
   ```bash
   # Build optimized production bundle
   cd frontend
   npm run build
   
   # Serve with nginx
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start with debug flags
python run.py serve --reload --host 0.0.0.0 --port 8000

# Frontend debug
cd frontend
REACT_APP_DEBUG=true npm start
```

### Getting Help

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/your-username/reddit-scraper-v2/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/reddit-scraper-v2/discussions)
- **Email:** support@reddit-scraper.com

---

**🚀 Happy Deploying!**

*Reddit Scraper v2.0 - Enterprise Edition*