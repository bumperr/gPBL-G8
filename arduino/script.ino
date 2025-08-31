#include <WiFiS3.h>
#include <PubSubClient.h>
#include <DHT.h>

// --- WiFi & MQTT ---
const char *ssid = "Hdk";
const char *pswrd = "27082006";
const char *mqtt_server = "10.136.133.66";

// --- DHT11 ---
#define DHTPIN 3
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- LED ---
#define LED_PIN 8

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
  Serial.println("");
  Serial.println("WiFi connected!");
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

  if (String(topic) == "home/led/cmd") {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned ON");
    } else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED turned OFF");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("UNO_R4_Client")) {
      Serial.println("connected");
      client.subscribe("home/led/cmd");
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
  pinMode(LED_PIN, OUTPUT);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  String payload = String(t) + "," + String(h);
  client.publish("home/dht11", payload.c_str());

  Serial.print("Published: ");
  Serial.println(payload);

  delay(1000);
}