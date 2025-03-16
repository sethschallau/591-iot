#include <Wire.h>
#include <GY521.h>

GY521 mpu(0x68);

#define LED_PIN 2
#define WIGGLE_ROOM 0.05 

float ax_offset = 0, ay_offset = 0, az_offset = 0;
float gx_offset = 0, gy_offset = 0, gz_offset = 0;

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

    Serial.println("ax,ay,az,gx,gy,gz");
}

void loop() {
    unsigned long start_time = millis();
    while (millis() - start_time < 3000) {
        mpu.read();

        float ax = apply_wiggle(mpu.getAccelX(), ax_offset);
        float ay = apply_wiggle(mpu.getAccelY(), ay_offset);
        float az = apply_wiggle(mpu.getAccelZ(), az_offset);
        float gx = apply_wiggle(mpu.getGyroX(), gx_offset);
        float gy = apply_wiggle(mpu.getGyroY(), gy_offset);
        float gz = apply_wiggle(mpu.getGyroZ(), gz_offset);

        Serial.printf("%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n", ax, ay, az, gx, gy, gz);
        delay(100);
    }
    while (1);
}
