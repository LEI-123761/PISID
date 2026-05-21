from flask import Flask, request
import os
import subprocess
import threading
import requests
import mysql.connector
import time

app = Flask(__name__)

def thread_code(simulation_id):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        mazerun_path = os.path.join(base_dir, "mazerun", "mazerun.exe")

        subprocess.run([mazerun_path, "4", "--broker", "broker.hivemq.com", "--flagMessage", "1"])
    finally:
        time.sleep(2)

        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="maze",
            port=13306
        )

        cursor = connection.cursor()
        cursor.execute("UPDATE Simulacao SET Status = 'Terminado' WHERE IDSimulacao = %s", (simulation_id,))
        connection.commit()

@app.route("/run")
def run_game():
    sim_id = request.args.get("id")
    threading.Thread(target=thread_code, args=(sim_id,)).start()
    return "finished"


app.run(host="0.0.0.0", port=5000)