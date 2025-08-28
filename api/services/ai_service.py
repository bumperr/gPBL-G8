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
        try:
            # Enhance the prompt for elder care context
            elder_name = elder_info.get('name', 'Elder') if elder_info else 'Elder'
            
            enhanced_prompt = f"""
            You are a caring AI assistant helping an elderly person named {elder_name}. 
            The elder said: "{transcribed_text}"
            
            Please respond in a warm, caring, and clear manner. Consider:
            - If this sounds like an emergency, clearly indicate that help is being contacted
            - If it's a question, provide helpful and simple answers
            - If it's a request for assistance, offer appropriate guidance
            - Keep responses conversational and easy to understand
            - Show empathy and care in your responses
            """
            
            response = await self.chat_completion(enhanced_prompt)
            
            # Check for emergency keywords
            emergency_keywords = ['help', 'emergency', 'fall', 'hurt', 'pain', 'sick', 'call 911', 'ambulance']
            is_emergency = any(keyword in transcribed_text.lower() for keyword in emergency_keywords)
            
            return {
                **response,
                "is_emergency": is_emergency,
                "elder_message": transcribed_text,
                "elder_info": elder_info
            }
            
        except Exception as e:
            return {
                "response": "I'm having trouble right now. If this is an emergency, please call 911.",
                "success": False,
                "error": str(e),
                "is_emergency": True,  # Err on the side of caution
                "elder_message": transcribed_text,
                "elder_info": elder_info
            }
            
    async def list_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return [self.default_model]