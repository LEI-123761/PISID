import mysql.connector
from pymongo import MongoClient
import paho.mqtt.client as mqtt

# mongo_cliente= MongoClient("30001:27017, 30002:27017, 30003:27017", replicaSet="rs0", readPreference="nearest")
# mongo_cliente= MongoClient("mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=rs0")
mongo_cliente= MongoClient("mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
print("connected")
bd= mongo_cliente["SensorData"]
print(bd)
print("")
colecao= bd["sound_errors"]
print(colecao)

registo= {"campo1":"valo1", "campo2": 3}
response= colecao.insert_one(registo)
print("inserted")

# print("hello world")
