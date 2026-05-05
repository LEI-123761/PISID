# **DESCRIÇÃO**
# publisher_temperatura.py
#
# Este script corre no PC1 (onde está o MongoDB).
# Lê documentos de temperatura que ainda não foram enviados
# (Sent=False) e publica-os no broker MQTT.
# O receiver_temperatura.py no PC2 recebe essas mensagens
# e insere-as no MySQL.

import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import time

#configuração
MONGO_URI   = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
DB_NAME     = "SensorData"
COLLECTION  = "temps_received"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "mazetemp_4"
CLIENT_ID   = "pisid_publisher_temperatura"

#callbacks MQTT
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[TEMP] Ligado ao broker | session present: {flags['session present']}")
    else:
        print(f"[TEMP] Erro ao ligar, rc={reason_code}")

def on_publish(client, userdata, mid):
    print(f"[TEMP] Mensagem mid={mid} confirmada pelo broker")

#ligação MongoDB
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[DB_NAME][COLLECTION]

#ligação MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_publish  = on_publish
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
#loop para publicar no MQTT
# mqtt_client.loop_start()

print("[TEMP] Publisher iniciado...")

#loop principal para buscar coisas no mongo
while True:
    print("HI")
    try:
        docs = list(collection.find({"Sent": False}).sort("Id", 1))
        print(docs)

        for doc in docs:
            print(doc)
            payload = {
                "Id":doc.get("Id"),
                "Hour":doc.get("Hour"),
                "Temperature":doc.get("Temperature"),
            }
            print(payload)
            result = mqtt_client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
            print("gonna wait")
            # result.wait_for_publish()
            print(f"[TEMP] Enviado id={payload['Id']}")

    except Exception as e:
        print(f"[TEMP] Erro: {e}")

    time.sleep(1)