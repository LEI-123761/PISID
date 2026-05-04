import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import threading
import validacoes as v

def check_occupation_origin(origin_index):
    time.sleep(3) #espera 3 segs
    origem= contador_marsamis[origin_index]
    if(origem[0] == origem[1]): #se nao sairam/entrarem marsamis
        for i in range(0, 3):
            mqtt_cliente.publish("pisid_mazeact", "{Type:Score, Player:4, Room:"+str((origin_index+1))+"}", 2)
            #atualizar algum contador para a sala?

    #abrir portas depois de disparar as 3 vezes ou se nao disparou
    mqtt_cliente.publish("pisid_mazeact", "{Type:OpenAllDoor, Player:4}", 2) #mudar para abrir todas as portas da sala

def check_occupation_destiny(destiny_index):
    time.sleep(3) #espera 3 segs
    destino= contador_marsamis[destiny_index]
    if(destino[0] == destino[1]): #se nao sairam marsamis
        for i in range(0, 3):
            mqtt_cliente.publish("pisid_mazeact", "{Type:Score, Player:4, Room:"+str((destiny_index+1))+"}", 2)
            #atualizar algum contador para a sala?

    #abrir portas depois de disparar as 3 vezes ou se nao disparou
    mqtt_cliente.publish("pisid_mazeact", "{Type:OpenAllDoor, Player:4}", 2) #mudar para abrir todas as portas da sala

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

    if(v.move_anomalo(registo, player, num_marsamis, last_room[player-1]), num_salas): #ver se e anomolo
        colecao= bd["move_errors"]
        colecao.insert_one(registo)
        return

    #cc e um valor valido
    registo["Sent"]= False
    colecao= bd["moves_received"]
    colecao.insert_one(registo)

    #atualizar contadores e tratamento de marsamis
    last_room[player-1]= registo["RoomOrigin"]

    origin_room_index= registo["RoomOrigin"]-1 #-1 como index
    destiny_room_index= registo["RoomDestiny"]-1

    destino= contador_marsamis[destiny_room_index]
    if(registo["Marsami"]%2 != 0): #se marsami for odd
        if(origin_room_index != -1): #se sala nao for 0
            origem= contador_marsamis[origin_room_index]
            origem[0]-= 1

            if(origem[0] == origem[1]):
                mqtt_cliente.publish("pisid_mazeact", "{Type:CloseAllDoor, Player:4}", 2) #mudar para fechar todas as portas de uma sala
                (threading.Thread(target=check_occupation_origin(), args=(origin_room_index))).start()

        destino[0]+= 1
        if(destino[0] == destino[1]):
            mqtt_cliente.publish("pisid_mazeact", "{Type:CloseAllDoor, Player:4}", 2) #mudar para fechar todas as portas de uma sala
            (threading.Thread(target=check_occupation_destiny(), args=(destiny_room_index))).start()
    else:
        if(origin_room_index != -1):
            origem= contador_marsamis[origin_room_index]
            origem[1]-= 1

            if(origem[0] == origem[1]):
                mqtt_cliente.publish("pisid_mazeact", "{Type:CloseAllDoor, Player:4}", 2) #mudar para fechar todas as portas de uma sala
            (threading.Thread(target=check_occupation_origin(), args=(origin_room_index))).start()

        destino[1]+= 1
        if(destino[0] == destino[1]):
            mqtt_cliente.publish("pisid_mazeact", "{Type:CloseAllDoor, Player:4}", 2) #mudar para fechar todas as portas de uma sala
            (threading.Thread(target=check_occupation_destiny(), args=(destiny_room_index))).start()

##################Codigo Principal##################
#cliente MySQL (Cloud)
mysql_cliente= mysql.connector.connect(host="194.210.86.10", user="aluno", password="aluno", database="maze")
cursor= mysql_cliente.cursor()

num_salas= cursor.execute("SELECT numberrooms FROM SetupMaze")
num_marsamis= cursor.execute("SELECT numbermarsamis FROM SetupMaze")

mysql_cliente.close()

contador_marsamis= []
for i in num_salas:
    contador_marsamis.append((0, 0)) #((odd, even), ...)

last_room= []
for j in num_marsamis:
    last_room.append(0)

#cliente Mongo
mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest")
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client("moves_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.subscribe("pisid_mazemov_4")
mqtt_cliente.loop_forever()