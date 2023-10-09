import time
import telebot
import pandas as pd
import subprocess

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
    # Выполнение команды
    # Создайте список тикеров
    tickers = [
        'ETLN', 'SBER', 'SBERP', 'ROSN', 'NVTK', 'LKOH', 'GAZP', 'SIBN', 'GMKN', 'CHGZ',
        'SNGSP', 'LSNGP', 'PLZL', 'TATN', 'TATNP', 'NLMK', 'SNGS', 'CHMF', 'TRNFP', 'UNAC',
        'YNDX', 'PHOR', 'IRKT', 'AKRN', 'TCSG', 'RUAL', 'MAGN', 'MGNT', 'OZON', 'ALRS',
        'VSMO', 'PIKK', 'MTSS', 'MOEX', 'HYDR', 'BANE', 'IRAO', 'VTBR', 'FESH', 'FLOT',
        'ENPG', 'BANEP', 'RTKM', 'SMLT', 'NMTP', 'CBOM', 'NKNC', 'RASP', 'POLY', 'RTKMP',
        'KZOS', 'TRMK', 'LSNG', 'MGTS', 'RSTIP', 'HHRU', 'GCHE', 'KMAZ', 'AFKS', 'MGTSP',
        'AFLT', 'AGRO', 'RGSS', 'FIVE', 'ROSB', 'NKNCP', 'FEES', 'KUBE', 'UPRO', 'KAZTP',
        'APTK', 'MTLRP', 'BSPB', 'KAZT', 'MSNG', 'UTAR', 'GLTR', 'RSTI', 'YAKG', 'NKHP',
        'MTLR', 'AVAN', 'SGZH', 'KCHEP', 'AQUA', 'SELG', 'DVEC', 'MSTT', 'MFGS', 'MRKS',
        'INGR', 'BELU', 'LSRG', 'USBN', 'UKUZ', 'MSRS', 'OGKB', 'MDMG', 'TNSE', 'MRKK',
        'KZOSP', 'RTSB', 'RKKE', 'KCHE', 'AMEZ', 'ROLO', 'RNFT', 'VJGZ', 'DSKY', 'SIBG',
        'VRSB', 'TGKA', 'QIWI', 'MFGSP', 'MRKP', 'MRKU', 'VJGZP', 'GTRK', 'BLNG', 'HIMCP',
        'VSYD', 'MVID', 'NNSB', 'JNOS', 'CHMK', 'SVAV', 'ABRD', 'VSYDP', 'PAZA', 'KROT',
        'RTSBP', 'LNZL', 'TGKD', 'SFIN', 'TTLK', 'JNOSP', 'TGKN', 'MRKC', 'YRSB', 'GAZA',
        'VRSBP', 'ENRU', 'TGKDP', 'UCSS', 'URKZ', 'KOGK', 'WTCM', 'TGKBP', 'KRSB', 'KRSBP',
        'KRKOP', 'BISVP', 'SAGO', 'MRKY', 'RAVN', 'CHKZ', 'UWGN', 'KBSB', 'KRKN', 'SLEN',
        'MRKV', 'NNSBP', 'PMSBP', 'MISB', 'BRZL', 'TGKB', 'MISBP', 'WTCMP', 'IGSTP', 'SAGOP',
        'IGST', 'PRMB', 'LNTA', 'YKEN', 'RUSI', 'OKEY', 'ZILL', 'MRKZ', 'ISKJ', 'KMEZ', 'ZVEZ',
        'PMSB', 'VGSB', 'KGKC', 'NAUK', 'EELT', 'YRSBP', 'RZSB', 'KGKCP', 'KROTP', 'LPSB',
        'YKENP', 'PRFN', 'NKSH', 'UNKL', 'KRKNP', 'VGSBP', 'NFAZ', 'TORS', 'LNZLP', 'KTSB',
        'MAGE', 'TASB', 'SARE', 'STSB', 'DZRD', 'POGR', 'ASSB', 'CNTL', 'MAGEP', 'ROST', 'NSVZ',
        'RDRB', 'MGNZ', 'STSBP', 'KLSB', 'CNTLP', 'TORSP', 'LVHK', 'DZRDP', 'RBCM', 'TASBP',
        'LIFE', 'SAREP', 'MERF', 'GEMA', 'TUZA', 'DIOD', 'VLHZ', 'KTSBP', 'KUZB', 'ARSA', 'MRSB',
        'ELTZ', 'RUGR', 'ORUP', 'DASB', 'MSST', 'GRNT', 'ODVA', 'RLMNP', 'GTLC', 'RLMN'
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
    last_prices = df['Last price'].str.strip().iloc[1:].to_string(index=False, header=False)

    # Запись данных в файл example.txt
    with open('example.txt', 'w') as example_file:
        example_file.write(last_prices)
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
            if abs(percentage_change) >= 0.001:
                # Форматирование текста с использованием HTML-разметки
                message_text = f"<b>Резкое изменение за 1 минуту:</b>\n\n" \
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





#6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M
