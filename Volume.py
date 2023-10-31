import re
import telebot
from datetime import datetime, timedelta, timezone
import time
import pytz
import html
import asyncio
from tinkoff.invest import (
    AsyncClient,
    MarketDataRequest,
    SubscriptionAction,
    SubscribeOrderBookRequest,
    OrderBookInstrument,
)

TOKEN = "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ"
order_books = {}  # Add a dictionary to store order book data
# Ваш токен бота и ID чата
bot_token = "6384593851:AAHHgUGXdQ8bar8HMKRuNgi1NnV_rhqnx0M"
chat_id = "@novostikompaniy"

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

async def request_iterator(figi):
    yield MarketDataRequest(
        subscribe_order_book_request=SubscribeOrderBookRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
            instruments=[
                OrderBookInstrument(
                    figi=figi,
                    depth=50,
                )
            ],
        )
    )
    await asyncio.sleep(5)

async def process_marketdata(figi):
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator(figi)
        ):
            print(marketdata)
            with open('StreamBook.md', 'a') as stream:
                stream.write(str(marketdata) + '\n')
                print(marketdata)
                order_books[figi] = marketdata
# Функция для извлечения close=Quotation из строки
def extract_close_from_line(line):
    match = re.search(r"close=Quotation\(units=(\d+), nano=(\d+)\)", line)
    if match:
        units = int(match.group(1))
        nano = int(match.group(2))
        close_value1 = units + nano * 1e-9  # Преобразование в одно число
        return close_value1
    return None

# Функция для получения close=Quotation для указанного figi из файла Close.md
def get_close_value_for_figi(figi):
    with open("Close.md", "r") as close_file:
        lines = close_file.readlines()
        figi_found = False

        for line in lines:
            figi_match = re.search(r"FIGI: (\S+)", line)
            if figi_match and figi_match.group(1) == figi:
                figi_found = True
            elif figi_found:
                close_value1 = extract_close_from_line(line)
                if close_value1 is not None:
                    return close_value1

    return None

def extract_open_from_line(line):
    match = re.search(r"open=Quotation\(units=(\d+), nano=(\d+)\)", line)
    if match:
        units = int(match.group(1))
        nano = int(match.group(2))
        open_value = units + nano * 1e-9  # Convert to a single number
        return open_value
    return None
async def main():
    sent_messages = set()
    last_cleanup_time = datetime.now(timezone.utc)
    # Создание словаря для хранения Total Volume по FIGI
    total_volumes = {}
    # Создайте объект timezone для UTC
    utc_timezone = timezone.utc
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
                    if figi in total_volumes and volume > (total_volumes[figi] * 45) and figi not in sent_messages:
                        await process_marketdata(figi)
                        current_figi = figi
                        close_value1 = get_close_value_for_figi(current_figi)
                        DayProcent = ((close_value - close_value1) / close_value1) * 100

                        # Открываем файл и считываем его содержимое
                        with open('tickers.txt', 'r') as file:
                            tickers_data = [line.strip().split() for line in file]
                        # Получаем текущий FIGI (замените это на ваш способ получения FIGI)
                        current_figi2 = figi # Замените на ваш текущий FIGI
                        # Ищем соответствующий тикер в данных из файла
                        for ticker, figi in tickers_data:
                            if figi == current_figi:
                                print(f'Тикер акции для FIGI {current_figi2}: {ticker}')
                                break
                        else:
                            print(f'Тикер для FIGI {current_figi2} не найден в файле.')
                        # Закрываем файл
                        file.close()

                        # Create a clickable link with the Tinkoff URL using HTML formatting
                        tinkoff_url = f"https://www.tinkoff.ru/invest/stocks/{ticker}"
                        link_text = f"<a href='{tinkoff_url}'>{ticker}</a>"


                        if figi in order_books:
                            order_book_data = order_books[figi]
                            # Process the order book data here
                            print("Order Book Data for FIGI:", figi)
                            print(order_book_data)

                        with open('StreamBook.md', 'r') as file:
                            data = file.read()

                        # Извлечение списков bids из данных
                        bids_data_list = re.findall(r'bids=\[(.*?)\]', data)

                        total_bids_quantity = 0
                        for bids_data in bids_data_list:
                            # Извлечение значений quantity из списка bids
                            bids_quantities = re.findall(r'quantity=(\d+)', bids_data)

                            # Преобразование значений quantity в целые числа и вычисление их суммы
                            total_bids_quantity += sum(int(quantity) for quantity in bids_quantities)

                        # Извлечение списков asks из данных
                        asks_data_list = re.findall(r'asks=\[(.*?)\]', data)

                        total_asks_quantity = 0
                        for asks_data in asks_data_list:
                            # Извлечение значений quantity из списка asks
                            asks_quantities = re.findall(r'quantity=(\d+)', asks_data)

                            # Преобразование значений quantity в целые числа и вычисление их суммы
                            total_asks_quantity += sum(int(quantity) for quantity in asks_quantities)

                        # Вычисление общего количества
                        total_quantity = total_bids_quantity + total_asks_quantity

                        # Вычисление процентов
                        bids_percentage = (total_bids_quantity / total_quantity) * 100 if total_quantity != 0 else 0
                        asks_percentage = (total_asks_quantity / total_quantity) * 100 if total_quantity != 0 else 0

                        moscow_tz = pytz.timezone('Europe/Moscow')
                        current_time3 = datetime.now(tz=moscow_tz)
                        current_time_formatted = current_time3.strftime('%Y-%m-%d %H:%M:%S')

                        # Extract the open value from the stream data
                        open_value = extract_open_from_line(line)
                        open_close_percentage = ((close_value - open_value) / open_value) * 100
                        # Отправка сообщения в Telegram, если объем в 2 раза больше Total Volume
                        message = f"<b>Аномальный объём</b>\n" \
                                  f"<b>{figi} {link_text} </b>\n\n" \
                                  f"<b>Общая стоимость составила:</b> {total_value:.2f} руб. ({volume} лотов)\n" \
                                  f"<b>Изменение цены: </b> {open_close_percentage:.2f}% \n"\
                                  f"<b>Цена сейчас: </b> {close_value}\n" \
                                  f"<b>Покупки: </b>{bids_percentage:.2f}% <b>Продажи:</b>{asks_percentage:.2f}%\n" \
                                  f"<b>Процент за день:</b> {DayProcent:.2f}%\n" \
                                  f"<b>Время отправки:</b> {current_time_formatted}\n" \

                        try:
                            bot.send_message(chat_id, message, parse_mode="HTML",disable_web_page_preview=True)
                            sent_messages.add(figi)
                            # Очистите файл StreamBook.md после успешной отправки сообщения
                            with open("StreamBook.md", "w") as streambook_file:
                                streambook_file.truncate(0)
                        except Exception as e:
                            print(f"Ошибка при отправке сообщения в Telegram: {e}")
                    if current_time - line_time < timedelta(minutes=1):
                        new_lines.append(line)
            with open("Stream.md", "w") as stream_file:
                stream_file.writelines(new_lines)

        if current_time - last_cleanup_time >= timedelta(minutes=1):
            sent_messages.clear()  # Очищаем множество отправленных сообщений
            last_cleanup_time = current_time  # Обновляем время последней очистки

        time.sleep(2.5)

if __name__ == "__main__":
    asyncio.run(main())
