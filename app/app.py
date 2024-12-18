import psycopg2
import requests
import time
import os

API_KEY = os.getenv("API_KEY")
API_TOKEN = os.getenv("API_TOKEN")
BOARD_ID = "uKRwHpBj"
NEW_LIST_ID = "673f33da5d8736643b6afaf6"# ID списка с новыми тикетами
IN_PROGRESS_LIST_ID = "673f33da5d8736643b6afaf7"  # ID списка "В обработке"
PROCESSED_LIST_ID = "673f38c8c5244b279e080dc1" # ID списка обработанных тикетов


def fetch_and_process_tickets():
    try:
        conn = psycopg2.connect(
            host=os.getenv('EXTERNAL_DATABASE_URL'),
            database="postgres_db_av9c",
            user="user",
            password=os.getenv('DATABASE_PASSWORD')
        )
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
    except psycopg2.Error as e:
        print(f"Database error: {e}")


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
    try:
        conn = psycopg2.connect(
            host="postgres_db",
            database="support_db",
            user="user",
            password="password"
        )
        cursor = conn.cursor()

        # Обработка карточек из списка "В обработке"
        update_status_from_trello(cursor, IN_PROGRESS_LIST_ID, 'processed')

        # Обработка карточек из списка "Обработанные"
        update_status_from_trello(cursor, PROCESSED_LIST_ID, 'finished')

        # Сохранение изменений
        conn.commit()

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error fetching or updating tickets: {e}")


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



# Основной цикл обработки
if __name__ == "__main__":
    while True:
        print("Checking for new tickets...")
        fetch_and_process_tickets()
        print("Synchronizing statuses with Trello...")
        update_tickets_status_from_trello()
        print("Waiting for 10 seconds before checking again...")
        time.sleep(10)  # Ожидание 10 секунд перед следующей проверкой
