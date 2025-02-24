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


# Initialize default values
state = {"lightSensor": None, "threshold": None, "lightStatus": None}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe([
            (TOPICS["lightSensor"], 2),
            (TOPICS["threshold"], 2),
            (TOPICS["lightStatus"], 2)
        ])
        client.publish(TOPICS["status"], "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = int(msg.payload.decode().strip())

    if topic in (TOPICS["lightSensor"], TOPICS["threshold"], TOPICS["lightStatus"]):
        state[topic] = payload
        print(f"Updated {topic}: {payload}")

    # Only proceed if we have both sensor values
    if state["lightSensor"] is not None and state["threshold"] is not None:
        try:
            sensor_value = int(state["lightSensor"])
            threshold_value = int(state["threshold"])
        except ValueError:
            print("Invalid sensor or threshold value.")
            return

        # This comparison matches your homework description exactly:
        if sensor_value >= threshold_value:
            new_decision = "TurnOn"
        else:
            new_decision = "TurnOff"

        # Compare with previous decision (received from "LightStatus")
        if new_decision != state["lightStatus"]:
            client.publish(TOPICS["lightStatus"], new_decision, retain=True)
            state["lightStatus"] = new_decision
            print(f"Published new decision: {new_decision}")

try:
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Graceful disconnect")
    client.publish(TOPICS["status"], "offline", retain=True)
    client.disconnect()
