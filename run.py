#!/usr/bin/env python3
"""
Reddit Scraper - Main entry point
A comprehensive tool for scraping Reddit posts and user profiles.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.main import cli

if __name__ == '__main__':
    cli()