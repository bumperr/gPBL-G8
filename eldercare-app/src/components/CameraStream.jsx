import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Button,
  Alert,
  CircularProgress,
  Tooltip,
  Switch,
  FormControlLabel,
  Slider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Videocam,
  VideocamOff,
  Fullscreen,
  FullscreenExit,
  Settings,
  Refresh,
  PhotoCamera,
  RecordVoiceOver,
  VolumeUp,
  VolumeOff,
  Security,
  CameraAlt,
  Tune
} from '@mui/icons-material';

const CameraStream = ({ 
  elderName = 'Elder User',
  cameraServerUrl = 'http://192.168.1.200:8080', // Raspberry Pi camera server
  onSnapshot = null,
  onError = null 
}) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [streamQuality, setStreamQuality] = useState(80);
  const [brightness, setBrightness] = useState(50);
  const [contrast, setContrast] = useState(50);
  const [saturation, setSaturation] = useState(50);
  const [resolution, setResolution] = useState('1280x720');
  const [nightVision, setNightVision] = useState(false);
  const [motionDetection, setMotionDetection] = useState(true);

  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const streamCheckInterval = useRef(null);

  // Camera stream URL endpoints
  const getStreamUrl = () => `${cameraServerUrl}/stream.mjpg`;
  const getSnapshotUrl = () => `${cameraServerUrl}/snapshot`;
  const getControlUrl = (action) => `${cameraServerUrl}/control?${action}`;

  useEffect(() => {
    // Auto-start streaming when component mounts
    startStreaming();
    
    return () => {
      stopStreaming();
    };
  }, []);

  const startStreaming = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // Test camera server connectivity
      const response = await fetch(`${cameraServerUrl}/status`, {
        method: 'GET',
        timeout: 5000
      });
      
      if (!response.ok) {
        throw new Error(`Camera server not responding: ${response.status}`);
      }
      
      // Start video stream
      if (videoRef.current) {
        videoRef.current.src = getStreamUrl();
        videoRef.current.onload = () => {
          setIsStreaming(true);
          setIsLoading(false);
          startStreamHealthCheck();
        };
        videoRef.current.onerror = () => {
          throw new Error('Failed to load video stream');
        };
      }
      
    } catch (err) {
      console.error('Camera streaming error:', err);
      setError(`Camera connection failed: ${err.message}`);
      setIsLoading(false);
      setIsStreaming(false);
      
      if (onError) {
        onError(err.message);
      }
    }
  };

  const stopStreaming = () => {
    if (videoRef.current) {
      videoRef.current.src = '';
    }
    
    if (streamCheckInterval.current) {
      clearInterval(streamCheckInterval.current);
    }
    
    setIsStreaming(false);
    setIsLoading(false);
  };

  const startStreamHealthCheck = () => {
    // Check stream health every 10 seconds
    streamCheckInterval.current = setInterval(async () => {
      try {
        const response = await fetch(`${cameraServerUrl}/status`);
        if (!response.ok) {
          throw new Error('Stream health check failed');
        }
      } catch (err) {
        console.warn('Stream health check failed:', err);
        setError('Connection unstable - attempting to reconnect...');
        setTimeout(() => {
          if (isStreaming) {
            refreshStream();
          }
        }, 2000);
      }
    }, 10000);
  };

  const refreshStream = () => {
    stopStreaming();
    setTimeout(startStreaming, 1000);
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current?.requestFullscreen) {
        containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  const takeSnapshot = async () => {
    try {
      const response = await fetch(getSnapshotUrl());
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const link = document.createElement('a');
        link.href = url;
        link.download = `eldercare_snapshot_${elderName}_${new Date().toISOString().slice(0,19)}.jpg`;
        link.click();
        
        URL.revokeObjectURL(url);
        
        if (onSnapshot) {
          onSnapshot(blob);
        }
      }
    } catch (err) {
      console.error('Snapshot failed:', err);
      setError('Failed to take snapshot');
    }
  };

  const toggleRecording = async () => {
    try {
      const action = isRecording ? 'stop_recording' : 'start_recording';
      const response = await fetch(getControlUrl(`action=${action}`));
      
      if (response.ok) {
        setIsRecording(!isRecording);
      }
    } catch (err) {
      console.error('Recording toggle failed:', err);
      setError('Failed to toggle recording');
    }
  };

  const adjustCameraSetting = async (setting, value) => {
    try {
      const response = await fetch(getControlUrl(`${setting}=${value}`));
      if (!response.ok) {
        throw new Error(`Failed to adjust ${setting}`);
      }
    } catch (err) {
      console.error('Camera setting adjustment failed:', err);
      setError(`Failed to adjust ${setting}`);
    }
  };

  const handleQualityChange = (event, newValue) => {
    setStreamQuality(newValue);
    adjustCameraSetting('quality', newValue);
  };

  const handleBrightnessChange = (event, newValue) => {
    setBrightness(newValue);
    adjustCameraSetting('brightness', newValue);
  };

  const handleContrastChange = (event, newValue) => {
    setContrast(newValue);
    adjustCameraSetting('contrast', newValue);
  };

  const handleSaturationChange = (event, newValue) => {
    setSaturation(newValue);
    adjustCameraSetting('saturation', newValue);
  };

  const handleResolutionChange = (event) => {
    const newResolution = event.target.value;
    setResolution(newResolution);
    adjustCameraSetting('resolution', newResolution);
  };

  const toggleNightVision = async () => {
    const newValue = !nightVision;
    setNightVision(newValue);
    await adjustCameraSetting('night_vision', newValue ? 'on' : 'off');
  };

  const toggleMotionDetection = async () => {
    const newValue = !motionDetection;
    setMotionDetection(newValue);
    await adjustCameraSetting('motion_detection', newValue ? 'on' : 'off');
  };

  const resetCameraSettings = async () => {
    setBrightness(50);
    setContrast(50);
    setSaturation(50);
    setStreamQuality(80);
    await adjustCameraSetting('reset', 'all');
  };

  return (
    <Paper 
      ref={containerRef}
      elevation={3} 
      sx={{ 
        p: 2, 
        borderRadius: 3,
        background: 'linear-gradient(145deg, #f0f4f8, #e2e8f0)',
        position: 'relative',
        minHeight: isFullscreen ? '100vh' : 400
      }}
    >
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 2 
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Videocam color="primary" />
          Live Camera - {elderName}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Stream">
            <IconButton onClick={refreshStream} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Take Snapshot">
            <IconButton onClick={takeSnapshot} disabled={!isStreaming}>
              <PhotoCamera />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isRecording ? "Stop Recording" : "Start Recording"}>
            <IconButton 
              onClick={toggleRecording} 
              disabled={!isStreaming}
              sx={{ color: isRecording ? 'red' : 'inherit' }}
            >
              <RecordVoiceOver />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Camera Settings">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={nightVision ? "Disable Night Vision" : "Enable Night Vision"}>
            <IconButton 
              onClick={toggleNightVision}
              sx={{ color: nightVision ? 'yellow' : 'inherit' }}
            >
              <Security />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={motionDetection ? "Disable Motion Detection" : "Enable Motion Detection"}>
            <IconButton 
              onClick={toggleMotionDetection}
              sx={{ color: motionDetection ? 'green' : 'inherit' }}
            >
              <CameraAlt />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
            <IconButton onClick={toggleFullscreen} disabled={!isStreaming}>
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Stream Container */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: isFullscreen ? 'calc(100vh - 120px)' : 400,
          backgroundColor: '#000',
          borderRadius: 2,
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {/* Loading Indicator */}
        {isLoading && (
          <Box sx={{ 
            position: 'absolute', 
            zIndex: 2, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            color: 'white'
          }}>
            <CircularProgress color="primary" sx={{ mb: 2 }} />
            <Typography variant="body2">Connecting to camera...</Typography>
          </Box>
        )}

        {/* Video Stream */}
        {isStreaming ? (
          <img
            ref={videoRef}
            alt="Elder Care Live Stream"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain'
            }}
          />
        ) : (
          <Box sx={{ 
            textAlign: 'center', 
            color: 'white',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}>
            <VideocamOff sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
            <Typography variant="h6" sx={{ opacity: 0.7 }}>
              Camera Stream Not Available
            </Typography>
            <Button 
              variant="contained" 
              onClick={startStreaming}
              sx={{ mt: 2 }}
              disabled={isLoading}
            >
              Start Camera
            </Button>
          </Box>
        )}

        {/* Stream Status Overlay */}
        <Box sx={{
          position: 'absolute',
          top: 10,
          right: 10,
          backgroundColor: isStreaming ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)',
          color: 'white',
          px: 2,
          py: 0.5,
          borderRadius: 1,
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <Box sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: 'currentColor',
            animation: isStreaming ? 'blink 1s infinite' : 'none'
          }} />
          {isStreaming ? 'LIVE' : 'OFFLINE'}
        </Box>

        {/* Recording Indicator */}
        {isRecording && (
          <Box sx={{
            position: 'absolute',
            top: 10,
            left: 10,
            backgroundColor: 'rgba(244, 67, 54, 0.9)',
            color: 'white',
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontSize: '0.875rem',
            animation: 'pulse 1s infinite'
          }}>
            🔴 REC
          </Box>
        )}
      </Box>

      {/* Controls Footer */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mt: 2 
      }}>
        <FormControlLabel
          control={
            <Switch
              checked={audioEnabled}
              onChange={(e) => setAudioEnabled(e.target.checked)}
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {audioEnabled ? <VolumeUp /> : <VolumeOff />}
              Audio
            </Box>
          }
        />

        <Typography variant="body2" color="text.secondary">
          {isStreaming ? `Connected to ${cameraServerUrl}` : 'Not connected'}
        </Typography>
      </Box>

      {/* Camera Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Camera Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography gutterBottom>Stream Quality</Typography>
            <Slider
              value={streamQuality}
              onChange={handleQualityChange}
              valueLabelDisplay="auto"
              step={10}
              marks
              min={10}
              max={100}
              valueLabelFormat={(value) => `${value}%`}
            />

            <Typography gutterBottom sx={{ mt: 3 }}>Brightness</Typography>
            <Slider
              value={brightness}
              onChange={handleBrightnessChange}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              valueLabelFormat={(value) => `${value}%`}
            />

            <Typography gutterBottom sx={{ mt: 3 }}>Contrast</Typography>
            <Slider
              value={contrast}
              onChange={handleContrastChange}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              valueLabelFormat={(value) => `${value}%`}
            />

            <Typography gutterBottom sx={{ mt: 3 }}>Saturation</Typography>
            <Slider
              value={saturation}
              onChange={handleSaturationChange}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              valueLabelFormat={(value) => `${value}%`}
            />

            <FormControl fullWidth sx={{ mt: 3 }}>
              <InputLabel>Resolution</InputLabel>
              <Select
                value={resolution}
                onChange={handleResolutionChange}
                label="Resolution"
              >
                <MenuItem value="640x480">640x480 (VGA)</MenuItem>
                <MenuItem value="800x600">800x600 (SVGA)</MenuItem>
                <MenuItem value="1024x768">1024x768 (XGA)</MenuItem>
                <MenuItem value="1280x720">1280x720 (HD)</MenuItem>
                <MenuItem value="1920x1080">1920x1080 (Full HD)</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={nightVision}
                    onChange={toggleNightVision}
                    color="warning"
                  />
                }
                label="Night Vision Mode"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={motionDetection}
                    onChange={toggleMotionDetection}
                    color="success"
                  />
                }
                label="Motion Detection"
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={resetCameraSettings} startIcon={<Tune />}>
            Reset to Default
          </Button>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Custom CSS for animations */}
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.5; }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `}
      </style>
    </Paper>
  );
};

export default CameraStream;