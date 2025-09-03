# AI-Powered Elder Care Assistant

A comprehensive eldercare solution integrating local LLMs with IoT for in-home monitoring, companionship, and remote care. The system features speech-to-text processing, smart home integration via MQTT, emergency detection, and caregiver dashboards.

## 🌟 Features

### Backend (FastAPI + Python)
- **Speech-to-Text**: OpenAI Whisper
- **Local LLM Integration**: Ollama (gemma3:4b) for privacy-preserving AI responses.  Using llava:7b for image processing and interpertation.
- **Smart Home Integration**: Structured MQTT topics for device control 
- **Emergency Detection**: LLm- powered keyword recognition and alerting
- **Live Camera Streaming**: webcam camera integration with MJPEG streaming through websocket
- **Modular Architecture**: Organized blueprints for speech, chat, MQTT, camera, and eldercare

### Frontend (React + Vite)
- **Voice Interface**: Real-time speech recording and transcription
- **Elder-Friendly UI**: Large buttons, clear fonts, accessible design
- **Caregiver Dashboard**: Health monitoring and emergency alerts
- **Live Camera Views**: Multi-elder video monitoring with controls
- **Mobile Responsive**: PWA-ready for mobile devices
- **Real-time Updates**: Live conversation display with AI responses

### Smart Home & Hardware Integration
- **MQTT Communication**: Structured topics for device control
- **Arduino R4 WiFi**: IoT device control and sensor integration

## 📋 Prerequisites

- **Python 3.8+** - For backend API
- **Node.js 16+** - For frontend React app
- **Ollama** - Local LLM runtime
- **MQTT Broker** - Mosquitto or similar (optional but recommended)

## 🚀 Quick Start

'''
cd eldercare-app | npm run dev
'''

'''
venv/Scripts/Activate | python main.py 
'''

'''
mosquitto 
'''

'''
ollama serve
'''
## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Ready to help elders live independently with AI-powered assistance!**
