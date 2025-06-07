#!/usr/bin/env python3
"""
Start Reddit Scraper Dashboard
Quick start script for the web dashboard
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import uvicorn
        import fastapi
        import praw
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("📦 Please install requirements: pip install -r requirements.txt")
        return False

def check_config():
    """Check if configuration exists."""
    config_file = Path("config/settings.yaml")
    if not config_file.exists():
        print("⚙️  Configuration file not found.")
        print("🔧 Run: python run.py setup")
        return False
    return True

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting Reddit Scraper API...")
    
    # Add src to Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    
    # Start uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.dashboard_api:create_app",
        "--factory",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    return subprocess.Popen(cmd, env=env)

def start_frontend():
    """Start the React frontend."""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    print("🎨 Starting React frontend...")
    
    # Start React development server
    cmd = ["npm", "start"]
    
    return subprocess.Popen(cmd, cwd=frontend_dir)

def main():
    """Main function to start the dashboard."""
    print("🎯 Reddit Scraper v2.0 - Dashboard Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        print("\n🔧 Setting up configuration...")
        subprocess.run([sys.executable, "run.py", "setup"])
    
    # Start backend
    backend_process = start_backend()
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Start frontend
    frontend_process = None
    frontend_dir = Path("frontend")
    
    if frontend_dir.exists():
        try:
            frontend_process = start_frontend()
            print("⏳ Waiting for frontend to start...")
            time.sleep(5)
            
            # Open browser
            print("🌐 Opening dashboard in browser...")
            webbrowser.open("http://localhost:3000")
            
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js to run the frontend.")
            print("📱 You can still access the API at: http://localhost:8000")
            print("📚 API documentation at: http://localhost:8000/docs")
    else:
        print("📱 Frontend not available. API running at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
    
    print("\n✅ Dashboard started successfully!")
    print("🎯 Dashboard: http://localhost:3000")
    print("🔧 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()