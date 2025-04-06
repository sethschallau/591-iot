from flask import Flask, render_template, jsonify
from flask_mqtt import Mqtt
import os

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = '3.147.73.221'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'ec2-user'
app.config['MQTT_PASSWORD'] = '591iot'
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = 'dispenserRunTime'

mqtt = Mqtt(app)

# Constants
FULL_ROLL_TIME = 300  #seconds
ROLLS_PER_TREE = 1700
CO2_PER_ROLL = 0.06  #pounds
DATA_FILE = "dispenserRunTime.txt"

def read_total_time():
    try:
        with open(DATA_FILE, "r") as f:
            return float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0.0

def write_total_time(total):
    with open(DATA_FILE, "w") as f:
        f.write(str(total))

def calculate_impact(seconds):
    rolls_used = seconds / FULL_ROLL_TIME
    trees_used = rolls_used / ROLLS_PER_TREE
    co2_used = rolls_used * CO2_PER_ROLL
    return rolls_used, trees_used, co2_used

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    try:
        new_seconds = float(message.payload.decode())
        current_total = read_total_time()
        updated_total = current_total + new_seconds
        write_total_time(updated_total)
    except ValueError:
        print("Invalid MQTT payload")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    total_seconds = read_total_time()
    rolls, trees, co2 = calculate_impact(total_seconds)
    return jsonify({
        "rolls_used": round(rolls, 3),
        "trees_used": round(trees, 5),
        "co2_used_lbs": round(co2, 3)
    })

if __name__ == '__main__':
    mqtt.subscribe(app.config['MQTT_TOPIC'])
    app.run(host='0.0.0.0', port=5050, debug=False)
