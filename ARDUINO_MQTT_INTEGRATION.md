# Arduino R4 WiFi MQTT Integration for Elder Care System

## Overview

This guide demonstrates how to integrate Arduino R4 WiFi with the Elder Care Assistant's MQTT system to receive commands and control IoT devices based on elder interactions from the UI.

Hướng dẫn này trình bày cách tích hợp Arduino R4 WiFi với hệ thống MQTT của Trợ lý Chăm sóc Người cao tuổi để nhận lệnh và điều khiển các thiết bị IoT dựa trên tương tác của người cao tuổi từ giao diện người dùng.

Japanese (日本語):
このガイドでは、Arduino R4 WiFi を高齢者ケアアシスタントの MQTT システムと統合し、ユーザーインターフェースからの高齢者の操作に基づいてコマンドを受信し、IoT デバイスを制御する方法を説明します。

## Prerequisites

### Hardware
- **Arduino UNO R4 WiFi** - Main microcontroller
- **Smart Home Devices**: LEDs, servos, sensors, relays, etc.
- **WiFi Network**: 2.4GHz network for Arduino connectivity

### Software Libraries
```cpp
#include <WiFiS3.h>           // WiFi connectivity for R4
#include <ArduinoMqttClient.h> // MQTT client library
#include <ArduinoJson.h>       // JSON parsing library
#include <Servo.h>             // For servo control (door locks, etc.)
```

### Arduino IDE Setup
```bash
# Install required libraries via Library Manager:
1. ArduinoMqttClient by Arduino
2. ArduinoJson by Benoit Blanchon
3. WiFiS3 (built-in for R4)
```

## MQTT Topics Structure Reference

Based on the Elder Care UI, the Arduino will listen to these topics:

```
eldercare/commands/lights/{action}      # Light control
eldercare/commands/thermostat/{action}  # Temperature control  
eldercare/commands/locks/{action}       # Door/window locks
eldercare/commands/security/{action}    # Security system
eldercare/emergency/{severity}          # Emergency alerts
eldercare/health/{metric}              # Health monitoring
```

## Arduino Code Implementation

### 1. Basic Setup and Configuration

```cpp
#include <WiFiS3.h>
#include <ArduinoMqttClient.h>
#include <ArduinoJson.h>
#include <Servo.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT broker settings
const char* mqtt_broker = "192.168.1.100";  // Your MQTT broker IP
const int mqtt_port = 1883;
const char* mqtt_client_id = "arduino_eldercare";

// Hardware pin definitions
#define LED_LIVING_ROOM 2
#define LED_BEDROOM 3
#define LED_KITCHEN 4
#define SERVO_DOOR_LOCK 9
#define RELAY_THERMOSTAT 5
#define BUZZER_EMERGENCY 6
#define SENSOR_MOTION 7
#define STATUS_LED 13

// Objects
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
Servo doorLock;

// State variables
bool lightsState[3] = {false, false, false}; // living room, bedroom, kitchen
bool doorLocked = true;
int currentTemp = 22;
bool emergencyMode = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize hardware pins
  pinMode(LED_LIVING_ROOM, OUTPUT);
  pinMode(LED_BEDROOM, OUTPUT);
  pinMode(LED_KITCHEN, OUTPUT);
  pinMode(RELAY_THERMOSTAT, OUTPUT);
  pinMode(BUZZER_EMERGENCY, OUTPUT);
  pinMode(SENSOR_MOTION, INPUT);
  pinMode(STATUS_LED, OUTPUT);
  
  doorLock.attach(SERVO_DOOR_LOCK);
  doorLock.write(0); // Initial locked position
  
  // Connect to WiFi
  connectWiFi();
  
  // Connect to MQTT broker
  connectMQTT();
  
  // Subscribe to eldercare topics
  subscribeToTopics();
  
  Serial.println("Arduino Elder Care System Ready!");
  digitalWrite(STATUS_LED, HIGH);
}
```

### 2. WiFi and MQTT Connection Functions

```cpp
void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("Connected to WiFi! IP: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {
  Serial.print("Connecting to MQTT broker...");
  
  while (!mqttClient.connect(mqtt_broker, mqtt_port)) {
    Serial.print(".");
    delay(1000);
  }
  
  Serial.println();
  Serial.println("Connected to MQTT broker!");
}

void subscribeToTopics() {
  // Subscribe to smart home command topics
  mqttClient.subscribe("eldercare/commands/lights/+");
  mqttClient.subscribe("eldercare/commands/thermostat/+");
  mqttClient.subscribe("eldercare/commands/locks/+");
  mqttClient.subscribe("eldercare/commands/security/+");
  
  // Subscribe to emergency alerts
  mqttClient.subscribe("eldercare/emergency/+");
  
  // Subscribe to health monitoring
  mqttClient.subscribe("eldercare/health/+");
  
  Serial.println("Subscribed to eldercare topics");
}
```

### 3. MQTT Message Handler and JSON Parsing

```cpp
void loop() {
  // Maintain MQTT connection
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  
  mqttClient.poll();
  
  // Handle any other periodic tasks
  checkMotionSensor();
  updateStatusLED();
  
  delay(100);
}

void onMqttMessage(int messageSize) {
  String topic = mqttClient.messageTopic();
  String payload = "";
  
  // Read the payload
  while (mqttClient.available()) {
    payload += (char)mqttClient.read();
  }
  
  Serial.println("Received MQTT message:");
  Serial.println("Topic: " + topic);
  Serial.println("Payload: " + payload);
  
  // Parse and handle the message
  handleMqttMessage(topic, payload);
}

void handleMqttMessage(String topic, String payload) {
  // Parse JSON payload
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, payload);
  
  String elderName = doc["elder_name"] | "unknown";
  String deviceType = doc["device_type"] | "";
  String action = doc["action"] | "";
  String room = doc["room"] | "living_room";
  
  Serial.println("Parsed - Elder: " + elderName + ", Device: " + deviceType + ", Action: " + action);
  
  // Route to appropriate handler based on topic
  if (topic.startsWith("eldercare/commands/lights/")) {
    handleLightCommand(action, room, doc);
  }
  else if (topic.startsWith("eldercare/commands/thermostat/")) {
    handleThermostatCommand(action, doc);
  }
  else if (topic.startsWith("eldercare/commands/locks/")) {
    handleLockCommand(action, doc);
  }
  else if (topic.startsWith("eldercare/commands/security/")) {
    handleSecurityCommand(action, doc);
  }
  else if (topic.startsWith("eldercare/emergency/")) {
    handleEmergencyAlert(topic, doc);
  }
  else if (topic.startsWith("eldercare/health/")) {
    handleHealthMetric(topic, doc);
  }
  
  // Send confirmation response
  sendResponseToServer(topic, elderName, deviceType, action, "success");
}
```

### 4. Device-Specific Command Handlers

```cpp
// Light Control Handler
void handleLightCommand(String action, String room, DynamicJsonDocument& doc) {
  int pin = getLightPin(room);
  bool success = false;
  
  if (action == "turn_on") {
    digitalWrite(pin, HIGH);
    setLightState(room, true);
    success = true;
    Serial.println("Light turned ON in " + room);
    
    // Handle brightness if specified
    if (doc.containsKey("parameters") && doc["parameters"].containsKey("brightness")) {
      int brightness = doc["parameters"]["brightness"];
      analogWrite(pin, map(brightness, 0, 100, 0, 255));
      Serial.println("Brightness set to: " + String(brightness) + "%");
    }
  }
  else if (action == "turn_off") {
    digitalWrite(pin, LOW);
    setLightState(room, false);
    success = true;
    Serial.println("Light turned OFF in " + room);
  }
  
  if (success) {
    blinkStatusLED(2); // Confirm action
  }
}

// Thermostat Control Handler
void handleThermostatCommand(String action, DynamicJsonDocument& doc) {
  if (action == "set_temperature") {
    int targetTemp = doc["parameters"]["temperature"] | 22;
    
    // Simulate thermostat control with relay
    if (targetTemp > currentTemp) {
      digitalWrite(RELAY_THERMOSTAT, HIGH); // Heat ON
      Serial.println("Heating turned ON - Target: " + String(targetTemp) + "°C");
    } else {
      digitalWrite(RELAY_THERMOSTAT, LOW); // Heat OFF
      Serial.println("Heating turned OFF");
    }
    
    currentTemp = targetTemp; // Simulate temperature change
    blinkStatusLED(3);
  }
}

// Door Lock Control Handler
void handleLockCommand(String action, DynamicJsonDocument& doc) {
  if (action == "lock" && !doorLocked) {
    doorLock.write(0); // Locked position
    doorLocked = true;
    Serial.println("Door LOCKED");
    blinkStatusLED(1);
  }
  else if (action == "unlock" && doorLocked) {
    doorLock.write(90); // Unlocked position
    doorLocked = false;
    Serial.println("Door UNLOCKED");
    blinkStatusLED(4);
  }
}

// Security System Handler
void handleSecurityCommand(String action, DynamicJsonDocument& doc) {
  if (action == "arm") {
    // Enable motion sensor monitoring
    Serial.println("Security system ARMED");
    // Could enable more sensors, cameras, etc.
  }
  else if (action == "disarm") {
    Serial.println("Security system DISARMED");
  }
}

// Emergency Alert Handler
void handleEmergencyAlert(String topic, DynamicJsonDocument& doc) {
  String severity = doc["severity"] | "medium";
  String message = doc["message"] | "Emergency alert";
  String elderName = doc["elder_name"] | "Elder";
  
  Serial.println("🚨 EMERGENCY ALERT 🚨");
  Serial.println("Severity: " + severity);
  Serial.println("Elder: " + elderName);
  Serial.println("Message: " + message);
  
  if (severity == "critical" || severity == "high") {
    emergencyMode = true;
    
    // Turn on all lights
    digitalWrite(LED_LIVING_ROOM, HIGH);
    digitalWrite(LED_BEDROOM, HIGH);
    digitalWrite(LED_KITCHEN, HIGH);
    
    // Unlock doors for emergency access
    if (doorLocked) {
      doorLock.write(90);
      doorLocked = false;
    }
    
    // Sound emergency alarm
    for (int i = 0; i < 10; i++) {
      digitalWrite(BUZZER_EMERGENCY, HIGH);
      delay(200);
      digitalWrite(BUZZER_EMERGENCY, LOW);
      delay(200);
    }
    
    // Flash status LED rapidly
    for (int i = 0; i < 20; i++) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      delay(100);
    }
  }
}

// Health Monitoring Handler
void handleHealthMetric(String topic, DynamicJsonDocument& doc) {
  String metric = doc["metric_type"] | "";
  float value = doc["value"] | 0.0;
  String elderName = doc["elder_name"] | "Elder";
  
  Serial.println("Health Update - " + elderName + ": " + metric + " = " + String(value));
  
  // React to abnormal health readings
  if (metric == "heart_rate") {
    if (value > 100 || value < 60) {
      Serial.println("⚠️ Abnormal heart rate detected!");
      blinkStatusLED(5); // Health warning pattern
    }
  }
  else if (metric == "blood_pressure" && value > 140) {
    Serial.println("⚠️ High blood pressure detected!");
    blinkStatusLED(5);
  }
}
```

### 5. Helper Functions

```cpp
// Get appropriate LED pin for room
int getLightPin(String room) {
  if (room == "living_room") return LED_LIVING_ROOM;
  else if (room == "bedroom") return LED_BEDROOM;
  else if (room == "kitchen") return LED_KITCHEN;
  return LED_LIVING_ROOM; // Default
}

// Update light state tracking
void setLightState(String room, bool state) {
  if (room == "living_room") lightsState[0] = state;
  else if (room == "bedroom") lightsState[1] = state;
  else if (room == "kitchen") lightsState[2] = state;
}

// Status LED patterns for different actions
void blinkStatusLED(int pattern) {
  for (int i = 0; i < pattern; i++) {
    digitalWrite(STATUS_LED, LOW);
    delay(200);
    digitalWrite(STATUS_LED, HIGH);
    delay(200);
  }
}

// Motion sensor monitoring
void checkMotionSensor() {
  static unsigned long lastMotion = 0;
  
  if (digitalRead(SENSOR_MOTION) == HIGH) {
    if (millis() - lastMotion > 5000) { // 5 second debounce
      Serial.println("Motion detected!");
      
      // Send motion data to server
      sendMotionAlert();
      lastMotion = millis();
    }
  }
}

// Send motion alert to MQTT
void sendMotionAlert() {
  DynamicJsonDocument doc(512);
  doc["sensor_type"] = "motion";
  doc["location"] = "living_room";
  doc["timestamp"] = millis();
  doc["status"] = "motion_detected";
  
  String payload;
  serializeJson(doc, payload);
  
  mqttClient.beginMessage("eldercare/sensors/motion");
  mqttClient.print(payload);
  mqttClient.endMessage();
}

// Send response back to server
void sendResponseToServer(String originalTopic, String elderName, String deviceType, String action, String status) {
  DynamicJsonDocument response(512);
  response["status"] = status;
  response["elder_name"] = elderName;
  response["device_type"] = deviceType;
  response["action"] = action;
  response["timestamp"] = millis();
  response["executed"] = true;
  response["arduino_id"] = mqtt_client_id;
  
  String payload;
  serializeJson(response, payload);
  
  String responseTopic = "eldercare/responses/" + deviceType + "/" + elderName;
  
  mqttClient.beginMessage(responseTopic.c_str());
  mqttClient.print(payload);
  mqttClient.endMessage();
  
  Serial.println("Response sent to: " + responseTopic);
}

// MQTT reconnection handler
void reconnectMQTT() {
  Serial.print("Attempting MQTT reconnection...");
  
  while (!mqttClient.connect(mqtt_broker, mqtt_port)) {
    Serial.print(".");
    delay(1000);
  }
  
  Serial.println(" connected!");
  subscribeToTopics();
}

// Status LED update based on system state
void updateStatusLED() {
  if (emergencyMode) {
    // Fast blinking in emergency
    digitalWrite(STATUS_LED, (millis() / 250) % 2);
  } else if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) {
    // Slow blinking when disconnected
    digitalWrite(STATUS_LED, (millis() / 1000) % 2);
  } else {
    // Solid on when all good
    digitalWrite(STATUS_LED, HIGH);
  }
}
```

## Usage Examples from Elder UI

### 1. Voice Command: "Turn on the bedroom lights"
```json
Topic: eldercare/commands/lights/turn_on
Payload: {
  "elder_name": "john_doe",
  "device_type": "lights",
  "action": "turn_on",
  "parameters": {"brightness": 80},
  "room": "bedroom",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "ai_assistant"
}
```

**Arduino Response**: Turns on LED connected to pin 3, sends confirmation back.

### 2. Voice Command: "Lock the front door"
```json
Topic: eldercare/commands/locks/lock
Payload: {
  "elder_name": "jane_smith",
  "device_type": "locks",
  "action": "lock",
  "room": "front_door",
  "timestamp": "2024-01-15T10:35:00Z",
  "source": "ai_assistant"
}
```

**Arduino Response**: Servo rotates to locked position (0°), confirms action.

### 3. Emergency Alert: "I've fallen and can't get up"
```json
Topic: eldercare/emergency/high
Payload: {
  "elder_name": "bob_johnson",
  "message": "Fall detected in bathroom",
  "severity": "high",
  "location": "bathroom",
  "timestamp": "2024-01-15T10:40:00Z",
  "source": "ai_assistant",
  "requires_response": true
}
```

**Arduino Response**: 
- Turns on all lights
- Unlocks doors
- Sounds emergency buzzer
- Flashes status LED

## Wiring Diagram

```
Arduino R4 WiFi Pin Connections:
├── Digital Pin 2  → Living Room LED + 220Ω resistor → GND
├── Digital Pin 3  → Bedroom LED + 220Ω resistor → GND  
├── Digital Pin 4  → Kitchen LED + 220Ω resistor → GND
├── Digital Pin 5  → Relay Module (Thermostat Control)
├── Digital Pin 6  → Buzzer + 100Ω resistor → GND
├── Digital Pin 7  → PIR Motion Sensor Data Pin
├── Digital Pin 9  → Servo Motor Signal (Door Lock)
├── Digital Pin 13 → Status LED + 220Ω resistor → GND
├── 5V            → Servo Motor VCC, PIR Sensor VCC
└── GND           → Common Ground for all components
```

## Testing Commands

Use MQTT client or the Elder Care web interface:

```bash
# Test light control
mosquitto_pub -h localhost -t eldercare/commands/lights/turn_on \
  -m '{"elder_name":"test","device_type":"lights","action":"turn_on","room":"living_room"}'

# Test door lock
mosquitto_pub -h localhost -t eldercare/commands/locks/lock \
  -m '{"elder_name":"test","device_type":"locks","action":"lock"}'

# Test emergency alert
mosquitto_pub -h localhost -t eldercare/emergency/high \
  -m '{"elder_name":"test","message":"Emergency test","severity":"high"}'
```

## Troubleshooting

### Common Issues:
1. **WiFi Connection**: Check SSID/password and 2.4GHz network
2. **MQTT Connection**: Verify broker IP and port 1883
3. **JSON Parsing**: Ensure payload format matches examples
4. **Hardware**: Check wiring and component functionality

### Debug Output:
The Arduino Serial Monitor (115200 baud) shows:
- WiFi connection status
- MQTT messages received and parsed
- Device actions executed
- Response messages sent

This integration enables seamless control of Arduino-based smart home devices through voice commands from the Elder Care Assistant interface!