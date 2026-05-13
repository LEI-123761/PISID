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
import threading
import time

# Configuração
MQTT_TOPIC_SUB = "mazesound_4"
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

def check_reopen(ultima_msg_id):
    time.sleep(12) #mais tempo do q os alertas

    print("can i reopen after "+str(ultima_msg_id)+"?")
    thread_client = connect_to_mysql(MYSQL_CONFIG, attempts=utils.MYSQL_ATTEMPTS)
    thread_cursor = thread_client.cursor(buffered=True)
    # query = "SELECT ID FROM Mensagens WHERE Sensor = 'SOM' AND ID > %s ORDER BY ID ASC"
    thread_cursor.execute("SELECT ID FROM Mensagens WHERE Sensor = 'SOM' AND ID > "+str(ultima_msg_id))
    alertas = thread_cursor.fetchall()
    print("Alertas:",alertas)

    if(alertas == []):
        print("No more alertas")
        mqtt_client.publish(MQTT_TOPIC_ACT, "{Type:OpenAllDoor, Player:4}", qos=2)

    thread_cursor.close()

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
                comando = f'{{"Type": CloseAllDoor, "Player": {PLAYER_ID}}}'
                print(comando)
                mqtt_client.publish(MQTT_TOPIC_ACT, comando, qos=1)
                print(f"!!! [ATUADOR-SOM] Ruído Crítico: {id_msg}. Comando CloseAllDoor enviado.")

                (threading.Thread(target=check_reopen, args=(id_msg,))).start()
            ultima_msg_id = id_msg
        cursor.close()

        #adicionar uma verificacao se o ultimo msg foi ha mais q 3s segundos para abrir todas as portas
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
        mycursor.execute("SELECT IDMongo FROM Som WHERE IDMongo="+str(data.get("Id"))+" AND IDSimulacao="+str(ID_SIMULACAO))
        result= mycursor.fetchone()

        if(result == None):
            print("id", str(data.get("Id")))
            # insere a leitura de ruído na tabela Som
            mycursor.execute("""
                             INSERT INTO Som (IDSimulacao, IDMongo, Hora, Som)
                             VALUES (%s, %s, %s, %s)
                             """, (
                                 ID_SIMULACAO,
                                 data.get("Id"),
                                 data.get("Hour"),
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
