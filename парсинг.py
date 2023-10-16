import time
import telebot
import re  # Импорт модуля регулярных выражений
import subprocess
from datetime import datetime, time as dt_time

token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"
channel_id = "@novostikompaniy"
bot = telebot.TeleBot(token)

# Define the instrument to monitor
instrument_ticker = "SBER"  # Replace with the desired instrument's ticker
depth = 50  # Replace with the desired depth


@bot.message_handler(content_types=['text'])
def commands(message):
    if message.text == "Старт":
        bot.send_message(channel_id, "Бот запущен и monitoring data.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")


# Read tickers from the file
with open("tickers.txt", "r") as file:
    tickers = file.read().splitlines()

while True:
    for instrument_ticker in tickers:
        # Формируем команду для получения данных о стакане и записываем её в файл glass.md
        order_book_command = f'tksbrokerapi -t {instrument_ticker} --depth {depth} --price > glass.md'
        subprocess.call(order_book_command, shell=True)

        # Читаем данные из файла glass.md
        with open("glass.md", "r") as file:
            file_contents = file.read()

        # Используем регулярные выражения для извлечения числа из строки "Total sell"
        total_sell_match = re.search(r"Total sell:\s*(\d+)", file_contents)
        if total_sell_match:
            total_sell = int(total_sell_match.group(1))
        else:
            total_sell = None

        # Используем регулярные выражения для извлечения числа из строки "Total buy"
        total_buy_match = re.search(r"Total buy:\s*(\d+)", file_contents)
        if total_buy_match:
            total_buy = int(total_buy_match.group(1))
        else:
            total_buy = None

        # Добавьте код для обработки данных, например, расчета процентного соотношения
        # total_sell и total_buy здесь
        if total_sell and total_buy:
            buy_ratio = total_buy / (total_sell + total_buy) * 100
            sell_ratio = total_sell / (total_sell + total_buy) * 100
            if buy_ratio > 60 or sell_ratio > 60:
                try:
                    bot.send_message(channel_id,
                                     f"Аномалия обнаружена для {instrument_ticker}: Покупка {sell_ratio:.2f}% Продажа {buy_ratio:.2f}%")
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Failed to send message: {e}")
    time.sleep(10)

bot.stop_polling()





#t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ