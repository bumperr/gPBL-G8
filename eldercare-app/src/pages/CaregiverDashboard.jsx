import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Paper,
  Alert,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  LinearProgress,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Dashboard,
  Person,
  Favorite,
  Warning,
  CheckCircle,
  Schedule,
  VolumeUp,
  Home,
  Phone,
  TrendingUp,
  Notifications,
  Settings,
  PlayArrow
} from '@mui/icons-material';
import apiService from '../services/api';
import CameraStream from '../components/CameraStream';

const CaregiverDashboard = ({ caregiverInfo }) => {
  const [elders, setElders] = useState([
    {
      id: 1,
      name: 'Mary Johnson',
      age: 78,
      status: 'safe',
      lastActivity: new Date(Date.now() - 15 * 60 * 1000),
      vitals: { heartRate: 72, bloodPressure: '120/80', temperature: 98.6 },
      location: 'Living Room',
      emergencyContact: '+1-555-0123'
    },
    {
      id: 2,
      name: 'Robert Smith',
      age: 82,
      status: 'alert',
      lastActivity: new Date(Date.now() - 2 * 60 * 1000),
      vitals: { heartRate: 68, bloodPressure: '118/75', temperature: 98.4 },
      location: 'Kitchen',
      emergencyContact: '+1-555-0124'
    }
  ]);

  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: 'voice_message',
      elderId: 1,
      elderName: 'Mary Johnson',
      message: 'Voice message received: "I need help with my medication"',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      priority: 'medium',
      handled: false
    },
    {
      id: 2,
      type: 'health',
      elderId: 2,
      elderName: 'Robert Smith',
      message: 'Heart rate slightly elevated (85 BPM)',
      timestamp: new Date(Date.now() - 10 * 60 * 1000),
      priority: 'low',
      handled: true
    }
  ]);

  const [serverStatus, setServerStatus] = useState('disconnected');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [autoRespond, setAutoRespond] = useState(true);

  // Check server health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiService.checkHealth();
        setServerStatus('connected');
      } catch (error) {
        setServerStatus('disconnected');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate random vitals updates
      setElders(prev => prev.map(elder => ({
        ...elder,
        vitals: {
          ...elder.vitals,
          heartRate: Math.floor(Math.random() * 20) + 65,
          temperature: (Math.random() * 2 + 97.5).toFixed(1)
        }
      })));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleAlertAction = async (alertId, action) => {
    const alert = alerts.find(a => a.id === alertId);
    if (!alert) return;

    try {
      if (action === 'respond') {
        // Send automated response
        const response = getAutomatedResponse(alert);
        await apiService.sendChatMessage(response);
        await apiService.textToSpeech(response, 'gtts', 'en');
      } else if (action === 'call') {
        // Simulate calling the elder
        const elder = elders.find(e => e.id === alert.elderId);
        if (elder) {
          console.log(`Calling ${elder.name} at ${elder.emergencyContact}`);
        }
      }

      // Mark alert as handled
      setAlerts(prev => prev.map(a => 
        a.id === alertId ? { ...a, handled: true } : a
      ));

    } catch (error) {
      console.error('Alert action failed:', error);
    }
  };

  const getAutomatedResponse = (alert) => {
    if (alert.type === 'voice_message') {
      return "I've received your message and a caregiver will respond shortly. If this is an emergency, please press the emergency button.";
    } else if (alert.type === 'health') {
      return "Your health metrics have been noted. Please rest and stay hydrated. Contact your doctor if you feel unwell.";
    }
    return "Your message has been received. Help is on the way if needed.";
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'safe': return 'success';
      case 'alert': return 'warning';
      case 'emergency': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const formatTimeAgo = (date) => {
    const minutes = Math.floor((Date.now() - date.getTime()) / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'between', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Dashboard color="primary" fontSize="large" />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                Caregiver Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {caregiverInfo?.name || 'Caregiver'} • Status: {serverStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
              </Typography>
            </Box>
          </Box>
          
          <FormControlLabel
            control={
              <Switch
                checked={autoRespond}
                onChange={(e) => setAutoRespond(e.target.checked)}
                color="primary"
              />
            }
            label="Auto-respond to alerts"
          />
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* Elder Status Cards */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Elder Status Overview
            </Typography>
            
            <Grid container spacing={2}>
              {elders.map(elder => (
                <Grid item xs={12} md={6} key={elder.id}>
                  <Card sx={{ borderRadius: 2, borderLeft: `4px solid ${getStatusColor(elder.status) === 'success' ? '#4CAF50' : getStatusColor(elder.status) === 'warning' ? '#FF9800' : '#f44336'}` }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6">{elder.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            Age: {elder.age} • {elder.location}
                          </Typography>
                        </Box>
                        <Chip 
                          label={elder.status.toUpperCase()} 
                          color={getStatusColor(elder.status)}
                          size="small"
                        />
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Vital Signs
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                          <Chip size="small" label={`❤️ ${elder.vitals.heartRate} BPM`} />
                          <Chip size="small" label={`🩺 ${elder.vitals.bloodPressure}`} />
                          <Chip size="small" label={`🌡️ ${elder.vitals.temperature}°F`} />
                        </Box>
                      </Box>

                      <Typography variant="body2" color="text.secondary">
                        Last activity: {formatTimeAgo(elder.lastActivity)}
                      </Typography>

                      <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                        <Button
                          size="small"
                          startIcon={<Phone />}
                          variant="outlined"
                          onClick={() => console.log(`Calling ${elder.name}`)}
                        >
                          Call
                        </Button>
                        <Button
                          size="small"
                          startIcon={<VolumeUp />}
                          variant="outlined"
                          onClick={() => apiService.textToSpeech(`Hello ${elder.name}, this is your caregiver checking in. How are you feeling?`)}
                        >
                          Announce
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Alerts and Notifications */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Notifications color="primary" />
              Recent Alerts ({alerts.filter(a => !a.handled).length} unhandled)
            </Typography>
            
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {alerts.map(alert => (
                <React.Fragment key={alert.id}>
                  <ListItem 
                    sx={{ 
                      backgroundColor: alert.handled ? 'transparent' : 'rgba(255, 152, 0, 0.1)',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <ListItemIcon>
                      {alert.type === 'voice_message' && <VolumeUp color={getPriorityColor(alert.priority)} />}
                      {alert.type === 'health' && <Favorite color={getPriorityColor(alert.priority)} />}
                      {alert.type === 'emergency' && <Warning color="error" />}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {alert.elderName}
                          </Typography>
                          <Typography variant="body2">
                            {alert.message}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                          <Typography variant="caption">
                            {formatTimeAgo(alert.timestamp)}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            {!alert.handled && (
                              <>
                                <Button
                                  size="small"
                                  onClick={() => handleAlertAction(alert.id, 'respond')}
                                  disabled={!autoRespond}
                                >
                                  Respond
                                </Button>
                                <Button
                                  size="small"
                                  onClick={() => handleAlertAction(alert.id, 'call')}
                                >
                                  Call
                                </Button>
                              </>
                            )}
                            {alert.handled && <CheckCircle color="success" fontSize="small" />}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <Home color={serverStatus === 'connected' ? 'success' : 'error'} />
                </ListItemIcon>
                <ListItemText
                  primary="Smart Home Server"
                  secondary={serverStatus === 'connected' ? 'Connected' : 'Disconnected'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Favorite color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Health Monitoring"
                  secondary="Active"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <VolumeUp color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Voice Assistant"
                  secondary="Ready"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom>
              Today's Summary
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Typography variant="h4" color="primary">
                    {alerts.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Alerts
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Typography variant="h4" color="success.main">
                    {alerts.filter(a => a.handled).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Resolved
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Typography variant="h4" color="info.main">
                    {elders.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Elders Monitored
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Typography variant="h4" color="warning.main">
                    {elders.filter(e => e.status === 'safe').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Safe Status
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Live Camera Feed Section */}
      <Paper elevation={2} sx={{ p: 2, borderRadius: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Dashboard color="primary" />
          Live Elder Care Monitoring
        </Typography>
        
        <Grid container spacing={3}>
          {elders.map(elder => (
            <Grid item xs={12} lg={6} key={elder.id}>
              <CameraStream
                elderName={elder.name}
                cameraServerUrl={`http://192.168.1.${200 + elder.id}:8080`} // Different Pi for each elder
                onSnapshot={(blob) => {
                  console.log(`Snapshot taken for ${elder.name}`);
                  // Handle snapshot - could save to server or display
                }}
                onError={(error) => {
                  console.error(`Camera error for ${elder.name}:`, error);
                  // Handle camera errors
                  setAlerts(prev => [...prev, {
                    id: Date.now(),
                    type: 'camera_error',
                    elderId: elder.id,
                    elderName: elder.name,
                    message: `Camera connection issue: ${error}`,
                    timestamp: new Date(),
                    priority: 'medium',
                    handled: false
                  }]);
                }}
              />
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
};

export default CaregiverDashboard;