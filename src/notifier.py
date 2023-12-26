import requests
import json
from datetime import datetime
from tokens import BOT_API_TOKEN, CHAT_ID

def create_message(books):
    message = f">> {datetime.now().strftime('%Y-%m-%d, %H:%M')} <<\n\n"
    for i, book in enumerate(books):
        message += f"*{book['name']}*, by {book['author']}\n"
        message += f"\t- New lowest price for {book['name']}: R$ {book['prices'][0]:.2f}\n".replace('.', ',')
        message += f"\t- [Listings](https://www.estantevirtual.com.br/busca?q={book['search_query']})\n"
        message += "\n" if i < len(books) - 1 else ""

    return message

def send_message(message):
    telegram_api_url = f"https://api.telegram.org/bot{BOT_API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'MARKDOWN'
    }

    try:
        response = requests.post(telegram_api_url, json=payload)
        response.raise_for_status()
        print("Message sent successfully!")
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")


if __name__ == "__main__":
    with open("data/database.json", "r") as f:
        data = json.load(f)

    msg = create_message(data['books'])
    print(msg)
