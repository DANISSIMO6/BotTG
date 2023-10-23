import asyncio

import warnings
from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)
import pytz

TOKEN = "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ"

async def main():
    async def request_iterator():
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[
                    CandleInstrument(
                        figi="BBG004730N88",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
            request_iterator()
        ):
            if marketdata and marketdata.candle:
                candle = marketdata.candle
                figi = candle.figi
                open_quotation = f"{candle.open.units},{candle.open.nano}"
                close_quotation = f"{candle.close.units},{candle.close.nano}"
                volume = candle.volume
                time = candle.time.astimezone(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
                last_trade_ts = candle.last_trade_ts.astimezone(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                with open('Stream.md', 'a') as f:
                    f.write(f"FIGI: {figi}, Open: {open_quotation}, Close: {close_quotation}, Volume: {volume}, Time: {time}, Last Trade Time: {last_trade_ts}\n")

if __name__ == "__main__":
    asyncio.run(main())
