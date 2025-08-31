import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Chip,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore,
  Refresh,
  Analytics,
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Info,
  ImageSearch,
  Timeline,
  Assessment,
  Psychology,
  TrendingUp,
  Schedule,
  LocationOn,
  AccessTime,
  Security
} from '@mui/icons-material';

const CameraAnalytics = ({ elderId = 1, elderName = "John" }) => {
  const [analytics, setAnalytics] = useState([]);
  const [summary, setSummary] = useState({});
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('week');
  const [activityType, setActivityType] = useState('');
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [aiAnalysisOpen, setAiAnalysisOpen] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Activity type colors and icons
  const getActivityTypeConfig = (type) => {
    const configs = {
      'normal': { color: '#4CAF50', bgColor: '#E8F5E9', icon: <CheckCircle />, label: 'Normal' },
      'unusual': { color: '#FF9800', bgColor: '#FFF3E0', icon: <Info />, label: 'Unusual' },
      'alert': { color: '#F44336', bgColor: '#FFEBEE', icon: <Warning />, label: 'Alert' },
      'emergency': { color: '#D32F2F', bgColor: '#FFEBEE', icon: <ErrorIcon />, label: 'Emergency' }
    };
    return configs[type] || configs['normal'];
  };

  // Load analytics data
  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        period,
        limit: '50'
      });
      
      if (activityType) {
        params.append('activity_type', activityType);
      }
      
      const response = await fetch(`${API_BASE}/analytics/camera/${elderId}?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setAnalytics(data.analytics);
        setSummary(data.summary);
      } else {
        console.error('Failed to load analytics:', data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load AI behavioral analysis
  const loadAIAnalysis = async () => {
    try {
      setLoadingAI(true);
      
      const response = await fetch(`${API_BASE}/analytics/ai-analysis/${elderId}?period=${period}`);
      const data = await response.json();
      
      if (data.success) {
        setAiAnalysis(data);
        setAiAnalysisOpen(true);
      } else {
        console.error('Failed to load AI analysis:', data);
      }
    } catch (error) {
      console.error('Error loading AI analysis:', error);
    } finally {
      setLoadingAI(false);
    }
  };

  // Initialize data
  useEffect(() => {
    loadAnalytics();
  }, [period, activityType, elderId]);

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  // Format duration
  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  // Get placeholder image (since we don't have actual images yet)
  const getPlaceholderImage = (activity, activityType) => {
    // This will be replaced with actual base64 images from VLM analysis later
    const placeholders = {
      'walking': '🚶‍♂️',
      'sitting': '🪑',
      'eating': '🍽️',
      'sleeping': '😴',
      'standing': '🧍‍♂️',
      'restless_movement': '😰',
      'unsteady_walking': '⚠️',
      'nighttime_wandering': '🌙',
      'sudden_sitting': '🚨'
    };
    
    return placeholders[activity] || '📷';
  };

  const renderSummaryCards = () => {
    if (!summary.statistics) return null;

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h4" color="primary">
              {summary.statistics.total_activities}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Activities
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h4" color="error">
              {summary.statistics.anomalies_detected}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Anomalies Detected
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h4" color="warning.main">
              {summary.statistics.anomaly_rate_percent}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Anomaly Rate
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h4" color="success.main">
              {summary.statistics.average_confidence}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Confidence
            </Typography>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Analytics color="primary" />
            📹 Camera Analytics - {elderName}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<Psychology />}
              onClick={loadAIAnalysis}
              disabled={loadingAI}
              sx={{ mr: 1 }}
            >
              {loadingAI ? <CircularProgress size={20} /> : 'AI Analysis'}
            </Button>
            
            <IconButton onClick={loadAnalytics} disabled={loading}>
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {/* Filters */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Period</InputLabel>
            <Select
              value={period}
              label="Period"
              onChange={(e) => setPeriod(e.target.value)}
            >
              <MenuItem value="day">Today</MenuItem>
              <MenuItem value="week">This Week</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
              <MenuItem value="all">All Time</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Activity Type</InputLabel>
            <Select
              value={activityType}
              label="Activity Type"
              onChange={(e) => setActivityType(e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="normal">Normal</MenuItem>
              <MenuItem value="unusual">Unusual</MenuItem>
              <MenuItem value="alert">Alert</MenuItem>
              <MenuItem value="emergency">Emergency</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Summary Cards */}
        {renderSummaryCards()}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Analytics Table */}
        {!loading && (
          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Image</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Activity</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analytics.map((activity) => {
                  const typeConfig = getActivityTypeConfig(activity.activity_type);
                  
                  return (
                    <TableRow
                      key={activity.id}
                      sx={{
                        backgroundColor: activity.anomaly_detected ? 'rgba(255, 193, 7, 0.1)' : 'inherit',
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                      }}
                      onClick={() => setSelectedActivity(activity)}
                    >
                      {/* Placeholder Image */}
                      <TableCell>
                        <Avatar
                          sx={{
                            bgcolor: typeConfig.bgColor,
                            color: typeConfig.color,
                            width: 50,
                            height: 50
                          }}
                        >
                          {activity.image_base64 ? (
                            <img
                              src={`data:image/jpeg;base64,${activity.image_base64}`}
                              alt={activity.activity_detected}
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            />
                          ) : (
                            <Typography variant="h6">
                              {getPlaceholderImage(activity.activity_detected, activity.activity_type)}
                            </Typography>
                          )}
                        </Avatar>
                      </TableCell>

                      {/* Timestamp */}
                      <TableCell>
                        <Typography variant="body2">
                          {formatTimestamp(activity.timestamp)}
                        </Typography>
                      </TableCell>

                      {/* Activity */}
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {activity.activity_detected.replace(/_/g, ' ')}
                        </Typography>
                        {activity.anomaly_detected && (
                          <Tooltip title="Anomaly detected">
                            <Warning color="warning" fontSize="small" />
                          </Tooltip>
                        )}
                      </TableCell>

                      {/* Type */}
                      <TableCell>
                        <Chip
                          icon={typeConfig.icon}
                          label={typeConfig.label}
                          size="small"
                          sx={{
                            backgroundColor: typeConfig.bgColor,
                            color: typeConfig.color,
                            '& .MuiChip-icon': { color: typeConfig.color }
                          }}
                        />
                      </TableCell>

                      {/* Location */}
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <LocationOn fontSize="small" color="action" />
                          <Typography variant="body2">
                            {activity.location}
                          </Typography>
                        </Box>
                      </TableCell>

                      {/* Duration */}
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTime fontSize="small" color="action" />
                          <Typography variant="body2">
                            {formatDuration(activity.duration_seconds)}
                          </Typography>
                        </Box>
                      </TableCell>

                      {/* Confidence */}
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={activity.confidence_score * 100}
                            sx={{ width: 50, height: 6 }}
                          />
                          <Typography variant="caption">
                            {Math.round(activity.confidence_score * 100)}%
                          </Typography>
                        </Box>
                      </TableCell>

                      {/* Details Button */}
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Info />}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedActivity(activity);
                          }}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* No Data Message */}
        {!loading && analytics.length === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            No camera analytics data found for the selected period and filters.
          </Alert>
        )}

        {/* Activity Details Dialog */}
        <Dialog
          open={!!selectedActivity}
          onClose={() => setSelectedActivity(null)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Activity Details - {selectedActivity?.activity_detected?.replace(/_/g, ' ')}
          </DialogTitle>
          <DialogContent>
            {selectedActivity && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Avatar
                    sx={{
                      width: 150,
                      height: 150,
                      mx: 'auto',
                      bgcolor: getActivityTypeConfig(selectedActivity.activity_type).bgColor
                    }}
                  >
                    {selectedActivity.image_base64 ? (
                      <img
                        src={`data:image/jpeg;base64,${selectedActivity.image_base64}`}
                        alt={selectedActivity.activity_detected}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : (
                      <Typography variant="h1">
                        {getPlaceholderImage(selectedActivity.activity_detected, selectedActivity.activity_type)}
                      </Typography>
                    )}
                  </Avatar>
                </Grid>
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" gutterBottom>
                    Activity Information
                  </Typography>
                  <Typography><strong>Time:</strong> {formatTimestamp(selectedActivity.timestamp)}</Typography>
                  <Typography><strong>Location:</strong> {selectedActivity.location}</Typography>
                  <Typography><strong>Duration:</strong> {formatDuration(selectedActivity.duration_seconds)}</Typography>
                  <Typography><strong>Confidence:</strong> {Math.round(selectedActivity.confidence_score * 100)}%</Typography>
                  <Typography><strong>Anomaly:</strong> {selectedActivity.anomaly_detected ? 'Yes' : 'No'}</Typography>
                  
                  {selectedActivity.ai_analysis && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h6" gutterBottom>AI Analysis</Typography>
                      <Typography variant="body2">
                        {selectedActivity.ai_analysis}
                      </Typography>
                    </Box>
                  )}
                  
                  {selectedActivity.metadata && Object.keys(selectedActivity.metadata).length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h6" gutterBottom>Additional Data</Typography>
                      <pre style={{ fontSize: '12px', background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
                        {JSON.stringify(selectedActivity.metadata, null, 2)}
                      </pre>
                    </Box>
                  )}
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSelectedActivity(null)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* AI Analysis Dialog */}
        <Dialog
          open={aiAnalysisOpen}
          onClose={() => setAiAnalysisOpen(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Psychology color="primary" />
              AI Behavioral Analysis - {elderName}
            </Box>
          </DialogTitle>
          <DialogContent>
            {aiAnalysis && (
              <Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                  {aiAnalysis.ai_behavioral_analysis}
                </Typography>
                
                <Typography variant="caption" color="text.secondary">
                  Analysis generated: {new Date(aiAnalysis.generated_at).toLocaleString()} | 
                  Confidence: {Math.round(aiAnalysis.confidence_score * 100)}% | 
                  Data points: {aiAnalysis.data_points_analyzed}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAiAnalysisOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default CameraAnalytics;