#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <GY521.h>

const char* ssid = "SethPhone";  
const char* password = "sethisopen";  

const char* mqtt_server = "broker.emqx.io";  
const int mqtt_port = 1883;  
const char* mqtt_topic = "sethschallaudoor";  

WiFiClient espClient;
PubSubClient client(espClient);
GY521 mpu(0x68);

#define LED_PIN 2

void connectWiFi() {
   Serial.print("Connecting to WiFi: ");
   Serial.println(ssid);
   WiFi.begin(ssid, password);

   int retries = 0;
   while (WiFi.status() != WL_CONNECTED && retries < 30) {
       delay(500);
       Serial.print(".");
       retries++;
   }

   if (WiFi.status() == WL_CONNECTED) {
       Serial.println("\nWiFi Connected!");
       digitalWrite(LED_PIN, HIGH);
   } else {
       Serial.println("\nWiFi Connection Failed!");
   }
}

void connectMQTT() {
   Serial.println("Connecting to MQTT...");
   
   while (!client.connected()) {
       Serial.print("Attempting MQTT connection...");
       if (client.connect("ESP32Client")) {
           Serial.println("Connected to MQTT!");
       } else {
           Serial.print("Failed, rc=");
           Serial.print(client.state());
           Serial.println(" Retrying in 5s...");
           delay(5000);
       }
   }
}

void setup() {
   Serial.begin(115200);
   pinMode(LED_PIN, OUTPUT);
   digitalWrite(LED_PIN, LOW);

   Wire.begin();
   mpu.begin();
   mpu.setAccelSensitivity(2);
   mpu.setGyroSensitivity(250);

   connectWiFi();
   client.setServer(mqtt_server, mqtt_port);
   connectMQTT();
}

void sendSensorData() {
   mpu.read();

   float ax = mpu.getAccelX();
   float ay = mpu.getAccelY();
   float az = mpu.getAccelZ();
   float gx = mpu.getGyroX();
   float gy = mpu.getGyroY();
   float gz = mpu.getGyroZ();

   char payload[256];
   snprintf(payload, sizeof(payload), 
            "{\"ax\":%.6f,\"ay\":%.6f,\"az\":%.6f,\"gx\":%.6f,\"gy\":%.6f,\"gz\":%.6f}",
            ax, ay, az, gx, gy, gz);

   client.publish(mqtt_topic, payload)
}

void loop() {
   if (!client.connected()) {
       connectMQTT();
   }

   client.loop();
   sendSensorData();  
   delay(100);
}