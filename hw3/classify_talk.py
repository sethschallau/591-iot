import paho.mqtt.client as mqtt
import json
import pickle

BROKER = "broker.hivemq.com"
PORT = 1883
SUBSCRIBE_TOPIC = "sethschallaudoor"
PUBLISH_TOPIC = "sethschallauinterface"

# Load trained classifier
with open("classifier.pkl", "rb") as f:
    classifier = pickle.load(f)

def classify_message(payload):
    try:
        data = json.loads(payload)
        features = [data['accel_x'], data['accel_y'], data['accel_z'],
                    data['gyro_x'], data['gyro_y'], data['gyro_z']]
        result = classifier.predict([features])[0]
        return "Door OPEN" if result == 1 else "Door CLOSED"
    except Exception as e:
        print("Error in classification:", e)
        return "Invalid Data"

def on_message(client, userdata, message):
    received_payload = message.payload.decode()
    classification_result = classify_message(received_payload)
    print(f"Received IMU → Classified: {classification_result}")
    client.publish(PUBLISH_TOPIC, classification_result)

client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(SUBSCRIBE_TOPIC)

client.loop_forever()
