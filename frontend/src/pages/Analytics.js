import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Refresh,
  Psychology,
  Whatshot,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';

import { apiService } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
);

const Analytics = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Analysis data
  const [sentimentData, setSentimentData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  
  // Form data
  const [analysisConfig, setAnalysisConfig] = useState({
    subreddit: '',
    days_back: 7,
    min_score: null,
  });

  const runSentimentAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.analyzeSentiment(analysisConfig);
      setSentimentData(data);
      
      if (data.posts_analyzed > 0) {
        setSuccess(`Analyzed sentiment for ${data.posts_analyzed} posts`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [analysisConfig]);

  const runTrendAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.analyzeTrends(analysisConfig);
      setTrendData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [analysisConfig]);

  useEffect(() => {
    // Load initial analytics
    runSentimentAnalysis();
    runTrendAnalysis();
  }, [runSentimentAnalysis, runTrendAnalysis]);

  const handleRunAnalysis = () => {
    if (activeTab === 0) {
      runSentimentAnalysis();
    } else {
      runTrendAnalysis();
    }
  };

  // Chart configurations
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#b0b0b0',
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#b0b0b0' },
        grid: { color: '#404040' },
      },
      y: {
        ticks: { color: '#b0b0b0' },
        grid: { color: '#404040' },
      },
    },
  };

  // Sentiment chart data
  const sentimentChartData = sentimentData?.sentiment_summary ? {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [
      {
        data: [
          sentimentData.sentiment_summary.positive_percentage || 0,
          sentimentData.sentiment_summary.negative_percentage || 0,
          sentimentData.sentiment_summary.neutral_percentage || 0,
        ],
        backgroundColor: ['#4caf50', '#f44336', '#757575'],
        borderWidth: 2,
        borderColor: '#1a1a1a',
      },
    ],
  } : null;

  // Posting trends chart data
  const postingTrendsData = trendData?.posting_trends?.daily_posting_pattern ? {
    labels: Object.keys(trendData.posting_trends.daily_posting_pattern),
    datasets: [
      {
        label: 'Posts per Day',
        data: Object.values(trendData.posting_trends.daily_posting_pattern),
        borderColor: '#4a9eff',
        backgroundColor: 'rgba(74, 158, 255, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  } : null;

  // Engagement trends chart data
  const engagementTrendsData = trendData?.engagement_trends?.hourly_engagement ? {
    labels: Object.keys(trendData.engagement_trends.hourly_engagement).map(h => `${h}:00`),
    datasets: [
      {
        label: 'Average Engagement',
        data: Object.values(trendData.engagement_trends.hourly_engagement),
        backgroundColor: 'rgba(255, 69, 0, 0.6)',
        borderColor: '#ff4500',
        borderWidth: 1,
      },
    ],
  } : null;

  const getSentimentColor = (label) => {
    switch (label) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'default';
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h4" gutterBottom>
            Advanced Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Sentiment analysis, trend prediction, and content insights
          </Typography>
        </motion.div>

        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          onClick={handleRunAnalysis}
          disabled={loading}
          sx={{
            background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
            '&:hover': {
              background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
            },
          }}
        >
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analysis Configuration
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Subreddit (optional)"
                  placeholder="e.g., python"
                  value={analysisConfig.subreddit}
                  onChange={(e) => setAnalysisConfig({ ...analysisConfig, subreddit: e.target.value })}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Days Back</InputLabel>
                  <Select
                    value={analysisConfig.days_back}
                    onChange={(e) => setAnalysisConfig({ ...analysisConfig, days_back: e.target.value })}
                    label="Days Back"
                  >
                    <MenuItem value={1}>1 Day</MenuItem>
                    <MenuItem value={3}>3 Days</MenuItem>
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={14}>14 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Min Score (optional)"
                  type="number"
                  value={analysisConfig.min_score || ''}
                  onChange={(e) => setAnalysisConfig({ 
                    ...analysisConfig, 
                    min_score: e.target.value ? parseInt(e.target.value) : null 
                  })}
                  size="small"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              sx={{
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 500,
                },
              }}
            >
              <Tab
                icon={<Psychology />}
                label="Sentiment Analysis"
                iconPosition="start"
              />
              <Tab
                icon={<Whatshot />}
                label="Trend Analysis"
                iconPosition="start"
              />
            </Tabs>
          </Box>

          {/* Sentiment Analysis Tab */}
          <TabPanel value={activeTab} index={0}>
            {sentimentData ? (
              <Grid container spacing={3}>
                {/* Sentiment Overview */}
                <Grid item xs={12} md={4}>
                  <Card
                    sx={{
                      background: 'linear-gradient(135deg, #4caf5015 0%, #4caf5005 100%)',
                      border: '1px solid #4caf5030',
                    }}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Sentiment Overview
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="h3" color="primary">
                          {sentimentData.sentiment_summary?.average_sentiment?.toFixed(2) || '0.00'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Average Sentiment Score
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">Positive:</Typography>
                          <Typography variant="body2" color="success.main">
                            {sentimentData.sentiment_summary?.positive_percentage?.toFixed(1) || 0}%
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">Negative:</Typography>
                          <Typography variant="body2" color="error.main">
                            {sentimentData.sentiment_summary?.negative_percentage?.toFixed(1) || 0}%
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">Neutral:</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {sentimentData.sentiment_summary?.neutral_percentage?.toFixed(1) || 0}%
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Sentiment Distribution Chart */}
                <Grid item xs={12} md={8}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Sentiment Distribution
                      </Typography>
                      <Box sx={{ height: 300 }}>
                        {sentimentChartData ? (
                          <Pie data={sentimentChartData} options={chartOptions} />
                        ) : (
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              height: '100%',
                              color: 'text.secondary',
                            }}
                          >
                            No sentiment data available
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Subreddit Sentiment Breakdown */}
                {sentimentData.sentiment_summary?.subreddit_sentiment && (
                  <Grid item xs={12}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Sentiment by Subreddit
                        </Typography>
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Subreddit</TableCell>
                                <TableCell align="right">Posts</TableCell>
                                <TableCell align="right">Avg Sentiment</TableCell>
                                <TableCell align="right">Sentiment Range</TableCell>
                                <TableCell align="center">Overall Mood</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.entries(sentimentData.sentiment_summary.subreddit_sentiment).map(([subreddit, data]) => (
                                <TableRow key={subreddit}>
                                  <TableCell>r/{subreddit}</TableCell>
                                  <TableCell align="right">{data.post_count}</TableCell>
                                  <TableCell align="right">{data.average_sentiment.toFixed(3)}</TableCell>
                                  <TableCell align="right">{data.sentiment_range.toFixed(3)}</TableCell>
                                  <TableCell align="center">
                                    <Chip
                                      label={data.average_sentiment > 0.05 ? 'Positive' : data.average_sentiment < -0.05 ? 'Negative' : 'Neutral'}
                                      color={getSentimentColor(data.average_sentiment > 0.05 ? 'positive' : data.average_sentiment < -0.05 ? 'negative' : 'neutral')}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            ) : (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  py: 8,
                  color: 'text.secondary',
                }}
              >
                <Psychology sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  No sentiment analysis data
                </Typography>
                <Typography variant="body2">
                  Run sentiment analysis to see insights here
                </Typography>
              </Box>
            )}
          </TabPanel>

          {/* Trend Analysis Tab */}
          <TabPanel value={activeTab} index={1}>
            {trendData ? (
              <Grid container spacing={3}>
                {/* Posting Trends */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Daily Posting Trends
                      </Typography>
                      <Box sx={{ height: 300 }}>
                        {postingTrendsData ? (
                          <Line data={postingTrendsData} options={chartOptions} />
                        ) : (
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              height: '100%',
                              color: 'text.secondary',
                            }}
                          >
                            No posting trend data available
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Engagement by Hour */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Engagement by Hour
                      </Typography>
                      <Box sx={{ height: 300 }}>
                        {engagementTrendsData ? (
                          <Bar data={engagementTrendsData} options={chartOptions} />
                        ) : (
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              height: '100%',
                              color: 'text.secondary',
                            }}
                          >
                            No engagement data available
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Trending Subreddits */}
                {trendData.subreddit_trends?.trending_subreddits && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Trending Subreddits
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          {trendData.subreddit_trends.trending_subreddits.slice(0, 5).map((subreddit, index) => (
                            <Box
                              key={subreddit.subreddit}
                              sx={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                p: 2,
                                border: '1px solid #404040',
                                borderRadius: 2,
                                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                              }}
                            >
                              <Box>
                                <Typography variant="subtitle1">
                                  #{index + 1} r/{subreddit.subreddit}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {subreddit.post_count} posts | Avg engagement: {Math.round(subreddit.average_engagement)}
                                </Typography>
                              </Box>
                              <Box sx={{ textAlign: 'right' }}>
                                <Typography variant="h6" color="primary">
                                  {Math.round(subreddit.trending_score)}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  Trending Score
                                </Typography>
                              </Box>
                            </Box>
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* Viral Predictions */}
                {trendData.viral_predictions && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          <Whatshot sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Viral Potential Predictions
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {trendData.viral_predictions.slice(0, 5).map((post, index) => (
                            <Box
                              key={post.id}
                              sx={{
                                p: 2,
                                border: '1px solid #404040',
                                borderRadius: 2,
                                backgroundColor: 'rgba(255, 69, 0, 0.05)',
                              }}
                            >
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="subtitle2" noWrap sx={{ maxWidth: '70%' }}>
                                  {post.title}
                                </Typography>
                                <Chip
                                  label={`${Math.round(post.viral_potential)}%`}
                                  size="small"
                                  color="secondary"
                                  variant="outlined"
                                />
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                r/{post.subreddit} | Score: {post.score} | Comments: {post.num_comments}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            ) : (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  py: 8,
                  color: 'text.secondary',
                }}
              >
                <Whatshot sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  No trend analysis data
                </Typography>
                <Typography variant="body2">
                  Run trend analysis to see insights here
                </Typography>
              </Box>
            )}
          </TabPanel>
        </Card>
      </motion.div>
    </Box>
  );
};

export default Analytics;