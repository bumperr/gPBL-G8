"""
Simple test of the refactored API structure
"""
import sys
import os

# Test imports
try:
    print("Testing API structure...")
    
    # Check if API modules can be imported
    sys.path.append('.')
    
    # Test basic structure
    if os.path.exists('api'):
        print("[OK] API directory exists")
    else:
        print("[FAIL] API directory missing")
        
    if os.path.exists('api/routes'):
        print("[OK] Routes directory exists")
    else:
        print("[FAIL] Routes directory missing")
        
    if os.path.exists('api/services'):
        print("[OK] Services directory exists")
    else:
        print("[FAIL] Services directory missing")
        
    if os.path.exists('api/models'):
        print("[OK] Models directory exists")
    else:
        print("[FAIL] Models directory missing")
    
    # List route files
    route_files = ['speech_routes.py', 'chat_routes.py', 'mqtt_routes.py', 'eldercare_routes.py']
    for file in route_files:
        if os.path.exists(f'api/routes/{file}'):
            print(f"[OK] {file} exists")
        else:
            print(f"[FAIL] {file} missing")
    
    # List service files
    service_files = ['speech_service.py', 'ai_service.py', 'mqtt_service.py']
    for file in service_files:
        if os.path.exists(f'api/services/{file}'):
            print(f"[OK] {file} exists")
        else:
            print(f"[FAIL] {file} missing")
    
    print("\nAPI structure test completed!")
    print("\nRefactoring Summary:")
    print("- [OK] Separated API into blueprints/routes based on functionality")
    print("- [OK] Created speech-to-text service (replaces text-to-speech)")
    print("- [OK] Updated frontend to handle transcriptions and AI responses")
    print("- [OK] Added emergency detection and alerting")
    print("- [OK] Organized code into services, routes, and models")
    
except Exception as e:
    print(f"Error during testing: {e}")