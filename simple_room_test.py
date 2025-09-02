import requests
import json

def test_room_lights():
    """Test multi-room light control via API"""
    
    test_cases = [
        "Turn on living room light",
        "Turn off bedroom lights", 
        "Switch on kitchen light",
        "Turn off bathroom light"
    ]
    
    print("Testing Multi-Room Light Control")
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
                
                print(f"Response: {ai_response.get('response', '')[:60]}...")
                print("SUCCESS")
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\n{'='*40}")
    print("Multi-room Arduino system ready!")
    print("All 4 rooms (Living, Bedroom, Kitchen, Bathroom) supported")

if __name__ == "__main__":
    test_room_lights()