import paho.mqtt.client as mqtt
import mysql.connector
import json
import utils
import time.sleep as sleep

from connection import connect_to_mysql

MYSQL_CONFIG = {
    "host":     utils.HOST,
    "user":     utils.MOVES_USER,
    "password": utils.MOVES_PASSWORD,
    "database": utils.DATABASE 
}

tentativas = utils.MYSQL_ATTEMPTS
mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=tentativas)
ID_SIMULACAO = None

if mysqlclient:
    mycursor = mysqlclient.cursor()
    print("[MOV] Ligado ao MySQL")

    # obtém o ID da simulação activa, os inserts ficam associados a ela
    # se não houver simulação activa ao receber mensagens, essas são ignoradas
    ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)

    if ID_SIMULACAO is None:
        print("[MOV] Aviso: sem simulação activa no arranque")

else: 
    print("[MOV] Erro: erro ao ligar a BD depois de ", tentativas, " tentativas")


while True:
    cloud= mysql.connector.connect(host="194.210.86.10", user="aluno", password="aluno", database="maze")
    cloud_cursor= cloud.cursor()

    cloud_cursor.execute("SELECT normaltemperature FROM SetupMaze")
    norm_temp= cloud_cursor.fetchone()[0]
    cloud_cursor.execute("SELECT normalnoise FROM SetupMaze")
    norm_noise= cloud_cursor.fetchone()[0]
    cloud_cursor.execute("SELECT temperaturevarhightoleration FROM SetupMaze")
    temperatura_max= cloud_cursor.fetchone()[0] + norm_temp
    cloud_cursor.execute("SELECT temperaturevarlowtoleration FROM SetupMaze")
    temperatura_min= norm_temp - cloud_cursor.fetchone()[0]
    cloud_cursor.execute("SELECT noisevartoleration FROM SetupMaze")
    noise_max= cloud_cursor.fetchone()[0] + norm_noise

    mysqlclient.execute("ALTER TABLE Parametros; ALTER TemperaturaMax SET DEFAULT %s;ALTER TemperaturaMin SET DEFAULT %s;ALTER NoiseMax SET DEFAULT %s", (temperatura_max, temperatura_min, noise_max))
    sleep(3)