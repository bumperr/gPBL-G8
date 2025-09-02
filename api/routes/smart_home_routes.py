from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Any
import json
import asyncio
from api.services.mqtt_service import MQTTService

router = APIRouter(prefix="/smart-home", tags=["Smart Home"])

# Active WebSocket connections
active_connections: List[WebSocket] = []

class MQTTCommand(BaseModel):
    topic: str
    payload: str

# MQTT Service instance
mqtt_service = MQTTService()

@router.websocket("/ws/arduino-status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Arduino status WebSocket connected"
        }))
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
            
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.post("/mqtt/send")
async def send_mqtt_command(command: MQTTCommand):
    """Send MQTT command to Arduino"""
    try:
        await mqtt_service.publish_message(command.topic, command.payload)
        
        # Broadcast to all WebSocket connections
        await broadcast_to_websockets({
            "type": "command_sent",
            "topic": command.topic,
            "payload": command.payload,
            "timestamp": mqtt_service._get_timestamp() if hasattr(mqtt_service, '_get_timestamp') else None
        })
        
        return {
            "status": "success",
            "message": f"Command sent to {command.topic}",
            "topic": command.topic,
            "payload": command.payload
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MQTT command failed: {str(e)}")

@router.get("/status")
async def get_smart_home_status():
    """Get current smart home device status"""
    # This could be enhanced to read from a database or cache
    return {
        "lights": {
            "living_room": False,
            "bedroom": False, 
            "kitchen": False,
            "bathroom": False
        },
        "thermostat": {
            "target_temp": 22,
            "current_temp": 23.5,
            "humidity": 65
        },
        "last_updated": mqtt_service._get_timestamp() if hasattr(mqtt_service, '_get_timestamp') else None
    }

@router.post("/lights/{room}/toggle")
async def toggle_room_light(room: str, state: bool):
    """Toggle specific room light"""
    
    # Validate room
    valid_rooms = ['living_room', 'bedroom', 'kitchen', 'bathroom']
    if room not in valid_rooms:
        raise HTTPException(status_code=400, detail=f"Invalid room. Must be one of: {valid_rooms}")
    
    # Map room to MQTT topic (matching Arduino expectations)
    topic = f"home/{room}/lights/cmd"
    payload = "ON" if state else "OFF"
    
    try:
        await mqtt_service.publish_message(topic, payload)
        
        # Broadcast status update
        await broadcast_to_websockets({
            "type": "light_status",
            "room": room,
            "state": payload,
            "timestamp": mqtt_service._get_timestamp() if hasattr(mqtt_service, '_get_timestamp') else None
        })
        
        return {
            "status": "success",
            "room": room,
            "state": payload,
            "topic": topic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Light control failed: {str(e)}")

@router.post("/thermostat/set")  
async def set_thermostat(temperature: float, humidity: float = None):
    """Set thermostat temperature"""
    
    if temperature < 16 or temperature > 30:
        raise HTTPException(status_code=400, detail="Temperature must be between 16°C and 30°C")
    
    try:
        # Send to Arduino via MQTT (matches Arduino expectation)
        payload = f"{temperature},{humidity or 50}"
        await mqtt_service.publish_message("home/room/data", payload)
        
        # Broadcast status update
        await broadcast_to_websockets({
            "type": "thermostat_update", 
            "target_temp": temperature,
            "humidity": humidity,
            "timestamp": mqtt_service._get_timestamp() if hasattr(mqtt_service, '_get_timestamp') else None
        })
        
        return {
            "status": "success",
            "target_temperature": temperature,
            "humidity": humidity,
            "payload": payload
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thermostat control failed: {str(e)}")

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if active_connections:
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in active_connections:
            try:
                await connection.send_text(message_str)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in active_connections:
                active_connections.remove(connection)

# MQTT Message Handler (called by MQTT service when messages arrive)
async def handle_arduino_feedback(topic: str, payload: str):
    """Handle feedback messages from Arduino"""
    try:
        # Parse Arduino feedback
        if topic.endswith("/lights/cmd"):
            room = topic.split("/")[1]  # Extract room from topic
            await broadcast_to_websockets({
                "type": "light_status",
                "room": room,
                "state": payload,
                "source": "arduino_feedback"
            })
            
        elif topic == "home/dht11":
            # Parse sensor data: "temperature,humidity"
            try:
                temp, humidity = payload.split(",")
                await broadcast_to_websockets({
                    "type": "sensor_data",
                    "temperature": float(temp),
                    "humidity": float(humidity),
                    "source": "arduino_sensor"
                })
            except ValueError:
                pass  # Ignore malformed sensor data
                
    except Exception as e:
        print(f"Arduino feedback handling error: {e}")

# Register the feedback handler with MQTT service
if mqtt_service:
    # This would need to be integrated with the MQTT service callback mechanism
    pass