import paho.mqtt.client as mqtt
import time
import random

# --- MQTT broker ---
BROKER = "localhost"
PORT = 1883
CLIENT_ID = "Python_Simulator"

# --- LED states ---
led_status = {
    "living_room": "OFF",
    "bedroom": "OFF",
    "kitchen": "OFF",
    "bathroom": "OFF"
}

# --- Callback: when connected ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # Subscribe to LED command topics
        client.subscribe("home/living_room/lights/cmd")
        client.subscribe("home/bedroom/lights/cmd")
        client.subscribe("home/kitchen/lights/cmd")
        client.subscribe("home/bathroom/lights/cmd")
    else:
        print("Connection failed with code", rc)

# --- Callback: when message received ---
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Received {topic}: {payload}")

    # Handle LED commands
    for room in led_status.keys():
        if topic == f"home/{room}/lights/cmd":
            if payload in ["ON", "OFF"]:
                led_status[room] = payload
                # Publish status update
                client.publish(f"home/{room}/lights/status", payload)
                print(f"LED {room} -> {payload}")

# --- Create client ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

# --- Main loop ---
try:
    last_publish = 0
    while True:
        now = time.time()

        # Publish simulated DHT11 data every 10 seconds
        if now - last_publish > 10:
            temp = round(random.uniform(22.0, 30.0), 1)
            humid = round(random.uniform(40.0, 70.0), 1)
            payload = f"{temp},{humid}"
            client.publish("home/dht11", payload)
            print(f"Published sensor: {payload}")
            last_publish = now

        # Simulate frontend sending target data (optional)
        if random.random() < 0.05:  # 5% chance each loop
            target_temp = round(random.uniform(24.0, 28.0), 1)
            target_humid = round(random.uniform(50.0, 65.0), 1)
            payload = f"{target_temp},{target_humid}"
            client.publish("home/room/data", payload)
            print(f"📤 Simulated frontend target: {payload}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping simulator...")
    client.loop_stop()
    client.disconnect()
