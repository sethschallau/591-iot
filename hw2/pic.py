import paho.mqtt.client as mqtt

BROKER = "10.153.19.51"

LIGHT_SENSOR_TOPIC = "lightSensor"
THRESHOLD_TOPIC = "threshold"
LIGHT_STATUS_TOPIC = "LightStatus"
STATUS_TOPIC = "Status/RaspberryPiC"

last_sent_status = None
light_sensor_value = None
threshold_value = None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")

        client.subscribe(LIGHT_SENSOR_TOPIC, qos=2)
        client.subscribe(THRESHOLD_TOPIC, qos=2)
        client.subscribe(LIGHT_STATUS_TOPIC, qos=2)

        client.publish(STATUS_TOPIC, "online", qos=2, retain=True)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global light_sensor_value, threshold_value, last_sent_status

    topic = msg.topic
    payload = msg.payload.decode().strip()

    if topic == LIGHT_SENSOR_TOPIC:
        light_sensor_value = float(payload)

    elif topic == THRESHOLD_TOPIC:
        threshold_value = float(payload)

    elif topic == LIGHT_STATUS_TOPIC:
        last_sent_status = payload

    if light_sensor_value is not None and threshold_value is not None:
        determine_light_status(client)


def determine_light_status(client):
    global last_sent_status, light_sensor_value, threshold_value

    if light_sensor_value >= threshold_value:
        new_status = "TurnOff"
    else:
        new_status = "TurnOn"

    if new_status != last_sent_status:
        client.publish(LIGHT_STATUS_TOPIC, new_status, qos=2, retain=True)
        last_sent_status = new_status


client = mqtt.Client()

client.will_set(STATUS_TOPIC, "offline", qos=2, retain=True)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(BROKER, 1883, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.publish(STATUS_TOPIC, "offline", qos=2, retain=True)
    client.disconnect()
