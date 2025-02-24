import paho.mqtt.client as mqtt
import time
import random  

# MQTT setup
broker = "BROKER_IP_ADDRESS"  
port = 1883
topic = "test/topic"  

def on_publish(client, userdata, mid):
    print("Message Published: ", mid)


client = mqtt.Client()


client.on_publish = on_publish


client.connect(broker, port)


while True:
  
    sensor_value = random.randint(0, 1023)  
    
    
    payload = str(sensor_value)
    

    result = client.publish(topic, payload, qos=2, retain=True)
    
   
    print(f"Published: {payload}")
    

    time.sleep(2)
