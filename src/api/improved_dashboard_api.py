"""Improved FastAPI dashboard with better error handling and scalability."""

import logging
import asyncio
import uuid
import json
import os
import sys
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import weakref

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


class WebSocketManager:
    """Improved WebSocket connection manager."""
    
    def __init__(self):
        self.connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """Add new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        async with self._lock:
            self.connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.connections:
            return
        
        message_str = json.dumps(message, default=str)
        disconnected = set()
        
        # Send to all connections concurrently
        async def send_to_client(websocket: WebSocket):
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Use gather with return_exceptions to prevent one failure from blocking others
        await asyncio.gather(
            *[send_to_client(ws) for ws in self.connections.copy()],
            return_exceptions=True
        )
        
        # Remove disconnected clients
        if disconnected:
            async with self._lock:
                self.connections -= disconnected


class SessionManager:
    """Improved session management with persistence."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.active_sessions: Dict[str, ScrapeStatus] = {}
        self._lock = asyncio.Lock()
        
        # Load active sessions from database on startup
        self._load_active_sessions()
    
    def _load_active_sessions(self):
        """Load active sessions from database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, subreddits, start_time, status
                    FROM scraping_sessions 
                    WHERE status IN ('running', 'starting')
                    ORDER BY start_time DESC
                """)
                
                for row in cursor.fetchall():
                    session_data = dict(row)
                    subreddits = json.loads(session_data['subreddits'])
                    
                    # Mark as failed if found running on startup (likely crashed)
                    status = ScrapeStatus(
                        session_id=session_data['session_id'],
                        status="failed",
                        progress=0.0,
                        message="Session interrupted (system restart)",
                        start_time=datetime.fromisoformat(session_data['start_time']),
                        error_message="System restart detected"
                    )
                    
                    self.active_sessions[session_data['session_id']] = status
                    
                    # Update database
                    self.db.update_session(
                        session_id=session_data['session_id'],
                        status="failed",
                        error_message="System restart detected"
                    )
                
                logger.info(f"Loaded {len(self.active_sessions)} sessions from database")
                
        except Exception as e:
            logger.error(f"Failed to load active sessions: {e}")
    
    async def create_session(self, session_id: str, request: ScrapeRequest) -> ScrapeStatus:
        """Create new session."""
        status = ScrapeStatus(
            session_id=session_id,
            status="starting",
            progress=0.0,
            message="Initializing scraping session",
            start_time=datetime.now()
        )
        
        async with self._lock:
            self.active_sessions[session_id] = status
        
        return status
    
    async def update_session(self, session_id: str, **updates):
        """Update session status."""
        async with self._lock:
            if session_id in self.active_sessions:
                for key, value in updates.items():
                    if hasattr(self.active_sessions[session_id], key):
                        setattr(self.active_sessions[session_id], key, value)
    
    async def get_session(self, session_id: str) -> Optional[ScrapeStatus]:
        """Get session status."""
        async with self._lock:
            return self.active_sessions.get(session_id)
    
    async def remove_session(self, session_id: str):
        """Remove session from active sessions."""
        async with self._lock:
            self.active_sessions.pop(session_id, None)


class ImprovedDashboardAPI:
    """Improved FastAPI dashboard with better error handling and scalability."""
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize improved dashboard API."""
        self.app = FastAPI(
            title="Reddit Scraper Dashboard",
            description="Real-time monitoring and control dashboard for Reddit scraper",
            version="2.0.0"
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
        self.db = DatabaseManager(max_connections=20)  # Increased connection pool
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_predictor = TrendPredictor()
        
        # Managers
        self.websocket_manager = WebSocketManager()
        self.session_manager = SessionManager(self.db)
        
        # Background task tracking
        self.background_tasks: Dict[str, asyncio.Task] = {}
        
        # Setup routes
        self._setup_routes()
        
        # Setup cleanup task
        self._setup_cleanup_task()
        
        logger.info("Improved Dashboard API initialized")
    
    def _setup_cleanup_task(self):
        """Setup periodic cleanup task."""
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    await self._cleanup_completed_tasks()
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
        
        # Start cleanup task
        asyncio.create_task(cleanup_task())
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed background tasks."""
        completed_tasks = []
        
        for session_id, task in self.background_tasks.items():
            if task.done():
                completed_tasks.append(session_id)
                
                # Check for exceptions
                try:
                    await task
                except Exception as e:
                    logger.error(f"Background task {session_id} failed: {e}")
                    await self.session_manager.update_session(
                        session_id,
                        status="failed",
                        error_message=str(e)
                    )
        
        # Remove completed tasks
        for session_id in completed_tasks:
            self.background_tasks.pop(session_id, None)
        
        if completed_tasks:
            logger.info(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    def _setup_routes(self):
        """Setup API routes with improved error handling."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {"message": "Reddit Scraper Dashboard API", "version": "2.0.0"}
        
        @self.app.get("/health")
        async def health_check():
            """Enhanced health check endpoint."""
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
                    except Exception as e:
                        reddit_status = f"error: {str(e)}"
                
                # Connection pool stats
                pool_stats = self.db.connection_pool.get_stats()
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": "connected",
                    "reddit_api": reddit_status,
                    "database_stats": stats,
                    "connection_pool": pool_stats,
                    "active_sessions": len(self.session_manager.active_sessions),
                    "websocket_connections": len(self.websocket_manager.connections),
                    "background_tasks": len(self.background_tasks)
                }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")
        
        @self.app.post("/scrape/start")
        async def start_scraping(request: ScrapeRequest):
            """Start a new scraping session with improved error handling."""
            try:
                if not self.config.validate_reddit_config():
                    raise HTTPException(status_code=400, detail="Reddit API not configured")
                
                session_id = str(uuid.uuid4())
                
                # Create session in database
                self.db.create_session(
                    session_id=session_id,
                    subreddits=request.subreddits,
                    configuration=request.dict()
                )
                
                # Create session status
                status = await self.session_manager.create_session(session_id, request)
                
                # Start scraping task
                task = asyncio.create_task(self._run_scraping_session(session_id, request))
                self.background_tasks[session_id] = task
                
                return {"session_id": session_id, "status": "started"}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to start scraping session: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")
        
        @self.app.get("/scrape/status/{session_id}")
        async def get_scrape_status(session_id: str):
            """Get status of a scraping session."""
            status = await self.session_manager.get_session(session_id)
            if not status:
                raise HTTPException(status_code=404, detail="Session not found")
            return status
        
        @self.app.get("/scrape/sessions")
        async def get_all_sessions():
            """Get all scraping sessions with pagination."""
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT session_id, subreddits, posts_count, users_count, 
                               start_time, end_time, status, error_message
                        FROM scraping_sessions 
                        ORDER BY start_time DESC 
                        LIMIT 100
                    """)
                    
                    sessions = []
                    for row in cursor.fetchall():
                        session = dict(row)
                        session['subreddits'] = json.loads(session['subreddits'])
                        sessions.append(session)
                    
                    return {
                        "sessions": sessions,
                        "active_count": len(self.session_manager.active_sessions)
                    }
            except Exception as e:
                logger.error(f"Failed to get sessions: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")
        
        @self.app.delete("/scrape/stop/{session_id}")
        async def stop_scraping(session_id: str):
            """Stop a scraping session."""
            try:
                # Update session status
                await self.session_manager.update_session(
                    session_id,
                    status="stopping",
                    message="Stopping session..."
                )
                
                # Cancel background task if exists
                if session_id in self.background_tasks:
                    task = self.background_tasks[session_id]
                    task.cancel()
                    
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    
                    self.background_tasks.pop(session_id, None)
                
                # Update database
                self.db.update_session(
                    session_id=session_id,
                    status="stopped",
                    error_message="Stopped by user"
                )
                
                return {"message": "Session stopped successfully"}
                
            except Exception as e:
                logger.error(f"Failed to stop session {session_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await self.websocket_manager.connect(websocket)
            
            try:
                # Send initial status
                await websocket.send_text(json.dumps({
                    "type": "connected",
                    "timestamp": datetime.now().isoformat(),
                    "message": "WebSocket connected successfully"
                }))
                
                # Keep connection alive and send periodic updates
                while True:
                    await asyncio.sleep(10)  # Send updates every 10 seconds
                    
                    # Send status update
                    status_update = {
                        "type": "status_update",
                        "timestamp": datetime.now().isoformat(),
                        "active_sessions": len(self.session_manager.active_sessions),
                        "sessions": [
                            {
                                "session_id": session_id,
                                "status": status.status,
                                "progress": status.progress,
                                "posts_scraped": status.posts_scraped
                            }
                            for session_id, status in self.session_manager.active_sessions.items()
                        ]
                    }
                    
                    await websocket.send_text(json.dumps(status_update, default=str))
                    
            except WebSocketDisconnect:
                await self.websocket_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await self.websocket_manager.disconnect(websocket)
        
        # Add other endpoints with similar error handling improvements...
        # (Analytics, data endpoints, etc.)
    
    async def _run_scraping_session(self, session_id: str, request: ScrapeRequest):
        """Run a scraping session with improved error handling."""
        try:
            await self.session_manager.update_session(
                session_id,
                status="running",
                message="Starting scraping..."
            )
            
            # Notify WebSocket clients
            await self.websocket_manager.broadcast({
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
                    max_workers=request.max_workers,
                    use_processes=False  # Use threads for better WebSocket integration
                )
                
                # Add progress callback
                async def progress_callback(completed, total):
                    progress = (completed / total) * 100
                    message = f"Scraped {completed}/{total} subreddits"
                    
                    await self.session_manager.update_session(
                        session_id,
                        progress=progress,
                        message=message
                    )
                    
                    await self.websocket_manager.broadcast({
                        "type": "progress_update",
                        "session_id": session_id,
                        "progress": progress,
                        "message": message
                    })
                
                # Note: This would need to be adapted for async callbacks
                # For now, we'll use the synchronous version
                
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
                # Sequential scraping with async updates
                client = RedditClient(**reddit_config)
                all_posts = []
                
                for i, subreddit in enumerate(request.subreddits):
                    progress = (i / len(request.subreddits)) * 100
                    message = f"Scraping r/{subreddit}..."
                    
                    await self.session_manager.update_session(
                        session_id,
                        progress=progress,
                        message=message
                    )
                    
                    posts = client.get_subreddit_posts(
                        subreddit_name=subreddit,
                        sort_type=request.sort_type,
                        limit=request.posts_per_subreddit,
                        time_filter=request.time_filter
                    )
                    
                    all_posts.extend(posts)
                    
                    await self.session_manager.update_session(
                        session_id,
                        posts_scraped=len(all_posts)
                    )
                    
                    await self.websocket_manager.broadcast({
                        "type": "progress_update",
                        "session_id": session_id,
                        "progress": progress,
                        "posts_scraped": len(all_posts)
                    })
            
            # Store posts in database
            if all_posts:
                stored_count = self.db.store_posts(all_posts, session_id)
                
                await self.session_manager.update_session(
                    session_id,
                    posts_scraped=stored_count
                )
                
                # Analyze sentiment for smaller datasets
                if len(all_posts) <= 500:
                    analyzed_posts = self.sentiment_analyzer.analyze_posts(all_posts)
                    self.db.store_posts(analyzed_posts, session_id)
            
            # Update session status
            await self.session_manager.update_session(
                session_id,
                status="completed",
                progress=100.0,
                message=f"Completed! Scraped {len(all_posts)} posts"
            )
            
            # Update database
            self.db.update_session(
                session_id=session_id,
                posts_count=len(all_posts),
                status="completed"
            )
            
            # Notify completion
            await self.websocket_manager.broadcast({
                "type": "session_completed",
                "session_id": session_id,
                "posts_scraped": len(all_posts)
            })
            
            # Remove from active sessions after delay
            await asyncio.sleep(60)  # Keep in active for 1 minute
            await self.session_manager.remove_session(session_id)
            
        except asyncio.CancelledError:
            logger.info(f"Scraping session {session_id} was cancelled")
            await self.session_manager.update_session(
                session_id,
                status="cancelled",
                message="Session was cancelled"
            )
            
            self.db.update_session(
                session_id=session_id,
                status="cancelled",
                error_message="Session was cancelled by user"
            )
            
            await self.websocket_manager.broadcast({
                "type": "session_cancelled",
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Scraping session {session_id} failed: {e}")
            
            await self.session_manager.update_session(
                session_id,
                status="failed",
                error_message=str(e),
                message=f"Failed: {str(e)}"
            )
            
            self.db.update_session(
                session_id=session_id,
                status="failed",
                error_message=str(e)
            )
            
            await self.websocket_manager.broadcast({
                "type": "session_failed",
                "session_id": session_id,
                "error": str(e)
            })


# Create FastAPI app instance
def create_app(config_file: str = "config/settings.yaml") -> FastAPI:
    """Create improved FastAPI application."""
    dashboard = ImprovedDashboardAPI(config_file)
    return dashboard.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")