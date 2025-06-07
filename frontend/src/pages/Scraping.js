import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  FormControlLabel,
  Switch,
  Chip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  CloudDownload,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import { websocketService } from '../services/websocketService';

const Scraping = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSessions, setActiveSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    subreddits: ['python', 'datascience'],
    posts_per_subreddit: 100,
    sort_type: 'hot',
    time_filter: 'all',
    include_users: false,
    extract_content: false,
    parallel: true,
    max_workers: 5,
  });

  const fetchSessions = useCallback(async () => {
    try {
      const data = await apiService.getAllSessions();
      setSessions(data);
      setActiveSessions(data.filter(s => s.status === 'running'));
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'session_started':
        setSuccess(`Scraping session started for: ${data.subreddits.join(', ')}`);
        fetchSessions();
        break;
      case 'session_completed':
        setSuccess(`Scraping session completed! Scraped ${data.posts_scraped} posts`);
        fetchSessions();
        break;
      case 'session_failed':
        setError(`Scraping session failed: ${data.error}`);
        fetchSessions();
        break;
      case 'status_update':
        setActiveSessions(data.sessions || []);
        break;
      default:
        break;
    }
  }, [fetchSessions]);

  useEffect(() => {
    fetchSessions();
    
    // Subscribe to WebSocket updates
    const unsubscribe = websocketService.subscribe('*', handleWebSocketMessage);
    
    return () => {
      unsubscribe();
    };
  }, [fetchSessions, handleWebSocketMessage]);

  const handleStartScraping = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const config = {
        ...formData,
        subreddits: formData.subreddits.filter(s => s.trim()),
      };
      
      await apiService.startScraping(config);
      setDialogOpen(false);
      setSuccess('Scraping session started successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStopScraping = async (sessionId) => {
    try {
      await apiService.stopScraping(sessionId);
      setSuccess('Stop request sent');
      fetchSessions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubredditChange = (index, value) => {
    const newSubreddits = [...formData.subreddits];
    newSubreddits[index] = value;
    setFormData({ ...formData, subreddits: newSubreddits });
  };

  const addSubreddit = () => {
    setFormData({
      ...formData,
      subreddits: [...formData.subreddits, ''],
    });
  };

  const removeSubreddit = (index) => {
    const newSubreddits = formData.subreddits.filter((_, i) => i !== index);
    setFormData({ ...formData, subreddits: newSubreddits });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'stopping':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
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
            Scraping Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Start, monitor, and manage your Reddit scraping sessions
          </Typography>
        </motion.div>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchSessions}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => setDialogOpen(true)}
            sx={{
              background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
              '&:hover': {
                background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
              },
            }}
          >
            Start New Session
          </Button>
        </Box>
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

      {/* Active Sessions */}
      {activeSessions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Sessions ({activeSessions.length})
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
                            Session {session.session_id?.slice(0, 8)}...
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip
                              label={session.status}
                              size="small"
                              color={getStatusColor(session.status)}
                              variant="outlined"
                            />
                            <Tooltip title="Stop session">
                              <IconButton
                                size="small"
                                onClick={() => handleStopScraping(session.session_id)}
                                sx={{ color: 'error.main' }}
                              >
                                <Stop />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Message: {session.message || 'Running...'}
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Posts: {session.posts_scraped || 0} | Users: {session.users_scraped || 0}
                        </Typography>
                        
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Progress: {Math.round(session.progress || 0)}%
                          </Typography>
                        </Box>
                        
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

      {/* Session History */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Session History
            </Typography>
            
            {sessions.length === 0 ? (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  py: 4,
                  color: 'text.secondary',
                }}
              >
                <CloudDownload sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  No scraping sessions yet
                </Typography>
                <Typography variant="body2">
                  Start your first scraping session to see it here
                </Typography>
              </Box>
            ) : (
              <List>
                {sessions.slice(0, 10).map((session) => (
                  <ListItem
                    key={session.session_id}
                    sx={{
                      border: '1px solid #404040',
                      borderRadius: 2,
                      mb: 1,
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Typography variant="subtitle1">
                            Session {session.session_id?.slice(0, 8)}...
                          </Typography>
                          <Chip
                            label={session.status}
                            size="small"
                            color={getStatusColor(session.status)}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Subreddits: {parseSubreddits(session.subreddits || '[]').join(', ')}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Posts: {session.posts_count || 0} | Users: {session.users_count || 0}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Started: {formatDate(session.start_time)}
                            {session.end_time && ` | Ended: ${formatDate(session.end_time)}`}
                          </Typography>
                          {session.error_message && (
                            <Typography variant="body2" color="error.main">
                              Error: {session.error_message}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="View details">
                        <IconButton edge="end">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* New Session Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
            border: '1px solid #404040',
          },
        }}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Settings />
            Configure New Scraping Session
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Subreddits */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Subreddits to Scrape
              </Typography>
              {formData.subreddits.map((subreddit, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Enter subreddit name (without r/)"
                    value={subreddit}
                    onChange={(e) => handleSubredditChange(index, e.target.value)}
                  />
                  {formData.subreddits.length > 1 && (
                    <IconButton
                      onClick={() => removeSubreddit(index)}
                      color="error"
                      size="small"
                    >
                      <Delete />
                    </IconButton>
                  )}
                </Box>
              ))}
              <Button
                variant="outlined"
                size="small"
                onClick={addSubreddit}
                sx={{ mt: 1 }}
              >
                Add Subreddit
              </Button>
            </Grid>

            {/* Posts per subreddit */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" gutterBottom>
                Posts per Subreddit: {formData.posts_per_subreddit}
              </Typography>
              <Slider
                value={formData.posts_per_subreddit}
                onChange={(e, value) => setFormData({ ...formData, posts_per_subreddit: value })}
                min={10}
                max={1000}
                step={10}
                marks={[
                  { value: 10, label: '10' },
                  { value: 100, label: '100' },
                  { value: 500, label: '500' },
                  { value: 1000, label: '1000' },
                ]}
              />
            </Grid>

            {/* Sort type */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort Type</InputLabel>
                <Select
                  value={formData.sort_type}
                  onChange={(e) => setFormData({ ...formData, sort_type: e.target.value })}
                  label="Sort Type"
                >
                  <MenuItem value="hot">Hot</MenuItem>
                  <MenuItem value="new">New</MenuItem>
                  <MenuItem value="top">Top</MenuItem>
                  <MenuItem value="rising">Rising</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Time filter */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Time Filter</InputLabel>
                <Select
                  value={formData.time_filter}
                  onChange={(e) => setFormData({ ...formData, time_filter: e.target.value })}
                  label="Time Filter"
                  disabled={formData.sort_type !== 'top'}
                >
                  <MenuItem value="hour">Hour</MenuItem>
                  <MenuItem value="day">Day</MenuItem>
                  <MenuItem value="week">Week</MenuItem>
                  <MenuItem value="month">Month</MenuItem>
                  <MenuItem value="year">Year</MenuItem>
                  <MenuItem value="all">All Time</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Max workers */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" gutterBottom>
                Max Workers: {formData.max_workers}
              </Typography>
              <Slider
                value={formData.max_workers}
                onChange={(e, value) => setFormData({ ...formData, max_workers: value })}
                min={1}
                max={10}
                step={1}
                marks={[
                  { value: 1, label: '1' },
                  { value: 5, label: '5' },
                  { value: 10, label: '10' },
                ]}
                disabled={!formData.parallel}
              />
            </Grid>

            {/* Options */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Options
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.parallel}
                      onChange={(e) => setFormData({ ...formData, parallel: e.target.checked })}
                    />
                  }
                  label="Use parallel processing"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.include_users}
                      onChange={(e) => setFormData({ ...formData, include_users: e.target.checked })}
                    />
                  }
                  label="Include user profiles"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.extract_content}
                      onChange={(e) => setFormData({ ...formData, extract_content: e.target.checked })}
                    />
                  }
                  label="Extract content from external links"
                />
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleStartScraping}
            disabled={loading || formData.subreddits.filter(s => s.trim()).length === 0}
            startIcon={<PlayArrow />}
            sx={{
              background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
              '&:hover': {
                background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
              },
            }}
          >
            {loading ? 'Starting...' : 'Start Scraping'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Scraping;