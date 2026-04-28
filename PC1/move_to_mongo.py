import paho.mqtt.client as mqtt
import pymongo
import validacoes as v

def receive_msg(client, userdata, message):
    msg= message.payload
    registo= {"Marsami": msg["Marsami"], "RoomOrigin": msg["RoomOrigin"],
              "RoomDestiny": msg["RoomDestiny"], "Status": msg["Status"]}

    if(v.move_anomalo(registo)): #ver se e anomolo
        colecao= bd["sensor_errors"] #manter junto ou separar? Pensava q era manter mas estamos a separar no relatorio
        colecao.insert_one(registo)
        return

    #cc e um valor valido
    registo["Sent"]= False
    colecao= bd["moves_received"]
    colecao.insert_one(registo)

    #atualizar contador
    origin_room_num= 0 #convert str to int
    destiny_room_num= 0
    origem= contador_marsamis[origin_room_num]
    destino= contador_marsamis[destiny_room_num]
    if(False): #se marsami for odd
        origem[0]-= 1
        destino[0]+= 1
    else:
        origem[1]-= 1
        destino[1]+= 1

    #tratamento de marsamis
    if(origem[0] == origem[1]):
        #close all doors
        #wait x secs
        #check again by reading mongo
        #if still equal disparar 3 vezes
        #else open doors
        pass
    elif(destino[0] == destino[1]):
        #close all doors
        #wait x secs
        #check again by reading mongo
        #if still equal disparar 3 vezes
        #else open doors
        pass

##################Codigo Principal##################
contador_marsamis= [] #falta implementar esta parte

num_salas= 4 #ler dados da cloud
for i in num_salas:
    contador_marsamis.append((0, 0))

#cliente Mongo
mongo_cliente= pymongo.MongoClient("") #q endereco e q usamos?
bd= mongo_cliente["SensorData"] #nome da base de dados

#cliente MQTT
mqtt_cliente= mqtt.Client("moves_mongo")
mqtt_cliente.on_message= receive_msg

mqtt_cliente.connect("www.hivemq.com", 1883)
mqtt_cliente.loop_start()

mqtt_cliente.subscribe("pisid_mazemov_4")