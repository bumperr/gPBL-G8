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

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Load available cameras
  const loadAvailableCameras = async () => {
    try {
      const response = await fetch(`${API_BASE}/camera/available`);
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
      const response = await fetch(`${API_BASE}/camera/status`);
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
      const startResponse = await fetch(`${API_BASE}/camera/start/${selectedCamera}`, {
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
      const stopResponse = await fetch(`${API_BASE}/camera/stop/${selectedCamera}`, {
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
      const response = await fetch(`${API_BASE}/camera/frame/${selectedCamera}`);
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
      const response = await fetch(`${API_BASE}/camera/snapshot/${selectedCamera}`);
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
    return `${API_BASE}/camera/stream/${selectedCamera}`;
  };

  return (
    <Card sx={{ maxWidth: width + 50, mx: 'auto' }}>
      <CardContent>
        {/* Camera Status Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Videocam color="primary" />
            Server Camera Stream
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
              >
                Settings
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

        {/* Camera Selection */}
        {showControls && availableCameras.length > 1 && (
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Camera</InputLabel>
            <Select
              value={selectedCamera}
              label="Select Camera"
              onChange={(e) => handleCameraChange(e.target.value)}
              disabled={isStreaming}
            >
              {availableCameras.filter(cam => cam.available).map((camera) => (
                <MenuItem key={camera.id} value={camera.id}>
                  {camera.name} - {camera.width}x{camera.height}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* Video Display */}
        <Box sx={{ 
          border: '2px solid #ddd', 
          borderRadius: 2, 
          overflow: 'hidden', 
          backgroundColor: '#000',
          position: 'relative',
          width: width,
          height: height,
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
          <Box sx={{ display: 'flex', gap: 1, mt: 2, justifyContent: 'center' }}>
            {!isStreaming ? (
              <Button
                variant="contained"
                startIcon={isLoading ? <CircularProgress size={20} /> : <Videocam />}
                onClick={startStreaming}
                disabled={isLoading || cameraStatus === 'offline'}
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
              >
                Stop Stream
              </Button>
            )}
            
            <Button
              variant="outlined"
              startIcon={<CameraAlt />}
              onClick={takeSnapshot}
              disabled={!isStreaming || isLoading}
            >
              Snapshot
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadAvailableCameras}
              disabled={isLoading}
            >
              Refresh
            </Button>
          </Box>
        )}

        {/* Status Info */}
        <Box sx={{ mt: 2, p: 1, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="caption" display="block">
            Camera: {selectedCamera} | Status: {isStreaming ? 'Streaming' : 'Stopped'}
          </Typography>
          <Typography variant="caption" display="block">
            Mode: {streamMode.toUpperCase()} | Resolution: {width}x{height}
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