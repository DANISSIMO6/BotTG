import telebot
import requests
import time

from bs4 import BeautifulSoup

token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"  # ыВаш токен
channel_id = "@novostikompaniy"  # Ваш логин канала
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def commands(message):
    #bot.send_message(channel_id, message.text)
    if message.text == "Старт":
        # bot.send_message(channel_id, "Hello")
        back_silkainfa_href = None
        while True:
            silkainfa_text = parser(back_silkainfa_href)
            back_silkainfa_href = silkainfa_text[1]

            if silkainfa_text[0] != None:
                bot.send_message(channel_id, silkainfa_text[0])
                time.sleep(10)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")


def parser(back_silkainfa_href):
    URL = 'https://www.e-disclosure.ru'
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')

    table = soup.find('div', class_="table table_full last30__table table_top-events-list")
    #post = table.find ('tr')
    infa = table.find('br')
    silkainfa = table.find('a', href_="", href=True)
    silkainfa_href = silkainfa['href']

    if silkainfa_href != back_silkainfa_href:
        #time = table.find('td').text.strip()
        title = table.find('a', href_="").text.strip()
        silka = table.find('a', href_="", href=True)["href"].strip()
        infa = table.find('br')
        titleinfa = infa.find('a', href_="").text.strip()
        silkainfa = infa.find('a', href_="", href=True)["href"].strip()
        return f"{title}\n\n{silka}\n\n{titleinfa}\n\n{silkainfa}", silkainfa_href

    else:
        return None, silkainfa_href

bot.polling()

