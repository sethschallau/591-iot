# Component Requirements for MQTT-Based IoT System

## 1. Laptop #1 (MQTT Broker)
- Install and run an **MQTT broker** (e.g., Mosquitto).
- Must **retain messages** for `lightSensor`, `threshold`, `LightStatus`, `Status/RaspberryPiA`, and `Status/RaspberryPiC`.
- Must support **QoS 2** for all topics.
- Should detect **ungraceful disconnects** and publish retained "offline" messages for Raspberry Pi A and C.
- Provide **timestamped logging** of all messages sent and received.

---

## 2. Raspberry Pi A (Publisher + Subscriber)
### **Hardware Components**
- Connect an **LDR** and **potentiometer** via an ADC.
- Sample **LDR and potentiometer values** every **100 ms**.

### **Data Processing**
- Compare **current vs. previous** ADC readings.
- Publish only if the change exceeds a **threshold**.
- Normalize/scale **potentiometer values** to match LDR values.

### **MQTT Communication**
- **Publish** LDR values to topic **"lightSensor"**.
- **Publish** potentiometer values to topic **"threshold"**.
- Set **retain flag** on published messages.
- **Subscribe** to "lightSensor" and "threshold" to receive previous retained values.
- Publish retained **"Status/RaspberryPiA"** message as:
  - `"online"` on successful connection.
  - `"offline"` on graceful disconnect.
- Configure **Last Will and Testament (LWT)** to publish `"offline"` to `"Status/RaspberryPiA"` on ungraceful disconnect.

---

## 3. Raspberry Pi B (Subscriber, LED Controller)
### **Hardware Components**
- Connect **three LEDs**:
  - **LED1** for LightStatus.
  - **LED2** for Raspberry Pi A status.
  - **LED3** for Raspberry Pi C status.

### **MQTT Subscriptions**
- **Subscribe** to `"LightStatus"`:
  - If `"TurnOn"`, turn **LED1 ON**.
  - If `"TurnOff"`, turn **LED1 OFF**.
- **Subscribe** to `"Status/RaspberryPiA"`:
  - If `"online"`, turn **LED2 ON**.
  - If `"offline"`, turn **LED2 OFF**.
- **Subscribe** to `"Status/RaspberryPiC"`:
  - If `"online"`, turn **LED3 ON**.
  - If `"offline"`, turn **LED3 OFF** and turn **LED1 OFF**.

---

## 4. Raspberry Pi C (Publisher + Subscriber)
### **MQTT Subscriptions**
- **Subscribe** to `"lightSensor"` and `"threshold"`.
- Compare **LDR value vs. threshold**:
  - If `lightSensor ≥ threshold`, generate `"TurnOff"`.
  - Otherwise, generate `"TurnOn"`.
- **Subscribe** to `"LightStatus"` to track its previous decision.

### **MQTT Publishing**
- If the computed decision differs from the last sent value, publish it to `"LightStatus"`.
- Set **retain flag** on `"LightStatus"`.
- Publish retained **"Status/RaspberryPiC"** message as:
  - `"online"` on successful connection.
  - `"offline"` on graceful disconnect.
- Configure **Last Will and Testament (LWT)** to publish `"offline"` to `"Status/RaspberryPiC"` on ungraceful disconnect.

---

## 5. Laptop #2 / Smartphone (Subscriber, Logger)
### **MQTT Subscriptions**
- Subscribe to `"lightSensor"`, `"threshold"`, `"LightStatus"`, `"Status/RaspberryPiA"`, and `"Status/RaspberryPiC"`.

### **Logging Requirements**
- **Timestamp** all received messages.
- Maintain a log file with all received messages.
- **No duplicate messages** should be logged (MQTT broker should prevent duplicates, not post-processing).
- If a duplicate is justified, automatically append a **reason** in the log.
- Maintain a **record of LED1 ON/OFF events** with timestamps.
- Display timestamps **only for LED1 ON/OFF events** during the demo.
