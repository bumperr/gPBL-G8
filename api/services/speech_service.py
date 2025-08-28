import whisper
import base64
import tempfile
import os
from typing import Dict, Any
import speech_recognition as sr
from io import BytesIO

class SpeechToTextService:
    def __init__(self):
        self.whisper_model = None
        self.recognizer = sr.Recognizer()
        
    async def initialize_whisper(self):
        """Initialize Whisper model for speech recognition"""
        try:
            self.whisper_model = whisper.load_model("base")
            print("Whisper model initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Whisper: {e}")
            
    async def transcribe_audio_whisper(self, audio_data: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        if not self.whisper_model:
            await self.initialize_whisper()
            
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_filename = tmp_file.name
                
            # Transcribe using Whisper
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
            if model == "whisper" and self.whisper_model:
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