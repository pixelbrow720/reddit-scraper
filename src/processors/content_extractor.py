"""Content extraction from external links."""

import requests
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extract content from external URLs."""
    
    def __init__(self, timeout: int = 10, max_workers: int = 5, rate_limit: float = 1.0):
        """Initialize content extractor.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent workers
            rate_limit: Requests per second limit
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Common headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Domain-specific extractors
        self.domain_extractors = {
            'youtube.com': self._extract_youtube,
            'youtu.be': self._extract_youtube,
            'github.com': self._extract_github,
            'medium.com': self._extract_medium,
            'stackoverflow.com': self._extract_stackoverflow,
            'news.ycombinator.com': self._extract_hackernews,
            'twitter.com': self._extract_twitter,
            'x.com': self._extract_twitter
        }
        
        logger.info(f"Content extractor initialized with {max_workers} workers")
    
    def extract_content_from_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract content from external links in posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Posts with extracted content
        """
        posts_with_links = [post for post in posts if self._has_extractable_link(post)]
        
        if not posts_with_links:
            logger.info("No posts with extractable links found")
            return posts
        
        logger.info(f"Extracting content from {len(posts_with_links)} posts with external links")
        
        # Extract content using thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_post = {
                executor.submit(self._extract_post_content, post): post 
                for post in posts_with_links
            }
            
            for future in as_completed(future_to_post):
                post = future_to_post[future]
                try:
                    extracted_content = future.result()
                    if extracted_content:
                        post['extracted_content'] = extracted_content
                        logger.debug(f"Extracted content from {post.get('url', 'unknown URL')}")
                except Exception as e:
                    logger.warning(f"Failed to extract content from {post.get('url', 'unknown URL')}: {e}")
        
        return posts
    
    def _has_extractable_link(self, post: Dict[str, Any]) -> bool:
        """Check if post has an extractable external link.
        
        Args:
            post: Post dictionary
            
        Returns:
            True if post has extractable link
        """
        url = post.get('url', '')
        if not url or post.get('is_self', False):
            return False
        
        # Skip Reddit internal links
        if 'reddit.com' in url or 'redd.it' in url:
            return False
        
        # Skip direct image/video links
        if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']):
            return False
        
        return True
    
    def _extract_post_content(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract content from a single post's URL.
        
        Args:
            post: Post dictionary
            
        Returns:
            Extracted content dictionary or None
        """
        url = post.get('url', '')
        if not url:
            return None
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        try:
            # Get domain-specific extractor
            domain = urlparse(url).netloc.lower()
            domain = domain.replace('www.', '')
            
            extractor = self.domain_extractors.get(domain, self._extract_generic)
            
            # Make request
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract content
            content = extractor(response, url)
            
            if content:
                content['extraction_timestamp'] = time.time()
                content['source_url'] = url
                content['domain'] = domain
            
            return content
            
        except Exception as e:
            logger.debug(f"Content extraction failed for {url}: {e}")
            return None
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _extract_generic(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Generic content extraction for any website.
        
        Args:
            response: HTTP response
            url: Source URL
            
        Returns:
            Extracted content dictionary
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Try Open Graph title
            if not title:
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    title = og_title.get('content', '').strip()
            
            # Extract description
            description = None
            
            # Try meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Try Open Graph description
            if not description:
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    description = og_desc.get('content', '').strip()
            
            # Extract main content
            content_text = self._extract_main_content(soup)
            
            # Extract author
            author = self._extract_author(soup)
            
            # Extract publish date
            publish_date = self._extract_publish_date(soup)
            
            return {
                'title': title,
                'description': description,
                'content': content_text[:1000] if content_text else None,  # Limit content length
                'author': author,
                'publish_date': publish_date,
                'content_type': 'article',
                'word_count': len(content_text.split()) if content_text else 0
            }
            
        except Exception as e:
            logger.debug(f"Generic extraction failed for {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Main content text
        """
        # Try common content selectors
        content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                text = content_elem.get_text()
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                if len(text) > 100:  # Minimum content length
                    return text
        
        # Fallback: extract from body
        body = soup.find('body')
        if body:
            # Remove unwanted elements
            for elem in body(["script", "style", "nav", "header", "footer", "aside"]):
                elem.decompose()
            
            text = body.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Author name
        """
        # Try various author selectors
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '.post-author',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    return elem.get('content', '').strip()
                else:
                    return elem.get_text().strip()
        
        return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Publish date string
        """
        # Try various date selectors
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'time[datetime]',
            '.publish-date',
            '.post-date'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    return elem.get('content', '').strip()
                elif elem.name == 'time':
                    return elem.get('datetime', elem.get_text()).strip()
                else:
                    return elem.get_text().strip()
        
        return None
    
    def _extract_youtube(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract YouTube video information.
        
        Args:
            response: HTTP response
            url: YouTube URL
            
        Returns:
            YouTube video information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract video title
            title = None
            title_meta = soup.find('meta', property='og:title')
            if title_meta:
                title = title_meta.get('content', '').strip()
            
            # Extract description
            description = None
            desc_meta = soup.find('meta', property='og:description')
            if desc_meta:
                description = desc_meta.get('content', '').strip()
            
            # Extract channel name
            channel = None
            channel_meta = soup.find('meta', attrs={'name': 'author'})
            if channel_meta:
                channel = channel_meta.get('content', '').strip()
            
            # Extract video duration
            duration = None
            duration_meta = soup.find('meta', property='video:duration')
            if duration_meta:
                duration = duration_meta.get('content', '').strip()
            
            return {
                'title': title,
                'description': description,
                'author': channel,
                'duration': duration,
                'content_type': 'video',
                'platform': 'YouTube'
            }
            
        except Exception as e:
            logger.debug(f"YouTube extraction failed for {url}: {e}")
            return None
    
    def _extract_github(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract GitHub repository information.
        
        Args:
            response: HTTP response
            url: GitHub URL
            
        Returns:
            GitHub repository information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract repository name
            title = None
            title_elem = soup.find('strong', {'itemprop': 'name'})
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract description
            description = None
            desc_elem = soup.find('p', {'itemprop': 'about'})
            if desc_elem:
                description = desc_elem.get_text().strip()
            
            # Extract language
            language = None
            lang_elem = soup.find('span', {'itemprop': 'programmingLanguage'})
            if lang_elem:
                language = lang_elem.get_text().strip()
            
            # Extract stars count
            stars = None
            stars_elem = soup.find('span', {'id': 'repo-stars-counter-star'})
            if stars_elem:
                stars = stars_elem.get_text().strip()
            
            return {
                'title': title,
                'description': description,
                'language': language,
                'stars': stars,
                'content_type': 'repository',
                'platform': 'GitHub'
            }
            
        except Exception as e:
            logger.debug(f"GitHub extraction failed for {url}: {e}")
            return None
    
    def _extract_medium(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract Medium article information.
        
        Args:
            response: HTTP response
            url: Medium URL
            
        Returns:
            Medium article information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract author
            author = None
            author_elem = soup.find('a', {'rel': 'author'})
            if author_elem:
                author = author_elem.get_text().strip()
            
            # Extract reading time
            reading_time = None
            time_elem = soup.find('span', string=re.compile(r'\d+ min read'))
            if time_elem:
                reading_time = time_elem.get_text().strip()
            
            # Extract content preview
            content = None
            content_elem = soup.find('section')
            if content_elem:
                content = content_elem.get_text()[:500].strip()
            
            return {
                'title': title,
                'author': author,
                'reading_time': reading_time,
                'content': content,
                'content_type': 'article',
                'platform': 'Medium'
            }
            
        except Exception as e:
            logger.debug(f"Medium extraction failed for {url}: {e}")
            return None
    
    def _extract_stackoverflow(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract Stack Overflow question information.
        
        Args:
            response: HTTP response
            url: Stack Overflow URL
            
        Returns:
            Stack Overflow question information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract question title
            title = None
            title_elem = soup.find('h1', {'itemprop': 'name'})
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract tags
            tags = []
            tag_elems = soup.find_all('a', {'class': 'post-tag'})
            for tag_elem in tag_elems:
                tags.append(tag_elem.get_text().strip())
            
            # Extract vote count
            votes = None
            vote_elem = soup.find('span', {'itemprop': 'upvoteCount'})
            if vote_elem:
                votes = vote_elem.get_text().strip()
            
            # Extract answer count
            answers = None
            answer_elem = soup.find('span', {'itemprop': 'answerCount'})
            if answer_elem:
                answers = answer_elem.get_text().strip()
            
            return {
                'title': title,
                'tags': tags,
                'votes': votes,
                'answers': answers,
                'content_type': 'question',
                'platform': 'Stack Overflow'
            }
            
        except Exception as e:
            logger.debug(f"Stack Overflow extraction failed for {url}: {e}")
            return None
    
    def _extract_hackernews(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract Hacker News story information.
        
        Args:
            response: HTTP response
            url: Hacker News URL
            
        Returns:
            Hacker News story information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract story title
            title = None
            title_elem = soup.find('a', {'class': 'storylink'})
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract points
            points = None
            points_elem = soup.find('span', {'class': 'score'})
            if points_elem:
                points = points_elem.get_text().strip()
            
            # Extract comments count
            comments = None
            comment_elems = soup.find_all('a', string=re.compile(r'\d+ comment'))
            if comment_elems:
                comments = comment_elems[0].get_text().strip()
            
            return {
                'title': title,
                'points': points,
                'comments': comments,
                'content_type': 'story',
                'platform': 'Hacker News'
            }
            
        except Exception as e:
            logger.debug(f"Hacker News extraction failed for {url}: {e}")
            return None
    
    def _extract_twitter(self, response: requests.Response, url: str) -> Optional[Dict[str, Any]]:
        """Extract Twitter/X post information.
        
        Args:
            response: HTTP response
            url: Twitter/X URL
            
        Returns:
            Twitter/X post information
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract tweet text
            content = None
            content_meta = soup.find('meta', property='og:description')
            if content_meta:
                content = content_meta.get('content', '').strip()
            
            # Extract author
            author = None
            author_meta = soup.find('meta', property='og:title')
            if author_meta:
                author_text = author_meta.get('content', '')
                if 'on X:' in author_text:
                    author = author_text.split('on X:')[0].strip()
            
            return {
                'content': content,
                'author': author,
                'content_type': 'tweet',
                'platform': 'Twitter/X'
            }
            
        except Exception as e:
            logger.debug(f"Twitter extraction failed for {url}: {e}")
            return None