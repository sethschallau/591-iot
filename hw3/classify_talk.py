import paho.mqtt.client as mqtt
import pickle
import json
import numpy as np
from collections import deque

BROKER = "13.59.199.173"
PORT = 1883
USERNAME = "ec2-user"
PASSWORD = "591iot"
SUBSCRIBE_TOPIC = "sethschallaudoor"
PUBLISH_TOPIC = "sethschallauinterface"

class ClosedDoor:
    def state(self):
        return "closed"

    def handle(self, event):
        if event == "opening":
            return OpeningDoor()
        return self

class OpenDoor:
    def state(self):
        return "open"

    def handle(self, event):
        if event == "closing":
            return ClosingDoor()
        return self

class OpeningDoor:
    def state(self):
        return "opening"

    def handle(self, event):
        if event == "stable":
            return OpenDoor()
        return self

class ClosingDoor:
    def state(self):
        return "closing"

    def handle(self, event):
        if event == "stable":
            return ClosedDoor()
        return self
    
current_door = ClosedDoor()
buffer = deque(maxlen=12)

def load_classifier():
    with open("svm_model.pkl", "rb") as f:
        return pickle.load(f)

classifier = load_classifier()

def classify_chunk(chunk):
    features = np.array(chunk).flatten().reshape(1, -1)
    prediction = classifier.predict(features)[0]
    if prediction == 0:
        return "stable"
    elif prediction == 1:
        return "opening"
    else:
        return "closing"

def on_message(client, userdata, message):
    global current_door
    data = json.loads(message.payload.decode())
    buffer.append([data["ax"], data["az"], data["gx"], data["gz"]])

    if len(buffer) == 12:
        event = classify_chunk(list(buffer))
        current_door = current_door.handle(event)
        print(event)
        if current_door.state() in ["open", "closed"]:
            client.publish(PUBLISH_TOPIC, current_door.state())
        print(current_door.state())
        buffer.clear()

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(SUBSCRIBE_TOPIC)

client.loop_forever()
