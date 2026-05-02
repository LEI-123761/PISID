import paho.mqtt.client as mqtt
from pymongo import MongoClient
import validacoes as v

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    msg_sections= msg[1:-1].split(', ')

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    registo["Hour"]= ((msg_sections[1].split("\""))[1])
    registo["Temperature"]= float((msg_sections[2].split(":"))[1])

    if(v.temp_anomalo(registo, player)): #ver se e anomolo
        colecao= bd["temp_errors"]
    elif(v.temp_outlier(registo)): #ver se e outlier
        colecao= bd["temp_outliers"]
    else: #cc e um valor valido
        registo["Sent"]= False
        colecao= bd["temps_received"]

    colecao.insert_one(registo)

##################Codigo Principal##################
#cliente Mongo
mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest")
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client("temp_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazetemp_4")
mqtt_cliente.loop_start()