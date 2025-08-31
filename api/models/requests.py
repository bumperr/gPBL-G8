from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    model: str = "gemma3:4b"
    image_data: Optional[str] = None  # base64 encoded image
    elder_info: Optional[Dict[str, Any]] = None
    chat_type: str = "general"  # general, assistance, smart_home

class SpeechToTextRequest(BaseModel):
    audio_data: str  # base64 encoded audio
    language: str = "en"
    model: str = "whisper"

class MQTTMessage(BaseModel):
    topic: str
    message: str

class EmergencyAlert(BaseModel):
    elder_name: str
    message: str
    severity: str = "high"  # low, medium, high, critical
    location: Optional[str] = None
    timestamp: Optional[str] = None

# New structured MQTT request models
class SmartHomeCommand(BaseModel):
    elder_name: str
    device_type: str  # lights, thermostat, locks, security, entertainment
    action: str  # turn_on, turn_off, set_temperature, lock, unlock, etc.
    parameters: Optional[Dict[str, Any]] = None  # brightness, temperature, etc.
    room: Optional[str] = None
    timestamp: Optional[str] = None

class HealthMetric(BaseModel):
    elder_name: str
    metric_type: str  # heart_rate, blood_pressure, steps, sleep, medication
    value: Any  # metric value
    unit: Optional[str] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None

class ElderStatus(BaseModel):
    elder_name: str
    status_type: str  # activity, location, mood, emergency
    status_value: str
    confidence: Optional[float] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

# Enhanced ElderInfo model to match frontend expectations
class ElderInfo(BaseModel):
    id: Optional[str] = None
    name: str
    age: Optional[int] = None
    location: Optional[str] = "Home"
    phone: Optional[str] = None
    emergency_contacts: Optional[Dict[str, Any]] = None
    medical_conditions: Optional[list] = None
    medications: Optional[list] = None
    care_preferences: Optional[Dict[str, Any]] = None

# Enhanced request models for database integration
class VoiceAssistanceRequest(BaseModel):
    audio_data: str
    elder_info: ElderInfo
    language: str = "en"
    save_interaction: bool = True

class TextAssistanceRequest(BaseModel):
    message: str
    elder_info: ElderInfo
    save_interaction: bool = True

# Message persistence models
class ChatMessage(BaseModel):
    elder_id: str
    message_type: str  # 'user', 'ai', 'system'
    content: str
    intent_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    suggested_action: Optional[Dict[str, Any]] = None
    mental_health_assessment: Optional[Dict[str, Any]] = None
    is_emergency: bool = False
    metadata: Optional[Dict[str, Any]] = None