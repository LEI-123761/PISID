import paho.mqtt.client as mqtt
from pymongo import MongoClient
import time
import validacoes as v

def receive_msg(client, userdata, message):
    msg= message.payload
    registo= {"Marsami": msg["Marsami"], "RoomOrigin": msg["RoomOrigin"],
              "RoomDestiny": msg["RoomDestiny"], "Status": msg["Status"]}

    if(v.move_anomalo(registo, msg["Player"]), last_room): #ver se e anomolo
        colecao= bd["move_errors"]
        colecao.insert_one(registo)
        return

    #cc e um valor valido
    registo["Sent"]= False
    colecao= bd["moves_received"]
    colecao.insert_one(registo)

    #atualizar contadores
    last_room[int(msg["Marsami"])]= int(msg["RoomOrigin"])

    origin_room_index= int(msg["RoomOrigin"]) - 1 #-1 como index
    destiny_room_index= int(msg["RoomDestiny"]) - 1
    destino= contador_marsamis[destiny_room_index]
    if(False): #se marsami for odd
        if(origin_room_index != -1):
            origem= contador_marsamis[origin_room_index]
            origem[0]-= 1

        destino[0]+= 1
    else:
        if(origin_room_index != -1):
            origem= contador_marsamis[origin_room_index]
            origem[1]-= 1

        destino[1]+= 1

    #tratamento de marsamis
    if(origem[0] == origem[1]):
        #close all doors

        time.sleep(3) #espera 3 segs
        if(origem[0] == origem[1]): #se nao sairam marsamis
            #disparar 3 vezes
            pass
        else:
            #else open doors
            pass
    elif(destino[0] == destino[1]):
        #close all doors

        time.sleep(3) #espera 3 segs
        if(destino[0] == destino[1]): #se nao sairam marsamis
            #disparar 3 vezes
            pass
        else:
            #else open doors
            pass

##################Codigo Principal##################
#cliente MySQL

contador_marsamis= []
num_salas= 4 #ler dados da cloud
for i in num_salas:
    contador_marsamis.append((0, 0))

last_room= []
num_marsamis= 4
for j in num_marsamis:
    last_room.append(0)

#cliente Mongo
mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest") #
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client("moves_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazemov_4")
mqtt_cliente.loop_start()