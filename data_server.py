from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import data_types as dt
from datetime import datetime
import hardconfig
import sqlite3
import json

def loadStockView() -> dict:
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {hardconfig.STOCK_INFO_TABLE_NAME}")
    row = cursor.fetchall()
    res = {}
    for stock_info in row:
        res[stock_info[0]] = {
            "currency": stock_info[1],
            "current_price": stock_info[2],
            "last_price": stock_info[3],
            "last_change_amount": stock_info[4],
            "last_change_percent": stock_info[5],
            "legal_name": stock_info[6],
            "market_state": stock_info[7],
            "primary_color_rgba": stock_info[8],
            "name": stock_info[9],
            "logo_path": stock_info[10],
            "figi": stock_info[11]
        }
    return res

def loadCommon():
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT code FROM {hardconfig.STOCK_INFO_TABLE_NAME}")
    row = cursor.fetchall()
    return row


def loadPortfolioLookup(userid: int):
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    st_ = hardconfig.STOCK_INFO_TABLE_NAME
    pt_ = hardconfig.PROPERTY_INFO_TABLE_NAME
    ut_ = hardconfig.USERS_INFO_TABLE_NAME
    res = {}
    owned_tickers = cursor.execute(f"SELECT code FROM {pt_}"
                                   f" WHERE holder_id = {userid}").fetchall()
    for ticker in set(owned_tickers):
        # цена акции * количество купленных, прибыль, количество в портфеле, цена сейчас
        row = cursor.execute(f"SELECT ({st_}.current_price*{pt_}.count), ({st_}.current_price-{pt_}.buy_price),"
                                f" {pt_}.count, {st_}.current_price, {st_}.logo_path, {st_}.normal_name, {st_}.currency"
                                f" FROM {st_}, {pt_} WHERE {st_}.code = '{ticker[0]}' "
                                f"AND {pt_}.code = '{ticker[0]}' AND {pt_}.holder_id = {userid} ORDER BY {pt_}.count;").fetchone()
        res[ticker[0]] = {
            "total_stock_price": round(row[0],2),
            "profit": round(row[1], 2),
            "stock_count": row[2],
            "current_price": round(row[3], 2),
            "logo_path": row[4],
            "name": row[5],
            "currency": row[6]
        }
    tbr = cursor.execute(f"SELECT sum({st_}.current_price*{pt_}.count)+(SELECT money_rub_balance FROM {ut_} WHERE"
                         f" holder_id = {userid}),(SELECT money_rub_balance FROM {ut_} WHERE id = {userid}) FROM {st_}, {pt_},"
                         f" {ut_} WHERE {pt_}.code={st_}.code AND {pt_}.holder_id = {userid} AND {ut_}.id = {userid};").fetchone()
    total_balance = tbr[0]
    money_available = tbr[1]
    res['balance_data'] = {
        "total": total_balance if total_balance is not None else money_available,
        "money_avl": money_available
    }

    return res

def getForeignTickerInfo(ticker: str) -> dict:
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM stocks WHERE code = '{ticker}'")
    try:
        stock_info = cursor.fetchall()[0]
        return {
            "currency": stock_info[1],
            "current_price": stock_info[2],
            "last_price": stock_info[3],
            "last_change_amount": stock_info[4],
            "last_change_percent": stock_info[5],
            "legal_name": stock_info[6],
            "market_state": stock_info[7],
            "primary_color_rgba": stock_info[8],
            "name": stock_info[9],
            "logo_path": stock_info[10],
            "figi": stock_info[11],
            # "last_price_update_date":
            "gpt_predicted_price": stock_info[13],
            "yandex_predicted_price": stock_info[14],
            "sber_predicted_price": stock_info[15]
        }
    except IndexError:
        pass

def loadPreBuyLookup(userid: int, ticker: str):
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    # денежный доступный баланс, инфа по акции,
    st_ = hardconfig.STOCK_INFO_TABLE_NAME
    ut_ = hardconfig.USERS_INFO_TABLE_NAME
    query = f"SELECT {st_}.current_price, {st_}.normal_name, {st_}.logo_path, {ut_}.money_rub_balance FROM {st_}, {ut_} WHERE" \
            f" {st_}.code = '{ticker}' AND users.id = {userid};"
    row = cursor.execute(query).fetchone()
    if row is not None:
        return {
            "current_price": row[0],
            "name": row[1],
            "logo_path": row[2],
            "money_aval": row[3]
        }


def buyStock(id: int, amount: int, ticker: str):
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    st_ = hardconfig.STOCK_INFO_TABLE_NAME
    ut_ = hardconfig.USERS_INFO_TABLE_NAME
    pt_ = hardconfig.PROPERTY_INFO_TABLE_NAME
    _is_buy_possible = cursor.execute(f"SELECT {ut_}.money_rub_balance >= {st_}.current_price * {amount} FROM {st_}, "
                                      f"{ut_} WHERE {st_}.code = '{ticker}' AND {ut_}.id = {id};").fetchone()
    if _is_buy_possible is not None:
        if _is_buy_possible[0] == 0:
            return {"response": "FALSE"}

        _take_money_query = f"UPDATE {ut_} SET money_rub_balance = money_rub_balance - ((SELECT current_price FROM {st_}" \
                            f" WHERE code = '{ticker}') * {amount}) WHERE id = {id};"
        cursor.execute(_take_money_query)
        db.commit()

        date = str(datetime.now()).split(".")[0]
        _are_already_have_stock = cursor.execute(f"SELECT EXISTS (SELECT 1 FROM {pt_} "
                                                 f"WHERE holder_id = {id} AND code = '{ticker}')").fetchone()[0]

        if _are_already_have_stock == 0:
            insert_buyquery = f"INSERT INTO {pt_} (holder_id, code, buy_date, buy_price, count)" \
                              f" VALUES ({id}, '{ticker}', '{date}', (SELECT current_price FROM {st_}" \
                              f" WHERE code = '{ticker}'), {amount})"
            cursor.execute(insert_buyquery)
            db.commit()
            return {"response": "TRUE",
                    "amount": amount,
                    "logo_path": cursor.execute(f"SELECT logo_path FROM {st_} WHERE code = '{ticker}';").fetchone()[0],
                    "spend_amount": cursor.execute(f"SELECT current_price*{amount}"
                                                   f" FROM {st_} WHERE code = '{ticker}';").fetchone()[0]}

        else:
            update_buyquery = f"UPDATE {pt_} SET count = count + {amount} WHERE code = '{ticker}' AND holder_id = {id};"
            cursor.execute(update_buyquery)
            db.commit()
            return {"response": "TRUE",
                    "amount": amount,
                    "logo_path": cursor.execute(f"SELECT logo_path FROM {st_} WHERE code = '{ticker}';").fetchone()[0],
                    "spend_amount": cursor.execute(f"SELECT current_price*{amount}"
                                                   f" FROM stocks WHERE code = '{ticker}';").fetchone()[0]}


def loadPreSellLookup(userid: int, ticker: str):
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    st_ = hardconfig.STOCK_INFO_TABLE_NAME
    ut_ = hardconfig.USERS_INFO_TABLE_NAME
    pt_ = hardconfig.PROPERTY_INFO_TABLE_NAME
    ticker = ticker.upper()
    _is_possible = cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {pt_} WHERE {pt_}.code = '{ticker}'"
                                  f" AND {pt_}.holder_id = 1), {st_}.normal_name, {st_}.current_price,"
                                  f" {st_}.logo_path FROM {st_} WHERE code = '{ticker}';").fetchone()
    if _is_possible[0] == 0:
        return {
            'response': 'FALSE',
            'property_price': 0,
            'logo_path': _is_possible[3],
            'name': _is_possible[1],
            'current_price': _is_possible[2]
        }

    _prebuy_info = cursor.execute(f"SELECT ({pt_}.count*{st_}.current_price),"
                                  f" {st_}.normal_name, {st_}.current_price, {pt_}.count,"
                                  f" {st_}.logo_path FROM {st_}, {pt_} WHERE {st_}.code = "
                                  f"'{ticker}' AND {pt_}.code = '{ticker}' AND {pt_}.holder_id = {userid};").fetchone()


    return {
        'response': 'TRUE',
        'current_price': _prebuy_info[2],
        'name': _prebuy_info[1],
        'property_price': _prebuy_info[0],
        'property_count': _prebuy_info[3],
        'logo_path': _prebuy_info[4]
    }  # s



def sellStock(id, ticker, amount):
    db = sqlite3.connect('stocks.db')
    cursor = db.cursor()
    st_ = hardconfig.STOCK_INFO_TABLE_NAME
    ut_ = hardconfig.USERS_INFO_TABLE_NAME
    pt_ = hardconfig.PROPERTY_INFO_TABLE_NAME

    _is_sell_possible = cursor.execute(f"SELECT {pt_}.count >= {amount} FROM {pt_} WHERE {pt_}.code = '{ticker}'"
                                       f" AND {pt_}.holder_id = {id};").fetchone()
    if _is_sell_possible is None or _is_sell_possible[0] == 0:
        return {"response": "FALSE"}

    cursor.execute(f"UPDATE {ut_} SET money_rub_balance = (SELECT {pt_}.count*{st_}.current_price FROM {st_},"
                   f" {pt_} WHERE {st_}.code = '{ticker}' AND {pt_}.code = '{ticker}' AND {pt_}.holder_id = {id}) WHERE {ut_}.id = {id};"
                   )
    db.commit()
    cursor.execute(f"UPDATE {pt_} SET count = count - {amount} WHERE code = '{ticker}' AND holder_id = {id};")
    db.commit()
    _is_sold_out = cursor.execute(f"SELECT count FROM {pt_} WHERE code = '{ticker}' AND holder_id = {id};").fetchone()[0]
    print(_is_sold_out, type(_is_sold_out), _is_sold_out<=0)
    if _is_sold_out <= 0:
        cursor.execute(f"DELETE FROM {pt_} WHERE {pt_}.code = '{ticker}' AND {pt_}.holder_id = {id};")
        db.commit()
    _out_data = cursor.execute(f"SELECT logo_path, {amount}*current_price FROM {st_} WHERE code = '{ticker}';").fetchone()
    return {"response": "TRUE",
            "amount": amount,
            "sum": _out_data[1],
            "logo_path": _out_data[0]}


def loadAiText(code):
    msg_rice = """
Из выводов, сделанных нейронной сетью на основе анализа рынка, следует, что цена данной акции может существенно возрасти в ближайшем будущем.
    """
    msg_low = """
Согласно данным, полученным нейросетью, можно ожидать падения цены на данную акцию в ближайшее время
    """
    return {"msg_rice": msg_rice, "msg_low": msg_low}



def checkPath(str_: str) -> bool:
    for i in server_methods:
        if i in str_:
            return True
    return False


def antiInject(str_: str) -> str:
    for i in clean_str:
        str_ = str_.replace(i, "")
    return str_


UNSECURE = True
clean_str = ['/', '.', ',', '//', "'", '"']
server_methods = ['tc_lookup', 'fg_lookup', 'LSV_lookup', 'cm_lookup',
                  'pf_lookup', 'pb_lookup', 'BUY', 'SELL', 'ps_lookup']


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # async debugging and tests
        # time.sleep(.1)
        # TODO Обмен с клиентом сообщениями, прила сама в себе шифрует сообщение по ключу,
        #      а здесь сервак по этому же ключу расшифровывает все

        if self.headers['User-Agent'] == hardconfig.SECURE_SERVER_REQUEST_HASH or UNSECURE:
            if checkPath(self.path):
                datatarget = antiInject(self.path.split("::")[-1])
                method = antiInject(self.path.split("::")[-2])

                if method == 'tc_lookup':
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    self.wfile.write(json.dumps(getForeignTickerInfo(datatarget)).encode('utf-8'))

                elif method == 'LSV_lookup':

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    self.wfile.write(json.dumps(loadStockView()).encode('utf-8'))

                elif method == 'cm_lookup':
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    self.wfile.write(json.dumps(loadCommon()).encode('utf-8'))

                elif method == "ai_text":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    self.wfile.write(json.dumps(loadAiText()).encode('utf-8'))

                elif method == "pf_lookup":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    id = int(datatarget)
                    self.wfile.write(json.dumps(loadPortfolioLookup(id)).encode('utf-8'))

                elif method == "pb_lookup":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    try:
                        _id, ticker = datatarget.split("_")
                        self.wfile.write(json.dumps(loadPreBuyLookup(_id, ticker)).encode('utf-8'))
                    except ValueError:
                        pass
                elif method == "BUY":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    try:
                        id_, ticker, amount  = datatarget.split("_")
                        self.wfile.write(json.dumps(buyStock(id=id_, ticker=ticker, amount=amount)).encode('utf-8'))
                    except ValueError:
                        pass

                elif method == "ps_lookup":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    try:
                        _id, ticker = datatarget.split("_")
                        self.wfile.write(json.dumps(loadPreSellLookup(_id, ticker)).encode('utf-8'))
                    except ValueError:
                        pass

                elif method == "SELL":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    try:
                        id_, ticker, amount = datatarget.split("_")
                        self.wfile.write(json.dumps(sellStock(id=id_, ticker=ticker, amount=amount)).encode('utf-8'))
                    except ValueError:
                        pass

        else:
            self.send_response(401)
            self.send_header("Content-type", "text/html")
            self.end_headers()


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()