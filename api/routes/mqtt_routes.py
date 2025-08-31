from fastapi import APIRouter, HTTPException
from api.models.requests import MQTTMessage, EmergencyAlert, SmartHomeCommand, HealthMetric, ElderStatus
from api.services.mqtt_service import MQTTService
import json
from datetime import datetime

router = APIRouter(prefix="/mqtt", tags=["MQTT Communication"])

# MQTT service will be set from main.py
mqtt_service = None

# MQTT Topics Structure for Smart Home Integration
"""
Recommended MQTT Topics Structure:

1. Commands (AI → Smart Home):
   - eldercare/commands/{device_type}/{action}
   - eldercare/commands/lights/turn_on
   - eldercare/commands/thermostat/set_temperature
   - eldercare/commands/locks/lock
   - eldercare/commands/security/arm

2. Emergency (AI → Caregivers/Emergency Services):
   - eldercare/emergency/{severity}
   - eldercare/emergency/critical
   - eldercare/emergency/high
   - eldercare/emergency/medium

3. Health Monitoring (Sensors → AI → Caregivers):
   - eldercare/health/{metric}
   - eldercare/health/heart_rate
   - eldercare/health/blood_pressure
   - eldercare/health/medication
   - eldercare/health/sleep

4. Status Updates (AI → Dashboard):
   - eldercare/status/{elder_name}
   - eldercare/status/{elder_name}/activity
   - eldercare/status/{elder_name}/location
   - eldercare/status/{elder_name}/mood

5. Responses (Smart Home → AI):
   - eldercare/responses/{device_type}/{elder_name}
   - eldercare/responses/lights/john_doe
   - eldercare/responses/thermostat/jane_smith

6. Raw Voice (Backup/Analysis):
   - eldercare/voice/raw/{elder_name}
   - eldercare/voice/processed/{elder_name}
"""

@router.post("/send")
async def send_mqtt_message(request: MQTTMessage):
    """Send a message via MQTT - supports both structured and direct Arduino commands"""
    try:
        # Handle Arduino-compatible topics directly
        if request.topic.startswith("home/"):
            # Direct Arduino MQTT format (e.g., home/led/cmd, home/thermostat/set)
            success = await mqtt_service.publish_message(request.topic, request.message)
        else:
            # Standard structured topics
            success = await mqtt_service.publish_message(request.topic, request.message)
            
        if success:
            return {
                "status": "Message sent successfully" if mqtt_service.client and mqtt_service.client.is_connected() else "Message simulated (MQTT offline)",
                "topic": request.topic,
                "message": request.message,
                "timestamp": datetime.now().isoformat(),
                "simulated": not (mqtt_service.client and mqtt_service.client.is_connected())
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send MQTT message")
    except Exception as e:
        # Always return success for demo purposes when MQTT is down
        print(f"MQTT Exception handled: {e}")
        return {
            "status": "Message simulated (MQTT error handled)",
            "topic": request.topic,
            "message": request.message,
            "timestamp": datetime.now().isoformat(),
            "simulated": True,
            "error": str(e)
        }

@router.post("/emergency")
async def send_emergency_alert(request: EmergencyAlert):
    """Send emergency alert via MQTT"""
    try:
        alert_data = {
            "type": "emergency",
            "elder_name": request.elder_name,
            "message": request.message,
            "severity": request.severity,
            "location": request.location,
            "timestamp": request.timestamp or datetime.now().isoformat()
        }
        
        success = await mqtt_service.publish_message("emergency/alert", json.dumps(alert_data))
        
        if success:
            # Also send to caregiver notification channel
            await mqtt_service.publish_message("caregiver/notifications", json.dumps({
                **alert_data,
                "notification_type": "emergency"
            }))
            
            return {
                "status": "Emergency alert sent successfully",
                "alert": alert_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send emergency alert")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency alert failed: {str(e)}")

@router.get("/status")
async def mqtt_status():
    """Get MQTT service status"""
    return {
        "mqtt_service": "active" if mqtt_service.client and mqtt_service.client.is_connected() else "inactive",
        "broker": mqtt_service.broker,
        "port": mqtt_service.port,
        "subscribed_topics": ["elder/voice", "elder/emergency", "caregiver/commands"]
    }

@router.get("/health")
async def mqtt_health():
    """Health check for MQTT services"""
    try:
        is_connected = mqtt_service.client and mqtt_service.client.is_connected()
        return {
            "mqtt_service": "active" if is_connected else "inactive",
            "connection_status": "connected" if is_connected else "disconnected",
            "broker": mqtt_service.broker
        }
    except Exception as e:
        return {
            "mqtt_service": "error",
            "error": str(e)
        }

# New structured MQTT endpoints for Smart Home Integration

@router.post("/commands/smarthome")
async def send_smarthome_command(request: SmartHomeCommand):
    """Send smart home command via structured MQTT topic"""
    try:
        # Build structured topic: eldercare/commands/{device_type}/{action}
        topic = f"eldercare/commands/{request.device_type}/{request.action}"
        
        command_data = {
            "elder_name": request.elder_name,
            "device_type": request.device_type,
            "action": request.action,
            "parameters": request.parameters or {},
            "room": request.room,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "source": "ai_assistant"
        }
        
        success = await mqtt_service.publish_message(topic, json.dumps(command_data))
        
        if success:
            # Also publish to general commands topic for logging
            await mqtt_service.publish_message(
                f"eldercare/commands/log/{request.elder_name}",
                json.dumps(command_data)
            )
            
            return {
                "status": "Smart home command sent successfully",
                "topic": topic,
                "command": command_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send smart home command")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart home command failed: {str(e)}")

@router.post("/health/metric")
async def send_health_metric(request: HealthMetric):
    """Send health metric via structured MQTT topic"""
    try:
        # Build structured topic: eldercare/health/{metric_type}
        topic = f"eldercare/health/{request.metric_type}"
        
        health_data = {
            "elder_name": request.elder_name,
            "metric_type": request.metric_type,
            "value": request.value,
            "unit": request.unit,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "notes": request.notes,
            "source": "ai_assistant"
        }
        
        success = await mqtt_service.publish_message(topic, json.dumps(health_data))
        
        if success:
            # Also send to elder-specific health topic
            await mqtt_service.publish_message(
                f"eldercare/health/{request.elder_name}/{request.metric_type}",
                json.dumps(health_data)
            )
            
            return {
                "status": "Health metric sent successfully",
                "topic": topic,
                "metric": health_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send health metric")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health metric failed: {str(e)}")

@router.post("/status/elder")
async def send_elder_status(request: ElderStatus):
    """Send elder status update via structured MQTT topic"""
    try:
        # Build structured topic: eldercare/status/{elder_name}/{status_type}
        topic = f"eldercare/status/{request.elder_name}/{request.status_type}"
        
        status_data = {
            "elder_name": request.elder_name,
            "status_type": request.status_type,
            "status_value": request.status_value,
            "confidence": request.confidence,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "additional_data": request.additional_data or {},
            "source": "ai_assistant"
        }
        
        success = await mqtt_service.publish_message(topic, json.dumps(status_data))
        
        if success:
            # Also send to general elder status topic for dashboard
            await mqtt_service.publish_message(
                f"eldercare/status/{request.elder_name}",
                json.dumps(status_data)
            )
            
            return {
                "status": "Elder status sent successfully",
                "topic": topic,
                "status": status_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send elder status")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Elder status failed: {str(e)}")

@router.post("/emergency/structured")
async def send_structured_emergency(request: EmergencyAlert):
    """Send emergency alert via structured MQTT topic"""
    try:
        # Build structured topic: eldercare/emergency/{severity}
        topic = f"eldercare/emergency/{request.severity}"
        
        emergency_data = {
            "elder_name": request.elder_name,
            "message": request.message,
            "severity": request.severity,
            "location": request.location,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "source": "ai_assistant",
            "requires_response": request.severity in ["critical", "high"]
        }
        
        success = await mqtt_service.publish_message(topic, json.dumps(emergency_data))
        
        if success:
            # Send to multiple channels based on severity
            channels = [
                f"eldercare/emergency/alerts/{request.elder_name}",
                "eldercare/emergency/all",
                f"caregiver/emergency/{request.elder_name}"
            ]
            
            # For critical/high severity, also send to emergency services topic
            if request.severity in ["critical", "high"]:
                channels.append("emergency_services/alerts")
            
            for channel in channels:
                await mqtt_service.publish_message(channel, json.dumps(emergency_data))
            
            return {
                "status": "Structured emergency alert sent successfully",
                "topic": topic,
                "channels": channels,
                "emergency": emergency_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send structured emergency alert")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structured emergency alert failed: {str(e)}")

@router.get("/topics")
async def get_mqtt_topics():
    """Get all available MQTT topics structure"""
    return {
        "mqtt_topics_structure": {
            "commands": {
                "pattern": "eldercare/commands/{device_type}/{action}",
                "examples": [
                    "eldercare/commands/lights/turn_on",
                    "eldercare/commands/thermostat/set_temperature",
                    "eldercare/commands/locks/lock",
                    "eldercare/commands/security/arm"
                ],
                "device_types": ["lights", "thermostat", "locks", "security", "entertainment", "appliances"]
            },
            "emergency": {
                "pattern": "eldercare/emergency/{severity}",
                "examples": [
                    "eldercare/emergency/critical",
                    "eldercare/emergency/high",
                    "eldercare/emergency/medium",
                    "eldercare/emergency/low"
                ],
                "severities": ["critical", "high", "medium", "low"]
            },
            "health": {
                "pattern": "eldercare/health/{metric}",
                "examples": [
                    "eldercare/health/heart_rate",
                    "eldercare/health/blood_pressure",
                    "eldercare/health/medication",
                    "eldercare/health/sleep",
                    "eldercare/health/steps"
                ],
                "metrics": ["heart_rate", "blood_pressure", "medication", "sleep", "steps", "weight", "temperature"]
            },
            "status": {
                "pattern": "eldercare/status/{elder_name}/{status_type}",
                "examples": [
                    "eldercare/status/john_doe/activity",
                    "eldercare/status/jane_smith/location",
                    "eldercare/status/bob_johnson/mood"
                ],
                "status_types": ["activity", "location", "mood", "emergency", "health"]
            },
            "responses": {
                "pattern": "eldercare/responses/{device_type}/{elder_name}",
                "examples": [
                    "eldercare/responses/lights/john_doe",
                    "eldercare/responses/thermostat/jane_smith"
                ]
            },
            "voice": {
                "pattern": "eldercare/voice/{type}/{elder_name}",
                "examples": [
                    "eldercare/voice/raw/john_doe",
                    "eldercare/voice/processed/jane_smith"
                ]
            }
        },
        "integration_notes": {
            "home_assistant": "Use MQTT discovery or manual configuration with these topics",
            "node_red": "Create flows subscribing to eldercare/# for all messages",
            "openhab": "Configure MQTT binding with eldercare topic prefix"
        }
    } # type: ignore

# Arduino Integration Bridge - Direct compatibility with existing Arduino code
@router.post("/arduino/led")
async def control_arduino_led(state: str):
    """Direct Arduino LED control - matches Arduino script.ino expectations"""
    try:
        command = state.upper()  # ON or OFF
        if command not in ["ON", "OFF"]:
            raise HTTPException(status_code=400, detail="State must be 'ON' or 'OFF'")
            
        success = await mqtt_service.publish_message("home/led/cmd", command)
        
        if success:
            return {
                "status": f"Arduino LED turned {command}",
                "topic": "home/led/cmd",
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to control Arduino LED")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arduino LED control failed: {str(e)}")

@router.post("/arduino/thermostat") 
async def control_arduino_thermostat(temperature: int):
    """Arduino thermostat control - sends temperature to home/thermostat/set"""
    try:
        if not (16 <= temperature <= 30):
            raise HTTPException(status_code=400, detail="Temperature must be between 16-30°C")
            
        success = await mqtt_service.publish_message("home/thermostat/set", str(temperature))
        
        if success:
            return {
                "status": f"Arduino thermostat set to {temperature}°C",
                "topic": "home/thermostat/set", 
                "temperature": temperature,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to control Arduino thermostat")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arduino thermostat control failed: {str(e)}")

@router.get("/arduino/sensors")
async def get_arduino_sensors():
    """Get latest Arduino sensor data (DHT11 from home/dht11 topic)"""
    try:
        current_state = mqtt_service.get_current_state()
        return {
            "status": "Arduino sensors data",
            "topic": "home/dht11",
            "data": {
                "temperature": current_state["sensors"]["temperature"],
                "humidity": current_state["sensors"]["humidity"],
                "raw_payload": f"{current_state['sensors']['temperature']},{current_state['sensors']['humidity']}",
                "last_update": current_state["sensors"]["last_update"]
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Real-time sensor data from Arduino DHT11"
        }
    except Exception as e:
        return {
            "status": "Error getting sensor data",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/arduino/state")
async def get_arduino_state():
    """Get complete current Arduino/smart home state"""
    try:
        current_state = mqtt_service.get_current_state()
        return {
            "status": "Smart home state",
            "data": current_state,
            "timestamp": datetime.now().isoformat(),
            "mqtt_connection": "connected" if mqtt_service.client and mqtt_service.client.is_connected() else "disconnected",
            "mqtt_topics": {
                "sensors": "home/dht11",
                "led_control": "home/led/cmd", 
                "thermostat_control": "home/thermostat/set"
            }
        }
    except Exception as e:
        return {
            "status": "Error getting smart home state",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/debug/mqtt-status")
async def debug_mqtt_status():
    """Debug endpoint to check MQTT connection and recent messages"""
    try:
        is_connected = mqtt_service.client and mqtt_service.client.is_connected()
        current_state = mqtt_service.get_current_state()
        
        return {
            "mqtt_connected": is_connected,
            "mqtt_broker": mqtt_service.broker,
            "mqtt_port": mqtt_service.port,
            "current_state": current_state,
            "subscribed_topics": [
                "elder/voice", "elder/emergency", "caregiver/commands",
                "home/dht11", "home/led/status", "home/thermostat/status", "home/+/+"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


