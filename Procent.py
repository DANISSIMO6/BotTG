import time
import telebot
import pandas as pd
import re
import threading
import subprocess
from datetime import datetime, time as dt_time

token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"  # Замените на свой токен
channel_id = "@novostikompaniy"  # Имя вашего канала
bot = telebot.TeleBot(token)

depth = 50  # Replace with the desired depth

# Время начала и окончания первого отдыха (23:50 - 10:00)
start_time1 = dt_time(23, 50)
end_time1 = dt_time(10, 0)
# Время начала и окончания второго отдыха (19:00 - 19:05)
start_time2 = dt_time(19, 0)
end_time2 = dt_time(19, 5)
task1_completed = False
task2_completed = False
@bot.message_handler(content_types=['text'])
def commands(message):
    if message.text == "Старт":
        bot.send_message(channel_id, "Бот запущен и мониторит изменения данных.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")

with open("tickers.txt", "r") as file:
    tickers = file.read().splitlines()
def task1():
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

def task2():
    while True:
        tickers = [
            'ETLN', 'SBER', 'SBERP', 'ROSN', 'NVTK', 'LKOH', 'GAZP', 'SIBN', 'GMKN', 'SNGSP', 'LSNGP',
            'PLZL', 'TATN', 'TATNP', 'NLMK', 'SNGS', 'CHMF', 'TRNFP', 'UNAC', 'YNDX', 'PHOR', 'IRKT',
            'AKRN', 'TCSG', 'RUAL', 'MAGN', 'MGNT', 'OZON', 'ALRS', 'VSMO', 'PIKK', 'MTSS', 'MOEX',
            'HYDR', 'BANE', 'IRAO', 'VTBR', 'FESH', 'FLOT', 'ENPG', 'BANEP', 'RTKM', 'SMLT', 'NMTP',
            'CBOM', 'NKNC', 'RASP', 'POLY', 'RTKMP', 'KZOS', 'TRMK', 'LSNG', 'HHRU', 'GCHE', 'KMAZ',
            'AFKS', 'MGTSP', 'AFLT', 'AGRO', 'FIVE', 'NKNCP', 'FEES', 'UPRO', 'KAZTP', 'APTK', 'MTLRP',
            'BSPB', 'KAZT', 'MSNG', 'GLTR', 'YAKG', 'NKHP', 'MTLR', 'SGZH', 'AQUA', 'SELG', 'DVEC', 'MSTT',
            'MRKS', 'INGR', 'BELU', 'LSRG', 'MSRS', 'OGKB', 'MDMG', 'KZOSP', 'RKKE', 'AMEZ', 'ROLO', 'RNFT',
            'DSKY', 'VRSB', 'TGKA', 'QIWI', 'MRKP', 'MRKU', 'GTRK', 'BLNG', 'MVID', 'CHMK', 'SVAV', 'ABRD',
            'KROT', 'LNZL', 'SFIN', 'TTLK', 'TGKN', 'MRKC', 'TGKBP', 'MRKY', 'UWGN', 'MRKV', 'PMSBP', 'TGKB',
            'OKEY', 'MRKZ', 'PMSB', 'PRFN', 'UNKL', 'KRKNP', 'LNZLP', 'CNTL', 'ROST', 'NSVZ', 'KLSB', 'CNTLP',
            'LIFE', 'DIOD', 'RUGR'
        ]

        # Преобразуйте список тикеров в строку, разделенную пробелами
        tickers_str = ' '.join(tickers)
        # Измените команду на использование переменной tickers_str
        command = f'tksbrokerapi --token "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ" --prices {tickers_str} --output C:\\Windows\\System32\\TKSBrokerAPI\\docs\\examples\\AnomalyVolumesDetector\\pricez.md'

        subprocess.call(command, shell=True)

        # Чтение файла и создание DataFrame, пропуск первых 3 строк (заголовка и разделителей)
        df = pd.read_csv('pricez.md', sep='|', skiprows=3, header='infer', skipinitialspace=True)
        # Удаление лишних пробелов в именах столбцов
        df.columns = df.columns.str.strip()
        # Извлечение данных из столбца "Last price" и исключение первой строки
        # Извлечение данных из столбца "Actual sell / buy" и исключение первой строки
        actual_sell_buy = df['Actual sell / buy'].str.strip().iloc[1:]

        # Разделение столбца на два столбца "Actual sell" и "Actual buy"
        actual_sell_buy_split = actual_sell_buy.str.split('/', expand=True)
        actual_sell = actual_sell_buy_split[0].str.strip()
        actual_buy = actual_sell_buy_split[1].str.strip()

        def convert_to_float_or_none(x):
            try:
                return float(x)
            except (ValueError, TypeError):
                return None


        actual_buy = actual_buy.apply(lambda x: convert_to_float_or_none(x)).round(4)

        # Преобразование цены покупки в строку и запись в файл
        with open('example.txt', 'w') as example_file:
            example_file.write(actual_buy.to_string(index=False, header=False))

        # Чтение старых данных построчно из example1.txt
        with open('example1.txt') as old_data_file:
            old_data1 = old_data_file.readlines()

        # Чтение новых данных построчно из example.txt
        with open('example.txt', 'r') as new_data_file:
            new_data_lines = new_data_file.readlines()

        # Чтение тикеров построчно из tickers.txt
        with open('tickers.txt', 'r') as tickers_file:
            tickers = tickers_file.readlines()

        # Проверка изменений построчно
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

                # Проверка изменения в 0,5% и отправка уведомления
                if abs(percentage_change) >= 5.0:
                    # Форматирование текста с использованием HTML-разметки
                    message_text = f"<b>Резкое изменение за 1 минуту:</b>\n\n" \
                                   f"<b>Тикер:</b> <code> {ticker.strip()}</code>\n" \
                                   f"<b>Старые данные:</b> {old_value}\n" \
                                   f"<b>Новые данные:</b> {new_value}\n" \
                                   f"<b>Изменение в процентах:</b> {percentage_change:.2f}%"

                    # Отправляем уведомление в канал с форматированием
                    bot.send_message(channel_id, message_text, parse_mode="HTML")
                    time.sleep(3)
            # Обновление старых данных в example1.txt
            old_data1[i] = str(new_value) + '\n'

        # Перезапись старых данных в example1.txt
        with open('example1.txt', 'w') as old_data_file:
            old_data_file.writelines(old_data1)

        # Подождите 60 секунд перед следующей итерацией

t1 = threading.Thread(target=task1)
t2 = threading.Thread(target=task2)
t1.start()
t2.start()
t1.join()
t2.join()
bot.stop_polling()




#6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M
