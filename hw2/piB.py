import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

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

# Store latest LightStatus
latest_light_status = "TurnOff"

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
                # Immediately set LED1 according to latest LightStatus
                if latest_light_status == "TurnOn":
                    GPIO.output(TOPICS["LightStatus"], GPIO.HIGH)
                    print("LED1 (LightStatus) ON due to PiC online")
                else:
                    GPIO.output(TOPICS["LightStatus"], GPIO.LOW)
                    print("LED1 (LightStatus) OFF due to PiC online")
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
