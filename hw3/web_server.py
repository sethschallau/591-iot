from flask import Flask, render_template, jsonify
from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = 'sethschallauinterface'

mqtt = Mqtt(app)

# Store latest door status
door_status = "closed"

# Handle incoming MQTT messages
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global door_status
    door_status = message.payload.decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    return jsonify({"status": door_status})

if __name__ == '__main__':
    mqtt.subscribe(app.config['MQTT_TOPIC'])
    app.run(host='0.0.0.0', port=5050, debug=True)
