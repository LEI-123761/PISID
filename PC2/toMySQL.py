import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

TOPIC = "pisid_mazesound_4"

def on_connect(client, userdata, flags, rc, properties=None):
  print("Connected with result code "+str(rc))
  client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")), 60)
mqttc.subscribe(TOPIC)

mqttc.loop_forever()