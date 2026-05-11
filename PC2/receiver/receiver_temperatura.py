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
MQTT_TOPIC_SUB = "mazetemp_4"
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
            print(f"[ATUADOR-TEMP] Analisando mensagem ID {id_msg}: {msg_texto}")
            msg_clean = msg_texto.lower()
            comando = None

            # 3. Procurar por "maxim" ou "minim" (sem acentos para evitar erros)
            if "máximo" in msg_clean:
                comando = f'{{"Type": AcOn, "Player": {PLAYER_ID}}}'
            elif "mínimo" in msg_clean:
                comando = f'{{"Type": AcOff, "Player": {PLAYER_ID}}}'

            if comando:
                # 4. Publicar o comando
                mqtt_client.publish(MQTT_TOPIC_ACT, comando, qos=1)
                # PRINT IMPORTANTE para veres no terminal:
                print(f"!!! [AC] COMANDO ENVIADO: {comando} para o alerta {id_msg}")

            ultima_msg_id = id_msg

        cursor.close()
    except Exception as e:
        print(f"[ATUADOR-TEMP] Erro ao verificar AC: {e}")

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

        #verificar q ID nao existe
        mycursor.execute("SELECT IDMongo FROM Temperatura WHERE IDMongo="+str(data.get("Id")))
        result= mycursor.fetchone()

        if(result == None):
            # insere a leitura de temperatura na tabela Temperatura
            mycursor.execute("""
                             INSERT INTO Temperatura (IDSimulacao, IDMongo, Hora, Temperatura)
                             VALUES (%s, %s, %s, %s)
                             """, (
                                 ID_SIMULACAO,
                                 data.get("Id"),
                                 data.get("Hour"),
                                 data.get("Temperature"),
                             ))
            mysqlclient.commit()
            print("[TEMP] Nova leitura inserida com IDTemperatura:", mycursor.lastrowid)
        else:
            print("[TEMP] Já existe, não foi inserido")

        # Verifica se o trigger disparou um alerta de temperatura
        check_atuadores_temp(mysqlclient, client)

        # feedback publicado após commit confirmado
        feedback = {
            "collection": "temps_received",
            "Id":     data["Id"],
            "status":     "ok"
        }
        client.publish(MQTT_TOPIC_FB, json.dumps(feedback), qos=1)
        print(f"[TEMP] Feedback enviado Id={data['Id']}")
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
