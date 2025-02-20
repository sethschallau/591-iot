import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

BROKER = "192.168.1.69"
TOPICS = {
    "LightStatus": 17,
    "Status/RaspberryPiA": 27,
    "Status/RaspberryPiC": 22,
}


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
    topic = msg.topic
    payload = msg.payload.decode().strip()
    pin = TOPICS.get(topic)

    if pin:
        if topic == "LightStatus":
            if payload == "TurnOn":
                GPIO.output(pin, GPIO.HIGH)
                print(f"LED1 (LightStatus) ON")
            elif payload == "TurnOff":
                GPIO.output(pin, GPIO.LOW)
                print(f"LED1 (LightStatus) OFF")

        elif topic == "Status/RaspberryPiA":
            if payload == "online":
                GPIO.output(pin, GPIO.HIGH)
                print(f"LED2 (Pi A Status) ON")
            elif payload == "offline":
                GPIO.output(pin, GPIO.LOW)
                print(f"LED2 (Pi A Status) OFF")

        elif topic == "Status/RaspberryPiC":
            if payload == "online":
                GPIO.output(pin, GPIO.HIGH)
                print(f"LED3 (Pi C Status) ON")
            elif payload == "offline":
                GPIO.output(pin, GPIO.LOW)
                GPIO.output(TOPICS["LightStatus"], GPIO.LOW)
                print(f"LED3 (Pi C Status) OFF + LED1 OFF")


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
