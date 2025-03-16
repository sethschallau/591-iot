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
#define WIGGLE_ROOM 0.05

float ax_offset = 0, ay_offset = 0, az_offset = 0;
float gx_offset = 0, gy_offset = 0, gz_offset = 0;

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
            digitalWrite(LED_PIN, HIGH);
        } else {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            Serial.println(" Retrying in 5s...");
            delay(5000);
            digitalWrite(LED_PIN, LOW);
        }
    }
}

void calibrateSensor() {
    int samples = 50;
    for (int i = 0; i < samples; i++) {
        mpu.read();
        ax_offset += mpu.getAccelX();
        ay_offset += mpu.getAccelY();
        az_offset += mpu.getAccelZ();
        gx_offset += mpu.getGyroX();
        gy_offset += mpu.getGyroY();
        gz_offset += mpu.getGyroZ();
        delay(20);
    }
    ax_offset /= samples;
    ay_offset /= samples;
    az_offset /= samples;
    gx_offset /= samples;
    gy_offset /= samples;
    gz_offset /= samples;
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
    float ay = apply_wiggle(mpu.getAccelY(), ay_offset);
    float az = apply_wiggle(mpu.getAccelZ(), az_offset);
    float gx = apply_wiggle(mpu.getGyroX(), gx_offset);
    float gy = apply_wiggle(mpu.getGyroY(), gy_offset);
    float gz = apply_wiggle(mpu.getGyroZ(), gz_offset);

    char payload[256];
    snprintf(payload, sizeof(payload), 
             "{\"ax\":%.6f,\"ay\":%.6f,\"az\":%.6f,\"gx\":%.6f,\"gy\":%.6f,\"gz\":%.6f}",
             ax, ay, az, gx, gy, gz);

    if (client.publish(mqtt_topic, payload)) {
        Serial.println("Data sent: " + String(payload));
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
