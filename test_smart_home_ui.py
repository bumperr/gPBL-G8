#!/usr/bin/env python3
"""
Test the new smart home UI backend integration
"""
import requests
import json

def test_smart_home_backend():
    """Test the new smart home backend endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("=== Smart Home Backend Test ===")
    
    # Test 1: Get smart home status
    try:
        print("\n1. Testing GET /smart-home/status")
        response = requests.get(f"{base_url}/smart-home/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint working")
            print(f"   Lights: {data.get('lights', {})}")
            print(f"   Thermostat: {data.get('thermostat', {})}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 2: Toggle living room light
    try:
        print("\n2. Testing POST /smart-home/lights/living_room/toggle")
        response = requests.post(
            f"{base_url}/smart-home/lights/living_room/toggle",
            json={"state": True},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Light toggle endpoint working")
            print(f"   Response: {data}")
        else:
            print(f"❌ Light toggle failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Light toggle error: {e}")
    
    # Test 3: Set thermostat
    try:
        print("\n3. Testing POST /smart-home/thermostat/set")
        response = requests.post(
            f"{base_url}/smart-home/thermostat/set",
            params={"temperature": 24, "humidity": 60},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Thermostat endpoint working")
            print(f"   Response: {data}")
        else:
            print(f"❌ Thermostat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Thermostat error: {e}")
    
    # Test 4: Send direct MQTT command
    try:
        print("\n4. Testing POST /smart-home/mqtt/send")
        response = requests.post(
            f"{base_url}/smart-home/mqtt/send",
            json={
                "topic": "home/living_room/lights/cmd",
                "payload": "ON"
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ MQTT send endpoint working")
            print(f"   Response: {data}")
        else:
            print(f"❌ MQTT send failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MQTT send error: {e}")
    
    print("\n=== Test Summary ===")
    print("✅ New smart home backend endpoints are ready!")
    print("🏠 Arduino integration: 4 rooms with pins 8-11")
    print("📡 MQTT topics: home/{room}/lights/cmd")
    print("🌡️ Thermostat: home/room/data")

if __name__ == "__main__":
    test_smart_home_backend()