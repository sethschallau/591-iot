import paho.mqtt.client as mqtt
import pickle
import json
import numpy as np

BROKER = "broker.hivemq.com"
PORT = 1883
SUBSCRIBE_TOPIC = "sethschallaudoor"
PUBLISH_TOPIC = "sethschallauinterface"

class ClosedDoor:
    def state(self):
        return "closed"

    def next_state(self):
        return OpenDoor()

class OpenDoor:
    def state(self):
        return "open"

    def next_state(self):
        return ClosedDoor()

current_door = ClosedDoor()

def load_classifier():
    with open("svm_model.pkl", "rb") as f:
        return pickle.load(f)

classifier = load_classifier()

def classify_message(payload):
    data = json.loads(payload)
    features = np.array([[data["ax"], data["ay"], data["az"], data["gx"], data["gy"], data["gz"]]])
    prediction = classifier.predict(features)[0]
    return "stable" if prediction == 0 else "moving"

def on_message(client, userdata, message):
    global current_door
    received_payload = message.payload.decode()

    classification_result = classify_message(received_payload)
    
    if classification_result == "moving":
        current_door = current_door.next_state()
        client.publish(PUBLISH_TOPIC, current_door.state())

    

client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(SUBSCRIBE_TOPIC)

client.loop_forever()
