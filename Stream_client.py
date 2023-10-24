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
TOKEN = "t.OpTGgjrL00hW6AruBxEr9vhtxNd2gWxmVJ8uE2qEex-i699xS8C4PhGpyASIQbiL6U3Z109SsnEOHO7xQ5HgYQ"
# Список FIGIs
FIGIs = [
    "BBG001M2SC01"
]

async def main():
    data = []

    async def request_iterator():
        for figi in FIGIs:
            yield MarketDataRequest(
                subscribe_candles_request=SubscribeCandlesRequest(
                    subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                    instruments=[
                        CandleInstrument(
                            figi=figi,
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
            print(marketdata)
            with open('Stream.md', 'a') as stream:
                stream.write(str(marketdata) + '\n')


if __name__ == "__main__":
    asyncio.run(main())
