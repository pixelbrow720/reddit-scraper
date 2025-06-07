"""FastAPI dashboard for Reddit scraper monitoring and control."""

import logging
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.database_manager import DatabaseManager
from src.core.reddit_client import RedditClient
from src.core.parallel_scraper import ParallelScraper
from src.analytics.sentiment_analyzer import SentimentAnalyzer
from src.analytics.trend_predictor import TrendPredictor
from src.cli.config import Config

logger = logging.getLogger(__name__)


# Pydantic models
class ScrapeRequest(BaseModel):
    subreddits: List[str]
    posts_per_subreddit: int = 100
    sort_type: str = "hot"
    time_filter: str = "all"
    include_users: bool = False
    extract_content: bool = False
    parallel: bool = True
    max_workers: int = 5


class ScrapeStatus(BaseModel):
    session_id: str
    status: str
    progress: float
    message: str
    start_time: datetime
    posts_scraped: int = 0
    users_scraped: int = 0
    error_message: Optional[str] = None


class AnalyticsRequest(BaseModel):
    subreddit: Optional[str] = None
    days_back: int = 7
    min_score: Optional[int] = None


# Global state
active_sessions = {}
websocket_connections = []


class DashboardAPI:
    """FastAPI dashboard for Reddit scraper."""
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize dashboard API.
        
        Args:
            config_file: Path to configuration file
        """
        self.app = FastAPI(
            title="Reddit Scraper Dashboard",
            description="Real-time monitoring and control dashboard for Reddit scraper",
            version="1.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.config = Config(config_file)
        self.db = DatabaseManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_predictor = TrendPredictor()
        
        # Setup routes
        self._setup_routes()
        
        logger.info("Dashboard API initialized")
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {"message": "Reddit Scraper Dashboard API", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                # Test database connection
                stats = self.db.get_database_stats()
                
                # Test Reddit API if configured
                reddit_status = "not_configured"
                if self.config.validate_reddit_config():
                    try:
                        reddit_config = self.config.get_reddit_config()
                        client = RedditClient(**reddit_config)
                        if client.test_connection():
                            reddit_status = "connected"
                        else:
                            reddit_status = "connection_failed"
                    except Exception:
                        reddit_status = "error"
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": "connected",
                    "reddit_api": reddit_status,
                    "database_stats": stats
                }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail="Service unhealthy")
        
        @self.app.post("/scrape/start")
        async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
            """Start a new scraping session."""
            if not self.config.validate_reddit_config():
                raise HTTPException(status_code=400, detail="Reddit API not configured")
            
            session_id = str(uuid.uuid4())
            
            # Create session in database
            self.db.create_session(
                session_id=session_id,
                subreddits=request.subreddits,
                configuration=request.dict()
            )
            
            # Initialize session status
            status = ScrapeStatus(
                session_id=session_id,
                status="starting",
                progress=0.0,
                message="Initializing scraping session",
                start_time=datetime.now()
            )
            active_sessions[session_id] = status
            
            # Start scraping in background
            background_tasks.add_task(self._run_scraping_session, session_id, request)
            
            return {"session_id": session_id, "status": "started"}
        
        @self.app.get("/scrape/status/{session_id}")
        async def get_scrape_status(session_id: str):
            """Get status of a scraping session."""
            if session_id not in active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return active_sessions[session_id]
        
        @self.app.get("/scrape/sessions")
        async def get_all_sessions():
            """Get all scraping sessions."""
            # Get from database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, subreddits, posts_count, users_count, 
                           start_time, end_time, status, error_message
                    FROM scraping_sessions 
                    ORDER BY start_time DESC 
                    LIMIT 50
                """)
                
                sessions = []
                for row in cursor.fetchall():
                    session = dict(row)
                    session['subreddits'] = json.loads(session['subreddits'])
                    sessions.append(session)
                
                return sessions
        
        @self.app.delete("/scrape/stop/{session_id}")
        async def stop_scraping(session_id: str):
            """Stop a scraping session."""
            if session_id in active_sessions:
                active_sessions[session_id].status = "stopping"
                active_sessions[session_id].message = "Stopping session..."
                return {"message": "Session stop requested"}
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        
        @self.app.get("/data/posts")
        async def get_posts(
            subreddit: Optional[str] = None,
            limit: int = 100,
            min_score: Optional[int] = None,
            days_back: int = 7
        ):
            """Get posts from database."""
            start_date = datetime.now() - timedelta(days=days_back)
            
            posts = self.db.get_posts(
                subreddit=subreddit,
                limit=limit,
                min_score=min_score,
                start_date=start_date
            )
            
            return {"posts": posts, "count": len(posts)}
        
        @self.app.get("/analytics/summary")
        async def get_analytics_summary(days: int = 7):
            """Get analytics summary."""
            # Check cache first
            cache_key = f"analytics_summary_{days}"
            cached_data = self.db.get_cached_analytics(cache_key)
            
            if cached_data:
                return cached_data
            
            # Generate new analytics
            summary = self.db.get_analytics_summary(days)
            
            # Cache for 1 hour
            self.db.set_cached_analytics(cache_key, summary, expires_in_hours=1)
            
            return summary
        
        @self.app.post("/analytics/sentiment")
        async def analyze_sentiment(request: AnalyticsRequest):
            """Analyze sentiment for posts."""
            start_date = datetime.now() - timedelta(days=request.days_back)
            
            posts = self.db.get_posts(
                subreddit=request.subreddit,
                limit=1000,
                min_score=request.min_score,
                start_date=start_date
            )
            
            if not posts:
                return {"message": "No posts found for analysis"}
            
            # Analyze sentiment
            analyzed_posts = self.sentiment_analyzer.analyze_posts(posts)
            sentiment_summary = self.sentiment_analyzer.get_sentiment_summary(analyzed_posts)
            
            # Store analyzed posts back to database
            self.db.store_posts(analyzed_posts)
            
            return {
                "sentiment_summary": sentiment_summary,
                "posts_analyzed": len(analyzed_posts)
            }
        
        @self.app.post("/analytics/trends")
        async def analyze_trends(request: AnalyticsRequest):
            """Analyze trends for posts."""
            start_date = datetime.now() - timedelta(days=request.days_back)
            
            posts = self.db.get_posts(
                subreddit=request.subreddit,
                limit=1000,
                min_score=request.min_score,
                start_date=start_date
            )
            
            if not posts:
                return {"message": "No posts found for analysis"}
            
            # Analyze trends
            posting_trends = self.trend_predictor.analyze_posting_trends(posts, request.days_back)
            engagement_trends = self.trend_predictor.analyze_engagement_trends(posts)
            subreddit_trends = self.trend_predictor.analyze_subreddit_trends(posts)
            content_trends = self.trend_predictor.analyze_content_trends(posts)
            
            # Predict viral potential
            viral_posts = self.trend_predictor.predict_viral_potential(posts[:100])
            
            return {
                "posting_trends": posting_trends,
                "engagement_trends": engagement_trends,
                "subreddit_trends": subreddit_trends,
                "content_trends": content_trends,
                "viral_predictions": viral_posts[:10]  # Top 10 viral potential
            }
        
        @self.app.get("/analytics/realtime")
        async def get_realtime_analytics():
            """Get real-time analytics data."""
            # Get recent posts (last 24 hours)
            start_date = datetime.now() - timedelta(hours=24)
            recent_posts = self.db.get_posts(limit=500, start_date=start_date)
            
            if not recent_posts:
                return {"message": "No recent posts found"}
            
            # Quick analytics
            total_posts = len(recent_posts)
            avg_score = sum(p.get('score', 0) for p in recent_posts) / total_posts
            total_comments = sum(p.get('num_comments', 0) for p in recent_posts)
            
            # Hourly breakdown
            hourly_counts = {}
            for post in recent_posts:
                created_utc = post.get('created_utc', 0)
                if created_utc > 0:
                    hour = datetime.fromtimestamp(created_utc).hour
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            # Top subreddits
            subreddit_counts = {}
            for post in recent_posts:
                subreddit = post.get('subreddit', 'unknown')
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_posts_24h": total_posts,
                "average_score": round(avg_score, 2),
                "total_comments": total_comments,
                "hourly_distribution": hourly_counts,
                "top_subreddits": [{"subreddit": s, "count": c} for s, c in top_subreddits]
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            websocket_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await asyncio.sleep(5)
                    
                    # Get current status
                    status_update = {
                        "type": "status_update",
                        "timestamp": datetime.now().isoformat(),
                        "active_sessions": len(active_sessions),
                        "sessions": [
                            {
                                "session_id": sid,
                                "status": status.status,
                                "progress": status.progress,
                                "posts_scraped": status.posts_scraped
                            }
                            for sid, status in active_sessions.items()
                        ]
                    }
                    
                    await websocket.send_text(json.dumps(status_update))
                    
            except WebSocketDisconnect:
                websocket_connections.remove(websocket)
        
        @self.app.get("/config")
        async def get_configuration():
            """Get current configuration."""
            return {
                "reddit_configured": self.config.validate_reddit_config(),
                "database_path": self.db.db_path,
                "scraping_config": self.config.get_scraping_config(),
                "filtering_config": self.config.get_filtering_config()
            }
        
        @self.app.get("/stats/database")
        async def get_database_stats():
            """Get database statistics."""
            return self.db.get_database_stats()
    
    async def _run_scraping_session(self, session_id: str, request: ScrapeRequest):
        """Run a scraping session in the background."""
        try:
            status = active_sessions[session_id]
            status.status = "running"
            status.message = "Starting scraping..."
            
            # Notify WebSocket clients
            await self._notify_websocket_clients({
                "type": "session_started",
                "session_id": session_id,
                "subreddits": request.subreddits
            })
            
            # Get Reddit configuration
            reddit_config = self.config.get_reddit_config()
            
            if request.parallel and len(request.subreddits) > 1:
                # Use parallel scraper
                parallel_scraper = ParallelScraper(
                    reddit_config=reddit_config,
                    max_workers=request.max_workers
                )
                
                # Add progress callback
                def progress_callback(completed, total):
                    status.progress = (completed / total) * 100
                    status.message = f"Scraped {completed}/{total} subreddits"
                    asyncio.create_task(self._notify_websocket_clients({
                        "type": "progress_update",
                        "session_id": session_id,
                        "progress": status.progress,
                        "message": status.message
                    }))
                
                parallel_scraper.add_progress_callback(progress_callback)
                
                # Execute scraping
                results = parallel_scraper.scrape_multiple_subreddits(
                    subreddits=request.subreddits,
                    sort_type=request.sort_type,
                    posts_per_subreddit=request.posts_per_subreddit,
                    time_filter=request.time_filter
                )
                
                # Collect all posts
                all_posts = []
                for result in results:
                    if result.success:
                        all_posts.extend(result.posts)
                
            else:
                # Sequential scraping
                client = RedditClient(**reddit_config)
                all_posts = []
                
                for i, subreddit in enumerate(request.subreddits):
                    status.progress = (i / len(request.subreddits)) * 100
                    status.message = f"Scraping r/{subreddit}..."
                    
                    posts = client.get_subreddit_posts(
                        subreddit_name=subreddit,
                        sort_type=request.sort_type,
                        limit=request.posts_per_subreddit,
                        time_filter=request.time_filter
                    )
                    
                    all_posts.extend(posts)
                    status.posts_scraped = len(all_posts)
                    
                    await self._notify_websocket_clients({
                        "type": "progress_update",
                        "session_id": session_id,
                        "progress": status.progress,
                        "posts_scraped": status.posts_scraped
                    })
            
            # Store posts in database
            if all_posts:
                stored_count = self.db.store_posts(all_posts, session_id)
                status.posts_scraped = stored_count
                
                # Analyze sentiment if enabled
                if len(all_posts) <= 500:  # Only for smaller datasets
                    analyzed_posts = self.sentiment_analyzer.analyze_posts(all_posts)
                    self.db.store_posts(analyzed_posts, session_id)
            
            # Update session status
            status.status = "completed"
            status.progress = 100.0
            status.message = f"Completed! Scraped {len(all_posts)} posts"
            
            # Update database
            self.db.update_session(
                session_id=session_id,
                posts_count=len(all_posts),
                status="completed"
            )
            
            # Notify completion
            await self._notify_websocket_clients({
                "type": "session_completed",
                "session_id": session_id,
                "posts_scraped": len(all_posts)
            })
            
        except Exception as e:
            logger.error(f"Scraping session {session_id} failed: {e}")
            
            status.status = "failed"
            status.error_message = str(e)
            status.message = f"Failed: {str(e)}"
            
            # Update database
            self.db.update_session(
                session_id=session_id,
                status="failed",
                error_message=str(e)
            )
            
            # Notify failure
            await self._notify_websocket_clients({
                "type": "session_failed",
                "session_id": session_id,
                "error": str(e)
            })
    
    async def _notify_websocket_clients(self, message: Dict[str, Any]):
        """Notify all WebSocket clients."""
        if not websocket_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message_str)
            except Exception:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            websocket_connections.remove(websocket)


# Create FastAPI app instance
def create_app(config_file: str = "config/settings.yaml") -> FastAPI:
    """Create FastAPI application."""
    dashboard = DashboardAPI(config_file)
    return dashboard.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")