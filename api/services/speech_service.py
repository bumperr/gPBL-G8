import base64
import tempfile
import os
from typing import Dict, Any
import speech_recognition as sr
from io import BytesIO

# Audio format conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

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
        self.pydub_available = PYDUB_AVAILABLE
        
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
            
    def _convert_to_wav(self, audio_bytes: bytes, input_format: str = "webm") -> bytes:
        """Convert audio to WAV format using pydub with FFmpeg"""
        if not self.pydub_available:
            raise Exception("pydub not available for audio conversion")
            
        try:
            # Load audio from bytes - pydub will use FFmpeg automatically for WebM
            audio = AudioSegment.from_file(BytesIO(audio_bytes), format=input_format)
            
            # Convert to WAV format suitable for speech_recognition
            # Set parameters that work well with speech recognition
            audio = audio.set_frame_rate(16000).set_channels(1)  # 16kHz mono
            
            # Export to WAV
            wav_io = BytesIO()
            audio.export(wav_io, format="wav")
            return wav_io.getvalue()
            
        except Exception as e:
            raise Exception(f"Audio conversion from {input_format} failed: {str(e)}")
            
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
        """Transcribe audio using Google Speech Recognition with format conversion"""
        try:
            # Fix base64 padding if needed
            missing_padding = len(audio_data) % 4
            if missing_padding:
                audio_data += '=' * (4 - missing_padding)
                
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # First, try direct WAV processing (for when audio is already WAV)
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_filename = tmp_file.name
                    
                try:
                    with sr.AudioFile(tmp_filename) as source:
                        audio = self.recognizer.record(source)
                    
                    text = self.recognizer.recognize_google(audio, language=language)
                    
                    return {
                        "text": text,
                        "confidence": 0.8,
                        "language": language,
                        "segments": []
                    }
                finally:
                    os.unlink(tmp_filename)
                    
            except Exception as direct_error:
                print(f"Direct WAV processing failed: {direct_error}")
                
                # If direct processing fails, try format conversion with pydub
                if self.pydub_available:
                    print("Attempting audio format conversion...")
                    
                    # Try different input formats
                    for input_format in ["webm", "ogg", "mp3", "m4a"]:
                        try:
                            # Convert to WAV using pydub + FFmpeg
                            wav_bytes = self._convert_to_wav(audio_bytes, input_format)
                            print(f"Successfully converted from {input_format} to WAV")
                            
                            # Now process the converted WAV
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                                tmp_file.write(wav_bytes)
                                tmp_filename = tmp_file.name
                                
                            try:
                                with sr.AudioFile(tmp_filename) as source:
                                    audio = self.recognizer.record(source)
                                
                                text = self.recognizer.recognize_google(audio, language=language)
                                
                                return {
                                    "text": text,
                                    "confidence": 0.8,
                                    "language": language,
                                    "segments": [],
                                    "converted_from": input_format
                                }
                            finally:
                                os.unlink(tmp_filename)
                                
                        except Exception as conv_error:
                            print(f"Conversion from {input_format} failed: {conv_error}")
                            continue
                
                # If all conversion attempts fail
                return {
                    "text": "",
                    "confidence": 0.0,
                    "error": "Could not convert audio format - FFmpeg may not be available or audio format not supported"
                }
            
        except sr.UnknownValueError:
            return {
                "text": "",
                "confidence": 0.0,
                "error": "Could not understand audio"
            }
        except sr.RequestError as e:
            raise Exception(f"Google Speech Recognition error: {str(e)}")
        except Exception as e:
            raise Exception(f"Audio processing error: {str(e)}")
            
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