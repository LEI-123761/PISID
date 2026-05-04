# PISID Project

## Project Structure

- **PC1/**  
  Scripts for MongoDB data ingestion and validation:
  - `mongoToMqtt.py`, `move_to_mongo.py`, `sound_to_mongo.py`, `temp_to_mongo.py`, `validacoes.py`
  - `init-scripts/`: MongoDB initialization scripts

- **PC2/**  
  MySQL-based data pipeline and web interface:
  - `db/initdb/init.sql`: MySQL schema and user setup
  - `Dockerfile`: Python service image
  - `docker-compose.yml`: Orchestrates all services
  - `scripts/`:
    - `moves_to_sql.py`, `temps_to_sql.py`, `sounds_to_sql.py`: Python scripts for MySQL
    - `php/`: Web files for the Apache+PHP container

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

## Setup & Running

In the default path `PISID/`. Run the command
```bash
docker compose up -d
```

### Requirements
The only requiment is Docker. 

On Mac & Windows it's easier to install
[Docker Desktop](https://www.docker.com/products/docker-desktop/)