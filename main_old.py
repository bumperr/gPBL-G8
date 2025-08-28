from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import paho.mqtt.client as mqtt
import ollama
import pyttsx3
from gtts import gTTS
import io
import os
import asyncio
import json
from typing import Optional
import tempfile
import threading

app = FastAPI(title="AI Server", description="FastAPI server with OLLAMA LLM, TTS, and MQTT")

# Global variables
mqtt_client = None
tts_engine = None

# Models
class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2"

class TTSRequest(BaseModel):
    text: str
    voice: str = "gtts"  # "gtts" or "pyttsx3"
    language: str = "en"

class MQTTMessage(BaseModel):
    topic: str
    message: str

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "ai/responses"

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with result code {rc}")
        client.subscribe("ai/requests")
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_mqtt_message(client, userdata, msg):
    try:
        message = msg.payload.decode('utf-8')
        topic = msg.topic
        print(f"Received MQTT message from {topic}: {message}")
        
        # Process the message with OLLAMA
        try:
            data = json.loads(message)
            if 'message' in data:
                response = ollama.chat(
                    model=data.get('model', 'llama3.2'),
                    messages=[{'role': 'user', 'content': data['message']}]
                )
                ai_response = response['message']['content']
                
                # Publish response back to MQTT
                client.publish("ai/responses", json.dumps({
                    "original_message": data['message'],
                    "response": ai_response,
                    "model": data.get('model', 'llama3.2')
                }))
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    except Exception as e:
        print(f"Error decoding MQTT message: {e}")

@app.on_event("startup")
async def startup_event():
    global mqtt_client, tts_engine
    
    # Initialize TTS engine
    try:
        tts_engine = pyttsx3.init()
        print("TTS engine initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize TTS engine: {e}")
    
    # Initialize MQTT client
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        
        # Try to connect to MQTT broker
        mqtt_client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        print("MQTT client initialized")
    except Exception as e:
        print(f"Warning: Could not connect to MQTT broker: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

@app.get("/")
async def root():
    return {
        "message": "AI Server with OLLAMA, TTS, and MQTT",
        "endpoints": {
            "chat": "/chat",
            "tts": "/tts",
            "mqtt": "/mqtt/send",
            "health": "/health"
        }
    }

@app.post("/chat")
async def chat_with_ollama(request: ChatRequest):
    try:
        response = ollama.chat(
            model=request.model,
            messages=[{
                'role': 'user',
                'content': request.message
            }]
        )
        
        ai_response = response['message']['content']
        
        # Optionally publish to MQTT
        if mqtt_client:
            mqtt_client.publish(MQTT_TOPIC, json.dumps({
                "type": "chat_response",
                "message": request.message,
                "response": ai_response,
                "model": request.model
            }))
        
        return {
            "message": request.message,
            "response": ai_response,
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with OLLAMA: {str(e)}")

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        if request.voice == "gtts":
            # Use Google Text-to-Speech
            tts = gTTS(text=request.text, lang=request.language, slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                tmp_filename = tmp_file.name
            
            return FileResponse(
                path=tmp_filename,
                media_type="audio/mpeg",
                filename="speech.mp3"
            )
            
        elif request.voice == "pyttsx3":
            if not tts_engine:
                raise HTTPException(status_code=500, detail="TTS engine not initialized")
            
            # Use pyttsx3 for offline TTS
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tts_engine.save_to_file(request.text, tmp_file.name)
                tts_engine.runAndWait()
                tmp_filename = tmp_file.name
            
            return FileResponse(
                path=tmp_filename,
                media_type="audio/wav",
                filename="speech.wav"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid voice option. Use 'gtts' or 'pyttsx3'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@app.post("/mqtt/send")
async def send_mqtt_message(request: MQTTMessage):
    if not mqtt_client:
        raise HTTPException(status_code=500, detail="MQTT client not initialized")
    
    try:
        result = mqtt_client.publish(request.topic, request.message)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return {"status": "Message sent successfully", "topic": request.topic, "message": request.message}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send MQTT message: {result.rc}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending MQTT message: {str(e)}")

@app.get("/health")
async def health_check():
    status = {
        "server": "running",
        "mqtt": "disconnected",
        "tts": "unavailable",
        "ollama": "unknown"
    }
    
    # Check MQTT connection
    if mqtt_client and mqtt_client.is_connected():
        status["mqtt"] = "connected"
    
    # Check TTS engine
    if tts_engine:
        status["tts"] = "available"
    
    # Check OLLAMA
    try:
        models = ollama.list()
        status["ollama"] = f"available ({len(models['models'])} models)"
    except Exception:
        status["ollama"] = "unavailable"
    
    return status

@app.get("/models")
async def list_models():
    try:
        models = ollama.list()
        return {"models": [model['name'] for model in models['models']]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)