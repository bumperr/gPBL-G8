import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Alert,
  Paper,
  Avatar,
  Divider,
  Fab
} from '@mui/material';
import {
  Warning,
  Home,
  LocalHospital,
  Phone,
  Settings,
  VolumeUp,
  Brightness6,
  Thermostat,
  Lock,
  LockOpen
} from '@mui/icons-material';
import AudioRecorder from '../components/AudioRecorder';
import apiService from '../services/api';

const ElderInterface = ({ elderInfo, onEmergency }) => {
  const [messages, setMessages] = useState([]);
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [lastResponse, setLastResponse] = useState('');

  // Check server health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiService.checkHealth();
        setServerStatus('connected');
        console.log('Server health:', health);
      } catch (error) {
        setServerStatus('disconnected');
        console.error('Server health check failed:', error);
      }
    };

    checkHealth();
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleMessageSent = (messageData) => {
    const newMessage = {
      id: Date.now(),
      ...messageData
    };
    setMessages(prev => [newMessage, ...prev]);
    
    if (messageData.aiResponse?.response) {
      setLastResponse(messageData.aiResponse.response);
      // Speak the AI response using browser's built-in speech synthesis
      speakText(messageData.aiResponse.response);
    }
    
    // Handle emergency alerts
    if (messageData.isEmergency && onEmergency) {
      onEmergency('Emergency detected and caregivers notified!');
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 1;
      speechSynthesis.speak(utterance);
    }
  };

  const handleEmergencyCall = async () => {
    try {
      await apiService.sendManualEmergency(
        elderInfo?.name || 'Elder User',
        'Emergency assistance requested via button',
        'critical',
        'Home' // This could be enhanced with GPS location
      );
      
      if (onEmergency) {
        onEmergency('Emergency alert sent to caregivers');
      }

      // Also speak the emergency confirmation
      speakText('Emergency alert has been sent to your caregivers. Help is on the way.');
      
    } catch (error) {
      console.error('Emergency alert failed:', error);
    }
  };

  const handleSmartHomeControl = async (device, action, value = null) => {
    try {
      await apiService.controlSmartHome(device, action, value);
      const message = `${device} ${action}${value ? ` to ${value}` : ''}`;
      speakText(`${message} completed`);
    } catch (error) {
      console.error('Smart home control failed:', error);
    }
  };

  const quickActions = [
    {
      label: 'Turn on Lights',
      icon: <Brightness6 />,
      action: () => handleSmartHomeControl('lights', 'turn_on'),
      color: '#FFC107'
    },
    {
      label: 'Set Temperature',
      icon: <Thermostat />,
      action: () => handleSmartHomeControl('thermostat', 'set_temperature', 72),
      color: '#FF5722'
    },
    {
      label: 'Lock Doors',
      icon: <Lock />,
      action: () => handleSmartHomeControl('doors', 'lock'),
      color: '#795548'
    },
    {
      label: 'Call Family',
      icon: <Phone />,
      action: () => speakText('Calling your family now'),
      color: '#4CAF50'
    }
  ];

  return (
    <Container maxWidth="md" sx={{ py: 2 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: '#2196F3', width: 56, height: 56 }}>
            {elderInfo?.name?.charAt(0) || 'E'}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h5" fontWeight="bold">
              Hello, {elderInfo?.name || 'Elder User'}!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Status: {serverStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
            </Typography>
          </Box>
          
          <Fab
            color="error"
            size="large"
            onClick={handleEmergencyCall}
            sx={{ 
              backgroundColor: '#f44336',
              '&:hover': { backgroundColor: '#d32f2f' }
            }}
          >
            <Warning fontSize="large" />
          </Fab>
        </Box>
      </Paper>

      {serverStatus === 'disconnected' && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Unable to connect to smart home server. Some features may not work.
        </Alert>
      )}

      {/* Voice Assistant */}
      <AudioRecorder
        onMessageSent={handleMessageSent}
        elderInfo={elderInfo}
      />

      {/* Last AI Response */}
      {lastResponse && (
        <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <VolumeUp color="primary" />
            Assistant Response
          </Typography>
          <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
            {lastResponse}
          </Typography>
        </Paper>
      )}

      {/* Quick Actions */}
      <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          {quickActions.map((action, index) => (
            <Grid item xs={6} sm={3} key={index}>
              <Card 
                sx={{ 
                  textAlign: 'center', 
                  cursor: 'pointer',
                  borderRadius: 3,
                  '&:hover': { 
                    transform: 'translateY(-2px)',
                    boxShadow: 4
                  },
                  transition: 'all 0.2s'
                }}
                onClick={action.action}
              >
                <CardContent>
                  <Box 
                    sx={{ 
                      color: action.color, 
                      mb: 1,
                      '& svg': { fontSize: '2.5rem' }
                    }}
                  >
                    {action.icon}
                  </Box>
                  <Typography variant="body2" fontWeight="bold">
                    {action.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Recent Messages */}
      {messages.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Messages
          </Typography>
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {messages.map((message) => (
              <Box key={message.id} sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {new Date(message.timestamp).toLocaleTimeString()} 
                  {message.isEmergency && ' 🚨 EMERGENCY'}
                </Typography>
                
                {message.type === 'voice' ? (
                  <>
                    <Typography variant="body1" fontWeight="bold">
                      🎤 You said:
                    </Typography>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        ml: 2, 
                        p: 1, 
                        backgroundColor: '#e3f2fd', 
                        borderRadius: 1,
                        border: '1px solid #2196f3'
                      }}
                    >
                      "{message.transcription?.text || 'Audio processed'}"
                    </Typography>
                    
                    {message.aiResponse?.response && (
                      <>
                        <Typography variant="body1" fontWeight="bold" sx={{ mt: 1 }}>
                          🤖 Assistant replied:
                        </Typography>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            ml: 2,
                            mt: 1, 
                            p: 1, 
                            backgroundColor: '#f3e5f5', 
                            borderRadius: 1,
                            border: '1px solid #9c27b0'
                          }}
                        >
                          {message.aiResponse.response}
                        </Typography>
                      </>
                    )}
                    
                    {message.emergencyAlert && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        Emergency Alert Sent: {message.emergencyAlert.message}
                      </Alert>
                    )}
                  </>
                ) : (
                  <Typography variant="body1">
                    {message.content}
                  </Typography>
                )}
                
                <Divider sx={{ mt: 1 }} />
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default ElderInterface;