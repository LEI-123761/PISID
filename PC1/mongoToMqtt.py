from pymongo import MongoClient
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

#dados frequentes
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "maze"
COLLECTION = "movements"

MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "pisid_mazemov_1"

#tratar de timestamps
def load_timestamp():
    try:
        with open("last_ts.txt", "r") as f:
            return datetime.fromisoformat(f.read().strip())
    except:
        return None

def save_timestamp(ts):
    with open("last_ts.txt", "w") as f:
        f.write(ts.isoformat())

# 
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[DB_NAME][COLLECTION]

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, 1883)

#estado
last_timestamp = load_timestamp()
print("Timestamp inicial:", last_timestamp)

buffer = []

#loop
while True:

    print("A correr...")

    # query incremental
    query = {}
    if last_timestamp:
        query = {"Hour": {"$gt": last_timestamp}}

    docs = collection.find(query).sort([("Hour", 1), ("_id", 1)])

    docs_list = list(docs)
    print("Docs encontrados:", docs_list)

    # adicionar ao buffer
    for doc in docs_list:
        doc["_id"] = str(doc["_id"])

        # converter Date para string (para JSON)
        if isinstance(doc["Hour"], datetime):
            doc["Hour"] = doc["Hour"].isoformat()

        buffer.append(doc)

    # enviar buffer
    for item in buffer[:]:
        try:
            result = mqtt_client.publish(
                MQTT_TOPIC,
                json.dumps(item),
                qos=2
            )

            if result.rc == 0:
                print("Enviado:", item)

                # atualizar timestamp (converter de volta para datetime)
                last_timestamp = datetime.fromisoformat(item["Hour"])
                save_timestamp(last_timestamp)

                buffer.remove(item)

        except Exception as e:
            print("Erro:", e)

    time.sleep(1)