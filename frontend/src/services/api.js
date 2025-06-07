import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now(),
    };
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          throw new Error(data.detail || 'Bad request');
        case 401:
          throw new Error('Unauthorized');
        case 403:
          throw new Error('Forbidden');
        case 404:
          throw new Error(data.detail || 'Not found');
        case 500:
          throw new Error('Internal server error');
        default:
          throw new Error(data.detail || `HTTP ${status} error`);
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error - please check your connection');
    } else {
      // Other error
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
);

// API endpoints
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Configuration
  async getConfiguration() {
    const response = await api.get('/config');
    return response.data;
  },

  // Scraping endpoints
  async startScraping(config) {
    const response = await api.post('/scrape/start', config);
    return response.data;
  },

  async getScrapeStatus(sessionId) {
    const response = await api.get(`/scrape/status/${sessionId}`);
    return response.data;
  },

  async getAllSessions() {
    const response = await api.get('/scrape/sessions');
    return response.data;
  },

  async stopScraping(sessionId) {
    const response = await api.delete(`/scrape/stop/${sessionId}`);
    return response.data;
  },

  // Data endpoints
  async getPosts(params = {}) {
    const response = await api.get('/data/posts', { params });
    return response.data;
  },

  // Analytics endpoints
  async getAnalyticsSummary(days = 7) {
    const response = await api.get('/analytics/summary', { params: { days } });
    return response.data;
  },

  async analyzeSentiment(config) {
    const response = await api.post('/analytics/sentiment', config);
    return response.data;
  },

  async analyzeTrends(config) {
    const response = await api.post('/analytics/trends', config);
    return response.data;
  },

  async getRealtimeAnalytics() {
    const response = await api.get('/analytics/realtime');
    return response.data;
  },

  // Database stats
  async getDatabaseStats() {
    const response = await api.get('/stats/database');
    return response.data;
  },
};

export default api;