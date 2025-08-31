import sqlite3
import os

def init_database():
    """Initialize the MQTT devices database with schema and sample data"""
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(__file__)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, 'devices.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            room TEXT,
            mqtt_topic TEXT NOT NULL,
            device_type TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create device_actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            action_name TEXT NOT NULL,
            action_command TEXT NOT NULL,
            mqtt_payload TEXT,
            description TEXT,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Create device_keywords table for AI intent detection
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            keyword TEXT NOT NULL,
            context TEXT,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Clear existing data for fresh start
    cursor.execute('DELETE FROM device_keywords')
    cursor.execute('DELETE FROM device_actions')
    cursor.execute('DELETE FROM devices')
    
    # Insert sample devices
    devices_data = [
        # Living Room Devices
        ('Living Room Lights', 'lighting', 'living_room', 'home/living_room/lights', 'led_strip', 'Smart LED strip lighting for living room', 1),
        ('Living Room TV', 'entertainment', 'living_room', 'home/living_room/tv', 'smart_tv', 'Smart TV with streaming capabilities', 1),
        ('Living Room AC', 'climate', 'living_room', 'home/living_room/ac', 'air_conditioner', 'Air conditioning unit', 1),
        
        # Bedroom Devices  
        ('Bedroom Lights', 'lighting', 'bedroom', 'home/bedroom/lights', 'led_bulb', 'Smart LED bulbs for bedroom', 1),
        ('Bedroom Fan', 'climate', 'bedroom', 'home/bedroom/fan', 'ceiling_fan', 'Ceiling fan with speed control', 1),
        
        # Kitchen Devices
        ('Kitchen Lights', 'lighting', 'kitchen', 'home/kitchen/lights', 'led_panel', 'LED panel lighting for kitchen', 1),
        ('Kitchen Exhaust', 'ventilation', 'kitchen', 'home/kitchen/exhaust', 'exhaust_fan', 'Kitchen exhaust fan', 1),
        
        # General Home Systems
        ('Main Thermostat', 'climate', 'general', 'home/thermostat', 'thermostat', 'Main house thermostat', 1),
        ('Security System', 'security', 'general', 'home/security', 'alarm_system', 'Home security alarm system', 1),
        ('Front Door Lock', 'security', 'general', 'home/door/front', 'smart_lock', 'Smart lock for front door', 1),
    ]
    
    cursor.executemany('''
        INSERT INTO devices (name, category, room, mqtt_topic, device_type, description, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', devices_data)
    
    # Get device IDs for actions
    device_ids = {}
    cursor.execute('SELECT id, name FROM devices')
    for device_id, name in cursor.fetchall():
        device_ids[name] = device_id
    
    # Insert device actions
    actions_data = [
        # Lighting actions
        (device_ids['Living Room Lights'], 'turn_on', 'power_on', 'ON', 'Turn on the lights'),
        (device_ids['Living Room Lights'], 'turn_off', 'power_off', 'OFF', 'Turn off the lights'),
        (device_ids['Living Room Lights'], 'dim', 'set_brightness', '30', 'Dim the lights to 30%'),
        (device_ids['Living Room Lights'], 'brighten', 'set_brightness', '80', 'Brighten the lights to 80%'),
        
        (device_ids['Bedroom Lights'], 'turn_on', 'power_on', 'ON', 'Turn on bedroom lights'),
        (device_ids['Bedroom Lights'], 'turn_off', 'power_off', 'OFF', 'Turn off bedroom lights'),
        
        (device_ids['Kitchen Lights'], 'turn_on', 'power_on', 'ON', 'Turn on kitchen lights'),
        (device_ids['Kitchen Lights'], 'turn_off', 'power_off', 'OFF', 'Turn off kitchen lights'),
        
        # Climate control actions
        (device_ids['Main Thermostat'], 'set_temperature', 'set_temp', '22', 'Set temperature to specific value'),
        (device_ids['Main Thermostat'], 'increase_temp', 'temp_up', '+2', 'Increase temperature by 2 degrees'),
        (device_ids['Main Thermostat'], 'decrease_temp', 'temp_down', '-2', 'Decrease temperature by 2 degrees'),
        
        (device_ids['Living Room AC'], 'turn_on', 'power_on', 'ON', 'Turn on air conditioner'),
        (device_ids['Living Room AC'], 'turn_off', 'power_off', 'OFF', 'Turn off air conditioner'),
        (device_ids['Living Room AC'], 'set_cool', 'set_mode', 'COOL', 'Set AC to cooling mode'),
        
        (device_ids['Bedroom Fan'], 'turn_on', 'power_on', 'ON', 'Turn on bedroom fan'),
        (device_ids['Bedroom Fan'], 'turn_off', 'power_off', 'OFF', 'Turn off bedroom fan'),
        (device_ids['Bedroom Fan'], 'set_speed', 'fan_speed', 'MEDIUM', 'Set fan to medium speed'),
        
        # Entertainment actions
        (device_ids['Living Room TV'], 'turn_on', 'power_on', 'ON', 'Turn on TV'),
        (device_ids['Living Room TV'], 'turn_off', 'power_off', 'OFF', 'Turn off TV'),
        (device_ids['Living Room TV'], 'volume_up', 'vol_up', '+5', 'Increase volume'),
        (device_ids['Living Room TV'], 'volume_down', 'vol_down', '-5', 'Decrease volume'),
        
        # Security actions
        (device_ids['Security System'], 'arm', 'system_arm', 'ARM', 'Arm the security system'),
        (device_ids['Security System'], 'disarm', 'system_disarm', 'DISARM', 'Disarm the security system'),
        
        (device_ids['Front Door Lock'], 'lock', 'door_lock', 'LOCK', 'Lock the front door'),
        (device_ids['Front Door Lock'], 'unlock', 'door_unlock', 'UNLOCK', 'Unlock the front door'),
        
        # Other devices
        (device_ids['Kitchen Exhaust'], 'turn_on', 'power_on', 'ON', 'Turn on kitchen exhaust fan'),
        (device_ids['Kitchen Exhaust'], 'turn_off', 'power_off', 'OFF', 'Turn off kitchen exhaust fan'),
    ]
    
    cursor.executemany('''
        INSERT INTO device_actions (device_id, action_name, action_command, mqtt_payload, description)
        VALUES (?, ?, ?, ?, ?)
    ''', actions_data)
    
    # Insert keywords for AI intent detection
    keywords_data = [
        # Lighting keywords
        (device_ids['Living Room Lights'], 'living room lights', 'lighting'),
        (device_ids['Living Room Lights'], 'living room light', 'lighting'),
        (device_ids['Living Room Lights'], 'lounge lights', 'lighting'),
        (device_ids['Bedroom Lights'], 'bedroom lights', 'lighting'),
        (device_ids['Bedroom Lights'], 'bedroom light', 'lighting'),
        (device_ids['Kitchen Lights'], 'kitchen lights', 'lighting'),
        (device_ids['Kitchen Lights'], 'kitchen light', 'lighting'),
        
        # General lighting keywords
        (device_ids['Living Room Lights'], 'lights', 'general_lighting'),
        (device_ids['Living Room Lights'], 'light', 'general_lighting'),
        (device_ids['Living Room Lights'], 'lamp', 'general_lighting'),
        
        # Climate keywords
        (device_ids['Main Thermostat'], 'temperature', 'climate'),
        (device_ids['Main Thermostat'], 'thermostat', 'climate'),
        (device_ids['Main Thermostat'], 'heating', 'climate'),
        (device_ids['Main Thermostat'], 'cooling', 'climate'),
        (device_ids['Living Room AC'], 'air conditioner', 'climate'),
        (device_ids['Living Room AC'], 'ac', 'climate'),
        (device_ids['Living Room AC'], 'air con', 'climate'),
        (device_ids['Bedroom Fan'], 'fan', 'climate'),
        (device_ids['Bedroom Fan'], 'bedroom fan', 'climate'),
        
        # Entertainment keywords
        (device_ids['Living Room TV'], 'tv', 'entertainment'),
        (device_ids['Living Room TV'], 'television', 'entertainment'),
        (device_ids['Living Room TV'], 'living room tv', 'entertainment'),
        
        # Security keywords
        (device_ids['Security System'], 'security', 'security'),
        (device_ids['Security System'], 'alarm', 'security'),
        (device_ids['Security System'], 'security system', 'security'),
        (device_ids['Front Door Lock'], 'door', 'security'),
        (device_ids['Front Door Lock'], 'front door', 'security'),
        (device_ids['Front Door Lock'], 'door lock', 'security'),
        
        # Kitchen keywords
        (device_ids['Kitchen Exhaust'], 'exhaust', 'ventilation'),
        (device_ids['Kitchen Exhaust'], 'kitchen fan', 'ventilation'),
        (device_ids['Kitchen Exhaust'], 'exhaust fan', 'ventilation'),
    ]
    
    cursor.executemany('''
        INSERT INTO device_keywords (device_id, keyword, context)
        VALUES (?, ?, ?)
    ''', keywords_data)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at: {db_path}")
    print(f"Devices created: {len(devices_data)}")
    print(f"Actions created: {len(actions_data)}")
    print(f"Keywords created: {len(keywords_data)}")

if __name__ == "__main__":
    init_database()