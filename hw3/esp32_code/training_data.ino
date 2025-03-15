#include <Wire.h>
#include <GY521.h>

#define SDA_PIN D2  
#define SCL_PIN D1  
#define MPU_ADDR 0x68  

GY521 mpu(MPU_ADDR);

const float dt = 0.01;
unsigned long start_time;
bool logging = false;

void setup() {
    Serial.begin(115200);
    Wire.begin(SDA_PIN, SCL_PIN);
    mpu.begin();
    mpu.setAccelSensitivity(2);
    mpu.setGyroSensitivity(250);

    delay(2000);
    Serial.println("ax, ay, az, gx, gy, gz");
    start_time = millis();
    logging = true;
}

void loop() {
    if (!logging) return;

    mpu.read();

    float ax = mpu.getAccelX();
    float ay = mpu.getAccelY();
    float az = mpu.getAccelZ();
    float gx = mpu.getGyroX();
    float gy = mpu.getGyroY();
    float gz = mpu.getGyroZ();

    unsigned long timestamp = millis() - start_time;
    Serial.printf("%.6f, %.6f, %.6f, %.6f, %.6f, %.6f\n", 
                  ax, ay, az, gx, gy, gz);

    if (timestamp >= 3000) {
        logging = false;
        Serial.println("Logging complete.");
    }

    delay(10);
}
