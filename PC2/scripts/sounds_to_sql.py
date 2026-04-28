from typing import TypedDict
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from connection import connect_to_mysql
import json
import os

TOPIC = "pisid_mazesound_4"

load_dotenv();

config = {
    'user': os.environ.get("SOUNDS_USER"),
    'password': os.environ.get("SOUNDS_PASSWORD"),
    'host': os.environ.get("HOST", "mysql"),
    'database': os.environ.get("DATABASE", "maze")
}

get_idSimulacao_query = (
    "SELECT IDSimulacao "
    "FROM Simulacao "
    "WHERE Status = 'Correr' "
    "ORDER BY DataHoraInicio DESC "
    "LIMIT 1"
)

add_sound_query = (
  "INSERT INTO Som (IDSimulacao, Hora, Som) "
  "VALUES (%s, %s, %s)"
)

cnx = connect_to_mysql(config, attempts=5)

if cnx and cnx.is_connected():
  print("Connected to the database")

  cursor = cnx.cursor()
else:
    print("Failed to connect to the database after multiple attempts.")

def on_connect(client, userdata, flags, rc, properties=None):
  print("Connected with result code "+str(rc))
  client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
  cursor.execute(get_idSimulacao_query)
  id_simulacao = cursor.fetchone()[0]

  data = json.loads(msg.payload.decode('utf-8'))
  data_to_insert = (id_simulacao, data['Hour'], data['Sound'])

  cursor.execute(add_sound_query, data_to_insert)
  cnx.commit()
  print("Inserted sound data into the database: ", data_to_insert)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")), 60)
mqttc.subscribe(TOPIC)

mqttc.loop_forever()