#**DESCRICAO**
# receiver_temperatura.py
#
# Este script corre no PC2 (onde está o MySQL).
# Subscreve o tópico de temperatura no broker MQTT,
# insere cada leitura recebida no MySQL,
# e publica uma confirmação no tópico de feedback.
# O feedback.py no PC1 recebe essa confirmação e marca
# o documento original no MongoDB como Sent=True.


import paho.mqtt.client as mqtt
import mysql.connector
import json

#configuração
MQTT_BROKER    = "broker.hivemq.com"
MQTT_PORT      = 1883
MQTT_TOPIC_SUB = "pisid_mazetemp_4"
MQTT_TOPIC_FB  = "pisid_feedback_4"
CLIENT_ID      = "pisid_receiver_temperatura"

MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     13306,
    "user":     "root",
    "password": "root",
    "database": "maze"
}

#ligação MySQL persistente
mysqlclient = mysql.connector.connect(**MYSQL_CONFIG)
mycursor    = mysqlclient.cursor()
print("[TEMP] Ligado ao MySQL")

# obtém o ID da simulação activa
mycursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Status='Correr' LIMIT 1")
row = mycursor.fetchone()
ID_SIMULACAO = row[0] if row else None

if ID_SIMULACAO is None:
    print("[TEMP] Aviso: sem simulação activa no arranque")

#callback mensagem
def on_message(client, userdata, msg):
    try:
        if ID_SIMULACAO is None:
            print("[TEMP] Sem simulação activa, a ignorar mensagem")
            return

        data = json.loads(msg.payload.decode())
        print(f"[TEMP] Recebido: {data}")

        # insere a leitura de temperatura na tabela Temperatura
        mycursor.execute("""
            INSERT INTO Temperatura (IDSimulacao, Temperatura)
            VALUES (%s, %s)
        """, (
            ID_SIMULACAO,
            data.get("Temperature"),
        ))
        mysqlclient.commit()
        # feedback publicado após commit confirmado
        feedback = {
            "collection": "temps_received",
            "id_seq":     data["id_seq"],
            "status":     "ok"
        }
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
        print(f"[TEMP] Feedback enviado id_seq={data['id_seq']}")

    except Exception as e:
        print(f"[TEMP] Erro: {e}")
        mysqlclient.rollback()

#callback ligação
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[TEMP] Ligado ao broker | session present: {flags['session present']}")
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
    else:
        print(f"[TEMP] Erro ao ligar, rc={rc}")

#cliente MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

print("[TEMP] Receiver iniciado...")
mqtt_client.loop_forever()