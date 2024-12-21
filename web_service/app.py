from flask import Flask, request, jsonify, render_template
import psycopg2
import json
import requests  # Для отправки HTTP-запросов в email_service
import threading
import time
import os

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_TOKEN = os.getenv("API_TOKEN")
BOARD_ID = "uKRwHpBj"
NEW_LIST_ID = "673f33da5d8736643b6afaf6"# ID списка с новыми тикетами
IN_PROGRESS_LIST_ID = "673f33da5d8736643b6afaf7"  # ID списка "В обработке"
PROCESSED_LIST_ID = "673f38c8c5244b279e080dc1" # ID списка обработанных тикетов

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Подключение к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST'),
            database="postgres_db_av9c",
            user="user",
            password=os.getenv('DATABASE_PASSWORD')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None



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


        return jsonify({"message": "Запрос отправлен"}), 201
    except Exception as e:
        return jsonify({"message": "Ошибка создания запроса", "error": str(e)}), 500




def fetch_and_process_tickets():

    conn = get_db_connection()
    cursor = conn.cursor()
    # Выборка новых тикетов, которые еще не добавлены в Trello
    cursor.execute(
        "SELECT id, username, email, subject, description FROM tickets WHERE status = 'new' AND is_in_trello = FALSE"
    )
    tickets = cursor.fetchall()

    if not tickets:
        print("No new tickets to process.")
        return

    for ticket in tickets:
        ticket_id, username, email, subject, description = ticket
        print(f"Processing ticket {ticket_id} from {username}")

        # Логика отправки данных в Trello
        success = send_to_trello(username, email, subject, description)

        if success:
            cursor.execute(
                "UPDATE tickets SET is_in_trello = TRUE WHERE id = %s",
                (ticket_id,)
            )
            conn.commit()
            print(f"Ticket {ticket_id} marked as added to Trello (is_in_trello: TRUE).")
        else:
            print(f"Failed to process ticket {ticket_id}.")

    cursor.close()
    conn.close()

def send_to_trello(username, email, subject, description):
    url = f"https://api.trello.com/1/cards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'idList': NEW_LIST_ID,
        'key': API_KEY,
        'token': API_TOKEN,
        'name': f"{subject} (by {username})",
        'desc': f"**Email:** {email}\n\n**Description:**\n{description}"
    }

    try:
        response = requests.post(url, headers=headers, params=query)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully sent ticket to Trello: {username}, {subject}")
            return True
        else:
            print(f"Failed to send ticket to Trello: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"Error sending to Trello: {e}")
        return False


def update_tickets_status_from_trello():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Обработка карточек из списка "В обработке"
    update_status_from_trello(cursor, IN_PROGRESS_LIST_ID, 'processed')

    # Обработка карточек из списка "Обработанные"
    update_status_from_trello(cursor, PROCESSED_LIST_ID, 'finished')

    # Сохранение изменений
    conn.commit()

    cursor.close()
    conn.close()




def update_status_from_trello(cursor, list_id, new_status):
    """
    Обновляет статус заявок в базе данных на основе карточек из указанного списка Trello.
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {'key': API_KEY, 'token': API_TOKEN}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        cards = response.json()
        ticket_names = [
            card['name'].split(" (by ")[0] for card in cards
        ]  # Извлечение имени тикета из названия карточки

        if not ticket_names:
            print(f"No tickets found in Trello list {list_id}.")
            return

        # Обновление статуса в базе данных
        for ticket_name in ticket_names:
            cursor.execute(
                "UPDATE tickets SET status = %s WHERE subject = %s AND status != %s",
                (new_status, ticket_name, new_status)
            )
        print(f"Tickets in Trello list {list_id} updated to status {new_status}.")
    else:
        print(f"Failed to fetch cards from Trello (list {list_id}): {response.status_code}, {response.text}")

def check_tickets():
    while True:
        print("Checking for new tickets...")
        fetch_and_process_tickets()
        print("Synchronizing statuses with Trello...")
        update_tickets_status_from_trello()
        print("Waiting for 10 seconds before checking again...")
        time.sleep(30)  # Ожидание 30 секунд перед следующей проверкой

if __name__ == '__main__':
    # Создаем и запускаем фоновый поток для цикла проверки тикетов
    ticket_check_thread = threading.Thread(target=check_tickets)
    ticket_check_thread.daemon = True  # Поток завершится, когда завершится основной процесс
    ticket_check_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5000)
