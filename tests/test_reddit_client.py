"""Tests for Reddit client functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.reddit_client import RedditClient


class TestRedditClient(unittest.TestCase):
    """Test cases for RedditClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.user_agent = "TestAgent/1.0"
        
        # Mock PRAW to avoid actual API calls
        self.praw_patcher = patch('src.core.reddit_client.praw')
        self.mock_praw = self.praw_patcher.start()
        
        self.client = RedditClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.praw_patcher.stop()
    
    def test_client_initialization(self):
        """Test client initialization."""
        # Verify PRAW Reddit was called with correct parameters
        self.mock_praw.Reddit.assert_called_once_with(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
        # Verify read-only mode is set
        self.assertTrue(self.client.reddit.read_only)
    
    def test_test_connection_success(self):
        """Test successful connection test."""
        # Mock successful subreddit access
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [Mock()]
        self.client.reddit.subreddit.return_value = mock_subreddit
        
        result = self.client.test_connection()
        
        self.assertTrue(result)
        self.client.reddit.subreddit.assert_called_once_with("python")
        mock_subreddit.hot.assert_called_once_with(limit=1)
    
    def test_test_connection_failure(self):
        """Test connection test failure."""
        # Mock exception during subreddit access
        self.client.reddit.subreddit.side_effect = Exception("Connection failed")
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
    
    def test_get_subreddit_posts_hot(self):
        """Test getting hot posts from subreddit."""
        # Mock submission data
        mock_submission = Mock()
        mock_submission.id = "test_id"
        mock_submission.title = "Test Title"
        mock_submission.author = Mock()
        mock_submission.author.__str__ = Mock(return_value="test_author")
        mock_submission.subreddit = Mock()
        mock_submission.subreddit.__str__ = Mock(return_value="test_subreddit")
        mock_submission.score = 100
        mock_submission.upvote_ratio = 0.85
        mock_submission.num_comments = 50
        mock_submission.created_utc = 1640995200
        mock_submission.url = "https://reddit.com/test"
        mock_submission.permalink = "/r/test/comments/test"
        mock_submission.selftext = "Test content"
        mock_submission.link_flair_text = "Discussion"
        mock_submission.over_18 = False
        mock_submission.spoiler = False
        mock_submission.is_self = True
        mock_submission.domain = "self.test"
        
        # Mock subreddit and hot posts
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_submission]
        self.client.reddit.subreddit.return_value = mock_subreddit
        
        posts = self.client.get_subreddit_posts("test", "hot", 10)
        
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post['id'], "test_id")
        self.assertEqual(post['title'], "Test Title")
        self.assertEqual(post['author'], "test_author")
        self.assertEqual(post['score'], 100)
        self.assertTrue(post['is_self'])
    
    def test_get_subreddit_posts_top(self):
        """Test getting top posts from subreddit."""
        mock_subreddit = Mock()
        mock_subreddit.top.return_value = []
        self.client.reddit.subreddit.return_value = mock_subreddit
        
        posts = self.client.get_subreddit_posts("test", "top", 10, "week")
        
        mock_subreddit.top.assert_called_once_with(time_filter="week", limit=10)
        self.assertEqual(len(posts), 0)
    
    def test_get_subreddit_posts_invalid_sort(self):
        """Test getting posts with invalid sort type."""
        posts = self.client.get_subreddit_posts("test", "invalid", 10)
        
        self.assertEqual(len(posts), 0)
    
    def test_get_subreddit_posts_exception(self):
        """Test handling exception during post retrieval."""
        self.client.reddit.subreddit.side_effect = Exception("API Error")
        
        posts = self.client.get_subreddit_posts("test", "hot", 10)
        
        self.assertEqual(len(posts), 0)
    
    def test_get_user_profile_success(self):
        """Test successful user profile retrieval."""
        # Mock user data
        mock_user = Mock()
        mock_user.name = "test_user"
        mock_user.id = "user_id"
        mock_user.created_utc = 1234567890
        mock_user.comment_karma = 1000
        mock_user.link_karma = 500
        mock_user.verified = True
        mock_user.is_gold = False
        
        self.client.reddit.redditor.return_value = mock_user
        
        profile = self.client.get_user_profile("test_user")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['username'], "test_user")
        self.assertEqual(profile['comment_karma'], 1000)
        self.assertEqual(profile['link_karma'], 500)
        self.assertTrue(profile['is_verified'])
    
    def test_get_user_profile_not_found(self):
        """Test user profile retrieval for non-existent user."""
        mock_user = Mock()
        mock_user.created_utc = Mock(side_effect=Exception("User not found"))
        
        self.client.reddit.redditor.return_value = mock_user
        
        profile = self.client.get_user_profile("nonexistent_user")
        
        self.assertIsNone(profile)
    
    def test_get_user_profile_exception(self):
        """Test handling exception during user profile retrieval."""
        self.client.reddit.redditor.side_effect = Exception("API Error")
        
        profile = self.client.get_user_profile("test_user")
        
        self.assertIsNone(profile)
    
    def test_determine_content_type_text(self):
        """Test content type determination for text posts."""
        mock_submission = Mock()
        mock_submission.is_self = True
        
        content_type = self.client._determine_content_type(mock_submission)
        
        self.assertEqual(content_type, "text")
    
    def test_determine_content_type_image(self):
        """Test content type determination for image posts."""
        mock_submission = Mock()
        mock_submission.is_self = False
        mock_submission.url = "https://example.com/image.jpg"
        
        content_type = self.client._determine_content_type(mock_submission)
        
        self.assertEqual(content_type, "image")
    
    def test_determine_content_type_video(self):
        """Test content type determination for video posts."""
        mock_submission = Mock()
        mock_submission.is_self = False
        mock_submission.url = "https://youtube.com/watch?v=test"
        mock_submission.domain = "youtube.com"
        
        content_type = self.client._determine_content_type(mock_submission)
        
        self.assertEqual(content_type, "video")
    
    def test_determine_content_type_link(self):
        """Test content type determination for link posts."""
        mock_submission = Mock()
        mock_submission.is_self = False
        mock_submission.url = "https://example.com/article"
        mock_submission.domain = "example.com"
        
        content_type = self.client._determine_content_type(mock_submission)
        
        self.assertEqual(content_type, "link")


if __name__ == '__main__':
    unittest.main()