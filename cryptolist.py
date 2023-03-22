# pre-render
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import MDScrollView
from common_libs import loadCryptoView


class CryptoList(MDScrollView):
    def __init__(self, system_theme: str, chooseItemFunc, stock_items=None):
        super().__init__()
        self.id = "crypto_scrollview"
        if stock_items is None:
            stock_items = loadCryptoView()
        cryptoList = MDList(padding=20, id="CryptoList_MDList")
        self.add_widget(cryptoList)
        for i in stock_items:
            cryptoList.add_widget(
                StockItem(
                    code=i, stock_name=stock_items[i]['name'], price=stock_items[i]['current_price'],
                    last_change_amount=stock_items[i]['last_change_amount'],
                    last_change_percent=stock_items[i]['last_change_percent'],
                    logo_path=stock_items[i]['logo_path'], chooseItemFunc=chooseItemFunc,
                    currency="RUB" # TODO убрать нахуй когда будет норм подтяг инфы с БД
                )
            )
