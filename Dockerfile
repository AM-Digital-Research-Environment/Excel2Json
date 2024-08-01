FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.txt
