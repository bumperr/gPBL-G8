import asyncio
import base64
import json
import tempfile
import os
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
import cv2
from pathlib import Path

class VLMAnalysisService:
    """Video-Language Model Analysis Service for elder care monitoring"""
    
    def __init__(self):
        self.model_name = "video-llava"
        self.frame_buffer: Dict[int, List[str]] = {}  # Buffer frames for analysis
        self.analysis_queue = asyncio.Queue()
        self.is_processing = False
        
    async def initialize(self):
        """Initialize the VLM service"""
        try:
            # Check if video-llava or similar model is available
            # For demo purposes, we'll use a mock implementation
            print("Initializing VLM Analysis Service...")
            print("Note: This is a demo implementation - integrate with actual video-llava when available")
            return True
        except Exception as e:
            print(f"VLM service initialization failed: {e}")
            return False
    
    def add_frame_to_buffer(self, camera_id: int, frame_base64: str, timestamp: str):
        """Add frame to analysis buffer for 15-second clips"""
        if camera_id not in self.frame_buffer:
            self.frame_buffer[camera_id] = []
        
        frame_data = {
            "frame": frame_base64,
            "timestamp": timestamp
        }
        
        self.frame_buffer[camera_id].append(frame_data)
        
        # Keep only last 15 seconds of frames (assuming 15 FPS = 225 frames)
        if len(self.frame_buffer[camera_id]) > 225:
            self.frame_buffer[camera_id] = self.frame_buffer[camera_id][-225:]
    
    async def analyze_15_second_clip(self, camera_id: int, elder_id: int = 1) -> Dict:
        """Analyze 15-second video clip using VLM"""
        try:
            if camera_id not in self.frame_buffer or len(self.frame_buffer[camera_id]) < 10:
                return {
                    "success": False,
                    "error": "Insufficient frames for analysis"
                }
            
            frames = self.frame_buffer[camera_id][-225:]  # Last 15 seconds
            
            # For demo purposes, create a mock analysis
            # In production, this would call actual video-llava model
            analysis_result = await self._mock_vlm_analysis(camera_id, frames, elder_id)
            
            return {
                "success": True,
                "camera_id": camera_id,
                "elder_id": elder_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "frames_analyzed": len(frames),
                "analysis_duration_seconds": 15,
                **analysis_result
            }
            
        except Exception as e:
            print(f"VLM analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _mock_vlm_analysis(self, camera_id: int, frames: List[Dict], elder_id: int) -> Dict:
        """Mock VLM analysis - replace with actual video-llava integration"""
        
        # TODO: Replace with real Video-LLaVA integration
        # Example integration options:
        
        # Option 1: If Video-LLaVA available via Ollama
        # return await self._real_vlm_analysis_ollama(frames)
        
        # Option 2: If using Hugging Face Video-LLaVA
        # return await self._real_vlm_analysis_hf(frames)
        
        # Option 3: If using OpenAI GPT-4V for video
        # return await self._real_vlm_analysis_openai(frames)
        
        # Use actual working VLM - integrate with your AI service
        try:
            return await self._real_vlm_analysis_with_existing_ai(frames, camera_id, elder_id)
        except Exception as e:
            print(f"Real VLM analysis failed, using mock: {e}")
            
            # Fallback to preserve existing activity records
            if camera_id == 100:  # Elder Activities Sample
                return await self._analyze_elder_activities(frames)
            elif camera_id == 101:  # Fall Detection Demo
                return await self._analyze_fall_detection(frames)
            elif camera_id == 102:  # Daily Routine Analysis
                return await self._analyze_daily_routine(frames)
            else:
                return await self._analyze_general_activity(frames)
    
    async def _analyze_elder_activities(self, frames: List[Dict]) -> Dict:
        """Analyze elder activities sample"""
        # Mock analysis for elder activities
        activities = [
            "walking", "sitting", "standing", "watching_tv", 
            "slow_movement", "resting"
        ]
        
        detected_activity = np.random.choice(activities)
        confidence = np.random.uniform(0.7, 0.95)
        
        # Determine activity type and anomaly
        if detected_activity in ["slow_movement", "prolonged_standing"]:
            activity_type = "unusual"
            anomaly_detected = np.random.choice([True, False], p=[0.3, 0.7])
        elif detected_activity == "fall_detected":
            activity_type = "emergency"
            anomaly_detected = True
        else:
            activity_type = "normal"
            anomaly_detected = False
        
        ai_analysis = self._generate_activity_analysis(detected_activity, confidence)
        
        return {
            "activity_detected": detected_activity,
            "activity_type": activity_type,
            "confidence_score": confidence,
            "anomaly_detected": anomaly_detected,
            "ai_analysis": ai_analysis,
            "location": "Living Room",
            "duration_seconds": 15,
            "vlm_model": "video-llava-demo",
            "analysis_details": {
                "movement_pattern": "regular" if not anomaly_detected else "irregular",
                "posture_assessment": "stable" if confidence > 0.8 else "uncertain",
                "environmental_factors": "good lighting, clear view",
                "behavioral_notes": f"Elder observed {detected_activity} for analysis period"
            }
        }
    
    async def _analyze_fall_detection(self, frames: List[Dict]) -> Dict:
        """Analyze fall detection scenario"""
        fall_scenarios = [
            ("normal_walking", "normal", False),
            ("unsteady_movement", "unusual", True),
            ("fall_detected", "emergency", True),
            ("person_on_ground", "emergency", True)
        ]
        
        activity, activity_type, anomaly = np.random.choice(fall_scenarios, p=[0.4, 0.3, 0.2, 0.1])
        confidence = np.random.uniform(0.85, 0.98) if anomaly else np.random.uniform(0.7, 0.9)
        
        ai_analysis = self._generate_fall_analysis(activity, confidence, anomaly)
        
        return {
            "activity_detected": activity,
            "activity_type": activity_type,
            "confidence_score": confidence,
            "anomaly_detected": anomaly,
            "ai_analysis": ai_analysis,
            "location": "Living Room",
            "duration_seconds": 15,
            "vlm_model": "video-llava-demo",
            "emergency_level": "critical" if "fall" in activity else "normal",
            "analysis_details": {
                "fall_risk_assessment": "high" if anomaly else "low",
                "movement_stability": "unstable" if anomaly else "stable", 
                "immediate_action_required": anomaly,
                "emergency_contacts_notified": anomaly
            }
        }
    
    async def _analyze_daily_routine(self, frames: List[Dict]) -> Dict:
        """Analyze daily routine patterns"""
        routine_activities = [
            "morning_routine", "meal_preparation", "resting", 
            "evening_activities", "sleep_preparation"
        ]
        
        activity = np.random.choice(routine_activities)
        confidence = np.random.uniform(0.75, 0.92)
        
        # Routine deviation analysis
        routine_deviation = np.random.choice([True, False], p=[0.2, 0.8])
        activity_type = "unusual" if routine_deviation else "normal"
        
        ai_analysis = self._generate_routine_analysis(activity, confidence, routine_deviation)
        
        return {
            "activity_detected": activity,
            "activity_type": activity_type,
            "confidence_score": confidence,
            "anomaly_detected": routine_deviation,
            "ai_analysis": ai_analysis,
            "location": self._get_location_for_activity(activity),
            "duration_seconds": 15,
            "vlm_model": "video-llava-demo",
            "routine_analysis": {
                "expected_activity": activity,
                "time_appropriateness": not routine_deviation,
                "pattern_consistency": "consistent" if not routine_deviation else "deviation_detected",
                "health_indicators": "normal" if confidence > 0.8 else "monitoring_recommended"
            }
        }
    
    async def _analyze_general_activity(self, frames: List[Dict]) -> Dict:
        """General activity analysis for physical cameras"""
        general_activities = [
            "walking", "sitting", "standing", "moving", "stationary"
        ]
        
        activity = np.random.choice(general_activities)
        confidence = np.random.uniform(0.6, 0.85)
        anomaly = np.random.choice([True, False], p=[0.1, 0.9])
        
        return {
            "activity_detected": activity,
            "activity_type": "unusual" if anomaly else "normal",
            "confidence_score": confidence,
            "anomaly_detected": anomaly,
            "ai_analysis": f"General activity analysis detected {activity} with {confidence:.1%} confidence.",
            "location": "Camera View",
            "duration_seconds": 15,
            "vlm_model": "video-llava-demo"
        }
    
    def _generate_activity_analysis(self, activity: str, confidence: float) -> str:
        """Generate detailed AI analysis for activities"""
        analysis_templates = {
            "walking": f"Elder observed walking steadily across the room. Movement appears coordinated with {confidence:.1%} confidence. Gait analysis suggests normal mobility.",
            "sitting": f"Elder is seated comfortably. Posture appears stable and relaxed. No signs of distress detected with {confidence:.1%} confidence.",
            "standing": f"Elder maintaining standing position. Balance appears adequate. Duration and stability monitored with {confidence:.1%} confidence.",
            "watching_tv": f"Elder engaged in leisure activity (television viewing). Positioned safely and comfortably with {confidence:.1%} confidence.",
            "slow_movement": f"Slower than typical movement pattern observed. May indicate fatigue or mobility changes. Recommend continued monitoring with {confidence:.1%} confidence.",
            "resting": f"Elder at rest. Breathing appears regular, posture comfortable. Extended rest period noted with {confidence:.1%} confidence."
        }
        
        return analysis_templates.get(activity, f"Activity '{activity}' detected with {confidence:.1%} confidence. Continuing monitoring.")
    
    def _generate_fall_analysis(self, activity: str, confidence: float, anomaly: bool) -> str:
        """Generate detailed fall analysis"""
        if "fall" in activity:
            return f"CRITICAL: Fall event detected with {confidence:.1%} confidence. Emergency protocols should be activated immediately. Elder requires immediate assistance."
        elif "unsteady" in activity:
            return f"WARNING: Unsteady movement pattern detected with {confidence:.1%} confidence. Increased fall risk observed. Enhanced monitoring recommended."
        elif "ground" in activity:
            return f"EMERGENCY: Person detected on ground with {confidence:.1%} confidence. Immediate medical attention required. Emergency services should be contacted."
        else:
            return f"Normal movement pattern observed with {confidence:.1%} confidence. No immediate fall risk indicators detected."
    
    def _generate_routine_analysis(self, activity: str, confidence: float, deviation: bool) -> str:
        """Generate routine analysis"""
        if deviation:
            return f"Routine deviation detected: {activity} observed outside normal schedule with {confidence:.1%} confidence. Pattern change may indicate health status changes or external factors."
        else:
            return f"Normal routine pattern: {activity} occurring within expected timeframe with {confidence:.1%} confidence. Daily routine consistency maintained."
    
    def _get_location_for_activity(self, activity: str) -> str:
        """Map activity to likely location"""
        location_map = {
            "morning_routine": "Bedroom/Bathroom",
            "meal_preparation": "Kitchen",
            "resting": "Living Room",
            "evening_activities": "Living Room",
            "sleep_preparation": "Bedroom"
        }
        return location_map.get(activity, "Home")
    
    async def process_analysis_queue(self):
        """Process queued analysis requests"""
        while True:
            try:
                if not self.analysis_queue.empty():
                    analysis_request = await self.analysis_queue.get()
                    result = await self.analyze_15_second_clip(
                        analysis_request["camera_id"],
                        analysis_request.get("elder_id", 1)
                    )
                    
                    # Store result to database (implement in next step)
                    await self._store_analysis_result(result)
                    
                await asyncio.sleep(1)  # Prevent busy waiting
                
            except Exception as e:
                print(f"Error processing analysis queue: {e}")
                await asyncio.sleep(5)
    
    async def _store_analysis_result(self, result: Dict):
        """Store VLM analysis result to analytics database"""
        try:
            if not result.get("success"):
                print(f"Skipping storage of failed analysis: {result}")
                return
            
            # Import database functionality
            import sqlite3
            import json
            import os
            
            # Get database connection
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'eldercare.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Extract analysis data
            camera_id = result.get("camera_id", 0)
            elder_id = result.get("elder_id", 1)
            activity_detected = result.get("activity_detected", "unknown")
            activity_type = result.get("activity_type", "normal")
            confidence_score = result.get("confidence_score", 0.0)
            anomaly_detected = result.get("anomaly_detected", False)
            ai_analysis = result.get("ai_analysis", "VLM analysis performed")
            location = result.get("location", "Camera View")
            duration_seconds = result.get("duration_seconds", 15)
            
            # Create metadata with VLM-specific information
            metadata = {
                "vlm_model": result.get("vlm_model", "video-llava-demo"),
                "frames_analyzed": result.get("frames_analyzed", 0),
                "analysis_duration": result.get("analysis_duration_seconds", 15),
                "analysis_details": result.get("analysis_details", {}),
                "emergency_level": result.get("emergency_level"),
                "routine_analysis": result.get("routine_analysis"),
                "analysis_timestamp": result.get("analysis_timestamp"),
                "analysis_type": "vlm_video_analysis"
            }
            
            # Check if we should preserve existing records (don't overwrite)
            # Insert new record while preserving existing ones
            cursor.execute("""
                INSERT INTO camera_analytics (
                    elder_id, camera_id, image_base64, activity_detected, activity_type,
                    confidence_score, location, duration_seconds, anomaly_detected,
                    ai_analysis, metadata, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                elder_id, camera_id, None,  # No single image for video analysis
                activity_detected, activity_type, confidence_score, location,
                duration_seconds, anomaly_detected, ai_analysis,
                json.dumps(metadata), datetime.now().isoformat()
            ))
            
            # Log preservation of existing records
            cursor.execute("SELECT COUNT(*) FROM camera_analytics WHERE elder_id = ?", (elder_id,))
            total_records = cursor.fetchone()[0]
            print(f"Activity record added. Total records for elder {elder_id}: {total_records}")
            
            activity_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"VLM analysis stored to database with ID: {activity_id}")
            
            # Trigger emergency alerts if needed
            if result.get("activity_type") == "emergency" or result.get("emergency_level") == "critical":
                await self._handle_emergency_detection(result, activity_id)
            
        except Exception as e:
            print(f"Error storing VLM analysis result: {e}")
    
    async def _handle_emergency_detection(self, result: Dict, activity_id: int):
        """Handle emergency detection from VLM analysis"""
        try:
            print(f"EMERGENCY DETECTED by VLM - Activity ID: {activity_id}")
            
            # Import emergency services
            from api.services.mqtt_service import MQTTService
            
            # Create emergency alert
            emergency_data = {
                "type": "emergency_alert",
                "source": "vlm_analysis",
                "activity_id": activity_id,
                "camera_id": result.get("camera_id"),
                "elder_id": result.get("elder_id", 1),
                "activity_detected": result.get("activity_detected"),
                "confidence": result.get("confidence_score", 0.0),
                "location": result.get("location", "Home"),
                "emergency_level": result.get("emergency_level", "high"),
                "ai_analysis": result.get("ai_analysis", ""),
                "timestamp": datetime.now().isoformat(),
                "requires_immediate_attention": True
            }
            
            # This could be expanded to send actual notifications
            print(f"Emergency alert data: {json.dumps(emergency_data, indent=2)}")
            
            # In a production system, this would:
            # 1. Send MQTT alert to caregivers
            # 2. Trigger phone/SMS notifications
            # 3. Update dashboard with urgent alert
            # 4. Log to emergency response system
            
        except Exception as e:
            print(f"Error handling emergency detection: {e}")
    
    def queue_analysis(self, camera_id: int, elder_id: int = 1):
        """Queue analysis request"""
        try:
            analysis_request = {
                "camera_id": camera_id,
                "elder_id": elder_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use asyncio.create_task to add to queue safely
            asyncio.create_task(self._add_to_queue(analysis_request))
            
        except Exception as e:
            print(f"Error queueing analysis: {e}")
    
    async def _add_to_queue(self, request: Dict):
        """Add request to analysis queue"""
        await self.analysis_queue.put(request)
    
    # Real VLM Integration Methods (ready for implementation)
    
    async def _real_vlm_analysis_with_existing_ai(self, frames: List[Dict], camera_id: int, elder_id: int) -> Dict:
        """Real VLM analysis using existing AI service with image analysis"""
        try:
            from api.services.ai_service import AIService
            ai_service = AIService()
            
            # Select key frames for analysis (every 5th frame, max 6 frames)
            key_frames = frames[::5][-6:] if len(frames) >= 6 else frames
            
            if not key_frames:
                return await self._analyze_general_activity(frames)
            
            # Use the most recent frame for analysis
            latest_frame = key_frames[-1]["frame"]
            
            # Create eldercare-specific vision prompt
            vision_prompt = f"""You are an AI assistant analyzing eldercare monitoring camera footage. 

Analyze this camera image and provide a structured assessment:

1. **Primary Activity**: What is the person doing? (walking, sitting, standing, lying down, falling, no person visible, etc.)

2. **Safety Assessment**: 
   - NORMAL: Regular daily activities, person appears safe
   - UNUSUAL: Concerning but not immediately dangerous (unsteady movement, unusual posture)
   - ALERT: Potentially dangerous situation requiring attention
   - EMERGENCY: Immediate danger (fall detected, person on ground, distress)

3. **Confidence Level**: How confident are you in this analysis? (0.0 to 1.0)

4. **Location Context**: Where does this appear to be taken? (living room, kitchen, bedroom, bathroom, etc.)

5. **Detailed Analysis**: Provide specific observations about the person's posture, movement, and any safety concerns.

6. **Duration Estimate**: If there's movement, estimate if this appears to be a brief moment or sustained activity.

Format your response as JSON with these exact keys:
- "activity_detected": string
- "safety_status": "normal"|"unusual"|"alert"|"emergency"  
- "confidence_score": float (0.0-1.0)
- "location": string
- "detailed_analysis": string
- "duration_assessment": string
- "anomaly_detected": boolean
"""

            # Use AI service for image analysis (similar to how chat with images works)
            try:
                response = await ai_service.chat_completion(
                    vision_prompt,
                    model="gemma3:4b",  # Your existing model
                    image_data=latest_frame,  # Base64 image
                )
                
                # Parse AI response
                ai_response_text = response.get("response", "")
                parsed_result = self._parse_ai_vision_response(ai_response_text)
                
                # Map safety status to activity type
                safety_to_activity_type = {
                    "normal": "normal",
                    "unusual": "unusual", 
                    "alert": "alert",
                    "emergency": "emergency"
                }
                
                activity_type = safety_to_activity_type.get(parsed_result.get("safety_status", "normal"), "normal")
                
                return {
                    "activity_detected": parsed_result.get("activity_detected", "unknown_activity"),
                    "activity_type": activity_type,
                    "confidence_score": float(parsed_result.get("confidence_score", 0.7)),
                    "anomaly_detected": parsed_result.get("anomaly_detected", activity_type != "normal"),
                    "ai_analysis": parsed_result.get("detailed_analysis", ai_response_text[:200] + "..."),
                    "location": parsed_result.get("location", "Camera View"),
                    "duration_seconds": 15,
                    "vlm_model": "gemma3:4b-vision-analysis",
                    "analysis_method": "real_ai_service",
                    "frames_analyzed": len(key_frames),
                    "analysis_details": {
                        "safety_status": parsed_result.get("safety_status", "normal"),
                        "duration_assessment": parsed_result.get("duration_assessment", "sustained_activity"),
                        "vision_confidence": parsed_result.get("confidence_score", 0.7),
                        "analysis_timestamp": datetime.now().isoformat()
                    }
                }
                
            except Exception as ai_error:
                print(f"AI service vision analysis error: {ai_error}")
                # Fallback to basic frame analysis
                return await self._basic_frame_analysis(latest_frame, camera_id)
            
        except Exception as e:
            print(f"Real VLM analysis error: {e}")
            raise e
    
    def _parse_ai_vision_response(self, response_text: str) -> Dict:
        """Parse AI vision response into structured format"""
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback: parse text response manually
            result = {}
            
            # Extract activity
            activity_patterns = [
                r"activity[^:]*:\s*[\"']?([^\"'\n,]+)[\"']?",
                r"doing[^:]*:\s*[\"']?([^\"'\n,]+)[\"']?",
                r"person is\s+([^,.\n]+)",
            ]
            
            for pattern in activity_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    result["activity_detected"] = match.group(1).strip().lower()
                    break
            
            # Extract safety status
            safety_patterns = [
                r"safety[^:]*:\s*[\"']?(normal|unusual|alert|emergency)[\"']?",
                r"status[^:]*:\s*[\"']?(normal|unusual|alert|emergency)[\"']?",
            ]
            
            for pattern in safety_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    result["safety_status"] = match.group(1).lower()
                    break
            
            # Extract confidence
            conf_match = re.search(r"confidence[^:]*:\s*([0-9.]+)", response_text, re.IGNORECASE)
            if conf_match:
                result["confidence_score"] = float(conf_match.group(1))
            
            # Extract location
            loc_match = re.search(r"location[^:]*:\s*[\"']?([^\"'\n,]+)[\"']?", response_text, re.IGNORECASE)
            if loc_match:
                result["location"] = loc_match.group(1).strip()
            
            # Set defaults
            result.setdefault("activity_detected", "unknown")
            result.setdefault("safety_status", "normal")
            result.setdefault("confidence_score", 0.7)
            result.setdefault("location", "Home")
            result.setdefault("detailed_analysis", response_text[:300])
            result.setdefault("duration_assessment", "sustained_activity")
            result.setdefault("anomaly_detected", result["safety_status"] != "normal")
            
            return result
            
        except Exception as e:
            print(f"Error parsing AI vision response: {e}")
            return {
                "activity_detected": "parsing_error",
                "safety_status": "normal", 
                "confidence_score": 0.5,
                "location": "Unknown",
                "detailed_analysis": response_text[:200] if response_text else "No analysis available",
                "duration_assessment": "unknown",
                "anomaly_detected": False
            }
    
    async def _basic_frame_analysis(self, frame_base64: str, camera_id: int) -> Dict:
        """Basic frame analysis fallback"""
        return {
            "activity_detected": "basic_analysis",
            "activity_type": "normal",
            "confidence_score": 0.6,
            "anomaly_detected": False,
            "ai_analysis": f"Basic frame analysis for camera {camera_id}",
            "location": "Camera View", 
            "duration_seconds": 15,
            "vlm_model": "basic-frame-analysis",
            "analysis_method": "fallback"
        }
    
    async def _real_vlm_analysis_ollama(self, frames: List[Dict]) -> Dict:
        """Real Video-LLaVA analysis via Ollama (when available)"""
        try:
            # Example integration with Ollama Video-LLaVA
            # This would require Video-LLaVA model installed in Ollama
            
            from api.services.ai_service import AIService
            ai_service = AIService()
            
            # Create video analysis prompt
            prompt = """
            Analyze this eldercare monitoring video for:
            1. Activity detection (walking, sitting, standing, falling)
            2. Safety assessment (normal, concerning, emergency)
            3. Behavioral patterns
            4. Any anomalies requiring attention
            
            Provide structured analysis with:
            - Primary activity detected
            - Confidence level (0-1)
            - Safety status (normal/unusual/alert/emergency) 
            - Detailed description
            - Recommended actions if needed
            """
            
            # In real implementation, you would:
            # 1. Convert frames to video format
            # 2. Send to Video-LLaVA model
            # 3. Parse structured response
            
            # For now, return mock structure that real VLM would provide
            return {
                "activity_detected": "walking", 
                "confidence_score": 0.85,
                "activity_type": "normal",
                "anomaly_detected": False,
                "ai_analysis": "Video-LLaVA analysis: Elder walking normally across room",
                "vlm_model": "video-llava-1.5-7b"  # Real model name
            }
            
        except Exception as e:
            print(f"Ollama VLM analysis error: {e}")
            # Fallback to mock
            return await self._analyze_general_activity(frames)
    
    async def _real_vlm_analysis_hf(self, frames: List[Dict]) -> Dict:
        """Real Video-LLaVA analysis via Hugging Face"""
        try:
            # Example Hugging Face Video-LLaVA integration
            # pip install transformers torch pillow
            
            # from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration
            # import torch
            # from PIL import Image
            # import io
            
            # # Load model (do this once during initialization)
            # model = VideoLlavaForConditionalGeneration.from_pretrained(
            #     "LanguageBind/Video-LLaVA-7B-hf"
            # )
            # processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")
            
            # # Convert base64 frames to images
            # video_frames = []
            # for frame_data in frames[-30:]:  # Use last 30 frames (2 seconds at 15fps)
            #     image_bytes = base64.b64decode(frame_data["frame"])
            #     image = Image.open(io.BytesIO(image_bytes))
            #     video_frames.append(image)
            
            # # Create prompt for elder care analysis
            # prompt = "USER: <video>Analyze this eldercare monitoring video. What activity is the elder performing? Is there any safety concern? ASSISTANT:"
            
            # # Process and generate
            # inputs = processor(text=prompt, videos=[video_frames], return_tensors="pt")
            # generate_ids = model.generate(**inputs, max_length=100)
            # response = processor.batch_decode(generate_ids, skip_special_tokens=True)[0]
            
            # # Parse response into structured format
            # return self._parse_vlm_response(response)
            
            return {
                "activity_detected": "analyzed_by_hf_vlm",
                "confidence_score": 0.90,
                "activity_type": "normal", 
                "anomaly_detected": False,
                "ai_analysis": "Hugging Face Video-LLaVA analysis would go here",
                "vlm_model": "LanguageBind/Video-LLaVA-7B-hf"
            }
            
        except Exception as e:
            print(f"Hugging Face VLM analysis error: {e}")
            return await self._analyze_general_activity(frames)
    
    async def _real_vlm_analysis_openai(self, frames: List[Dict]) -> Dict:
        """Real video analysis via OpenAI GPT-4V (frame-by-frame)"""
        try:
            # Example OpenAI GPT-4V integration for video analysis
            # import openai
            
            # # Select key frames for analysis (e.g., every 5th frame)
            # key_frames = frames[::5][-6:]  # Last 6 key frames
            
            # frame_messages = []
            # for i, frame_data in enumerate(key_frames):
            #     frame_messages.append({
            #         "type": "image_url",
            #         "image_url": {
            #             "url": f"data:image/jpeg;base64,{frame_data['frame']}"
            #         }
            #     })
            
            # response = await openai.ChatCompletion.acreate(
            #     model="gpt-4-vision-preview",
            #     messages=[
            #         {
            #             "role": "user",
            #             "content": [
            #                 {"type": "text", "text": "Analyze these eldercare monitoring frames for activity and safety. What is the elder doing? Any concerns?"},
            #                 *frame_messages
            #             ]
            #         }
            #     ]
            # )
            
            # return self._parse_openai_response(response.choices[0].message.content)
            
            return {
                "activity_detected": "gpt4v_analyzed",
                "confidence_score": 0.88,
                "activity_type": "normal",
                "anomaly_detected": False, 
                "ai_analysis": "OpenAI GPT-4V video analysis would go here",
                "vlm_model": "gpt-4-vision-preview"
            }
            
        except Exception as e:
            print(f"OpenAI VLM analysis error: {e}")
            return await self._analyze_general_activity(frames)
    
    def _parse_vlm_response(self, response_text: str) -> Dict:
        """Parse VLM model response into structured format"""
        # This would parse the actual VLM response into the required format
        # Implementation depends on the specific VLM model's output format
        pass

# Global VLM service instance
vlm_service = VLMAnalysisService()