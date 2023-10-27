import os
import schedule
import time
from datetime import datetime, timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

TOKEN = 't.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ'

# Define a list of figi values
figi_list = [
    # ... Ваш список FIGI-значений здесь
]

def fetch_data():
    with Client(TOKEN) as client:
        # Create a single file for all figi values
        with open('Close.md', 'w') as file:
            for figi in figi_list:
                file.write(f"FIGI: {figi}\n")
                for candle in client.get_all_candles(
                    figi=figi,
                    from_=now() - timedelta(days=1),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
                ):
                    # Write the candle data to the single file
                    file.write(str(candle) + '\n')

def job():
    # Clear the file before writing new data
    with open('Close.md', 'w') as file:
        pass
    fetch_data()

# Define the time for the job to run (10:00 AM)
target_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

while True:
    current_time = datetime.now()
    # Check if it's a weekday and the current time matches the target time
    if current_time.weekday() < 5 and current_time == target_time:
        job()
    time.sleep(60)  # Check every minute
