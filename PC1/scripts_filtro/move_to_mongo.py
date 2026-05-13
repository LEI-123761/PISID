import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import threading
import validacoes as v

def check_occupation_origin(origin_index, closed):
    print("Checking room origin")
    time.sleep(3) #espera 3 segs

    origem= contador_marsamis[origin_index]
    print("Origem contador:", origem)
    if(origem[0] == origem[1]): #se nao sairam/entrarem marsamis
        print("Scoring")
        for i in range(0, 3):
            mqtt_cliente.publish("pisid_mazeact", "{Type:Score, Player:4, Room:"+str((origin_index+1))+"}", 2)
            tentativa_gatilho[origin_index]+= 1

    print("abrir")
    #abrir portas depois de disparar as 3 vezes ou se nao disparou
    for c in closed: #abrir todas as portas da sala
        mqtt_cliente.publish("pisid_mazeact",
                             "{Type:OpenDoor, Player:4, "
                             "RoomOrigin:"+str(c[0])+", RoomDestiny:"+str(c[1])+"}", 2)

def check_occupation_destiny(destiny_index, closed):
    print("Checking room destiny")
    time.sleep(3) #espera 3 segs

    destino= contador_marsamis[destiny_index]
    print("Destino contador:", destino)
    if(destino[0] == destino[1]): #se nao sairam marsamis
        print("Scoring")
        for i in range(0, 3):
            mqtt_cliente.publish("pisid_mazeact", "{Type:Score, Player:4, Room:"+str((destiny_index+1))+"}", 2)
            tentativa_gatilho[destiny_index]+= 1

    print("abrir")
    #abrir portas depois de disparar as 3 vezes ou se nao disparou
    for c in closed: #abrir todas as portas da sala
        mqtt_cliente.publish("pisid_mazeact",
                             "{Type:OpenDoor, Player:4, "
                             "RoomOrigin:"+str(c[0])+", RoomDestiny:"+str(c[1])+"}", 2)

def close_room(sala):
    cursor.execute("SELECT RoomB FROM Corridor WHERE RoomA="+str(sala))
    destinos= cursor.fetchall()

    cursor.execute("SELECT RoomA FROM Corridor WHERE RoomB="+str(sala))
    origems= cursor.fetchall()

    closed= []
    for d in destinos:
        mqtt_cliente.publish("pisid_mazeact",
                             "{Type:CloseDoor, Player:4, "
                             "RoomOrigin:"+str(sala)+", RoomDestiny:"+str(d[0])+"}", 2)
        closed.append([sala, d[0]])

    for o in origems:
        mqtt_cliente.publish("pisid_mazeact",
                             "{Type:CloseDoor, Player:4, "
                             "RoomOrigin:"+str(o[0])+", RoomDestiny:"+str(sala)+"}", 2)
        closed.append([o[0], sala])

    return closed

def receive_msg(client, userdata, message):
    #set up registo
    msg= message.payload.decode("utf-8")
    print("RECEIVED: ", msg)
    msg_sections= msg[1:-1].split(', ') #1:-1 por q tem "", mas verificar nos testes

    player= int((msg_sections[0].split(":"))[1])
    registo= {}
    marsami= int((msg_sections[1].split(":"))[1])
    registo["Marsami"]= marsami
    registo["RoomOrigin"]= int((msg_sections[2].split(":"))[1])
    registo["RoomDestiny"]= int((msg_sections[3].split(":"))[1])
    registo["Status"]= int((msg_sections[4].split(":"))[1])

    cursor.execute("SELECT active FROM Corridor WHERE RoomA="+str(registo["RoomOrigin"])+" AND RoomB="+str(registo["RoomDestiny"]))
    active= cursor.fetchone()
    is_anomalo, razao= v.move_anomalo(registo, player, num_marsamis, last_room[marsami-1], num_salas, active)
    if(is_anomalo): #ver se e anomolo
        registo["Motivo"]= razao
        colecao= bd["move_errors"]
        colecao.insert_one(registo)
        return

    #cc e um valor valido
    registo["Id"]= current_id[0]
    registo["Sent"]= False
    colecao= bd["moves_received"]
    colecao.insert_one(registo)
    current_id[0]+= 1

    #atualizar contadores e tratamento de marsamis
    last_room[marsami-1]= registo["RoomDestiny"]

    origin_room_index= registo["RoomOrigin"]-1 #-1 como index
    destiny_room_index= registo["RoomDestiny"]-1

    destino= contador_marsamis[destiny_room_index]
    if(registo["Marsami"]%2 != 0): #se marsami for odd
        if(origin_room_index != -1): #se sala nao for 0
            origem= contador_marsamis[origin_room_index]
            origem[0]-= 1

            if((origem[0] == origem[1]) and (tentativa_gatilho[origin_room_index] != 3) and (origem[0] != 0)):
                print("Origem Igual:", origem)
                closed= close_room(registo["RoomOrigin"]) #fechar todos as corredores de uma sala
                (threading.Thread(target=check_occupation_origin, args=(origin_room_index, closed,))).start()

        destino[0]+= 1
        if(destino[0] == destino[1] and (tentativa_gatilho[destiny_room_index] != 3) and (destino[0] != 0) and (origin_room_index != -1)):
            print("Destino Igual:", destino)
            closed= close_room(registo["RoomDestiny"]) #fechar todos as corredores de uma sala
            (threading.Thread(target=check_occupation_destiny, args=(destiny_room_index, closed,))).start()
    else:
        if(origin_room_index != -1):
            origem= contador_marsamis[origin_room_index]
            origem[1]-= 1

            if(origem[0] == origem[1] and (tentativa_gatilho[origin_room_index] != 3) and (origem[0] != 0)):
                print("Origem Igual:", origem)
                closed= close_room(registo["RoomOrigin"]) #fechar todos as corredores de uma sala
                (threading.Thread(target=check_occupation_origin, args=(origin_room_index, closed,))).start()

        destino[1]+= 1
        if(destino[0] == destino[1] and (tentativa_gatilho[destiny_room_index] != 3) and (destino[0] != 0) and (origin_room_index != -1)):
            print("Destino Igual:", destino)
            closed= close_room(registo["RoomDestiny"]) #fechar todos as corredores de uma sala
            (threading.Thread(target=check_occupation_destiny, args=(destiny_room_index, closed,))).start()

##################Codigo Principal##################
#cliente MySQL (Cloud)
mysql_cliente= mysql.connector.connect(host="194.210.86.10", user="aluno", password="aluno", database="maze")
cursor= mysql_cliente.cursor()

try:
    cursor.execute("SELECT numberrooms FROM SetupMaze")
    num_salas= cursor.fetchone()[0]
    cursor.execute("SELECT numbermarsamis FROM SetupMaze")
    num_marsamis= cursor.fetchone()[0]

except Exception as e:
    print("Exception ", e)
    num_salas= 50
    num_marsamis= 50

# mysql_cliente.close()

contador_marsamis= []
tentativa_gatilho= []
for i in range(0, num_salas):
    contador_marsamis.append([0, 0]) #([odd, even], ...)
    tentativa_gatilho.append(0)

last_room= []
for j in range(0, num_marsamis):
    last_room.append(0)

#cliente Mongo
current_id= [1]
mongo_cliente= MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client()
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("broker.hivemq.com", 1883)
# mqtt_cliente.connect("broker.mqttdashboard.com", 1883)
mqtt_cliente.subscribe("pisid_mazemov_4")
mqtt_cliente.loop_forever()