#!/usr/bin/env python3
"""
Test subtlety detection - dark room and house cold scenarios
"""
import requests
import json

def test_subtlety_detection():
    """Test enhanced subtlety detection via API"""
    
    test_cases = [
        # Dark room detection
        "The room is dark",
        "It's getting dark in the bedroom", 
        "Too dark in here, can't see",
        "I need some light in the kitchen",
        
        # House cold detection
        "The house is cold",
        "House feels cold today",
        "I'm feeling cold",
        "Too cold in here"
    ]
    
    print("Testing Enhanced Subtlety Detection")
    print("=" * 40)
    
    for message in test_cases:
        print(f"\nTesting: '{message}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/eldercare/text-assistance",
                json={
                    "message": message,
                    "elder_info": {"name": "Test User", "age": 75}
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                print(f"Intent: {ai_response.get('intent_detected', 'None')}")
                print(f"Action: {ai_response.get('suggested_action', {}).get('function_name', 'None')}")
                
                # Check for MQTT commands
                mqtt_commands = data.get('mqtt_commands', [])
                if mqtt_commands:
                    for cmd in mqtt_commands:
                        print(f"MQTT Topic: {cmd.get('topic', 'N/A')}")
                        print(f"MQTT Payload: {cmd.get('payload', {})}")
                
                # Check for environmental reasoning
                if ai_response.get('environmental_reasoning'):
                    print("Environmental Reasoning: DETECTED ✅")
                
                print(f"Response: {ai_response.get('response', '')[:80]}...")
                print("SUCCESS")
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\n{'='*40}")
    print("Subtlety detection test complete!")

if __name__ == "__main__":
    test_subtlety_detection()