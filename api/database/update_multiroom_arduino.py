#!/usr/bin/env python3
"""
Update the intent database with multi-room Arduino control based on the updated script.ino
Covers: Living Room (pin 8), Bedroom (pin 9), Kitchen (pin 10), Bathroom (pin 11)
"""
import sqlite3
import os

def update_multiroom_arduino():
    """Add multi-room Arduino light control to the database"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'eldercare_intents.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Please run init_intent_actions.py first")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add new room-specific intents
    room_intents_data = [
        ('living_room_lights', 'Control living room lights via Arduino pin 8', 'arduino', 0.8, 1),
        ('bedroom_lights', 'Control bedroom lights via Arduino pin 9', 'arduino', 0.8, 1),
        ('kitchen_lights', 'Control kitchen lights via Arduino pin 10', 'arduino', 0.8, 1),
        ('bathroom_lights', 'Control bathroom lights via Arduino pin 11', 'arduino', 0.8, 1),
    ]
    
    # Insert new intents
    for intent_data in room_intents_data:
        cursor.execute('''
            INSERT OR IGNORE INTO intents (intent_name, description, category, confidence_threshold, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', intent_data)
    
    # Get intent IDs
    intent_ids = {}
    cursor.execute('SELECT id, intent_name FROM intents')
    for intent_id, name in cursor.fetchall():
        intent_ids[name] = intent_id
    
    # Add room-specific keywords
    room_keywords_data = [
        # Living Room
        (intent_ids['living_room_lights'], 'living room light', 2.5, 'room_specific'),
        (intent_ids['living_room_lights'], 'living room lights', 2.5, 'room_specific'),
        (intent_ids['living_room_lights'], 'lounge light', 2.0, 'room_specific'),
        (intent_ids['living_room_lights'], 'main light', 1.8, 'room_specific'),
        (intent_ids['living_room_lights'], 'front room light', 2.0, 'room_specific'),
        
        # Bedroom
        (intent_ids['bedroom_lights'], 'bedroom light', 2.5, 'room_specific'),
        (intent_ids['bedroom_lights'], 'bedroom lights', 2.5, 'room_specific'),
        (intent_ids['bedroom_lights'], 'room light', 1.8, 'room_specific'),
        (intent_ids['bedroom_lights'], 'sleeping room light', 2.0, 'room_specific'),
        
        # Kitchen
        (intent_ids['kitchen_lights'], 'kitchen light', 2.5, 'room_specific'),
        (intent_ids['kitchen_lights'], 'kitchen lights', 2.5, 'room_specific'),
        (intent_ids['kitchen_lights'], 'cooking area light', 2.0, 'room_specific'),
        
        # Bathroom
        (intent_ids['bathroom_lights'], 'bathroom light', 2.5, 'room_specific'),
        (intent_ids['bathroom_lights'], 'bathroom lights', 2.5, 'room_specific'),
        (intent_ids['bathroom_lights'], 'toilet light', 2.0, 'room_specific'),
        (intent_ids['bathroom_lights'], 'washroom light', 2.0, 'room_specific'),
        
        # Generic keywords that should trigger room detection
        (intent_ids['living_room_lights'], 'turn on lights', 1.0, 'generic_action'),
        (intent_ids['bedroom_lights'], 'turn on lights', 1.0, 'generic_action'),
        (intent_ids['kitchen_lights'], 'turn on lights', 1.0, 'generic_action'),
        (intent_ids['bathroom_lights'], 'turn on lights', 1.0, 'generic_action'),
    ]
    
    # Insert keywords
    for keyword_data in room_keywords_data:
        cursor.execute('''
            INSERT OR IGNORE INTO intent_keywords (intent_id, keyword, weight, context)
            VALUES (?, ?, ?, ?)
        ''', keyword_data)
    
    # Add room-specific actions based on Arduino pins
    room_actions_data = [
        # Living Room (Arduino Pin 8)
        (intent_ids['living_room_lights'], 'Turn On Living Room Light', 'control_arduino_room_light', 
         'Turn on living room light via Arduino pin 8', 1, 'low', 'home/living_room/lights/cmd', 'ON', 1, 1),
        (intent_ids['living_room_lights'], 'Turn Off Living Room Light', 'control_arduino_room_light', 
         'Turn off living room light via Arduino pin 8', 1, 'low', 'home/living_room/lights/cmd', 'OFF', 1, 1),
        
        # Bedroom (Arduino Pin 9)  
        (intent_ids['bedroom_lights'], 'Turn On Bedroom Light', 'control_arduino_room_light', 
         'Turn on bedroom light via Arduino pin 9', 1, 'low', 'home/bedroom/lights/cmd', 'ON', 1, 1),
        (intent_ids['bedroom_lights'], 'Turn Off Bedroom Light', 'control_arduino_room_light', 
         'Turn off bedroom light via Arduino pin 9', 1, 'low', 'home/bedroom/lights/cmd', 'OFF', 1, 1),
        
        # Kitchen (Arduino Pin 10)
        (intent_ids['kitchen_lights'], 'Turn On Kitchen Light', 'control_arduino_room_light', 
         'Turn on kitchen light via Arduino pin 10', 1, 'low', 'home/kitchen/lights/cmd', 'ON', 1, 1),
        (intent_ids['kitchen_lights'], 'Turn Off Kitchen Light', 'control_arduino_room_light', 
         'Turn off kitchen light via Arduino pin 10', 1, 'low', 'home/kitchen/lights/cmd', 'OFF', 1, 1),
        
        # Bathroom (Arduino Pin 11)
        (intent_ids['bathroom_lights'], 'Turn On Bathroom Light', 'control_arduino_room_light', 
         'Turn on bathroom light via Arduino pin 11', 1, 'low', 'home/bathroom/lights/cmd', 'ON', 1, 1),
        (intent_ids['bathroom_lights'], 'Turn Off Bathroom Light', 'control_arduino_room_light', 
         'Turn off bathroom light via Arduino pin 11', 1, 'low', 'home/bathroom/lights/cmd', 'OFF', 1, 1),
    ]
    
    # Insert actions
    for action_data in room_actions_data:
        cursor.execute('''
            INSERT OR IGNORE INTO intent_actions (intent_id, action_name, function_name, description, 
                                                  confirmation_required, risk_level, mqtt_topic, 
                                                  mqtt_payload_template, arduino_compatible, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', action_data)
    
    # Get action IDs for parameters
    action_ids = {}
    cursor.execute('SELECT id, function_name, mqtt_topic FROM intent_actions WHERE function_name = "control_arduino_room_light"')
    for action_id, function_name, mqtt_topic in cursor.fetchall():
        action_ids[mqtt_topic] = action_id
    
    # Add parameters for room-specific actions
    room_parameters_data = []
    
    room_pin_mapping = {
        'home/living_room/lights/cmd': ('living_room', 8),
        'home/bedroom/lights/cmd': ('bedroom', 9), 
        'home/kitchen/lights/cmd': ('kitchen', 10),
        'home/bathroom/lights/cmd': ('bathroom', 11)
    }
    
    for mqtt_topic, (room_name, pin_number) in room_pin_mapping.items():
        if mqtt_topic in action_ids:
            action_id = action_ids[mqtt_topic]
            
            # Add parameters for each room's light control
            room_parameters_data.extend([
                (action_id, 'room_name', 'string', room_name, f'Name of the room ({room_name})', 1, None),
                (action_id, 'arduino_pin', 'integer', str(pin_number), f'Arduino pin number for {room_name} light', 0, None),
                (action_id, 'led_state', 'string', 'ON', 'LED state: ON or OFF', 1, '^(ON|OFF)$'),
                (action_id, 'device_type', 'string', 'room_light', 'Type of device being controlled', 0, None),
            ])
    
    # Insert parameters
    for param_data in room_parameters_data:
        cursor.execute('''
            INSERT OR IGNORE INTO action_parameters (action_id, parameter_name, parameter_type, 
                                                    default_value, description, is_required, validation_rule)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', param_data)
    
    conn.commit()
    conn.close()
    
    print("Multi-room Arduino control updated successfully!")
    print("\nArduino Pin Assignments:")
    print("  Living Room Light -> Pin 8  -> home/living_room/lights/cmd")
    print("  Bedroom Light     -> Pin 9  -> home/bedroom/lights/cmd") 
    print("  Kitchen Light     -> Pin 10 -> home/kitchen/lights/cmd")
    print("  Bathroom Light    -> Pin 11 -> home/bathroom/lights/cmd")
    
    print(f"\nAdded:")
    print(f"  - {len(room_intents_data)} new room-specific intents")
    print(f"  - {len(room_keywords_data)} room-specific keywords")
    print(f"  - {len(room_actions_data)} Arduino actions")
    print(f"  - {len(room_parameters_data)} action parameters")

if __name__ == "__main__":
    update_multiroom_arduino()