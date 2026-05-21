import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import time

#configuração
MONGO_URI   = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
DB_NAME     = "SensorData"
COLLECTION  = "moves_received"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "mazemov_4"
CLIENT_ID   = "pisid_publisher_movimentos"

# chamada automatica quando se liga ao broker
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MOV] Ligado ao broker | session present")
    else:
        print(f"[MOV] Erro ao ligar, rc={reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"[MOV] Mensagem mid={mid} confirmada pelo broker")

#ligação MongoDB
mongo_client = MongoClient(MONGO_URI)
collection   = mongo_client[DB_NAME][COLLECTION]

#ligação MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=True)
mqtt_client.on_connect = on_connect
mqtt_client.on_publish  = on_publish
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
# loop_start() corre o MQTT em background para não bloquear o loop principal
mqtt_client.loop_start()

print("[MOV] Publisher iniciado...")

#loop principal
while True:
    try:
        # busca apenas documentos q ainda não receberam confirmacao de serem recebidos
        docs = list(collection.find({"Sent": False}).sort("Id", 1))

        for doc in docs:
            # id é o identificador incremental
            payload = {
                "Id":      doc.get("Id"),
                "Marsami":     doc.get("Marsami"),
                "RoomOrigin":  doc.get("RoomOrigin"),
                "RoomDestiny": doc.get("RoomDestiny"),
                "Status":      doc.get("Status")
            }

            result = mqtt_client.publish(MQTT_TOPIC, json.dumps(payload), qos=2)
            result.wait_for_publish() # bloqueia até o handshake estar completo
            if result[0] == 0:
                print(f"[MOV] Enviado Id={payload['Id']}")
            else:
                print(f"[MOV] Erro ao enviar MQTT")

    except Exception as e:
        print(f"[MOV] Erro: {e}")

    time.sleep(1)