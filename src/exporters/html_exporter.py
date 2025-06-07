"""HTML export functionality with dark theme and interactive charts."""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import base64
from collections import Counter

logger = logging.getLogger(__name__)


class HTMLExporter:
    """Export data to HTML format with dark theme and interactive charts."""
    
    def __init__(self, output_dir: str = "output/html", dark_theme: bool = True):
        """Initialize HTML exporter.
        
        Args:
            output_dir: Output directory for HTML files
            dark_theme: Whether to use dark theme
        """
        self.output_dir = output_dir
        self.dark_theme = dark_theme
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"HTML exporter initialized with output directory: {output_dir}")
    
    def export_posts_report(self, posts: List[Dict[str, Any]], users: List[Dict[str, Any]] = None,
                           filename: str = None) -> str:
        """Export comprehensive HTML report.
        
        Args:
            posts: List of post dictionaries
            users: List of user profile dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate HTML content
        html_content = self._generate_html_report(posts, users)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Exported HTML report with {len(posts)} posts to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting HTML report: {e}")
            raise
    
    def _generate_html_report(self, posts: List[Dict[str, Any]], 
                             users: List[Dict[str, Any]] = None) -> str:
        """Generate complete HTML report.
        
        Args:
            posts: List of post dictionaries
            users: List of user profile dictionaries
            
        Returns:
            HTML content string
        """
        # Generate statistics
        stats = self._generate_statistics(posts, users)
        
        # Generate charts data
        charts_data = self._prepare_charts_data(posts)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Scraper Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header(stats)}
        {self._generate_summary_section(stats)}
        {self._generate_charts_section(charts_data)}
        {self._generate_top_posts_section(posts)}
        {self._generate_subreddit_breakdown(posts)}
        {self._generate_user_analysis(users) if users else ''}
        {self._generate_footer()}
    </div>
    {self._get_javascript(charts_data)}
</body>
</html>
        """
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        if self.dark_theme:
            return """
    <style>
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3d3d3d;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --accent: #4a9eff;
            --accent-hover: #3a8eef;
            --border: #404040;
            --success: #4caf50;
            --warning: #ff9800;
            --error: #f44336;
            --reddit-orange: #ff4500;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border-radius: 15px;
            border: 1px solid var(--border);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, var(--accent), var(--reddit-orange));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header .subtitle {
            color: var(--text-secondary);
            font-size: 1.1em;
        }
        
        .section {
            margin-bottom: 40px;
            background-color: var(--bg-secondary);
            border-radius: 10px;
            padding: 25px;
            border: 1px solid var(--border);
        }
        
        .section h2 {
            color: var(--accent);
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background-color: var(--bg-tertiary);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid var(--border);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            color: var(--accent);
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background-color: var(--bg-tertiary);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .chart-title {
            text-align: center;
            margin-bottom: 15px;
            color: var(--text-primary);
            font-size: 1.2em;
        }
        
        .post-item {
            background-color: var(--bg-tertiary);
            margin-bottom: 15px;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
            transition: background-color 0.3s ease;
        }
        
        .post-item:hover {
            background-color: var(--bg-primary);
        }
        
        .post-title {
            font-size: 1.1em;
            margin-bottom: 10px;
            color: var(--text-primary);
        }
        
        .post-title a {
            color: var(--accent);
            text-decoration: none;
        }
        
        .post-title a:hover {
            color: var(--accent-hover);
            text-decoration: underline;
        }
        
        .post-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .subreddit-tag {
            background-color: var(--reddit-orange);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .score {
            color: var(--success);
            font-weight: bold;
        }
        
        .comments {
            color: var(--warning);
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .table th,
        .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .table th {
            background-color: var(--bg-tertiary);
            color: var(--accent);
            font-weight: bold;
        }
        
        .table tr:hover {
            background-color: var(--bg-tertiary);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: var(--text-secondary);
            border-top: 1px solid var(--border);
        }
        
        .progress-bar {
            background-color: var(--bg-tertiary);
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-fill {
            height: 8px;
            background: linear-gradient(90deg, var(--accent), var(--reddit-orange));
            transition: width 0.3s ease;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .post-meta {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
            """
        else:
            # Light theme styles
            return """
    <style>
        /* Light theme styles would go here */
        /* Similar structure but with light colors */
    </style>
            """
    
    def _generate_header(self, stats: Dict[str, Any]) -> str:
        """Generate header section."""
        return f"""
        <div class="header">
            <h1>📊 Reddit Scraper Report</h1>
            <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p class="subtitle">Total Posts Analyzed: {stats.get('total_posts', 0):,}</p>
        </div>
        """
    
    def _generate_summary_section(self, stats: Dict[str, Any]) -> str:
        """Generate summary statistics section."""
        return f"""
        <div class="section">
            <h2>📈 Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats.get('total_posts', 0):,}</div>
                    <div class="stat-label">Total Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('avg_score', 0):.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('total_comments', 0):,}</div>
                    <div class="stat-label">Total Comments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('unique_authors', 0):,}</div>
                    <div class="stat-label">Unique Authors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('unique_subreddits', 0)}</div>
                    <div class="stat-label">Subreddits</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('avg_comments', 0):.1f}</div>
                    <div class="stat-label">Avg Comments</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_charts_section(self, charts_data: Dict[str, Any]) -> str:
        """Generate charts section."""
        return f"""
        <div class="section">
            <h2>📊 Data Visualization</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Score Distribution</div>
                    <canvas id="scoreChart" width="400" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Posts by Hour</div>
                    <canvas id="hourChart" width="400" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Subreddit Distribution</div>
                    <canvas id="subredditChart" width="400" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Content Types</div>
                    <canvas id="contentChart" width="400" height="300"></canvas>
                </div>
            </div>
        </div>
        """
    
    def _generate_top_posts_section(self, posts: List[Dict[str, Any]]) -> str:
        """Generate top posts section."""
        # Sort posts by score
        top_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:10]
        
        posts_html = ""
        for i, post in enumerate(top_posts, 1):
            posts_html += f"""
            <div class="post-item">
                <div class="post-title">
                    <strong>#{i}</strong> 
                    <a href="{post.get('permalink', '#')}" target="_blank">
                        {post.get('title', 'No title')[:100]}{'...' if len(post.get('title', '')) > 100 else ''}
                    </a>
                </div>
                <div class="post-meta">
                    <div class="meta-item">
                        <span class="subreddit-tag">r/{post.get('subreddit', 'unknown')}</span>
                    </div>
                    <div class="meta-item">
                        👤 <strong>{post.get('author', 'unknown')}</strong>
                    </div>
                    <div class="meta-item">
                        ⬆️ <span class="score">{post.get('score', 0):,}</span>
                    </div>
                    <div class="meta-item">
                        💬 <span class="comments">{post.get('num_comments', 0):,}</span>
                    </div>
                    <div class="meta-item">
                        🕒 {datetime.fromtimestamp(post.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M')}
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🏆 Top Posts by Score</h2>
            {posts_html}
        </div>
        """
    
    def _generate_subreddit_breakdown(self, posts: List[Dict[str, Any]]) -> str:
        """Generate subreddit breakdown section."""
        # Calculate subreddit statistics
        subreddit_stats = {}
        for post in posts:
            subreddit = post.get('subreddit', 'unknown')
            if subreddit not in subreddit_stats:
                subreddit_stats[subreddit] = {
                    'count': 0,
                    'total_score': 0,
                    'total_comments': 0
                }
            
            subreddit_stats[subreddit]['count'] += 1
            subreddit_stats[subreddit]['total_score'] += post.get('score', 0)
            subreddit_stats[subreddit]['total_comments'] += post.get('num_comments', 0)
        
        # Sort by post count
        sorted_subreddits = sorted(subreddit_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        table_rows = ""
        max_count = max([stats['count'] for stats in subreddit_stats.values()]) if subreddit_stats else 1
        
        for subreddit, stats in sorted_subreddits:
            avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
            avg_comments = stats['total_comments'] / stats['count'] if stats['count'] > 0 else 0
            percentage = (stats['count'] / max_count) * 100
            
            table_rows += f"""
            <tr>
                <td><strong>r/{subreddit}</strong></td>
                <td>{stats['count']:,}</td>
                <td>{avg_score:.1f}</td>
                <td>{avg_comments:.1f}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {percentage}%"></div>
                    </div>
                </td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>📋 Subreddit Breakdown</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Subreddit</th>
                        <th>Posts</th>
                        <th>Avg Score</th>
                        <th>Avg Comments</th>
                        <th>Relative Activity</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_user_analysis(self, users: List[Dict[str, Any]]) -> str:
        """Generate user analysis section."""
        if not users:
            return ""
        
        # Sort users by karma
        top_users = sorted(users, key=lambda x: x.get('comment_karma', 0) + x.get('link_karma', 0), reverse=True)[:10]
        
        users_html = ""
        for i, user in enumerate(top_users, 1):
            total_karma = user.get('comment_karma', 0) + user.get('link_karma', 0)
            users_html += f"""
            <tr>
                <td>#{i}</td>
                <td><strong>u/{user.get('username', 'unknown')}</strong></td>
                <td>{user.get('comment_karma', 0):,}</td>
                <td>{user.get('link_karma', 0):,}</td>
                <td><strong>{total_karma:,}</strong></td>
                <td>{'✓' if user.get('is_verified', False) else '✗'}</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>👥 Top Users by Karma</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Username</th>
                        <th>Comment Karma</th>
                        <th>Link Karma</th>
                        <th>Total Karma</th>
                        <th>Verified</th>
                    </tr>
                </thead>
                <tbody>
                    {users_html}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generate footer section."""
        return f"""
        <div class="footer">
            <p>Generated by Reddit Scraper v1.0.0</p>
            <p>Created by <a href="https://github.com/pixelbrow720" style="color: var(--accent);">@pixelbrow720</a> | 
               <a href="https://twitter.com/BrowPixel" style="color: var(--accent);">@BrowPixel</a></p>
            <p>Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        """
    
    def _generate_statistics(self, posts: List[Dict[str, Any]], 
                           users: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate statistics for the report."""
        if not posts:
            return {}
        
        scores = [post.get('score', 0) for post in posts]
        comments = [post.get('num_comments', 0) for post in posts]
        
        return {
            'total_posts': len(posts),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'total_comments': sum(comments),
            'avg_comments': sum(comments) / len(comments) if comments else 0,
            'unique_authors': len(set(post.get('author', '') for post in posts if post.get('author') != '[deleted]')),
            'unique_subreddits': len(set(post.get('subreddit', '') for post in posts)),
            'total_users': len(users) if users else 0
        }
    
    def _prepare_charts_data(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for charts."""
        # Score distribution
        score_ranges = [0, 10, 50, 100, 500, 1000, float('inf')]
        score_labels = ['0-9', '10-49', '50-99', '100-499', '500-999', '1000+']
        score_counts = [0] * len(score_labels)
        
        for post in posts:
            score = post.get('score', 0)
            for i, range_max in enumerate(score_ranges[1:]):
                if score < range_max:
                    score_counts[i] += 1
                    break
        
        # Posts by hour
        hour_counts = [0] * 24
        for post in posts:
            hour = datetime.fromtimestamp(post.get('created_utc', 0)).hour
            hour_counts[hour] += 1
        
        # Subreddit distribution (top 10)
        subreddit_counter = Counter(post.get('subreddit', 'unknown') for post in posts)
        top_subreddits = subreddit_counter.most_common(10)
        
        # Content types
        content_counter = Counter(post.get('category', 'unknown') for post in posts)
        
        return {
            'score_distribution': {
                'labels': score_labels,
                'data': score_counts
            },
            'hourly_posts': {
                'labels': [f"{i:02d}:00" for i in range(24)],
                'data': hour_counts
            },
            'subreddit_distribution': {
                'labels': [f"r/{sub}" for sub, _ in top_subreddits],
                'data': [count for _, count in top_subreddits]
            },
            'content_types': {
                'labels': list(content_counter.keys()),
                'data': list(content_counter.values())
            }
        }
    
    def _get_javascript(self, charts_data: Dict[str, Any]) -> str:
        """Get JavaScript for interactive charts."""
        return f"""
    <script>
        // Chart.js configuration for dark theme
        Chart.defaults.color = '#b0b0b0';
        Chart.defaults.borderColor = '#404040';
        Chart.defaults.backgroundColor = 'rgba(74, 158, 255, 0.1)';
        
        const chartColors = [
            '#4a9eff', '#ff4500', '#4caf50', '#ff9800', '#9c27b0',
            '#f44336', '#00bcd4', '#ffeb3b', '#795548', '#607d8b'
        ];
        
        // Score Distribution Chart
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        new Chart(scoreCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(charts_data.get('score_distribution', {}).get('labels', []))},
                datasets: [{{
                    label: 'Number of Posts',
                    data: {json.dumps(charts_data.get('score_distribution', {}).get('data', []))},
                    backgroundColor: chartColors[0],
                    borderColor: chartColors[0],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            color: '#404040'
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: '#404040'
                        }}
                    }}
                }}
            }}
        }});
        
        // Hourly Posts Chart
        const hourCtx = document.getElementById('hourChart').getContext('2d');
        new Chart(hourCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(charts_data.get('hourly_posts', {}).get('labels', []))},
                datasets: [{{
                    label: 'Posts per Hour',
                    data: {json.dumps(charts_data.get('hourly_posts', {}).get('data', []))},
                    borderColor: chartColors[1],
                    backgroundColor: 'rgba(255, 69, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            color: '#404040'
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: '#404040'
                        }}
                    }}
                }}
            }}
        }});
        
        // Subreddit Distribution Chart
        const subredditCtx = document.getElementById('subredditChart').getContext('2d');
        new Chart(subredditCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(charts_data.get('subreddit_distribution', {}).get('labels', []))},
                datasets: [{{
                    data: {json.dumps(charts_data.get('subreddit_distribution', {}).get('data', []))},
                    backgroundColor: chartColors.slice(0, {len(charts_data.get('subreddit_distribution', {}).get('labels', []))}),
                    borderWidth: 2,
                    borderColor: '#2d2d2d'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }}
                }}
            }}
        }});
        
        // Content Types Chart
        const contentCtx = document.getElementById('contentChart').getContext('2d');
        new Chart(contentCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps(charts_data.get('content_types', {}).get('labels', []))},
                datasets: [{{
                    data: {json.dumps(charts_data.get('content_types', {}).get('data', []))},
                    backgroundColor: chartColors.slice(0, {len(charts_data.get('content_types', {}).get('labels', []))}),
                    borderWidth: 2,
                    borderColor: '#2d2d2d'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }}
                }}
            }}
        }});
    </script>
        """