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
  Fab,
  Tabs,
  Tab,
  Slider,
  Chip
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
  LockOpen,
  Mic,
  Chat,
  Lightbulb,
  Kitchen,
  Bed,
  Chair
} from '@mui/icons-material';
import TextChat from '../components/TextChat';
import VoiceCommunication from '../components/VoiceCommunication';
import SmartHomeControls from '../components/SmartHomeControls';
import apiService from '../services/api';

const ElderInterface = ({ elderInfo, onEmergency }) => {
  const [messages, setMessages] = useState([]);
  const [serverStatus, setServerStatus] = useState('disconnected');
  const [lastResponse, setLastResponse] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [communicationMode, setCommunicationMode] = useState(0); // 0: text chat, 1: voice
  const [intentDetections, setIntentDetections] = useState([]);
  

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

  // WebSocket connection for real-time MQTT updates (same as caregiver dashboard)
  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;
    
    const connectWebSocket = () => {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/smart-home`;
      console.log('Elder interface: Attempting WebSocket connection to:', wsUrl);
      
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('Elder interface: WebSocket connected for smart home updates');
        // Send a ping to verify connection
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Elder interface: WebSocket message received:', data);
        
        // Note: Smart home state is now managed by SmartHomeControls component
        // This WebSocket is kept for general elder interface notifications
        if (data.type === 'pong') {
          // Keep-alive response
          return;
        }
      } catch (error) {
        console.error('Elder interface: Error processing WebSocket message:', error);
      }
    };
    
      ws.onerror = (error) => {
        console.error('Elder interface: WebSocket error:', error);
        console.error('Elder interface: WebSocket connection failed to:', wsUrl);
      };
      
      ws.onclose = (event) => {
        console.log('Elder interface: WebSocket disconnected');
        console.log('Elder interface: WebSocket close event:', { code: event.code, reason: event.reason, wasClean: event.wasClean });
        
        // Only attempt reconnect for specific error codes, but limit attempts
        if (!event.wasClean && event.code === 1006) {
          console.warn('Elder interface: WebSocket server appears unavailable. App will continue without real-time updates.');
          // Don't attempt reconnect for now to avoid spam
        } else if (!event.wasClean && event.code !== 1000) {
          console.warn('Elder interface: WebSocket connection closed unexpectedly, attempting reconnect in 10 seconds...');
          reconnectTimeout = setTimeout(() => {
            console.log('Elder interface: Attempting WebSocket reconnection...');
            connectWebSocket();
          }, 10000); // Increased to 10 seconds
        }
      };
    };
    
    // Initial connection
    connectWebSocket();
    
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close();
      }
    };
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
      
      // Enhanced voice settings for warm, vibrant, happy tone
      utterance.rate = 0.85; // Slightly faster but still clear
      utterance.pitch = 1.2; // Higher pitch for friendlier tone
      utterance.volume = 0.9; // Comfortable volume
      
      // Try to select a female voice if available (typically warmer)
      const voices = speechSynthesis.getVoices();
      const preferredVoices = voices.filter(voice => 
        voice.lang.startsWith('en') && 
        (voice.name.toLowerCase().includes('female') || 
         voice.name.toLowerCase().includes('karen') ||
         voice.name.toLowerCase().includes('samantha') ||
         voice.name.toLowerCase().includes('susan') ||
         voice.name.toLowerCase().includes('zira'))
      );
      
      if (preferredVoices.length > 0) {
        utterance.voice = preferredVoices[0];
      }
      
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


  const handleSmartHomeControl = async (device, action, value = null, room = null) => {
    try {
      // Note: Smart home controls now handled by SmartHomeControls component
      // This function is kept for backward compatibility with quick actions
      speakText(`Smart home control: ${device} ${action} - please use the smart home controls panel below for better experience`);
    } catch (error) {
      console.error('Smart home control failed:', error);
      speakText('Please use the smart home controls panel below');
    }
  };

  const handleIntentDetected = (intentData) => {
    // Handle detected intent from text chat
    setIntentDetections(prev => [
      {
        id: Date.now(),
        ...intentData,
        timestamp: new Date()
      },
      ...prev.slice(0, 9) // Keep last 10 detections
    ]);

    // Handle emergency from text chat
    if (intentData.is_emergency && onEmergency) {
      onEmergency(`Emergency detected via text: ${intentData.elder_message}`);
    }
  };

  const handleVoiceInteractionSaved = (interaction) => {
    // Handle voice interaction result
    const voiceMessage = {
      id: interaction.id,
      type: 'voice',
      timestamp: interaction.timestamp,
      transcription: { text: interaction.elder_speech },
      aiResponse: { response: interaction.ai_response },
      isEmergency: interaction.is_emergency
    };

    setMessages(prev => [voiceMessage, ...prev]);
    
    if (interaction.ai_response) {
      setLastResponse(interaction.ai_response);
      // Automatic speech already handled by VoiceCommunication component
    }
    
    // Handle emergency alerts from voice
    if (interaction.is_emergency && onEmergency) {
      onEmergency(`Emergency detected via voice: ${interaction.elder_speech}`);
    }

    // Add to intent detections if intent was detected
    if (interaction.intent) {
      setIntentDetections(prev => [
        {
          id: interaction.id,
          elder_message: interaction.elder_speech,
          ai_response: {
            intent_detected: interaction.intent,
            confidence_score: interaction.confidence || 0.8,
            response: interaction.ai_response
          },
          is_emergency: interaction.is_emergency,
          timestamp: interaction.timestamp
        },
        ...prev.slice(0, 9)
      ]);
    }
  };

  const quickActions = [
    {
      label: 'Call Sarah',
      icon: <Phone />,
      action: () => {
        const whatsappUrl = `https://wa.me/6011468550?text=Hi Sarah, this is John. Could you give me a call when you're free?`;
        window.open(whatsappUrl, '_blank');
        speakText('Calling Sarah via WhatsApp');
      },
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

      {/* AI Assistant Communication - Text and Voice */}
      <Paper elevation={2} sx={{ borderRadius: 3, mb: 3 }}>
        {/* Communication Mode Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={communicationMode} 
            onChange={(e, newValue) => setCommunicationMode(newValue)}
            variant="fullWidth"
          >
            <Tab 
              label="💬 Text Chat" 
              icon={<Chat />} 
              sx={{ 
                fontSize: '1rem', 
                fontWeight: 'bold',
                minHeight: 64
              }}
            />
            <Tab 
              label="🎤 Voice Talk" 
              icon={<Mic />} 
              sx={{ 
                fontSize: '1rem', 
                fontWeight: 'bold',
                minHeight: 64
              }}
            />
          </Tabs>
        </Box>

        {/* Text Chat Mode */}
        {communicationMode === 0 && (
          <Box sx={{ height: '600px' }}>
            <TextChat
              elderInfo={elderInfo}
              onIntentDetected={handleIntentDetected}
              enableVoiceMessages={true}
              onVoiceMessage={handleMessageSent}
              height="100%"
            />
          </Box>
        )}

        {/* Voice Communication Mode */}
        {communicationMode === 1 && (
          <Box sx={{ p: 2 }}>
            <VoiceCommunication
              elderInfo={elderInfo}
              onInteractionSaved={handleVoiceInteractionSaved}
              showAdvancedControls={false}
            />
          </Box>
        )}
      </Paper>

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

      {/* Smart Home Controls - New Component */}
      <SmartHomeControls 
        elderInfo={elderInfo}
        onSpeakText={speakText}
      />

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

      {/* Latest Intent Detections */}
      {intentDetections.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            🎯 AI Intent Detection & Actions
          </Typography>
          <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
            {intentDetections.slice(0, 3).map((detection) => (
              <Alert 
                key={detection.id}
                severity={
                  detection.ai_response?.intent_detected === 'emergency' ? 'error' :
                  detection.ai_response?.intent_detected === 'health_concern' ? 'warning' :
                  detection.ai_response?.intent_detected === 'loneliness' ? 'info' : 'success'
                }
                sx={{ mb: 1, fontSize: '0.9rem' }}
              >
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    Intent: {detection.ai_response?.intent_detected?.toUpperCase().replace('_', ' ')} 
                    {detection.ai_response?.confidence_score && 
                      ` (${Math.round(detection.ai_response.confidence_score * 100)}% confidence)`
                    }
                  </Typography>
                  {detection.ai_response?.suggested_action && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Suggested Action:</strong> {detection.ai_response.suggested_action.function_name}
                      {detection.ai_response.suggested_action.parameters && 
                        ` with parameters: ${JSON.stringify(detection.ai_response.suggested_action.parameters)}`
                      }
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    {detection.timestamp.toLocaleTimeString()}
                  </Typography>
                </Box>
              </Alert>
            ))}
          </Box>
        </Paper>
      )}

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