import paho.mqtt.client as mqtt
import json
import asyncio
from typing import Optional, Callable
import threading

class MQTTService:
    def __init__(self, broker: str = "localhost", port: int = 1883):
        self.broker = broker
        self.port = port
        self.client: Optional[mqtt.Client] = None
        self.message_callbacks = {}
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker with result code {rc}")
            # Subscribe to relevant topics
            client.subscribe("elder/voice")
            client.subscribe("elder/emergency")
            client.subscribe("caregiver/commands")
        else:
            print(f"Failed to connect to MQTT broker with result code {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            message = msg.payload.decode('utf-8')
            topic = msg.topic
            print(f"Received MQTT message from {topic}: {message}")
            
            # Call registered callbacks for this topic
            if topic in self.message_callbacks:
                for callback in self.message_callbacks[topic]:
                    try:
                        callback(topic, message)
                    except Exception as e:
                        print(f"Error in message callback: {e}")
                        
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
            
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
        if not self.client:
            raise Exception("MQTT client not initialized")
            
        try:
            result = self.client.publish(topic, message)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing MQTT message: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()