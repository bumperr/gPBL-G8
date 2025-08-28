from fastapi import APIRouter, HTTPException
from api.models.requests import EmergencyAlert
from api.services.mqtt_service import MQTTService
from api.services.ai_service import AIService
import json
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/eldercare", tags=["Elder Care"])

# Initialize services
mqtt_service = MQTTService()
ai_service = AIService()

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

@router.get("/health")
async def eldercare_health():
    """Health check for elder care services"""
    return {
        "eldercare_service": "active",
        "components": {
            "speech_recognition": "active",
            "ai_assistance": "active", 
            "emergency_system": "active",
            "mqtt_communication": "active" if mqtt_service.client and mqtt_service.client.is_connected() else "inactive"
        }
    }