FROM python:3.9.11

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

WORKDIR /web_service

COPY web_service requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Убеждаемся, что файл скопирован и сделан исполняемым
RUN chmod +x web_service/wait-for-db.sh

ENTRYPOINT ["web_service/wait-for-db.sh", "postgres_db", "--", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

