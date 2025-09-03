from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import speech_routes, chat_routes, mqtt_routes, eldercare_routes, camera_routes, websocket_routes, devices_routes, analytics_routes, smart_home_routes
from api.services.mqtt_service import MQTTService
from api.services.speech_service import SpeechToTextService
import asyncio


# Global services - Use network MQTT broker IP
mqtt_service = MQTTService(broker="localhost", port=1883)
speech_service = SpeechToTextService()

# Initialize VLM service for video analysis
from api.services.vlm_service import vlm_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("Starting Elder Care Speech Assistant API...")
    
    # Initialize MQTT service
    try:
        await mqtt_service.initialize()
        print("MQTT service initialized")
    except Exception as e:
        print(f"MQTT service initialization failed: {e}")
    
    # Initialize speech recognition service
    try:
        await speech_service.initialize_whisper()
        print("Speech recognition service initialized")
    except Exception as e:
        print(f"Speech recognition initialization failed: {e}")
        
    # Set global services for routes
    speech_routes.mqtt_service = mqtt_service
    eldercare_routes.mqtt_service = mqtt_service
    mqtt_routes.mqtt_service = mqtt_service
    smart_home_routes.mqtt_service = mqtt_service
    
    # Initialize WebSocket with MQTT service
    from api.routes.websocket_routes import initialize_websocket_with_mqtt
    initialize_websocket_with_mqtt(mqtt_service)
    
    # Initialize chat route services
    try:
        from api.routes.chat_routes import initialize_chat_services
        await initialize_chat_services()
        print("Chat route services initialized")
    except Exception as e:
        print(f"Chat route services initialization failed: {e}")
    
    # Initialize VLM service
    try:
        await vlm_service.initialize()
        print("VLM service initialized")
        
        # Start VLM analysis processing in background
        asyncio.create_task(vlm_service.process_analysis_queue())
        print("VLM analysis queue processor started")
    except Exception as e:
        print(f"VLM service initialization failed: {e}")
    
    print("Elder Care Speech Assistant API is ready!")
    
    yield
    
    # Shutdown
    print("Shutting down Elder Care Speech Assistant API...")
    
    if mqtt_service:
        mqtt_service.disconnect()
        print("MQTT service disconnected")
    
    print("Elder Care Speech Assistant API shutdown complete")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Elder Care Speech Assistant API",
    description="AI-powered speech-to-text eldercare assistant with MQTT integration",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(eldercare_routes.router)
app.include_router(speech_routes.router)
app.include_router(chat_routes.router)
app.include_router(mqtt_routes.router)
app.include_router(camera_routes.router)
app.include_router(websocket_routes.router)
app.include_router(devices_routes.router)
app.include_router(analytics_routes.router)
app.include_router(smart_home_routes.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Elder Care Speech Assistant API",
        "version": "2.0.0",
        "features": [
            "Speech-to-text transcription",
            "AI-powered elder assistance", 
            "Emergency detection and alerts",
            "MQTT communication",
            "Caregiver notifications"
        ],
        "endpoints": {
            "eldercare": "/eldercare (Main elder care endpoints)",
            "speech": "/speech (Speech recognition)",
            "chat": "/chat (AI chat)",
            "mqtt": "/mqtt (MQTT communication)",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    status = {
        "api": "running",
        "version": "2.0.0",
        "services": {}
    }
    
    # Check MQTT service
    try:
        if mqtt_service.client and mqtt_service.client.is_connected():
            status["services"]["mqtt"] = "connected"
        else:
            status["services"]["mqtt"] = "disconnected"
    except Exception:
        status["services"]["mqtt"] = "error"
    
    # Check speech service
    try:
        if speech_service.whisper_model:
            status["services"]["speech_recognition"] = "whisper_ready"
        else:
            status["services"]["speech_recognition"] = "google_fallback"
    except Exception:
        status["services"]["speech_recognition"] = "error"
    
    # Check AI service
    try:
        import ollama
        models = ollama.list()
        status["services"]["ai"] = f"available ({len(models['models'])} models)"
    except Exception:
        status["services"]["ai"] = "unavailable"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)