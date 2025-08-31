import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Chip,
  Alert,
  IconButton,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Send,
  Psychology,
  SmartToy,
  Person,
  LightbulbOutlined,
  PhotoCamera,
  Image,
  Close,
  Home,
  Warning,
  CheckCircle,
  VideoCall,
  Phone,
  LocalHospital,
  MusicNote,
  People,
  Mic,
  MicOff,
  PlayArrow,
  Pause,
  VolumeUp,
  Download
} from '@mui/icons-material';
import apiService from '../services/api';
import useAudioRecorder from '../hooks/useAudioRecorder';

// Add CSS animations
const styles = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes slideInFromLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
  }
  
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
  }
  
  @keyframes pulse {
    0% { box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3); }
    50% { box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5); }
    100% { box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3); }
  }
`;

// Inject styles
if (!document.querySelector('#chat-animations')) {
  const styleSheet = document.createElement('style');
  styleSheet.id = 'chat-animations';
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}

const TextChat = ({ elderInfo, onIntentDetected, enableVoiceMessages = false, onVoiceMessage, height = '700px' }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [chatType, setChatType] = useState('assistance');
  const [smartHomeDialog, setSmartHomeDialog] = useState({ open: false, commands: [], message: '' });
  const [actionConfirmDialog, setActionConfirmDialog] = useState({ open: false, action: null, message: '' });
  const [isTTSEnabled, setIsTTSEnabled] = useState(true);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Voice recording functionality
  const audioRecorder = useAudioRecorder();
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);

  const scrollToBottom = () => {
    // Only scroll if the messagesEndRef is within the messages container
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: "smooth",
        block: "end",
        inline: "nearest"
      });
    }
  };

  useEffect(() => {
    // Add a small delay to ensure DOM is updated
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 100);
    return () => clearTimeout(timer);
  }, [messages]);

  // Add initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        id: 0,
        type: 'ai',
        content: `Hello ${elderInfo?.name || 'John'}! 👋 I'm your AI companion, here to help you with:

🏠 **Smart Home Control**: "Turn on living room lights", "Set temperature to 72 degrees", "Lock the door"

❤️ **Health & Wellness**: I can listen to your concerns, provide companionship, and detect emergencies

💬 **General Chat**: Ask me anything or just have a friendly conversation

🚨 **Emergency Support**: I can detect urgent situations and alert your caregivers Sarah

📸 **Image Analysis**: Upload photos and I'll help you understand what's in them

What would you like to talk about today?`,
        timestamp: new Date(),
        isWelcome: true
      };
      setMessages([welcomeMessage]);
    }
  }, [elderInfo?.name]);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      image: imagePreview,
      hasImage: !!selectedImage
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    const currentImage = selectedImage;
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (currentImage) {
        // Send with image using FormData
        const formData = new FormData();
        formData.append('message', currentMessage);
        formData.append('chat_type', chatType);
        formData.append('elder_info', JSON.stringify(elderInfo));
        formData.append('image', currentImage);

        response = await apiService.chatWithImage(formData);
        removeImage(); // Clear image after sending
      } else {
        // Send text-only message to eldercare text assistance
        response = await apiService.processElderText(currentMessage, elderInfo);
      }
      
      // Handle eldercare endpoint response structure
      const aiResponse = response.ai_response || response;
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse.response,
        timestamp: new Date(),
        chatType: response.chat_type || aiResponse.chat_type,
        hasImage: response.has_image || aiResponse.has_image,
        mqttCommands: response.mqtt_commands || aiResponse.mqtt_commands || [],
        isEmergency: response.is_emergency || aiResponse.is_emergency,
        intentDetected: aiResponse.intent_detected,
        suggestedAction: aiResponse.suggested_action,
        confidenceScore: aiResponse.confidence_score,
        mentalHealthAssessment: aiResponse.mental_health_assessment
      };

      setMessages(prev => [...prev, aiMessage]);

      // Handle smart home commands with confirmation
      const smartHomeCommands = response.mqtt_commands || aiResponse.mqtt_commands || [];
      if (smartHomeCommands.length > 0) {
        setSmartHomeDialog({
          open: true,
          commands: smartHomeCommands,
          message: currentMessage
        });
      }

      // Notify parent component about detected intent
      if (aiResponse.intent_detected && onIntentDetected) {
        onIntentDetected(aiResponse);
      }

      // Speak the response if TTS is enabled
      if ('speechSynthesis' in window && aiResponse.response && isTTSEnabled) {
        const utterance = new SpeechSynthesisUtterance(aiResponse.response);
        
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

    } catch (error) {
      console.error('Text chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I'm sorry, I'm having trouble understanding right now. Could you please try again?",
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const getIntentColor = (intent) => {
    const colors = {
      'emergency': '#d32f2f',
      'health_concern': '#f57c00',
      'loneliness': '#7b1fa2',
      'request_help': '#388e3c',
      'conversation': '#2e7d32',
      'smart_home': '#388e3c',
      'medication': '#c2185b'
    };
    return colors[intent] || '#4caf50';
  };

  const executeSmartHomeCommands = async (commands) => {
    try {
      for (const command of commands) {
        await apiService.sendMQTTMessage(command.topic, command.payload);
      }
      
      const confirmationMessage = {
        id: Date.now() + Math.random(),
        type: 'ai',
        content: `✅ Smart home commands executed successfully! ${commands.map(cmd => 
          `${cmd.payload.action} ${cmd.payload.device_type}${cmd.payload.room ? ' in ' + cmd.payload.room : ''}`
        ).join(', ')}`,
        timestamp: new Date(),
        isConfirmation: true
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
      setSmartHomeDialog({ open: false, commands: [], message: '' });
    } catch (error) {
      console.error('Smart home execution failed:', error);
      const errorMessage = {
        id: Date.now() + Math.random(),
        type: 'ai',
        content: `❌ Sorry, I couldn't execute the smart home commands. Please try again or contact support.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const cancelSmartHomeCommands = () => {
    setSmartHomeDialog({ open: false, commands: [], message: '' });
  };

  const handleActionConfirmation = (suggestedAction, messageContent) => {
    setActionConfirmDialog({
      open: true,
      action: suggestedAction,
      message: messageContent
    });
  };

  const confirmAction = async () => {
    const action = actionConfirmDialog.action;
    if (action) {
      await executeAction(action.function_name, action.parameters);
      setActionConfirmDialog({ open: false, action: null, message: '' });
    }
  };

  const cancelAction = () => {
    setActionConfirmDialog({ open: false, action: null, message: '' });
  };

  const executeAction = async (action, parameters) => {
    try {
      switch (action) {
        case 'start_video_call':
        case 'contact_family':
          const phoneNumber = parameters.phone_number || '+6011468550'; // Default family number
          const whatsappUrl = `https://wa.me/${phoneNumber.replace('+', '')}?text=Hi, I would like to have a video call with you.`;
          window.open(whatsappUrl, '_blank');
          
          const callMessage = {
            id: Date.now() + Math.random(),
            type: 'ai',
            content: `📞 I've opened WhatsApp to call ${parameters.contact_name || 'your family member'} at ${phoneNumber}. You can now start a video call!`,
            timestamp: new Date(),
            isActionResult: true
          };
          setMessages(prev => [...prev, callMessage]);
          break;

        case 'call_emergency':
          const emergencyMessage = {
            id: Date.now() + Math.random(),
            type: 'ai',
            content: `🚨 Emergency services have been notified! Help is on the way. Please stay calm and stay on the line if you can.`,
            timestamp: new Date(),
            isActionResult: true,
            isEmergency: true
          };
          setMessages(prev => [...prev, emergencyMessage]);
          
          // Also trigger emergency alert through API
          if (elderInfo) {
            await apiService.sendManualEmergency(
              elderInfo.name,
              parameters.reason || 'Emergency assistance requested',
              'high',
              parameters.location || 'Home'
            );
          }
          break;

        case 'play_music':
          const musicMessage = {
            id: Date.now() + Math.random(),
            type: 'ai',
            content: `🎵 I would help you play ${parameters.genre || 'relaxing'} music, but I need to be connected to your smart speaker. For now, you can ask your family to help set up music streaming.`,
            timestamp: new Date(),
            isActionResult: true
          };
          setMessages(prev => [...prev, musicMessage]);
          break;

        case 'send_health_alert':
          const healthMessage = {
            id: Date.now() + Math.random(),
            type: 'ai',
            content: `💝 I've noted your health concern and will inform your caregivers. Please don't hesitate to call emergency services if you feel worse.`,
            timestamp: new Date(),
            isActionResult: true
          };
          setMessages(prev => [...prev, healthMessage]);
          break;

        case 'control_smart_device':
          // Handle smart home device control with database info
          const deviceName = parameters.device_name || parameters.device || 'device';
          const room = parameters.room || '';
          const actionDescription = parameters.action_description || 'control device';
          const mqttTopic = parameters.mqtt_topic;
          const mqttPayload = parameters.mqtt_payload;
          
          try {
            // Send MQTT command through API using database info
            await apiService.sendMQTTMessage(mqttTopic, mqttPayload);
            
            const smartHomeMessage = {
              id: Date.now() + Math.random(),
              type: 'ai',
              content: `✅ Perfect! I've successfully ${actionDescription.toLowerCase()} ${room ? `in the ${room.replace('_', ' ')}` : ''}. The command has been sent to your smart home system.`,
              timestamp: new Date(),
              isActionResult: true,
              deviceInfo: {
                name: deviceName,
                room: room,
                category: parameters.device_category,
                action: parameters.action_name
              }
            };
            setMessages(prev => [...prev, smartHomeMessage]);
            
          } catch (mqttError) {
            console.error('Smart home control failed:', mqttError);
            const errorMessage = {
              id: Date.now() + Math.random(),
              type: 'ai',
              content: `❌ I had trouble controlling the ${deviceName}${room ? ` in the ${room.replace('_', ' ')}` : ''}. Please check if your smart home system is connected and try again.`,
              timestamp: new Date(),
              isError: true,
              deviceInfo: {
                name: deviceName,
                room: room,
                error: mqttError.message || 'Connection failed'
              }
            };
            setMessages(prev => [...prev, errorMessage]);
          }
          break;

        default:
          console.log('Action not implemented:', action);
      }
    } catch (error) {
      console.error('Action execution failed:', error);
      const errorMessage = {
        id: Date.now() + Math.random(),
        type: 'ai',
        content: `❌ Sorry, I couldn't complete that action right now. Please try again or contact support.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle voice message recording and processing
  const handleVoiceMessage = async () => {
    if (audioRecorder.isRecording) {
      // Stop recording
      audioRecorder.stopRecording();
      
      if (audioRecorder.audioBlob) {
        setIsProcessingVoice(true);
        
        try {
          // Store audio locally with a unique filename
          const timestamp = new Date().toISOString().replace(/[:]/g, '-');
          const audioFileName = `voice_message_${timestamp}.webm`;
          
          // Create a local URL for the audio blob
          const localAudioUrl = URL.createObjectURL(audioRecorder.audioBlob);
          
          // Store audio blob in localStorage (if small enough) or just keep the URL
          const audioData = {
            fileName: audioFileName,
            blob: audioRecorder.audioBlob,
            url: localAudioUrl,
            timestamp: timestamp,
            duration: audioRecorder.durationSeconds
          };

          // Add voice message to chat immediately
          const voiceMessage = {
            id: Date.now(),
            type: 'user',
            content: '🎤 Voice message (stored locally)',
            isVoice: true,
            audioUrl: localAudioUrl,
            duration: audioRecorder.durationSeconds,
            timestamp: new Date(),
            audioData: audioData
          };
          
          setMessages(prev => [...prev, voiceMessage]);

          // Optionally process voice with AI (can be disabled for local storage only)
          try {
            // Convert audio to base64 for API
            const base64Audio = await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result.split(',')[1]);
              reader.onerror = reject;
              reader.readAsDataURL(audioRecorder.audioBlob);
            });

            const response = await apiService.processElderSpeech(base64Audio, elderInfo);
          
            // Add transcription and AI response
            const transcriptionMessage = {
              id: Date.now() + 1,
              type: 'transcription',
              content: `"${response.transcription?.text || 'Audio processed'}"`,
              originalVoiceId: voiceMessage.id
            };

            const aiMessage = {
              id: Date.now() + 2,
              type: 'ai',
              content: response.ai_response?.response || 'I heard your message.',
              intentDetected: response.ai_response?.intent_detected,
              suggestedAction: response.ai_response?.suggested_action,
              timestamp: new Date()
            };

            setMessages(prev => [...prev, transcriptionMessage, aiMessage]);
            
            // Handle intents and actions like regular text chat
            if (response.ai_response && onIntentDetected) {
              onIntentDetected(response.ai_response);
            }

            // Call the voice message callback
            if (onVoiceMessage) {
              onVoiceMessage({
                type: 'voice',
                transcription: response.transcription,
                aiResponse: response.ai_response,
                timestamp: new Date(),
                audioBlob: audioRecorder.audioBlob,
                audioData: audioData
              });
            }

            // Handle smart home commands
            if (response.mqtt_commands?.length > 0) {
              setSmartHomeDialog({
                open: true,
                commands: response.mqtt_commands,
                message: response.transcription?.text || 'Voice command'
              });
            }

          } catch (aiError) {
            // AI processing failed, but audio is still stored locally
            console.warn('AI processing failed, but voice message saved locally:', aiError);
            const warningMessage = {
              id: Date.now() + 1,
              type: 'ai',
              content: "Voice message saved locally. AI processing is temporarily unavailable.",
              isWarning: true,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, warningMessage]);
            
            // Still call the voice message callback with local data
            if (onVoiceMessage) {
              onVoiceMessage({
                type: 'voice',
                timestamp: new Date(),
                audioBlob: audioRecorder.audioBlob,
                audioData: audioData,
                aiProcessingFailed: true
              });
            }
          }

        } catch (error) {
          console.error('Voice recording error:', error);
          const errorMessage = {
            id: Date.now() + 1,
            type: 'ai',
            content: "Sorry, there was an error with your voice message. Please try again.",
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
        } finally {
          setIsProcessingVoice(false);
          audioRecorder.clearRecording();
        }
      }
    } else {
      // Start recording
      audioRecorder.startRecording();
    }
  };

  // Function to download audio file locally
  const downloadAudioFile = (audioData) => {
    try {
      // Create download link
      const link = document.createElement('a');
      link.href = audioData.url;
      link.download = audioData.fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log(`Downloaded audio file: ${audioData.fileName}`);
    } catch (error) {
      console.error('Failed to download audio file:', error);
    }
  };

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

  return (
    <Box 
      sx={{ 
        height: height, 
        display: 'flex', 
        flexDirection: 'column',
        background: '#ffffff',
        overflow: 'hidden'
      }}
    >
      {/* Minimal Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        p: 1,
        borderBottom: '1px solid #e0e0e0',
        minHeight: 48
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Psychology sx={{ color: '#4caf50', fontSize: '1.2rem', mr: 1 }} />
          <Typography variant="subtitle1" sx={{ color: '#2e7d32', fontWeight: 500 }}>
            AI Assistant
          </Typography>
        </Box>
        
        {/* TTS Toggle Button */}
        <IconButton
          size="small"
          onClick={() => setIsTTSEnabled(!isTTSEnabled)}
          sx={{ 
            color: isTTSEnabled ? '#4caf50' : '#ccc',
            '&:hover': { backgroundColor: 'rgba(76, 175, 80, 0.1)' }
          }}
          title={isTTSEnabled ? 'Disable text-to-speech' : 'Enable text-to-speech'}
        >
          {isTTSEnabled ? <VolumeUp fontSize="small" /> : <VolumeUp fontSize="small" sx={{ opacity: 0.5 }} />}
        </IconButton>
      </Box>
      
      {/* Messages Area - Maximum space */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto',
        background: '#ffffff',
        scrollBehavior: 'smooth',
        '&::-webkit-scrollbar': {
          width: '6px'
        },
        '&::-webkit-scrollbar-track': {
          background: '#f1f1f1'
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#c1c1c1',
          borderRadius: '3px'
        }
      }}>
        {messages.length === 0 ? (
          <Box sx={{ 
            textAlign: 'center', 
            p: 2,
            opacity: 0.7
          }}>
            <SmartToy sx={{ fontSize: 32, mb: 1, color: '#4caf50' }} />
            <Typography variant="body2" sx={{ color: '#666' }}>
              Start a conversation...
            </Typography>
          </Box>
        ) : (
          messages.map((message) => (
            <Box key={message.id} sx={{ p: 1 }}>
              {/* Message Content - Direct layout */}
              <Box sx={{
                p: 1.5,
                backgroundColor: message.type === 'user' ? '#f0f8f0' : '#f8f9fa',
                borderLeft: `3px solid ${message.type === 'user' ? '#4caf50' : '#2196f3'}`,
                mb: 0.5
              }}>
                {/* Message type indicator and content */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                  {message.type === 'user' ? (
                    <Person sx={{ color: '#4caf50', fontSize: 16, mt: 0.5 }} />
                  ) : (
                    <SmartToy sx={{ color: '#2196f3', fontSize: 16, mt: 0.5 }} />
                  )}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="caption" sx={{ color: '#666', display: 'block', mb: 0.5 }}>
                      {message.type === 'user' ? 'You' : 'AI'} • {message.timestamp.toLocaleTimeString()}
                    </Typography>
                    
                    {message.isVoice ? (
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <VolumeUp sx={{ color: '#4caf50', fontSize: 16 }} />
                          <Typography variant="caption">Voice • {message.duration}s</Typography>
                          {message.audioData && (
                            <IconButton size="small" onClick={() => downloadAudioFile(message.audioData)}>
                              <Download fontSize="small" />
                            </IconButton>
                          )}
                        </Box>
                        <audio controls src={message.audioUrl} style={{ width: '100%', height: '30px' }} />
                      </Box>
                    ) : message.type === 'transcription' ? (
                      <Box sx={{ backgroundColor: '#f0f8f0', border: '1px dashed #4caf50', borderRadius: 1, p: 1 }}>
                        <Typography variant="caption">📝 {message.content}</Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.4 }}>
                        {message.content}
                      </Typography>
                    )}
                  </Box>
                </Box>
                
                {/* Additional content - minimal */}
                {message.image && (
                  <img
                    src={message.image}
                    alt="Uploaded"
                    style={{ maxWidth: '100%', maxHeight: '120px', borderRadius: '4px', marginTop: '8px' }}
                  />
                )}
                
                {/* Essential alerts only */}
                {message.isEmergency && (
                  <Box sx={{ mt: 1, p: 1, backgroundColor: '#ffebee', borderRadius: 1, fontSize: '0.8rem' }}>
                    🚨 Emergency detected - Help notified
                  </Box>
                )}
                
                {message.suggestedAction && message.suggestedAction.function_name && 
                 !['provide_companionship'].includes(message.suggestedAction.function_name) && (
                  <Box sx={{ mt: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleActionConfirmation(message.suggestedAction, message.content)}
                      startIcon={getActionIcon(message.suggestedAction.function_name)}
                      sx={{ fontSize: '0.75rem', textTransform: 'none' }}
                    >
                      {getActionLabel(message.suggestedAction.function_name, message.suggestedAction.parameters)}
                    </Button>
                  </Box>
                )}
                
                {message.isError && (
                  <Box sx={{ mt: 1, p: 1, backgroundColor: '#ffebee', borderRadius: 1, fontSize: '0.8rem', color: '#d32f2f' }}>
                    Connection issue - please try again
                  </Box>
                )}
              </Box>
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Image Preview - Compact */}
      {imagePreview && (
        <Box sx={{ p: 1, borderTop: '1px solid #e0e0e0', backgroundColor: '#f8f9fa' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <img src={imagePreview} alt="Preview" style={{ width: 40, height: 40, borderRadius: '4px' }} />
            <Typography variant="caption">Image attached</Typography>
            <IconButton size="small" onClick={removeImage} sx={{ ml: 'auto', p: 0.5 }}>
              <Close fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      )}

      {/* Input Area - Minimal */}
      <Box sx={{ 
        display: 'flex', 
        gap: 1, 
        alignItems: 'center',
        p: 1,
        borderTop: '1px solid #e0e0e0',
        backgroundColor: '#ffffff'
      }}>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          ref={fileInputRef}
          style={{ display: 'none' }}
        />
        
        <IconButton
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          size="small"
          sx={{ color: '#4caf50' }}
        >
          <PhotoCamera fontSize="small" />
        </IconButton>

        {enableVoiceMessages && (
          <IconButton
            onClick={handleVoiceMessage}
            disabled={isProcessingVoice}
            size="small"
            sx={{ color: audioRecorder.isRecording ? '#f44336' : '#2196f3' }}
          >
            {isProcessingVoice ? (
              <VolumeUp fontSize="small" />
            ) : audioRecorder.isRecording ? (
              <MicOff fontSize="small" />
            ) : (
              <Mic fontSize="small" />
            )}
          </IconButton>
        )}

        <TextField
          fullWidth
          multiline
          maxRows={2}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type message..."
          disabled={isLoading}
          variant="outlined"
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': { border: 'none' },
              backgroundColor: '#f8f9fa',
              borderRadius: 1
            }
          }}
        />
        
        <IconButton
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
          size="small"
          sx={{ color: !inputMessage.trim() || isLoading ? '#ccc' : '#4caf50' }}
        >
          <Send fontSize="small" />
        </IconButton>
      </Box>

      {/* Loading indicator */}
      {isLoading && (
        <Box sx={{ p: 1, textAlign: 'center', backgroundColor: '#f8f9fa', borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            AI is thinking...
          </Typography>
        </Box>
      )}

      {/* Smart Home Confirmation Dialog */}
      <Dialog open={smartHomeDialog.open} onClose={cancelSmartHomeCommands} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Home color="primary" />
          Smart Home Control Confirmation
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              ⚠️ Security Confirmation Required
            </Typography>
            <Typography variant="body2">
              I detected a smart home control request. Please confirm before I execute these commands:
            </Typography>
          </Alert>
          
          <Typography variant="body2" sx={{ mb: 2, fontStyle: 'italic' }}>
            Your request: "{smartHomeDialog.message}"
          </Typography>

          <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Commands to execute:
            </Typography>
            {smartHomeDialog.commands.map((cmd, idx) => (
              <Box key={idx} sx={{ mb: 1, p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2">
                  📱 <strong>{cmd.payload.action?.toUpperCase()}</strong> {cmd.payload.device_type}
                  {cmd.payload.room && <span> in <strong>{cmd.payload.room}</strong></span>}
                  {cmd.payload.parameters && (
                    <span> (Settings: {JSON.stringify(cmd.payload.parameters)})</span>
                  )}
                </Typography>
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelSmartHomeCommands} color="error" variant="outlined">
            ❌ Cancel
          </Button>
          <Button 
            onClick={() => executeSmartHomeCommands(smartHomeDialog.commands)} 
            color="primary" 
            variant="contained"
            startIcon={<CheckCircle />}
          >
            ✅ Execute Commands
          </Button>
        </DialogActions>
      </Dialog>

      {/* Action Confirmation Dialog */}
      <Dialog open={actionConfirmDialog.open} onClose={cancelAction} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CheckCircle color="primary" />
          Confirm Action
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              🤖 AI Assistant wants to help you with:
            </Typography>
            <Typography variant="body2">
              {actionConfirmDialog.action?.reasoning}
            </Typography>
          </Alert>
          
          <Typography variant="body2" sx={{ mb: 2 }}>
            <strong>Your message:</strong> "{actionConfirmDialog.message}"
          </Typography>

          <Box sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Proposed action:
            </Typography>
            <Typography variant="body2">
              {actionConfirmDialog.action && getActionLabel(
                actionConfirmDialog.action.function_name, 
                actionConfirmDialog.action.parameters
              )}
            </Typography>
            {actionConfirmDialog.action?.parameters && Object.keys(actionConfirmDialog.action.parameters).length > 0 && (
              <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
                Details: {JSON.stringify(actionConfirmDialog.action.parameters, null, 2)}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelAction} color="secondary" variant="outlined">
            ❌ No, thanks
          </Button>
          <Button 
            onClick={confirmAction} 
            color="primary" 
            variant="contained"
            startIcon={actionConfirmDialog.action && getActionIcon(actionConfirmDialog.action.function_name)}
          >
            ✅ Yes, please help
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TextChat;