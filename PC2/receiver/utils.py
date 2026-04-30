# Moves
MOVES_USER= "movimentos_user"
MOVES_PASSWORD="movimentos_password"

# Temp 
TEMPS_USER="temperatura_user"
TEMPS_PASSWORD="temperatura_password"

# Sound 
SOUNDS_USER="som_user"
SOUNDS_PASSWORD="som_password"

# Mysql DB
HOST="mysql"
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