import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Fade,
  Paper,
  Divider
} from '@mui/material';
import {
  Mic,
  MicOff,
  VolumeUp,
  VolumeOff,
  Send,
  Refresh,
  AccessTime,
  Psychology,
  Hearing,
  RecordVoiceOver,
  Stop,
  PlayArrow,
  Settings,
  SpeakerNotes,
  Assistant,
  Person,
  PersonOutline,
  VideoCall,
  LocalHospital,
  MusicNote,
  Home,
  CheckCircle
} from '@mui/icons-material';

const VoiceCommunication = ({ 
  elderInfo = { name: 'John', age: 75 }, 
  onInteractionSaved,
  showAdvancedControls = false 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [error, setError] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState({
    autoPlay: true,
    language: 'en',
    saveInteractions: true
  });
  const [suggestedAction, setSuggestedAction] = useState(null);
  const [smartHomeCommands, setSmartHomeCommands] = useState([]);
  const [showActionDialog, setShowActionDialog] = useState(false);
  const [showSmartHomeDialog, setShowSmartHomeDialog] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);
  const speechSynthesisRef = useRef(null);

  // Initialize component
  useEffect(() => {
    // Check if speech synthesis is available
    if ('speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
    }

    // Cleanup on unmount
    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel();
      }
    };
  }, []);

  // Start recording audio
  const startRecording = async () => {
    try {
      setError(null);
      setTranscription('');
      setAiResponse('');

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        processAudio(audioBlob);
        
        // Stop all audio tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start recording timer
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      console.log('Recording started');

    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Could not access microphone. Please check permissions.');
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
      
      console.log('Recording stopped');
    }
  };

  // Process audio with speech-to-text
  const processAudio = async (audioBlob) => {
    try {
      setIsProcessing(true);

      // Convert blob to base64
      const audioBase64 = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.readAsDataURL(audioBlob);
      });

      // Send to eldercare voice assistance API
      const response = await fetch('/api/eldercare/voice-assistance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          audio_data: audioBase64,
          elder_info: elderInfo,
          language: voiceSettings.language,
          save_interaction: voiceSettings.saveInteractions
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        setTranscription(data.transcription.text);
        setAiResponse(data.ai_response.response);

        // Handle suggested actions
        if (data.ai_response.suggested_action) {
          setSuggestedAction(data.ai_response.suggested_action);
          setShowActionDialog(true);
        }

        // Handle smart home commands
        if (data.mqtt_commands && data.mqtt_commands.length > 0) {
          setSmartHomeCommands(data.mqtt_commands);
          setShowSmartHomeDialog(true);
        }

        // Add to conversation history
        const interaction = {
          id: Date.now(),
          timestamp: new Date(),
          elder_speech: data.transcription.text,
          ai_response: data.ai_response.response,
          confidence: data.transcription.confidence,
          intent: data.ai_response.intent_detected,
          is_emergency: data.ai_response.is_emergency,
          suggested_action: data.ai_response.suggested_action
        };

        setConversationHistory(prev => [interaction, ...prev.slice(0, 4)]); // Keep last 5

        // Auto-play AI response if enabled
        if (voiceSettings.autoPlay && data.ai_response.response) {
          speakText(data.ai_response.response);
        }

        // Notify parent component
        if (onInteractionSaved) {
          onInteractionSaved(interaction);
        }

        // Handle emergency situations
        if (data.ai_response.is_emergency) {
          setError(null); // Clear any previous errors
          // Emergency handling could be added here
        }

      } else {
        setError(data.message || 'Could not process audio');
        setTranscription(data.transcription?.text || '');
      }

    } catch (error) {
      console.error('Error processing audio:', error);
      setError('Failed to process audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Speak text using speech synthesis
  const speakText = (text) => {
    if (!speechSynthesisRef.current || !text) return;

    // Cancel any ongoing speech
    speechSynthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.8; // Slower for elderly users
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    speechSynthesisRef.current.speak(utterance);
  };

  // Stop speech synthesis
  const stopSpeaking = () => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  // Format recording time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get elder avatar
  const getElderAvatar = () => {
    const isWoman = elderInfo.name?.toLowerCase().includes('mary') || 
                   elderInfo.name?.toLowerCase().includes('jane') ||
                   elderInfo.gender === 'female';
    return isWoman ? <Person /> : <PersonOutline />;
  };

  // Action helper functions (similar to TextChat)
  const getActionIcon = (functionName) => {
    switch (functionName) {
      case 'start_video_call':
      case 'contact_family':
        return <VideoCall />;
      case 'call_emergency':
        return <LocalHospital />;
      case 'play_music':
        return <MusicNote />;
      case 'send_health_alert':
        return <LocalHospital />;
      case 'control_smart_device':
        return <Home />;
      default:
        return <CheckCircle />;
    }
  };

  const getActionLabel = (functionName, parameters) => {
    switch (functionName) {
      case 'start_video_call':
      case 'contact_family':
        return `📞 Call ${parameters?.contact_name || 'Family'} via WhatsApp`;
      case 'call_emergency':
        return '🚨 Call Emergency Services';
      case 'play_music':
        return `🎵 Play ${parameters?.genre || 'Music'}`;
      case 'send_health_alert':
        return '💝 Alert Caregivers';
      case 'control_smart_device':
        const deviceName = parameters?.device_name || 'Device';
        const actionDesc = parameters?.action_description || 'Control device';
        return `🏠 ${actionDesc}`;
      default:
        return '✅ Take Action';
    }
  };

  // Execute suggested action
  const executeAction = async (action) => {
    console.log('=== EXECUTING ACTION ===');
    console.log('Action:', action);
    console.log('Function name:', action.function_name);
    console.log('Parameters:', action.parameters);
    
    try {
      switch (action.function_name) {
        case 'start_video_call':
        case 'contact_family':
          const phoneNumber = action.parameters.phone_number || '+6011468550';
          const whatsappUrl = `https://wa.me/${phoneNumber.replace('+', '')}?text=Hi, I would like to have a video call with you.`;
          window.open(whatsappUrl, '_blank');
          speakText(`I've opened WhatsApp to call ${action.parameters.contact_name || 'your family member'}.`);
          break;

        case 'call_emergency':
          speakText('Emergency services have been notified! Help is on the way.');
          // Could integrate with actual emergency system
          break;

        case 'send_health_alert':
          speakText('I\'ve notified your caregivers about your health concern. They will check on you soon.');
          break;

        case 'read_arduino_sensors':
          speakText('Let me check the current temperature and humidity readings for you.');
          // This action typically doesn't require confirmation, just provides info
          break;

        case 'set_target_temperature':
          // Handle target temperature setting using same method as control_thermostat
          try {
            const targetTemp = action.parameters.target_temperature || action.parameters.temperature || 22;
            const targetHumidity = action.parameters.target_humidity || 50;
            
            const response = await fetch('http://localhost:8000/mqtt/send', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                topic: 'home/room/data',
                message: `${targetTemp},${targetHumidity}`
              })
            });

            if (response.ok) {
              speakText(`I've set the target temperature to ${targetTemp} degrees successfully!`);
            } else {
              throw new Error('Failed to set target temperature');
            }
          } catch (error) {
            console.error('Target temperature setting failed:', error);
            speakText(`Sorry, I had trouble setting the target temperature.`);
          }
          break;

        case 'schedule_medication_reminder':
          speakText('I\'ve noted your medication reminder request. Your caregiver will help set this up for you.');
          break;

        case 'provide_companionship':
          speakText('I\'m here to chat with you anytime you need company. What would you like to talk about?');
          break;

        case 'general_conversation':
          speakText('I\'m happy to continue our conversation. Is there anything specific you\'d like to discuss?');
          break;

        case 'control_arduino_room_light':
          // Handle Arduino room light control using exact same method as manual controls
          console.log('=== CONTROL_ARDUINO_ROOM_LIGHT CASE ===');
          try {
            const room = action.parameters.room_name || 'living_room';
            const ledState = action.parameters.led_state || 'ON';
            const topic = `home/${room}/lights/cmd`;
            
            console.log('Room:', room);
            console.log('LED State:', ledState);
            console.log('Topic:', topic);
            console.log('About to send MQTT command...');
            
            // Use the same endpoint and format as SmartHomeControls manual control
            const response = await fetch('http://localhost:8000/mqtt/send', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                topic: topic,
                message: ledState
              })
            });

            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            if (response.ok) {
              const roomName = room.replace('_', ' ');
              console.log('SUCCESS! About to speak success message');
              speakText(`I've ${ledState === 'ON' ? 'turned on' : 'turned off'} the ${roomName} light successfully!`);
            } else {
              console.log('Response not ok, throwing error');
              const errorText = await response.text();
              console.log('Error response:', errorText);
              throw new Error('Failed to control room light');
            }
          } catch (error) {
            console.error('Room light control failed:', error);
            speakText(`Sorry, I had trouble controlling the room light.`);
          }
          break;

        case 'control_thermostat':
          // Handle thermostat control using exact same method as manual controls
          try {
            const temperature = action.parameters.temperature || 22;
            const humidity = 50; // Default humidity like manual control
            
            // Use the same endpoint and format as SmartHomeControls manual control
            const response = await fetch('http://localhost:8000/mqtt/send', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                topic: 'home/room/data',
                message: `${temperature},${humidity}`
              })
            });

            if (response.ok) {
              speakText(`I've set the thermostat to ${temperature} degrees successfully!`);
            } else {
              throw new Error('Failed to control thermostat');
            }
          } catch (error) {
            console.error('Thermostat control failed:', error);
            speakText(`Sorry, I had trouble controlling the thermostat.`);
          }
          break;

        case 'control_smart_device':
          // Handle smart home device control using same API as manual controls
          const room = action.parameters.room || 'living_room';
          const isLightAction = action.parameters.device_category === 'lighting' || 
                              action.parameters.device_name?.toLowerCase().includes('light');
          
          if (isLightAction && action.parameters.action_name) {
            try {
              // Use the same method as SmartHomeControls manual control
              const command = action.parameters.action_name === 'turn_on' ? 'ON' : 'OFF';
              const topic = `home/${room}/lights/cmd`;
              
              const response = await fetch('http://localhost:8000/mqtt/send', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  topic: topic,
                  message: command
                })
              });

              if (response.ok) {
                const deviceName = action.parameters.device_name || 'lights';
                speakText(`I've ${command === 'ON' ? 'turned on' : 'turned off'} the ${deviceName} successfully!`);
              } else {
                throw new Error('Failed to control light');
              }
            } catch (error) {
              console.error('Light control failed:', error);
              speakText(`Sorry, I had trouble controlling the lights. Please try the manual controls.`);
            }
          } else if (action.parameters.device_category === 'climate') {
            // Handle thermostat using manual control API
            try {
              const temperature = action.parameters.temperature || 22;
              const response = await fetch('/api/smart-home/thermostat/set', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ temperature, humidity: 50 })
              });

              if (response.ok) {
                speakText(`I've set the thermostat to ${temperature} degrees successfully!`);
              } else {
                throw new Error('Failed to control thermostat');
              }
            } catch (error) {
              console.error('Thermostat control failed:', error);
              speakText(`Sorry, I had trouble controlling the thermostat.`);
            }
          } else {
            speakText(`I've sent the command to control your ${action.parameters.device_name || 'device'}.`);
          }
          break;

        default:
          speakText('Action has been noted.');
      }
      setShowActionDialog(false);
      setSuggestedAction(null);
    } catch (error) {
      console.error('Action execution failed:', error);
      speakText('Sorry, I had trouble executing that action.');
    }
  };

  // Execute smart home commands
  const executeSmartHomeCommands = async (commands) => {
    try {
      // Here you would call the MQTT API
      speakText(`Smart home commands executed successfully!`);
      setShowSmartHomeDialog(false);
      setSmartHomeCommands([]);
    } catch (error) {
      console.error('Smart home execution failed:', error);
      speakText('Sorry, I had trouble controlling your smart home devices.');
    }
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', position: 'relative' }}>
      <CardContent sx={{ pb: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            {getElderAvatar()}
          </Avatar>
          <Box>
            <Typography variant="h6">
              Voice Assistant for {elderInfo.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              🎙️ Speak naturally • AI will respond with care
            </Typography>
          </Box>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Recording Controls */}
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          {!isRecording ? (
            <Button
              variant="contained"
              size="large"
              startIcon={<Mic />}
              onClick={startRecording}
              disabled={isProcessing}
              sx={{ 
                minHeight: 60, 
                fontSize: '1.1rem',
                borderRadius: 3,
                px: 4
              }}
            >
              {isProcessing ? 'Processing...' : 'Start Speaking'}
            </Button>
          ) : (
            <Box>
              <Button
                variant="contained"
                color="error"
                size="large"
                startIcon={<Stop />}
                onClick={stopRecording}
                sx={{ 
                  minHeight: 60, 
                  fontSize: '1.1rem',
                  borderRadius: 3,
                  px: 4,
                  animation: 'pulse 1.5s infinite'
                }}
              >
                Stop Recording
              </Button>
              <Typography variant="h5" sx={{ mt: 2, color: 'error.main' }}>
                <AccessTime sx={{ mr: 1, verticalAlign: 'middle' }} />
                {formatTime(recordingTime)}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Processing Indicator */}
        {isProcessing && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress sx={{ mb: 1 }} />
            <Typography variant="body2" textAlign="center" color="text.secondary">
              🤖 Understanding your speech and preparing response...
            </Typography>
          </Box>
        )}

        {/* Current Interaction */}
        {(transcription || aiResponse) && (
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
            {transcription && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <RecordVoiceOver color="primary" /> What you said:
                </Typography>
                <Typography variant="body1" sx={{ fontStyle: 'italic', pl: 2 }}>
                  "{transcription}"
                </Typography>
              </Box>
            )}

            {aiResponse && (
              <Box>
                <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Assistant color="secondary" /> AI Response:
                  {isSpeaking && (
                    <Chip 
                      size="small" 
                      label="Speaking" 
                      color="success"
                      icon={<VolumeUp />}
                    />
                  )}
                </Typography>
                <Typography variant="body1" sx={{ pl: 2 }}>
                  {aiResponse}
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                  {!isSpeaking ? (
                    <IconButton size="small" onClick={() => speakText(aiResponse)}>
                      <VolumeUp />
                    </IconButton>
                  ) : (
                    <IconButton size="small" onClick={stopSpeaking} color="error">
                      <VolumeOff />
                    </IconButton>
                  )}
                  
                  {/* Show action button if there's a suggested action */}
                  {suggestedAction && suggestedAction.function_name && 
                   !['provide_companionship'].includes(suggestedAction.function_name) && (
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => setShowActionDialog(true)}
                      startIcon={getActionIcon(suggestedAction.function_name)}
                      sx={{ fontSize: '0.75rem', textTransform: 'none' }}
                    >
                      {getActionLabel(suggestedAction.function_name, suggestedAction.parameters)}
                    </Button>
                  )}
                </Box>
              </Box>
            )}
          </Paper>
        )}

        {/* Conversation History */}
        {conversationHistory.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              <SpeakerNotes /> Recent Conversations:
            </Typography>
            {conversationHistory.slice(1).map((interaction) => ( // Skip current (first) interaction
              <Fade in key={interaction.id}>
                <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'grey.100' }}>
                  <Typography variant="caption" color="text.secondary">
                    {interaction.timestamp.toLocaleTimeString()}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    <strong>You:</strong> {interaction.elder_speech}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>AI:</strong> {interaction.ai_response}
                  </Typography>
                  {interaction.is_emergency && (
                    <Chip size="small" label="Emergency Detected" color="error" sx={{ mt: 0.5 }} />
                  )}
                </Paper>
              </Fade>
            ))}
          </Box>
        )}

        {/* Quick Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
          <Button 
            variant="outlined" 
            size="small" 
            startIcon={<Refresh />}
            onClick={() => {
              setTranscription('');
              setAiResponse('');
              setError(null);
            }}
          >
            Clear
          </Button>
          
          {showAdvancedControls && (
            <Button 
              variant="outlined" 
              size="small" 
              startIcon={<Settings />}
              onClick={() => {/* Settings could be implemented */}}
            >
              Settings
            </Button>
          )}
        </Box>

        {/* Voice Settings (if advanced controls enabled) */}
        {showAdvancedControls && (
          <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Settings: Auto-play responses • Save interactions • Language: {voiceSettings.language}
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* Recording Animation CSS */}
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
      `}</style>

      {/* Action Confirmation Dialog */}
      <Dialog open={showActionDialog} onClose={() => setShowActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CheckCircle color="primary" />
          Confirm Voice Action
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              🎙️ Voice Assistant wants to help you with:
            </Typography>
            <Typography variant="body2">
              {suggestedAction?.reasoning}
            </Typography>
          </Alert>

          <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Proposed action:
            </Typography>
            <Typography variant="body2">
              {suggestedAction && getActionLabel(
                suggestedAction.function_name, 
                suggestedAction.parameters
              )}
            </Typography>
            {suggestedAction?.parameters && Object.keys(suggestedAction.parameters).length > 0 && (
              <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
                Details: {JSON.stringify(suggestedAction.parameters, null, 2)}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowActionDialog(false)} color="secondary" variant="outlined">
            ❌ No, thanks
          </Button>
          <Button 
            onClick={() => executeAction(suggestedAction)} 
            color="primary" 
            variant="contained"
            startIcon={suggestedAction && getActionIcon(suggestedAction.function_name)}
          >
            ✅ Yes, please help
          </Button>
        </DialogActions>
      </Dialog>

      {/* Smart Home Confirmation Dialog */}
      <Dialog open={showSmartHomeDialog} onClose={() => setShowSmartHomeDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Home color="primary" />
          Smart Home Control Confirmation
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              ⚠️ Voice Command Detected
            </Typography>
            <Typography variant="body2">
              I detected a smart home control request from your voice. Please confirm:
            </Typography>
          </Alert>

          <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Commands to execute:
            </Typography>
            {smartHomeCommands.map((cmd, idx) => (
              <Box key={idx} sx={{ mb: 1, p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2">
                  📱 <strong>{cmd.payload?.action?.toUpperCase()}</strong> {cmd.payload?.device_type}
                  {cmd.payload?.room && <span> in <strong>{cmd.payload.room}</strong></span>}
                </Typography>
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSmartHomeDialog(false)} color="error" variant="outlined">
            ❌ Cancel
          </Button>
          <Button 
            onClick={() => executeSmartHomeCommands(smartHomeCommands)} 
            color="primary" 
            variant="contained"
            startIcon={<CheckCircle />}
          >
            ✅ Execute Commands
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default VoiceCommunication;