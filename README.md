# PISID Project

## Run Project
1. In the PC1 Directory run the command "docker compose up"
2. In the PC2 Directory run the command "docker compose up --build"
3. Run the runner.py script

## Project Structure

- **PC1/**  
  Scripts for Nuvem -> MongoDB migration and validation:
  - `move_to_mongo.py`, `sound_to_mongo.py`, `temp_to_mongo.py`, `validacoes.py`
  
  Scripts for MongoDB -> MQTT:
  - `publisher_movimentos.py`, `publisher_ruido.py`, `publisher_temperatura.py`
  
  Feedback scripts:
  - `feedback.py`
  
  MongoDB initialization scripts:
  - `init-scripts/`

- **PC2/**  
  MySQL-based data pipeline and web interface:
  - `db/initdb/init.sql`: MySQL schema and user setup
  - `Dockerfile`: Python service image
  - `docker-compose.yml`: Orchestrates all services
  - `php/`: Web files for the Apache+PHP container
  - `web/`: PHP scripts for handling HTML form submissions and database interactions
  - `css/`: Stylesheet for the web interface
  
  Scripts MQTT -> MySQL:
    - `receiver_movimentos.py`, `receiver_ruido.py`, `receiver_temperatura.py`, `utils.py`,
      `cloud_parameters.py`, `connection.py`
    
- **requirements.txt**  
  Python dependencies for all services

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose

## Python Dependencies (requirements.txt)

For local development or testig, it’s recommended to use a Python virtual environment ([venv](https://docs.python.org/3/library/venv.html)):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This keeps dependencies isolated from your system Python and avoids version conflicts.

### Requirements
The only requiment is Docker. 

On Mac & Windows it's easier to install
[Docker Desktop](https://www.docker.com/products/docker-desktop/)
