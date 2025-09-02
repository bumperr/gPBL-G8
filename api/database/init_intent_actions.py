#!/usr/bin/env python3
"""
Enhanced database initialization with intent actions and parameters
Based on Arduino script and call functionality
"""
import sqlite3
import os
import json

def init_intent_actions_database():
    """Initialize enhanced database with intent actions, parameters, and Arduino-specific data"""
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(__file__)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, 'eldercare_intents.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create intents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intent_name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT NOT NULL,
            confidence_threshold REAL DEFAULT 0.7,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create intent_keywords table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intent_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intent_id INTEGER,
            keyword TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            context TEXT,
            FOREIGN KEY (intent_id) REFERENCES intents (id)
        )
    ''')
    
    # Create intent_actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intent_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intent_id INTEGER,
            action_name TEXT NOT NULL,
            function_name TEXT NOT NULL,
            description TEXT,
            confirmation_required BOOLEAN DEFAULT 1,
            risk_level TEXT DEFAULT 'low',
            mqtt_topic TEXT,
            mqtt_payload_template TEXT,
            arduino_compatible BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (intent_id) REFERENCES intents (id)
        )
    ''')
    
    # Create action_parameters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS action_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id INTEGER,
            parameter_name TEXT NOT NULL,
            parameter_type TEXT NOT NULL, -- string, integer, boolean, json
            default_value TEXT,
            description TEXT,
            is_required BOOLEAN DEFAULT 0,
            validation_rule TEXT,
            FOREIGN KEY (action_id) REFERENCES intent_actions (id)
        )
    ''')
    
    # Clear existing data for fresh start
    cursor.execute('DELETE FROM action_parameters')
    cursor.execute('DELETE FROM intent_actions')
    cursor.execute('DELETE FROM intent_keywords')
    cursor.execute('DELETE FROM intents')
    
    # Insert intent categories based on AI service analysis
    intents_data = [
        # Family & Communication
        ('family_contact', 'Contact family members or caregivers', 'communication', 0.8, 1),
        ('emergency', 'Emergency situations requiring immediate help', 'emergency', 0.9, 1),
        
        # Smart Home & Arduino Control
        ('smart_home', 'Control smart home devices and Arduino systems', 'automation', 0.7, 1),
        ('arduino_led_control', 'Control Arduino LED based on script.ino', 'arduino', 0.8, 1),
        ('temperature_monitoring', 'Monitor and control temperature via Arduino DHT11', 'arduino', 0.7, 1),
        
        # Health & Wellness
        ('health_concern', 'Health-related issues and medication', 'health', 0.8, 1),
        ('loneliness', 'Emotional support and companionship', 'social', 0.6, 1),
        ('conversation', 'General conversation and chat', 'social', 0.5, 1),
    ]
    
    cursor.executemany('''
        INSERT INTO intents (intent_name, description, category, confidence_threshold, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', intents_data)
    
    # Get intent IDs
    intent_ids = {}
    cursor.execute('SELECT id, intent_name FROM intents')
    for intent_id, name in cursor.fetchall():
        intent_ids[name] = intent_id
    
    # Insert keywords based on Arduino script and common patterns
    keywords_data = [
        # Family contact keywords
        (intent_ids['family_contact'], 'call', 2.0, 'communication'),
        (intent_ids['family_contact'], 'phone', 2.0, 'communication'),
        (intent_ids['family_contact'], 'contact', 1.5, 'communication'),
        (intent_ids['family_contact'], 'sarah', 2.0, 'family_name'),
        (intent_ids['family_contact'], 'family', 1.8, 'communication'),
        (intent_ids['family_contact'], 'daughter', 1.8, 'family_relation'),
        (intent_ids['family_contact'], 'son', 1.8, 'family_relation'),
        (intent_ids['family_contact'], 'video call', 2.0, 'communication'),
        (intent_ids['family_contact'], 'whatsapp', 1.5, 'communication'),
        
        # Emergency keywords
        (intent_ids['emergency'], 'help', 2.0, 'urgent'),
        (intent_ids['emergency'], 'emergency', 2.5, 'urgent'),
        (intent_ids['emergency'], 'pain', 1.8, 'medical'),
        (intent_ids['emergency'], 'hurt', 1.8, 'medical'),
        (intent_ids['emergency'], 'fall', 2.0, 'medical'),
        (intent_ids['emergency'], 'sick', 1.5, 'medical'),
        (intent_ids['emergency'], 'ambulance', 2.0, 'medical'),
        (intent_ids['emergency'], '911', 2.5, 'emergency_number'),
        
        # Arduino LED control (from script.ino)
        (intent_ids['arduino_led_control'], 'led', 2.0, 'arduino_device'),
        (intent_ids['arduino_led_control'], 'light', 1.8, 'arduino_device'),
        (intent_ids['arduino_led_control'], 'turn on', 1.5, 'arduino_action'),
        (intent_ids['arduino_led_control'], 'turn off', 1.5, 'arduino_action'),
        (intent_ids['arduino_led_control'], 'switch on', 1.5, 'arduino_action'),
        (intent_ids['arduino_led_control'], 'switch off', 1.5, 'arduino_action'),
        
        # Temperature monitoring (from DHT11 in script.ino)
        (intent_ids['temperature_monitoring'], 'temperature', 2.0, 'arduino_sensor'),
        (intent_ids['temperature_monitoring'], 'humidity', 1.8, 'arduino_sensor'),
        (intent_ids['temperature_monitoring'], 'too hot', 1.5, 'comfort'),
        (intent_ids['temperature_monitoring'], 'too cold', 1.5, 'comfort'),
        (intent_ids['temperature_monitoring'], 'room temp', 1.8, 'arduino_sensor'),
        (intent_ids['temperature_monitoring'], 'thermostat', 1.5, 'climate_control'),
        
        # General smart home
        (intent_ids['smart_home'], 'smart home', 2.0, 'automation'),
        (intent_ids['smart_home'], 'control', 1.5, 'automation'),
        (intent_ids['smart_home'], 'device', 1.2, 'automation'),
        
        # Health keywords
        (intent_ids['health_concern'], 'medication', 1.8, 'health'),
        (intent_ids['health_concern'], 'pills', 1.8, 'health'),
        (intent_ids['health_concern'], 'doctor', 1.5, 'health'),
        (intent_ids['health_concern'], 'not feeling well', 2.0, 'health'),
        
        # Social keywords
        (intent_ids['loneliness'], 'lonely', 2.0, 'emotional'),
        (intent_ids['loneliness'], 'sad', 1.5, 'emotional'),
        (intent_ids['loneliness'], 'talk', 1.2, 'social'),
        (intent_ids['conversation'], 'hello', 1.0, 'greeting'),
        (intent_ids['conversation'], 'how are you', 1.2, 'greeting'),
    ]
    
    cursor.executemany('''
        INSERT INTO intent_keywords (intent_id, keyword, weight, context)
        VALUES (?, ?, ?, ?)
    ''', keywords_data)
    
    # Insert intent actions based on Arduino capabilities and call functionality
    actions_data = [
        # Family contact actions
        (intent_ids['family_contact'], 'Start Video Call', 'start_video_call', 'Initiate video call via WhatsApp', 1, 'low', None, None, 0, 1),
        (intent_ids['family_contact'], 'Contact Family', 'contact_family', 'Contact family member through various means', 1, 'low', None, None, 0, 1),
        
        # Emergency actions
        (intent_ids['emergency'], 'Call Emergency Services', 'call_emergency', 'Call 911 or emergency services', 1, 'high', None, None, 0, 1),
        (intent_ids['emergency'], 'Send Health Alert', 'send_health_alert', 'Alert caregivers about health concern', 1, 'medium', None, None, 0, 1),
        
        # Arduino LED control actions (based on script.ino)
        (intent_ids['arduino_led_control'], 'Turn On Arduino LED', 'control_arduino_led', 'Turn on LED connected to Arduino pin 8', 1, 'low', 'home/led/cmd', 'ON', 1, 1),
        (intent_ids['arduino_led_control'], 'Turn Off Arduino LED', 'control_arduino_led', 'Turn off LED connected to Arduino pin 8', 1, 'low', 'home/led/cmd', 'OFF', 1, 1),
        
        # Temperature monitoring actions (based on DHT11 sensor)
        (intent_ids['temperature_monitoring'], 'Read Room Temperature', 'read_arduino_sensors', 'Get temperature and humidity from DHT11 sensor', 0, 'low', 'home/dht11', None, 1, 1),
        (intent_ids['temperature_monitoring'], 'Set Target Temperature', 'set_target_temperature', 'Set target temperature for room', 1, 'low', 'home/room/data', '{temperature},{humidity}', 1, 1),
        
        # Smart home general actions
        (intent_ids['smart_home'], 'Control Smart Device', 'control_smart_device', 'Control various smart home devices', 1, 'medium', None, None, 0, 1),
        
        # Health actions
        (intent_ids['health_concern'], 'Schedule Medication Reminder', 'schedule_medication_reminder', 'Set up medication reminders', 1, 'medium', None, None, 0, 1),
        
        # Social actions
        (intent_ids['loneliness'], 'Provide Companionship', 'provide_companionship', 'Engage in supportive conversation', 0, 'low', None, None, 0, 1),
        (intent_ids['conversation'], 'General Conversation', 'general_conversation', 'Respond to general conversation', 0, 'low', None, None, 0, 1),
    ]
    
    cursor.executemany('''
        INSERT INTO intent_actions (intent_id, action_name, function_name, description, confirmation_required, 
                                   risk_level, mqtt_topic, mqtt_payload_template, arduino_compatible, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', actions_data)
    
    # Get action IDs
    action_ids = {}
    cursor.execute('SELECT id, function_name FROM intent_actions')
    for action_id, function_name in cursor.fetchall():
        action_ids[function_name] = action_id
    
    # Insert action parameters based on AI service requirements
    parameters_data = [
        # Video call parameters
        (action_ids['start_video_call'], 'contact_name', 'string', 'Family Member', 'Name of person to call', 1, None),
        (action_ids['start_video_call'], 'phone_number', 'string', '+6011468550', 'WhatsApp phone number', 1, '^\\+[1-9]\\d{10,14}$'),
        
        # Contact family parameters
        (action_ids['contact_family'], 'contact_name', 'string', 'Sarah', 'Name of family member', 1, None),
        (action_ids['contact_family'], 'phone_number', 'string', '+6011468550', 'Contact phone number', 1, '^\\+[1-9]\\d{10,14}$'),
        (action_ids['contact_family'], 'message', 'string', None, 'Optional message to send', 0, None),
        
        # Emergency parameters
        (action_ids['call_emergency'], 'reason', 'string', 'General emergency', 'Reason for emergency call', 0, None),
        (action_ids['call_emergency'], 'location', 'string', 'Home', 'Location of emergency', 0, None),
        
        # Arduino LED control parameters (based on script.ino)
        (action_ids['control_arduino_led'], 'led_state', 'string', 'ON', 'LED state: ON or OFF', 1, '^(ON|OFF)$'),
        (action_ids['control_arduino_led'], 'device_pin', 'integer', '8', 'Arduino pin number for LED', 0, None),
        
        # Temperature monitoring parameters
        (action_ids['read_arduino_sensors'], 'sensor_type', 'string', 'DHT11', 'Type of sensor to read', 0, None),
        (action_ids['set_target_temperature'], 'target_temperature', 'integer', '22', 'Target temperature in Celsius', 1, '^[1-3][0-9]$'),
        (action_ids['set_target_temperature'], 'target_humidity', 'integer', '50', 'Target humidity percentage', 0, '^[0-9]{1,2}$'),
        
        # Smart device parameters
        (action_ids['control_smart_device'], 'device_name', 'string', None, 'Name of device to control', 1, None),
        (action_ids['control_smart_device'], 'action_name', 'string', None, 'Action to perform on device', 1, None),
        (action_ids['control_smart_device'], 'device_category', 'string', None, 'Category of device (lighting, climate, etc.)', 0, None),
        (action_ids['control_smart_device'], 'room', 'string', None, 'Room where device is located', 0, None),
        (action_ids['control_smart_device'], 'mqtt_topic', 'string', None, 'MQTT topic for device control', 0, None),
        (action_ids['control_smart_device'], 'mqtt_payload', 'json', None, 'MQTT payload for device control', 0, None),
        
        # Health parameters
        (action_ids['send_health_alert'], 'severity', 'string', 'medium', 'Severity level of health concern', 0, '^(low|medium|high)$'),
        (action_ids['send_health_alert'], 'symptoms', 'string', None, 'Description of symptoms', 0, None),
        (action_ids['schedule_medication_reminder'], 'medication_name', 'string', None, 'Name of medication', 1, None),
        (action_ids['schedule_medication_reminder'], 'reminder_time', 'string', None, 'Time for medication reminder', 1, None),
    ]
    
    cursor.executemany('''
        INSERT INTO action_parameters (action_id, parameter_name, parameter_type, default_value, 
                                     description, is_required, validation_rule)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', parameters_data)
    
    conn.commit()
    conn.close()
    
    print(f"Enhanced intent actions database initialized successfully at: {db_path}")
    print(f"Intents created: {len(intents_data)}")
    print(f"Keywords created: {len(keywords_data)}")
    print(f"Actions created: {len(actions_data)}")
    print(f"Parameters created: {len(parameters_data)}")
    print("\nArduino-compatible actions:")
    for action in actions_data:
        if action[8]:  # arduino_compatible = 1
            print(f"  - {action[1]} -> MQTT: {action[6]} -> Payload: {action[7]}")

if __name__ == "__main__":
    init_intent_actions_database()