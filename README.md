# AI-Powered Elder Care Assistant

A comprehensive eldercare solution integrating local LLMs with IoT for in-home monitoring, companionship, and remote care. The system features speech-to-text processing, smart home integration via MQTT, emergency detection, and caregiver dashboards.

## 🌟 Features

### Backend (FastAPI + Python)
- **Speech-to-Text**: OpenAI Whisper + Google Speech Recognition
- **Local LLM Integration**: Ollama (Llama 3.2) for privacy-preserving AI responses
- **Smart Home Integration**: Structured MQTT topics for device control
- **Emergency Detection**: AI-powered keyword recognition and alerting
- **Health Monitoring**: Vital signs tracking and analysis
- **Live Camera Streaming**: Raspberry Pi camera integration with MJPEG streaming
- **Motion Detection & Alerts**: Real-time person detection and fall alerts
- **Modular Architecture**: Organized blueprints for speech, chat, MQTT, camera, and eldercare

### Frontend (React + Vite)
- **Voice Interface**: Real-time speech recording and transcription
- **Elder-Friendly UI**: Large buttons, clear fonts, accessible design
- **Caregiver Dashboard**: Health monitoring and emergency alerts
- **Live Camera Views**: Multi-elder video monitoring with controls
- **Camera Controls**: Brightness, contrast, resolution, night vision settings
- **Motion Alerts**: Real-time notifications with snapshot capture
- **Mobile Responsive**: PWA-ready for mobile devices
- **Real-time Updates**: Live conversation display with AI responses

### Smart Home & Hardware Integration
- **MQTT Communication**: Structured topics for device control
- **Home Assistant Ready**: Complete configuration examples
- **Node-RED Flows**: Visual programming integration
- **Raspberry Pi Cameras**: Multi-location video monitoring
- **Arduino R4 WiFi**: IoT device control and sensor integration
- **Multi-Platform Support**: OpenHAB, Node-RED, Home Assistant

## 📋 Prerequisites

- **Python 3.8+** - For backend API
- **Node.js 16+** - For frontend React app
- **Ollama** - Local LLM runtime
- **MQTT Broker** - Mosquitto or similar (optional but recommended)
- **Raspberry Pi 4** - For camera servers (optional but recommended for video monitoring)

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Clone and navigate to project
cd Vietnam

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Download and start Ollama model
ollama pull llama3.2
ollama serve  # In separate terminal
```

### 2. Frontend Setup

```bash
# Navigate to React app
cd eldercare-app

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your backend URL if different from localhost:8000
```

### 3. Start the System

**Option 1: Using Batch Files (Windows)**
```bash
# Start backend
start_server.bat

# Start frontend (in new terminal)
cd eldercare-app
start-dev.bat
```

**Option 2: Manual Start**
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd eldercare-app
npm run dev
```

### 4. Access the Applications

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend App**: http://localhost:3000
- **Caregiver Dashboard**: http://localhost:3000/caregiver (includes live camera feeds)

## 📱 Mobile Access

### Access Web App on Mobile

1. **Find Your Computer's IP Address**:
   ```bash
   # Windows
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   
   # Linux/Mac
   ifconfig
   # Look for inet address
   ```

2. **Update Environment Variables**:
   ```bash
   # In eldercare-app/.env
   VITE_API_URL=http://YOUR_IP_ADDRESS:8000
   ```

3. **Start with Network Access**:
   ```bash
   # Backend (accessible from network)
   python main.py  # Already binds to 0.0.0.0:8000
   
   # Frontend (accessible from network)
   npm run dev -- --host 0.0.0.0
   ```

4. **Access from Mobile Device**:
   - **Frontend**: `http://YOUR_IP_ADDRESS:3000`
   - **API Docs**: `http://YOUR_IP_ADDRESS:8000/docs`

### PWA Installation

1. Open the web app in mobile browser
2. Look for "Add to Home Screen" prompt
3. Follow browser-specific installation steps
4. App will behave like a native mobile app

## 🔧 Testing the API

### Using FastAPI Interactive Documentation

1. **Access Swagger UI**: http://localhost:8000/docs
2. **Explore Endpoints**: Click on any endpoint to expand
3. **Try It Out**: Click "Try it out" button on any endpoint
4. **Execute Requests**: Fill parameters and click "Execute"

### Key Endpoints to Test

#### 1. Health Check
```bash
GET /health
# Tests all service connectivity
```

#### 2. Speech-to-Text
```bash
POST /speech/transcribe
{
  "audio_data": "base64_encoded_audio",
  "language": "en",
  "model": "whisper"
}
```

#### 3. Elder Voice Assistance
```bash
POST /eldercare/voice-assistance
{
  "audio_data": "base64_encoded_audio",
  "elder_info": {
    "name": "John Doe",
    "age": 75
  },
  "language": "en"
}
```

#### 4. Smart Home Control
```bash
POST /mqtt/commands/smarthome
{
  "elder_name": "john_doe",
  "device_type": "lights",
  "action": "turn_on",
  "parameters": {"brightness": 80},
  "room": "bedroom"
}
```

#### 5. Emergency Alert
```bash
POST /mqtt/emergency/structured
{
  "elder_name": "jane_smith",
  "message": "Fall detected in bathroom",
  "severity": "high",
  "location": "bathroom"
}
```

### Using cURL Commands

```bash
# Test basic connectivity
curl http://localhost:8000/health

# Test AI chat
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how can you help me?", "model": "llama3.2"}'

# Test smart home command
curl -X POST "http://localhost:8000/mqtt/commands/smarthome" \
  -H "Content-Type: application/json" \
  -d '{
    "elder_name": "test_user",
    "device_type": "lights", 
    "action": "turn_on",
    "room": "living_room"
  }'

# Get MQTT topics structure
curl http://localhost:8000/mqtt/topics

# Test camera endpoints
curl http://localhost:8000/camera/status
curl http://localhost:8000/camera/stream-url
curl http://localhost:8000/camera/snapshot -o snapshot.jpg
```

## 🏠 Smart Home Integration

### Home Assistant Setup

1. **Copy Configuration**:
   ```bash
   cp integration_examples/home_assistant_config.yaml /path/to/homeassistant/
   ```

2. **Configure MQTT Broker** in Home Assistant:
   ```yaml
   mqtt:
     broker: YOUR_MQTT_BROKER_IP
     port: 1883
     discovery: true
   ```

3. **Restart Home Assistant** and check MQTT integration

### Node-RED Setup

1. **Import Flows**:
   - Copy `integration_examples/node_red_flows.json`
   - Import in Node-RED interface

2. **Configure MQTT Broker** in Node-RED flows

3. **Deploy Flows** and test device control

### Raspberry Pi Camera Setup

1. **Set up Camera Servers** (one per elder):
   ```bash
   # Follow detailed instructions in:
   # RASPBERRY_PI_CAMERA_INTEGRATION.md
   
   # Quick setup on each Raspberry Pi:
   sudo apt update && sudo apt upgrade -y
   sudo raspi-config  # Enable camera
   
   # Install camera server (details in integration guide)
   # Configure different IP addresses:
   # Elder 1: 192.168.1.200:8080
   # Elder 2: 192.168.1.201:8080
   # Elder 3: 192.168.1.202:8080
   ```

2. **Test Camera Integration**:
   ```bash
   # Test each camera server
   curl http://192.168.1.200:8080/status
   curl http://192.168.1.200:8080/stream.mjpg
   ```

3. **Configure in Frontend**:
   - Camera streams automatically load in Caregiver Dashboard
   - Each elder gets dedicated camera server
   - Controls available for brightness, contrast, resolution

## 🛠 Development & Customization

### Adding New Device Types

1. **Update MQTT Topics**:
   ```python
   # In api/routes/mqtt_routes.py
   "device_types": ["lights", "thermostat", "locks", "your_new_device"]
   ```

2. **Add Device Logic**:
   ```python
   # In smart home integration
   elif device_type == "your_new_device":
       # Handle device-specific commands
   ```

### Customizing Elder Care Responses

1. **Edit AI Prompts**:
   ```python
   # In api/services/ai_service.py
   enhanced_prompt = f"""
   You are a caring AI assistant helping {elder_name}.
   # Customize prompt here
   """
   ```

2. **Add Emergency Keywords**:
   ```python
   # In api/services/ai_service.py
   emergency_keywords = ['help', 'emergency', 'fall', 'your_new_keyword']
   ```

## 📊 Monitoring & Logging

### Health Monitoring
- **Backend Health**: http://localhost:8000/health
- **Service Status**: Check individual service endpoints
- **MQTT Status**: http://localhost:8000/mqtt/status
- **Camera Health**: http://localhost:8000/camera/health

### Log Files
```bash
# View application logs
tail -f logs/eldercare.log  # If logging is configured

# MQTT broker logs
sudo journalctl -u mosquitto -f  # Linux systemd
```

## 🔒 Security Considerations

### Production Deployment

1. **Enable HTTPS**:
   ```bash
   # Use reverse proxy (nginx/Apache) with SSL certificates
   # Or configure Uvicorn with SSL
   uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

2. **MQTT Security**:
   ```bash
   # Enable MQTT authentication and TLS
   # Configure in mosquitto.conf
   ```

3. **Environment Variables**:
   ```bash
   # Store sensitive data in environment variables
   export MQTT_USERNAME=your_username
   export MQTT_PASSWORD=your_password
   ```

## ❓ Troubleshooting

### Common Issues

**Backend Issues**:
- **Ollama not responding**: Ensure `ollama serve` is running
- **MQTT connection failed**: Check if MQTT broker is running
- **Speech recognition errors**: Check microphone permissions

**Frontend Issues**:
- **App not loading**: Check if backend is running on correct port
- **Voice recording not working**: Enable microphone permissions in browser
- **API calls failing**: Verify VITE_API_URL in .env file
- **Camera not streaming**: Check Raspberry Pi camera server status and network connectivity

**Mobile Issues**:
- **Can't access from mobile**: Check firewall settings and use correct IP
- **Voice recording on mobile**: Ensure HTTPS for microphone access in production

### Debug Commands

```bash
# Check if services are running
netstat -an | grep :8000  # Backend
netstat -an | grep :3000  # Frontend
netstat -an | grep :1883  # MQTT

# Test MQTT connectivity
mosquitto_pub -h localhost -t test/topic -m "test message"
mosquitto_sub -h localhost -t eldercare/#

# Check Ollama models
ollama list

# Test camera server connectivity
curl http://192.168.1.200:8080/status
ping 192.168.1.200
```

## 📚 Additional Resources

- **Camera Integration Guide**: `RASPBERRY_PI_CAMERA_INTEGRATION.md`
- **Arduino MQTT Integration**: `ARDUINO_MQTT_INTEGRATION.md`
- **MQTT Topics Documentation**: `MQTT_TOPICS_DOCUMENTATION.md`
- **Refactoring Summary**: `REFACTORING_SUMMARY.md`
- **Vite Migration**: `eldercare-app/VITE_MIGRATION_SUMMARY.md`
- **Integration Examples**: `integration_examples/` directory

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Ready to help elders live independently with AI-powered assistance!**