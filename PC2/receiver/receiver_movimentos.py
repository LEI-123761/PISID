# **DESCRICAO**
# receiver_movimentos.py
#
# Este script corre no PC2 (onde está o MySQL).
# Subscreve o tópico de movimentos no broker MQTT,
# insere cada movimento recebido no MySQL,
# e publica uma confirmação no tópico de feedback.
# O feedback.py no PC1 recebe essa confirmação e marca
# o documento original no MongoDB como Sent=True.


import paho.mqtt.client as mqtt
import mysql.connector
import json
import utils

from connection import connect_to_mysql

#configuração
MQTT_TOPIC_SUB = "pisid_mazemov_4"
# tópico onde publicamos confirmação após inserir no MySQL
MQTT_TOPIC_FB  = "pisid_feedback_4"
CLIENT_ID      = "pisid_receiver_movimentos"


MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.MOVES_USER,
    "password": utils.MOVES_PASSWORD,
    "database": utils.DATABASE 
}

#ligação MySQL persistente
# ligação aberta uma vez no arranque, mais eficiente do que
# abrir/fechar a cada mensagem
tentativas = utils.MYSQL_ATTEMPTS
mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=tentativas)
global ID_SIMULACAO

if mysqlclient:
    mycursor = mysqlclient.cursor()
    print("[MOV] Ligado ao MySQL")

    # obtém o ID da simulação activa, os inserts ficam associados a ela
    # se não houver simulação activa ao receber mensagens, essas são ignoradas
    ID_SIMULACAO = utils.get_id_simulacao(mycursor)

    if ID_SIMULACAO is None:
        print("[MOV] Aviso: sem simulação activa no arranque")

else: 
    print("[MOV] Erro: erro ao ligar a BD depois de ", tentativas, " tentativas")

# chamada automaticamente pelo paho quando chega uma mensagem
def on_message(client, userdata, msg):
    try:
        if ID_SIMULACAO is None:
            # Tenta obter id_simulacao novamente
            ID_SIMULACAO = utils.get_id_simulacao(mycursor)
            if ID_SIMULACAO is None:
                print("[MOV] Sem simulação activa, a ignorar mensagem")
                return

        # msg.payload são bytes → decode() → string → json.loads() → dicionário
        data = json.loads(msg.payload.decode())
        print(f"[MOV] Recebido: {data}")

        if mysqlclient is None:
            print("[MOV] Erro: Sem conexão a base de dados, a guardar dados localmente")

            with open("buffer.jsonl", "a") as file:
                file.write(json.dumps(data) + "\n")

            return

        # insere o movimento no MySQL
        # %s são placeholders protegidos contra SQL injection
        mycursor.execute("""
            INSERT INTO MedicoesPassagens (IDSimulacao, SalaOrigem, SalaDestino, Marsami, Status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ID_SIMULACAO,
            data.get("RoomOrigin"),
            data.get("RoomDestiny"),
            data.get("Marsami"),
            data.get("Status"),
        ))
        # commit confirma a transação
        mysqlclient.commit()

        # feedback publicado DEPOIS do commit
        # garante que Sent=True só é marcado quando os dados estão no MySQL
        feedback = {
            "collection": "moves_received",
            "id_seq":     data["id_seq"],
            "status":     "ok"
        }
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
        print(f"[MOV] Feedback enviado id_seq={data['id_seq']}")

    except Exception as e:
        print(f"[MOV] Erro: {e}")
        # rollback cancela transação incompleta
        # como feedback não foi publicado, Sent fica False
        # e o publisher reenvia a mensagem
        mysqlclient.rollback()

#callback ligação
# subscrição feita aqui dentro para ser refeita se o broker reiniciar
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MOV] Ligado ao broker: {client._host}")
        client.subscribe(MQTT_TOPIC_SUB, qos=2)
    else:
        print(f"[MOV] Erro ao ligar, rc={reason_code}")

#cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(utils.MQTT_BROKER, utils.MQTT_PORT)

print("[MOV] Receiver iniciado...")
mqtt_client.loop_forever()
