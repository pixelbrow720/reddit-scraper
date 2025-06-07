import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Sidebar from './components/Layout/Sidebar';
import TopBar from './components/Layout/TopBar';
import Dashboard from './pages/Dashboard';
import Scraping from './pages/Scraping';
import Analytics from './pages/Analytics';
import Data from './pages/Data';
import Settings from './pages/Settings';

// Services
import { websocketService } from './services/websocketService';

const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const location = useLocation();

  useEffect(() => {
    // Initialize WebSocket connection
    websocketService.connect();
    
    // Listen for connection status changes
    const handleConnectionChange = (status) => {
      setConnectionStatus(status);
    };

    websocketService.onConnectionChange(handleConnectionChange);

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Page transition variants
  const pageVariants = {
    initial: {
      opacity: 0,
      x: -20,
    },
    in: {
      opacity: 1,
      x: 0,
    },
    out: {
      opacity: 0,
      x: 20,
    },
  };

  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3,
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* Sidebar */}
      <Sidebar 
        open={sidebarOpen} 
        onToggle={handleSidebarToggle}
        connectionStatus={connectionStatus}
      />
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          transition: 'margin-left 0.3s ease',
          marginLeft: sidebarOpen ? '280px' : '80px',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%)',
        }}
      >
        {/* Top Bar */}
        <TopBar 
          onSidebarToggle={handleSidebarToggle}
          connectionStatus={connectionStatus}
        />
        
        {/* Page Content */}
        <Box
          sx={{
            flexGrow: 1,
            p: 3,
            overflow: 'auto',
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/scraping" element={<Scraping />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/data" element={<Data />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </Box>
      </Box>
    </Box>
  );
};

export default App;