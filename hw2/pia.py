import paho.mqtt.client as mqtt
import spidev
import time

BROKER = "192.168.1.69"
TOPICS = {
    "lightSensor": "lightSensor",
    "threshold": "threshold",
    "status": "Status/RaspberryPiA",
}

client = mqtt.Client()
client.will_set(TOPICS["status"], "offline", retain=True)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000


def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe([(TOPICS["lightSensor"], 2), (TOPICS["threshold"], 2)])
        client.publish(TOPICS["status"], "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")


prev_ldr = prev_pot = 0

def publish_sensor_data():
    global prev_ldr, prev_pot
    ldr_value = read_adc(0)
    pot_value = read_adc(1)

    if abs(ldr_value - prev_ldr) > 5:
        client.publish(TOPICS["lightSensor"], ldr_value, retain=True)
        prev_ldr = ldr_value

    if abs(pot_value - prev_pot) > 5:
        client.publish(TOPICS["threshold"], pot_value, retain=True)
        prev_pot = pot_value


client.on_connect = on_connect
client.connect(BROKER, 1883, 60)

try:
    while True:
        publish_sensor_data()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    client.publish(TOPICS["status"], "offline", retain=True)
    client.disconnect()
