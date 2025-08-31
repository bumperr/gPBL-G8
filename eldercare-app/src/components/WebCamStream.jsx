import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  Typography,
  IconButton,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  Videocam,
  VideocamOff,
  FullscreenExitOutlined,
  Fullscreen,
  PhotoCamera,
  Settings
} from '@mui/icons-material';

const WebCamStream = ({ 
  onVideoStream,
  onSnapshot,
  autoStart = false,
  showControls = true,
  width = 640,
  height = 480 
}) => {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [streamStats, setStreamStats] = useState({
    fps: 0,
    resolution: '',
    deviceName: ''
  });

  // Get available video devices
  const getVideoDevices = async () => {
    try {
      // Request permission first
      await navigator.mediaDevices.getUserMedia({ video: true });
      
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      
      console.log('Available video devices:', videoDevices);
      
      setDevices(videoDevices);
      
      // Auto-select first device if none selected
      if (videoDevices.length > 0 && !selectedDevice) {
        setSelectedDevice(videoDevices[0].deviceId);
      }
      
      return videoDevices;
    } catch (err) {
      console.error('Error getting video devices:', err);
      setError('Unable to access camera devices. Please check permissions.');
      return [];
    }
  };

  // Start video stream
  const startStream = async (deviceId = selectedDevice) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Stop existing stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      const constraints = {
        video: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          width: { ideal: width },
          height: { ideal: height },
          frameRate: { ideal: 30 }
        },
        audio: false // We only need video for eldercare monitoring
      };
      
      console.log('Starting stream with constraints:', constraints);
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          const video = videoRef.current;
          const track = stream.getVideoTracks()[0];
          const settings = track.getSettings();
          
          setStreamStats({
            fps: settings.frameRate || 30,
            resolution: `${settings.width}x${settings.height}`,
            deviceName: track.label || 'Unknown Camera'
          });
          
          console.log('Video stream started:', settings);
        };
      }
      
      setIsStreaming(true);
      
      // Notify parent component
      if (onVideoStream) {
        onVideoStream(stream);
      }
      
    } catch (err) {
      console.error('Error starting stream:', err);
      let errorMessage = 'Failed to start video stream. ';
      
      if (err.name === 'NotFoundError') {
        errorMessage += 'No camera found.';
      } else if (err.name === 'NotAllowedError') {
        errorMessage += 'Camera access denied. Please allow camera permissions.';
      } else if (err.name === 'NotReadableError') {
        errorMessage += 'Camera is already in use by another application.';
      } else {
        errorMessage += err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Stop video stream
  const stopStream = () => {
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      
      setIsStreaming(false);
      setStreamStats({ fps: 0, resolution: '', deviceName: '' });
      
      console.log('Video stream stopped');
    } catch (err) {
      console.error('Error stopping stream:', err);
    }
  };

  // Take snapshot
  const takeSnapshot = () => {
    try {
      if (!videoRef.current || !isStreaming) {
        setError('No video stream available for snapshot');
        return;
      }
      
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0);
      
      // Convert to blob
      canvas.toBlob((blob) => {
        if (onSnapshot) {
          onSnapshot(blob, canvas.toDataURL('image/jpeg', 0.9));
        }
      }, 'image/jpeg', 0.9);
      
      console.log('Snapshot taken');
    } catch (err) {
      console.error('Error taking snapshot:', err);
      setError('Failed to take snapshot');
    }
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    if (!isFullscreen && videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
        setIsFullscreen(true);
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  // Handle device selection
  const handleDeviceChange = async (event) => {
    const deviceId = event.target.value;
    setSelectedDevice(deviceId);
    
    if (isStreaming) {
      await startStream(deviceId);
    }
  };

  // Initialize on mount
  useEffect(() => {
    const init = async () => {
      await getVideoDevices();
      if (autoStart) {
        setTimeout(() => startStream(), 500);
      }
    };
    
    init();
    
    // Cleanup on unmount
    return () => {
      stopStream();
    };
  }, []);

  // Handle fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 2, maxWidth: '100%' }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center">
          <Videocam sx={{ mr: 1 }} />
          Video Stream
          {isStreaming && (
            <Chip 
              label="LIVE" 
              color="error" 
              size="small" 
              sx={{ ml: 2, animation: 'blink 2s infinite' }} 
            />
          )}
        </Typography>
        
        {showControls && (
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            {/* Device Selection */}
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Camera Device</InputLabel>
              <Select
                value={selectedDevice}
                onChange={handleDeviceChange}
                label="Camera Device"
                disabled={devices.length === 0}
              >
                {devices.map((device) => (
                  <MenuItem key={device.deviceId} value={device.deviceId}>
                    {device.label || `Camera ${devices.indexOf(device) + 1}`}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            {/* Control Buttons */}
            <Button
              variant={isStreaming ? "outlined" : "contained"}
              color={isStreaming ? "error" : "primary"}
              onClick={isStreaming ? stopStream : startStream}
              disabled={isLoading || devices.length === 0}
              startIcon={
                isLoading ? (
                  <CircularProgress size={16} />
                ) : isStreaming ? (
                  <VideocamOff />
                ) : (
                  <Videocam />
                )
              }
            >
              {isLoading ? 'Loading...' : isStreaming ? 'Stop' : 'Start'}
            </Button>
            
            <IconButton
              onClick={takeSnapshot}
              disabled={!isStreaming}
              color="primary"
              title="Take Snapshot"
            >
              <PhotoCamera />
            </IconButton>
            
            <IconButton
              onClick={toggleFullscreen}
              disabled={!isStreaming}
              color="primary"
              title="Toggle Fullscreen"
            >
              {isFullscreen ? <FullscreenExitOutlined /> : <Fullscreen />}
            </IconButton>
          </Box>
        )}
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {/* No Devices Warning */}
      {devices.length === 0 && !isLoading && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          No camera devices found. Please connect a camera and refresh the page.
          <Button size="small" onClick={getVideoDevices} sx={{ ml: 1 }}>
            Refresh
          </Button>
        </Alert>
      )}

      {/* Video Display */}
      <Box 
        sx={{ 
          position: 'relative',
          maxWidth: '100%',
          bgcolor: '#000',
          borderRadius: 1,
          overflow: 'hidden'
        }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            width: '100%',
            height: 'auto',
            maxWidth: width,
            maxHeight: height,
            display: 'block',
            backgroundColor: '#000'
          }}
        />
        
        {/* Stream Stats Overlay */}
        {isStreaming && streamStats.resolution && (
          <Card 
            sx={{ 
              position: 'absolute', 
              top: 8, 
              right: 8, 
              bgcolor: 'rgba(0,0,0,0.7)',
              minWidth: 'auto'
            }}
          >
            <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="white" component="div">
                {streamStats.resolution} • {streamStats.fps} FPS
              </Typography>
              <Typography variant="caption" color="white" component="div">
                {streamStats.deviceName}
              </Typography>
            </CardContent>
          </Card>
        )}
        
        {/* No Stream Placeholder */}
        {!isStreaming && !isLoading && (
          <Box 
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: 240,
              color: 'grey.500'
            }}
          >
            <VideocamOff sx={{ fontSize: 48, mb: 1 }} />
            <Typography variant="body2">
              No video stream active
            </Typography>
          </Box>
        )}
        
        {/* Loading Indicator */}
        {isLoading && (
          <Box 
            sx={{ 
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(0,0,0,0.5)'
            }}
          >
            <CircularProgress color="primary" />
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default WebCamStream;