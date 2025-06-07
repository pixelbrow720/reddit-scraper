import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Refresh as RefreshIcon,
  CloudDownload as DownloadIcon,
  TrendingUp as TrendingIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiService } from '../../services/api';

const TopBar = ({ onSidebarToggle, connectionStatus }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    // Fetch real-time data periodically
    const fetchRealtimeData = async () => {
      try {
        const data = await apiService.getRealtimeAnalytics();
        setRealtimeData(data);
        setLastUpdate(new Date());
      } catch (error) {
        console.error('Failed to fetch real-time data:', error);
      }
    };

    fetchRealtimeData();
    const interval = setInterval(fetchRealtimeData, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRefresh = async () => {
    try {
      const data = await apiService.getRealtimeAnalytics();
      setRealtimeData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getConnectionStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'success';
      case 'connecting':
      case 'reconnecting':
        return 'warning';
      default:
        return 'error';
    }
  };

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer - 1,
        backdropFilter: 'blur(20px)',
        backgroundColor: 'rgba(26, 26, 26, 0.8)',
      }}
    >
      <Toolbar sx={{ gap: 2 }}>
        {/* Menu Toggle */}
        <IconButton
          edge="start"
          color="inherit"
          onClick={onSidebarToggle}
          sx={{
            '&:hover': {
              backgroundColor: 'rgba(74, 158, 255, 0.1)',
              transform: 'scale(1.1)',
            },
            transition: 'all 0.2s ease',
          }}
        >
          <MenuIcon />
        </IconButton>

        {/* Page Title */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Reddit Scraper Dashboard
        </Typography>

        {/* Real-time Stats */}
        {realtimeData && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Tooltip title="Posts in last 24 hours">
                <Chip
                  icon={<DownloadIcon />}
                  label={`${realtimeData.total_posts_24h || 0} posts`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Tooltip>
              
              <Tooltip title="Average score">
                <Chip
                  icon={<TrendingIcon />}
                  label={`${realtimeData.average_score || 0} avg`}
                  size="small"
                  color="secondary"
                  variant="outlined"
                />
              </Tooltip>
            </Box>
          </motion.div>
        )}

        {/* Connection Status */}
        <Chip
          label={connectionStatus}
          size="small"
          color={getConnectionStatusColor(connectionStatus)}
          variant="outlined"
          sx={{
            textTransform: 'capitalize',
            fontWeight: 500,
          }}
        />

        {/* Refresh Button */}
        <Tooltip title="Refresh data">
          <IconButton
            color="inherit"
            onClick={handleRefresh}
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(74, 158, 255, 0.1)',
                transform: 'rotate(180deg)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>

        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton
            color="inherit"
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(74, 158, 255, 0.1)',
              },
            }}
          >
            <Badge badgeContent={0} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User Menu */}
        <Tooltip title="User menu">
          <IconButton
            onClick={handleMenuOpen}
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(74, 158, 255, 0.1)',
              },
            }}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                background: 'linear-gradient(45deg, #4a9eff, #ff4500)',
              }}
            >
              <PersonIcon fontSize="small" />
            </Avatar>
          </IconButton>
        </Tooltip>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          PaperProps={{
            sx: {
              mt: 1,
              minWidth: 200,
              background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
              border: '1px solid #404040',
            },
          }}
        >
          <MenuItem onClick={handleMenuClose}>
            <PersonIcon sx={{ mr: 2 }} />
            Profile
          </MenuItem>
          <Divider sx={{ borderColor: '#404040' }} />
          <MenuItem onClick={handleMenuClose}>
            Settings
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            Help & Support
          </MenuItem>
          <Divider sx={{ borderColor: '#404040' }} />
          <MenuItem onClick={handleMenuClose}>
            Sign Out
          </MenuItem>
        </Menu>

        {/* Last Update Time */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ ml: 2, minWidth: 80 }}
        >
          {formatTime(lastUpdate)}
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;