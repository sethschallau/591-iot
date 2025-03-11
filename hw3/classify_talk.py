import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
SUBSCRIBE_TOPIC = "sethschallaudoor"
PUBLISH_TOPIC = "sethschallauinterface"

# def load_classifier():
#     #classifier from file (example: "classifier.pkl")
#     return None

def classify_message(payload):

    return payload

def on_message(client, userdata, message):
    received_payload = message.payload.decode()

    classification_result = classify_message(received_payload)

    client.publish(PUBLISH_TOPIC, classification_result)

client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(SUBSCRIBE_TOPIC)

client.loop_forever()
