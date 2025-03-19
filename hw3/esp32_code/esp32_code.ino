#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <GY521.h>

const char* ssid = "SethPhone";  
const char* password = "sethisopen";  

const char* mqtt_server = "13.59.199.173";  
const int mqtt_port = 1883;  
const char* mqtt_user = "ec2-user";  
const char* mqtt_pass = "591iot";  
const char* mqtt_topic = "sethschallaudoor";  

WiFiClient espClient;
PubSubClient client(espClient);
GY521 mpu(0x68);

#define LED_PIN 2
#define WIGGLE_ROOM 0.015 

float ax_offset = 0, az_offset = 0;

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
        if (client.connect("ESP32Client", mqtt_user, mqtt_pass)) {
            Serial.println("Connected to MQTT!");
            digitalWrite(LED_PIN, HIGH);
        } else {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            Serial.println(" Retrying in 5s...");
            digitalWrite(LED_PIN, LOW);
            delay(5000);
            
        }
    }
}

void calibrateSensor() {
    int samples = 50;
    for (int i = 0; i < samples; i++) {
        mpu.read();
        ax_offset += mpu.getAccelX();
        az_offset += mpu.getAccelZ();
        delay(20);
    }
    ax_offset /= samples;
    az_offset /= samples;
}

float apply_wiggle(float value, float offset) {
    float normalized = value - offset;
    if (abs(normalized) < WIGGLE_ROOM) {
        return 0.0;
    }
    return normalized;
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    Wire.begin();
    mpu.begin();
    mpu.setAccelSensitivity(2);
    mpu.setGyroSensitivity(250);

    calibrateSensor();
    connectWiFi();
    client.setServer(mqtt_server, mqtt_port);
    connectMQTT();
}

void sendSensorData() {
    mpu.read();

    float ax = apply_wiggle(mpu.getAccelX(), ax_offset);
    float az = apply_wiggle(mpu.getAccelZ(), az_offset);
    float gx = mpu.getGyroX();
    float gz = mpu.getGyroZ();

    char payload[256];
    snprintf(payload, sizeof(payload), 
             "{\"ax\":%.6f,\"az\":%.6f,\"gx\":%.6f,\"gz\":%.6f}",
             ax, az, gx, gz);

    if (client.publish(mqtt_topic, payload)) {
        Serial.println("Data sent: " + String(payload));
        digitalWrite(LED_PIN, HIGH);
    } else {
        Serial.println("Failed to send data");
    }
}

void loop() {
    if (!client.connected()) {
        connectMQTT();
    }
    client.loop();
    sendSensorData();  
    delay(100);
}
