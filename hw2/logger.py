import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.69"
LOG_FILE = "mqtt_log.txt"

TOPICS = ["lightSensor", "threshold", "LightStatus", "Status/RaspberryPiA", "Status/RaspberryPiC"]
message_log = {}

def on_message(client, userdata, msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"{timestamp} | {msg.topic} | {msg.payload.decode()}\n"

    if msg.topic in message_log and message_log[msg.topic] == msg.payload.decode():
        message = f"{timestamp} | {msg.topic} | {msg.payload.decode()} (Duplicate)\n"

    message_log[msg.topic] = msg.payload.decode()

    with open(LOG_FILE, "a") as log:
        log.write(message)

    if msg.topic == "LightStatus":
        print(f"{timestamp} | LED1 {'ON' if msg.payload.decode() == 'TurnOn' else 'OFF'}")

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

for topic in TOPICS:
    client.subscribe(topic)

client.on_message = on_message
client.loop_forever()
