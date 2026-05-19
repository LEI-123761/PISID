import mysql.connector
import utils
import time

from connection import connect_to_mysql

MYSQL_CONFIG = {
    "host": utils.HOST,
    "user": "root",
    "password": "root",
    "database": utils.DATABASE
}

tentativas = utils.MYSQL_ATTEMPTS

# ligação à BD local
mysqlclient = connect_to_mysql(MYSQL_CONFIG, attempts=tentativas)

ID_SIMULACAO = None

if mysqlclient:
    mycursor = mysqlclient.cursor()
    print("[MOV] Ligado ao MySQL")

    ID_SIMULACAO = utils.get_id_simulacao(mysqlclient)

    if ID_SIMULACAO is None:
        print("[MOV] Aviso: sem simulação ativa no arranque")

else:
    print("[MOV] Erro: erro ao ligar à BD depois de", tentativas, "tentativas")
    exit()


while True:

    try:
        # ligação cloud
        cloud = mysql.connector.connect(
            host="194.210.86.10",
            user="aluno",
            password="aluno",
            database="maze"
        )

        cloud_cursor = cloud.cursor()

        # obter parâmetros numa única query
        cloud_cursor.execute("""
                             SELECT
                                 normaltemperature,
                                 normalnoise,
                                 temperaturevarhightoleration,
                                 temperaturevarlowtoleration,
                                 noisevartoleration
                             FROM SetupMaze
                             """)

        (
            norm_temp,
            norm_noise,
            temp_high_tol,
            temp_low_tol,
            noise_tol
        ) = cloud_cursor.fetchone()

        # calcular valores
        temperatura_max = norm_temp + temp_high_tol
        temperatura_min = norm_temp - temp_low_tol
        noise_max = norm_noise + noise_tol

        print(f"Temperatura Max: {temperatura_max}")
        print(f"Temperatura Min: {temperatura_min}")
        print(f"Noise Max: {noise_max}")

        # alterar DEFAULTS da tabela
        query = f"""
        ALTER TABLE Parametros
        MODIFY TemperaturaMax DECIMAL(4,2) DEFAULT {temperatura_max},
        MODIFY TemperaturaMin DECIMAL(4,2) DEFAULT {temperatura_min},
        MODIFY SomMax DECIMAL(4,2) DEFAULT {noise_max}
        """

        mycursor.execute(query)
        mysqlclient.commit()

        print("[MOV] Defaults atualizados")

    except mysql.connector.Error as err:
        print("[ERRO MYSQL]", err)

    except Exception as e:
        print("[ERRO]", e)

    finally:
        try:
            cloud_cursor.close()
            cloud.close()
        except:
            pass

    time.sleep(30)