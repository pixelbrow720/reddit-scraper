"""Configuration management for Reddit scraper."""

import yaml
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for Reddit scraper."""
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
                return config or {}
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                return self._get_default_config()
        else:
            logger.info("Configuration file not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "reddit_api": {
                "client_id": "",
                "client_secret": "",
                "user_agent": "RedditScraper/1.0"
            },
            "scraping": {
                "rate_limit": 1.0,
                "max_retries": 3,
                "timeout": 30,
                "concurrent_workers": 5
            },
            "output": {
                "formats": ["json", "csv"],
                "include_metadata": True,
                "compress_output": False
            },
            "filtering": {
                "min_score": 1,
                "max_age_days": 365,
                "exclude_nsfw": True,
                "exclude_deleted": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/scraper.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'reddit_api.client_id')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        logger.debug(f"Configuration updated: {key} = {value}")
    
    def validate_reddit_config(self) -> bool:
        """Validate Reddit API configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        client_id = self.get('reddit_api.client_id')
        client_secret = self.get('reddit_api.client_secret')
        user_agent = self.get('reddit_api.user_agent')
        
        if not client_id or not client_secret or not user_agent:
            logger.error("Reddit API configuration is incomplete")
            return False
        
        if len(client_id) < 10 or len(client_secret) < 10:
            logger.error("Reddit API credentials appear to be invalid")
            return False
        
        return True
    
    def setup_reddit_config(self, client_id: str, client_secret: str, 
                           user_agent: str = None) -> None:
        """Setup Reddit API configuration.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string
        """
        self.set('reddit_api.client_id', client_id)
        self.set('reddit_api.client_secret', client_secret)
        
        if user_agent:
            self.set('reddit_api.user_agent', user_agent)
        
        logger.info("Reddit API configuration updated")
    
    def get_reddit_config(self) -> Dict[str, str]:
        """Get Reddit API configuration.
        
        Returns:
            Dictionary with Reddit API configuration
        """
        return {
            'client_id': self.get('reddit_api.client_id', ''),
            'client_secret': self.get('reddit_api.client_secret', ''),
            'user_agent': self.get('reddit_api.user_agent', 'RedditScraper/1.0')
        }
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping configuration.
        
        Returns:
            Dictionary with scraping configuration
        """
        return {
            'rate_limit': self.get('scraping.rate_limit', 1.0),
            'max_retries': self.get('scraping.max_retries', 3),
            'timeout': self.get('scraping.timeout', 30),
            'concurrent_workers': self.get('scraping.concurrent_workers', 5)
        }
    
    def get_filtering_config(self) -> Dict[str, Any]:
        """Get filtering configuration.
        
        Returns:
            Dictionary with filtering configuration
        """
        return {
            'min_score': self.get('filtering.min_score', 1),
            'max_age_days': self.get('filtering.max_age_days', 365),
            'exclude_nsfw': self.get('filtering.exclude_nsfw', True),
            'exclude_deleted': self.get('filtering.exclude_deleted', True)
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration.
        
        Returns:
            Dictionary with output configuration
        """
        return {
            'formats': self.get('output.formats', ['json', 'csv']),
            'include_metadata': self.get('output.include_metadata', True),
            'compress_output': self.get('output.compress_output', False)
        }
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_level = self.get('logging.level', 'INFO')
        log_file = self.get('logging.file', 'logs/scraper.log')
        log_format = self.get('logging.format', 
                             '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")


def create_default_config_file(config_file: str = "config/settings.yaml") -> None:
    """Create default configuration file.
    
    Args:
        config_file: Path to configuration file
    """
    config = Config()
    config.config_file = config_file
    config.save_config()
    print(f"Default configuration file created at {config_file}")
    print("Please edit the file to add your Reddit API credentials.")