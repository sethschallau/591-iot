import paho.mqtt.client as mqtt
import datetime

BROKER = "10.153.19.51"
TOPICS = [
    "LightStatus",
    "lightSensor",
    "threshold",
    "Status/RaspberryPiA",
    "Status/RaspberryPiC",
]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        for topic in TOPICS:
            client.subscribe(topic, qos=2)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"{timestamp} - Topic: {topic}, Message: {payload}")

    if topic == "LightStatus":
        with open("LightStatus_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - {payload}\n")



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(BROKER, 1883, 60)


try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
