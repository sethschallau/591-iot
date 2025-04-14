#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT configuration
const char* ssid = "Panthera";
const char* password = "icedragon";
const char* mqtt_server = "3.147.73.221";
const int mqtt_port = 1883;
const char* mqtt_user = "ec2-user";
const char* mqtt_pass = "591iot";
const char* mqtt_topic = "dispenserRunTime";

// MQTT and WiFi clients
WiFiClient espClient;
PubSubClient client(espClient);

// Pin definitions for ULN2003 and 28BYJ-48 motor
#define IN1 D3
#define IN2 D4
#define IN3 D5
#define IN4 D6

// Ultrasonic sensor pins
#define TRIG_PIN D2
#define ECHO_PIN D1
#define DISTANCE_THRESHOLD 6  // cm

unsigned long motorStartTime = 0;
bool motorRunning = false;

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

void connectMQTT() {
  Serial.println("Connecting to MQTT...");
  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqtt_user, mqtt_pass)) {
      Serial.println("Connected to MQTT!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Motor pin setup
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Ultrasonic sensor pin setup
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  connectWiFi();
  client.setServer(mqtt_server, mqtt_port);
  connectMQTT();
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();

  long distance = getDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance <= DISTANCE_THRESHOLD && !motorRunning) {
    Serial.println("paper dispensing");
    motorRunning = true;
    motorStartTime = millis();
    rotateMotorForTime(5000);
    client.publish(mqtt_topic, "5");
    Serial.println("Published 5 to dispenserRunTime");
  }

  if (motorRunning && millis() - motorStartTime >= 5000) {
    stopMotor();
    motorRunning = false;
  }

  delay(100);
}

long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  long distance = (duration / 2) / 29.1;

  return distance;
}

void rotateMotorForTime(unsigned long time) {
  unsigned long startTime = millis();
  while (millis() - startTime < time) {
    rotateMotor();
    delay(5);
  }
}

void rotateMotor() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  delay(5);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(5);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);
}

void stopMotor() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
