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
  DialogActions,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  Badge,
  CircularProgress
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
  PlayArrow,
  VideoCall,
  Lightbulb,
  Thermostat,
  Kitchen,
  Bed,
  Chair,
  Power,
  PowerOff,
  ExpandMore,
  Videocam,
  LocalHospital,
  Assignment,
  Timeline
} from '@mui/icons-material';
import apiService from '../services/api';
import WebCamStream from '../components/WebCamStream';
import ServerCameraStream from '../components/ServerCameraStream';
import CameraAnalytics from '../components/CameraAnalytics';

const CaregiverDashboard = ({ caregiverInfo }) => {
  // State for eldercare data from database
  const [elders, setElders] = useState([]);
  const [selectedElder, setSelectedElder] = useState(null);
  const [facilityStats, setFacilityStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState(0);
  const [videoStreamOpen, setVideoStreamOpen] = useState(false);

  // John's data simulation for vitals and activities (for parts not covered by database)
  const [johnData, setJohnData] = useState({
    vitals: {
      heartRate: 72,
      bloodPressure: '120/80',
      temperature: 98.6
    },
    lastActivity: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
    location: 'Living Room',
    status: 'safe',
    emergencyContact: '+6011468550',
    medications: [
      { name: 'Lisinopril', taken: true },
      { name: 'Multivitamin', taken: true },
      { name: 'Acetaminophen', taken: false }
    ]
  });

  // Load eldercare data from database
  const loadEldercareData = async () => {
    try {
      setLoading(true);
      console.log('Loading eldercare data...');
      
      // Get facility dashboard data
      const dashboardResponse = await fetch(`/api/eldercare/dashboard`);
      console.log('Dashboard response status:', dashboardResponse.status);
      
      if (!dashboardResponse.ok) {
        throw new Error(`Dashboard API returned status ${dashboardResponse.status}`);
      }
      
      const dashboardData = await dashboardResponse.json();
      console.log('Dashboard data loaded:', dashboardData);
      
      if (dashboardData.success) {
        setElders(dashboardData.elders);
        setFacilityStats(dashboardData.facility_stats);
        console.log('Elders set:', dashboardData.elders);
        
        // Auto-select first elder if available
        if (dashboardData.elders.length > 0) {
          setSelectedElder(dashboardData.elders[0]);
          console.log('Auto-selected elder:', dashboardData.elders[0]);
        }
      } else {
        console.error('Dashboard data not successful:', dashboardData);
      }
    } catch (error) {
      console.error('Error loading eldercare data:', error);
    } finally {
      setLoading(false);
      console.log('Loading finished');
    }
  };

  // Load specific elder details
  const loadElderDetails = async (elderId) => {
    try {
      const response = await fetch(`/api/eldercare/elders/${elderId}`);
      const data = await response.json();
      
      if (data.success) {
        setSelectedElder(data.elder);
        return data;
      }
    } catch (error) {
      console.error('Error loading elder details:', error);
    }
    return null;
  };

  // Handle video stream
  const handleVideoStream = (stream) => {
    console.log('Video stream started:', stream);
  };

  // Handle snapshot
  const handleSnapshot = (blob, dataUrl) => {
    console.log('Snapshot taken:', blob);
    // Could save to elder's profile or send to monitoring system
  };

  // Initialize data on mount
  useEffect(() => {
    loadEldercareData();
    
    // Fallback timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (loading) {
        console.log('Loading timeout - forcing completion');
        setLoading(false);
        // Set fallback data if needed
        if (elders.length === 0) {
          const fallbackElder = {
            id: 1,
            name: 'John',
            age: 78,
            gender: 'male',
            care_level: 'assisted',
            room_location: 'Living Room',
            bed_number: 'Main Area',
            emergency_contact_name: 'Sarah',
            emergency_contact_phone: '+6011468550',
            medical_conditions: ['hypertension', 'mild_dementia', 'arthritis'],
            medications: ['lisinopril_10mg_daily', 'acetaminophen_as_needed', 'multivitamin'],
            allergies: ['penicillin', 'shellfish']
          };
          console.log('Setting fallback elder data:', fallbackElder);
          setElders([fallbackElder]);
          setSelectedElder(fallbackElder);
          setFacilityStats({ total_elders: 1, total_active_alerts: 0, total_pending_activities: 0, elders_with_interactions_today: 0 });
        }
      }
    }, 5000); // 5 second timeout
    
    return () => clearTimeout(timeout);
  }, []);

  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: 'ai_chat',
      elderId: 1,
      elderName: 'John',
      message: 'Chat interaction: "I feel lonely today"',
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      priority: 'medium',
      handled: false,
      details: 'John expressed loneliness. AI suggested video call with Sarah.'
    },
    {
      id: 2,
      type: 'smart_home',
      elderId: 1,
      elderName: 'John',
      message: 'Smart home request: "Turn on living room lights"',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      priority: 'low',
      handled: true,
      details: 'Successfully executed lighting control commands.'
    },
    {
      id: 3,
      type: 'health_check',
      elderId: 1,
      elderName: 'John',
      message: 'Regular health monitoring - all vitals normal',
      timestamp: new Date(Date.now() - 30 * 60 * 1000),
      priority: 'low',
      handled: true,
      details: 'Vital signs within normal ranges.'
    }
  ]);

  const [serverStatus, setServerStatus] = useState('disconnected');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [autoRespond, setAutoRespond] = useState(true);
  
  // Smart home control state
  const [smartHomeControls, setSmartHomeControls] = useState({
    lights: {
      living_room: false,
      kitchen: false,
      bedroom: false,
      bathroom: false
    },
    thermostat: {
      temperature: 22, // Current set temperature
      current_temp: 23.5, // Current room temperature from DHT11
      humidity: 65 // Current humidity from DHT11
    }
  });

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

  // Polling for real-time MQTT updates (fallback if WebSocket fails)
  useEffect(() => {
    // First try WebSocket connection
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//localhost:8000/ws/smart-home`;
    console.log('CaregiverDashboard: Attempting WebSocket connection to:', wsUrl);
    const ws = new WebSocket(wsUrl);
    
    let pollInterval = null;
    
    ws.onopen = () => {
      console.log('WebSocket connected for smart home updates');
      setServerStatus('connected');
      // Clear polling interval if WebSocket connects
      if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        if (data.type === 'initial_state' || data.type === 'state_update') {
          // Update smart home controls with real Arduino data
          const state = data.current_state || data.data;
          
          if (state.sensors) {
            setSmartHomeControls(prev => ({
              ...prev,
              thermostat: {
                ...prev.thermostat,
                current_temp: state.sensors.temperature || prev.thermostat.current_temp,
                humidity: state.sensors.humidity || prev.thermostat.humidity
              }
            }));
          }
          
          if (state.devices) {
            setSmartHomeControls(prev => ({
              ...prev,
              lights: {
                ...prev.lights,
                // Update LED state if available
                living_room: state.devices.led === "ON" ? true : prev.lights.living_room
              },
              thermostat: {
                ...prev.thermostat,
                temperature: state.devices.thermostat_target || prev.thermostat.temperature
              }
            }));
          }
        }
        
        if (data.type === 'mqtt_update') {
          // Handle specific MQTT topic updates
          if (data.topic === 'home/dht11') {
            const [temp, humidity] = data.message.split(',');
            setSmartHomeControls(prev => ({
              ...prev,
              thermostat: {
                ...prev.thermostat,
                current_temp: parseFloat(temp) || prev.thermostat.current_temp,
                humidity: parseFloat(humidity) || prev.thermostat.humidity
              }
            }));
          } else if (data.topic === 'home/led/cmd') {
            setSmartHomeControls(prev => ({
              ...prev,
              lights: {
                ...prev.lights,
                living_room: data.message === "ON"
              }
            }));
          } else if (data.topic === 'home/thermostat/set') {
            setSmartHomeControls(prev => ({
              ...prev,
              thermostat: {
                ...prev.thermostat,
                temperature: parseInt(data.message) || prev.thermostat.temperature
              }
            }));
          }
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setServerStatus('disconnected');
      
      // Start polling as fallback if WebSocket fails
      if (!pollInterval) {
        console.log('Starting polling fallback for smart home updates');
        pollInterval = setInterval(async () => {
          try {
            const response = await fetch('/smart-home/status');
            if (response.ok) {
              const data = await response.json();
              console.log('Polling update received:', data);
              
              // Update thermostat with current temperature and humidity
              if (data.raw_state && data.raw_state.sensors) {
                setSmartHomeControls(prev => ({
                  ...prev,
                  thermostat: {
                    ...prev.thermostat,
                    current_temp: data.raw_state.sensors.temperature || prev.thermostat.current_temp,
                    humidity: data.raw_state.sensors.humidity || prev.thermostat.humidity
                  }
                }));
              }
            }
          } catch (error) {
            console.error('Polling error:', error);
          }
        }, 2000); // Poll every 2 seconds
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setServerStatus('disconnected');
      
      // Start polling as fallback if WebSocket closes
      if (!pollInterval) {
        console.log('Starting polling fallback for smart home updates');
        pollInterval = setInterval(async () => {
          try {
            const response = await fetch('/smart-home/status');
            if (response.ok) {
              const data = await response.json();
              console.log('Polling update received:', data);
              
              // Update thermostat with current temperature and humidity
              if (data.raw_state && data.raw_state.sensors) {
                setSmartHomeControls(prev => ({
                  ...prev,
                  thermostat: {
                    ...prev.thermostat,
                    current_temp: data.raw_state.sensors.temperature || prev.thermostat.current_temp,
                    humidity: data.raw_state.sensors.humidity || prev.thermostat.humidity
                  }
                }));
              }
            }
          } catch (error) {
            console.error('Polling error:', error);
          }
        }, 2000); // Poll every 2 seconds
      }
    };
    
    return () => {
      ws.close();
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, []);

  // Simulate real-time updates for John's data (keep for vitals that aren't from Arduino)
  useEffect(() => {
    const interval = setInterval(() => {
      setJohnData(prev => ({
        ...prev,
        vitals: {
          ...prev.vitals,
          heartRate: Math.floor(Math.random() * 15) + 68, // John's normal range: 68-83
          // Remove temperature simulation since we get it from Arduino now
        },
        lastActivity: Math.random() > 0.7 ? new Date() : prev.lastActivity, // 30% chance of activity update
        location: Math.random() > 0.8 ? 
          ['Living Room', 'Kitchen', 'Bedroom', 'Bathroom'][Math.floor(Math.random() * 4)] : 
          prev.location
      }));
    }, 15000); // Update every 15 seconds for more frequent monitoring

    return () => clearInterval(interval);
  }, []);

  const handleAlertAction = async (alertId, action) => {
    const alert = alerts.find(a => a.id === alertId);
    if (!alert) return;

    try {
      if (action === 'respond') {
        // Send automated response to John
        const response = getAutomatedResponse(alert);
        console.log(`Sending response to John: ${response}`);
        // In a real implementation, this would send the message through the chat system
      } else if (action === 'call') {
        // Call John via WhatsApp
        const whatsappUrl = `https://wa.me/${johnData.emergencyContact.replace('+', '')}?text=Hi John, this is Sarah. I saw an alert and wanted to check in on you. Are you okay?`;
        window.open(whatsappUrl, '_blank');
        console.log(`Opening WhatsApp to call John at ${johnData.emergencyContact}`);
      } else if (action === 'video_call') {
        // Start video call with John
        const whatsappUrl = `https://wa.me/${johnData.emergencyContact.replace('+', '')}?text=Hi John, would you like to have a video call? I'm here if you need to talk.`;
        window.open(whatsappUrl, '_blank');
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
    if (alert.type === 'ai_chat') {
      return "Hi John, I saw that you were chatting with the AI. Sarah will reach out to you soon. You're not alone!";
    } else if (alert.type === 'smart_home') {
      return "John, I noticed your smart home request. Everything looks good from here. Let me know if you need any adjustments.";
    } else if (alert.type === 'health_check') {
      return "John, your vitals look good today. Keep up the great work taking care of yourself!";
    } else if (alert.type === 'emergency') {
      return "John, I'm coming to check on you right away. Stay calm, help is on the way.";
    }
    return "Hi John, this is Sarah. I'm here if you need anything. Take care!";
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

  // Smart home control functions
  const handleLightControl = async (room, state) => {
    try {
      // Send MQTT command based on Arduino endpoints
      const mqttTopic = room === 'living_room' ? 'home/led/cmd' : `home/${room}/led/cmd`;
      const command = state ? 'ON' : 'OFF';
      
      await apiService.sendMQTTMessage(mqttTopic, command);
      
      // Don't update state immediately - let WebSocket handle it
      // This ensures UI syncs with actual Arduino device state
      console.log(`Light command sent for ${room}: ${command}`);

      // Add alert for successful control
      setAlerts(prev => [...prev, {
        id: Date.now(),
        type: 'smart_home',
        elderId: 1,
        elderName: 'John',
        message: `Light ${state ? 'turned on' : 'turned off'} in ${room.replace('_', ' ')}`,
        timestamp: new Date(),
        priority: 'low',
        handled: false
      }]);

      console.log(`${room} light ${state ? 'ON' : 'OFF'} command sent successfully`);
    } catch (error) {
      console.error('Failed to control light:', error);
    }
  };

  const handleThermostatChange = async (newTemperature) => {
    try {
      // Send thermostat command via MQTT
      await apiService.sendMQTTMessage('home/thermostat/set', newTemperature.toString());
      
      // Don't update state immediately - let WebSocket handle it
      // This ensures UI syncs with actual Arduino device state
      console.log(`Thermostat command sent: ${newTemperature}°C`);

      // Add alert for thermostat change
      setAlerts(prev => [...prev, {
        id: Date.now(),
        type: 'smart_home',
        elderId: 1,
        elderName: 'John',
        message: `Thermostat set to ${newTemperature}°C for John's comfort`,
        timestamp: new Date(),
        priority: 'low',
        handled: false
      }]);

      console.log(`Thermostat set to ${newTemperature}°C`);
    } catch (error) {
      console.error('Failed to control thermostat:', error);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 2, textAlign: 'center' }}>
        <CircularProgress size={50} />
        <Typography variant="h6" sx={{ mt: 2 }}>Loading Eldercare Data...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Dashboard color="primary" fontSize="large" />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                Eldercare Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {caregiverInfo?.name || 'Caregiver'} • {elders.length} Residents • Status: {serverStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<Videocam />}
              onClick={() => setVideoStreamOpen(true)}
            >
              Video Monitor
            </Button>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRespond}
                  onChange={(e) => setAutoRespond(e.target.checked)}
                  color="primary"
                />
              }
              label="Auto-respond"
            />
          </Box>
        </Box>
      </Paper>

      {/* Facility Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary">{facilityStats.total_elders || 0}</Typography>
              <Typography variant="body2">Total Residents</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error">{facilityStats.total_active_alerts || 0}</Typography>
              <Typography variant="body2">Active Alerts</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">{facilityStats.total_pending_activities || 0}</Typography>
              <Typography variant="body2">Pending Activities</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">{facilityStats.elders_with_interactions_today || 0}</Typography>
              <Typography variant="body2">Active Today</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Elder Tabs */}
      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={(e, newTab) => setCurrentTab(newTab)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {elders.map((elder, index) => (
            <Tab 
              key={elder.id}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ width: 24, height: 24 }}>
                    {elder.name.charAt(0)}
                  </Avatar>
                  {elder.name}
                  <Badge
                    badgeContent={elder.dashboard_stats?.active_alerts || 0}
                    color="error"
                    max={99}
                  />
                </Box>
              }
              onClick={() => {
                setSelectedElder(elder);
                loadElderDetails(elder.id);
              }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* Video Stream Dialog */}
      <Dialog
        open={videoStreamOpen}
        onClose={() => setVideoStreamOpen(false)}
        maxWidth="lg"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            maxHeight: { xs: '100%', sm: '90vh' },
            margin: { xs: 0, sm: 2 }
          }
        }}
      >
        <DialogTitle sx={{ 
          pb: { xs: 1, sm: 2 },
          fontSize: { xs: '1.1rem', sm: '1.25rem' }
        }}>
          Video Monitoring - {selectedElder?.name || 'Select Elder'}
        </DialogTitle>
        <DialogContent sx={{ 
          p: { xs: 1, sm: 2 },
          '&:first-of-type': { pt: { xs: 1, sm: 2 } }
        }}>
          <ServerCameraStream
            cameraId={0}
            onSnapshot={handleSnapshot}
            onError={(error) => console.error('Video monitor error:', error)}
            autoStart={true}
            showControls={true}
            width={640}
            height={480}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVideoStreamOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {selectedElder && (
        <Grid container spacing={3}>
          {/* Selected Elder Details */}
          <Grid item xs={12} lg={8}>
            <Paper elevation={2} sx={{ p: 2, borderRadius: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                👴 {selectedElder.name}'s Profile & Health Monitoring
              </Typography>
            
            <Grid container spacing={3}>
              {/* John's Main Status Card */}
              <Grid item xs={12} lg={8}>
                <Card sx={{ 
                  borderRadius: 3, 
                  borderLeft: '6px solid #4CAF50',
                  background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)',
                  boxShadow: '0 4px 20px rgba(76, 175, 80, 0.2)'
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 3 }}>
                      <Box>
                        <Typography variant="h5" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                          {selectedElder.name}
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
                          Age: {selectedElder.age} • Gender: {selectedElder.gender} • Care Level: {selectedElder.care_level}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          📍 Room: <strong>{selectedElder.room_location} - {selectedElder.bed_number}</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          📞 Emergency: {selectedElder.emergency_contact_phone} ({selectedElder.emergency_contact_name})
                        </Typography>
                      </Box>
                      <Chip 
                        label="ACTIVE" 
                        color="success"
                        size="medium"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" color="text.secondary" gutterBottom sx={{ color: '#388e3c' }}>
                        📊 Real-time Vital Signs
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Chip 
                          size="medium" 
                          label={`❤️ ${johnData.vitals.heartRate} BPM`} 
                          sx={{ backgroundColor: '#c8e6c9', color: '#2e7d32', fontWeight: 'bold' }}
                        />
                        <Chip 
                          size="medium" 
                          label={`🩺 ${johnData.vitals.bloodPressure}`} 
                          sx={{ backgroundColor: '#c8e6c9', color: '#2e7d32', fontWeight: 'bold' }}
                        />
                        <Chip 
                          size="medium" 
                          label={`🌡️ ${johnData.vitals.temperature}°F`} 
                          sx={{ backgroundColor: '#c8e6c9', color: '#2e7d32', fontWeight: 'bold' }}
                        />
                      </Box>
                    </Box>

                    <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                      🕐 Last activity: <strong>{formatTimeAgo(johnData.lastActivity)}</strong>
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 2, mt: 3, flexWrap: 'wrap' }}>
                      <Button
                        size="medium"
                        startIcon={<Phone />}
                        variant="contained"
                        sx={{ 
                          background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)',
                          '&:hover': { background: 'linear-gradient(135deg, #388e3c 0%, #4caf50 100%)' }
                        }}
                        onClick={() => {
                          const whatsappUrl = `https://wa.me/${johnData.emergencyContact.replace('+', '')}?text=Hi John, this is Sarah checking in. How are you doing today?`;
                          window.open(whatsappUrl, '_blank');
                        }}
                      >
                        📞 Call John
                      </Button>
                      <Button
                        size="medium"
                        startIcon={<VideoCall />}
                        variant="contained"
                        sx={{ 
                          background: 'linear-gradient(135deg, #66bb6a 0%, #81c784 100%)',
                          '&:hover': { background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)' }
                        }}
                        onClick={() => {
                          const whatsappUrl = `https://wa.me/${johnData.emergencyContact.replace('+', '')}?text=Hi John, would you like to have a video call? I'm free to chat!`;
                          window.open(whatsappUrl, '_blank');
                        }}
                      >
                        📹 Video Call
                      </Button>
                      <Button
                        size="medium"
                        startIcon={<VolumeUp />}
                        variant="outlined"
                        sx={{ 
                          borderColor: '#4caf50', 
                          color: '#2e7d32',
                          '&:hover': { backgroundColor: '#e8f5e8' }
                        }}
                        onClick={() => console.log('Sending voice message to John')}
                      >
                        📢 Send Voice Message
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Elder's Medical Info & Conditions */}
              <Grid item xs={12} lg={4}>
                <Card sx={{ borderRadius: 3, mb: 2, background: 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                      💊 Medications
                    </Typography>
                    {selectedElder.medications && selectedElder.medications.length > 0 ? (
                      selectedElder.medications.map((med, index) => (
                        <Box key={index} sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center', 
                          py: 1,
                          borderBottom: index < selectedElder.medications.length - 1 ? '1px solid #c8e6c9' : 'none'
                        }}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{med}</Typography>
                          </Box>
                        </Box>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No medications recorded</Typography>
                    )}
                  </CardContent>
                </Card>

                <Card sx={{ borderRadius: 3, mb: 2, background: 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                      🏥 Medical Conditions
                    </Typography>
                    {selectedElder.medical_conditions && selectedElder.medical_conditions.length > 0 ? (
                      selectedElder.medical_conditions.map((condition, index) => (
                        <Chip 
                          key={index}
                          label={condition}
                          size="small"
                          sx={{ mr: 1, mb: 1, backgroundColor: '#ffcdd2' }}
                        />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No conditions recorded</Typography>
                    )}
                  </CardContent>
                </Card>

                <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                      ⚠️ Allergies
                    </Typography>
                    {selectedElder.allergies && selectedElder.allergies.length > 0 ? (
                      selectedElder.allergies.map((allergy, index) => (
                        <Chip 
                          key={index}
                          label={allergy}
                          size="small"
                          color="warning"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No allergies recorded</Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Smart Home Quick Controls */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ 
            p: 3, 
            borderRadius: 3, 
            mb: 3,
            background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)',
            border: '2px solid #c8e6c9'
          }}>
            <Typography variant="h5" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
              🏠 John's Smart Home Controls
            </Typography>
            
            <Grid container spacing={3}>
              {/* Room Light Controls */}
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom sx={{ color: '#388e3c' }}>
                  💡 Room Lighting
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(smartHomeControls.lights).map(([room, isOn]) => {
                    const roomIcons = {
                      living_room: <Chair />,
                      kitchen: <Kitchen />,
                      bedroom: <Bed />,
                      bathroom: <Home />
                    };
                    
                    return (
                      <Grid item xs={6} sm={3} key={room}>
                        <Card sx={{ 
                          borderRadius: 3,
                          backgroundColor: isOn ? '#c8e6c9' : '#f5f5f5',
                          border: isOn ? '2px solid #4caf50' : '2px solid #e0e0e0',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease-in-out',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 4px 20px rgba(76, 175, 80, 0.3)'
                          }
                        }}>
                          <CardContent 
                            sx={{ 
                              textAlign: 'center', 
                              py: 2,
                              '&:last-child': { pb: 2 }
                            }}
                            onClick={() => handleLightControl(room, !isOn)}
                          >
                            <Box sx={{ 
                              display: 'flex', 
                              flexDirection: 'column', 
                              alignItems: 'center', 
                              gap: 1 
                            }}>
                              <Box sx={{ position: 'relative' }}>
                                {roomIcons[room]}
                                <Lightbulb sx={{ 
                                  position: 'absolute',
                                  top: -8,
                                  right: -8,
                                  fontSize: '1rem',
                                  color: isOn ? '#4caf50' : '#bdbdbd'
                                }} />
                              </Box>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  fontWeight: 'bold',
                                  color: isOn ? '#2e7d32' : '#666',
                                  textTransform: 'capitalize'
                                }}
                              >
                                {room.replace('_', ' ')}
                              </Typography>
                              <Chip 
                                label={isOn ? 'ON' : 'OFF'} 
                                size="small"
                                sx={{ 
                                  backgroundColor: isOn ? '#4caf50' : '#bdbdbd',
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              </Grid>

              {/* Thermostat Control */}
              <Grid item xs={12} md={4}>
                <Typography variant="h6" gutterBottom sx={{ color: '#388e3c' }}>
                  🌡️ Climate Control
                </Typography>
                <Card sx={{ 
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)',
                  border: '2px solid #81c784',
                  height: '100%'
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      <Thermostat sx={{ fontSize: 48, color: '#4caf50', mb: 1 }} />
                      <Typography variant="h4" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                        {smartHomeControls.thermostat.temperature}°C
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Target Temperature
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Current: {smartHomeControls.thermostat.current_temp}°C
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Humidity: {smartHomeControls.thermostat.humidity}%
                      </Typography>
                    </Box>

                    <Box sx={{ px: 1 }}>
                      <input
                        type="range"
                        min="16"
                        max="30"
                        value={smartHomeControls.thermostat.temperature}
                        onChange={(e) => handleThermostatChange(parseInt(e.target.value))}
                        style={{
                          width: '100%',
                          height: '8px',
                          borderRadius: '4px',
                          background: `linear-gradient(to right, #81c784 0%, #4caf50 50%, #2e7d32 100%)`,
                          outline: 'none',
                          cursor: 'pointer'
                        }}
                      />
                      <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        mt: 1 
                      }}>
                        <Typography variant="caption" color="text.secondary">16°C</Typography>
                        <Typography variant="caption" color="text.secondary">30°C</Typography>
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        sx={{ 
                          borderColor: '#4caf50', 
                          color: '#2e7d32',
                          '&:hover': { backgroundColor: '#e8f5e8' }
                        }}
                        onClick={() => handleThermostatChange(smartHomeControls.thermostat.temperature - 1)}
                      >
                        ➖
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        sx={{ 
                          borderColor: '#4caf50', 
                          color: '#2e7d32',
                          '&:hover': { backgroundColor: '#e8f5e8' }
                        }}
                        onClick={() => handleThermostatChange(smartHomeControls.thermostat.temperature + 1)}
                      >
                        ➕
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
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

        {/* John's Daily Summary */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ 
            p: 3, 
            borderRadius: 3,
            background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)',
            border: '2px solid #c8e6c9'
          }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
              📊 John's Daily Summary
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                  <Typography variant="h3" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                    {alerts.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Interactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                  <Typography variant="h3" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                    {alerts.filter(a => a.handled).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completed
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                  <Typography variant="h3" sx={{ color: '#66bb6a', fontWeight: 'bold' }}>
                    {johnData.medications.filter(m => m.taken).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Meds Taken
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                  <Typography variant="h3" sx={{ color: johnData.status === 'safe' ? '#4caf50' : '#ff9800', fontWeight: 'bold' }}>
                    {johnData.status === 'safe' ? '✅' : '⚠️'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Current Status
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* Live Camera Feed */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ 
        p: 3, 
        borderRadius: 3, 
        mt: 3,
        background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)',
        border: '2px solid #c8e6c9'
      }}>
        <Typography variant="h6" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1,
          color: '#2e7d32',
          fontWeight: 'bold' 
        }}>
          📹 John's Live Monitoring Feed
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Real-time visual monitoring for John's safety and wellbeing
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <ServerCameraStream
              cameraId={0}
              onSnapshot={(blob, dataUrl) => {
                console.log('Snapshot taken for John via server camera');
                // Could save to server or display
                setAlerts(prev => [...prev, {
                  id: Date.now(),
                  type: 'camera_snapshot',
                  elderId: 1,
                  elderName: 'John',
                  message: 'Server camera snapshot taken for safety monitoring',
                  timestamp: new Date(),
                  priority: 'low',
                  handled: false
                }]);
              }}
              onError={(error) => {
                console.error('Server camera error for John:', error);
                setAlerts(prev => [...prev, {
                  id: Date.now(),
                  type: 'camera_error',
                  elderId: 1,
                  elderName: 'John',
                  message: `Server camera error: ${error}`,
                  timestamp: new Date(),
                  priority: 'high',
                  handled: false
                }]);
              }}
              autoStart={false}
              showControls={true}
              width={480}
              height={360}
            />
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card sx={{ 
              borderRadius: 3, 
              background: 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)',
              height: '300px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center'
            }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: '#2e7d32', mb: 2 }}>
                  📊 Camera Analytics Preview
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Motion Detection: Active<br/>
                  Last Activity: {formatTimeAgo(johnData.lastActivity)}<br/>
                  Current Location: {johnData.location}
                </Typography>
                <Button
                  variant="contained"
                  sx={{ 
                    background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)',
                    mt: 2
                  }}
                  onClick={() => console.log('Taking manual snapshot for John')}
                >
                  📸 Take Snapshot
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
        </Grid>
        
        {/* Camera Analytics Section */}
        <Grid item xs={12}>
          <CameraAnalytics 
            elderId={selectedElder.id} 
            elderName={selectedElder.name}
          />
        </Grid>
      </Grid>
      )}
      
      {!selectedElder && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            Select an elder from the tabs above to view their details
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default CaregiverDashboard;