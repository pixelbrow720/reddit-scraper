"""Tests for data processors."""

import unittest
from unittest.mock import patch
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.processors.post_processor import PostProcessor


class TestPostProcessor(unittest.TestCase):
    """Test cases for PostProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PostProcessor(
            min_score=10,
            max_age_days=30,
            exclude_nsfw=True,
            exclude_deleted=True
        )
        
        # Sample post data
        current_time = datetime.utcnow().timestamp()
        old_time = (datetime.utcnow() - timedelta(days=40)).timestamp()
        
        self.sample_posts = [
            {
                'id': 'post1',
                'title': 'Good Post',
                'author': 'user1',
                'score': 50,
                'created_utc': current_time,
                'is_nsfw': False,
                'selftext': 'This is good content'
            },
            {
                'id': 'post2',
                'title': 'Low Score Post',
                'author': 'user2',
                'score': 5,
                'created_utc': current_time,
                'is_nsfw': False,
                'selftext': 'Low score content'
            },
            {
                'id': 'post3',
                'title': 'NSFW Post',
                'author': 'user3',
                'score': 100,
                'created_utc': current_time,
                'is_nsfw': True,
                'selftext': 'NSFW content'
            },
            {
                'id': 'post4',
                'title': 'Old Post',
                'author': 'user4',
                'score': 75,
                'created_utc': old_time,
                'is_nsfw': False,
                'selftext': 'Old content'
            },
            {
                'id': 'post5',
                'title': 'Deleted Post',
                'author': '[deleted]',
                'score': 25,
                'created_utc': current_time,
                'is_nsfw': False,
                'selftext': '[deleted]'
            }
        ]
    
    def test_filter_posts_score(self):
        """Test filtering posts by minimum score."""
        filtered = self.processor.filter_posts(self.sample_posts)
        
        # Should exclude post2 (score 5 < 10)
        scores = [post['score'] for post in filtered]
        self.assertTrue(all(score >= 10 for score in scores))
        self.assertNotIn(5, scores)
    
    def test_filter_posts_nsfw(self):
        """Test filtering NSFW posts."""
        filtered = self.processor.filter_posts(self.sample_posts)
        
        # Should exclude NSFW posts
        nsfw_flags = [post['is_nsfw'] for post in filtered]
        self.assertTrue(all(not flag for flag in nsfw_flags))
    
    def test_filter_posts_age(self):
        """Test filtering posts by age."""
        filtered = self.processor.filter_posts(self.sample_posts)
        
        # Should exclude old posts
        current_time = datetime.utcnow().timestamp()
        max_age_seconds = 30 * 24 * 3600
        
        for post in filtered:
            age = current_time - post['created_utc']
            self.assertLessEqual(age, max_age_seconds)
    
    def test_filter_posts_deleted(self):
        """Test filtering deleted posts."""
        filtered = self.processor.filter_posts(self.sample_posts)
        
        # Should exclude deleted posts
        authors = [post['author'] for post in filtered]
        self.assertNotIn('[deleted]', authors)
    
    def test_deduplicate_posts(self):
        """Test deduplication of posts."""
        # Create duplicate posts
        duplicate_posts = self.sample_posts + [self.sample_posts[0].copy()]
        
        deduplicated = self.processor.deduplicate_posts(duplicate_posts)
        
        # Should have one less post
        self.assertEqual(len(deduplicated), len(self.sample_posts))
        
        # Check all IDs are unique
        ids = [post['id'] for post in deduplicated]
        self.assertEqual(len(ids), len(set(ids)))
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "  **Bold text**  *italic*  ~~strikethrough~~  ^superscript^  "
        cleaned = self.processor.clean_text(dirty_text)
        
        self.assertEqual(cleaned, "Bold text italic strikethrough superscript")
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        self.assertEqual(self.processor.clean_text(""), "")
        self.assertEqual(self.processor.clean_text(None), "")
    
    def test_extract_urls(self):
        """Test URL extraction from text."""
        text = "Check out https://example.com and http://test.org for more info"
        urls = self.processor.extract_urls(text)
        
        self.assertEqual(len(urls), 2)
        self.assertIn("https://example.com", urls)
        self.assertIn("http://test.org", urls)
    
    def test_extract_urls_empty(self):
        """Test URL extraction from empty text."""
        self.assertEqual(self.processor.extract_urls(""), [])
        self.assertEqual(self.processor.extract_urls(None), [])
    
    def test_categorize_post_question(self):
        """Test categorizing question posts."""
        post = {'title': 'How to learn Python?', 'selftext': '', 'is_self': True}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'question')
    
    def test_categorize_post_discussion(self):
        """Test categorizing discussion posts."""
        post = {'title': 'Discussion about AI', 'selftext': '', 'is_self': True}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'discussion')
    
    def test_categorize_post_tutorial(self):
        """Test categorizing tutorial posts."""
        post = {'title': 'Tutorial: How to build a web app', 'selftext': '', 'is_self': True}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'tutorial')
    
    def test_categorize_post_showcase(self):
        """Test categorizing showcase posts."""
        post = {'title': 'I made a cool app', 'selftext': '', 'is_self': True}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'showcase')
    
    def test_categorize_post_text_default(self):
        """Test categorizing default text posts."""
        post = {'title': 'Random post', 'selftext': '', 'is_self': True}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'text')
    
    def test_categorize_post_link_default(self):
        """Test categorizing default link posts."""
        post = {'title': 'Random link', 'selftext': '', 'is_self': False}
        category = self.processor.categorize_post(post)
        self.assertEqual(category, 'link')
    
    def test_add_derived_fields(self):
        """Test adding derived fields to posts."""
        posts = [
            {
                'title': '  Test Title  ',
                'selftext': '  Test content with https://example.com  ',
                'score': 100,
                'num_comments': 20,
                'created_utc': 1640995200,
                'is_self': True
            }
        ]
        
        enhanced = self.processor.add_derived_fields(posts)
        post = enhanced[0]
        
        # Check cleaned fields
        self.assertEqual(post['title_clean'], 'Test Title')
        self.assertEqual(post['selftext_clean'], 'Test content with https://example.com')
        
        # Check extracted URLs
        self.assertIn('https://example.com', post['extracted_urls'])
        
        # Check category
        self.assertEqual(post['category'], 'text')
        
        # Check engagement ratio
        self.assertEqual(post['engagement_ratio'], 0.2)  # 20/100
        
        # Check time-based fields
        self.assertIn('created_date', post)
        self.assertIn('created_hour', post)
        self.assertIn('created_weekday', post)
    
    def test_processor_with_different_settings(self):
        """Test processor with different filter settings."""
        lenient_processor = PostProcessor(
            min_score=1,
            max_age_days=365,
            exclude_nsfw=False,
            exclude_deleted=False
        )
        
        filtered = lenient_processor.filter_posts(self.sample_posts)
        
        # Should include more posts with lenient settings
        self.assertGreater(len(filtered), 1)
        
        # Should include NSFW posts
        nsfw_posts = [post for post in filtered if post.get('is_nsfw', False)]
        self.assertGreater(len(nsfw_posts), 0)


class TestContentExtractor(unittest.TestCase):
    """Test cases for ContentExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid issues if requests is not available
        try:
            from src.processors.content_extractor import ContentExtractor
            self.extractor = ContentExtractor(timeout=5, max_workers=2)
        except ImportError:
            self.skipTest("ContentExtractor dependencies not available")
    
    def test_has_extractable_link_self_post(self):
        """Test extractable link detection for self posts."""
        post = {'url': 'https://reddit.com/r/test', 'is_self': True}
        self.assertFalse(self.extractor._has_extractable_link(post))
    
    def test_has_extractable_link_reddit_link(self):
        """Test extractable link detection for Reddit links."""
        post = {'url': 'https://reddit.com/r/test/comments/abc', 'is_self': False}
        self.assertFalse(self.extractor._has_extractable_link(post))
    
    def test_has_extractable_link_image(self):
        """Test extractable link detection for image links."""
        post = {'url': 'https://example.com/image.jpg', 'is_self': False}
        self.assertFalse(self.extractor._has_extractable_link(post))
    
    def test_has_extractable_link_valid(self):
        """Test extractable link detection for valid links."""
        post = {'url': 'https://example.com/article', 'is_self': False}
        self.assertTrue(self.extractor._has_extractable_link(post))
    
    @patch('src.processors.content_extractor.requests.get')
    def test_extract_generic_content(self, mock_get):
        """Test generic content extraction."""
        # Mock HTML response
        mock_response = unittest.mock.Mock()
        mock_response.content = b'''
        <html>
            <head>
                <title>Test Article</title>
                <meta name="description" content="Test description">
                <meta name="author" content="Test Author">
            </head>
            <body>
                <article>
                    <p>This is the main content of the article.</p>
                </article>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response
        
        content = self.extractor._extract_generic(mock_response, "https://example.com")
        
        self.assertIsNotNone(content)
        self.assertEqual(content['title'], 'Test Article')
        self.assertEqual(content['description'], 'Test description')
        self.assertEqual(content['author'], 'Test Author')
        self.assertIn('main content', content['content'])


if __name__ == '__main__':
    unittest.main()