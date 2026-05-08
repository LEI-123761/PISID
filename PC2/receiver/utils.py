# Moves
MOVES_USER= "mig_movimentos"
MOVES_PASSWORD="mig_movimentos4"

# Temp 
TEMPS_USER="mig_temperatura"
TEMPS_PASSWORD="mig_temperatura4"

# Sound 
SOUNDS_USER="mig_som"
SOUNDS_PASSWORD="mig_som4"

# Mysql DB
HOST="mysql"
PORT = 3306
DATABASE="maze"
MYSQL_ATTEMPTS = 5

# MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883

def get_id_simulacao(client):
    cursor = client.cursor()
    cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Status='Correr' LIMIT 1")
    row = cursor.fetchone() 
    cursor.close()
    return row[0] if row else None