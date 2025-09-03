import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Switch,
  Box,
  Slider,
  Chip,
  Button,
  Paper,
  IconButton
} from '@mui/material';
import {
  Lightbulb,
  LightbulbOutlined,
  Thermostat,
  Home,
  Bed,
  Kitchen,
  Bathtub,
  Chair,
  ThermostatAuto
} from '@mui/icons-material';

const SmartHomeControls = ({ elderInfo, onSpeakText }) => {
  // State management for Arduino-connected devices
  const [roomLights, setRoomLights] = useState({
    living_room: false,
    bedroom: false,
    kitchen: false,
    bathroom: false
  });
  
  const [thermostatData, setThermostatData] = useState({
    targetTemp: 22,
    currentTemp: 0,
    humidity: 0
  });

  const [loading, setLoading] = useState({});

  // Room configuration matching Arduino setup
  const roomConfig = {
    living_room: {
      name: 'Living Room',
      icon: <Chair />,
      pin: 8,
      topic: 'home/living_room/lights/cmd',
      color: '#FF9800'
    },
    bedroom: {
      name: 'Bedroom', 
      icon: <Bed />,
      pin: 9,
      topic: 'home/bedroom/lights/cmd',
      color: '#9C27B0'
    },
    kitchen: {
      name: 'Kitchen',
      icon: <Kitchen />,
      pin: 10, 
      topic: 'home/kitchen/lights/cmd',
      color: '#4CAF50'
    },
    bathroom: {
      name: 'Bathroom',
      icon: <Bathtub />,
      pin: 11,
      topic: 'home/bathroom/lights/cmd', 
      color: '#2196F3'
    }
  };

  // WebSocket connection for real-time Arduino feedback
  useEffect(() => {
    const connectWebSocket = () => {
      console.log('🔌 Attempting WebSocket connection to ws://localhost:8000/ws/smart-home');
      const ws = new WebSocket(`ws://localhost:8000/ws/smart-home`);
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
      };
      
      ws.onclose = (event) => {
        console.log('❌ WebSocket disconnected:', event.code, event.reason);
      };
      
      ws.onerror = (error) => {
        console.error('🚨 WebSocket error:', error);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', data);
          
          // Handle initial state from server
          if (data.type === 'initial_state' && data.data) {
            console.log('🏠 Received initial state:', data.data);
            const state = data.data;
            if (state.sensors) {
              setThermostatData(prev => ({
                ...prev,
                currentTemp: state.sensors.temperature || prev.currentTemp,
                humidity: state.sensors.humidity || prev.humidity,
                targetTemp: state.devices?.thermostat_target || prev.targetTemp
              }));
            }
            if (state.devices) {
              setRoomLights({
                living_room: state.devices.living_room_led === 'ON',
                bedroom: state.devices.bedroom_led === 'ON',
                kitchen: state.devices.kitchen_led === 'ON',
                bathroom: state.devices.bathroom_led === 'ON'
              });
            }
          }
          
          // Handle MQTT updates with current state
          if (data.type === 'mqtt_update' && data.current_state) {
            const state = data.current_state;
            
            // Update sensor readings from DHT11
            if (data.topic === 'home/dht11' && state.sensors) {
              console.log('🌡️ DHT11 update received:', state.sensors);
              setThermostatData(prev => ({
                ...prev,
                currentTemp: state.sensors.temperature || prev.currentTemp,
                humidity: state.sensors.humidity || prev.humidity,
                targetTemp: state.devices?.thermostat_target || prev.targetTemp
              }));
            }
            
            // Update LED states from status messages
            if (data.topic.includes('/lights/') && state.devices) {
              setRoomLights({
                living_room: state.devices.living_room_led === 'ON',
                bedroom: state.devices.bedroom_led === 'ON',
                kitchen: state.devices.kitchen_led === 'ON',
                bathroom: state.devices.bathroom_led === 'ON'
              });
            }
          }
          
          // Legacy support for direct sensor data messages
          if (data.type === 'sensor_data') {
            setThermostatData(prev => ({
              ...prev,
              currentTemp: data.temperature || prev.currentTemp,
              humidity: data.humidity || prev.humidity
            }));
          }
          
          // Legacy support for light status messages
          if (data.type === 'light_status') {
            setRoomLights(prev => ({
              ...prev,
              [data.room]: data.state === 'ON'
            }));
          }
        } catch (e) {
          console.log('WebSocket message parse error:', e);
        }
      };

      return ws;
    };

    const ws = connectWebSocket();
    
    // Listen for Take Action optimistic updates
    const handleSmartHomeUpdate = (event) => {
      const { type, room, state, temperature, humidity } = event.detail;
      
      if (type === 'light') {
        console.log(`🎯 Take Action UI update: ${room} light ${state ? 'ON' : 'OFF'}`);
        setRoomLights(prev => ({ ...prev, [room]: state }));
      } else if (type === 'thermostat') {
        console.log(`🎯 Take Action UI update: Thermostat ${temperature}°C`);
        setThermostatData(prev => ({ 
          ...prev, 
          targetTemp: temperature,
          ...(humidity && { humidity: humidity })
        }));
      }
    };
    
    window.addEventListener('smartHomeUpdate', handleSmartHomeUpdate);
    
    return () => {
      ws?.close();
      window.removeEventListener('smartHomeUpdate', handleSmartHomeUpdate);
    };
  }, []);

  // Send MQTT command to Arduino
  const sendArduinoCommand = async (topic, payload, room = null) => {
    try {
      setLoading(prev => ({ ...prev, [room || topic]: true }));

      const response = await fetch('http://localhost:8000/mqtt/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          message: typeof payload === 'string' ? payload : JSON.stringify(payload)
        })
      });

      if (response.ok) {
        // Speak feedback for elder
        if (room && onSpeakText) {
          const roomName = roomConfig[room]?.name || room;
          const action = payload === 'ON' ? 'turned on' : 'turned off';
          onSpeakText(`${roomName} light ${action}`);
        }
      }
    } catch (error) {
      console.error('Arduino command failed:', error);
      if (onSpeakText) {
        onSpeakText('Command failed, please try again');
      }
    } finally {
      setLoading(prev => ({ ...prev, [room || topic]: false }));
    }
  };

  // Handle room light toggle
  const toggleRoomLight = async (room) => {
    const currentState = roomLights[room];
    const newState = !currentState;
    const command = newState ? 'ON' : 'OFF';
    
    // Optimistically update UI
    setRoomLights(prev => ({ ...prev, [room]: newState }));
    
    // Send to Arduino
    await sendArduinoCommand(roomConfig[room].topic, command, room);
  };

  // Handle thermostat change
  const handleThermostatChange = async (newTemp) => {
    setThermostatData(prev => ({ ...prev, targetTemp: newTemp }));
    await sendArduinoCommand('home/room/data', `${newTemp},${thermostatData.humidity}`);
    
    if (onSpeakText) {
      onSpeakText(`Temperature set to ${newTemp} degrees`);
    }
  };

  // Quick action buttons
  const handleAllLightsToggle = async (turnOn) => {
    const command = turnOn ? 'ON' : 'OFF';
    
    // Update all lights optimistically
    const newState = Object.keys(roomLights).reduce((acc, room) => {
      acc[room] = turnOn;
      return acc;
    }, {});
    setRoomLights(newState);

    // Send commands to all rooms
    for (const room of Object.keys(roomConfig)) {
      await sendArduinoCommand(roomConfig[room].topic, command, room);
    }

    if (onSpeakText) {
      onSpeakText(`All lights ${turnOn ? 'turned on' : 'turned off'}`);
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom sx={{ 
        textAlign: 'center',
        mb: 4, 
        color: '#2E7D32',
        fontWeight: 'bold'
      }}>
        🏠 Smart Home Controls
      </Typography>

      {/* Quick Actions */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#388E3C', fontWeight: 'bold' }}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Button
              fullWidth
              size="large"
              variant="contained"
              onClick={() => handleAllLightsToggle(true)}
              sx={{ 
                py: 2, 
                fontSize: '1.1rem',
                backgroundColor: '#4CAF50',
                '&:hover': { backgroundColor: '#45A049' }
              }}
            >
              🌟 Turn All Lights On
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth  
              size="large"
              variant="outlined"
              onClick={() => handleAllLightsToggle(false)}
              sx={{ 
                py: 2, 
                fontSize: '1.1rem',
                borderColor: '#757575',
                color: '#757575'
              }}
            >
              🌙 Turn All Lights Off
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Room Light Controls */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#388E3C', fontWeight: 'bold', mb: 3 }}>
          💡 Room Lights
        </Typography>
        
        <Grid container spacing={3}>
          {Object.entries(roomConfig).map(([roomKey, config]) => {
            const isOn = roomLights[roomKey];
            const isLoading = loading[roomKey];
            
            return (
              <Grid item xs={12} sm={6} md={3} key={roomKey}>
                <Card 
                  sx={{ 
                    height: 160,
                    borderRadius: 3,
                    background: isOn 
                      ? `linear-gradient(135deg, ${config.color}20 0%, ${config.color}40 100%)`
                      : 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
                    border: `3px solid ${isOn ? config.color : '#e0e0e0'}`,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 8px 25px ${config.color}30`
                    },
                    opacity: isLoading ? 0.7 : 1
                  }}
                  onClick={() => !isLoading && toggleRoomLight(roomKey)}
                >
                  <CardContent sx={{ 
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center'
                  }}>
                    <Box sx={{ position: 'relative', mb: 2 }}>
                      <Box sx={{ color: isOn ? config.color : '#bdbdbd', fontSize: '2.5rem' }}>
                        {config.icon}
                      </Box>
                      {isOn ? (
                        <Lightbulb sx={{ 
                          position: 'absolute',
                          top: -10,
                          right: -10,
                          fontSize: '1.5rem',
                          color: '#FFC107',
                          filter: 'drop-shadow(0 0 4px rgba(255,193,7,0.6))'
                        }} />
                      ) : (
                        <LightbulbOutlined sx={{ 
                          position: 'absolute',
                          top: -10,
                          right: -10,
                          fontSize: '1.5rem',
                          color: '#bdbdbd'
                        }} />
                      )}
                    </Box>
                    
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        fontWeight: 'bold',
                        color: isOn ? config.color : '#757575',
                        mb: 1
                      }}
                    >
                      {config.name}
                    </Typography>
                    
                    <Chip 
                      label={isLoading ? 'Loading...' : (isOn ? 'ON' : 'OFF')}
                      size="small"
                      sx={{
                        backgroundColor: isOn ? `${config.color}20` : '#f5f5f5',
                        color: isOn ? config.color : '#757575',
                        fontWeight: 'bold'
                      }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Paper>

      {/* Thermostat Control */}
      <Paper elevation={2} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#388E3C', fontWeight: 'bold', mb: 3 }}>
          🌡️ Temperature Control
        </Typography>
        
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ textAlign: 'center' }}>
              <ThermostatAuto sx={{ fontSize: 60, color: '#FF5722', mb: 2 }} />
              <Typography variant="h3" sx={{ color: '#FF5722', fontWeight: 'bold', mb: 1 }}>
                {thermostatData.targetTemp}°C
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Target Temperature
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ px: 2 }}>
              <Typography variant="body1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Adjust Temperature
              </Typography>
              <Slider
                value={thermostatData.targetTemp}
                onChange={(e, newValue) => handleThermostatChange(newValue)}
                min={16}
                max={30}
                marks={[
                  { value: 18, label: '18°C' },
                  { value: 22, label: '22°C' },
                  { value: 26, label: '26°C' }
                ]}
                valueLabelDisplay="auto"
                sx={{
                  color: '#FF5722',
                  height: 8,
                  '& .MuiSlider-thumb': {
                    height: 24,
                    width: 24,
                  }
                }}
              />
              
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#2196F3' }}>
                    {thermostatData.currentTemp}°C
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Current Temp
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#00BCD4' }}>
                    {thermostatData.humidity}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Humidity
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default SmartHomeControls;