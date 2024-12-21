FROM python:3.9.11

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./


RUN chmod +x app/wait-for-db.sh

ENTRYPOINT ["./wait-for-db.sh", "postgres_db", "--", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]

