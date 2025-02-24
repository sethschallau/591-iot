import paho.mqtt.client as mqtt
import spidev
import time

BROKER = "X.X.X.X"
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

state = {"lightSensor": None, "threshold": None}

LDR_CHANNEL = 0
POT_CHANNEL = 1

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]

def scale_value(value, original_min, original_max, new_min=0, new_max=100):
    scaled = ((value - original_min) / (original_max - original_min)) * (new_max - new_min) + new_min
    return max(new_min, min(new_max, int(scaled)))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe([(TOPICS["lightSensor"], 2), (TOPICS["threshold"], 2)])
        client.publish(TOPICS["status"], "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    state[topic] = int(payload)

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()


LDR_MIN, LDR_MAX = 10, 100
POT_MIN, POT_MAX = 90, 250
CHANGE_THRESHOLD = 5

try:
    prev_ldr = prev_pot = None
    while True:
        raw_ldr = read_adc(LDR_CHANNEL)
        raw_pot = read_adc(POT_CHANNEL)

        ldr_value = scale_value(raw_ldr, LDR_MIN, LDR_MAX)
        pot_value = scale_value(raw_pot, POT_MIN, POT_MAX)

        if (prev_ldr is None) or abs(ldr_value - prev_ldr) >= CHANGE_THRESHOLD:
            client.publish(TOPICS["lightSensor"], ldr_value, retain=True)
            prev_ldr = ldr_value

        if (prev_pot is None) or abs(pot_value - prev_pot) >= CHANGE_THRESHOLD:
            client.publish(TOPICS["threshold"], pot_value, retain=True)
            prev_pot = pot_value

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Graceful disconnect")
    client.publish(TOPICS["status"], "offline", retain=True)
    client.disconnect()
    client.loop_stop()