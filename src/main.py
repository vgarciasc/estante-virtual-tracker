import json
import datetime
from bs4 import BeautifulSoup
import requests as re

from notifier import create_message, send_message
import time


def get_current_prices(search_query):
    # Get HTML of page 'https://www.estantevirtual.com.br/busca?q=<search_query>'

    # Make a request to 'https://www.estantevirtual.com.br/busca?q=<search_query>'
    response = re.get(f"https://www.estantevirtual.com.br/busca?q={search_query}")

    # Get HTML of page
    html = response.text

    # Parse HTML to get the prices of the books, which are contained in spans with class 'preco'
    soup = BeautifulSoup(html, "html.parser")
    prices = soup.find_all("span", class_="preco")
    prices = [float(p.text.replace("R$ ", "").replace(",", ".")) for p in prices]
    prices.sort()

    # Return a list of prices
    return prices


def get_lowest_price(price_list):
    return min(price_list) if len(price_list) > 0 else None


if __name__ == "__main__":
    # Load JSON in "data/database.json"
    with open("data/database.json", "r") as f:
        data = json.load(f)

    to_notify = []
    for book in data['books']:
        if book['active'] is False:
            continue

        lowest_price_until_now = get_lowest_price(book['prices'])

        current_prices = get_current_prices(book["search_query"])
        current_lowest_price = get_lowest_price(current_prices)

        book['date_updated'] = datetime.datetime.now().strftime("%Y-%m-%d")
        book["prices"] = current_prices

        if len(current_prices) == 0:
            print(f"Book {book['name']} is unlisted.")
            continue

        if lowest_price_until_now is None or current_lowest_price < lowest_price_until_now:
            print(f"New lowest price for {book['name']}: {current_lowest_price}")
            to_notify.append(book)

        time.sleep(5)  # Sleep for 5 seconds to avoid getting blocked by the website

    # Save JSON in "data/database.json"
    with open("data/database.json", "w") as f:
        json.dump(data, f, indent=4)

    # Send notification
    if len(to_notify) > 0:
        print("Sending notification...")
        msg = create_message(to_notify)
        send_message(msg)
