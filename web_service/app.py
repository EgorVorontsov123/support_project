from flask import Flask, request, jsonify, render_template
import psycopg2
import json
import requests  # Для отправки HTTP-запросов в email_service

app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Подключение к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="postgres_db",  # Название контейнера с базой данных
            database="support_db",
            user="user",
            password="password"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Отправка email через email_service
def send_email(email, subject, description):
    try:
        response = requests.post(
            "http://email_service:5000/send_email",  # Адрес email_service
            json={
                "email": email,
                "subject": subject,
                "description": description
            }
        )
        if response.status_code == 200:
            print("Email отправлен успешно")
        else:
            print(f"Ошибка отправки email: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Ошибка подключения к email_service: {e}")

# Обработка POST-запроса
@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()

    # Валидация данных
    required_fields = ['username', 'email', 'subject', 'description']
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"message": "All fields are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection error"}), 500

    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tickets (username, email, subject, description) VALUES (%s, %s, %s, %s)",
            (data['username'], data['email'], data['subject'], data['description'])
        )

        conn.commit()
        cursor.close()
        conn.close()

        # Отправка email
        send_email(data['email'], data['subject'], data['description'])

        return jsonify({"message": "Ticket created and email sent successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error creating ticket", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
