#**DESCRICAO**
# receiver_ruido.py
#
# Este script corre no PC2 (onde está o MySQL).
# Subscreve o tópico de ruído no broker MQTT,
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
MQTT_TOPIC_SUB = "pisid_mazesound_4"
MQTT_TOPIC_FB  = "pisid_feedback_4"
CLIENT_ID      = "pisid_receiver_ruido"

MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.MOVES_USER,
    "password": utils.MOVES_PASSWORD,
    "database": utils.DATABASE 
}

#ligação MySQL persistente
tentativas = utils.MYSQL_ATTEMPTS
mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=tentativas)

if mysqlclient:
    mycursor    = mysqlclient.cursor()
    print("[SOM] Ligado ao MySQL")

    # obtém o ID da simulação activa
    ID_SIMULACAO = utils.get_id_simulacao(mycursor)

    if ID_SIMULACAO is None:
        print("[SOM] Aviso: sem simulação activa no arranque")
else: 
    print("[MOV] Erro: erro ao ligar a BD depois de ", tentativas, " tentativas")

#callback mensagem
def on_message(client, userdata, msg):
    try:
        if ID_SIMULACAO is None:
            # Tenta obter id_simulacao novamente
            ID_SIMULACAO = utils.get_id_simulacao(mycursor)
            if ID_SIMULACAO is None:
                print("[SOM] Sem simulação activa, a ignorar mensagem")
                return

        data = json.loads(msg.payload.decode())
        print(f"[SOM] Recebido: {data}")

        # insere a leitura de ruído na tabela Som
        mycursor.execute("""
            INSERT INTO Som (IDSimulacao, Som)
            VALUES (%s, %s)
        """, (
            ID_SIMULACAO,
            data.get("Sound"),
        ))
        mysqlclient.commit()

        # feedback publicado após commit confirmado
        feedback = {
            "collection": "sounds_received",
            "id_seq":     data["id_seq"],
            "status":     "ok"
        }
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
        print(f"[SOM] Feedback enviado id_seq={data['id_seq']}")

    except Exception as e:
        print(f"[SOM] Erro: {e}")
        mysqlclient.rollback()

#callback ligação
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[SOM] Ligado ao broker: {client._host}")
        # QoS 1 para ruído — confirmação sem overhead do QoS 2
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
    else:
        print(f"[SOM] Erro ao ligar, rc={reason_code}")

#cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(utils.MQTT_BROKER, utils.MQTT_PORT)

print("[SOM] Receiver iniciado...")
mqtt_client.loop_forever()
