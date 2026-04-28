FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 1. Copy only dependencies first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 2. Then copy application code
COPY . .