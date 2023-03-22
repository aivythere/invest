import sqlite3
import time
from tinkoff.invest import Client, SecurityTradingStatus
import hardconfig
import pytz
import common_libs
import datetime
from threading import Thread

# TODO    Здесь будет цикл, обновляющий postgresql базу где-то на ВДСке каждые хуй-знает-сколько секунд по всем акциям
# TODO    один хуй, их будет относительно немного. С криптой в разы проще

decode_market_state = {
        SecurityTradingStatus.SECURITY_TRADING_STATUS_NORMAL_TRADING: "OPEN",
        SecurityTradingStatus.SECURITY_TRADING_STATUS_UNSPECIFIED: "CLOSED (UNSPECIFIED)",
        SecurityTradingStatus.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING: "CLOSED (NOT_AVAILABLE_FOR_TRADING)",
        SecurityTradingStatus.SECURITY_TRADING_STATUS_BREAK_IN_TRADING: "CLOSED (BRAKE_IN_TRADING)",
        # SecurityTradingStatus.
    }


def getAllFigi() -> list:
    db = sqlite3.connect(hardconfig.TEMP_DBFILE)
    cursor = db.cursor()
    cursor.execute(f"SELECT figi FROM {hardconfig.STOCK_INFO_TABLE_NAME}")
    row = cursor.fetchall()
    return [figi[0] for figi in row]


def tinkoff_get_stock_price(figi_list: list[str]) -> dict:
    with Client(hardconfig.TINKOFF_TOKEN) as client:
        TARGET_TZ = pytz.timezone(hardconfig.SERVER_TIMEZONE)
        price = client.market_data.get_last_prices(figi=figi_list)
        market_state = client.market_data.get_trading_statuses(instrument_ids=figi_list)
        result = {}

        for price in price.last_prices:
            result[price.figi] = {
                "price": common_libs.convertPrice(price.price),
                "last_price_update_date": f"{price.time.replace(tzinfo=pytz.utc).astimezone(TARGET_TZ).date()}"
                                          f" {price.time.replace(tzinfo=pytz.utc).astimezone(TARGET_TZ).time()}",
            }
        for elem in market_state.trading_statuses:
            try:
                result[elem.figi]["market_state"] = decode_market_state[elem.trading_status]
            except KeyError:
                result[elem.figi]["market_state"] = str(elem.trading_status)

        return result


def start_updating():
    db = sqlite3.connect(hardconfig.TEMP_DBFILE)
    cursor = db.cursor()
    while True:
        res = tinkoff_get_stock_price(getAllFigi())
        for figi in res.keys():
            # print(figi, "    ", res[figi])
            query = f"UPDATE {hardconfig.STOCK_INFO_TABLE_NAME} SET " \
                    f"current_price = {res[figi]['price']}," \
                    f"last_market_change_percent = round(((current_price-last_price)/current_price)*100,2)," \
                    f"last_price_update_date = '{res[figi]['last_price_update_date']}'," \
                    f"last_market_change_amount = round(current_price-last_price, 2)," \
                    f"market_state = '{res[figi]['market_state']}' WHERE figi = '{figi}';"
            cursor.execute(query)
            db.commit()


        time.sleep(30)

def dailyPriceUpdate():
    db = sqlite3.connect(hardconfig.TEMP_DBFILE)
    cursor = db.cursor()
    while True:
        if datetime.datetime.now().hour == hardconfig.LAST_PRICE_UPDATE_HOUR:
            cursor.execute(
                f"UPDATE {hardconfig.STOCK_INFO_TABLE_NAME} SET last_price = current_price"
            )
        time.sleep(1200)


if __name__ == "__main__":
    start_updating()
    daily_price_update = Thread(target=dailyPriceUpdate)
    daily_price_update.start()
