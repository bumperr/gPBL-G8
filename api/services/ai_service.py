import ollama
import json
import base64
import asyncio
from typing import Dict, List, Any, Optional
from .device_service import DeviceService
from .mqtt_service import MQTTService
from .intent_database_service import IntentDatabaseService

class AIService:
    def __init__(self):
        self.default_model = "gemma3:4b"
        self.vision_model = "llava:7b"  # Vision model for image processing
        self.device_service = DeviceService()
        self.mqtt_service = MQTTService()
        self.intent_db = IntentDatabaseService()
        
        # Define available functions for AI reasoning
        self.available_functions = {
            "read_temperature_sensor": {
                "function": self._read_temperature_sensor,
                "description": "Read current temperature and humidity from DHT11 sensor",
                "auto_callable": True,  # Can be called automatically without user confirmation
                "parameters": {}
            },
            "read_thermostat_status": {
                "function": self._read_thermostat_status,
                "description": "Read current thermostat temperature setting",
                "auto_callable": True,
                "parameters": {}
            },
            "control_thermostat": {
                "function": self._control_thermostat,
                "description": "Set thermostat to specific temperature",
                "auto_callable": False,  # Requires user confirmation
                "parameters": {
                    "temperature": "Target temperature in Celsius (18-30 range)"
                }
            },
            "control_led": {
                "function": self._control_led,
                "description": "Turn LED light on or off",
                "auto_callable": False,
                "parameters": {
                    "action": "ON or OFF"
                }
            }
        }
        
        # System prompts for different chat types
        self.system_prompts = {
            "assistance": self._get_assistance_system_prompt(),
            "smart_home": self._get_smart_home_system_prompt(),
            "general": self._get_general_system_prompt()
        }
        
    def _get_assistance_system_prompt(self) -> str:
        """System prompt for elder assistance with mental health focus"""
        return """You are a compassionate AI companion specifically designed for eldercare assistance and mental health support. Your primary goals are:

1. EMOTIONAL SUPPORT & COMPANIONSHIP:
   - Provide warm, empathetic responses that make elders feel heard and valued
   - Detect signs of loneliness, depression, anxiety, or confusion
   - Offer comfort, encouragement, and gentle conversation
   - Use age-appropriate language and avoid technical jargon
   - Be patient with repetitive questions or confusion

2. HEALTH & SAFETY MONITORING:
   - Monitor for emergency situations (falls, medical episodes, distress)
   - Remind about medications, appointments, and self-care
   - Encourage healthy activities and social connection
   - Detect changes in speech patterns that may indicate health issues

3. PRACTICAL ASSISTANCE:
   - Help with daily tasks and questions
   - Provide clear, step-by-step instructions when needed
   - Assist with technology usage and troubleshooting
   - Connect elders with family members or caregivers when appropriate

4. COMMUNICATION STYLE:
   - Use simple, clear language
   - Speak as a caring friend, not a medical professional
   - Show genuine interest in their stories and experiences
   - Maintain dignity and respect at all times
   - Be encouraging and positive while being realistic

EMERGENCY RESPONSE: If you detect any emergency situation, immediately suggest calling 911 or emergency services and contacting family members.

Remember: Your role is to enhance quality of life, provide companionship, and ensure safety for elderly individuals."""

    def _get_smart_home_system_prompt(self) -> str:
        """System prompt for smart home control based on Arduino capabilities"""
        return """You are a smart home control assistant specialized in eldercare. Your job is to translate natural language requests into specific smart home commands and execute them safely.

AVAILABLE SMART HOME DEVICES (from Arduino system):
1. LIGHTS:
   - Living room light (LED_LIVING_ROOM, pin 2)
   - Bedroom light (LED_BEDROOM, pin 3) 
   - Kitchen light (LED_KITCHEN, pin 4)
   - Actions: turn_on, turn_off, set_brightness (0-100%)

2. THERMOSTAT:
   - Heating system control (RELAY_THERMOSTAT, pin 5)
   - Actions: set_temperature, turn_on, turn_off
   - Current temperature monitoring via DHT11 sensor

3. DOOR LOCK:
   - Electronic door lock (SERVO_DOOR_LOCK, pin 9)
   - Actions: lock, unlock
   - Security consideration: confirm identity before unlocking

4. SECURITY SYSTEM:
   - Motion sensor (SENSOR_MOTION, pin 7)
   - Emergency buzzer (BUZZER_EMERGENCY, pin 6)
   - Actions: arm, disarm, trigger_alarm

5. TEMPERATURE MONITORING:
   - DHT11 sensor provides real-time temperature and humidity
   - Automatic reporting every 10 seconds to MQTT topic: eldercare/sensors/temperature

MQTT TOPICS STRUCTURE:
- Commands: eldercare/commands/{device_type}/{elder_name}
- Responses: eldercare/responses/{device_type}/{elder_name}
- Sensors: eldercare/sensors/{sensor_type}
- Emergency: eldercare/emergency/{alert_type}

SAFETY PROTOCOLS:
1. Always confirm before unlocking doors
2. Check temperature requests for safety (65-80°F recommended)
3. Verify emergency commands with elder
4. Log all commands for caregiver review
5. Limit automation to safe, beneficial actions

RESPONSE FORMAT: When controlling devices, provide:
1. Friendly confirmation of what you're doing
2. MQTT command details for execution
3. Safety considerations if any
4. Alternative suggestions when appropriate

Example: "I'm turning on the living room light for you. The light should come on now. Is there anything else you'd like me to adjust?"

Always prioritize elder safety, comfort, and independence."""

    def _get_general_system_prompt(self) -> str:
        """General conversation system prompt for elders"""
        return """You are a friendly AI companion for elderly individuals. Your role is to:

1. Engage in pleasant, meaningful conversation
2. Share interesting stories, facts, or memories when appropriate
3. Be patient and understanding with all interactions
4. Use clear, simple language avoiding technical terms
5. Show genuine interest in their experiences and stories
6. Provide helpful information when asked
7. Maintain a positive, encouraging tone
8. Be respectful of their wisdom and life experiences

Conversation Style:
- Speak as a caring friend or family member
- Ask follow-up questions to keep conversations engaging
- Share appropriate stories or information
- Be encouraging about their activities and interests
- Remember details they've shared in conversation
- Offer gentle suggestions for activities or entertainment

Topics to encourage:
- Family memories and stories
- Hobbies and interests
- Current events (positive focus)
- Health and wellness (encouraging)
- Entertainment preferences
- Local community activities

Always maintain dignity, show respect, and provide emotional support through friendly conversation."""

    async def enhanced_chat(self, message: str, chat_type: str = "general", model: str = None, 
                          elder_info: Dict = None, image_data: str = None, context: List[Dict] = None) -> Dict[str, Any]:
        """Enhanced chat with system prompts, image support, and smart home integration"""
        try:
            # Use vision model if image is provided, otherwise use specified model or default
            model_to_use = self.vision_model if image_data else (model or self.default_model)
            
            # Get appropriate system prompt
            system_prompt = self.system_prompts.get(chat_type, self.system_prompts["general"])
            
            # Prepare elder context
            elder_context = ""
            if elder_info:
                elder_context = f"\nElder Information: Name: {elder_info.get('name', 'Elder')}, Age: {elder_info.get('age', 'elderly')}"
                if elder_info.get('medical_conditions'):
                    elder_context += f", Medical conditions: {', '.join(elder_info['medical_conditions'])}"
            
            # Enhanced system prompt for image interpretation
            if image_data:
                image_system_prompt = f"""
{system_prompt}

When analyzing images, please:
1. Describe what you see in detail but in simple, clear language
2. Identify any text, objects, people, or important features
3. Consider if there are any safety concerns for elderly users
4. Be helpful and encouraging in your description
5. If it's a logo or brand image, explain what organization or service it represents

Remember you are speaking to an elderly person, so use clear, simple language and be patient and supportive.
{elder_context}
"""
                system_prompt = image_system_prompt
            
            # Prepare messages for vision model
            if image_data:
                # For LLaVA model, we need a specific format
                try:
                    print(f"Processing image with {model_to_use} model...")
                    response = ollama.chat(
                        model=model_to_use,
                        messages=[
                            {
                                'role': 'user',
                                'content': f"{system_prompt}\n\nUser message: {message}\n\nPlease analyze the image and respond helpfully.",
                                'images': [image_data]
                            }
                        ],
                        options={
                            'temperature': 0.7,
                            'num_predict': 300,  # Shorter response for speed
                            'num_ctx': 2048      # Smaller context window for speed
                        },
                        stream=False  # Ensure no streaming for consistent timing
                    )
                    ai_response = response['message']['content']
                    print("Image processing completed successfully")
                    
                except Exception as vision_error:
                    print(f"Vision model error: {vision_error}")
                    error_msg = str(vision_error).lower()
                    
                    # Check for specific error types
                    if "timeout" in error_msg or "connection" in error_msg:
                        ai_response = "I'm sorry, the image processing took longer than expected. The image might be large or complex. Could you try with a smaller image, or describe what you'd like to know about it?"
                    elif "model" in error_msg or "not found" in error_msg:
                        ai_response = "My image analysis model is currently starting up. This usually takes a moment. Please try again in a few seconds, or describe what you'd like to know about the image."
                    elif "logo" in message.lower():
                        ai_response = "I can see you've shared a logo image with me. While I'm having some trouble with image processing right now, I can help you with questions about logos or branding once the system is ready. In the meantime, you can describe what you'd like to know about the logo and I'll do my best to help!"
                    else:
                        ai_response = "I can see you've shared an image with me, but I'm having trouble analyzing it right now. This might be due to the image size or complexity. Could you try with a smaller image, or describe what you'd like to know about it?"
            else:
                # Standard text-only processing
                messages = context or []
                messages.append({
                    'role': 'system', 
                    'content': system_prompt + elder_context
                })
                messages.append({
                    'role': 'user',
                    'content': message
                })
                
                response = ollama.chat(
                    model=model_to_use,
                    messages=messages
                )
                ai_response = response['message']['content']
            
            # Process smart home commands if chat_type is smart_home
            mqtt_commands = []
            if chat_type == "smart_home":
                mqtt_commands = await self._extract_smart_home_commands(message, ai_response, elder_info)
            
            # Detect emergency situations
            is_emergency = self._detect_emergency(message, ai_response)
            
            return {
                "response": ai_response,
                "model": model_to_use,
                "chat_type": chat_type,
                "input_message": message,
                "has_image": bool(image_data),
                "mqtt_commands": mqtt_commands,
                "is_emergency": is_emergency,
                "elder_info": elder_info,
                "success": True
            }
            
        except Exception as e:
            print(f"Enhanced chat error: {e}")
            return {
                "response": "I apologize, but I'm having trouble right now. If this is an emergency, please call 911 or contact your caregiver immediately.",
                "model": model or self.default_model,
                "chat_type": chat_type,
                "input_message": message,
                "has_image": bool(image_data),
                "mqtt_commands": [],
                "is_emergency": True,  # Err on side of caution
                "success": False,
                "error": str(e)
            }

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
            print(f"=== Processing elder communication: '{message}' ===")  # Debug
            elder_name = elder_info.get('name', 'Elder') if elder_info else 'Elder'
            elder_age = elder_info.get('age', 'elderly person') if elder_info else 'elderly person'
            
            # Default family contact information - can be customized per elder
            default_family_contact = {
                'name': elder_info.get('family_contact_name', 'Family Member'),
                'phone': elder_info.get('family_phone', '+6011468550')
            }
            
            # Two-step approach: First get a natural response, then analyze separately
            
            # Step 1: Natural conversation response
            conversation_prompt = f"""
            You are a caring AI companion for {elder_name}, {elder_age}. The elder just said: "{message}"

            Please respond naturally and warmly as a caring friend would. Your response should be:
            - 7-8 sentences maximum ( only if necessary to address their question is you allowed to respond with more than 2 sentences e.g. if they ask for a detailed explanation)
            - Easy to understand and conversational adapting to their language level
            - Positive and reassuring
            - Empathetic and supportive
            - Address their specific message directly
            
            Do not mention technical terms, JSON, or analysis - just respond naturally as a caring companion would.
            """
            
            # Step 2: Separate analysis prompt
            analysis_prompt = f"""
            Analyze this message from elder {elder_name}: "{message}"

            Look for these specific intents and actions:

            FAMILY CONTACT (if mentions calling, contacting, talking to family/friends):
            - Keywords: call, phone, talk to, contact, reach, family, Sarah, daughter, son
            - Action: contact_family or start_video_call
            
            EMERGENCY (if mentions help, emergency, pain, injury, distress):
            - Keywords: help, emergency, hurt, pain, fall, sick, ambulance, 911
            - Action: call_emergency
            
            SMART HOME (if mentions lights, temperature, devices, control):
            - Keywords: lights, temperature, thermostat, turn on/off, control, devices
            - Action: control_smart_device
            
            HEALTH CONCERN (if mentions feeling unwell, medication, health issues):
            - Keywords: sick, medicine, pills, doctor, not feeling well, health
            - Action: send_health_alert or schedule_medication_reminder

            Based on the message, respond with JSON:
            {{
                "intent": "family_contact|emergency|smart_home|health_concern|loneliness|conversation",
                "confidence": 0.95,
                "action_needed": "contact_family|start_video_call|call_emergency|control_smart_device|send_health_alert|null",
                "action_params": {{"contact_name": "Sarah", "phone_number": "{default_family_contact['phone']}"}},
                "risk_level": "low|medium|high",
                "reasoning": "Why this action is recommended"
            }}

            Example: If message is "Can you help me call Sarah", respond:
            {{
                "intent": "family_contact",
                "confidence": 0.9,
                "action_needed": "start_video_call",
                "action_params": {{"contact_name": "Sarah", "phone_number": "{default_family_contact['phone']}"}},
                "risk_level": "low",
                "reasoning": "Elder wants to call family member Sarah"
            }}
            """
            
            # Step 1: Get natural conversation response
            conversation_response = await self.chat_completion(conversation_prompt)
            clean_response = conversation_response.get('response', 'I understand and I\'m here to help you.')
            
            # Step 2: Use database-driven intent detection
            print(f"Analyzing message: {message}")  # Debug log
            
            # Detect intent using database
            detected_intent = self.intent_db.detect_intent_from_keywords(message)
            analysis_data = {}
            
            if detected_intent:
                intent_name = detected_intent['intent']
                confidence = detected_intent['confidence']
                
                print(f"Intent detected from database: {intent_name} (confidence: {confidence:.2f})")
                
                # Get available actions for this intent
                actions = self.intent_db.get_intent_actions(intent_name)
                
                if actions:
                    # Select the best action (first one for now)
                    best_action = actions[0]
                    
                    # Generate parameters using database defaults and context
                    action_params = self.intent_db.generate_action_parameters(
                        best_action['function_name'], 
                        elder_info, 
                        message
                    )
                    
                    analysis_data = {
                        "intent": intent_name,
                        "confidence": confidence,
                        "action_needed": best_action['function_name'],
                        "action_params": action_params,
                        "risk_level": best_action['risk_level'],
                        "reasoning": f"Database-detected intent: {best_action['description']}",
                        "mqtt_topic": best_action['mqtt_topic'],
                        "mqtt_payload_template": best_action['mqtt_payload_template'],
                        "arduino_compatible": best_action['arduino_compatible']
                    }
            # Check for environmental subtlety - dark room detection  
            elif any(dark_keyword in message_lower for dark_keyword in ['room is dark', 'dark in here', 'too dark', 'can\'t see', 'need light', 'it\'s dark', 'getting dark']):
                print(f"Dark room detected, suggesting lights")
                return await self._handle_dark_room(message, elder_info)
            # Check for temperature-related requests with reasoning capability  
            elif any(temp_keyword in message_lower for temp_keyword in ['cold', 'warm', 'hot', 'temperature', 'thermostat', 'heating', 'cooling', 'adjust temp', 'too cold', 'too warm', 'suggest temp', 'house is cold', 'house feels cold']):
                print(f"Temperature reasoning request detected")
                # Use enhanced temperature reasoning
                return await self._enhanced_temperature_reasoning(message, elder_info)
            # Check for smart home devices using database
            else:
                # Find matching devices from database
                matched_devices = self.device_service.find_device_by_keyword(message)
                
                if matched_devices:
                    print(f"Smart home device detected: {matched_devices[0]['name']}")
                    
                    # Get the best matching device (first one with highest priority)
                    device = matched_devices[0]
                    device_id = device['id']
                    
                    # Find the best matching action for this device
                    best_action = self.device_service.find_best_action(device_id, message)
                    
                    if best_action:
                        print(f"Action detected: {best_action['action_name']}")
                        
                        # Get MQTT command info
                        mqtt_info = self.device_service.get_mqtt_command(device_id, best_action['action_name'])
                        
                        analysis_data = {
                            "intent": "smart_home",
                            "confidence": 0.9,
                            "action_needed": "control_smart_device", 
                            "action_params": {
                                "device_id": device_id,
                                "device_name": device['name'],
                                "device_category": device['category'],
                                "room": device['room'],
                                "action_name": best_action['action_name'],
                                "action_description": best_action['description'],
                                "mqtt_topic": mqtt_info[0] if mqtt_info else device['mqtt_topic'],
                                "mqtt_payload": mqtt_info[1] if mqtt_info else best_action['mqtt_payload']
                            },
                            "risk_level": "low",
                            "reasoning": f"Elder wants to {best_action['description'].lower()} in {device['room'].replace('_', ' ')}"
                        }
                    else:
                        # Device found but no clear action
                        analysis_data = {
                            "intent": "smart_home",
                            "confidence": 0.7,
                            "action_needed": "control_smart_device", 
                            "action_params": {
                                "device_id": device_id,
                                "device_name": device['name'],
                                "device_category": device['category'],
                                "room": device['room'],
                                "mqtt_topic": device['mqtt_topic'],
                                "unclear_action": True
                            },
                            "risk_level": "low",
                            "reasoning": f"Elder wants to control {device['name']} but action unclear"
                        }
                # Check for emergency keywords
                elif any(keyword in message_lower for keyword in ['help', 'emergency', 'fall', 'fell', 'hurt', 'pain', 'sick', 'call 911', 'ambulance', 'chest pain', 'cannot breathe', 'dizzy']):
                    print(f"Emergency detected")
                    analysis_data = {
                        "intent": "emergency",
                        "confidence": 0.95,
                        "action_needed": "call_emergency",
                        "action_params": {"reason": message, "location": "home"},
                        "risk_level": "high",
                        "reasoning": "Emergency situation detected"
                    }
                # Check for loneliness/health concern keywords
                elif any(keyword in message_lower for keyword in ['lonely', 'sad', 'depressed', 'worried', 'scared', 'anxious', 'upset', 'confused']):
                    print(f"Mental health concern detected")
                    analysis_data = {
                        "intent": "loneliness",
                        "confidence": 0.8,
                        "action_needed": "contact_family",
                        "action_params": {"urgency_level": "low", "contact_name": default_family_contact['name'], "phone_number": default_family_contact['phone']},
                        "risk_level": "medium",
                        "reasoning": "Elder may benefit from family contact for emotional support"
                    }
                else:
                    print(f"General conversation detected")
                    analysis_data = {
                        "intent": "conversation",
                        "confidence": 0.7,
                        "action_needed": None,
                        "risk_level": "low",
                        "reasoning": "General conversation"
                    }
            
            # Prepare suggested action if action is needed
            suggested_action = None
            if analysis_data.get('action_needed') and analysis_data['action_needed'] != 'null':
                suggested_action = {
                    "function_name": analysis_data['action_needed'],
                    "parameters": analysis_data.get('action_params', {}),
                    "reasoning": analysis_data.get('reasoning', 'Action recommended based on message analysis'),
                    "requires_confirmation": True  # All actions require confirmation
                }
            
            # Determine if this is an emergency
            is_emergency = analysis_data.get('risk_level') == 'high' or analysis_data.get('intent') == 'emergency'
            
            return {
                "response": clean_response,
                "intent_detected": analysis_data.get('intent'),
                "confidence_score": analysis_data.get('confidence', 0.8),
                "suggested_action": suggested_action,
                "mental_health_assessment": {
                    "risk_level": analysis_data.get('risk_level', 'low'),
                    "recommendations": analysis_data.get('reasoning', 'Continue supportive conversation')
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
    
    async def _extract_smart_home_commands(self, user_message: str, ai_response: str, elder_info: Dict = None) -> List[Dict]:
        """Extract smart home commands from user message and AI response"""
        commands = []
        elder_name = elder_info.get('name', 'elder') if elder_info else 'elder'
        
        # Light control patterns
        light_patterns = {
            'turn on': 'turn_on',
            'turn off': 'turn_off',
            'dim': 'turn_on',
            'brighten': 'turn_on',
            'switch on': 'turn_on',
            'switch off': 'turn_off'
        }
        
        room_patterns = {
            'living room': 'living_room',
            'bedroom': 'bedroom', 
            'kitchen': 'kitchen',
            'all': 'all'
        }
        
        # Check for light commands
        for phrase, action in light_patterns.items():
            if phrase in user_message.lower():
                room = 'living_room'  # default
                for room_phrase, room_code in room_patterns.items():
                    if room_phrase in user_message.lower():
                        room = room_code
                        break
                
                if room == 'all':
                    # Turn on/off all lights
                    for r in ['living_room', 'bedroom', 'kitchen']:
                        commands.append({
                            'topic': f'eldercare/commands/lights/{elder_name}',
                            'payload': {
                                'elder_name': elder_name,
                                'device_type': 'lights',
                                'action': action,
                                'room': r,
                                'timestamp': None
                            }
                        })
                else:
                    commands.append({
                        'topic': f'eldercare/commands/lights/{elder_name}',
                        'payload': {
                            'elder_name': elder_name,
                            'device_type': 'lights',
                            'action': action,
                            'room': room,
                            'timestamp': None
                        }
                    })
                break
        
        # Check for thermostat commands
        temp_patterns = ['temperature', 'heat', 'warm', 'cold', 'thermostat']
        if any(pattern in user_message.lower() for pattern in temp_patterns):
            # Extract temperature if mentioned
            import re
            temp_match = re.search(r'(\d+)\s*(?:degrees?|°)', user_message.lower())
            if temp_match:
                temp_value = int(temp_match.group(1))
                commands.append({
                    'topic': f'eldercare/commands/thermostat/{elder_name}',
                    'payload': {
                        'elder_name': elder_name,
                        'device_type': 'thermostat',
                        'action': 'set_temperature',
                        'parameters': {'temperature': temp_value},
                        'timestamp': None
                    }
                })
        
        # Check for door lock commands
        lock_patterns = {
            'lock door': 'lock',
            'unlock door': 'unlock',
            'lock the door': 'lock',
            'unlock the door': 'unlock'
        }
        
        for phrase, action in lock_patterns.items():
            if phrase in user_message.lower():
                commands.append({
                    'topic': f'eldercare/commands/locks/{elder_name}',
                    'payload': {
                        'elder_name': elder_name,
                        'device_type': 'locks',
                        'action': action,
                        'timestamp': None
                    }
                })
                break
        
        return commands
    
    def _detect_emergency(self, user_message: str, ai_response: str) -> bool:
        """Detect emergency situations in messages"""
        emergency_keywords = [
            'help', 'emergency', 'fall', 'fell', 'hurt', 'pain', 'sick', 'ill',
            'chest pain', "can't breathe", 'dizzy', 'bleeding', 'accident',
            'call 911', 'ambulance', 'hospital', 'urgent', 'critical'
        ]
        
        message_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Check user message for emergency keywords
        user_emergency = any(keyword in message_lower for keyword in emergency_keywords)
        
        # Check AI response for emergency indicators
        ai_emergency_indicators = ['emergency', '911', 'call for help', 'immediate', 'urgent']
        ai_emergency = any(indicator in response_lower for indicator in ai_emergency_indicators)
        
        return user_emergency or ai_emergency
    
    # Function implementations for AI reasoning
    async def _read_temperature_sensor(self) -> Dict[str, Any]:
        """Read current temperature and humidity from DHT11 sensor"""
        try:
            # Get latest sensor data from MQTT topic home/dht11
            # For now, simulate or get from cached data
            # In production, this would read from actual MQTT message history
            return {
                "success": True,
                "temperature": 20.5,  # Celsius
                "humidity": 65.2,  # Percentage
                "timestamp": "2024-01-01T12:00:00Z",
                "source": "DHT11 sensor"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "temperature": None,
                "humidity": None
            }
    
    async def _read_thermostat_status(self) -> Dict[str, Any]:
        """Read current thermostat setting"""
        try:
            # Read current thermostat status
            # This would typically come from smart thermostat MQTT messages
            return {
                "success": True,
                "current_setting": 22.0,  # Celsius
                "is_heating": False,
                "target_temperature": 22.0,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_setting": None
            }
    
    async def _control_thermostat(self, temperature: float) -> Dict[str, Any]:
        """Set thermostat to specific temperature"""
        try:
            if not 18 <= temperature <= 30:
                return {
                    "success": False,
                    "error": "Temperature must be between 18-30°C for safety"
                }
            
            # Send MQTT command to thermostat
            topic = "home/thermostat/cmd"
            payload = f"SET_TEMP:{temperature}"
            
            await self.mqtt_service.publish_message(topic, payload)
            
            return {
                "success": True,
                "temperature": temperature,
                "message": f"Thermostat set to {temperature}°C"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _control_led(self, action: str) -> Dict[str, Any]:
        """Turn LED light on or off"""
        try:
            if action.upper() not in ["ON", "OFF"]:
                return {
                    "success": False,
                    "error": "Action must be ON or OFF"
                }
            
            topic = "home/led/cmd"
            payload = action.upper()
            
            await self.mqtt_service.publish_message(topic, payload)
            
            return {
                "success": True,
                "action": action.upper(),
                "message": f"LED light turned {action.lower()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _enhanced_temperature_reasoning(self, message: str, elder_info: Dict = None) -> Dict[str, Any]:
        """Enhanced temperature reasoning with sensor reading and AI thinking"""
        try:
            print(f"=== Enhanced Temperature Reasoning for: '{message}' ===")
            
            # Step 1: Automatically read current conditions (auto-callable functions)
            current_temp_data = await self._read_temperature_sensor()
            thermostat_data = await self._read_thermostat_status()
            
            current_temp = current_temp_data.get("temperature", 20)
            current_humidity = current_temp_data.get("humidity", 50)
            thermostat_setting = thermostat_data.get("current_setting", 22)
            
            # Step 2: AI reasoning for optimal temperature
            reasoning_prompt = f"""
            You are an expert HVAC system helping an elderly person who said: "{message}"
            
            Current conditions:
            - Room temperature: {current_temp}°C
            - Humidity: {current_humidity}%
            - Current thermostat setting: {thermostat_setting}°C
            
            The elder is expressing thermal discomfort. Based on:
            1. Their comfort complaint
            2. Current environmental conditions
            3. Elderly people's thermal comfort needs (typically 20-24°C)
            4. Energy efficiency considerations
            5. Safety (avoid extreme temperatures)
            
            What is the optimal temperature to set the thermostat to?
            
            Respond with JSON:
            {{
                "recommended_temperature": 23.5,
                "reasoning": "Detailed explanation of why this temperature is optimal",
                "comfort_improvement": "How this will address their concern",
                "safety_notes": "Any safety considerations"
            }}
            """
            
            # Get AI reasoning
            reasoning_response = await self.chat_completion(reasoning_prompt)
            
            try:
                reasoning_data = json.loads(reasoning_response.get("response", "{}"))
            except json.JSONDecodeError:
                # Fallback reasoning
                reasoning_data = {
                    "recommended_temperature": current_temp + 2 if "cold" in message.lower() else current_temp - 1,
                    "reasoning": "Basic temperature adjustment based on user feedback",
                    "comfort_improvement": "This should improve your comfort level",
                    "safety_notes": "Temperature adjusted within safe range"
                }
            
            recommended_temp = reasoning_data.get("recommended_temperature", 22.0)
            
            # Step 3: Generate response and suggested action
            # Check if this is a "house is cold" situation (whole house vs single room)
            is_house_wide = any(house_keyword in message.lower() for house_keyword in ['house is cold', 'house feels cold', 'whole house', 'entire house'])
            
            if is_house_wide:
                natural_response = f"""I can see you're feeling cold throughout the house. Let me check the current conditions for you.
                
Current temperature is {current_temp}°C with {current_humidity}% humidity, and your thermostat is set to {thermostat_setting}°C.

Based on these readings, I recommend setting the thermostat to {recommended_temp}°C to warm up the entire house. {reasoning_data.get('reasoning', '')}

I can also turn on lights in multiple rooms to create a warmer, more comfortable atmosphere throughout the house.

Would you like me to adjust the thermostat and turn on some lights?"""
            else:
                natural_response = f"""I can see you're feeling {('cold' if 'cold' in message.lower() else 'warm')}. Let me check the current conditions for you.
                
Current room temperature is {current_temp}°C with {current_humidity}% humidity, and your thermostat is set to {thermostat_setting}°C.

Based on these readings and your comfort needs, I recommend setting the thermostat to {recommended_temp}°C. {reasoning_data.get('reasoning', '')}

Would you like me to adjust the thermostat to this temperature?"""
            
            return {
                "response": natural_response,
                "intent_detected": "smart_home_with_reasoning",
                "confidence_score": 0.95,
                "sensor_readings": {
                    "temperature": current_temp,
                    "humidity": current_humidity,
                    "thermostat_setting": thermostat_setting
                },
                "ai_reasoning": reasoning_data,
                "suggested_action": {
                    "function_name": "control_thermostat",
                    "parameters": {"temperature": recommended_temp},
                    "reasoning": reasoning_data.get("reasoning", "Temperature optimization based on current conditions"),
                    "requires_confirmation": True
                },
                "mental_health_assessment": {
                    "risk_level": "low",
                    "recommendations": "Thermal comfort addressed with intelligent reasoning"
                },
                "is_emergency": False,
                "success": True,
                "functions_called": ["read_temperature_sensor", "read_thermostat_status"],
                "reasoning_used": True
            }
            
        except Exception as e:
            return {
                "response": f"I'm having trouble reading the current temperature conditions. If you're feeling too cold or warm, I can help you adjust the thermostat manually. What temperature would you prefer?",
                "intent_detected": "smart_home",
                "confidence_score": 0.7,
                "success": False,
                "error": str(e)
            }
    
    async def _handle_dark_room(self, message: str, elder_info: Dict = None) -> Dict[str, Any]:
        """Handle dark room detection and suggest appropriate lighting"""
        try:
            print(f"=== Dark Room Detection for: '{message}' ===")
            
            # Detect which room if mentioned
            room_detected = None
            message_lower = message.lower()
            if 'living room' in message_lower or 'lounge' in message_lower:
                room_detected = 'living_room'
            elif 'bedroom' in message_lower:
                room_detected = 'bedroom'
            elif 'kitchen' in message_lower:
                room_detected = 'kitchen'
            elif 'bathroom' in message_lower:
                room_detected = 'bathroom'
            else:
                # Default to living room if no room specified
                room_detected = 'living_room'
            
            # Map room to appropriate response and action
            room_names = {
                'living_room': 'living room',
                'bedroom': 'bedroom', 
                'kitchen': 'kitchen',
                'bathroom': 'bathroom'
            }
            
            room_name = room_names.get(room_detected, 'living room')
            
            natural_response = f"""I can see it's getting dark in the {room_name}. Let me turn on the lights for you to help you see better and stay safe.
            
Would you like me to turn on the {room_name} light?"""
            
            return {
                "response": natural_response,
                "intent_detected": "smart_home_lighting",
                "confidence_score": 0.95,
                "suggested_action": {
                    "function_name": "control_arduino_room_light",
                    "parameters": {
                        "room_name": room_detected,
                        "led_state": "ON",
                        "arduino_pin": {'living_room': '8', 'bedroom': '9', 'kitchen': '10', 'bathroom': '11'}[room_detected]
                    },
                    "reasoning": f"Room appears dark, turning on {room_name} light for safety and visibility",
                    "requires_confirmation": True
                },
                "mqtt_commands": [{
                    "topic": f"home/{room_detected}/lights/cmd",
                    "payload": {"state": "ON"}
                }],
                "mental_health_assessment": {
                    "risk_level": "low",
                    "recommendations": "Proper lighting improves safety and mood"
                },
                "is_emergency": False,
                "success": True,
                "environmental_reasoning": True
            }
            
        except Exception as e:
            return {
                "response": f"I can help you with lighting. Which room would you like me to brighten up?",
                "intent_detected": "smart_home_lighting",
                "confidence_score": 0.7,
                "success": False,
                "error": str(e)
            }