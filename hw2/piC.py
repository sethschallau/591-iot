import paho.mqtt.client as mqtt

BROKER = "X.X.X.X"
TOPICS = {
    "lightSensor": "lightSensor",
    "threshold": "threshold",
    "lightStatus": "LightStatus",
    "status": "Status/RaspberryPiC",
}

client = mqtt.Client()
client.will_set(TOPICS["status"], "offline", retain=True)


last_status = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe([(TOPICS["lightSensor"], 2), (TOPICS["threshold"], 2)])
        client.publish(TOPICS["status"], "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global last_status
    topic = msg.topic
    payload = int(msg.payload.decode().strip())

    # Get current values
    light_sensor = int(client._userdata.get("lightSensor", 0))
    threshold = int(client._userdata.get("threshold", 50))  # Default 50

    # Store received values
    client._userdata[topic] = payload

    if topic in [TOPICS["lightSensor"], TOPICS["threshold"]]:
        # Recalculate light status
        new_status = "TurnOff" if light_sensor >= threshold else "TurnOn"
        if new_status != last_status:
            client.publish(TOPICS["lightStatus"], new_status, retain=True)
            print(f"Updated LightStatus: {new_status}")
            last_status = new_status


client.user_data_set({})
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()
