from tinkoff.invest import Client, GetLastPricesResponse, LastPrice, Quotation
import hardconfig
import common_libs


def getCandles(figi: str, period: str):
    period, from_, to = common_libs.decode_graph[period]

    with Client(hardconfig.TINKOFF_TOKEN) as client:
        candles = client.market_data.get_candles(
                    figi = figi,
                    from_= from_,
                    to = to,
                    interval = period
                )
        return candles