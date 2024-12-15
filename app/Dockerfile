FROM python:3.9.11

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# ����������, ��� ���� ���������� � ������ �����������
RUN chmod +x ./wait-for-db.sh

ENTRYPOINT ["./wait-for-db.sh", "postgres_db", "--", "python3", "app.py"]

