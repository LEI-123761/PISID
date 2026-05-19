import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import validacoes as v
import time

CLIENT_ID  = "pisid_filtro_som"

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    print("[SOM] Received", msg)
    msg_sections= msg[1:-1].split(', ')

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    registo["Hour"]= ((msg_sections[1][1:-1].split("\": \""))[1])
    registo["Sound"]= float((msg_sections[2].split(":"))[1])

    is_anomalo, razao= v.sound_anomalo(registo, player)
    if(is_anomalo): #ver se e anomolo
        registo["Motivo"]= razao
        colecao= bd["sound_errors"]
    elif(v.sound_outlier(registo["Sound"], threshold_som, last_three)): #ver se e outlier
        colecao= bd["sound_outliers"]
    else: #cc e um valor valido
        registo["Id"]= current_id[0]
        current_id[0]+= 1
        registo["Sent"]= False
        colecao= bd["sounds_received"]

        last_three.append(registo["Sound"])
        if(len(last_three) == 4):
            del last_three[0]

    colecao.insert_one(registo)

##################Codigo Principal##################
#cliente MySQL
connecting= False
while connecting == False:
    try:
        mysql_cliente= mysql.connector.connect(host="mysql_connection", user="mig_som", password="mig_som4", database="maze") #preciso dos utlizadores para ligar me com as credenciais certas...
        connecting= True
    except:
        print("Failed to connect, trying again...")
        time.sleep(1)

cursor= mysql_cliente.cursor()

try:
    cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Status='Correr' LIMIT 1")
    id_sim= cursor.fetchone()[0]
    cursor.execute("SELECT LimiarSom FROM Parametros WHERE IDSimulacao= "+str(id_sim))
    threshold_som= cursor.fetchone()[0]
except Exception as e:
    print("Exception ", e)
    threshold_som= 5

mysql_cliente.close()

#cliente Mongo
last_three= []
current_id= [1]
mongo_cliente= MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
bd= mongo_cliente["SensorData"]

#cliente MQTT
mqtt_cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, clean_session=True)
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("broker.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazesound_4")
mqtt_cliente.loop_forever()
