from fastapi import APIRouter, HTTPException
from api.models.requests import SpeechToTextRequest
from api.services.speech_service import SpeechToTextService
from api.services.ai_service import AIService
from api.services.mqtt_service import MQTTService
import json

router = APIRouter(prefix="/speech", tags=["Speech Recognition"])

# Initialize services
speech_service = SpeechToTextService()
ai_service = AIService()

@router.post("/transcribe")
async def transcribe_speech(request: SpeechToTextRequest):
    """Convert speech to text"""
    try:
        result = await speech_service.transcribe_audio(
            request.audio_data, 
            request.language, 
            request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/process-elder-speech")
async def process_elder_speech(request: dict):
    """Process speech from elder - transcribe and get AI response"""
    try:
        # Extract data from request
        audio_data = request.get('audio_data')
        language = request.get('language', 'en')
        elder_info = request.get('elder_info', {})
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Transcribe speech
        transcription_result = await speech_service.transcribe_audio(audio_data, language)
        
        if not transcription_result.get('text'):
            return {
                "transcription": transcription_result,
                "ai_response": {
                    "response": "I couldn't understand what you said. Could you please try again?",
                    "success": False
                }
            }
        
        # Process with AI
        ai_response = await ai_service.process_elder_speech(
            transcription_result['text'], 
            elder_info
        )
        
        # If emergency detected, publish alert
        if ai_response.get('is_emergency'):
            try:
                from api.services.mqtt_service import MQTTService
                mqtt_service = MQTTService()
                await mqtt_service.publish_message("emergency/alert", json.dumps({
                    "elder_info": elder_info,
                    "transcription": transcription_result['text'],
                    "timestamp": "now",
                    "severity": "high"
                }))
            except Exception as mqtt_error:
                print(f"Failed to publish emergency alert: {mqtt_error}")
        
        return {
            "transcription": transcription_result,
            "ai_response": ai_response,
            "timestamp": "now"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/health")
async def speech_health():
    """Health check for speech services"""
    return {
        "speech_service": "active",
        "supported_languages": ["en", "es", "fr", "de"],
        "available_models": ["whisper", "google"]
    }