import re
import telebot
from datetime import datetime, timedelta, timezone
import time
import os
import asyncio
from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    SubscribeOrderBookRequest,
    OrderBookInstrument,
)

TOKEN = "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ"

sent_messages = set()
order_books = {}  # Add a dictionary to store order book data

# Создайте объект timezone для UTC
utc_timezone = timezone.utc
stream_data = []
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
    await asyncio.sleep(1)

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

async def main():
    last_cleanup_time = datetime.now(timezone.utc)
    # Создание словаря для хранения Total Volume по FIGI
    total_volumes = {}
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
                        await process_marketdata(figi)
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
                        # Получить текущее время
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_cleanup_time = datetime.now(timezone.utc)
                        line_time = datetime.now(timezone.utc)
                        # Отправка сообщения в Telegram, если объем в 2 раза больше Total Volume
                        message = f'Аномальный объём\n' \
                                  f'Аномальное изменение цены\n' \
                                  f'Изменение цены:\n' \
                                  f'Объём: {total_value}М₽\n' \
                                  f"Покупка: {bids_percentage:.2f}%\n" \
                                  f"Продажа: {asks_percentage:.2f}%\n" \
                                  f'Цена:\n' \
                                  f'Изменение за день:'\
                                  f"Время отправки: {current_time}\n"

                        bot.send_message(chat_id, message)
                        sent_messages.add(figi)
                    # Clear the content of StreamBook.md
                    with open('StreamBook.md', 'w') as file:
                        file.write('')

                    sent_messages.add(figi)

            if current_time - line_time < timedelta(minutes=6):
                new_lines.append(line)
            with open("Stream.md", "w") as stream_file:
                stream_file.writelines(new_lines)

            time.sleep(2.5)


if __name__ == "__main__":
    asyncio.run(main())
