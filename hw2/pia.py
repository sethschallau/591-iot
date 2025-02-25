import serial
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import spidev
import time

# Set up LED on GPIO 18
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Set up SPI (MCP3008 ADC)
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000

# Set up Serial Connection (Change port if needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# MQTT setup
broker = "10.153.19.51"  # Broker IP (replace with actual broker IP)
client = mqtt.Client()
client.connect(broker, 1883, 60)

# Last known values for LDR and Potentiometer
last_ldr = None
last_pot = None

# Thresholds for significant changes
ldr_threshold = 5
pot_threshold = 5

# # Function to read data from ADC (MCP3008)
# def read_adc(channel):
#     adc_value = spi.xfer2([1, (8 + channel) << 4, 0])
#     return ((adc_value[1] & 3) << 8) + adc_value[2]

# Set the will message for "Status/RaspberryPiA"
client.will_set("Status/RaspberryPiA", "offline", qos=1, retain=True)

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish("Status/RaspberryPiA", "online", qos=1, retain=True)

# Callback for when the client subscribes to a topic
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed with QoS {granted_qos}")

# Set up MQTT callbacks
client.on_connect = on_connect
client.on_subscribe = on_subscribe

# Connect to MQTT broker
client.connect(broker, 1883, 60)
client.loop_start()

# Subscribe to topics
client.subscribe("lightSensor", qos=1)
client.subscribe("threshold", qos=1)

# Main loop to sample LDR and Potentiometer and publish values
while True:
    try:
        # Read LDR and Potentiometer values from ADC
        #ldr_value = read_adc(0)  # LDR connected to channel 0
        #pot_value = read_adc(1)  # Potentiometer connected to channel 1

        ldr_value = 0
        pot_value = 0

        data = ser.readline().decode('utf-8').strip()

        if data:
            ldr_value, pot_value = map(int, data.split(","))  # Extract values
            #print(f"LDR: {ldr}, Potentiometer: {pot}")

        # Normalize values (if needed, or scale them as required)
        # normalized_ldr = ldr_value / 1023.0  # Assuming 10-bit ADC
        # normalized_pot = pot_value / 1023.0  # Assuming 10-bit ADC

        normalized_pot = pot_value
        normalized_ldr = ldr_value

        # Print the LDR and Potentiometer values
        print(f"LDR: {ldr_value}, Potentiometer: {pot_value}")
        
        # Publish to MQTT broker if there is a significant change
        if last_ldr is None or abs(ldr_value - last_ldr) > ldr_threshold:
            client.publish("lightSensor", normalized_ldr, qos=1, retain=True)
            last_ldr = ldr_value
            print(f"Published - lightsensor")
        
        if last_pot is None or abs(pot_value - last_pot) > pot_threshold:
            #normalized_pot = (pot_value - 90) / (250 - 90)  # Example scaling from 90-250 to 0-1
            client.publish("threshold", normalized_pot, qos=1, retain=True)
            last_pot = pot_value
            print(f"Published - threshold")

        # Compare and control LED based on threshold
        if ldr_value < pot_value:  # If LDR value is less than threshold (potentiometer)
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn ON LED
        else:
            GPIO.output(LED_PIN, GPIO.LOW)   # Turn OFF LED

        # Wait for 100ms before sampling again
        time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")

