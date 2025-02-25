import serial
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import spidev
import time


LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 1350000


ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)


broker = "10.153.19.51" 
client = mqtt.Client()
client.connect(broker, 1883, 60)


last_ldr = None
last_pot = None


ldr_threshold = 5
pot_threshold = 5


client.will_set("Status/RaspberryPiA", "offline", qos=1, retain=True)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish("Status/RaspberryPiA", "online", qos=1, retain=True)


def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed with QoS {granted_qos}")


client.on_connect = on_connect
client.on_subscribe = on_subscribe


client.connect(broker, 1883, 60)
client.loop_start()

client.subscribe("lightSensor", qos=1)
client.subscribe("threshold", qos=1)


while True:
    try:
        ldr_value = 0
        pot_value = 0

        data = ser.readline().decode('utf-8').strip()

        if data:
            ldr_value, pot_value = map(int, data.split(",")) 

        normalized_pot = pot_value
        normalized_ldr = ldr_value

       
        print(f"LDR: {ldr_value}, Potentiometer: {pot_value}")
        
 
        if last_ldr is None or abs(ldr_value - last_ldr) > ldr_threshold:
            client.publish("lightSensor", normalized_ldr, qos=1, retain=True)
            last_ldr = ldr_value
            print(f"Published - lightsensor")
        
        if last_pot is None or abs(pot_value - last_pot) > pot_threshold:
    
            client.publish("threshold", normalized_pot, qos=1, retain=True)
            last_pot = pot_value
            print(f"Published - threshold")

      
        if ldr_value < pot_value:  
            GPIO.output(LED_PIN, GPIO.HIGH)  
        else:
            GPIO.output(LED_PIN, GPIO.LOW)  


        time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")

