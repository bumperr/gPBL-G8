import base64
import tempfile
import os
from typing import Dict, Any
import speech_recognition as sr
from io import BytesIO

# Optional whisper import with error handling
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"Whisper not available: {e}")
    WHISPER_AVAILABLE = False
    whisper = None

class SpeechToTextService:
    def __init__(self):
        self.whisper_model = None
        self.recognizer = sr.Recognizer()
        self.whisper_available = WHISPER_AVAILABLE
        
    async def initialize_whisper(self):
        """Initialize Whisper model for speech recognition"""
        if not self.whisper_available:
            print("Whisper not available, skipping initialization")
            return
            
        try:
            self.whisper_model = whisper.load_model("base")
            print("Whisper model initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Whisper: {e}")
            self.whisper_available = False
            
    async def transcribe_audio_whisper(self, audio_data: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        if not self.whisper_model:
            await self.initialize_whisper()
            
        try:
            # Fix base64 padding if needed
            missing_padding = len(audio_data) % 4
            if missing_padding:
                audio_data += '=' * (4 - missing_padding)
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary file with appropriate extension for WebM
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_filename = tmp_file.name
                
            # Transcribe using Whisper (Whisper can handle various formats)
            result = self.whisper_model.transcribe(tmp_filename, language=language)
            
            # Clean up temporary file
            os.unlink(tmp_filename)
            
            return {
                "text": result["text"],
                "confidence": 1.0,  # Whisper doesn't provide confidence scores
                "language": result.get("language", language),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            raise Exception(f"Speech recognition failed: {str(e)}")
            
    async def transcribe_audio_google(self, audio_data: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio using Google Speech Recognition (fallback)"""
        try:
            # Fix base64 padding if needed
            missing_padding = len(audio_data) % 4
            if missing_padding:
                audio_data += '=' * (4 - missing_padding)
                
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create audio data object
            audio = sr.AudioData(audio_bytes, sample_rate=16000, sample_width=2)
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio, language=language)
            
            return {
                "text": text,
                "confidence": 0.8,  # Approximate confidence
                "language": language,
                "segments": []
            }
            
        except sr.UnknownValueError:
            return {
                "text": "",
                "confidence": 0.0,
                "error": "Could not understand audio"
            }
        except sr.RequestError as e:
            raise Exception(f"Google Speech Recognition error: {str(e)}")
            
    async def transcribe_audio(self, audio_data: str, language: str = "en", model: str = "whisper") -> Dict[str, Any]:
        """Main transcription method with fallback options"""
        try:
            if model == "whisper" and self.whisper_available and self.whisper_model:
                return await self.transcribe_audio_whisper(audio_data, language)
            else:
                # Fallback to Google Speech Recognition
                return await self.transcribe_audio_google(audio_data, language)
        except Exception as e:
            # Try fallback if primary method fails
            if model == "whisper":
                try:
                    return await self.transcribe_audio_google(audio_data, language)
                except Exception as fallback_error:
                    raise Exception(f"All transcription methods failed. Primary: {str(e)}, Fallback: {str(fallback_error)}")
            else:
                raise e