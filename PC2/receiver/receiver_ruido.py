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

# Configuração
MQTT_TOPIC_SUB = "pisid_mazesound_4"
MQTT_TOPIC_FB  = "pisid_feedback_4"
MQTT_TOPIC_ACT = "pisid_mazeact"
CLIENT_ID      = "pisid_receiver_ruido"
PLAYER_ID      = 4

MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.SOUNDS_USER,
    "password": utils.SOUNDS_PASSWORD,
    "database": utils.DATABASE
}

mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=utils.MYSQL_ATTEMPTS)
ultima_msg_id = 0

if mysqlclient:
    mycursor = mysqlclient.cursor()
    mycursor.execute("SELECT MAX(ID) FROM Mensagens")
    res = mycursor.fetchone()[0]
    ultima_msg_id = res if res is not None else 0
    print(f"[SOM] A monitorizar alertas a partir do ID: {ultima_msg_id}")
    ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)

def check_atuadores_som(mysql_conn, mqtt_client):
    global ultima_msg_id
    try:
        cursor = mysql_conn.cursor(buffered=True)
        query = "SELECT ID, Msg FROM Mensagens WHERE Sensor = 'SOM' AND ID > %s ORDER BY ID ASC"
        cursor.execute(query, (ultima_msg_id,))
        alertas = cursor.fetchall()

        for id_msg, msg_texto in alertas:
            print(f"[ATUADOR-SOM] Analisando mensagem ID {id_msg}: {msg_texto}")
            if "máximo" in msg_texto.lower():
                comando = {"Type": "CloseAllDoor", "Player": PLAYER_ID}
                mqtt_client.publish(MQTT_TOPIC_ACT, json.dumps(comando), qos=1)
                print(f"!!! [ATUADOR-SOM] Ruído Crítico: {id_msg}. Comando CloseAllDoor enviado.")
            ultima_msg_id = id_msg
        cursor.close()
    except Exception as e:
        print(f"[ATUADOR-SOM] Erro: {e}")

def on_message(client, userdata, msg):
    global ID_SIMULACAO
    try:
        if ID_SIMULACAO is None:
            # Tenta obter id_simulacao novamente
            ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)
            if ID_SIMULACAO is None:
                print("[SOM] Sem simulação activa, a ignorar mensagem")
                return

        data = json.loads(msg.payload.decode())
        print(f"[SOM] Recebido: {data}")

        #verificar q ID nao existe
        mycursor.execute("SELECT IDSom FROM Som WHERE IDSom="+str(data.get("Id")))
        result= mycursor.fetchone()

        if(result == None):
            # insere a leitura de ruído na tabela Som
            mycursor.execute("""
                             INSERT INTO Som (IDSimulacao, Som)
                             VALUES (%s, %s)
                             """, (
                                 ID_SIMULACAO,
                                 data.get("Sound"),
                             ))
            mysqlclient.commit()
            print("[SOM] Nova leitura inserida com IDSom:", mycursor.lastrowid)
        else:
            print("[SOM] Já existe, não foi inserido")

        # Verifica se o trigger disparou um alerta de som
        check_atuadores_som(mysqlclient, client)

        # feedback publicado após commit confirmado
        feedback = {
            "collection": "sounds_received",
            "Id":     data["Id"],
            "status":     "ok"
        }
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
        print(f"[SOM] Feedback enviado Id={data['Id']}")
    except Exception as e:
        print(f"[SOM] Erro: {e}")
        mysqlclient.rollback()

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        client.subscribe(MQTT_TOPIC_SUB, qos=1)

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(utils.MQTT_BROKER, utils.MQTT_PORT)
mqtt_client.loop_forever()
