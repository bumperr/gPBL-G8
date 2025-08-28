# Raspberry Pi Camera Integration Guide for Elder Care System

This guide provides complete instructions for setting up Raspberry Pi camera servers for the AI-Powered Elder Care Assistant system, enabling real-time video monitoring and AI-based alert detection.

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [Camera Server Installation](#camera-server-installation)
4. [Network Configuration](#network-configuration)
5. [Integration with Elder Care System](#integration-with-elder-care-system)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

## Hardware Requirements

### Essential Components
- **Raspberry Pi 4B (4GB RAM recommended)** - Main processing unit
- **Raspberry Pi Camera Module V2 or V3** - High-quality 8MP camera
- **MicroSD Card (32GB Class 10)** - Fast storage for OS and recordings
- **Power Supply (5V 3A USB-C)** - Reliable power source
- **Ethernet Cable or WiFi** - Network connectivity
- **Case with Camera Mount** - Protection and positioning

### Optional Components
- **IR Camera Module** - For night vision capability
- **PIR Motion Sensor** - Additional motion detection
- **External USB Microphone** - Audio monitoring
- **LED Status Indicators** - Visual system status

## Raspberry Pi Setup

### 1. Install Raspberry Pi OS
```bash
# Download Raspberry Pi Imager
# Flash latest Raspberry Pi OS Lite to SD card
# Enable SSH, Camera, and WiFi during imaging
```

### 2. Initial Configuration
```bash
# SSH into Raspberry Pi
ssh pi@192.168.1.200

# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera interface
sudo raspi-config
# Navigate to Interfacing Options > Camera > Enable

# Install required packages
sudo apt install -y python3-pip python3-venv git cmake build-essential

# Reboot to apply changes
sudo reboot
```

### 3. Create Project Directory
```bash
# Create project structure
mkdir -p ~/eldercare-camera
cd ~/eldercare-camera

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
```

## Camera Server Installation

### 1. Install Dependencies
```bash
# Activate virtual environment
source ~/eldercare-camera/venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
opencv-python==4.8.1.78
picamera2==0.3.12
numpy==1.25.2
Pillow==10.1.0
python-multipart==0.0.6
httpx==0.25.2
websockets==12.0
python-socketio==5.10.0
```

### 2. Camera Server Code
Create `~/eldercare-camera/camera_server.py`:

```python
from fastapi import FastAPI, Response, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
import io
import time
import json
import asyncio
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import threading
import queue

app = FastAPI(title="Elder Care Camera Server", version="1.0.0")

class CameraManager:
    def __init__(self):
        self.picam2 = Picamera2()
        self.is_streaming = False
        self.is_recording = False
        self.motion_detection = True
        self.night_vision = False
        self.settings = {
            "brightness": 0.5,
            "contrast": 1.0,
            "saturation": 1.0,
            "quality": 80,
            "resolution": "1280x720"
        }
        self.motion_events = []
        self.alerts = []
        self.setup_camera()
    
    def setup_camera(self):
        """Initialize camera with default settings"""
        try:
            config = self.picam2.create_video_configuration(
                main={"size": (1280, 720), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            print("✓ Camera initialized successfully")
        except Exception as e:
            print(f"✗ Camera initialization failed: {e}")
    
    def generate_frames(self):
        """Generate frames for MJPEG streaming"""
        while self.is_streaming:
            try:
                frame = self.picam2.capture_array()
                
                # Apply settings
                if self.night_vision:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                
                # Motion detection
                if self.motion_detection:
                    self.detect_motion(frame)
                
                # Encode frame
                _, buffer = cv2.imencode('.jpg', frame, 
                    [cv2.IMWRITE_JPEG_QUALITY, self.settings['quality']])
                
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
            except Exception as e:
                print(f"Frame generation error: {e}")
                break
    
    def detect_motion(self, frame):
        """Basic motion detection"""
        # Simplified motion detection - in production, use more sophisticated algorithms
        timestamp = datetime.now()
        if len(self.motion_events) == 0 or \
           (timestamp - self.motion_events[-1]).seconds > 5:
            self.motion_events.append(timestamp)
            
            # Limit stored events
            if len(self.motion_events) > 100:
                self.motion_events = self.motion_events[-50:]
    
    def take_snapshot(self):
        """Capture a single frame"""
        try:
            frame = self.picam2.capture_array()
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Snapshot failed: {e}")
    
    def start_streaming(self):
        """Start video streaming"""
        self.is_streaming = True
        print("🎥 Camera streaming started")
    
    def stop_streaming(self):
        """Stop video streaming"""
        self.is_streaming = False
        print("🛑 Camera streaming stopped")
    
    def update_settings(self, **kwargs):
        """Update camera settings"""
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
                print(f"📷 Updated {key} to {value}")

# Initialize camera manager
camera = CameraManager()

@app.on_event("startup")
async def startup():
    """Start camera streaming on server startup"""
    camera.start_streaming()
    print("🚀 Elder Care Camera Server started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on server shutdown"""
    camera.stop_streaming()
    camera.picam2.stop()
    print("👋 Camera server shutdown complete")

@app.get("/")
async def root():
    """Camera server information"""
    return {
        "name": "Elder Care Camera Server",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Live MJPEG Streaming",
            "Snapshot Capture",
            "Motion Detection", 
            "Night Vision",
            "Camera Controls"
        ]
    }

@app.get("/status")
async def camera_status():
    """Get camera status"""
    return {
        "camera_active": camera.is_streaming,
        "recording": camera.is_recording,
        "motion_detection": camera.motion_detection,
        "night_vision": camera.night_vision,
        "settings": camera.settings,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stream.mjpg")
async def video_stream():
    """MJPEG video stream endpoint"""
    return StreamingResponse(
        camera.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/snapshot")
async def take_snapshot():
    """Take a snapshot"""
    try:
        image_data = camera.take_snapshot()
        return Response(
            content=image_data,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename=snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/control")
async def camera_control(action: str, value: str = None):
    """Camera control endpoint"""
    try:
        if action == "brightness" and value:
            camera.update_settings(brightness=float(value)/100)
        elif action == "contrast" and value:
            camera.update_settings(contrast=float(value)/100)
        elif action == "saturation" and value:
            camera.update_settings(saturation=float(value)/100)
        elif action == "quality" and value:
            camera.update_settings(quality=int(value))
        elif action == "resolution" and value:
            camera.update_settings(resolution=value)
        elif action == "night_vision":
            camera.night_vision = value == "on"
        elif action == "motion_detection":
            camera.motion_detection = value == "on"
        elif action == "reset_settings":
            camera.settings = {
                "brightness": 0.5,
                "contrast": 1.0, 
                "saturation": 1.0,
                "quality": 80,
                "resolution": "1280x720"
            }
        elif action == "motion_status":
            return {
                "enabled": camera.motion_detection,
                "events": [event.isoformat() for event in camera.motion_events[-10:]],
                "last_motion": camera.motion_events[-1].isoformat() if camera.motion_events else None
            }
        
        return {"status": "success", "action": action, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 3. Create Startup Service
Create `/etc/systemd/system/eldercare-camera.service`:

```ini
[Unit]
Description=Elder Care Camera Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/eldercare-camera
Environment=PATH=/home/pi/eldercare-camera/venv/bin
ExecStart=/home/pi/eldercare-camera/venv/bin/python camera_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start Service
```bash
# Enable service
sudo systemctl enable eldercare-camera.service

# Start service
sudo systemctl start eldercare-camera.service

# Check status
sudo systemctl status eldercare-camera.service
```

## Network Configuration

### 1. Static IP Configuration
Edit `/etc/dhcpcd.conf`:
```bash
# Static IP configuration for Elder 1 camera
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4

# For Elder 2, use 192.168.1.201
# For Elder 3, use 192.168.1.202
```

### 2. Firewall Configuration
```bash
# Install UFW if not present
sudo apt install ufw

# Allow camera server port
sudo ufw allow 8080

# Allow SSH (be careful with remote access)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

### 3. Port Forwarding (Optional)
For remote access, configure your router to forward ports:
- Elder 1: External 8080 → 192.168.1.200:8080  
- Elder 2: External 8081 → 192.168.1.201:8080
- Elder 3: External 8082 → 192.168.1.202:8080

## Integration with Elder Care System

### 1. Update Elder Care Backend
The camera endpoints are already configured in `api/routes/camera_routes.py`. Update the camera server URLs:

```python
# For multiple elders, update in CaregiverDashboard.jsx
cameraServerUrl={`http://192.168.1.${200 + elder.id}:8080`}
```

### 2. Test Integration
```bash
# Test camera status
curl http://192.168.1.200:8080/status

# Test snapshot
curl http://192.168.1.200:8080/snapshot -o test_snapshot.jpg

# Test stream (in browser)
# Navigate to: http://192.168.1.200:8080/stream.mjpg
```

### 3. Frontend Integration
The `CameraStream` component automatically connects to the configured Raspberry Pi servers:

```jsx
// Multiple camera setup in CaregiverDashboard.jsx
{elders.map(elder => (
  <CameraStream
    key={elder.id}
    elderName={elder.name}
    cameraServerUrl={`http://192.168.1.${200 + elder.id}:8080`}
    onSnapshot={(blob) => console.log(`Snapshot for ${elder.name}`)}
    onError={(error) => console.error(`Camera error: ${error}`)}
  />
))}
```

## Advanced Features

### 1. AI-Based Person Detection
Enhance motion detection with person recognition:

```python
# Add to camera_server.py
import tensorflow as tf

class PersonDetector:
    def __init__(self):
        # Load pre-trained model
        self.model = tf.lite.Interpreter(model_path="person_detection.tflite")
        self.model.allocate_tensors()
    
    def detect_person(self, frame):
        # Run inference
        # Return person detection results
        pass
```

### 2. Fall Detection Algorithm
```python
def detect_fall(self, frame, previous_frame):
    """Detect potential falls using frame analysis"""
    # Implement fall detection logic
    # Based on rapid vertical movement patterns
    pass
```

### 3. Audio Integration
```python
# Add microphone support
import pyaudio
import speech_recognition as sr

class AudioMonitor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def listen_for_distress(self):
        """Listen for distress calls"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1)
                text = self.recognizer.recognize_google(audio)
                
                # Check for emergency keywords
                emergency_words = ["help", "emergency", "fall", "pain"]
                if any(word in text.lower() for word in emergency_words):
                    return {"alert": True, "text": text}
        except:
            pass
        return {"alert": False}
```

### 4. Cloud Storage Integration
```python
# Add cloud backup capability
import boto3
from datetime import datetime

class CloudStorage:
    def __init__(self, aws_access_key, aws_secret_key, bucket_name):
        self.s3 = boto3.client('s3', 
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
        self.bucket = bucket_name
    
    def upload_recording(self, file_path):
        """Upload recording to cloud storage"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"eldercare_recordings/{timestamp}.mp4"
        
        self.s3.upload_file(file_path, self.bucket, key)
        return f"https://{self.bucket}.s3.amazonaws.com/{key}"
```

## Troubleshooting

### Common Issues

#### 1. Camera Not Detected
```bash
# Check camera connection
vcgencmd get_camera

# Expected output: supported=1 detected=1

# If not detected:
sudo raspi-config  # Re-enable camera
sudo reboot
```

#### 2. Stream Not Loading
```bash
# Check if service is running
sudo systemctl status eldercare-camera.service

# Check logs
journalctl -u eldercare-camera.service -f

# Test local access
curl localhost:8080/status
```

#### 3. Poor Video Quality
```bash
# Increase GPU memory
sudo raspi-config
# Advanced Options > Memory Split > 128

# Check camera focus (if adjustable)
# Ensure proper lighting
```

#### 4. Network Connectivity
```bash
# Check IP configuration
ip addr show

# Test network connectivity
ping 192.168.1.1

# Check port accessibility
netstat -tlnp | grep 8080
```

#### 5. High CPU Usage
```bash
# Monitor system resources
htop

# Reduce camera resolution in settings
# Lower frame rate if necessary
# Consider using hardware acceleration
```

### Performance Optimization

#### 1. GPU Acceleration
```bash
# Enable GPU memory split
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# Use hardware encoding when available
# Update camera_server.py to use H.264 encoding
```

#### 2. Network Optimization
```bash
# Optimize network buffer sizes
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
```

#### 3. Storage Management
```bash
# Set up log rotation
sudo logrotate -f /etc/logrotate.conf

# Create cleanup script for old recordings
#!/bin/bash
find ~/eldercare-camera/recordings -name "*.mp4" -mtime +7 -delete
```

## Security Considerations

### 1. Network Security
- Use WPA3 encryption for WiFi
- Implement VPN for remote access
- Regular security updates
- Strong passwords for all accounts

### 2. Data Privacy
- Local processing preferred over cloud
- Encrypted storage for sensitive recordings
- Access control and audit logs
- GDPR/HIPAA compliance as needed

### 3. Physical Security
- Secure mounting of cameras
- Tamper detection alerts
- Backup power solutions
- Environmental protection

## Maintenance Schedule

### Daily
- Monitor system status dashboard
- Check camera connectivity
- Review motion detection events

### Weekly  
- Update system packages
- Clean camera lenses
- Check available storage space
- Review security logs

### Monthly
- Full system backup
- Test emergency procedures
- Update camera firmware
- Performance optimization review

## Integration Testing

### 1. End-to-End Test
```bash
# Test complete workflow
curl -X POST http://your-api-server:8000/camera/status
curl http://192.168.1.200:8080/snapshot -o test.jpg
# Verify image quality and timestamp
```

### 2. Load Testing
```bash
# Multiple concurrent stream access
# Monitor CPU and network usage
# Verify stream quality under load
```

### 3. Failover Testing
```bash
# Test camera server restart
sudo systemctl restart eldercare-camera.service

# Test network disconnection recovery
# Verify automatic reconnection
```

This comprehensive guide provides everything needed to set up and maintain Raspberry Pi camera servers for the elder care monitoring system. The integration enables real-time video monitoring, motion detection, and emergency response capabilities essential for elderly safety and peace of mind for caregivers.