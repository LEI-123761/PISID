import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import validacoes as v

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    msg_sections= msg[1:-1].split(', ') #1:-1 por q tem "", mas verificar nos testes

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    registo["Hour"]= ((msg_sections[1].split("\""))[1])
    registo["Sound"]= float((msg_sections[2].split(":"))[1])

    if(v.sound_anomalo(registo, player)): #ver se e anomolo
        colecao= bd["sound_errors"]
    elif(v.sound_outlier(registo["Sound"], threshold_som, last_three)): #ver se e outlier
        colecao= bd["sound_outliers"]
    else: #cc e um valor valido
        registo["Sent"]= False
        colecao= bd["sounds_received"]

        last_three.append(registo["Sound"])
        if(len(last_three) == 4):
            del last_three[0]

    colecao.insert_one(registo)

##################Codigo Principal##################
#cliente MySQL
mysql_cliente= mysql.connector.connect(host="", user="", password="", database="maze") #preciso dos utlizadores para ligar me com as credenciais certas...
cursor= mysql_cliente.cursor()

threshold_som= cursor.execute("SELECT LimiarSom FROM Parametros WHERE IDSimulacao == ")

mysql_cliente.close()

#cliente Mongo
last_three= []
mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest")
bd= mongo_cliente["SensorData"]

#cliente MQTT
mqtt_cliente= mqtt.Client("sound_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazesound_4")
mqtt_cliente.loop_forever()