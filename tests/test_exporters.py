"""Tests for data exporters."""

import unittest
import tempfile
import os
import json
import csv
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.html_exporter import HTMLExporter


class TestJSONExporter(unittest.TestCase):
    """Test cases for JSONExporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = JSONExporter(output_dir=self.temp_dir)
        
        self.sample_posts = [
            {
                'id': 'post1',
                'title': 'Test Post 1',
                'author': 'user1',
                'subreddit': 'test',
                'score': 100,
                'num_comments': 50,
                'created_utc': 1640995200
            },
            {
                'id': 'post2',
                'title': 'Test Post 2',
                'author': 'user2',
                'subreddit': 'test',
                'score': 75,
                'num_comments': 25,
                'created_utc': 1640995300
            }
        ]
        
        self.sample_users = [
            {
                'username': 'user1',
                'comment_karma': 1000,
                'link_karma': 500
            },
            {
                'username': 'user2',
                'comment_karma': 750,
                'link_karma': 250
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_export_posts(self):
        """Test exporting posts to JSON."""
        filepath = self.exporter.export_posts(self.sample_posts, "test_posts.json")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('posts', data)
        self.assertEqual(len(data['posts']), 2)
        self.assertEqual(data['posts'][0]['id'], 'post1')
    
    def test_export_users(self):
        """Test exporting users to JSON."""
        filepath = self.exporter.export_users(self.sample_users, "test_users.json")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('users', data)
        self.assertEqual(len(data['users']), 2)
        self.assertEqual(data['users'][0]['username'], 'user1')
    
    def test_export_combined(self):
        """Test exporting combined posts and users."""
        filepath = self.exporter.export_combined(self.sample_posts, self.sample_users, "test_combined.json")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('posts', data)
        self.assertIn('users', data)
        self.assertIn('statistics', data)
        self.assertEqual(len(data['posts']), 2)
        self.assertEqual(len(data['users']), 2)
    
    def test_generate_statistics(self):
        """Test statistics generation."""
        stats = self.exporter._generate_statistics(self.sample_posts)
        
        self.assertEqual(stats['total_posts'], 2)
        self.assertEqual(stats['avg_score'], 87.5)  # (100 + 75) / 2
        self.assertEqual(stats['total_comments'], 75)  # 50 + 25
        self.assertIn('subreddits', stats)
    
    def test_auto_filename_generation(self):
        """Test automatic filename generation."""
        filepath = self.exporter.export_posts(self.sample_posts)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.basename(filepath).startswith('reddit_posts_'))
        self.assertTrue(filepath.endswith('.json'))


class TestCSVExporter(unittest.TestCase):
    """Test cases for CSVExporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = CSVExporter(output_dir=self.temp_dir)
        
        self.sample_posts = [
            {
                'id': 'post1',
                'title': 'Test Post 1',
                'author': 'user1',
                'subreddit': 'test',
                'score': 100,
                'num_comments': 50,
                'created_utc': 1640995200,
                'is_nsfw': False,
                'category': 'text'
            },
            {
                'id': 'post2',
                'title': 'Test Post 2',
                'author': 'user2',
                'subreddit': 'programming',
                'score': 75,
                'num_comments': 25,
                'created_utc': 1640995300,
                'is_nsfw': False,
                'category': 'link'
            }
        ]
        
        self.sample_users = [
            {
                'username': 'user1',
                'comment_karma': 1000,
                'link_karma': 500,
                'is_verified': True
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_export_posts(self):
        """Test exporting posts to CSV."""
        filepath = self.exporter.export_posts(self.sample_posts, "test_posts.csv")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['id'], 'post1')
        self.assertEqual(rows[0]['title'], 'Test Post 1')
        self.assertEqual(rows[1]['id'], 'post2')
    
    def test_export_users(self):
        """Test exporting users to CSV."""
        filepath = self.exporter.export_users(self.sample_users, "test_users.csv")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['username'], 'user1')
        self.assertEqual(rows[0]['is_verified'], 'True')
    
    def test_export_summary_stats(self):
        """Test exporting summary statistics."""
        filepath = self.exporter.export_summary_stats(self.sample_posts, "test_summary.csv")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Check header
        self.assertEqual(rows[0], ['Metric', 'Value'])
        
        # Check some metrics
        metrics = {row[0]: row[1] for row in rows[1:]}
        self.assertEqual(metrics['Total Posts'], '2')
        self.assertEqual(metrics['Unique Subreddits'], '2')
    
    def test_export_subreddit_breakdown(self):
        """Test exporting subreddit breakdown."""
        filepath = self.exporter.export_subreddit_breakdown(self.sample_posts, "test_breakdown.csv")
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)  # Two different subreddits
        
        # Check if subreddits are present
        subreddits = [row['Subreddit'] for row in rows]
        self.assertIn('test', subreddits)
        self.assertIn('programming', subreddits)
    
    def test_clean_post_for_csv(self):
        """Test post cleaning for CSV export."""
        post = {
            'title': 'Test\nTitle\rwith\nnewlines',
            'is_nsfw': True,
            'score': None
        }
        
        cleaned = self.exporter._clean_post_for_csv(post)
        
        # Check newlines are removed
        self.assertEqual(cleaned['title'], 'Test Title with newlines')
        
        # Check boolean conversion
        self.assertEqual(cleaned['is_nsfw'], 'True')
        
        # Check None handling
        self.assertEqual(cleaned['score'], '')


class TestHTMLExporter(unittest.TestCase):
    """Test cases for HTMLExporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = HTMLExporter(output_dir=self.temp_dir, dark_theme=True)
        
        self.sample_posts = [
            {
                'id': 'post1',
                'title': 'Test Post 1',
                'author': 'user1',
                'subreddit': 'test',
                'score': 100,
                'num_comments': 50,
                'created_utc': 1640995200,
                'permalink': '/r/test/comments/post1',
                'category': 'text'
            },
            {
                'id': 'post2',
                'title': 'Test Post 2',
                'author': 'user2',
                'subreddit': 'programming',
                'score': 75,
                'num_comments': 25,
                'created_utc': 1640995300,
                'permalink': '/r/programming/comments/post2',
                'category': 'link'
            }
        ]
        
        self.sample_users = [
            {
                'username': 'user1',
                'comment_karma': 1000,
                'link_karma': 500
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_export_posts_report(self):
        """Test exporting HTML report."""
        filepath = self.exporter.export_posts_report(
            self.sample_posts, 
            self.sample_users, 
            "test_report.html"
        )
        
        self.assertTrue(os.path.exists(filepath))
        
        # Verify it's valid HTML
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<html', content)
        self.assertIn('Reddit Scraper Report', content)
        self.assertIn('Test Post 1', content)
        self.assertIn('Test Post 2', content)
    
    def test_generate_statistics(self):
        """Test statistics generation for HTML."""
        stats = self.exporter._generate_statistics(self.sample_posts, self.sample_users)
        
        self.assertEqual(stats['total_posts'], 2)
        self.assertEqual(stats['avg_score'], 87.5)
        self.assertEqual(stats['total_users'], 1)
        self.assertEqual(stats['unique_subreddits'], 2)
    
    def test_prepare_charts_data(self):
        """Test chart data preparation."""
        charts_data = self.exporter._prepare_charts_data(self.sample_posts)
        
        self.assertIn('score_distribution', charts_data)
        self.assertIn('hourly_posts', charts_data)
        self.assertIn('subreddit_distribution', charts_data)
        self.assertIn('content_types', charts_data)
        
        # Check score distribution
        score_dist = charts_data['score_distribution']
        self.assertIn('labels', score_dist)
        self.assertIn('data', score_dist)
        
        # Check subreddit distribution
        sub_dist = charts_data['subreddit_distribution']
        self.assertIn('r/test', sub_dist['labels'])
        self.assertIn('r/programming', sub_dist['labels'])
    
    def test_dark_theme_css(self):
        """Test dark theme CSS generation."""
        css = self.exporter._get_css_styles()
        
        self.assertIn('--bg-primary: #1a1a1a', css)
        self.assertIn('--text-primary: #ffffff', css)
        self.assertIn('dark', css.lower())
    
    def test_auto_filename_generation(self):
        """Test automatic filename generation."""
        filepath = self.exporter.export_posts_report(self.sample_posts)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.basename(filepath).startswith('reddit_report_'))
        self.assertTrue(filepath.endswith('.html'))


if __name__ == '__main__':
    unittest.main()