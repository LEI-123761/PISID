from dotenv import load_dotenv;
import os;
from connection import connect_to_mysql
import json
import paho.mqtt.client as mqtt

load_dotenv();

TOPIC = "pisid_mazemov_4"

config = {
    'user': os.environ.get("MOVES_USER"),
    'password': os.environ.get("MOVES_PASSWORD"),
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

add_moves_query = (
  "INSERT INTO MedicoesPassagens (IDSimulacao, SalaOrigem, SalaDestino, Marsami, Status) "
  "VALUES (%s, %s, %s, %s, %s)"
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

  data_to_insert = (id_simulacao, data['RoomOrigin'], data['RoomDestiny'], data['Marsami'], data['Status'])

  cursor.execute(add_moves_query, data_to_insert)
  cnx.commit()
  print("Inserted move data into the database: ", data_to_insert)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")), 60)
mqttc.subscribe(TOPIC)

mqttc.loop_forever()