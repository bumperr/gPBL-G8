from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from api.models.requests import ChatRequest
from api.services.ai_service import AIService
from api.services.mqtt_service import MQTTService
import base64
import json
from typing import Optional

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# Initialize services
ai_service = AIService()
mqtt_service = MQTTService()

# Initialize MQTT service (async initialization will be done in startup)
async def initialize_chat_services():
    """Initialize chat route services"""
    try:
        await mqtt_service.initialize()
        print("Chat routes: MQTT service initialized")
    except Exception as e:
        print(f"Chat routes: MQTT initialization failed: {e}")

# Call this from the main startup event

@router.post("/")
async def chat_with_ai(request: ChatRequest):
    """Enhanced chat endpoint with image support and smart home integration"""
    try:
        response = await ai_service.enhanced_chat(
            message=request.message,
            chat_type=request.chat_type,
            model=request.model,
            elder_info=request.elder_info,
            image_data=request.image_data
        )
        
        # Execute MQTT commands if any
        if response.get('mqtt_commands'):
            for command in response['mqtt_commands']:
                await mqtt_service.publish_message(command['topic'], command['payload'])
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/upload-image")
async def chat_with_image(
    message: str = Form(...),
    chat_type: str = Form("general"),
    model: Optional[str] = Form(None),
    elder_info: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    """Chat endpoint with image file upload"""
    try:
        # Read and encode image
        image_bytes = await image.read()
        image_data = base64.b64encode(image_bytes).decode('utf-8')
        
        # Parse elder_info if provided
        elder_info_dict = json.loads(elder_info) if elder_info else None
        
        response = await ai_service.enhanced_chat(
            message=message,
            chat_type=chat_type,
            model=model,
            elder_info=elder_info_dict,
            image_data=image_data
        )
        
        # Execute MQTT commands if any
        if response.get('mqtt_commands'):
            for command in response['mqtt_commands']:
                await mqtt_service.publish_message(command['topic'], command['payload'])
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image chat failed: {str(e)}")

@router.post("/legacy")
async def legacy_chat(request: ChatRequest):
    """Legacy chat endpoint for backward compatibility"""
    try:
        response = await ai_service.chat_completion(request.message, request.model) # type: ignore
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/models")
async def list_available_models():
    """Get list of available AI models"""
    try:
        models = await ai_service.list_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/health")
async def chat_health():
    """Health check for chat services"""
    try:
        models = await ai_service.list_available_models()
        return {
            "ai_service": "active",
            "available_models": len(models),
            "default_model": ai_service.default_model
        }
    except Exception as e:
        return {
            "ai_service": "error",
            "error": str(e)
        }