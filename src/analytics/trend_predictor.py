"""Trend prediction and analysis for Reddit data."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class TrendPredictor:
    """Advanced trend prediction and analysis for Reddit data."""
    
    def __init__(self, use_ml: bool = True):
        """Initialize trend predictor.
        
        Args:
            use_ml: Whether to use machine learning for predictions
        """
        self.use_ml = use_ml and SKLEARN_AVAILABLE and NUMPY_AVAILABLE
        
        if not self.use_ml:
            logger.info("Using statistical methods for trend prediction (ML libraries not available)")
        else:
            logger.info("Using machine learning for trend prediction")
    
    def analyze_posting_trends(self, posts: List[Dict[str, Any]], 
                             days_back: int = 30) -> Dict[str, Any]:
        """Analyze posting trends over time.
        
        Args:
            posts: List of post dictionaries
            days_back: Number of days to analyze
            
        Returns:
            Posting trend analysis
        """
        if not posts:
            return {}
        
        # Group posts by date
        daily_counts = defaultdict(int)
        hourly_counts = defaultdict(int)
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_timestamp = cutoff_date.timestamp()
        
        for post in posts:
            created_utc = post.get('created_utc', 0)
            if created_utc < cutoff_timestamp:
                continue
            
            post_date = datetime.fromtimestamp(created_utc)
            date_key = post_date.strftime('%Y-%m-%d')
            hour_key = post_date.hour
            
            daily_counts[date_key] += 1
            hourly_counts[hour_key] += 1
        
        # Calculate trends
        analysis = {
            'daily_posting_pattern': dict(daily_counts),
            'hourly_posting_pattern': dict(hourly_counts),
            'total_posts_analyzed': len([p for p in posts if p.get('created_utc', 0) >= cutoff_timestamp]),
            'analysis_period_days': days_back
        }
        
        # Daily trend analysis
        if daily_counts:
            daily_values = list(daily_counts.values())
            analysis['daily_stats'] = {
                'average_posts_per_day': statistics.mean(daily_values),
                'median_posts_per_day': statistics.median(daily_values),
                'max_posts_per_day': max(daily_values),
                'min_posts_per_day': min(daily_values),
                'std_posts_per_day': statistics.stdev(daily_values) if len(daily_values) > 1 else 0
            }
            
            # Trend direction
            if len(daily_values) >= 3:
                trend_direction = self._calculate_trend_direction(daily_values)
                analysis['trend_direction'] = trend_direction
        
        # Peak hours analysis
        if hourly_counts:
            peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            analysis['peak_hours'] = [{'hour': hour, 'posts': count} for hour, count in peak_hours]
        
        # Predict next period
        if self.use_ml and len(daily_counts) >= 7:
            prediction = self._predict_posting_volume(list(daily_counts.values()))
            analysis['prediction'] = prediction
        
        return analysis
    
    def analyze_engagement_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement trends (scores, comments).
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Engagement trend analysis
        """
        if not posts:
            return {}
        
        # Extract engagement metrics
        scores = [post.get('score', 0) for post in posts]
        comments = [post.get('num_comments', 0) for post in posts]
        upvote_ratios = [post.get('upvote_ratio', 0.5) for post in posts if post.get('upvote_ratio')]
        
        analysis = {
            'total_posts': len(posts),
            'score_stats': self._calculate_stats(scores),
            'comment_stats': self._calculate_stats(comments),
            'upvote_ratio_stats': self._calculate_stats(upvote_ratios) if upvote_ratios else {}
        }
        
        # Engagement ratio analysis
        engagement_ratios = []
        for post in posts:
            score = post.get('score', 0)
            comments_count = post.get('num_comments', 0)
            if score > 0:
                ratio = comments_count / score
                engagement_ratios.append(ratio)
        
        if engagement_ratios:
            analysis['engagement_ratio_stats'] = self._calculate_stats(engagement_ratios)
        
        # Time-based engagement analysis
        time_engagement = self._analyze_time_based_engagement(posts)
        analysis.update(time_engagement)
        
        return analysis
    
    def analyze_subreddit_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends across different subreddits.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Subreddit trend analysis
        """
        if not posts:
            return {}
        
        # Group by subreddit
        subreddit_data = defaultdict(list)
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            subreddit_data[subreddit].append(post)
        
        analysis = {
            'total_subreddits': len(subreddit_data),
            'subreddit_breakdown': {}
        }
        
        # Analyze each subreddit
        for subreddit, subreddit_posts in subreddit_data.items():
            scores = [p.get('score', 0) for p in subreddit_posts]
            comments = [p.get('num_comments', 0) for p in subreddit_posts]
            
            subreddit_analysis = {
                'post_count': len(subreddit_posts),
                'average_score': statistics.mean(scores) if scores else 0,
                'average_comments': statistics.mean(comments) if comments else 0,
                'total_engagement': sum(scores) + sum(comments),
                'post_frequency': self._calculate_posting_frequency(subreddit_posts)
            }
            
            # Growth trend for this subreddit
            if len(subreddit_posts) >= 5:
                growth_trend = self._calculate_subreddit_growth(subreddit_posts)
                subreddit_analysis['growth_trend'] = growth_trend
            
            analysis['subreddit_breakdown'][subreddit] = subreddit_analysis
        
        # Identify trending subreddits
        trending = self._identify_trending_subreddits(analysis['subreddit_breakdown'])
        analysis['trending_subreddits'] = trending
        
        return analysis
    
    def predict_viral_potential(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict viral potential of posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Posts with viral potential scores
        """
        analyzed_posts = []
        
        for post in posts:
            viral_score = self._calculate_viral_score(post)
            
            post_copy = post.copy()
            post_copy['viral_potential'] = viral_score
            post_copy['viral_category'] = self._categorize_viral_potential(viral_score)
            
            analyzed_posts.append(post_copy)
        
        # Sort by viral potential
        analyzed_posts.sort(key=lambda x: x['viral_potential'], reverse=True)
        
        logger.info(f"Analyzed viral potential for {len(analyzed_posts)} posts")
        return analyzed_posts
    
    def analyze_content_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content type and topic trends.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Content trend analysis
        """
        if not posts:
            return {}
        
        # Content type analysis
        content_types = Counter(post.get('content_type', 'unknown') for post in posts)
        categories = Counter(post.get('category', 'unknown') for post in posts)
        domains = Counter(post.get('domain', 'unknown') for post in posts)
        
        # Flair analysis
        flairs = Counter(post.get('flair', 'No Flair') for post in posts if post.get('flair'))
        
        # Title keyword analysis
        title_keywords = self._extract_trending_keywords(posts)
        
        analysis = {
            'content_type_distribution': dict(content_types),
            'category_distribution': dict(categories),
            'domain_distribution': dict(domains.most_common(10)),
            'flair_distribution': dict(flairs.most_common(10)),
            'trending_keywords': title_keywords,
            'content_performance': self._analyze_content_performance(posts)
        }
        
        return analysis
    
    def _calculate_trend_direction(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction from time series data.
        
        Args:
            values: List of values over time
            
        Returns:
            Trend direction analysis
        """
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'strength': 0.0}
        
        # Simple linear trend
        n = len(values)
        x = list(range(n))
        
        if self.use_ml:
            # Use linear regression
            X = np.array(x).reshape(-1, 1)
            y = np.array(values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            r2 = r2_score(y, model.predict(X))
            
        else:
            # Calculate slope manually
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(values)
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Calculate R-squared manually
            y_pred = [slope * (xi - x_mean) + y_mean for xi in x]
            ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
            ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine direction
        if slope > 0.1:
            direction = 'increasing'
        elif slope < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(slope),
            'confidence': r2,
            'trend_quality': 'strong' if r2 > 0.7 else 'moderate' if r2 > 0.4 else 'weak'
        }
    
    def _predict_posting_volume(self, daily_values: List[int]) -> Dict[str, Any]:
        """Predict future posting volume.
        
        Args:
            daily_values: Daily posting counts
            
        Returns:
            Prediction results
        """
        if not self.use_ml or len(daily_values) < 7:
            # Simple moving average prediction
            recent_avg = statistics.mean(daily_values[-7:])
            return {
                'method': 'moving_average',
                'predicted_next_day': round(recent_avg),
                'confidence': 0.5
            }
        
        # Prepare data for ML prediction
        X = np.array(range(len(daily_values))).reshape(-1, 1)
        y = np.array(daily_values)
        
        # Try linear regression
        linear_model = LinearRegression()
        linear_model.fit(X, y)
        linear_pred = linear_model.predict([[len(daily_values)]])[0]
        linear_r2 = r2_score(y, linear_model.predict(X))
        
        # Try polynomial regression
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y)
        
        X_next_poly = poly_features.transform([[len(daily_values)]])
        poly_pred = poly_model.predict(X_next_poly)[0]
        poly_r2 = r2_score(y, poly_model.predict(X_poly))
        
        # Choose best model
        if poly_r2 > linear_r2:
            prediction = max(0, poly_pred)  # Ensure non-negative
            confidence = poly_r2
            method = 'polynomial'
        else:
            prediction = max(0, linear_pred)
            confidence = linear_r2
            method = 'linear'
        
        return {
            'method': method,
            'predicted_next_day': round(prediction),
            'confidence': confidence,
            'linear_prediction': round(max(0, linear_pred)),
            'polynomial_prediction': round(max(0, poly_pred))
        }
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Statistics dictionary
        """
        if not values:
            return {}
        
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }
    
    def _analyze_time_based_engagement(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns by time.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Time-based engagement analysis
        """
        hourly_engagement = defaultdict(list)
        daily_engagement = defaultdict(list)
        
        for post in posts:
            created_utc = post.get('created_utc', 0)
            if created_utc == 0:
                continue
            
            post_time = datetime.fromtimestamp(created_utc)
            hour = post_time.hour
            day = post_time.strftime('%A')
            
            engagement = post.get('score', 0) + post.get('num_comments', 0)
            
            hourly_engagement[hour].append(engagement)
            daily_engagement[day].append(engagement)
        
        # Calculate averages
        hourly_avg = {hour: statistics.mean(engagements) 
                     for hour, engagements in hourly_engagement.items()}
        daily_avg = {day: statistics.mean(engagements) 
                    for day, engagements in daily_engagement.items()}
        
        # Find peak times
        peak_hour = max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else (0, 0)
        peak_day = max(daily_avg.items(), key=lambda x: x[1]) if daily_avg else ('Unknown', 0)
        
        return {
            'hourly_engagement': hourly_avg,
            'daily_engagement': daily_avg,
            'peak_hour': {'hour': peak_hour[0], 'avg_engagement': peak_hour[1]},
            'peak_day': {'day': peak_day[0], 'avg_engagement': peak_day[1]}
        }
    
    def _calculate_posting_frequency(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate posting frequency for a set of posts.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Posting frequency analysis
        """
        if len(posts) < 2:
            return {'frequency': 0, 'interval_hours': 0}
        
        timestamps = [post.get('created_utc', 0) for post in posts if post.get('created_utc', 0) > 0]
        timestamps.sort()
        
        if len(timestamps) < 2:
            return {'frequency': 0, 'interval_hours': 0}
        
        # Calculate intervals between posts
        intervals = []
        for i in range(1, len(timestamps)):
            interval_hours = (timestamps[i] - timestamps[i-1]) / 3600
            intervals.append(interval_hours)
        
        avg_interval = statistics.mean(intervals)
        posts_per_day = 24 / avg_interval if avg_interval > 0 else 0
        
        return {
            'posts_per_day': posts_per_day,
            'average_interval_hours': avg_interval,
            'total_timespan_days': (timestamps[-1] - timestamps[0]) / 86400
        }
    
    def _calculate_subreddit_growth(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate growth trend for a subreddit.
        
        Args:
            posts: List of posts from a subreddit
            
        Returns:
            Growth trend analysis
        """
        # Group posts by day
        daily_counts = defaultdict(int)
        for post in posts:
            created_utc = post.get('created_utc', 0)
            if created_utc > 0:
                date_key = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')
                daily_counts[date_key] += 1
        
        if len(daily_counts) < 3:
            return {'growth_rate': 0, 'trend': 'insufficient_data'}
        
        # Calculate growth rate
        values = list(daily_counts.values())
        trend = self._calculate_trend_direction(values)
        
        # Calculate percentage growth
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        growth_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        return {
            'growth_rate_percent': growth_rate,
            'trend_direction': trend['direction'],
            'trend_strength': trend['strength'],
            'confidence': trend['confidence']
        }
    
    def _identify_trending_subreddits(self, subreddit_data: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify trending subreddits.
        
        Args:
            subreddit_data: Subreddit analysis data
            
        Returns:
            List of trending subreddits
        """
        trending = []
        
        for subreddit, data in subreddit_data.items():
            # Calculate trending score
            post_count = data.get('post_count', 0)
            avg_score = data.get('average_score', 0)
            avg_comments = data.get('average_comments', 0)
            growth_trend = data.get('growth_trend', {})
            
            # Trending score formula
            trending_score = (
                post_count * 0.3 +
                avg_score * 0.3 +
                avg_comments * 0.2 +
                growth_trend.get('growth_rate_percent', 0) * 0.2
            )
            
            trending.append({
                'subreddit': subreddit,
                'trending_score': trending_score,
                'post_count': post_count,
                'average_engagement': avg_score + avg_comments,
                'growth_rate': growth_trend.get('growth_rate_percent', 0)
            })
        
        # Sort by trending score
        trending.sort(key=lambda x: x['trending_score'], reverse=True)
        
        return trending[:10]  # Top 10 trending
    
    def _calculate_viral_score(self, post: Dict[str, Any]) -> float:
        """Calculate viral potential score for a post.
        
        Args:
            post: Post dictionary
            
        Returns:
            Viral potential score (0-100)
        """
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        upvote_ratio = post.get('upvote_ratio', 0.5)
        
        # Time factor (newer posts get bonus)
        created_utc = post.get('created_utc', 0)
        if created_utc > 0:
            hours_old = (datetime.now().timestamp() - created_utc) / 3600
            time_factor = max(0, 1 - (hours_old / 24))  # Decay over 24 hours
        else:
            time_factor = 0
        
        # Engagement velocity
        if created_utc > 0 and hours_old > 0:
            engagement_velocity = (score + comments) / hours_old
        else:
            engagement_velocity = 0
        
        # Title factors
        title = post.get('title', '').lower()
        title_viral_indicators = [
            'breaking', 'urgent', 'amazing', 'incredible', 'shocking',
            'you won\'t believe', 'this will', 'everyone needs to',
            'viral', 'trending', 'must see', 'watch this'
        ]
        title_factor = sum(1 for indicator in title_viral_indicators if indicator in title)
        
        # Content type factor
        content_type = post.get('content_type', 'text')
        content_multiplier = {
            'image': 1.2,
            'video': 1.5,
            'link': 1.0,
            'text': 0.8
        }.get(content_type, 1.0)
        
        # Calculate viral score
        viral_score = (
            (score * 0.3) +
            (comments * 0.2) +
            (upvote_ratio * 20) +
            (engagement_velocity * 0.2) +
            (time_factor * 10) +
            (title_factor * 5)
        ) * content_multiplier
        
        # Normalize to 0-100 scale
        viral_score = min(100, max(0, viral_score))
        
        return viral_score
    
    def _categorize_viral_potential(self, score: float) -> str:
        """Categorize viral potential based on score.
        
        Args:
            score: Viral potential score
            
        Returns:
            Viral potential category
        """
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    def _extract_trending_keywords(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending keywords from post titles.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            List of trending keywords with counts
        """
        # Common stop words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their'
        }
        
        word_counts = Counter()
        
        for post in posts:
            title = post.get('title', '').lower()
            # Simple word extraction (could be improved with NLP)
            words = title.split()
            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 2 and word not in stop_words:
                    word_counts[word] += 1
        
        # Return top keywords
        trending_keywords = []
        for word, count in word_counts.most_common(20):
            trending_keywords.append({
                'keyword': word,
                'count': count,
                'frequency': count / len(posts) if posts else 0
            })
        
        return trending_keywords
    
    def _analyze_content_performance(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by content type.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            Content performance analysis
        """
        content_performance = defaultdict(list)
        
        for post in posts:
            content_type = post.get('content_type', 'unknown')
            engagement = post.get('score', 0) + post.get('num_comments', 0)
            content_performance[content_type].append(engagement)
        
        performance_stats = {}
        for content_type, engagements in content_performance.items():
            if engagements:
                performance_stats[content_type] = {
                    'average_engagement': statistics.mean(engagements),
                    'median_engagement': statistics.median(engagements),
                    'max_engagement': max(engagements),
                    'post_count': len(engagements)
                }
        
        return performance_stats