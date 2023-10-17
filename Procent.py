import time
import telebot
import pandas as pd
import re
import subprocess
from datetime import datetime, time as dt_time
from io import StringIO

# Укажите токен вашего бота и ID канала
token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"   # Замените на токен вашего бота
channel_id = "@novostikompaniy"  # Замените на имя вашего канала
bot = telebot.TeleBot(token)

depth = 50  # Укажите желаемую глубину

# Укажите времена начала и окончания перерывов
start_time1 = dt_time(23, 50)
end_time1 = dt_time(10, 0)
start_time2 = dt_time(19, 0)
end_time2 = dt_time(19, 5)

with open("tickers.txt", "r") as file:
    tickers = file.read().splitlines()

while True:
    current_time = dt_time(datetime.now().hour, datetime.now().minute)

    # Если сейчас время перерыва, подождите минуту
    if start_time1 <= current_time <= end_time1 or start_time2 <= current_time <= end_time2:
        time.sleep(60)
        continue

    for instrument_ticker in tickers:
        order_book_command = f'tksbrokerapi -t {instrument_ticker} --depth {depth} --price > glass.md'
        subprocess.call(order_book_command, shell=True)

        with open("glass.md", "r") as file:
            file_contents = file.read()

        total_sell_match = re.search(r"Total sell:\s*(\d+)", file_contents)
        total_sell = int(total_sell_match.group(1) if total_sell_match else 0)

        total_buy_match = re.search(r"Total buy:\s*(\d+)", file_contents)
        total_buy = int(total_buy_match.group(1) if total_buy_match else 0)

        if total_sell and total_buy:
            buy_ratio = total_buy / (total_sell + total_buy) * 100
            sell_ratio = total_sell / (total_sell + total_buy) * 100

            # Если соотношение покупок и продаж больше 60%, отправляем уведомление
            if buy_ratio > 90 or sell_ratio > 90:
                try:
                    bot.send_message(channel_id, f"Обнаружена аномалия для {instrument_ticker}: Покупка {sell_ratio:.2f}% Продажа {buy_ratio:.2f}%")
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Не удалось отправить сообщение: {e}")

    tickers_str = ' '.join(tickers)
    command = f'tksbrokerapi --token "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ" --prices {tickers_str} --output C:\\Windows\\System32\\TKSBrokerAPI\\docs\\examples\\AnomalyVolumesDetector\\pricez.md'
    subprocess.call(command, shell=True)

    df = pd.read_csv('pricez.md', sep='|', skiprows=3, header='infer', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    actual_sell_buy = df['Actual sell / buy'].str.strip().iloc[1:]
    actual_sell_buy_split = actual_sell_buy.str.split('/', expand=True)
    actual_sell = actual_sell_buy_split[0].str.strip()
    actual_buy = actual_sell_buy_split[1].str.strip()
    actual_buy = actual_buy.apply(lambda x: float(x) if x else None).round(4)

    with StringIO() as output_buffer:
        actual_buy.to_string(output_buffer, index=False, header=False)
        output_buffer.seek(0)
        new_data_lines = output_buffer.readlines()

    with open('example1.txt') as old_data_file:
        old_data1 = old_data_file.readlines()

    with open('tickers.txt', 'r') as tickers_file:
        tickers = tickers_file.readlines()

    for i, (old_line, new_line, ticker) in enumerate(zip(old_data1, new_data_lines, tickers)):
        old_value = float(old_line.strip())
        new_value = float(new_line.strip())

        if old_value != new_value:
            print(f"Тикер: {ticker.strip()}")
            print(f"Строка {i + 1}: Данные изменились!")
            percentage_change = (new_value - old_value) / old_value * 100
            print(f"Старые данные: {old_value}")
            print(f"Новые данные: {new_value}")
            print(f"Изменение в процентах: {percentage_change:.2f}%")

            if abs(percentage_change) >= 5.0:
                message_text = f"<b>Резкое изменение за 1 минуту:</b>\n\n" \
                               f"<b>Тикер:</b> <code> {ticker.strip()}</code>\n" \
                               f"<b>Старые данные:</b> {old_value}\n" \
                               f"<b>Новые данные:</b> {new_value}\n" \
                               f"<b>Изменение в процентах:</b> {percentage_change:.2f}%"

                bot.send_message(channel_id, message_text, parse_mode="HTML")
                time.sleep(3)

        old_data1[i] = str(new_value) + '\n'

    with open('example1.txt', 'w') as old_data_file:
        old_data_file.writelines(old_data1)

    time.sleep(60)

bot.stop_polling()
