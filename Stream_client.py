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
    "BBG001M2SC01", "BBG004730N88", "BBG0047315Y7", "BBG004731354", "BBG00475KKY8", "BBG004731032", "BBG004730RP0",
    "BBG004S684M6", "BBG004731489", "BBG004S681M2", "BBG000NLCCM3", "BBG000R607Y3", "BBG004RVFFC0", "BBG004S68829",
    "BBG004S681B4", "BBG0047315D0", "BBG00475K6C3", "BBG00475KHX6", "BBG000Q7ZZY2", "BBG006L8G4H1", "BBG004S689R0",
    "BBG000FWGSZ5", "BBG004S688G4", "BBG00QPYJ5H0", "BBG008F2T3T2", "BBG004S68507", "BBG004RVFCY3", "BBG00Y91R9T3",
    "BBG004S68B31", "BBG004S68CV8", "BBG004S68BH6", "BBG004S681W1", "BBG004730JJ5", "BBG00475K2X9", "BBG004S68758",
    "BBG004S68473", "BBG004730ZJ9", "BBG000QF1Q17", "BBG000R04X57", "BBG000RMWQD4", "BBG004S686N0", "BBG004S682Z6",
    "BBG00F6NKQX3", "BBG004S68BR5", "BBG009GSYN76", "BBG000GQSRR5", "BBG004S68696", "BBG004PYF2N3", "BBG004S685M3",
    "BBG0029SFXB3", "BBG004TC84Z8", "BBG000NLC9Z6", "TCS2207L1061", "BBG000RTHVK7", "BBG000LNHHJ9", "BBG004S68614",
    "BBG000PZ0833", "BBG004S683W7", "BBG007N0Z367", "BBG00JXPFBN0", "BBG000GQSVC2", "BBG00475JZZ6", "BBG004S686W0",
    "BBG002B9T6Y1", "BBG000K3STR7", "BBG004S68FR6", "BBG000QJW156", "BBG002B9MYC1", "BBG004S687W8", "BBG000VFX6Y4",
    "BBG002B298N6", "BBG00BGKYH17", "BBG004S68598", "BBG0100R9963", "BBG000W325F7", "BBG002458LF8", "BBG000V07CB8",
    "BBG004S68DD6", "BBG000VJMH65", "BBG000BXPZB7", "BBG000TY1CD1", "BBG004S68C39", "BBG004S687G6", "BBG000RK52V1",
    "BBG00Y3XYV94", "BBG0029SG1C1", "BBG000LWNRP3", "BBG000RJWGC4", "BBG004Z2RGW8", "BBG00F9XX7H4", "BBG000BN56Q9",
    "BBG000BX7DH0", "BBG000QFH687", "BBG005D1WCQ1", "BBG000VG1034", "BBG000VKG4R5", "BBG00HY6V6H5", "BBG000VQWH86",
    "BBG004S68CP5", "BBG000RP8V70", "BBG004S68JR8", "BBG002W2FT69", "BBG000NLB2G3", "BBG000SK7JS5", "BBG003LYCMB1",
    "BBG000RJL816", "BBG000RG4ZQ4", "BBG000VH7TZ8", "BBG000Q7GJ60", "BBG000C7P5M7", "BBG008HD3V85", "BBG000PKWCQ7",
    "BBG000MZL2S9", "BBG000Q7GG57", "BBG00172J7S9", "BBG000TJ6F42", "BBG000MZL0Y6", "TCS00A0JNXF9", "BBG002YFXL29",
    "BBG002B2J5X0", "BBG000SR0YS4", "BBG000BBV4M5", "BBG000BSBZH7", "BBG002BCQK67", "BBG000DBD6F6", "BBG0027F0Y27",
    "BBG0019K04R5", "BBG000G25P51", "BBG0014PFYM2"
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
                            interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
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
