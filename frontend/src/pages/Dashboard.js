import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  CloudDownload,
  Refresh,
  People,
  Forum,
  ThumbUp,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Line, Doughnut } from 'react-chartjs-2';
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
} from 'chart.js';

import { apiService } from '../services/api';
import { websocketService } from '../services/websocketService';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [activeSessions, setActiveSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [analyticsData, realtimeAnalytics, sessions] = await Promise.all([
        apiService.getAnalyticsSummary(7),
        apiService.getRealtimeAnalytics(),
        apiService.getAllSessions(),
      ]);

      setAnalytics(analyticsData);
      setRealtimeData(realtimeAnalytics);
      setActiveSessions(sessions.filter(s => s.status === 'running'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'session_started':
      case 'session_completed':
      case 'session_failed':
        fetchDashboardData();
        break;
      case 'status_update':
        setActiveSessions(data.sessions || []);
        break;
      default:
        break;
    }
  }, [fetchDashboardData]);

  useEffect(() => {
    fetchDashboardData();
    
    // Subscribe to WebSocket updates
    const unsubscribe = websocketService.subscribe('*', handleWebSocketMessage);
    
    // Set up periodic refresh
    const interval = setInterval(fetchDashboardData, 60000); // Refresh every minute

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, [fetchDashboardData, handleWebSocketMessage]);

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const parseSubreddits = (subredditsData) => {
    try {
      if (typeof subredditsData === 'string') {
        // Try to parse as JSON first
        try {
          return JSON.parse(subredditsData);
        } catch {
          // If JSON parsing fails, treat as comma-separated string
          return subredditsData.split(',').map(s => s.trim()).filter(s => s);
        }
      }
      if (Array.isArray(subredditsData)) {
        return subredditsData;
      }
      return [];
    } catch {
      return [];
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

  const hourlyData = {
    labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    datasets: [
      {
        label: 'Posts per Hour',
        data: realtimeData?.hourly_distribution 
          ? Array.from({ length: 24 }, (_, i) => realtimeData.hourly_distribution[i] || 0)
          : Array(24).fill(0),
        borderColor: '#4a9eff',
        backgroundColor: 'rgba(74, 158, 255, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const subredditData = {
    labels: realtimeData?.top_subreddits?.map(s => `r/${s.subreddit}`) || [],
    datasets: [
      {
        data: realtimeData?.top_subreddits?.map(s => s.count) || [],
        backgroundColor: [
          '#4a9eff',
          '#ff4500',
          '#4caf50',
          '#ff9800',
          '#9c27b0',
        ],
        borderWidth: 2,
        borderColor: '#1a1a1a',
      },
    ],
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Loading Dashboard...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Typography variant="h4" gutterBottom>
          Dashboard Error
        </Typography>
      </Box>
    );
  }

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
            Dashboard Overview
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time monitoring and analytics for your Reddit scraping operations
          </Typography>
        </motion.div>

        <Tooltip title="Refresh data">
          <IconButton
            onClick={handleRefresh}
            sx={{
              background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
                transform: 'rotate(180deg)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          {
            title: 'Total Posts',
            value: analytics?.total_posts || 0,
            icon: <Forum />,
            color: '#4a9eff',
            trend: '+12%',
            trendUp: true,
          },
          {
            title: 'Unique Authors',
            value: analytics?.unique_authors || 0,
            icon: <People />,
            color: '#4caf50',
            trend: '+8%',
            trendUp: true,
          },
          {
            title: 'Average Score',
            value: Math.round(analytics?.avg_score || 0),
            icon: <ThumbUp />,
            color: '#ff9800',
            trend: '-3%',
            trendUp: false,
          },
          {
            title: 'Active Sessions',
            value: activeSessions.length,
            icon: <CloudDownload />,
            color: '#9c27b0',
            trend: activeSessions.length > 0 ? 'Running' : 'Idle',
            trendUp: activeSessions.length > 0,
          },
        ].map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card
                sx={{
                  height: '100%',
                  background: `linear-gradient(135deg, ${stat.color}15 0%, ${stat.color}05 100%)`,
                  border: `1px solid ${stat.color}30`,
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 2,
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        mr: 2,
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Typography variant="h6" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                  
                  <Typography variant="h3" sx={{ mb: 1, fontWeight: 700 }}>
                    {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {stat.trendUp ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                    <Typography
                      variant="body2"
                      color={stat.trendUp ? 'success.main' : 'error.main'}
                      sx={{ ml: 0.5 }}
                    >
                      {stat.trend}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Hourly Activity Chart */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Posting Activity (24h)
                </Typography>
                <Box sx={{ height: 300 }}>
                  <Line data={hourlyData} options={chartOptions} />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Top Subreddits */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Subreddits
                </Typography>
                <Box sx={{ height: 300 }}>
                  {realtimeData?.top_subreddits?.length > 0 ? (
                    <Doughnut 
                      data={subredditData} 
                      options={{
                        ...chartOptions,
                        plugins: {
                          ...chartOptions.plugins,
                          legend: {
                            position: 'bottom',
                            labels: {
                              color: '#b0b0b0',
                              padding: 20,
                            },
                          },
                        },
                      }} 
                    />
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
                      No data available
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Active Sessions */}
      {activeSessions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Scraping Sessions
              </Typography>
              <Grid container spacing={2}>
                {activeSessions.map((session) => (
                  <Grid item xs={12} md={6} key={session.session_id}>
                    <Card
                      sx={{
                        background: 'linear-gradient(135deg, #4a9eff15 0%, #4a9eff05 100%)',
                        border: '1px solid #4a9eff30',
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Typography variant="subtitle1">
                            Session {session.session_id.slice(0, 8)}...
                          </Typography>
                          <Chip
                            label={session.status}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Subreddits: {parseSubreddits(session.subreddits || '[]').join(', ')}
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Posts: {session.posts_count || 0} | Users: {session.users_count || 0}
                        </Typography>
                        
                        <LinearProgress
                          variant="determinate"
                          value={session.progress || 0}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: '#2d2d2d',
                            '& .MuiLinearProgress-bar': {
                              background: 'linear-gradient(90deg, #4a9eff 0%, #ff4500 100%)',
                            },
                          }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Statistics (Last 7 Days)
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {analytics?.unique_subreddits || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Unique Subreddits
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="secondary">
                    {Math.round(analytics?.total_comments || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Comments
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {Math.round(analytics?.avg_comments || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Comments/Post
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {Math.round(analytics?.max_score || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Highest Score
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default Dashboard;