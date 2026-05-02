import paho.mqtt.client as mqtt
from pymongo import MongoClient
import time
import validacoes as v

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    msg_sections= msg[1:-1].split(', ') #1:-1 por q tem "", mas verificar nos testes

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    registo["Marsami"]= int((msg_sections[1].split(":"))[1])
    registo["RoomOrigin"]= int((msg_sections[2].split(":"))[1])
    registo["RoomDestiny"]= int((msg_sections[3].split(":"))[1])
    registo["Status"]= int((msg_sections[4].split(":"))[1])

    if(v.move_anomalo(registo, player, last_room[player-1])): #ver se e anomolo
        colecao= bd["move_errors"]
        colecao.insert_one(registo)
        return

    #cc e um valor valido
    registo["Sent"]= False
    colecao= bd["moves_received"]
    colecao.insert_one(registo)

    #atualizar contadores
    last_room[player-1]= registo["RoomOrigin"]

    origin_room_index= registo["RoomOrigin"]-1 #-1 como index
    destiny_room_index= registo["RoomDestiny"]-1
    destino= contador_marsamis[destiny_room_index]
    if(False): #se marsami for odd
        if(origin_room_index != -1): #se sala nao for 0
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
        origem= contador_marsamis[origin_room_index]
        if(origem[0] == origem[1]): #se nao sairam marsamis
            #disparar 3 vezes
            pass
        else:
            #else open doors
            pass
    elif(destino[0] == destino[1]):
        #close all doors

        time.sleep(3) #espera 3 segs
        destino= contador_marsamis[destiny_room_index]
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