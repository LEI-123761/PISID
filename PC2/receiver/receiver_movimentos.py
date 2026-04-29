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

#configuração
MQTT_BROKER    = "broker.hivemq.com"
MQTT_PORT      = 1883
MQTT_TOPIC_SUB = "pisid_mazemov_4"
# tópico onde publicamos confirmação após inserir no MySQL
MQTT_TOPIC_FB  = "pisid_feedback_4"
CLIENT_ID      = "pisid_receiver_movimentos"


MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     13306,
    "user":     "root",
    "password": "root",
    "database": "maze"
}

#ligação MySQL persistente
# ligação aberta uma vez no arranque, mais eficiente do que
# abrir/fechar a cada mensagem
mysqlclient = mysql.connector.connect(**MYSQL_CONFIG)
mycursor    = mysqlclient.cursor()
print("[MOV] Ligado ao MySQL")

# obtém o ID da simulação activa, os inserts ficam associados a ela
# se não houver simulação activa, mensagens são ignoradas
mycursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Status='Correr' LIMIT 1")
row = mycursor.fetchone()
ID_SIMULACAO = row[0] if row else None

if ID_SIMULACAO is None:
    print("[MOV] Aviso: sem simulação activa no arranque")

# chamada automaticamente pelo paho quando chega uma mensagem
def on_message(client, userdata, msg):
    try:
        if ID_SIMULACAO is None:
            print("[MOV] Sem simulação activa, a ignorar mensagem")
            return

        # msg.payload são bytes → decode() → string → json.loads() → dicionário
        data = json.loads(msg.payload.decode())
        print(f"[MOV] Recebido: {data}")

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
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MOV] Ligado ao broker | session present: {flags['session present']}")
        client.subscribe(MQTT_TOPIC_SUB, qos=2)
    else:
        print(f"[MOV] Erro ao ligar, rc={rc}")

#cliente MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

print("[MOV] Receiver iniciado...")
mqtt_client.loop_forever()