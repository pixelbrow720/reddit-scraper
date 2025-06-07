"""Sentiment analysis for Reddit posts and comments."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime
import statistics

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Advanced sentiment analysis for Reddit content."""
    
    def __init__(self, use_vader: bool = True, use_textblob: bool = True):
        """Initialize sentiment analyzer.
        
        Args:
            use_vader: Whether to use VADER sentiment analyzer
            use_textblob: Whether to use TextBlob sentiment analyzer
        """
        self.use_vader = use_vader and VADER_AVAILABLE
        self.use_textblob = use_textblob and TEXTBLOB_AVAILABLE
        
        if self.use_vader:
            self.vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer initialized")
        
        if not self.use_vader and not self.use_textblob:
            logger.warning("No sentiment analysis libraries available. Install vaderSentiment or textblob.")
        
        # Reddit-specific sentiment patterns
        self.reddit_patterns = {
            'positive': [
                r'\b(amazing|awesome|great|excellent|fantastic|wonderful|love|best)\b',
                r'\b(upvote|upvoted|this\s+is\s+gold|thanks|thank\s+you)\b',
                r'\b(lol|haha|lmao|rofl)\b',
                r':\)|:-\)|:D|:-D|\^_\^'
            ],
            'negative': [
                r'\b(terrible|awful|horrible|worst|hate|sucks|stupid|dumb)\b',
                r'\b(downvote|downvoted|cringe|wtf|fml)\b',
                r':\(|:-\(|:\'\(|D:'
            ],
            'neutral': [
                r'\b(okay|ok|meh|whatever|idk|dunno)\b'
            ]
        }
        
        # Compile regex patterns
        self.compiled_patterns = {}
        for sentiment, patterns in self.reddit_patterns.items():
            self.compiled_patterns[sentiment] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        if not text or not text.strip():
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'label': 'neutral',
                'confidence': 0.0,
                'method': 'none'
            }
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        results = []
        
        # VADER analysis
        if self.use_vader:
            vader_result = self._analyze_with_vader(cleaned_text)
            results.append(vader_result)
        
        # TextBlob analysis
        if self.use_textblob:
            textblob_result = self._analyze_with_textblob(cleaned_text)
            results.append(textblob_result)
        
        # Reddit pattern analysis
        pattern_result = self._analyze_with_patterns(cleaned_text)
        results.append(pattern_result)
        
        # Combine results
        if results:
            combined_result = self._combine_results(results)
        else:
            combined_result = pattern_result
        
        return combined_result
    
    def analyze_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Posts with sentiment analysis added
        """
        analyzed_posts = []
        
        for post in posts:
            # Combine title and selftext for analysis
            text_parts = []
            if post.get('title'):
                text_parts.append(post['title'])
            if post.get('selftext'):
                text_parts.append(post['selftext'])
            
            combined_text = ' '.join(text_parts)
            
            # Analyze sentiment
            sentiment = self.analyze_text(combined_text)
            
            # Add sentiment to post
            post_copy = post.copy()
            post_copy.update({
                'sentiment_score': sentiment['compound'],
                'sentiment_positive': sentiment['positive'],
                'sentiment_negative': sentiment['negative'],
                'sentiment_neutral': sentiment['neutral'],
                'sentiment_label': sentiment['label'],
                'sentiment_confidence': sentiment['confidence'],
                'sentiment_method': sentiment['method']
            })
            
            analyzed_posts.append(post_copy)
        
        logger.info(f"Analyzed sentiment for {len(analyzed_posts)} posts")
        return analyzed_posts
    
    def get_sentiment_summary(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get sentiment summary for posts.
        
        Args:
            posts: List of posts with sentiment analysis
            
        Returns:
            Sentiment summary statistics
        """
        if not posts:
            return {}
        
        # Extract sentiment scores
        scores = [post.get('sentiment_score', 0.0) for post in posts if post.get('sentiment_score') is not None]
        labels = [post.get('sentiment_label', 'neutral') for post in posts if post.get('sentiment_label')]
        
        if not scores:
            return {}
        
        # Calculate statistics
        summary = {
            'total_posts': len(posts),
            'analyzed_posts': len(scores),
            'average_sentiment': statistics.mean(scores),
            'median_sentiment': statistics.median(scores),
            'sentiment_std': statistics.stdev(scores) if len(scores) > 1 else 0.0,
            'min_sentiment': min(scores),
            'max_sentiment': max(scores)
        }
        
        # Label distribution
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        summary['label_distribution'] = label_counts
        
        # Sentiment percentages
        total_analyzed = len(scores)
        if total_analyzed > 0:
            summary['positive_percentage'] = (label_counts.get('positive', 0) / total_analyzed) * 100
            summary['negative_percentage'] = (label_counts.get('negative', 0) / total_analyzed) * 100
            summary['neutral_percentage'] = (label_counts.get('neutral', 0) / total_analyzed) * 100
        
        # Subreddit sentiment breakdown
        subreddit_sentiment = {}
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            sentiment_score = post.get('sentiment_score')
            
            if sentiment_score is not None:
                if subreddit not in subreddit_sentiment:
                    subreddit_sentiment[subreddit] = []
                subreddit_sentiment[subreddit].append(sentiment_score)
        
        # Calculate average sentiment per subreddit
        subreddit_averages = {}
        for subreddit, scores in subreddit_sentiment.items():
            subreddit_averages[subreddit] = {
                'average_sentiment': statistics.mean(scores),
                'post_count': len(scores),
                'sentiment_range': max(scores) - min(scores) if len(scores) > 1 else 0.0
            }
        
        summary['subreddit_sentiment'] = subreddit_averages
        
        return summary
    
    def _clean_text(self, text: str) -> str:
        """Clean text for sentiment analysis.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific formatting
        text = re.sub(r'/u/\w+', '', text)  # Remove username mentions
        text = re.sub(r'/r/\w+', '', text)  # Remove subreddit mentions
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove bold formatting
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Remove italic formatting
        text = re.sub(r'~~(.+?)~~', r'\1', text)  # Remove strikethrough
        text = re.sub(r'\^(.+?)\^', r'\1', text)  # Remove superscript
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            VADER sentiment results
        """
        scores = self.vader_analyzer.polarity_scores(text)
        
        # Determine label based on compound score
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': label,
            'confidence': abs(compound),
            'method': 'vader'
        }
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            TextBlob sentiment results
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Convert to VADER-like format
        if polarity > 0.1:
            label = 'positive'
            positive = (polarity + 1) / 2  # Convert to 0-1 range
            negative = 0.0
            neutral = 1 - positive
        elif polarity < -0.1:
            label = 'negative'
            negative = abs(polarity)
            positive = 0.0
            neutral = 1 - negative
        else:
            label = 'neutral'
            neutral = 1.0
            positive = 0.0
            negative = 0.0
        
        return {
            'compound': polarity,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'label': label,
            'confidence': abs(polarity),
            'method': 'textblob',
            'subjectivity': subjectivity
        }
    
    def _analyze_with_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Reddit-specific patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Pattern-based sentiment results
        """
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Count pattern matches
        for pattern in self.compiled_patterns['positive']:
            positive_count += len(pattern.findall(text))
        
        for pattern in self.compiled_patterns['negative']:
            negative_count += len(pattern.findall(text))
        
        for pattern in self.compiled_patterns['neutral']:
            neutral_count += len(pattern.findall(text))
        
        total_matches = positive_count + negative_count + neutral_count
        
        if total_matches == 0:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'label': 'neutral',
                'confidence': 0.0,
                'method': 'patterns'
            }
        
        # Calculate scores
        positive_score = positive_count / total_matches
        negative_score = negative_count / total_matches
        neutral_score = neutral_count / total_matches
        
        # Calculate compound score
        compound = positive_score - negative_score
        
        # Determine label
        if positive_score > negative_score and positive_score > neutral_score:
            label = 'positive'
        elif negative_score > positive_score and negative_score > neutral_score:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score,
            'label': label,
            'confidence': max(positive_score, negative_score, neutral_score),
            'method': 'patterns'
        }
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple sentiment analysis results.
        
        Args:
            results: List of sentiment analysis results
            
        Returns:
            Combined sentiment result
        """
        if not results:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'label': 'neutral',
                'confidence': 0.0,
                'method': 'none'
            }
        
        if len(results) == 1:
            return results[0]
        
        # Weight different methods
        weights = {
            'vader': 0.5,
            'textblob': 0.3,
            'patterns': 0.2
        }
        
        # Calculate weighted averages
        total_weight = 0
        weighted_compound = 0
        weighted_positive = 0
        weighted_negative = 0
        weighted_neutral = 0
        
        methods_used = []
        
        for result in results:
            method = result.get('method', 'unknown')
            weight = weights.get(method, 0.1)
            
            weighted_compound += result['compound'] * weight
            weighted_positive += result['positive'] * weight
            weighted_negative += result['negative'] * weight
            weighted_neutral += result['neutral'] * weight
            total_weight += weight
            methods_used.append(method)
        
        if total_weight > 0:
            compound = weighted_compound / total_weight
            positive = weighted_positive / total_weight
            negative = weighted_negative / total_weight
            neutral = weighted_neutral / total_weight
        else:
            compound = 0.0
            positive = 0.0
            negative = 0.0
            neutral = 1.0
        
        # Determine final label
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'label': label,
            'confidence': abs(compound),
            'method': '+'.join(methods_used)
        }