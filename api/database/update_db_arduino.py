import sqlite3
import os

def update_database_for_arduino():
    """Update the database to match the actual Arduino setup"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'devices.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM device_keywords')
    cursor.execute('DELETE FROM device_actions')
    cursor.execute('DELETE FROM devices')
    
    # Insert actual Arduino devices
    devices_data = [
        # LED on Arduino - pin 8, controlled via home/led/cmd
        ('LED Light', 'lighting', 'general', 'home/led/cmd', 'led', 'Main LED light controlled by Arduino', 1),
        
        # DHT11 sensor - pin 3, publishes to home/dht11 (read-only)
        ('Temperature Sensor', 'sensor', 'general', 'home/dht11', 'dht11', 'DHT11 temperature and humidity sensor', 1),
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
    
    # Insert device actions based on Arduino code
    actions_data = [
        # LED actions (from Arduino code: if message == "ON"/"OFF")
        (device_ids['LED Light'], 'turn_on', 'power_on', 'ON', 'Turn on the LED light'),
        (device_ids['LED Light'], 'turn_off', 'power_off', 'OFF', 'Turn off the LED light'),
        
        # DHT11 sensor actions (read-only)
        (device_ids['Temperature Sensor'], 'read_temperature', 'read_temp', '', 'Read current temperature and humidity'),
    ]
    
    cursor.executemany('''
        INSERT INTO device_actions (device_id, action_name, action_command, mqtt_payload, description)
        VALUES (?, ?, ?, ?, ?)
    ''', actions_data)
    
    # Insert keywords for AI intent detection - simplified and focused
    keywords_data = [
        # LED keywords
        (device_ids['LED Light'], 'light', 'lighting'),
        (device_ids['LED Light'], 'lights', 'lighting'),
        (device_ids['LED Light'], 'led', 'lighting'),
        (device_ids['LED Light'], 'lamp', 'lighting'),
        (device_ids['LED Light'], 'lighting', 'lighting'),
        
        # Temperature sensor keywords  
        (device_ids['Temperature Sensor'], 'temperature', 'sensor'),
        (device_ids['Temperature Sensor'], 'temp', 'sensor'),
        (device_ids['Temperature Sensor'], 'humidity', 'sensor'),
        (device_ids['Temperature Sensor'], 'sensor', 'sensor'),
        (device_ids['Temperature Sensor'], 'weather', 'sensor'),
    ]
    
    cursor.executemany('''
        INSERT INTO device_keywords (device_id, keyword, context)
        VALUES (?, ?, ?)
    ''', keywords_data)
    
    conn.commit()
    conn.close()
    
    print(f"Database updated for Arduino setup:")
    print(f"Devices created: {len(devices_data)}")
    print(f"Actions created: {len(actions_data)}")
    print(f"Keywords created: {len(keywords_data)}")
    print("\nDevices:")
    for device in devices_data:
        print(f"- {device[0]}: {device[2]} -> {device[3]}")

if __name__ == "__main__":
    update_database_for_arduino()