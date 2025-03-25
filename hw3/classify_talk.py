import paho.mqtt.client as mqtt
import pickle
import json
import numpy as np
from collections import deque


BROKER = "broker.hivemq.com"
PORT = 1883
SUBSCRIBE_TOPIC = "sethschallaudoor"
PUBLISH_TOPIC = "sethschallauinterface"

class ClosedDoor:
    def __init__(self):
        self.next_state = OpenDoor 

    def state(self):
        return "closed"

    def detect_moving(self):
        return MovingDoor(self.next_state()) 

class OpenDoor:
    def __init__(self):
        self.next_state = ClosedDoor

    def state(self):
        return "open"

    def detect_moving(self):
        return MovingDoor(self.next_state())

class MovingDoor:
    def __init__(self, next_state):
        self.next_state = next_state

    def state(self):
        return "moving"

    def detect_stable(self):
        return self.next_state
    
current_door = ClosedDoor()
buffer = deque(maxlen=6)

def load_classifier():
    with open("svm_model.pkl", "rb") as f:
        return pickle.load(f)

classifier = load_classifier()

def classify_chunk(chunk):
    features = np.array(chunk).flatten().reshape(1, -1)
    prediction = classifier.predict(features)[0]
    return "stable" if prediction == 0 else "moving"

def on_message(client, userdata, message):
    global current_door, previous_stable_state
    data = message.payload.decode()
    buffer.append([data["ax"], data["ay"], data["az"], data["gx"], data["gy"], data["gz"]])

    if len(buffer) == 6:
        classification_result = classify_chunk(list(buffer))
        
        if classification_result == "moving" and current_door.state() in ["closed", "open"]:
            current_door = current_door.detect_moving()

        elif classification_result == "stable" and current_door.state() == "moving":
            current_door = current_door.detect_stable()
            client.publish(PUBLISH_TOPIC, current_door.state())

        buffer.clear()

    

client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(SUBSCRIBE_TOPIC)

client.loop_forever()
