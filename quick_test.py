#!/usr/bin/env python3
import requests
import json

# Test both text and voice for dark room
test_cases = [
    ("Text", "the room is dark"),
    ("Text", "it's getting dark in here"),
    ("Text", "I need some light"),
]

for chat_type, message in test_cases:
    try:
        print(f"\n=== Testing {chat_type}: '{message}' ===")
        
        response = requests.post(
            "http://localhost:8000/eldercare/text-assistance",
            json={
                "message": message,
                "elder_info": {"name": "Test", "age": 75}
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_resp = data.get('ai_response', {})
            print("✅ SUCCESS")
            print(f"Intent: {ai_resp.get('intent_detected', 'None')}")
            print(f"Emergency: {ai_resp.get('is_emergency', False)}")  
            print(f"Action: {ai_resp.get('suggested_action', {}).get('function_name', 'None')}")
            if data.get('mqtt_commands'):
                print(f"MQTT: {len(data.get('mqtt_commands'))} commands")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")