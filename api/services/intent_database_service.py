#!/usr/bin/env python3
"""
Intent Database Service
Handles database operations for AI intent detection and action parameter retrieval
"""
import sqlite3
import os
import json
from typing import Dict, List, Any, Optional

class IntentDatabaseService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '../database/eldercare_intents.db')
        
    def _get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            # Initialize database if it doesn't exist
            from api.database.init_intent_actions import init_intent_actions_database
            init_intent_actions_database()
        return sqlite3.connect(self.db_path)
    
    def detect_intent_from_keywords(self, message: str, confidence_threshold: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Detect intent from message using keyword matching with weights
        
        Args:
            message: User's message
            confidence_threshold: Minimum confidence required
            
        Returns:
            Intent information with confidence score
        """
        message_lower = message.lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all active intents with their keywords
        cursor.execute('''
            SELECT i.id, i.intent_name, i.description, i.category, i.confidence_threshold,
                   ik.keyword, ik.weight, ik.context
            FROM intents i
            JOIN intent_keywords ik ON i.id = ik.intent_id
            WHERE i.is_active = 1
            ORDER BY ik.weight DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Calculate intent scores
        intent_scores = {}
        intent_info = {}
        
        for row in results:
            intent_id, intent_name, description, category, threshold, keyword, weight, context = row
            
            # Store intent info
            if intent_name not in intent_info:
                intent_info[intent_name] = {
                    'id': intent_id,
                    'name': intent_name,
                    'description': description,
                    'category': category,
                    'threshold': threshold
                }
            
            # Check if keyword matches
            if keyword.lower() in message_lower:
                if intent_name not in intent_scores:
                    intent_scores[intent_name] = 0
                intent_scores[intent_name] += weight
        
        # Find best matching intent
        if not intent_scores:
            return None
            
        best_intent = max(intent_scores.keys(), key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / 5.0, 1.0)  # Normalize to 0-1 scale
        
        # Check if confidence meets threshold
        intent_threshold = intent_info[best_intent]['threshold']
        if confidence < max(confidence_threshold, intent_threshold):
            return None
            
        return {
            'intent': best_intent,
            'confidence': confidence,
            'category': intent_info[best_intent]['category'],
            'description': intent_info[best_intent]['description'],
            'matched_keywords': [k for k in intent_scores.keys() if intent_scores[k] > 0]
        }
    
    def get_intent_actions(self, intent_name: str, arduino_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get available actions for an intent
        
        Args:
            intent_name: Name of the intent
            arduino_only: If True, only return Arduino-compatible actions
            
        Returns:
            List of action information with parameters
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build query based on arduino_only filter
        query = '''
            SELECT ia.id, ia.action_name, ia.function_name, ia.description, 
                   ia.confirmation_required, ia.risk_level, ia.mqtt_topic, 
                   ia.mqtt_payload_template, ia.arduino_compatible
            FROM intents i
            JOIN intent_actions ia ON i.id = ia.intent_id
            WHERE i.intent_name = ? AND ia.is_active = 1
        '''
        
        params = [intent_name]
        
        if arduino_only:
            query += ' AND ia.arduino_compatible = 1'
        
        cursor.execute(query, params)
        actions = cursor.fetchall()
        
        # Get parameters for each action
        result = []
        for action in actions:
            action_id, action_name, function_name, description, confirmation_required, risk_level, mqtt_topic, mqtt_payload_template, arduino_compatible = action
            
            # Get parameters for this action
            cursor.execute('''
                SELECT parameter_name, parameter_type, default_value, description, 
                       is_required, validation_rule
                FROM action_parameters
                WHERE action_id = ?
            ''', (action_id,))
            
            parameters = {}
            for param_row in cursor.fetchall():
                param_name, param_type, default_value, param_desc, is_required, validation_rule = param_row
                parameters[param_name] = {
                    'type': param_type,
                    'default': default_value,
                    'description': param_desc,
                    'required': bool(is_required),
                    'validation': validation_rule
                }
            
            result.append({
                'id': action_id,
                'action_name': action_name,
                'function_name': function_name,
                'description': description,
                'confirmation_required': bool(confirmation_required),
                'risk_level': risk_level,
                'mqtt_topic': mqtt_topic,
                'mqtt_payload_template': mqtt_payload_template,
                'arduino_compatible': bool(arduino_compatible),
                'parameters': parameters
            })
        
        conn.close()
        return result
    
    def get_action_by_function_name(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get action details by function name"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ia.id, ia.action_name, ia.function_name, ia.description, 
                   ia.confirmation_required, ia.risk_level, ia.mqtt_topic, 
                   ia.mqtt_payload_template, ia.arduino_compatible, i.intent_name
            FROM intent_actions ia
            JOIN intents i ON ia.intent_id = i.id
            WHERE ia.function_name = ? AND ia.is_active = 1
        ''', (function_name,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
            
        action_id, action_name, function_name, description, confirmation_required, risk_level, mqtt_topic, mqtt_payload_template, arduino_compatible, intent_name = result
        
        # Get parameters
        cursor.execute('''
            SELECT parameter_name, parameter_type, default_value, description, 
                   is_required, validation_rule
            FROM action_parameters
            WHERE action_id = ?
        ''', (action_id,))
        
        parameters = {}
        for param_row in cursor.fetchall():
            param_name, param_type, default_value, param_desc, is_required, validation_rule = param_row
            parameters[param_name] = {
                'type': param_type,
                'default': default_value,
                'description': param_desc,
                'required': bool(is_required),
                'validation': validation_rule
            }
        
        conn.close()
        
        return {
            'id': action_id,
            'action_name': action_name,
            'function_name': function_name,
            'description': description,
            'confirmation_required': bool(confirmation_required),
            'risk_level': risk_level,
            'mqtt_topic': mqtt_topic,
            'mqtt_payload_template': mqtt_payload_template,
            'arduino_compatible': bool(arduino_compatible),
            'intent_name': intent_name,
            'parameters': parameters
        }
    
    def generate_action_parameters(self, function_name: str, elder_info: Dict = None, message: str = "") -> Dict[str, Any]:
        """
        Generate action parameters based on database defaults and context
        
        Args:
            function_name: Function name to generate parameters for
            elder_info: Information about the elder
            message: Original user message for context
            
        Returns:
            Dictionary of parameters with values
        """
        action = self.get_action_by_function_name(function_name)
        if not action:
            return {}
            
        parameters = {}
        
        for param_name, param_info in action['parameters'].items():
            param_value = param_info['default']
            
            # Override with context-specific values
            if elder_info:
                if param_name == 'contact_name' and 'family_contact_name' in elder_info:
                    param_value = elder_info['family_contact_name']
                elif param_name == 'phone_number' and 'family_phone' in elder_info:
                    param_value = elder_info['family_phone']
                elif param_name == 'location' and 'location' in elder_info:
                    param_value = elder_info['location']
            
            # Extract values from message context
            if param_name == 'led_state':
                if 'turn on' in message.lower() or 'switch on' in message.lower():
                    param_value = 'ON'
                elif 'turn off' in message.lower() or 'switch off' in message.lower():
                    param_value = 'OFF'
            elif param_name == 'room_name':
                # Detect room from message
                message_lower = message.lower()
                if 'living room' in message_lower or 'lounge' in message_lower:
                    param_value = 'living_room'
                elif 'bedroom' in message_lower or 'sleeping room' in message_lower:
                    param_value = 'bedroom'
                elif 'kitchen' in message_lower or 'cooking area' in message_lower:
                    param_value = 'kitchen'
                elif 'bathroom' in message_lower or 'toilet' in message_lower or 'washroom' in message_lower:
                    param_value = 'bathroom'
            elif param_name == 'arduino_pin':
                # Map room to Arduino pin based on script.ino
                room_pin_map = {
                    'living_room': '8',
                    'bedroom': '9', 
                    'kitchen': '10',
                    'bathroom': '11'
                }
                # Get room from parameters or detect from message
                room = parameters.get('room_name', param_info['default'])
                param_value = room_pin_map.get(room, param_info['default'])
            elif param_name == 'target_temperature':
                # Look for temperature values in message
                import re
                temp_match = re.search(r'(\d+)\s*(?:degrees?|°)', message.lower())
                if temp_match:
                    param_value = temp_match.group(1)
            
            parameters[param_name] = param_value
            
        return parameters
    
    def get_arduino_actions(self) -> List[Dict[str, Any]]:
        """Get all Arduino-compatible actions"""
        return self.get_intent_actions('', arduino_only=True)
    
    def search_intents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all intents in a specific category"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT intent_name, description, confidence_threshold
            FROM intents
            WHERE category = ? AND is_active = 1
            ORDER BY intent_name
        ''', (category,))
        
        results = []
        for row in cursor.fetchall():
            intent_name, description, threshold = row
            results.append({
                'intent': intent_name,
                'description': description,
                'confidence_threshold': threshold,
                'category': category
            })
            
        conn.close()
        return results
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Count active records
        cursor.execute('SELECT COUNT(*) FROM intents WHERE is_active = 1')
        intents_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM intent_keywords')
        keywords_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM intent_actions WHERE is_active = 1')
        actions_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM intent_actions WHERE arduino_compatible = 1 AND is_active = 1')
        arduino_actions_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM action_parameters')
        parameters_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'intents': intents_count,
            'keywords': keywords_count,
            'actions': actions_count,
            'arduino_actions': arduino_actions_count,
            'parameters': parameters_count
        }

# Test function
def test_intent_database_service():
    """Test the intent database service"""
    service = IntentDatabaseService()
    
    print("=== Intent Database Service Test ===")
    
    # Test intent detection
    test_messages = [
        "Can you help me call Sarah?",
        "Turn on the LED light",
        "What's the temperature in the room?",
        "I need emergency help",
        "I'm feeling lonely"
    ]
    
    for message in test_messages:
        intent = service.detect_intent_from_keywords(message)
        if intent:
            print(f"\nMessage: '{message}'")
            print(f"Intent: {intent['intent']} (confidence: {intent['confidence']:.2f})")
            
            # Get actions for this intent
            actions = service.get_intent_actions(intent['intent'])
            for action in actions:
                print(f"  Action: {action['function_name']} ({action['action_name']})")
                if action['arduino_compatible']:
                    print(f"    Arduino: {action['mqtt_topic']} -> {action['mqtt_payload_template']}")
    
    # Show database stats
    stats = service.get_database_stats()
    print(f"\nDatabase Stats: {stats}")

if __name__ == "__main__":
    test_intent_database_service()