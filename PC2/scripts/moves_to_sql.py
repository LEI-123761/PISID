import mysql.connector;
import time;
import os;

while True:
    try:
        cnx = mysql.connector.connect(
            user=os.environ.get("MOVES_USER"), 
            password=os.environ.get("MOVES_PASSORD"),
            host=os.environ.get("HOST", "mysql"),
            database=os.environ.get("DATABASE", "maze")
        );
        print("Connected to the database");
        break;
    except:
        print("Waiting for MySQL...");
        time.sleep(2);
cnx.close();