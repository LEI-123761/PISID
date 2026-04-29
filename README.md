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

1. **Clone the repository** and ensure you are in the root `PISID/` directory.

2. **Build and start all services:**

   ```sh
   docker compose -f PC2/docker-compose.yml up --build
   ```

   This will:
   - Start MySQL (port 13306), with schema and users auto-initialized
   - Start Python containers for movements, temperature, and sound ingestion
   - Start a PHP web server (port 8080) and phpMyAdmin (port 8081)

3. **Access services:**
   - **phpMyAdmin:** [http://localhost:8081](http://localhost:8081)
   - **Web server:** [http://localhost:8080](http://localhost:8080)

4. **Python scripts** in `PC2/scripts/` are run automatically by their containers and connect to the MySQL database using credentials set in the compose file.

## Customization

- To change database credentials or service ports, edit `PC2/docker-compose.yml`.
- To add Python dependencies, update `requirements.txt` in the project root.

## Notes

- If you change the database schema (init.sql) or user setup, remove the `mysql_data` Docker volume to reinitialize:
  ```sh
  docker compose -f PC2/docker-compose.yml down -v
  docker compose -f PC2/docker-compose.yml up --build
  ```
