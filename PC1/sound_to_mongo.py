import paho.mqtt.client as mqtt
import pymongo
import validacoes as v

def receive_msg(client, userdata, message):
    msg= message.payload
    registo= {"Hour": msg["Hour"], "Sound": msg["Sound"]}

    if(v.sound_anomalo(registo)): #ver se e anomolo
        colecao= bd["sensor_errors"]
    elif(v.sound_outlier(registo)): #ver se e outlier
        colecao= bd["outliers"]
    else: #cc e um valor valido
        registo["Sent"]= False
        colecao= bd["sounds_received"]

    colecao.insert_one(registo)

##################Codigo Principal##################
#cliente Mongo
mongo_cliente= pymongo.MongoClient("") #q endereco e q usamos?
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client("sound_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.loop_start()

mqtt_cliente.subscribe("pisid_mazesound_4")