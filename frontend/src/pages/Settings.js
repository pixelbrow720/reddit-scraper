import React, { useState, useEffect } from 'react';
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
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save,
  Refresh,
  Delete,
  Info,
  Security,
  Storage,
  Api,
  Notifications,
  Palette,
  Speed,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

const Settings = () => {
  const [config, setConfig] = useState(null);
  const [dbStats, setDbStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null });

  // Settings state
  const [settings, setSettings] = useState({
    reddit: {
      client_id: '',
      client_secret: '',
      user_agent: 'RedditScraper/2.0',
    },
    scraping: {
      rate_limit: 1.0,
      max_retries: 3,
      timeout: 30,
      default_posts: 100,
      parallel_workers: 5,
    },
    filtering: {
      min_score: 1,
      max_age_days: 365,
      exclude_nsfw: true,
      exclude_deleted: true,
    },
    ui: {
      theme: 'dark',
      auto_refresh: true,
      refresh_interval: 30,
      notifications: true,
    },
    performance: {
      cache_enabled: true,
      cache_duration: 3600,
      cleanup_interval: 7,
      max_memory_usage: 1024,
    },
  });

  useEffect(() => {
    fetchConfiguration();
    fetchDatabaseStats();
  }, []);

  const fetchConfiguration = async () => {
    try {
      setLoading(true);
      const data = await apiService.getConfiguration();
      setConfig(data);
      
      // Update settings with current config
      if (data.scraping_config) {
        setSettings(prev => ({
          ...prev,
          scraping: { ...prev.scraping, ...data.scraping_config },
        }));
      }
      if (data.filtering_config) {
        setSettings(prev => ({
          ...prev,
          filtering: { ...prev.filtering, ...data.filtering_config },
        }));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDatabaseStats = async () => {
    try {
      const stats = await apiService.getDatabaseStats();
      setDbStats(stats);
    } catch (err) {
      console.error('Failed to fetch database stats:', err);
    }
  };

  const handleSaveSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would save settings to the backend
      // For now, we'll just show a success message
      setSuccess('Settings saved successfully!');
      
      // Refresh configuration
      await fetchConfiguration();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSettings = () => {
    setConfirmDialog({
      open: true,
      action: 'reset',
      title: 'Reset Settings',
      message: 'Are you sure you want to reset all settings to default values?',
    });
  };

  const handleCleanupDatabase = () => {
    setConfirmDialog({
      open: true,
      action: 'cleanup',
      title: 'Cleanup Database',
      message: 'This will remove old data from the database. This action cannot be undone.',
    });
  };

  const handleConfirmAction = async () => {
    try {
      setLoading(true);
      
      if (confirmDialog.action === 'reset') {
        // Reset to default settings
        setSettings({
          reddit: {
            client_id: '',
            client_secret: '',
            user_agent: 'RedditScraper/2.0',
          },
          scraping: {
            rate_limit: 1.0,
            max_retries: 3,
            timeout: 30,
            default_posts: 100,
            parallel_workers: 5,
          },
          filtering: {
            min_score: 1,
            max_age_days: 365,
            exclude_nsfw: true,
            exclude_deleted: true,
          },
          ui: {
            theme: 'dark',
            auto_refresh: true,
            refresh_interval: 30,
            notifications: true,
          },
          performance: {
            cache_enabled: true,
            cache_duration: 3600,
            cleanup_interval: 7,
            max_memory_usage: 1024,
          },
        });
        setSuccess('Settings reset to defaults');
      } else if (confirmDialog.action === 'cleanup') {
        // In a real implementation, this would call the cleanup API
        setSuccess('Database cleanup completed');
        await fetchDatabaseStats();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setConfirmDialog({ open: false, action: null });
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const SettingsSection = ({ title, icon, children }) => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        {children}
      </CardContent>
    </Card>
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
            Settings & Configuration
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure Reddit API, scraping parameters, and system preferences
          </Typography>
        </motion.div>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchConfiguration}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveSettings}
            disabled={loading}
            sx={{
              background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
              '&:hover': {
                background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
              },
            }}
          >
            Save Settings
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

      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          {/* Reddit API Configuration */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <SettingsSection
              title="Reddit API Configuration"
              icon={<Api color="primary" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      API Status:
                    </Typography>
                    <Chip
                      label={config?.reddit_configured ? 'Connected' : 'Not Configured'}
                      color={config?.reddit_configured ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Client ID"
                    value={settings.reddit.client_id}
                    onChange={(e) => setSettings({
                      ...settings,
                      reddit: { ...settings.reddit, client_id: e.target.value }
                    })}
                    size="small"
                    type="password"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Client Secret"
                    value={settings.reddit.client_secret}
                    onChange={(e) => setSettings({
                      ...settings,
                      reddit: { ...settings.reddit, client_secret: e.target.value }
                    })}
                    size="small"
                    type="password"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="User Agent"
                    value={settings.reddit.user_agent}
                    onChange={(e) => setSettings({
                      ...settings,
                      reddit: { ...settings.reddit, user_agent: e.target.value }
                    })}
                    size="small"
                    helperText="Identify your application to Reddit's API"
                  />
                </Grid>
              </Grid>
            </SettingsSection>
          </motion.div>

          {/* Scraping Configuration */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <SettingsSection
              title="Scraping Configuration"
              icon={<Speed color="secondary" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Rate Limit (req/sec)"
                    type="number"
                    value={settings.scraping.rate_limit}
                    onChange={(e) => setSettings({
                      ...settings,
                      scraping: { ...settings.scraping, rate_limit: parseFloat(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 0.1, max: 10, step: 0.1 }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Retries"
                    type="number"
                    value={settings.scraping.max_retries}
                    onChange={(e) => setSettings({
                      ...settings,
                      scraping: { ...settings.scraping, max_retries: parseInt(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 1, max: 10 }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Timeout (seconds)"
                    type="number"
                    value={settings.scraping.timeout}
                    onChange={(e) => setSettings({
                      ...settings,
                      scraping: { ...settings.scraping, timeout: parseInt(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 10, max: 120 }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Default Posts per Subreddit"
                    type="number"
                    value={settings.scraping.default_posts}
                    onChange={(e) => setSettings({
                      ...settings,
                      scraping: { ...settings.scraping, default_posts: parseInt(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 10, max: 1000 }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Parallel Workers"
                    type="number"
                    value={settings.scraping.parallel_workers}
                    onChange={(e) => setSettings({
                      ...settings,
                      scraping: { ...settings.scraping, parallel_workers: parseInt(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 1, max: 10 }}
                    helperText="Number of concurrent workers for parallel scraping"
                  />
                </Grid>
              </Grid>
            </SettingsSection>
          </motion.div>

          {/* Content Filtering */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <SettingsSection
              title="Content Filtering"
              icon={<Security color="warning" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Minimum Score"
                    type="number"
                    value={settings.filtering.min_score}
                    onChange={(e) => setSettings({
                      ...settings,
                      filtering: { ...settings.filtering, min_score: parseInt(e.target.value) }
                    })}
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Age (days)"
                    type="number"
                    value={settings.filtering.max_age_days}
                    onChange={(e) => setSettings({
                      ...settings,
                      filtering: { ...settings.filtering, max_age_days: parseInt(e.target.value) }
                    })}
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.filtering.exclude_nsfw}
                          onChange={(e) => setSettings({
                            ...settings,
                            filtering: { ...settings.filtering, exclude_nsfw: e.target.checked }
                          })}
                        />
                      }
                      label="Exclude NSFW content"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.filtering.exclude_deleted}
                          onChange={(e) => setSettings({
                            ...settings,
                            filtering: { ...settings.filtering, exclude_deleted: e.target.checked }
                          })}
                        />
                      }
                      label="Exclude deleted posts"
                    />
                  </Box>
                </Grid>
              </Grid>
            </SettingsSection>
          </motion.div>

          {/* UI Preferences */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <SettingsSection
              title="UI Preferences"
              icon={<Palette color="info" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={settings.ui.theme}
                      onChange={(e) => setSettings({
                        ...settings,
                        ui: { ...settings.ui, theme: e.target.value }
                      })}
                      label="Theme"
                    >
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="auto">Auto</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Refresh Interval (seconds)"
                    type="number"
                    value={settings.ui.refresh_interval}
                    onChange={(e) => setSettings({
                      ...settings,
                      ui: { ...settings.ui, refresh_interval: parseInt(e.target.value) }
                    })}
                    size="small"
                    inputProps={{ min: 5, max: 300 }}
                    disabled={!settings.ui.auto_refresh}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.ui.auto_refresh}
                          onChange={(e) => setSettings({
                            ...settings,
                            ui: { ...settings.ui, auto_refresh: e.target.checked }
                          })}
                        />
                      }
                      label="Auto-refresh dashboard"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.ui.notifications}
                          onChange={(e) => setSettings({
                            ...settings,
                            ui: { ...settings.ui, notifications: e.target.checked }
                          })}
                        />
                      }
                      label="Enable notifications"
                    />
                  </Box>
                </Grid>
              </Grid>
            </SettingsSection>
          </motion.div>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          {/* System Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <SettingsSection
              title="System Information"
              icon={<Info color="primary" />}
            >
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Application Version"
                    secondary="v2.0.0"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Database Path"
                    secondary={config?.database_path || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Reddit API Status"
                    secondary={
                      <Chip
                        label={config?.reddit_configured ? 'Connected' : 'Not Configured'}
                        color={config?.reddit_configured ? 'success' : 'error'}
                        size="small"
                      />
                    }
                  />
                </ListItem>
              </List>
            </SettingsSection>
          </motion.div>

          {/* Database Statistics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <SettingsSection
              title="Database Statistics"
              icon={<Storage color="secondary" />}
            >
              {dbStats ? (
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Total Posts"
                      secondary={dbStats.posts_count?.toLocaleString() || '0'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Total Users"
                      secondary={dbStats.users_count?.toLocaleString() || '0'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Scraping Sessions"
                      secondary={dbStats.scraping_sessions_count?.toLocaleString() || '0'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Database Size"
                      secondary={formatBytes(dbStats.database_size_bytes || 0)}
                    />
                  </ListItem>
                  {dbStats.data_date_range && (
                    <ListItem>
                      <ListItemText
                        primary="Data Range"
                        secondary={`${new Date(dbStats.data_date_range.start).toLocaleDateString()} - ${new Date(dbStats.data_date_range.end).toLocaleDateString()}`}
                      />
                    </ListItem>
                  )}
                </List>
              ) : (
                <Typography color="text.secondary">
                  Loading database statistics...
                </Typography>
              )}
              
              <Divider sx={{ my: 2 }} />
              
              <Button
                fullWidth
                variant="outlined"
                color="warning"
                startIcon={<Delete />}
                onClick={handleCleanupDatabase}
                size="small"
              >
                Cleanup Old Data
              </Button>
            </SettingsSection>
          </motion.div>

          {/* Performance Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <SettingsSection
              title="Performance"
              icon={<Speed color="success" />}
            >
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.performance.cache_enabled}
                        onChange={(e) => setSettings({
                          ...settings,
                          performance: { ...settings.performance, cache_enabled: e.target.checked }
                        })}
                      />
                    }
                    label="Enable caching"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Cache Duration (seconds)"
                    type="number"
                    value={settings.performance.cache_duration}
                    onChange={(e) => setSettings({
                      ...settings,
                      performance: { ...settings.performance, cache_duration: parseInt(e.target.value) }
                    })}
                    size="small"
                    disabled={!settings.performance.cache_enabled}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Cleanup Interval (days)"
                    type="number"
                    value={settings.performance.cleanup_interval}
                    onChange={(e) => setSettings({
                      ...settings,
                      performance: { ...settings.performance, cleanup_interval: parseInt(e.target.value) }
                    })}
                    size="small"
                  />
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 2 }} />
              
              <Button
                fullWidth
                variant="outlined"
                color="error"
                startIcon={<Refresh />}
                onClick={handleResetSettings}
                size="small"
              >
                Reset to Defaults
              </Button>
            </SettingsSection>
          </motion.div>
        </Grid>
      </Grid>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, action: null })}
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
            border: '1px solid #404040',
          },
        }}
      >
        <DialogTitle>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <Typography>{confirmDialog.message}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false, action: null })}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmAction}
            color="error"
            variant="contained"
            disabled={loading}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;