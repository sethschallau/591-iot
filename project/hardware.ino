#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT Config
const char* ssid = "SethPhone";
const char* password = "sethisopen";

const char* mqtt_server = "13.59.199.173";
const int mqtt_port = 1883;
const char* mqtt_user = "ec2-user";
const char* mqtt_pass = "591iot";
const char* mqtt_topic = "dispenserRunTime";

WiFiClient espClient;
PubSubClient client(espClient);

#define IN1 D3
#define IN2 D4
#define IN3 D5
#define IN4 D6

unsigned long previousMillis = 0;
const long interval = 5000;

bool motorRunning = false;
bool sentMQTT = false;

// WiFi Setup
void connectWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 30) {
        delay(500);
        Serial.print(".");
        retries++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? "\nWiFi Connected!" : "\nWiFi Failed!");
}

// MQTT Setup
void connectMQTT() {
    Serial.println("Connecting to MQTT...");
    while (!client.connected()) {
        if (client.connect("ESP32Client", mqtt_user, mqtt_pass)) {
            Serial.println("Connected to MQTT!");
        } else {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            delay(5000);
        }
    }
}

// Motor Control
void rotateMotor() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(5);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  delay(5);
}

void stopMotor() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  connectWiFi();
  client.setServer(mqtt_server, mqtt_port);
  connectMQTT();
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (motorRunning) {
      stopMotor();
      motorRunning = false;
      sentMQTT = false;
    } else {
      motorRunning = true;
      if (!sentMQTT) {
        client.publish(mqtt_topic, "5");
        Serial.println("Published 5 to dispenserRunTime");
        sentMQTT = true;
      }
    }
  }

  if (motorRunning) {
    rotateMotor();
  }
}
