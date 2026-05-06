import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import validacoes as v
import time

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    print("RECEIVED ", msg)
    print("threshold: ", threshold_temp)
    msg_sections= msg[1:-1].split(', ')

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    registo["Hour"]= ((msg_sections[1][1:-1].split("\": \""))[1])
    registo["Temperature"]= float((msg_sections[2].split(":"))[1])

    is_anomalo, razao= v.temp_anomalo(registo, player)
    if(is_anomalo): #ver se e anomolo
        registo["Motivo"]= razao
        colecao= bd["temp_errors"]
    elif(v.temp_outlier(registo["Temperature"], threshold_temp, last_three)): #ver se e outlier
        colecao= bd["temp_outliers"]
    else: #cc e um valor valido
        registo["Id"]= current_id[0]
        registo["Sent"]= False
        colecao= bd["temps_received"]

        last_three.append(registo["Temperature"])
        if(len(last_three) == 4):
            del last_three[0]

    colecao.insert_one(registo)
    current_id[0]+= 1

##################Codigo Principal##################
#cliente MySQL
connecting= False
while connecting == False:
    try:
        mysql_cliente= mysql.connector.connect(host="mysql_connection", user="mig_temperatura", password="mig_temperatura4", database="maze")
        connecting= True
    except:
        print("Failed to connect, trying again...")
        time.sleep(1)

cursor= mysql_cliente.cursor()

try:
    cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Status='Correr' LIMIT 1")
    id_sim= cursor.fetchone()[0]
    cursor.execute("SELECT LimiarTemperatura FROM Parametros WHERE IDSImulacao= "+str(id_sim))
    threshold_temp= cursor.fetchone()[0]
except Exception as e:
    print("Exception ", e)
    threshold_temp= 90

mysql_cliente.close()

#cliente Mongo
last_three= []
current_id= [1]
mongo_cliente= MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client()
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("broker.hivemq.com", 1883)
# mqtt_cliente.connect("broker.mqttdashboard.com", 1883)
mqtt_cliente.subscribe("pisid_mazetemp_4")
mqtt_cliente.loop_forever()