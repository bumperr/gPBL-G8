from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.services.camera_service import camera_service
import io
import base64
import json
from datetime import datetime
from typing import Optional
import asyncio

router = APIRouter(prefix="/camera", tags=["Camera Streaming"])

@router.get("/available")
async def get_available_cameras():
    """Get list of available cameras"""
    try:
        cameras = camera_service.get_available_cameras()
        return {
            "success": True,
            "cameras": cameras,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cameras: {str(e)}")

@router.post("/start/{camera_id}")
async def start_camera(camera_id: int):
    """Start streaming from a specific camera"""
    try:
        success = camera_service.start_camera_stream(camera_id)
        if success:
            return {
                "success": True,
                "message": f"Camera {camera_id} started successfully",
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to start camera {camera_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting camera: {str(e)}")

@router.post("/stop/{camera_id}")
async def stop_camera(camera_id: int):
    """Stop streaming from a specific camera"""
    try:
        success = camera_service.stop_camera_stream(camera_id)
        if success:
            return {
                "success": True,
                "message": f"Camera {camera_id} stopped successfully",
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to stop camera {camera_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping camera: {str(e)}")

@router.get("/frame/{camera_id}")
async def get_camera_frame(camera_id: int = 0):
    """Get the latest frame from a camera as base64 encoded image"""
    try:
        frame_base64 = camera_service.get_latest_frame(camera_id)
        if frame_base64:
            return {
                "success": True,
                "frame": frame_base64,
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat(),
                "format": "jpeg_base64"
            }
        else:
            # Try to start the camera if not active
            if camera_service.start_camera_stream(camera_id):
                # Wait a moment for the camera to initialize
                await asyncio.sleep(0.5)
                frame_base64 = camera_service.get_latest_frame(camera_id)
                if frame_base64:
                    return {
                        "success": True,
                        "frame": frame_base64,
                        "camera_id": camera_id,
                        "timestamp": datetime.now().isoformat(),
                        "format": "jpeg_base64"
                    }
            
            return {
                "success": False,
                "message": f"No frame available from camera {camera_id}",
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting frame: {str(e)}")

@router.get("/snapshot/{camera_id}")
async def take_snapshot(camera_id: int = 0):
    """Take a snapshot from the camera"""
    try:
        snapshot_base64 = camera_service.take_snapshot(camera_id)
        if snapshot_base64:
            return {
                "success": True,
                "snapshot": snapshot_base64,
                "camera_id": camera_id,
                "timestamp": datetime.now().isoformat(),
                "format": "jpeg_base64"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to take snapshot from camera {camera_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error taking snapshot: {str(e)}")

@router.get("/stream/{camera_id}")
async def stream_camera(camera_id: int = 0):
    """Stream camera feed as MJPEG"""
    try:
        def generate_frames():
            # Ensure camera is streaming
            if not camera_service.start_camera_stream(camera_id):
                return
            
            while camera_service.active_streams.get(camera_id, False):
                frame_base64 = camera_service.get_latest_frame(camera_id)
                if frame_base64:
                    # Convert base64 to bytes
                    frame_bytes = base64.b64decode(frame_base64)
                    
                    # Yield frame in MJPEG format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Small delay to control frame rate
                import time
                time.sleep(1/30)  # ~30 FPS
        
        return StreamingResponse(
            generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming camera: {str(e)}")

@router.get("/status")
async def get_camera_status():
    """Get status of all cameras"""
    try:
        status = camera_service.get_camera_status()
        return {
            "success": True,
            **status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting camera status: {str(e)}")

@router.post("/cleanup")
async def cleanup_cameras():
    """Clean up all camera resources"""
    try:
        camera_service.cleanup()
        return {
            "success": True,
            "message": "All cameras cleaned up successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up cameras: {str(e)}")

@router.post("/analyze-vlm/{camera_id}")
async def trigger_vlm_analysis(camera_id: int, elder_id: int = 1):
    """Manually trigger VLM analysis for a camera/video sample"""
    try:
        from api.services.vlm_service import vlm_service
        
        # Check if camera is streaming
        if not camera_service.active_streams.get(camera_id, False):
            return {
                "success": False,
                "message": f"Camera {camera_id} is not currently streaming",
                "camera_id": camera_id
            }
        
        # Get current frame
        current_frame = camera_service.get_latest_frame(camera_id)
        if not current_frame:
            return {
                "success": False,
                "message": f"No frame available from camera {camera_id}",
                "camera_id": camera_id
            }
        
        # Add frame to VLM buffer and trigger analysis
        timestamp = datetime.now().isoformat()
        vlm_service.add_frame_to_buffer(camera_id, current_frame, timestamp)
        vlm_service.queue_analysis(camera_id, elder_id)
        
        return {
            "success": True,
            "message": f"VLM analysis triggered for camera {camera_id}",
            "camera_id": camera_id,
            "elder_id": elder_id,
            "timestamp": timestamp,
            "analysis_queued": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering VLM analysis: {str(e)}")

@router.get("/vlm-status/{camera_id}")
async def get_vlm_status(camera_id: int):
    """Get VLM analysis status for a camera"""
    try:
        from api.services.vlm_service import vlm_service
        
        # Check if camera has frames in VLM buffer
        buffer_size = len(vlm_service.frame_buffer.get(camera_id, []))
        is_streaming = camera_service.active_streams.get(camera_id, False)
        
        # Get camera info
        camera_info = next((c for c in camera_service.camera_info if c['id'] == camera_id), None)
        
        return {
            "success": True,
            "camera_id": camera_id,
            "camera_info": camera_info,
            "is_streaming": is_streaming,
            "vlm_buffer_size": buffer_size,
            "vlm_ready": buffer_size >= 10,
            "analysis_frequency": "Every 15 seconds when streaming",
            "queue_size": vlm_service.analysis_queue.qsize(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting VLM status: {str(e)}")