from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from typing import Optional
import json
from datetime import datetime

router = APIRouter(prefix="/camera", tags=["Camera Streaming"])

# Raspberry Pi Camera Server Configuration
CAMERA_SERVER_HOST = "192.168.1.200"  # Default Raspberry Pi IP
CAMERA_SERVER_PORT = 8080
CAMERA_BASE_URL = f"http://{CAMERA_SERVER_HOST}:{CAMERA_SERVER_PORT}"

class CameraService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_stream_url(self) -> str:
        """Get the camera stream URL"""
        return f"{CAMERA_BASE_URL}/stream.mjpg"
    
    async def check_camera_status(self) -> dict:
        """Check if camera server is accessible"""
        try:
            response = await self.client.get(f"{CAMERA_BASE_URL}/status")
            if response.status_code == 200:
                return {
                    "status": "online",
                    "server": CAMERA_BASE_URL,
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                "status": "offline",
                "server": CAMERA_BASE_URL,
                "error": str(e)
            }
    
    async def get_snapshot(self) -> bytes:
        """Get a single snapshot from camera"""
        try:
            response = await self.client.get(f"{CAMERA_BASE_URL}/snapshot")
            if response.status_code == 200:
                return response.content
            else:
                raise HTTPException(status_code=response.status_code, 
                                  detail=f"Camera server error: {response.status_code}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Camera server unavailable: {str(e)}")
    
    async def control_camera(self, action: str, value: Optional[str] = None) -> dict:
        """Send control commands to camera"""
        try:
            params = {"action": action}
            if value:
                params["value"] = value
                
            response = await self.client.get(f"{CAMERA_BASE_URL}/control", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, 
                                  detail="Camera control failed")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Camera server unavailable: {str(e)}")

# Initialize camera service
camera_service = CameraService()

@router.get("/status")
async def get_camera_status():
    """Get camera server status and connectivity"""
    try:
        status = await camera_service.check_camera_status()
        return {
            "camera_service": status["status"],
            "server_url": CAMERA_BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "details": status
        }
    except Exception as e:
        return {
            "camera_service": "error",
            "server_url": CAMERA_BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/stream-url")
async def get_stream_url():
    """Get the direct stream URL for frontend"""
    stream_url = await camera_service.get_stream_url()
    return {
        "stream_url": stream_url,
        "server": CAMERA_BASE_URL,
        "format": "MJPEG",
        "description": "Elder Care Live Camera Stream"
    }

@router.get("/snapshot")
async def take_snapshot():
    """Take a snapshot from the camera"""
    try:
        image_data = await camera_service.get_snapshot()
        
        return Response(
            content=image_data,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename=eldercare_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snapshot failed: {str(e)}")

@router.post("/control")
async def control_camera(action: str, value: Optional[str] = None):
    """Control camera settings and functions"""
    try:
        result = await camera_service.control_camera(action, value)
        return {
            "status": "success",
            "action": action,
            "value": value,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera control failed: {str(e)}")

@router.get("/settings")
async def get_camera_settings():
    """Get current camera settings"""
    try:
        settings = await camera_service.control_camera("get_settings")
        return {
            "status": "success",
            "settings": settings,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@router.post("/settings")
async def update_camera_settings(
    brightness: Optional[int] = None,
    contrast: Optional[int] = None,
    saturation: Optional[int] = None,
    quality: Optional[int] = None,
    resolution: Optional[str] = None,
    night_vision: Optional[str] = None,
    motion_detection: Optional[str] = None,
    reset: Optional[str] = None
):
    """Update camera settings"""
    try:
        settings_updated = []
        
        if brightness is not None:
            await camera_service.control_camera("brightness", str(brightness))
            settings_updated.append(f"brightness={brightness}")
            
        if contrast is not None:
            await camera_service.control_camera("contrast", str(contrast))
            settings_updated.append(f"contrast={contrast}")
            
        if saturation is not None:
            await camera_service.control_camera("saturation", str(saturation))
            settings_updated.append(f"saturation={saturation}")
            
        if quality is not None:
            await camera_service.control_camera("quality", str(quality))
            settings_updated.append(f"quality={quality}")
            
        if resolution:
            await camera_service.control_camera("resolution", resolution)
            settings_updated.append(f"resolution={resolution}")
            
        if night_vision:
            await camera_service.control_camera("night_vision", night_vision)
            settings_updated.append(f"night_vision={night_vision}")
            
        if motion_detection:
            await camera_service.control_camera("motion_detection", motion_detection)
            settings_updated.append(f"motion_detection={motion_detection}")
            
        if reset:
            await camera_service.control_camera("reset_settings", reset)
            settings_updated.append(f"reset={reset}")
        
        return {
            "status": "success",
            "updated_settings": settings_updated,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings update failed: {str(e)}")

@router.post("/recording/start")
async def start_recording(duration_minutes: Optional[int] = 30):
    """Start recording video"""
    try:
        result = await camera_service.control_camera("start_recording", str(duration_minutes))
        return {
            "status": "recording_started",
            "duration_minutes": duration_minutes,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recording start failed: {str(e)}")

@router.post("/recording/stop")
async def stop_recording():
    """Stop recording video"""
    try:
        result = await camera_service.control_camera("stop_recording")
        return {
            "status": "recording_stopped",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recording stop failed: {str(e)}")

@router.get("/recordings")
async def list_recordings():
    """List available recordings"""
    try:
        result = await camera_service.control_camera("list_recordings")
        return {
            "status": "success",
            "recordings": result.get("recordings", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list recordings: {str(e)}")

@router.get("/health")
async def camera_health_check():
    """Comprehensive camera health check"""
    try:
        status = await camera_service.check_camera_status()
        
        # Test snapshot capability
        try:
            await camera_service.get_snapshot()
            snapshot_test = "pass"
        except:
            snapshot_test = "fail"
            
        # Test settings access
        try:
            await camera_service.control_camera("get_settings")
            settings_test = "pass"
        except:
            settings_test = "fail"
        
        return {
            "overall_status": "healthy" if status["status"] == "online" else "unhealthy",
            "server_connectivity": status["status"],
            "snapshot_capability": snapshot_test,
            "settings_access": settings_test,
            "server_url": CAMERA_BASE_URL,
            "timestamp": datetime.now().isoformat(),
            "tests": {
                "connectivity": status["status"] == "online",
                "snapshot": snapshot_test == "pass",
                "settings": settings_test == "pass"
            }
        }
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Configuration endpoints
@router.get("/config")
async def get_camera_config():
    """Get current camera server configuration"""
    return {
        "camera_server_host": CAMERA_SERVER_HOST,
        "camera_server_port": CAMERA_SERVER_PORT,
        "camera_base_url": CAMERA_BASE_URL,
        "stream_endpoint": "/stream.mjpg",
        "snapshot_endpoint": "/snapshot",
        "control_endpoint": "/control",
        "supported_resolutions": ["640x480", "800x600", "1024x768", "1280x720", "1920x1080"],
        "supported_formats": ["MJPEG", "H264"],
        "features": {
            "live_streaming": True,
            "snapshot_capture": True,
            "video_recording": True,
            "camera_controls": True,
            "settings_adjustment": True,
            "motion_detection": True,
            "night_vision": True,
            "alert_system": True
        }
    }

@router.get("/motion/status")
async def get_motion_detection_status():
    """Get current motion detection status and recent events"""
    try:
        result = await camera_service.control_camera("motion_status")
        return {
            "status": "success",
            "motion_detection_enabled": result.get("enabled", False),
            "recent_motion_events": result.get("events", []),
            "last_motion_time": result.get("last_motion", None),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get motion status: {str(e)}")

@router.post("/alerts/configure")
async def configure_camera_alerts(
    motion_alert: Optional[bool] = True,
    person_detection: Optional[bool] = True,
    fall_detection: Optional[bool] = True,
    sound_alert: Optional[bool] = True,
    alert_threshold: Optional[int] = 70
):
    """Configure camera-based alert system for elder care"""
    try:
        alert_config = {
            "motion_alert": motion_alert,
            "person_detection": person_detection,
            "fall_detection": fall_detection,
            "sound_alert": sound_alert,
            "alert_threshold": alert_threshold
        }
        
        result = await camera_service.control_camera("configure_alerts", json.dumps(alert_config))
        
        return {
            "status": "alerts_configured",
            "configuration": alert_config,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert configuration failed: {str(e)}")

@router.get("/alerts/recent")
async def get_recent_alerts():
    """Get recent camera-based alerts for elder care"""
    try:
        result = await camera_service.control_camera("get_recent_alerts")
        
        return {
            "status": "success",
            "recent_alerts": result.get("alerts", []),
            "alert_count": len(result.get("alerts", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/config")
async def update_camera_config(host: str, port: int = 8080):
    """Update camera server configuration"""
    global CAMERA_SERVER_HOST, CAMERA_SERVER_PORT, CAMERA_BASE_URL
    
    CAMERA_SERVER_HOST = host
    CAMERA_SERVER_PORT = port
    CAMERA_BASE_URL = f"http://{CAMERA_SERVER_HOST}:{CAMERA_SERVER_PORT}"
    
    # Test new configuration
    status = await camera_service.check_camera_status()
    
    return {
        "status": "configuration_updated",
        "new_host": CAMERA_SERVER_HOST,
        "new_port": CAMERA_SERVER_PORT,
        "new_base_url": CAMERA_BASE_URL,
        "connectivity_test": status,
        "timestamp": datetime.now().isoformat()
    }