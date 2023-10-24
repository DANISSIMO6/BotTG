import re
import telebot

# Вставьте ваш токен бота
bot_token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"
chat_id = "@novostikompaniy"  # Замените на ID вашего чата

# Создайте экземпляр бота
bot = telebot.TeleBot(bot_token)

# Создание словаря для хранения Total Volume по FIGI
total_volumes = {}

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
    for line in stream_file:
        figi_match = re.search(r"figi='(\S+)'", line)
        volume_match = re.search(r"volume=(\d+)", line)
        if figi_match and volume_match:
            figi = figi_match.group(1)
            volume = int(volume_match.group(1))
            if figi in total_volumes and volume > (total_volumes[figi] * 2):
                # Отправка сообщения в Telegram, если объем в 2 раза больше Total Volume
                message = f"Объем для FIGI {figi} в Stream.md больше чем в 2 раза Total Volume: {volume}"
                bot.send_message(chat_id, message)
