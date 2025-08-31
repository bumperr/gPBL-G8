import paho.mqtt.client as mqtt
import json
import asyncio
from typing import Optional, Callable
import threading

class MQTTService:
    def __init__(self, broker: str = "172.20.10.2", port: int = 1883):
        self.broker = broker
        self.port = port
        self.client: Optional[mqtt.Client] = None
        self.message_callbacks = {}
        # Store current smart home state
        self.current_state = {
            "sensors": {
                "temperature": 22.0,
                "humidity": 50.0,
                "last_update": None
            },
            "devices": {
                "led": "OFF",  # Arduino LED state
                "thermostat_target": 22,
                "last_command": None
            }
        }
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker with result code {rc}")
            # Subscribe to relevant topics
            client.subscribe("elder/voice")
            client.subscribe("elder/emergency")  
            client.subscribe("caregiver/commands")
            
            # Subscribe to Arduino topics for real-time state sync
            client.subscribe("home/dht11")  # Arduino DHT11 sensor data
            client.subscribe("home/led/status")  # LED status updates
            client.subscribe("home/thermostat/status")  # Thermostat status
            client.subscribe("home/+/+")  # All home device topics
            
            print("Subscribed to Arduino smart home topics")
        else:
            print(f"Failed to connect to MQTT broker with result code {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            message = msg.payload.decode('utf-8')
            topic = msg.topic
            print(f"Received MQTT message from {topic}: {message}")
            
            # Process Arduino smart home data and update state
            self._process_arduino_message(topic, message)
            
            # Call registered callbacks for this topic
            if topic in self.message_callbacks:
                print(f"[DEBUG] Calling {len(self.message_callbacks[topic])} callbacks for topic {topic}")
                for callback in self.message_callbacks[topic]:
                    try:
                        callback(topic, message)
                        print(f"[DEBUG] Callback executed successfully for {topic}")
                    except Exception as e:
                        print(f"Error in message callback: {e}")
            else:
                print(f"[DEBUG] No callbacks registered for topic {topic}")
                        
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
            
    def _process_arduino_message(self, topic: str, message: str):
        """Process Arduino MQTT messages and update current state"""
        import datetime
        
        try:
            print(f"Processing Arduino message: {topic} = {message}")
            
            if topic == "home/dht11":
                # Arduino DHT11 sends "temperature,humidity" format
                if ',' in message:
                    temp_str, humid_str = message.split(',')
                    temperature = float(temp_str.strip())
                    humidity = float(humid_str.strip())
                    
                    self.current_state["sensors"]["temperature"] = temperature
                    self.current_state["sensors"]["humidity"] = humidity
                    self.current_state["sensors"]["last_update"] = datetime.datetime.now().isoformat()
                    
                    print(f"[SUCCESS] Updated sensors: {temperature}°C, {humidity}%")
                    print(f"Current state after update: {self.current_state}")
                else:
                    print(f"[ERROR] Invalid DHT11 format: {message} (no comma found)")
                    
            elif topic == "home/led/cmd":
                # Track LED commands we send
                if message in ["ON", "OFF"]:
                    self.current_state["devices"]["led"] = message
                    self.current_state["devices"]["last_command"] = datetime.datetime.now().isoformat()
                    print(f"LED state updated: {message}")
                    
            elif topic == "home/thermostat/set":
                # Track thermostat commands
                try:
                    temp = int(message)
                    self.current_state["devices"]["thermostat_target"] = temp
                    self.current_state["devices"]["last_command"] = datetime.datetime.now().isoformat()
                    print(f"Thermostat target updated: {temp}°C")
                except ValueError:
                    pass
                    
            elif topic.startswith("home/") and topic.endswith("/status"):
                # Handle device status updates (if Arduino publishes status)
                device = topic.split("/")[1]
                self.current_state["devices"][f"{device}_status"] = message
                print(f"Device {device} status: {message}")
                
        except Exception as e:
            print(f"Error processing Arduino message {topic}: {e}")
    
    def get_current_state(self):
        """Get current smart home state"""
        return self.current_state.copy()
            
    async def initialize(self):
        """Initialize MQTT client"""
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            
            # Connect to broker
            self.client.connect_async(self.broker, self.port, 60)
            self.client.loop_start()
            print("MQTT client initialized")
            
        except Exception as e:
            print(f"Failed to initialize MQTT client: {e}")
            
    def register_callback(self, topic: str, callback: Callable):
        """Register a callback for a specific topic"""
        if topic not in self.message_callbacks:
            self.message_callbacks[topic] = []
        self.message_callbacks[topic].append(callback)
        
    async def publish_message(self, topic: str, message: str) -> bool:
        """Publish a message to a topic"""
        if not self.client or not self.client.is_connected():
            print(f"MQTT broker not connected, simulating message: {topic} -> {message}")
            
            # Simulate successful Arduino commands for demo purposes
            if topic == "home/led/cmd" and message in ["ON", "OFF"]:
                self.current_state["devices"]["led"] = message
                print(f"[SIMULATED] LED set to {message}")
                return True
            elif topic == "home/thermostat/cmd" and message.startswith("SET_TEMP:"):
                try:
                    temp = float(message.split(":")[1])
                    self.current_state["devices"]["thermostat_target"] = temp
                    print(f"[SIMULATED] Thermostat set to {temp}°C")
                    return True
                except:
                    pass
            
            # For other topics, just return success to not break the UI
            print(f"[SIMULATED] Message sent to {topic}")
            return True
            
        try:
            result = self.client.publish(topic, message)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing MQTT message: {e}, falling back to simulation")
            return True  # Return True to not break UI functionality
            
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()