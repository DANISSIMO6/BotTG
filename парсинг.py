import telebot
import requests
import time
from bs4 import BeautifulSoup

token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"  # Your token
channel_id = "@novostikompaniy"  # Your channel username
bot = telebot.TeleBot(token)

def send_long_message(chat_id, text):
    max_length = 4096  # Maximum length allowed by Telegram API
    for i in range(0, len(text), max_length):
        bot.send_message(chat_id, text[i:i + max_length])

@bot.message_handler(content_types=['text'])
def commands(message):
    if message.text == "Старт":
        back_silkainfa_href = None
        while True:
            silkainfa_text = parser(back_silkainfa_href)
            back_silkainfa_href = silkainfa_text[1]

            if silkainfa_text[0] is not None:
                send_long_message(channel_id, silkainfa_text[0])
                time.sleep(10)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")

def parser(back_silkainfa_href):
    URL = 'https://www.e-disclosure.ru'
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find('div', class_="table table_full last30__table table_top-events-list")
    infa = table.find('br')
    silkainfa = table.find('a', href_="", href=True)
    silkainfa_href = silkainfa['href']

    if silkainfa_href != back_silkainfa_href:
        title = table.find('a', href_="").text.strip()
        silka = table.find('a', href_="", href=True)["href"].strip()
        infa = table.find('br')
        titleinfa = infa.find('a', href_="").text.strip()
        silkainfa = infa.find('a', href_="", href=True)["href"].strip()

        # Open the link and get data
        event_page = requests.get(silkainfa)
        event_soup = BeautifulSoup(event_page.text, 'html.parser')
        event_data = event_soup.find('div', style="word-break: break-word; word-wrap: break-word; white-space: pre-wrap;").text.strip()

        message = f"{title}\n\n{silka}\n\n{titleinfa}\n\n{silkainfa}\n\n{event_data}"
        return message, silkainfa_href
    else:
        return None, silkainfa_href

bot.polling()
