"""Integration tests for Reddit Scraper."""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.cli.config import Config
from src.core.reddit_client import RedditClient
from src.processors.post_processor import PostProcessor
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.html_exporter import HTMLExporter


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete scraping workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        with open(self.config_file, 'w') as f:
            f.write("""
reddit_api:
  client_id: "test_client_id"
  client_secret: "test_client_secret"
  user_agent: "TestAgent/1.0"

scraping:
  rate_limit: 1.0
  max_retries: 3

filtering:
  min_score: 1
  exclude_nsfw: true
  exclude_deleted: true

output:
  formats: ["json", "csv", "html"]
  include_metadata: true
            """)
        
        # Mock sample data
        self.sample_posts = [
            {
                'id': 'post1',
                'title': 'Test Post 1',
                'author': 'user1',
                'subreddit': 'test',
                'score': 100,
                'upvote_ratio': 0.9,
                'num_comments': 50,
                'created_utc': 1640995200,
                'url': 'https://reddit.com/r/test/comments/post1',
                'permalink': '/r/test/comments/post1',
                'selftext': 'Test content 1',
                'link_url': None,
                'flair': 'Discussion',
                'is_nsfw': False,
                'is_spoiler': False,
                'is_self': True,
                'domain': 'self.test',
                'metadata': {
                    'scraped_at': '2024-01-01T00:00:00Z',
                    'content_type': 'text'
                }
            },
            {
                'id': 'post2',
                'title': 'Test Post 2',
                'author': 'user2',
                'subreddit': 'programming',
                'score': 75,
                'upvote_ratio': 0.8,
                'num_comments': 25,
                'created_utc': 1640995300,
                'url': 'https://example.com/article',
                'permalink': '/r/programming/comments/post2',
                'selftext': '',
                'link_url': 'https://example.com/article',
                'flair': 'Article',
                'is_nsfw': False,
                'is_spoiler': False,
                'is_self': False,
                'domain': 'example.com',
                'metadata': {
                    'scraped_at': '2024-01-01T00:00:00Z',
                    'content_type': 'link'
                }
            }
        ]
        
        self.sample_users = [
            {
                'username': 'user1',
                'id': 'user1_id',
                'created_utc': 1234567890,
                'comment_karma': 1000,
                'link_karma': 500,
                'is_verified': True,
                'has_premium': False,
                'profile_description': 'Test user 1',
                'metadata': {
                    'scraped_at': '2024-01-01T00:00:00Z'
                }
            },
            {
                'username': 'user2',
                'id': 'user2_id',
                'created_utc': 1234567891,
                'comment_karma': 750,
                'link_karma': 250,
                'is_verified': False,
                'has_premium': True,
                'profile_description': 'Test user 2',
                'metadata': {
                    'scraped_at': '2024-01-01T00:00:00Z'
                }
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.core.reddit_client.praw')
    def test_complete_scraping_workflow(self, mock_praw):
        """Test complete scraping workflow from config to export."""
        # Setup mocks
        mock_reddit = Mock()
        mock_praw.Reddit.return_value = mock_reddit
        
        # Mock subreddit posts
        mock_submissions = []
        for post_data in self.sample_posts:
            mock_submission = Mock()
            for key, value in post_data.items():
                if key == 'author':
                    mock_submission.author = Mock()
                    mock_submission.author.__str__ = Mock(return_value=value)
                elif key == 'subreddit':
                    mock_submission.subreddit = Mock()
                    mock_submission.subreddit.__str__ = Mock(return_value=value)
                elif key not in ['metadata']:
                    setattr(mock_submission, key, value)
            mock_submissions.append(mock_submission)
        
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = mock_submissions
        mock_reddit.subreddit.return_value = mock_subreddit
        
        # Mock user profiles
        mock_users = []
        for user_data in self.sample_users:
            mock_user = Mock()
            for key, value in user_data.items():
                if key not in ['metadata']:
                    setattr(mock_user, key, value)
            mock_users.append(mock_user)
        
        mock_reddit.redditor.side_effect = mock_users
        
        # Load configuration
        config = Config(self.config_file)
        
        # Initialize components
        reddit_config = config.get_reddit_config()
        client = RedditClient(**reddit_config)
        
        # Test connection
        self.assertTrue(client.test_connection())
        
        # Scrape posts
        posts = client.get_subreddit_posts("test", "hot", 10)
        self.assertEqual(len(posts), 2)
        
        # Get user profiles
        users = []
        for post in posts:
            author = post.get('author')
            if author and author != '[deleted]':
                user_profile = client.get_user_profile(author)
                if user_profile:
                    users.append(user_profile)
        
        self.assertEqual(len(users), 2)
        
        # Process posts
        filtering_config = config.get_filtering_config()
        processor = PostProcessor(**filtering_config)
        
        filtered_posts = processor.filter_posts(posts)
        deduplicated_posts = processor.deduplicate_posts(filtered_posts)
        enhanced_posts = processor.add_derived_fields(deduplicated_posts)
        
        self.assertEqual(len(enhanced_posts), 2)
        
        # Check derived fields
        for post in enhanced_posts:
            self.assertIn('title_clean', post)
            self.assertIn('category', post)
            self.assertIn('engagement_ratio', post)
        
        # Export to all formats
        output_dir = os.path.join(self.temp_dir, "output")
        
        # JSON export
        json_exporter = JSONExporter(output_dir=os.path.join(output_dir, "json"))
        json_file = json_exporter.export_combined(enhanced_posts, users, "test_export.json")
        self.assertTrue(os.path.exists(json_file))
        
        # CSV export
        csv_exporter = CSVExporter(output_dir=os.path.join(output_dir, "csv"))
        csv_file = csv_exporter.export_posts(enhanced_posts, "test_posts.csv")
        users_csv_file = csv_exporter.export_users(users, "test_users.csv")
        summary_file = csv_exporter.export_summary_stats(enhanced_posts, "test_summary.csv")
        
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(users_csv_file))
        self.assertTrue(os.path.exists(summary_file))
        
        # HTML export
        html_exporter = HTMLExporter(output_dir=os.path.join(output_dir, "html"))
        html_file = html_exporter.export_posts_report(enhanced_posts, users, "test_report.html")
        self.assertTrue(os.path.exists(html_file))
        
        # Verify file contents
        self._verify_json_export(json_file, enhanced_posts, users)
        self._verify_csv_export(csv_file, enhanced_posts)
        self._verify_html_export(html_file)
    
    def _verify_json_export(self, filepath, posts, users):
        """Verify JSON export content."""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('posts', data)
        self.assertIn('users', data)
        self.assertIn('statistics', data)
        
        self.assertEqual(len(data['posts']), len(posts))
        self.assertEqual(len(data['users']), len(users))
        
        # Check metadata
        metadata = data['metadata']
        self.assertIn('exported_at', metadata)
        self.assertIn('total_posts', metadata)
        self.assertIn('total_users', metadata)
        
        # Check statistics
        stats = data['statistics']
        self.assertIn('avg_score', stats)
        self.assertIn('total_comments', stats)
        self.assertIn('top_authors', stats)
    
    def _verify_csv_export(self, filepath, posts):
        """Verify CSV export content."""
        import csv
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), len(posts))
        
        # Check required columns
        required_columns = ['id', 'title', 'author', 'subreddit', 'score']
        for column in required_columns:
            self.assertIn(column, rows[0].keys())
        
        # Check data integrity
        for i, row in enumerate(rows):
            self.assertEqual(row['id'], posts[i]['id'])
            self.assertEqual(row['title'], posts[i]['title'])
    
    def _verify_html_export(self, filepath):
        """Verify HTML export content."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check HTML structure
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<html', content)
        self.assertIn('</html>', content)
        
        # Check content
        self.assertIn('Reddit Scraper Report', content)
        self.assertIn('Summary Statistics', content)
        self.assertIn('Data Visualization', content)
        self.assertIn('Top Posts', content)
        
        # Check Chart.js inclusion
        self.assertIn('chart.js', content)
        self.assertIn('canvas', content)
    
    @patch('src.core.reddit_client.praw')
    def test_error_handling_workflow(self, mock_praw):
        """Test error handling in the complete workflow."""
        # Setup mock to raise exception
        mock_praw.Reddit.side_effect = Exception("API Error")
        
        # Load configuration
        config = Config(self.config_file)
        reddit_config = config.get_reddit_config()
        
        # This should handle the exception gracefully
        client = RedditClient(**reddit_config)
        
        # Test connection should fail
        self.assertFalse(client.test_connection())
        
        # Scraping should return empty list
        posts = client.get_subreddit_posts("test", "hot", 10)
        self.assertEqual(len(posts), 0)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        config = Config(self.config_file)
        
        # Should validate successfully with test config
        self.assertTrue(config.validate_reddit_config())
        
        # Test invalid configuration
        config.set('reddit_api.client_id', '')
        self.assertFalse(config.validate_reddit_config())
    
    def test_filtering_edge_cases(self):
        """Test filtering with edge cases."""
        processor = PostProcessor(
            min_score=50,
            exclude_nsfw=True,
            exclude_deleted=True
        )
        
        # Test with posts that should be filtered out
        edge_case_posts = [
            {
                'id': 'low_score',
                'score': 10,  # Below threshold
                'is_nsfw': False,
                'author': 'user1',
                'created_utc': 1640995200
            },
            {
                'id': 'nsfw_post',
                'score': 100,
                'is_nsfw': True,  # NSFW
                'author': 'user2',
                'created_utc': 1640995200
            },
            {
                'id': 'deleted_post',
                'score': 75,
                'is_nsfw': False,
                'author': '[deleted]',  # Deleted
                'created_utc': 1640995200
            },
            {
                'id': 'good_post',
                'score': 100,
                'is_nsfw': False,
                'author': 'user3',
                'created_utc': 1640995200
            }
        ]
        
        filtered = processor.filter_posts(edge_case_posts)
        
        # Should only have the good post
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], 'good_post')


if __name__ == '__main__':
    unittest.main()