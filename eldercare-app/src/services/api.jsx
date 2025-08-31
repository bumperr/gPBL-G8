import axios from 'axios';

const API_BASE_URL = '/api';


const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check
  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Chat with AI
  async sendChatMessage(message, model = 'gemma3:4b') {
    try {
      const response = await api.post('/chat', {
        message,
        model
      });
      return response.data;
    } catch (error) {
      console.error('Chat request failed:', error);
      throw error;
    }
  },

  // Speech to Text
  async speechToText(audioData, language = 'en', model = 'whisper') {
    try {
      const response = await api.post('/speech/transcribe', {
        audio_data: audioData,
        language,
        model
      });
      return response.data;
    } catch (error) {
      console.error('Speech-to-text request failed:', error);
      throw error;
    }
  },

  // Voice assistance for elders
  async processElderSpeech(audioData, elderInfo, language = 'en') {
    try {
      const response = await api.post('/eldercare/voice-assistance', {
        audio_data: audioData,
        elder_info: elderInfo,
        language
      });
      return response.data;
    } catch (error) {
      console.error('Voice assistance failed:', error);
      throw error;
    }
  },

  // Text assistance for elders with mental health focus
  async processElderText(message, elderInfo) {
    try {
      const response = await api.post('/eldercare/text-assistance', {
        message,
        elder_info: elderInfo
      });
      return response.data;
    } catch (error) {
      console.error('Text assistance failed:', error);
      throw error;
    }
  },

  // Send MQTT message
  async sendMQTTMessage(topic, message) {
    try {
      const response = await api.post('/mqtt/send', {
        topic,
        message
      });
      return response.data;
    } catch (error) {
      console.error('MQTT message failed:', error);
      throw error;
    }
  },

  // Get available models
  async getModels() {
    try {
      const response = await api.get('/chat/models');
      return response.data;
    } catch (error) {
      console.error('Get models failed:', error);
      throw error;
    }
  },

  // Emergency alert (updated)
  async sendManualEmergency(elderName, message, severity = 'high', location = null) {
    try {
      const response = await api.post('/eldercare/manual-emergency', {
        elder_name: elderName,
        message,
        severity,
        location,
        timestamp: new Date().toISOString()
      });
      return response.data;
    } catch (error) {
      console.error('Manual emergency alert failed:', error);
      throw error;
    }
  },

  // Emergency alert
  async sendEmergencyAlert(message, location, elderInfo) {
    try {
      const emergencyData = {
        type: 'emergency',
        message,
        location,
        elderInfo,
        timestamp: new Date().toISOString(),
        priority: 'high'
      };
      
      const response = await api.post('/mqtt/send', {
        topic: 'emergency/alerts',
        message: JSON.stringify(emergencyData)
      });
      return response.data;
    } catch (error) {
      console.error('Emergency alert failed:', error);
      throw error;
    }
  },

  // Health monitoring data
  async sendHealthData(vitals, elderInfo) {
    try {
      const healthData = {
        type: 'health_monitoring',
        vitals,
        elderInfo,
        timestamp: new Date().toISOString()
      };
      
      const response = await api.post('/mqtt/send', {
        topic: 'health/monitoring',
        message: JSON.stringify(healthData)
      });
      return response.data;
    } catch (error) {
      console.error('Health data sending failed:', error);
      throw error;
    }
  },

  // Smart home control
  async controlSmartHome(device, action, value) {
    try {
      const controlData = {
        type: 'smart_home_control',
        device,
        action,
        value,
        timestamp: new Date().toISOString()
      };
      
      const response = await api.post('/mqtt/send', {
        topic: 'smarthome/control',
        message: JSON.stringify(controlData)
      });
      return response.data;
    } catch (error) {
      console.error('Smart home control failed:', error);
      throw error;
    }
  },

  // Enhanced chat with different types and image support
  async enhancedChat(data) {
    try {
      const response = await api.post('/chat/', data);
      return response.data;
    } catch (error) {
      console.error('Enhanced chat failed:', error);
      throw error;
    }
  },

  // Chat with image upload
  async chatWithImage(formData) {
    try {
      const response = await api.post('/chat/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Image chat failed:', error);
      throw error;
    }
  },

  // Legacy chat (backward compatibility)
  async legacyChat(message, model) {
    try {
      const response = await api.post('/chat/legacy', {
        message,
        model
      });
      return response.data;
    } catch (error) {
      console.error('Legacy chat failed:', error);
      throw error;
    }
  },

  // Device management
  async getDevices() {
    try {
      const response = await api.get('/devices');
      return response.data;
    } catch (error) {
      console.error('Get devices failed:', error);
      throw error;
    }
  },

  async getDevicesByRoom(room) {
    try {
      const response = await api.get(`/devices/rooms/${room}`);
      return response.data;
    } catch (error) {
      console.error('Get devices by room failed:', error);
      throw error;
    }
  },

  async getDevicesByCategory(category) {
    try {
      const response = await api.get(`/devices/categories/${category}`);
      return response.data;
    } catch (error) {
      console.error('Get devices by category failed:', error);
      throw error;
    }
  },

  async getDeviceDetails(deviceId) {
    try {
      const response = await api.get(`/devices/${deviceId}`);
      return response.data;
    } catch (error) {
      console.error('Get device details failed:', error);
      throw error;
    }
  },

  async searchDevices(query) {
    try {
      const response = await api.get(`/devices/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Search devices failed:', error);
      throw error;
    }
  },

  async getDeviceSummary() {
    try {
      const response = await api.get('/devices/summary');
      return response.data;
    } catch (error) {
      console.error('Get device summary failed:', error);
      throw error;
    }
  }
};

export default apiService;