import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Chip,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  CloudDownload as ScrapingIcon,
  Analytics as AnalyticsIcon,
  Storage as DataIcon,
  Settings as SettingsIcon,
  Reddit as RedditIcon,
  Circle as StatusIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const Sidebar = ({ open, onToggle, connectionStatus }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
      description: 'Overview and real-time metrics',
    },
    {
      text: 'Scraping',
      icon: <ScrapingIcon />,
      path: '/scraping',
      description: 'Start and monitor scraping sessions',
    },
    {
      text: 'Analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
      description: 'Sentiment analysis and trends',
    },
    {
      text: 'Data',
      icon: <DataIcon />,
      path: '/data',
      description: 'Browse and export scraped data',
    },
    {
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
      description: 'Configuration and preferences',
    },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return '#4caf50';
      case 'connecting':
      case 'reconnecting':
        return '#ff9800';
      case 'disconnected':
      case 'failed':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'reconnecting':
        return 'Reconnecting...';
      case 'disconnected':
        return 'Disconnected';
      case 'failed':
        return 'Connection Failed';
      default:
        return 'Unknown';
    }
  };

  const drawerWidth = open ? 280 : 80;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          transition: 'width 0.3s ease',
          overflow: 'hidden',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          minHeight: 64,
          borderBottom: '1px solid #404040',
        }}
      >
        <motion.div
          animate={{ rotate: open ? 0 : 360 }}
          transition={{ duration: 0.3 }}
        >
          <RedditIcon 
            sx={{ 
              fontSize: 32, 
              color: '#ff4500',
              filter: 'drop-shadow(0 0 8px rgba(255, 69, 0, 0.3))',
            }} 
          />
        </motion.div>
        
        {open && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(45deg, #4a9eff, #ff4500)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Reddit Scraper
            </Typography>
            <Typography variant="caption" color="text.secondary">
              v2.0.0 Dashboard
            </Typography>
          </motion.div>
        )}
      </Box>

      {/* Connection Status */}
      <Box sx={{ p: 2 }}>
        {open ? (
          <Chip
            icon={
              <StatusIcon 
                sx={{ 
                  color: getStatusColor(connectionStatus),
                  fontSize: '12px !important',
                }} 
              />
            }
            label={getStatusText(connectionStatus)}
            size="small"
            sx={{
              width: '100%',
              justifyContent: 'flex-start',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${getStatusColor(connectionStatus)}`,
              color: getStatusColor(connectionStatus),
            }}
          />
        ) : (
          <Tooltip title={getStatusText(connectionStatus)} placement="right">
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: `2px solid ${getStatusColor(connectionStatus)}`,
                mx: 'auto',
              }}
            >
              <StatusIcon 
                sx={{ 
                  color: getStatusColor(connectionStatus),
                  fontSize: 12,
                }} 
              />
            </Box>
          </Tooltip>
        )}
      </Box>

      <Divider sx={{ borderColor: '#404040' }} />

      {/* Navigation Menu */}
      <List sx={{ flexGrow: 1, px: 1, py: 2 }}>
        {menuItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          
          return (
            <motion.div
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <ListItem disablePadding sx={{ mb: 1 }}>
                <Tooltip 
                  title={open ? '' : item.description} 
                  placement="right"
                  arrow
                >
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    sx={{
                      borderRadius: 2,
                      minHeight: 48,
                      px: 2,
                      backgroundColor: isActive 
                        ? 'rgba(74, 158, 255, 0.1)' 
                        : 'transparent',
                      border: isActive 
                        ? '1px solid rgba(74, 158, 255, 0.3)' 
                        : '1px solid transparent',
                      '&:hover': {
                        backgroundColor: isActive 
                          ? 'rgba(74, 158, 255, 0.15)' 
                          : 'rgba(255, 255, 255, 0.05)',
                        transform: 'translateX(4px)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 40,
                        color: isActive ? '#4a9eff' : 'text.secondary',
                        transition: 'color 0.2s ease',
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    
                    {open && (
                      <ListItemText
                        primary={item.text}
                        secondary={item.description}
                        primaryTypographyProps={{
                          fontWeight: isActive ? 600 : 400,
                          color: isActive ? '#4a9eff' : 'text.primary',
                        }}
                        secondaryTypographyProps={{
                          fontSize: '0.75rem',
                          color: 'text.secondary',
                        }}
                      />
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            </motion.div>
          );
        })}
      </List>

      {/* Footer */}
      {open && (
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid #404040',
            textAlign: 'center',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Built with ❤️ by @pixelbrow720
          </Typography>
        </Box>
      )}
    </Drawer>
  );
};

export default Sidebar;