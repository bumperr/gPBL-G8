from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from api.services.mqtt_service import MQTTService

router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.mqtt_service = None
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                await self.disconnect_websocket(connection)
                
    async def disconnect_websocket(self, websocket: WebSocket):
        try:
            await websocket.close()
        except:
            pass
        self.disconnect(websocket)
        
    def set_mqtt_service(self, mqtt_service: MQTTService):
        self.mqtt_service = mqtt_service

manager = WebSocketManager()

@router.websocket("/ws/smart-home")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Get initial state and send to client
    if manager.mqtt_service:
        initial_state = manager.mqtt_service.get_current_state()
        await manager.send_personal_message(json.dumps({
            "type": "initial_state",
            "data": initial_state
        }), websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types from frontend
            if message_data.get("type") == "ping":
                await manager.send_personal_message(json.dumps({
                    "type": "pong"
                }), websocket)
            elif message_data.get("type") == "get_state":
                if manager.mqtt_service:
                    current_state = manager.mqtt_service.get_current_state()
                    await manager.send_personal_message(json.dumps({
                        "type": "state_update",
                        "data": current_state
                    }), websocket)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect_websocket(websocket)

async def broadcast_mqtt_update(topic: str, message: str):
    """Function to be called when MQTT message is received"""
    print(f"Broadcasting MQTT update: {topic} -> {message}")
    
    update_message = {
        "type": "mqtt_update",
        "topic": topic,
        "message": message,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # Also send current state if mqtt_service is available
    if manager.mqtt_service:
        current_state = manager.mqtt_service.get_current_state()
        update_message["current_state"] = current_state
        print(f"Current state: {current_state}")
    
    if len(manager.active_connections) > 0:
        print(f"Broadcasting to {len(manager.active_connections)} WebSocket connections")
        await manager.broadcast(json.dumps(update_message))
    else:
        print("No active WebSocket connections to broadcast to")

# Function to initialize WebSocket manager with MQTT service
def initialize_websocket_with_mqtt(mqtt_service: MQTTService):
    manager.set_mqtt_service(mqtt_service)
    
    # Register callback for real-time updates
    def mqtt_callback(topic: str, message: str):
        """MQTT callback that safely creates async tasks"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(broadcast_mqtt_update(topic, message))
            else:
                loop.run_until_complete(broadcast_mqtt_update(topic, message))
        except Exception as e:
            print(f"Error in MQTT callback for {topic}: {e}")
    
    mqtt_service.register_callback("home/dht11", mqtt_callback)
    mqtt_service.register_callback("home/led/cmd", mqtt_callback) 
    mqtt_service.register_callback("home/thermostat/set", mqtt_callback)
    
    print("WebSocket callbacks registered for Arduino MQTT topics")