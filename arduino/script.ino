#include <WiFiS3.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- WiFi & MQTT ---
const char *ssid = "Hdk";
const char *pswrd = "27082006";
const char *mqtt_server = "172.20.10.2";

// --- DHT11 Sensor ---
#define DHTPIN 3
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- Multi-Room LEDs ---
#define LIVING_ROOM_LED_PIN 8
#define BEDROOM_LED_PIN 9
#define KITCHEN_LED_PIN 10
#define BATHROOM_LED_PIN 11

String livingRoomLedStatus = "OFF";
String bedroomLedStatus = "OFF";
String kitchenLedStatus = "OFF";
String bathroomLedStatus = "OFF";

// --- OLED Display ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// --- Variables to store frontend data ---
String roomTemp = "--";
String roomHumid = "--";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pswrd);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Handle multi-room LED commands
  if (String(topic) == "home/living_room/lights/cmd") {
    if (message == "ON") {
      digitalWrite(LIVING_ROOM_LED_PIN, HIGH);
      livingRoomLedStatus = "ON";
    } else if (message == "OFF") {
      digitalWrite(LIVING_ROOM_LED_PIN, LOW);
      livingRoomLedStatus = "OFF";
    }
  }
  else if (String(topic) == "home/bedroom/lights/cmd") {
    if (message == "ON") {
      digitalWrite(BEDROOM_LED_PIN, HIGH);
      bedroomLedStatus = "ON";
    } else if (message == "OFF") {
      digitalWrite(BEDROOM_LED_PIN, LOW);
      bedroomLedStatus = "OFF";
    }
  }
  else if (String(topic) == "home/kitchen/lights/cmd") {
    if (message == "ON") {
      digitalWrite(KITCHEN_LED_PIN, HIGH);
      kitchenLedStatus = "ON";
    } else if (message == "OFF") {
      digitalWrite(KITCHEN_LED_PIN, LOW);
      kitchenLedStatus = "OFF";
    }
  }
  else if (String(topic) == "home/bathroom/lights/cmd") {
    if (message == "ON") {
      digitalWrite(BATHROOM_LED_PIN, HIGH);
      bathroomLedStatus = "ON";
    } else if (message == "OFF") {
      digitalWrite(BATHROOM_LED_PIN, LOW);
      bathroomLedStatus = "OFF";
    }
  }

  // Receive simulated data from frontend
  if (String(topic) == "home/room/data") {
    // Message format: "25.5,60.2" (temperature, humidity)
    int commaIndex = message.indexOf(',');
    if (commaIndex > 0) {
      roomTemp = message.substring(0, commaIndex);
      roomHumid = message.substring(commaIndex + 1);
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("UNO_R4_Client")) {
      Serial.println("connected");
      // Subscribe to multi-room LED commands
      client.subscribe("home/living_room/lights/cmd");
      client.subscribe("home/bedroom/lights/cmd");
      client.subscribe("home/kitchen/lights/cmd");
      client.subscribe("home/bathroom/lights/cmd");
      client.subscribe("home/room/data"); // subscribe to frontend topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Initialize multi-room LED pins
  pinMode(LIVING_ROOM_LED_PIN, OUTPUT);
  pinMode(BEDROOM_LED_PIN, OUTPUT);
  pinMode(KITCHEN_LED_PIN, OUTPUT);
  pinMode(BATHROOM_LED_PIN, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // --- Publish real sensor data to broker ---
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (!isnan(h) && !isnan(t)) {
    String payload = String(t) + "," + String(h);
    client.publish("home/dht11", payload.c_str());
    Serial.print("Published sensor: ");
    Serial.println(payload);
  }

  // --- Display simulated data from frontend (home/room/data) ---
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);

  display.print("Target Temp: ");
  display.println(roomTemp + " *C");

  display.print("Target Humid: ");
  display.println(roomHumid + " %");

  display.print("Living: ");
  display.println(livingRoomLedStatus);
  
  display.print("Bedroom: ");
  display.println(bedroomLedStatus);
  
  display.print("Kitchen: ");
  display.println(kitchenLedStatus);
  
  display.print("Bathroom: ");
  display.println(bathroomLedStatus);

  display.display();

  delay(2000);
}