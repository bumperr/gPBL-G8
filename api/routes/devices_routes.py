from fastapi import APIRouter, HTTPException
from api.services.device_service import DeviceService
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/devices", tags=["Smart Home Devices"])

# Initialize service
device_service = DeviceService()

@router.get("/")
async def get_all_devices():
    """Get all active devices"""
    try:
        devices = device_service.get_all_devices()
        return {
            "devices": devices,
            "total": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")

@router.get("/summary")
async def get_device_summary():
    """Get device summary statistics"""
    try:
        summary = device_service.get_device_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device summary: {str(e)}")

@router.get("/categories/{category}")
async def get_devices_by_category(category: str):
    """Get devices by category"""
    try:
        devices = device_service.get_devices_by_category(category)
        return {
            "category": category,
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices by category: {str(e)}")

@router.get("/rooms/{room}")
async def get_devices_by_room(room: str):
    """Get devices by room"""
    try:
        devices = device_service.get_devices_by_room(room)
        return {
            "room": room,
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices by room: {str(e)}")

@router.get("/search")
async def search_devices(q: str):
    """Search devices by query"""
    try:
        devices = device_service.search_devices(q)
        return {
            "query": q,
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search devices: {str(e)}")

@router.get("/{device_id}")
async def get_device_details(device_id: int):
    """Get specific device with its actions"""
    try:
        device = device_service.get_device_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        actions = device_service.get_device_actions(device_id)
        
        return {
            "device": device,
            "actions": actions,
            "total_actions": len(actions)
        }
    except Exception as e:
        if "Device not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get device details: {str(e)}")

@router.post("/{device_id}/test")
async def test_device_command(device_id: int, action_name: str):
    """Test a device command (returns MQTT info without sending)"""
    try:
        device = device_service.get_device_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        action = device_service.get_device_action(device_id, action_name)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        mqtt_info = device_service.get_mqtt_command(device_id, action_name)
        
        return {
            "device": device,
            "action": action,
            "mqtt_topic": mqtt_info[0] if mqtt_info else None,
            "mqtt_payload": mqtt_info[1] if mqtt_info else None,
            "status": "ready_to_send"
        }
    except Exception as e:
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to test command: {str(e)}")

@router.get("/health")
async def devices_health():
    """Health check for device service"""
    try:
        summary = device_service.get_device_summary()
        return {
            "device_service": "active",
            "database": "connected",
            "total_devices": summary['total_devices'],
            "total_actions": summary['total_actions']
        }
    except Exception as e:
        return {
            "device_service": "error",
            "database": "disconnected",
            "error": str(e)
        }