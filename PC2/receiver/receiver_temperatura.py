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
import utils
from connection import connect_to_mysql

#configuração
MQTT_TOPIC_SUB = "pisid_mazetemp_4"
MQTT_TOPIC_FB  = "pisid_feedback_4"
CLIENT_ID      = "pisid_receiver_temperatura"

MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.MOVES_USER,
    "password": utils.MOVES_PASSWORD,
    "database": utils.DATABASE 
}

#ligação MySQL persistente
mysqlclient = connect_to_mysql(MYSQL_CONFIG)

if mysqlclient:
    mycursor    = mysqlclient.cursor()
    print("[TEMP] Ligado ao MySQL")

    # obtém o ID da simulação activa
    ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)

    if ID_SIMULACAO is None:
        print("[TEMP] Aviso: sem simulação activa no arranque")

else: 
    print("[MOV] Erro: erro ao ligar a BD depois de ", tentativas, " tentativas")

#callback mensagem
def on_message(client, userdata, msg):
    global ID_SIMULACAO
    try:
        if ID_SIMULACAO is None:
            # Tenta obter id_simulacao novamente
            ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)
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
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[TEMP] Ligado ao broker: {client._host}")
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
    else:
        print(f"[TEMP] Erro ao ligar, rc={rc}")

#cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(utils.MQTT_BROKER, utils.MQTT_PORT)

print("[TEMP] Receiver iniciado...")
mqtt_client.loop_forever()
