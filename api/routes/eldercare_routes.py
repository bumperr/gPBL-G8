from fastapi import APIRouter, HTTPException
from api.models.requests import EmergencyAlert
from api.services.mqtt_service import MQTTService
from api.services.ai_service import AIService
from api.services.eldercare_service import EldercareService
import json
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/eldercare", tags=["Elder Care"])

# Initialize services
mqtt_service = MQTTService()
ai_service = AIService()
eldercare_service = EldercareService()

@router.post("/voice-assistance")
async def voice_assistance(request: Dict[str, Any]):
    """Complete voice assistance workflow for elders"""
    try:
        # Extract request data
        audio_data = request.get('audio_data')
        elder_info = request.get('elder_info', {})
        language = request.get('language', 'en')
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Import speech service
        from api.services.speech_service import SpeechToTextService
        speech_service = SpeechToTextService()
        
        # Transcribe audio
        transcription = await speech_service.transcribe_audio(audio_data, language)
        
        if not transcription.get('text'):
            return {
                "status": "error",
                "message": "Could not understand the audio",
                "transcription": transcription
            }
        
        # Process with AI
        ai_response = await ai_service.process_elder_speech(
            transcription['text'],
            elder_info
        )
        
        # Prepare response
        response_data = {
            "status": "success",
            "transcription": transcription,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Handle emergency situations
        if ai_response.get('is_emergency'):
            emergency_alert = {
                "type": "voice_emergency",
                "elder_name": elder_info.get('name', 'Unknown Elder'),
                "transcription": transcription['text'],
                "ai_assessment": ai_response['response'],
                "severity": "high",
                "timestamp": datetime.now().isoformat(),
                "location": elder_info.get('location')
            }
            
            # Send emergency alert
            await mqtt_service.publish_message("emergency/alert", json.dumps(emergency_alert))
            await mqtt_service.publish_message("caregiver/notifications", json.dumps({
                **emergency_alert,
                "notification_type": "emergency"
            }))
            
            response_data["emergency_alert"] = emergency_alert
        
        # Publish regular interaction to MQTT for caregivers
        interaction_log = {
            "type": "elder_interaction",
            "elder_name": elder_info.get('name', 'Unknown Elder'),
            "transcription": transcription['text'],
            "ai_response": ai_response['response'],
            "confidence": transcription.get('confidence', 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await mqtt_service.publish_message("elder/interactions", json.dumps(interaction_log))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice assistance failed: {str(e)}")

@router.post("/text-assistance")
async def text_assistance(request: Dict[str, Any]):
    """Enhanced text assistance workflow for elders with mental health focus"""
    try:
        # Extract request data
        message = request.get('message')
        elder_info = request.get('elder_info', {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process with enhanced AI service
        ai_response = await ai_service.process_elder_text(message, elder_info)
        
        # Prepare response with enhanced data
        response_data = {
            "status": "success",
            "message": message,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "elder_info": elder_info
        }
        
        # Handle emergency situations
        if ai_response.get('is_emergency'):
            emergency_data = {
                "elder_name": elder_info.get('name', 'Unknown Elder'),
                "message": f"Text emergency detected: {message}",
                "severity": "high",
                "location": elder_info.get('location', 'Unknown'),
                "timestamp": datetime.now().isoformat(),
                "intent_detected": ai_response.get('intent_detected'),
                "suggested_action": ai_response.get('suggested_action')
            }
            
            # Send MQTT emergency alert
            if mqtt_service:
                try:
                    topic = f"eldercare/emergency/{elder_info.get('name', 'unknown').lower().replace(' ', '_')}"
                    await mqtt_service.publish_message(topic, json.dumps(emergency_data))
                    response_data["emergency_alert"] = emergency_data
                    response_data["mqtt_sent"] = True
                except Exception as mqtt_error:
                    response_data["mqtt_error"] = str(mqtt_error)
                    response_data["mqtt_sent"] = False
        
        # Log interaction for caregivers with mental health data
        interaction_log = {
            "type": "text_interaction",
            "elder_name": elder_info.get('name', 'Unknown Elder'),
            "message": message,
            "ai_response": ai_response['response'],
            "intent_detected": ai_response.get('intent_detected'),
            "confidence_score": ai_response.get('confidence_score'),
            "mental_health_assessment": ai_response.get('mental_health_assessment'),
            "suggested_action": ai_response.get('suggested_action'),
            "timestamp": datetime.now().isoformat()
        }
        
        if mqtt_service:
            try:
                await mqtt_service.publish_message("elder/interactions", json.dumps(interaction_log))
            except Exception as mqtt_error:
                print(f"MQTT logging failed: {mqtt_error}")
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text assistance failed: {str(e)}")

@router.post("/manual-emergency")
async def manual_emergency(request: EmergencyAlert):
    """Manually trigger emergency alert"""
    try:
        alert_data = {
            "type": "manual_emergency",
            "elder_name": request.elder_name,
            "message": request.message,
            "severity": request.severity,
            "location": request.location,
            "timestamp": request.timestamp or datetime.now().isoformat()
        }
        
        # Send to multiple channels
        await mqtt_service.publish_message("emergency/alert", json.dumps(alert_data))
        await mqtt_service.publish_message("caregiver/notifications", json.dumps({
            **alert_data,
            "notification_type": "emergency"
        }))
        
        return {
            "status": "Emergency alert sent",
            "alert": alert_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency alert failed: {str(e)}")

@router.get("/elder-status/{elder_name}")
async def get_elder_status(elder_name: str):
    """Get current status of an elder"""
    # This would typically connect to a database or monitoring system
    # For now, return a placeholder response
    return {
        "elder_name": elder_name,
        "status": "active",
        "last_interaction": "2024-01-15T10:30:00Z",
        "health_indicators": {
            "heart_rate": "normal",
            "activity_level": "moderate",
            "sleep_quality": "good"
        },
        "recent_alerts": []
    }

# === DATABASE ENDPOINTS ===

@router.get("/elders")
async def get_all_elders():
    """Get all active elders from database"""
    try:
        elders = eldercare_service.get_all_elders()
        return {"success": True, "elders": elders, "count": len(elders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get elders: {str(e)}")

@router.get("/elders/{elder_id}")
async def get_elder(elder_id: int):
    """Get specific elder by ID"""
    try:
        elder = eldercare_service.get_elder_by_id(elder_id)
        if not elder:
            raise HTTPException(status_code=404, detail="Elder not found")
        
        caregivers = eldercare_service.get_caregivers_for_elder(elder_id)
        dashboard_stats = eldercare_service.get_elder_dashboard_stats(elder_id)
        
        return {
            "success": True,
            "elder": elder,
            "caregivers": caregivers,
            "dashboard_stats": dashboard_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get elder: {str(e)}")

@router.get("/dashboard")
async def get_facility_dashboard():
    """Get overall facility dashboard statistics"""
    try:
        stats = eldercare_service.get_facility_dashboard_stats()
        elders = eldercare_service.get_all_elders()
        
        return {
            "success": True,
            "facility_stats": stats,
            "elders": elders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get facility dashboard: {str(e)}")

@router.get("/health")
async def eldercare_health():
    """Health check for elder care services"""
    return {
        "eldercare_service": "active",
        "components": {
            "speech_recognition": "active",
            "ai_assistance": "active", 
            "emergency_system": "active",
            "database": "active",
            "mqtt_communication": "active" if mqtt_service.client and mqtt_service.client.is_connected() else "inactive"
        }
    }