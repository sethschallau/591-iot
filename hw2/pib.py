import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

BROKER = "192.168.1.69"
TOPICS = {
    "LightStatus": 17,
    "Status/RaspberryPiA": 27,
    "Status/RaspberryPiC": 22,
}
latest_light_status = "TurnOff"

GPIO.setmode(GPIO.BCM)
for pin in TOPICS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        for topic in TOPICS:
            client.subscribe(topic, qos=2)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global latest_light_status
    topic = msg.topic
    payload = msg.payload.decode().strip()
    pin = TOPICS.get(topic)

    if pin:
        if topic == "LightStatus":
            latest_light_status = payload
            if payload == "TurnOn":
                GPIO.output(pin, GPIO.HIGH)
            elif payload == "TurnOff":
                GPIO.output(pin, GPIO.LOW)

        elif topic == "Status/RaspberryPiA":
            if payload == "online":
                GPIO.output(pin, GPIO.HIGH)
            elif payload == "offline":
                GPIO.output(pin, GPIO.LOW)

        elif topic == "Status/RaspberryPiC":
            if payload == "online":
                GPIO.output(pin, GPIO.HIGH)
                if latest_light_status == "TurnOn":
                    GPIO.output(TOPICS["LightStatus"], GPIO.HIGH)
                else:
                    GPIO.output(TOPICS["LightStatus"], GPIO.LOW)
            elif payload == "offline":
                GPIO.output(pin, GPIO.LOW)
                GPIO.output(TOPICS["LightStatus"], GPIO.LOW)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(BROKER, 1883, 60)


try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
