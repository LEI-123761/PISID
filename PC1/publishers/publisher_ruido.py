# **DESCRICAO**
# publisher_ruido.py
#
# Este script corre no PC1 (onde está o MongoDB).
# Lê documentos de ruído que ainda não foram enviados
# (Sent=False) e publica-os no broker MQTT.
# O receiver_ruido.py no PC2 recebe essas mensagens
# e insere-as no MySQL.


import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import time

#configuração
MONGO_URI   = "mongodb://localhost:27017/"
DB_NAME     = "SensorData"
COLLECTION  = "sounds_received"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "pisid_mazesound_4"
CLIENT_ID   = "pisid_publisher_ruido"

#callbacks MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[SOM] Ligado ao broker | session present: {flags['session present']}")
    else:
        print(f"[SOM] Erro ao ligar, rc={rc}")

def on_publish(client, userdata, mid):
    print(f"[SOM] Mensagem mid={mid} confirmada pelo broker")

#ligação MongoDB
mongo_client = MongoClient(MONGO_URI)
collection   = mongo_client[DB_NAME][COLLECTION]

#ligação MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_publish  = on_publish
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

print("[SOM] Publisher iniciado...")

#loop principal
while True:
    try:
        docs = list(collection.find({"Sent": False}).sort("id_seq", 1))

        for doc in docs:
            payload = {
                "id_seq": doc["id_seq"],
                "Player": doc.get("Player"),
                "Hour":   doc.get("Hour"),
                "Sound":  doc.get("Sound"),
            }
            result = mqtt_client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
            result.wait_for_publish()
            print(f"[SOM] Enviado id_seq={payload['id_seq']}")

    except Exception as e:
        print(f"[SOM] Erro: {e}")

    time.sleep(1)