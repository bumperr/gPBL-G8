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
  PersonOutline
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

        // Add to conversation history
        const interaction = {
          id: Date.now(),
          timestamp: new Date(),
          elder_speech: data.transcription.text,
          ai_response: data.ai_response.response,
          confidence: data.transcription.confidence,
          intent: data.ai_response.intent_detected,
          is_emergency: data.ai_response.is_emergency
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
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  {!isSpeaking ? (
                    <IconButton size="small" onClick={() => speakText(aiResponse)}>
                      <VolumeUp />
                    </IconButton>
                  ) : (
                    <IconButton size="small" onClick={stopSpeaking} color="error">
                      <VolumeOff />
                    </IconButton>
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
    </Card>
  );
};

export default VoiceCommunication;