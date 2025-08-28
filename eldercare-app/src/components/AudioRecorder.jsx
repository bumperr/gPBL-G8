import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  Mic,
  MicOff,
  PlayArrow,
  Pause,
  Send,
  Delete,
  Download
} from '@mui/icons-material';
import useAudioRecorder from '../hooks/useAudioRecorder';
import apiService from '../services/api';

const AudioRecorder = ({ onMessageSent, elderInfo }) => {
  const {
    isRecording,
    audioURL,
    audioBlob,
    duration,
    durationSeconds,
    error,
    startRecording,
    stopRecording,
    clearRecording,
    downloadRecording,
    getAudioBase64
  } = useAudioRecorder();

  const [isPlaying, setIsPlaying] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState('');
  const audioRef = React.useRef(null);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleSendAudio = async () => {
    if (!audioBlob) return;

    setIsSending(true);
    setSendError('');

    try {
      // Convert audio to base64
      const audioBase64 = await getAudioBase64();
      
      // Process speech with AI assistance
      const response = await apiService.processElderSpeech(
        audioBase64,
        elderInfo || { name: 'Elder User' },
        'en'
      );

      if (response.status === 'success') {
        // Handle successful transcription and AI response
        if (onMessageSent) {
          onMessageSent({
            type: 'voice',
            transcription: response.transcription,
            aiResponse: response.ai_response,
            isEmergency: response.emergency_alert ? true : false,
            emergencyAlert: response.emergency_alert,
            timestamp: response.timestamp
          });
        }

        // Show success message or handle emergency
        if (response.emergency_alert) {
          setSendError('Emergency detected! Caregivers have been notified.');
        }
      } else {
        setSendError(response.message || 'Failed to process voice message');
      }

      clearRecording();
      
    } catch (err) {
      console.error('Failed to process voice message:', err);
      setSendError('Failed to process voice message. Please try again.');
      
      // Fallback: still try to send raw audio for manual review
      try {
        const audioBase64 = await getAudioBase64();
        await apiService.sendMQTTMessage('elder/voice_raw', JSON.stringify({
          type: 'raw_voice_message',
          audio: audioBase64,
          duration: durationSeconds,
          elderInfo: elderInfo || { name: 'Elder User' },
          timestamp: new Date().toISOString(),
          note: 'Processing failed - manual review needed'
        }));
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    } finally {
      setIsSending(false);
    }
  };

  const maxRecordingTime = 120; // 2 minutes
  const progressPercentage = (durationSeconds / maxRecordingTime) * 100;

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3, 
        m: 2, 
        borderRadius: 3,
        background: 'linear-gradient(145deg, #f0f4f8, #e2e8f0)'
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', color: '#2d3748' }}>
        Voice Assistant
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {sendError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {sendError}
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
        
        {/* Recording Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {!isRecording ? (
            <Button
              variant="contained"
              size="large"
              startIcon={<Mic />}
              onClick={startRecording}
              disabled={isSending}
              sx={{
                backgroundColor: '#4CAF50',
                '&:hover': { backgroundColor: '#45a049' },
                borderRadius: 3,
                px: 4,
                py: 1.5,
                fontSize: '1.1rem'
              }}
            >
              Start Recording
            </Button>
          ) : (
            <Button
              variant="contained"
              size="large"
              startIcon={<MicOff />}
              onClick={stopRecording}
              sx={{
                backgroundColor: '#f44336',
                '&:hover': { backgroundColor: '#d32f2f' },
                borderRadius: 3,
                px: 4,
                py: 1.5,
                fontSize: '1.1rem'
              }}
            >
              Stop Recording
            </Button>
          )}
        </Box>

        {/* Recording Duration and Progress */}
        {isRecording && (
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <Typography variant="h4" color="primary" sx={{ mb: 1 }}>
              {duration}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(progressPercentage, 100)}
              sx={{ height: 8, borderRadius: 5 }}
            />
            {durationSeconds >= maxRecordingTime && (
              <Typography variant="caption" color="warning.main">
                Maximum recording time reached
              </Typography>
            )}
          </Box>
        )}

        {/* Audio Playback */}
        {audioURL && (
          <Box sx={{ width: '100%' }}>
            <audio
              ref={audioRef}
              src={audioURL}
              onEnded={handleAudioEnded}
              style={{ display: 'none' }}
            />
            
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
              <IconButton 
                onClick={handlePlayPause}
                color="primary"
                size="large"
              >
                {isPlaying ? <Pause /> : <PlayArrow />}
              </IconButton>
              <Typography variant="body1">
                Recorded: {duration}
              </Typography>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={isSending ? <CircularProgress size={16} /> : <Send />}
                onClick={handleSendAudio}
                disabled={isSending}
                sx={{
                  backgroundColor: '#2196F3',
                  '&:hover': { backgroundColor: '#1976D2' }
                }}
              >
                {isSending ? 'Sending...' : 'Send Message'}
              </Button>

              <IconButton
                onClick={clearRecording}
                color="secondary"
                disabled={isSending}
              >
                <Delete />
              </IconButton>

              <IconButton
                onClick={downloadRecording}
                color="primary"
                disabled={isSending}
              >
                <Download />
              </IconButton>
            </Box>
          </Box>
        )}

        {/* Recording Instructions */}
        {!isRecording && !audioURL && (
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ textAlign: 'center', mt: 2 }}
          >
            Tap "Start Recording" to send a voice message to your caregivers or ask for assistance
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default AudioRecorder;