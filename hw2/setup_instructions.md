## **Pi A Instructions**
### **Install**
- You will need a working python3 install
- pip3 install paho-mqtt

### **Setup**
- On line 4, change the broker variable to the corresponding broker IP address


### **Running**
- python3 pib.py

## **Pi B Instructions**
### **Install**
- You will need a working python3 install
- pip3 install paho-mqtt

### **Setup**
- On line 4, change the broker variable to the corresponding broker IP address
- I made a service file, to restart the service on pib, sudo systemctl restart mqtt_pib.service


### **Running**
- python3 pib.py

## **Pi C Instructions**
### **Install**
- You will need a working python3 install
- pip3 install paho-mqtt

### **Setup**
- On line 3, change the broker variable to the corresponding broker IP address


### **Running**
- python3 pib.py


## **Laptop 1 Broker Instructions**
### **Install**
```sh
sudo apt install mosquitto mosquitto-clients -y
```

### **Setup**
Edit the Mosquitto configuration file:
```sh
sudo nano /etc/mosquitto/mosquitto.conf
```
Add the following lines:
```sh
listener 1883
allow_anonymous true
max_queued_messages 1000
queue_qos0_messages false
```
Save and exit.

### **Restart Mosquitto**
```sh
sudo systemctl restart mosquitto
```

### **Start Mosquitto Manually**
```sh
mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

### **Testing the Broker**
Open **two separate terminals** and run:

**Subscriber Terminal:**
```sh
mosquitto_sub -h localhost -t "test/topic" -q 2
```

**Publisher Terminal:**
```sh
mosquitto_pub -h localhost -t "test/topic" -m "Going Test Mode" -q 2 -r
```

## **Laptop #2 Instructions**
### **Install**
- You will need a working python3 install
- pip3 install paho-mqtt

### **Setup**
- On line 4, change the broker variable to the corresponding broker IP address

### **Running**
- python3 listener.py

### **Getting the log file**
- the log file will be written to the directory where the file is run