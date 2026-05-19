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

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"[FB] Recebido: {data}")

        # ignora mensagens que não sejam confirmações de sucesso
        if data.get("status") != "ok":
            return

        # nome da coleção MongoDB a actualizar
        collection_name = data.get("collection")
        # id do documento a marcar como enviado
        Id = data.get("Id")

        # marca o documento como Sent=True usando o id incremental
        filter = {'Id': Id}
        update_operation = {"$set": {"Sent": True}}
        result = db[collection_name].update_one(
            filter,
            update_operation
        )

        if result.modified_count > 0:
            print(f"[FB] Sent=True em {collection_name} Id={ Id}")
        else:
            # pode acontecer se o documento foi apagado entretanto
            print(f"[FB] Não encontrado: {collection_name} Id={Id}")

    except Exception as e:
        print(f"[FB] Erro: {e}")

#callback ligação
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[FB] Ligado ao broker | session present")
        client.subscribe(MQTT_TOPIC, qos=2)
    else:
        print(f"[FB] Erro ao ligar, rc={reason_code}")

#cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=True)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

print("[FB] Feedback iniciado...")
# loop_forever() mantém o script vivo à espera de confirmações
mqtt_client.loop_forever()