import ollama
from typing import Dict, List, Any

class AIService:
    def __init__(self):
        self.default_model = "llama3.2"
        
    async def chat_completion(self, message: str, model: str = None, context: List[Dict] = None) -> Dict[str, Any]:
        """Generate AI response to a message"""
        try:
            model = model or self.default_model
            
            # Prepare messages
            messages = context or []
            messages.append({'role': 'user', 'content': message})
            
            # Get response from Ollama
            response = ollama.chat(
                model=model,
                messages=messages
            )
            
            ai_response = response['message']['content']
            
            return {
                "response": ai_response,
                "model": model,
                "input_message": message,
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "model": model or self.default_model,
                "input_message": message,
                "success": False,
                "error": str(e)
            }
            
    async def process_elder_speech(self, transcribed_text: str, elder_info: Dict = None) -> Dict[str, Any]:
        """Process speech from elder and generate appropriate response"""
        return await self._process_elder_communication(transcribed_text, elder_info, "voice")
    
    async def process_elder_text(self, text: str, elder_info: Dict = None) -> Dict[str, Any]:
        """Process text from elder and generate appropriate response with enhanced analysis"""
        return await self._process_elder_communication(text, elder_info, "text")
    
    async def _process_elder_communication(self, message: str, elder_info: Dict = None, input_type: str = "text") -> Dict[str, Any]:
        """Enhanced processing for elder communication with mental health focus and intent detection"""
        try:
            elder_name = elder_info.get('name', 'Elder') if elder_info else 'Elder'
            elder_age = elder_info.get('age', 'elderly person') if elder_info else 'elderly person'
            
            # Enhanced system prompt for mental health companionship and intent detection
            enhanced_prompt = f"""
            You are a specialized AI companion for mental health support and eldercare assistance. You are talking to {elder_name}, {elder_age}.

            The elder said: "{message}"

            Your role includes:
            1. MENTAL HEALTH COMPANIONSHIP: Provide emotional support, detect mood changes, offer comfort and engagement
            2. INTENT DETECTION: Identify what the elder wants or needs 
            3. FUNCTION CALLING: Determine what action should be taken based on their request

            Analyze the message and provide:
            1. A warm, empathetic response (2-3 sentences max, easy to understand)
            2. Intent classification
            3. Confidence score (0-1)
            4. Suggested function call with parameters
            5. Mental health assessment

            Available intents: emergency, health_concern, loneliness, request_help, conversation, smart_home, medication, family_contact

            Available functions:
            - call_emergency(reason, location)
            - contact_family(urgency_level, message)
            - control_smart_device(device, action, value)
            - schedule_medication_reminder(medication, time)
            - play_music(genre, mood)
            - start_video_call(contact_name)
            - send_health_alert(concern, severity)

            Respond ONLY with a JSON object in this exact format:
            {{
                "response": "Your caring response here",
                "intent_detected": "detected_intent",
                "confidence_score": 0.95,
                "suggested_action": {{
                    "function_name": "function_to_call",
                    "parameters": {{"param1": "value1", "param2": "value2"}},
                    "reasoning": "Why this action is recommended"
                }},
                "mental_health_assessment": {{
                    "mood_indicators": ["positive", "lonely", "anxious"],
                    "risk_level": "low/medium/high",
                    "recommendations": "Brief recommendation"
                }}
            }}

            Remember: Be warm, caring, and focus on the elder's emotional wellbeing while providing practical help.
            """
            
            # Get AI response
            ai_response = await self.chat_completion(enhanced_prompt)
            
            # Try to parse JSON response
            try:
                import json
                if ai_response.get('response', '').strip().startswith('{'):
                    parsed_response = json.loads(ai_response['response'])
                    
                    # Legacy emergency detection as fallback
                    emergency_keywords = ['help', 'emergency', 'fall', 'hurt', 'pain', 'sick', 'call 911', 'ambulance', 'chest pain', 'can\'t breathe']
                    is_emergency = any(keyword in message.lower() for keyword in emergency_keywords) or parsed_response.get('intent_detected') == 'emergency'
                    
                    return {
                        "response": parsed_response.get('response', 'I understand you need assistance.'),
                        "intent_detected": parsed_response.get('intent_detected'),
                        "confidence_score": parsed_response.get('confidence_score', 0.8),
                        "suggested_action": parsed_response.get('suggested_action'),
                        "mental_health_assessment": parsed_response.get('mental_health_assessment'),
                        "is_emergency": is_emergency,
                        "elder_message": message,
                        "elder_info": elder_info,
                        "input_type": input_type,
                        "success": True
                    }
                else:
                    # Fallback to simple response if not JSON
                    raise ValueError("Response not in JSON format")
                    
            except (json.JSONDecodeError, ValueError):
                # Fallback processing
                emergency_keywords = ['help', 'emergency', 'fall', 'hurt', 'pain', 'sick', 'call 911', 'ambulance']
                is_emergency = any(keyword in message.lower() for keyword in emergency_keywords)
                
                return {
                    "response": ai_response.get('response', 'I understand and I\'m here to help you.'),
                    "intent_detected": "emergency" if is_emergency else "conversation",
                    "confidence_score": 0.9 if is_emergency else 0.7,
                    "suggested_action": {
                        "function_name": "call_emergency" if is_emergency else "provide_companionship",
                        "parameters": {"reason": message, "location": "home"} if is_emergency else {"type": "general_support"},
                        "reasoning": "Emergency detected in message" if is_emergency else "Providing companionship"
                    },
                    "mental_health_assessment": {
                        "mood_indicators": ["distressed"] if is_emergency else ["needs_support"],
                        "risk_level": "high" if is_emergency else "low",
                        "recommendations": "Immediate assistance required" if is_emergency else "Continue conversation"
                    },
                    "is_emergency": is_emergency,
                    "elder_message": message,
                    "elder_info": elder_info,
                    "input_type": input_type,
                    "success": True
                }
            
        except Exception as e:
            return {
                "response": "I'm here for you. If this is an emergency, please call 911 or press your emergency button.",
                "intent_detected": "emergency",
                "confidence_score": 1.0,
                "suggested_action": {
                    "function_name": "call_emergency",
                    "parameters": {"reason": "AI system error", "location": "home"},
                    "reasoning": "System error occurred, treating as potential emergency"
                },
                "mental_health_assessment": {
                    "mood_indicators": ["system_error"],
                    "risk_level": "medium",
                    "recommendations": "Manual check required due to system error"
                },
                "is_emergency": True,  # Err on the side of caution
                "elder_message": message,
                "elder_info": elder_info,
                "input_type": input_type,
                "success": False,
                "error": str(e)
            }
            
    async def list_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return [self.default_model]