import time
import telebot

token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"  # Замените на свой токен
channel_id = "@novostikompaniy"  # Имя вашего канала
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def commands(message):
    if message.text == "Старт":
        bot.send_message(channel_id, "Бот запущен и мониторит изменения данных.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши Старт")

while True:
    # Чтение старых данных построчно из example1.txt
    with open('example1.txt', 'r') as old_data_file:
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
            if abs(percentage_change) >= 0.5:
                # Форматирование текста с использованием HTML-разметки
                message_text = f"<b>Изменение за 1 минуту:</b>\n\n" \
                               f"<b>Тикер:</b> <code> {ticker.strip()}</code>\n" \
                               f"<b>Старые данные:</b> {old_value}\n" \
                               f"<b>Новые данные:</b> {new_value}\n" \
                               f"<b>Изменение в процентах:</b> {percentage_change:.2f}%"

                # Отправляем уведомление в канал с форматированием
                bot.send_message(channel_id, message_text, parse_mode="HTML")

        # Обновление старых данных в example1.txt
        old_data1[i] = str(new_value) + '\n'

    # Перезапись старых данных в example1.txt
    with open('example1.txt', 'w') as old_data_file:
        old_data_file.writelines(old_data1)

    # Подождите 60 секунд перед следующей итерацией
    time.sleep(60)

bot.stop_polling()


print('danil')


#6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M
