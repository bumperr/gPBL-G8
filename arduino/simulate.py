import paho.mqtt.client as mqtt
import time
import random
import json

# --- MQTT broker ---
BROKER = "localhost"
PORT = 1883
CLIENT_ID = "Arduino_Simulator"

class ArduinoSimulator:
    def __init__(self):
        # LED states for all rooms
        self.led_status = {
            "living_room": "OFF",
            "bedroom": "OFF",
            "kitchen": "OFF",
            "bathroom": "OFF"
        }
        
        # Sensor readings
        self.current_temp = 24.5
        self.current_humidity = 60.0
        self.target_temp = 22.0
        self.target_humidity = 50.0
        
        # MQTT client (updated API)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Arduino Simulator connected to MQTT broker")
            # Subscribe to LED command topics (exactly matching Arduino script.ino)
            client.subscribe("home/living_room/lights/cmd")
            client.subscribe("home/bedroom/lights/cmd") 
            client.subscribe("home/kitchen/lights/cmd")
            client.subscribe("home/bathroom/lights/cmd")
            
            # Subscribe to thermostat/room data from frontend (matching Arduino)
            client.subscribe("home/room/data")
            
            print("Subscribed to all Arduino topics")
            
            # Publish initial status for all rooms
            for room in self.led_status.keys():
                client.publish(f"home/{room}/lights/status", self.led_status[room])
                print(f"Initial {room} status: {self.led_status[room]}")
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"Received {topic}: {payload}")

        # Handle LED commands for each room (matching Arduino behavior)
        for room in self.led_status.keys():
            if topic == f"home/{room}/lights/cmd":
                if payload in ["ON", "OFF"]:
                    self.led_status[room] = payload
                    # Immediately publish status feedback (like Arduino would)
                    client.publish(f"home/{room}/lights/status", payload)
                    print(f"LED {room} -> {payload}")
        
        # Handle target temperature/humidity from UI (matching Arduino)
        if topic == "home/room/data":
            try:
                # Expected format: "25.5,60.2" (temperature,humidity)
                if ',' in payload:
                    temp_str, humid_str = payload.split(',')
                    self.target_temp = float(temp_str.strip())
                    self.target_humidity = float(humid_str.strip())
                    print(f"Target updated: {self.target_temp}C, {self.target_humidity}%")
                else:
                    print(f"Invalid room data format: {payload}")
            except ValueError as e:
                print(f"Error parsing room data: {e}")
    
    def update_sensor_readings(self):
        """Update sensor readings to trend toward targets"""
        # Slowly adjust current temp toward target (simulating heating/cooling)
        temp_diff = self.target_temp - self.current_temp
        if abs(temp_diff) > 0.1:
            self.current_temp += temp_diff * 0.1  # 10% adjustment per cycle
        
        # Add some natural variation
        self.current_temp += random.uniform(-0.2, 0.2)
        self.current_humidity += random.uniform(-1.0, 1.0)
        
        # Keep within reasonable bounds
        self.current_temp = max(18.0, min(35.0, self.current_temp))
        self.current_humidity = max(30.0, min(80.0, self.current_humidity))
    
    def run(self):
        """Start the Arduino simulator"""
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()

        try:
            last_sensor_publish = 0
            last_status_update = 0
            
            print("\nArduino Simulator running...")
            print("LED Controls: Send ON/OFF to home/{room}/lights/cmd")
            print("Thermostat: Send 'temp,humidity' to home/room/data")
            print("DHT11 sensor data published every 5 seconds")
            print("Press Ctrl+C to stop\n")
            
            while True:
                now = time.time()

                # Publish realistic DHT11 sensor data every 5 seconds
                if now - last_sensor_publish > 5:
                    self.update_sensor_readings()
                    
                    # Format like Arduino: "temperature,humidity"
                    payload = f"{self.current_temp:.1f},{self.current_humidity:.1f}"
                    self.client.publish("home/dht11", payload)
                    print(f"DHT11: {payload} (Target: {self.target_temp:.1f}C)")
                    last_sensor_publish = now

                # Publish LED status updates periodically (every 15 seconds) to keep UI in sync
                if now - last_status_update > 15:
                    for room, status in self.led_status.items():
                        self.client.publish(f"home/{room}/lights/status", status)
                    print(f"Status sync: {self.led_status}")
                    last_status_update = now

                time.sleep(0.5)  # More responsive to commands

        except KeyboardInterrupt:
            print("\nStopping Arduino simulator...")
            
            # Publish "disconnected" status for all devices
            for room in self.led_status.keys():
                self.client.publish(f"home/{room}/lights/status", "OFFLINE")
            
            self.client.loop_stop()
            self.client.disconnect()
            print("Arduino simulator stopped")

if __name__ == "__main__":
    simulator = ArduinoSimulator()
    simulator.run()