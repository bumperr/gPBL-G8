import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress
} from '@mui/material';
import {
  Videocam,
  Stop,
  CameraAlt,
  Refresh,
  Settings,
  Error,
  CheckCircle,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';

const ServerCameraStream = ({ 
  cameraId = 0,
  autoStart = false,
  onSnapshot,
  onError,
  showControls = true,
  width = 640,
  height = 480
}) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(cameraId);
  const [cameraStatus, setCameraStatus] = useState('offline');
  const [currentFrame, setCurrentFrame] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [streamMode, setStreamMode] = useState('frames'); // 'frames' or 'mjpeg'
  
  const intervalRef = useRef(null);
  const imgRef = useRef(null);

  const API_BASE = '';

  // Load available cameras
  const loadAvailableCameras = async () => {
    try {
      const response = await fetch(`/api/camera/available`);
      const data = await response.json();
      
      if (data.success) {
        setAvailableCameras(data.cameras);
        console.log('Available cameras loaded:', data.cameras);
      } else {
        console.error('Failed to load cameras:', data);
      }
    } catch (error) {
      console.error('Error loading cameras:', error);
      setError('Failed to load available cameras');
    }
  };

  // Check camera status
  const checkCameraStatus = async () => {
    try {
      const response = await fetch(`/api/camera/status`);
      const data = await response.json();
      
      if (data.success) {
        setCameraStatus('online');
        console.log('Camera status:', data);
      } else {
        setCameraStatus('offline');
      }
    } catch (error) {
      console.error('Error checking camera status:', error);
      setCameraStatus('offline');
    }
  };

  // Start camera streaming
  const startStreaming = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Start camera on server
      const startResponse = await fetch(`/api/camera/start/${selectedCamera}`, {
        method: 'POST'
      });
      const startData = await startResponse.json();
      
      if (!startData.success) {
        throw new Error(startData.message || 'Failed to start camera');
      }
      
      setIsStreaming(true);
      
      if (streamMode === 'frames') {
        // Start polling for frames
        intervalRef.current = setInterval(fetchLatestFrame, 1000/15); // ~15 FPS
      }
      
      console.log('Camera streaming started:', startData);
      
    } catch (error) {
      console.error('Error starting camera:', error);
      setError(error.message);
      onError && onError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Stop camera streaming
  const stopStreaming = async () => {
    try {
      setIsLoading(true);
      
      // Clear frame polling
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      
      // Stop camera on server
      const stopResponse = await fetch(`/api/camera/stop/${selectedCamera}`, {
        method: 'POST'
      });
      
      setIsStreaming(false);
      setCurrentFrame(null);
      
      console.log('Camera streaming stopped');
      
    } catch (error) {
      console.error('Error stopping camera:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch latest frame from server
  const fetchLatestFrame = async () => {
    try {
      const response = await fetch(`/api/camera/frame/${selectedCamera}`);
      const data = await response.json();
      
      if (data.success && data.frame) {
        setCurrentFrame(`data:image/jpeg;base64,${data.frame}`);
        setError(null);
      } else if (!data.success) {
        console.warn('No frame available:', data.message);
      }
    } catch (error) {
      console.error('Error fetching frame:', error);
      // Don't set error for frame fetch failures to avoid UI noise
    }
  };

  // Take snapshot
  const takeSnapshot = async () => {
    try {
      const response = await fetch(`/api/camera/snapshot/${selectedCamera}`);
      const data = await response.json();
      
      if (data.success) {
        const snapshotData = `data:image/jpeg;base64,${data.snapshot}`;
        
        // Convert to blob for callback
        const byteCharacters = atob(data.snapshot);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'image/jpeg' });
        
        onSnapshot && onSnapshot(blob, snapshotData);
        
        console.log('Snapshot taken successfully');
        return snapshotData;
      } else {
        throw new Error(data.message || 'Failed to take snapshot');
      }
    } catch (error) {
      console.error('Error taking snapshot:', error);
      setError(error.message);
      return null;
    }
  };

  // Handle camera change
  const handleCameraChange = (newCameraId) => {
    if (isStreaming) {
      stopStreaming().then(() => {
        setSelectedCamera(newCameraId);
      });
    } else {
      setSelectedCamera(newCameraId);
    }
  };

  // Initialize component
  useEffect(() => {
    loadAvailableCameras();
    checkCameraStatus();
    
    if (autoStart) {
      setTimeout(startStreaming, 500);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Get MJPEG stream URL
  const getMjpegStreamUrl = () => {
    return `/api/camera/stream/${selectedCamera}`;
  };

  return (
    <Card sx={{ 
      maxWidth: { xs: '100%', sm: width + 50 }, 
      mx: 'auto',
      width: '100%'
    }}>
      <CardContent sx={{ p: { xs: 1.5, sm: 2 }, '&:last-child': { pb: { xs: 1.5, sm: 2 } } }}>
        {/* Camera Status Header */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: { xs: 'flex-start', sm: 'center' }, 
          flexDirection: { xs: 'column', sm: 'row' },
          gap: { xs: 1, sm: 0 },
          mb: 2 
        }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Videocam color="primary" />
            <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
              Server Camera Stream
            </Box>
            <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>
              Camera
            </Box>
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Chip 
              label={cameraStatus} 
              color={cameraStatus === 'online' ? 'success' : 'error'} 
              size="small" 
              icon={cameraStatus === 'online' ? <CheckCircle /> : <Error />}
            />
            {showControls && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<Settings />}
                onClick={() => setSettingsOpen(true)}
                sx={{ display: { xs: 'none', sm: 'flex' } }}
              >
                Settings
              </Button>
            )}
            {showControls && (
              <Button
                variant="outlined"
                size="small"
                onClick={() => setSettingsOpen(true)}
                sx={{ display: { xs: 'flex', sm: 'none' }, minWidth: 'auto', px: 1 }}
              >
                <Settings />
              </Button>
            )}
          </Box>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Camera/Video Sample Selection */}
        {showControls && availableCameras.length > 1 && (
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Camera/Video Sample</InputLabel>
            <Select
              value={selectedCamera}
              label="Select Camera/Video Sample"
              onChange={(e) => handleCameraChange(e.target.value)}
              disabled={isStreaming}
            >
              {/* Live Cameras */}
              <MenuItem disabled sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                📷 Live Cameras
              </MenuItem>
              {availableCameras.filter(cam => cam.available && cam.type === 'camera').map((camera) => (
                <MenuItem key={camera.id} value={camera.id} sx={{ pl: 3 }}>
                  📷 {camera.name} - {camera.width}x{camera.height}
                </MenuItem>
              ))}
              
              {/* Video Samples */}
              <MenuItem disabled sx={{ fontWeight: 'bold', color: 'secondary.main', mt: 1 }}>
                🎬 VLM Analysis Demo Videos
              </MenuItem>
              {availableCameras.filter(cam => cam.available && cam.type === 'video_sample').map((camera) => (
                <MenuItem key={camera.id} value={camera.id} sx={{ pl: 3 }}>
                  <Box>
                    <Typography variant="body2">
                      🎬 {camera.name} - {camera.duration ? `${camera.duration}s` : 'Demo'}
                    </Typography>
                    {camera.description && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {camera.description}
                      </Typography>
                    )}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* VLM Analysis Info for Video Samples */}
        {showControls && availableCameras.find(cam => cam.id === selectedCamera)?.type === 'video_sample' && (
          <Box sx={{ 
            mb: 2, 
            p: 1.5, 
            backgroundColor: '#e3f2fd', 
            borderRadius: 1,
            border: '1px solid #2196f3'
          }}>
            <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              🤖 <strong>VLM Analysis Demo</strong>
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              This video sample demonstrates AI-powered video analysis every 15 seconds using Video-LLaVA technology.
              Analysis results are automatically stored in the analytics database.
            </Typography>
          </Box>
        )}

        {/* Video Display */}
        <Box sx={{ 
          border: '2px solid #ddd', 
          borderRadius: 2, 
          overflow: 'hidden', 
          backgroundColor: '#000',
          position: 'relative',
          width: { xs: '100%', sm: width },
          height: { xs: 'auto', sm: height },
          aspectRatio: { xs: '4/3', sm: 'auto' },
          minHeight: { xs: 240, sm: height },
          maxWidth: '100%',
          mx: 'auto'
        }}>
          {isLoading && (
            <Box sx={{ 
              position: 'absolute', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              zIndex: 10
            }}>
              <CircularProgress color="primary" />
            </Box>
          )}
          
          {!isStreaming && !isLoading && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              color: 'white',
              flexDirection: 'column',
              gap: 2
            }}>
              <Videocam sx={{ fontSize: 64, opacity: 0.5 }} />
              <Typography variant="body1">Camera Stream Offline</Typography>
            </Box>
          )}
          
          {isStreaming && streamMode === 'frames' && currentFrame && (
            <img
              ref={imgRef}
              src={currentFrame}
              alt="Camera Stream"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
          )}
          
          {isStreaming && streamMode === 'mjpeg' && (
            <img
              ref={imgRef}
              src={getMjpegStreamUrl()}
              alt="Camera Stream"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
              onError={(e) => {
                console.error('MJPEG stream error:', e);
                setError('Failed to load MJPEG stream');
              }}
            />
          )}
          
          {isStreaming && (
            <LinearProgress 
              sx={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                right: 0,
                height: 2
              }}
              color="primary"
            />
          )}
        </Box>

        {/* Controls */}
        {showControls && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 1, 
            mt: 2, 
            justifyContent: 'center' 
          }}>
            {!isStreaming ? (
              <Button
                variant="contained"
                startIcon={isLoading ? <CircularProgress size={20} /> : <Videocam />}
                onClick={startStreaming}
                disabled={isLoading || cameraStatus === 'offline'}
                fullWidth={{ xs: true, sm: false }}
                sx={{ minWidth: { sm: 120 } }}
              >
                Start Stream
              </Button>
            ) : (
              <Button
                variant="contained"
                color="error"
                startIcon={<Stop />}
                onClick={stopStreaming}
                disabled={isLoading}
                fullWidth={{ xs: true, sm: false }}
                sx={{ minWidth: { sm: 120 } }}
              >
                Stop Stream
              </Button>
            )}
            
            <Button
              variant="outlined"
              startIcon={<CameraAlt />}
              onClick={takeSnapshot}
              disabled={!isStreaming || isLoading}
              fullWidth={{ xs: true, sm: false }}
              sx={{ minWidth: { sm: 100 } }}
            >
              Snapshot
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadAvailableCameras}
              disabled={isLoading}
              fullWidth={{ xs: true, sm: false }}
              sx={{ minWidth: { sm: 100 } }}
            >
              Refresh
            </Button>
          </Box>
        )}

        {/* Status Info */}
        <Box sx={{ 
          mt: 2, 
          p: { xs: 0.5, sm: 1 }, 
          backgroundColor: '#f5f5f5', 
          borderRadius: 1,
          display: { xs: 'none', sm: 'block' }
        }}>
          <Typography variant="caption" display="block">
            Camera: {selectedCamera} | Status: {isStreaming ? 'Streaming' : 'Stopped'}
          </Typography>
          <Typography variant="caption" display="block">
            Mode: {streamMode.toUpperCase()} | Resolution: {width}x{height}
          </Typography>
        </Box>
        
        {/* Mobile Status Info - Compact */}
        <Box sx={{ 
          mt: 1, 
          display: { xs: 'flex', sm: 'none' },
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Typography variant="caption" color="text.secondary">
            Cam {selectedCamera}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {isStreaming ? '🔴 Live' : '⚫ Off'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {streamMode.toUpperCase()}
          </Typography>
        </Box>
      </CardContent>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Camera Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Stream Mode</InputLabel>
              <Select
                value={streamMode}
                label="Stream Mode"
                onChange={(e) => setStreamMode(e.target.value)}
                disabled={isStreaming}
              >
                <MenuItem value="frames">Individual Frames (Base64)</MenuItem>
                <MenuItem value="mjpeg">MJPEG Stream</MenuItem>
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="text.secondary">
              Individual Frames: Better compatibility, more CPU usage
              <br />
              MJPEG Stream: Better performance, requires direct server access
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default ServerCameraStream;