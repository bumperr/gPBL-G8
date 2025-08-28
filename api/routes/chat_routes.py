from fastapi import APIRouter, HTTPException
from api.models.requests import ChatRequest
from api.services.ai_service import AIService

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# Initialize services
ai_service = AIService()

@router.post("/")
async def chat_with_ai(request: ChatRequest):
    """Send a message to AI and get response"""
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