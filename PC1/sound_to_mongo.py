import paho.mqtt.client as mqtt
from pymongo import MongoClient
import validacoes as v

def receive_msg(client, userdata, message):
    msg= message.payload.decode("utf-8")

    #set up registo
    registo= {"Hour": msg["Hour"], "Sound": msg["Sound"]}
    player= 0

    if(v.sound_anomalo(registo, player)): #ver se e anomolo
        colecao= bd["sound_errors"]
    elif(v.sound_outlier(registo)): #ver se e outlier
        colecao= bd["sound_outliers"]
    else: #cc e um valor valido
        registo["Sent"]= False
        colecao= bd["sounds_received"]

    colecao.insert_one(registo)

##################Codigo Principal##################
#cliente Mongo
mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest")
bd= mongo_cliente["SensorData"]

#cliente MQTT
mqtt_cliente= mqtt.Client("sound_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazesound_4")
mqtt_cliente.loop_start()