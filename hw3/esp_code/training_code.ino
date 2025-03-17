#include <Wire.h>
#include <GY521.h>

GY521 mpu(0x68);

#define LED_PIN 2
#define WIGGLE_ROOM 0.015 

float ax_offset = 0, az_offset = 0;

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

void blinkLED() {
    for (int i = 0; i < 3; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(300);
        digitalWrite(LED_PIN, LOW);
        delay(300);
    }
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    pinMode(LED_PIN, OUTPUT);

    mpu.begin();
    mpu.setAccelSensitivity(2);
    mpu.setGyroSensitivity(250);

    calibrateSensor();
    blinkLED();

//    Serial.println("ax,az,gx,gz,state");
}

void loop() {
    static bool logging = true;
    static unsigned long start_time = millis();
    if (!logging) return;

    mpu.read();

    float ax = apply_wiggle(mpu.getAccelX(), ax_offset);
    float az = apply_wiggle(mpu.getAccelZ(), az_offset);
    float gx = mpu.getGyroX();
    float gz = mpu.getGyroZ();

//    Serial.printf("%.6f,%.6f,%.6f,%.6f\n", ax, az, gx, gz);

    if (abs(ax) == 0 && abs(az) == 0) {
        Serial.printf("%.6f,%.6f,%.6f,%.6f,stable\n", ax, az, gx, gz);
    } else {
        Serial.printf("%.6f,%.6f,%.6f,%.6f,moving\n", ax, az, gx, gz);

    }

    if (millis() - start_time >= 10000) {
        logging = false;
//        Serial.println("Logging complete.");
    }

    delay(10);
}
