import re
import telebot
from datetime import datetime, timedelta, timezone
import time

sent_messages = set()
# Создайте объект timezone для UTC
utc_timezone = timezone.utc
stream_data = []
# Ваш токен бота и ID чата
bot_token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"
chat_id = "@novostikompaniy"

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Создание словаря для хранения Total Volume по FIGI
total_volumes = {}
last_cleanup_time = datetime.now(timezone.utc)
while True:
    # Считывание данных из файла FIGI.md и заполнение словаря
    with open("FIGI.md", "r") as figi_file:
        figi_data = figi_file.read()
        figi_matches = re.finditer(r"FIGI: (\S+)[\s\S]*?Total Volume for 2nd to 5th weeks after division: ([\d.]+)", figi_data)
        for match in figi_matches:
            figi = match.group(1)
            total_volume = float(match.group(2))
            total_volumes[figi] = total_volume

    # Считывание данных из файла Stream.md
    with open("Stream.md", "r") as stream_file:
        lines = stream_file.readlines()
        new_lines = []
        for line in lines:
            figi_match = re.search(r"figi='(\S+)'", line)
            volume_match = re.search(r"volume=(\d+)", line)
            time_match = re.search(r"time=datetime.datetime\(([\d, ]+), tzinfo=datetime.timezone.utc\)", line)
            close_match = re.search(r"close=Quotation\(units=(\d+), nano=(\d+)\)", line)
            if figi_match and volume_match and time_match and close_match:
                figi = figi_match.group(1)
                volume = int(volume_match.group(1))
                close_units = int(close_match.group(1))
                close_nano = int(close_match.group(2))
                close_value = close_units + close_nano * 1e-9  # Преобразование в одно число
                total_value = volume * close_value  # Умножение объема на цену закрытия
                line_time = datetime(*map(int, time_match.group(1).split(", ")), tzinfo=utc_timezone)
                current_time = datetime.now(timezone.utc)
                if figi in total_volumes and volume > (total_volumes[figi] * 2) and figi not in sent_messages:
                    # Отправка сообщения в Telegram, если объем в 2 раза больше Total Volume
                    message = f"Объем для FIGI {figi} в Stream.md больше чем в 2 раза Total Volume: {volume}. " \
                              f"Общая стоимость составила: {total_value}"
                    bot.send_message(chat_id, message)
                    sent_messages.add(figi)
                if current_time - line_time < timedelta(minutes=6):
                    new_lines.append(line)
        with open("Stream.md", "w") as stream_file:
            stream_file.writelines(new_lines)

    if current_time - last_cleanup_time >= timedelta(minutes=1):
        sent_messages.clear()  # Очищаем множество отправленных сообщений
        last_cleanup_time = current_time  # Обновляем время последней очистки

    # Пауза на 1 минуту перед следующей итерацией
    time.sleep(2.5)


