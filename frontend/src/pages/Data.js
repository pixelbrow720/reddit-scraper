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
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link,
} from '@mui/material';
import {
  Storage,
  Refresh,
  Download,
  Visibility,
  FilterList,
  Search,
  OpenInNew,
  ThumbUp,
  Comment,
  Person,
  Schedule,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';

const Data = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalPosts, setTotalPosts] = useState(0);
  const [selectedPost, setSelectedPost] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState({
    subreddit: '',
    min_score: '',
    days_back: 7,
    search: '',
  });

  useEffect(() => {
    fetchPosts();
  }, [page, rowsPerPage, filters]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
        ...filters,
        min_score: filters.min_score ? parseInt(filters.min_score) : undefined,
      };
      
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === undefined) {
          delete params[key];
        }
      });
      
      const data = await apiService.getPosts(params);
      setPosts(data.posts || []);
      setTotalPosts(data.count || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
    setPage(0); // Reset to first page when filtering
  };

  const handleClearFilters = () => {
    setFilters({
      subreddit: '',
      min_score: '',
      days_back: 7,
      search: '',
    });
    setPage(0);
  };

  const handleViewPost = (post) => {
    setSelectedPost(post);
    setDetailDialogOpen(true);
  };

  const handleExportData = async () => {
    try {
      // This would trigger a download of the current filtered data
      // For now, we'll just show a success message
      alert('Export functionality would be implemented here');
    } catch (err) {
      setError(err.message);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const formatScore = (score) => {
    if (score >= 1000) {
      return `${(score / 1000).toFixed(1)}k`;
    }
    return score.toString();
  };

  const getSentimentColor = (score) => {
    if (score > 0.05) return 'success';
    if (score < -0.05) return 'error';
    return 'default';
  };

  const getSentimentLabel = (score) => {
    if (score > 0.05) return 'Positive';
    if (score < -0.05) return 'Negative';
    return 'Neutral';
  };

  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'image':
        return '🖼️';
      case 'video':
        return '🎥';
      case 'link':
        return '🔗';
      default:
        return '📝';
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
            Data Browser
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Browse, filter, and export your scraped Reddit data
          </Typography>
        </motion.div>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExportData}
          >
            Export Data
          </Button>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={fetchPosts}
            sx={{
              background: 'linear-gradient(45deg, #4a9eff, #2d7dd2)',
              '&:hover': {
                background: 'linear-gradient(45deg, #3a8eef, #1d6dc2)',
              },
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <FilterList sx={{ mr: 1 }} />
              <Typography variant="h6">
                Filters
              </Typography>
              <Button
                size="small"
                onClick={handleClearFilters}
                sx={{ ml: 'auto' }}
              >
                Clear All
              </Button>
            </Box>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Search"
                  placeholder="Search in titles..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  size="small"
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Subreddit"
                  placeholder="e.g., python"
                  value={filters.subreddit}
                  onChange={(e) => handleFilterChange('subreddit', e.target.value)}
                  size="small"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Min Score"
                  type="number"
                  value={filters.min_score}
                  onChange={(e) => handleFilterChange('min_score', e.target.value)}
                  size="small"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Days Back</InputLabel>
                  <Select
                    value={filters.days_back}
                    onChange={(e) => handleFilterChange('days_back', e.target.value)}
                    label="Days Back"
                  >
                    <MenuItem value={1}>1 Day</MenuItem>
                    <MenuItem value={3}>3 Days</MenuItem>
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={14}>14 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                    <MenuItem value={90}>90 Days</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Data Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardContent sx={{ p: 0 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Post</TableCell>
                    <TableCell>Subreddit</TableCell>
                    <TableCell align="center">Type</TableCell>
                    <TableCell align="right">Score</TableCell>
                    <TableCell align="right">Comments</TableCell>
                    <TableCell align="center">Sentiment</TableCell>
                    <TableCell>Author</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">
                          Loading posts...
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : posts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                        <Box
                          sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            color: 'text.secondary',
                          }}
                        >
                          <Storage sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                          <Typography variant="h6" gutterBottom>
                            No posts found
                          </Typography>
                          <Typography variant="body2">
                            Try adjusting your filters or scrape some data first
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                    posts.map((post) => (
                      <TableRow
                        key={post.id}
                        hover
                        sx={{
                          '&:hover': {
                            backgroundColor: 'rgba(74, 158, 255, 0.05)',
                          },
                        }}
                      >
                        <TableCell sx={{ maxWidth: 300 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              lineHeight: 1.4,
                            }}
                          >
                            {post.title}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Chip
                            label={`r/${post.subreddit}`}
                            size="small"
                            variant="outlined"
                            color="secondary"
                          />
                        </TableCell>
                        
                        <TableCell align="center">
                          <Tooltip title={post.content_type || 'text'}>
                            <span style={{ fontSize: '1.2em' }}>
                              {getContentTypeIcon(post.content_type)}
                            </span>
                          </Tooltip>
                        </TableCell>
                        
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                            <ThumbUp sx={{ fontSize: 16, mr: 0.5, color: 'success.main' }} />
                            <Typography variant="body2" color="success.main">
                              {formatScore(post.score)}
                            </Typography>
                          </Box>
                        </TableCell>
                        
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                            <Comment sx={{ fontSize: 16, mr: 0.5, color: 'info.main' }} />
                            <Typography variant="body2" color="info.main">
                              {post.num_comments}
                            </Typography>
                          </Box>
                        </TableCell>
                        
                        <TableCell align="center">
                          {post.sentiment_score !== null && post.sentiment_score !== undefined ? (
                            <Chip
                              label={getSentimentLabel(post.sentiment_score)}
                              size="small"
                              color={getSentimentColor(post.sentiment_score)}
                              variant="outlined"
                            />
                          ) : (
                            <Typography variant="caption" color="text.secondary">
                              N/A
                            </Typography>
                          )}
                        </TableCell>
                        
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Person sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary">
                              {post.author === '[deleted]' ? '[deleted]' : `u/${post.author}`}
                            </Typography>
                          </Box>
                        </TableCell>
                        
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Schedule sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(post.created_utc)}
                            </Typography>
                          </Box>
                        </TableCell>
                        
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="View details">
                              <IconButton
                                size="small"
                                onClick={() => handleViewPost(post)}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Open on Reddit">
                              <IconButton
                                size="small"
                                component={Link}
                                href={post.permalink}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <OpenInNew />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              component="div"
              count={totalPosts}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[10, 25, 50, 100]}
              sx={{
                borderTop: '1px solid #404040',
                '& .MuiTablePagination-toolbar': {
                  color: 'text.secondary',
                },
              }}
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Post Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
            border: '1px solid #404040',
          },
        }}
      >
        {selectedPost && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Post Details
                </Typography>
                <Chip
                  label={`r/${selectedPost.subreddit}`}
                  size="small"
                  color="secondary"
                  variant="outlined"
                />
              </Box>
            </DialogTitle>
            
            <DialogContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedPost.title}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<Person />}
                    label={selectedPost.author === '[deleted]' ? '[deleted]' : `u/${selectedPost.author}`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    icon={<ThumbUp />}
                    label={`${selectedPost.score} points`}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    icon={<Comment />}
                    label={`${selectedPost.num_comments} comments`}
                    size="small"
                    color="info"
                    variant="outlined"
                  />
                  <Chip
                    icon={<Schedule />}
                    label={formatDate(selectedPost.created_utc)}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                {selectedPost.sentiment_score !== null && selectedPost.sentiment_score !== undefined && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Sentiment Analysis
                    </Typography>
                    <Chip
                      label={`${getSentimentLabel(selectedPost.sentiment_score)} (${selectedPost.sentiment_score.toFixed(3)})`}
                      color={getSentimentColor(selectedPost.sentiment_score)}
                      variant="outlined"
                    />
                  </Box>
                )}
                
                {selectedPost.selftext && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Content
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        p: 2,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 1,
                        border: '1px solid #404040',
                        maxHeight: 200,
                        overflow: 'auto',
                      }}
                    >
                      {selectedPost.selftext}
                    </Typography>
                  </Box>
                )}
                
                {selectedPost.url && selectedPost.url !== selectedPost.permalink && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      External Link
                    </Typography>
                    <Link
                      href={selectedPost.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ wordBreak: 'break-all' }}
                    >
                      {selectedPost.url}
                    </Link>
                  </Box>
                )}
                
                {selectedPost.flair && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Flair
                    </Typography>
                    <Chip
                      label={selectedPost.flair}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                )}
              </Box>
            </DialogContent>
            
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>
                Close
              </Button>
              <Button
                variant="contained"
                component={Link}
                href={selectedPost.permalink}
                target="_blank"
                rel="noopener noreferrer"
                startIcon={<OpenInNew />}
              >
                View on Reddit
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default Data;