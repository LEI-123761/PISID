# **DESCRICAO**
# feedback.py
#
# Este script corre no PC1 (onde está o MongoDB).
# Subscreve o tópico de feedback no broker MQTT.
# Quando um receiver (PC2) insere dados no MySQL com sucesso,
# publica uma confirmação com o id_seq do documento.
# Este script recebe essa confirmação e marca o documento
# original no MongoDB como Sent=True, fechando o ciclo.

import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json

#configuração
MONGO_URI   = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
DB_NAME     = "SensorData"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
# tópico onde os receivers publicam as confirmações
MQTT_TOPIC  = "pisid_feedback_4"
CLIENT_ID   = "pisid_feedback"

#ligação MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# chamada automaticamente quando chega uma confirmação de um receiver
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"[FB] Recebido: {data}")

        # ignora mensagens que não sejam confirmações de sucesso
        if data.get("status") != "ok":
            return

        # nome da coleção MongoDB a actualizar
        collection_name = data.get("collection")
        # id_seq do documento a marcar como enviado
        id_seq = data.get("Id")

        # marca o documento como Sent=True usando o id_seq incremental
        result = db[collection_name].update_one(
            {"Id": id_seq},
            {"$set": {"Sent": True}}
        )

        if result.modified_count == 1:
            print(f"[FB] Sent=True em {collection_name} Id={id_seq}")
        else:
            # pode acontecer se o documento foi apagado entretanto
            print(f"[FB] Não encontrado: {collection_name} Id={id_seq}")

    except Exception as e:
        print(f"[FB] Erro: {e}")

#callback ligação
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[FB] Ligado ao broker | session present: {flags['session present']}")
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        print(f"[FB] Erro ao ligar, rc={rc}")

#liente MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

print("[FB] Feedback iniciado...")
# loop_forever() mantém o script vivo à espera de confirmações
mqtt_client.loop_forever()