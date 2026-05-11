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
import time
from connection import connect_to_mysql

# Configuração
MQTT_TOPIC_SUB = "pisid_mazetemp_4"
MQTT_TOPIC_FB  = "pisid_feedback_4"
MQTT_TOPIC_ACT = "pisid_mazeact"
CLIENT_ID      = "pisid_receiver_temperatura"
PLAYER_ID      = 4

MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.TEMPS_USER,
    "password": utils.TEMPS_PASSWORD,
    "database": utils.DATABASE
}

# Ligação MySQL persistente
tentativas = utils.MYSQL_ATTEMPTS
mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=tentativas)

# Variável para controlo de mensagens processadas
ultima_msg_id = 0

if mysqlclient:
    mycursor = mysqlclient.cursor()
    print("[TEMP] Ligado ao MySQL")

    # Sincronização: Começa a partir do último alerta já existente na BD
    mycursor.execute("SELECT MAX(ID) FROM Mensagens")
    res = mycursor.fetchone()[0]
    ultima_msg_id = res if res is not None else 0
    print(f"[TEMP] A monitorizar alertas a partir do ID: {ultima_msg_id}")

    ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)
else:
    print("[TEMP] Erro crítico na ligação à BD")

def check_atuadores_temp(mysql_conn, mqtt_client):
    global ultima_msg_id
    try:
        # 1. Usar um cursor buffered para garantir que lemos tudo
        cursor = mysql_conn.cursor(buffered=True)

        # 2. Forçar um SELECT fresco na tabela Mensagens
        query = "SELECT ID, Msg FROM Mensagens WHERE Sensor = 'TEMP' AND ID > %s ORDER BY ID ASC"
        cursor.execute(query, (ultima_msg_id,))
        alertas = cursor.fetchall()

        for id_msg, msg_texto in alertas:
            msg_clean = msg_texto.lower()
            comando_json = None

            # 3. Procurar por "maxim" ou "minim" (sem acentos para evitar erros)
            if "maxim" in msg_clean:
                comando_json = {"Type": "AcOn", "Player": PLAYER_ID}
            elif "minim" in msg_clean:
                comando_json = {"Type": "AcOff", "Player": PLAYER_ID}

            if comando_json:
                # 4. Publicar o comando
                mqtt_client.publish(MQTT_TOPIC_ACT, json.dumps(comando_json), qos=1)
                # PRINT IMPORTANTE para veres no terminal:
                print(f"!!! [AC] COMANDO ENVIADO: {comando_json['Type']} para o alerta {id_msg}")

            ultima_msg_id = id_msg

        cursor.close()
    except Exception as e:
        print(f"[ATUADOR-TEMP] Erro ao verificar AC: {e}")

def on_message(client, userdata, msg):
    global ID_SIMULACAO
    # ADICIONA ESTA LINHA PARA TESTE:
    print(f"DEBUG: Recebi algo no tópico {msg.topic}: {msg.payload.decode()}")
    try:
        print("chegou ate aqui0")
        if ID_SIMULACAO is None:
            ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)
            if ID_SIMULACAO is None: return
        print("chegou ate aqui1")
        data = json.loads(msg.payload.decode())
        mycursor.execute("INSERT INTO Temperatura (IDSimulacao, Temperatura) VALUES (%s, %s)",
                         (ID_SIMULACAO, data.get("Temperature")))
        mysqlclient.commit()
        print("chegou ate aqui2")
        # Verifica se o trigger disparou um alerta de temperatura
        time.sleep(0.5)
        check_atuadores_temp(mysqlclient, client)
        print("chegou ate aqui3")
        feedback = {"collection": "temps_received", "id_seq": data["id_seq"], "status": "ok"}
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
    except Exception as e:
        print(f"[TEMP] Erro: {e}")
        mysqlclient.rollback()

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
        print(f"[TEMP] Subscreveu {MQTT_TOPIC_SUB}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(utils.MQTT_BROKER, utils.MQTT_PORT)
mqtt_client.loop_forever()
