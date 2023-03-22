from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import NoTransition
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
import appcolor
from font.custom_font import SFLabel
import re
import hardconfig
from tinkoff.invest import Quotation
from tinkoff.invest import CandleInterval
from datetime import datetime, timedelta
from kivy.metrics import dp

from investing.font import custom_font

decode_graph = {
    "graph_day": (CandleInterval.CANDLE_INTERVAL_30_MIN, datetime.now() - timedelta(days=1), datetime.now()),
    "graph_week": (CandleInterval.CANDLE_INTERVAL_4_HOUR, datetime.now() - timedelta(days=7), datetime.now()),
    "graph_month": (CandleInterval.CANDLE_INTERVAL_DAY, datetime.now() - timedelta(days=31), datetime.now()),
    "graph_year": (CandleInterval.CANDLE_INTERVAL_MONTH, datetime.now() - timedelta(days=365), datetime.now())
}


def decorateNumberDigits(string):
    return '{:,}'.format(float(string)).replace(',', ' ')


def OfflineStocksTest():
    return {
        "VKCO": {
            "name": "VK",
            "current_price": "1 920,2 ₽",
            "last__change": "-3,6 ₽",
            "logo_path": "./img/vklogo.png",
            "primary_color_rgba": (8 / 255, 120 / 255, 1, .8)
        },
        "YNDX": {
            "name": "Yandex",
            "current_price": "1 613,2 ₽",
            "last_change": "-30,8 ₽",
            "logo_path": "./img/yandexlogo.png",
            "primary_color_rgba": (1, 93 / 255, 93 / 255, 1)
        },
        "LKOH": {
            "name": "Лукойл",
            "current_price": "4 152,5 ₽",
            "last_change": "+137,5 ₽",
            "logo_path": "./img/lukoillogo.png",
            "primary_color_rgba": (1, 93 / 255, 93 / 255, 1)
        },
        "GAZP": {
            "name": "Газпром",
            "current_price": "299,5 ₽",
            "last_change": "+4,8 ₽",
            "logo_path": "./img/gazpromlogo.png",
            "primary_color_rgba": (151 / 255, 227 / 255, 1, 1)
        }
        ,
        "POLY": {
            "name": "Polymetal",
            "current_price": "551,0 ₽",
            "last_change": "+16,5 ₽",
            "logo_path": "./img/polymetallogo.png",
            "primary_color_rgba": (0.5, 0.5, .5, 1)
        },
        "GMKN": {
            "name": "Норильский никель",
            "current_price": "20 080,5 ₽",
            "last_change": "-82,1 ₽",
            "logo_path": "./img/nornikelogo.png",
            "primary_color_rgba": (151 / 255, 227 / 255, 1, 1)
        }
    }


def loadCryptoView() -> dict:
    # получаем с бд список акций и хуйни, возвращаем словарь виджетов??
    # хуй знает. список инфы скорее. ниже просто тест
    return {
        "BTC": {
            "currency": 'RUB',
            "current_price": '123818312',
            "last_price": '12314123',
            "last_change_amount": '178239',
            "last_change_percent": '90',
            "legal_name": 'BTC INCORPORATE',
            "market_state": 'OPEN',
            "primary_color_rgba": '(100/255, 150/255, 150/255, 1)',
            "name": 'Bitcoin',
            "logo_path": './img/btclogo.png',
            "figi": 'none'
        },
        "ETH": {
            "currency": 'RUB',
            "current_price": '123818312',
            "last_price": '12314123',
            "last_change_amount": '178239',
            "last_change_percent": '90',
            "legal_name": 'ETH INCORPORATE',
            "market_state": 'OPEN',
            "primary_color_rgba": '(100/255, 150/255, 50/255, 1)',
            "name": 'Bitcoin',
            "logo_path": './img/ethlogo.png',
            "figi": 'none'
        },
        "SOL": {
            "currency": 'RUB',
            "current_price": '123818312',
            "last_price": '12314123',
            "last_change_amount": '178239',
            "last_change_percent": '90',
            "legal_name": 'BTC INCORPORATE',
            "market_state": 'OPEN',
            "primary_color_rgba": '(0/255, 150/255, 150/255, 1)',
            "name": 'Bitcoin',
            "logo_path": './img/sollogo.png',
            "figi": 'none'
        },
        "USDC":
            {
                "currency": 'RUB',
                "current_price": '123818312',
                "last_price": '12314123',
                "last_change_amount": '178239',
                "last_change_percent": '90',
                "legal_name": 'BTC INCORPORATE',
                "market_state": 'OPEN',
                "primary_color_rgba": '(0/255, 150/255, 0/255, .5)',
                "name": 'Bitcoin',
                "logo_path": './img/btclogo.png',
                "figi": 'none'
            }
    }


def bbClearText(text: str):
    return re.sub('\[.*?]', '', text)


def convertPrice(input: Quotation):
    """
        Смотри, мы работает по РУ-Акциям, поэтому на валюту похуй. В Quotation возвращается
        сумма без указания валюты. Что имеем

        units: 114
        nano: 250000000

        Это 114,25

        units: 0
        nano: 10000000

        А это 0,01 - сложная хуйня. Отчилается количеством знаков.

        250000000 - 9 знаков
        10000000 - 8 знаков
        Вот теперь уже понятнее. Все это  надо конвертнуть красиво
        :return:
        """  # Тут документация и мысли, не удаляй
    rub = input.units
    decimals = input.nano
    max_quotation_nano = 1_000_000_000
    return rub + decimals / max_quotation_nano


class ImageButton(ButtonBehavior, Image):
    def __init__(self, source: str, size_hint: list, inner_data, pos_hint=None,
                 x=None, y=None, on_release_func=None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.inner_data = inner_data
        self.on_release_func = on_release_func if on_release_func is not None else None
        self.opacity = 1
        self.size_hint = size_hint
        if pos_hint is not None:
            self.pos_hint = pos_hint
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    def on_release(self):
        if self.on_release_func is not None:
            self.on_release_func(self.inner_data)
        else:
            print("imgbutton onrelease function None")


class NavigationBar(MDFloatLayout):
    def __init__(self, screen_manager_instance):
        super().__init__()
        self.size_hint_y = None
        self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
        self.radius = 20
        self.height = dp(50)
        self.screen_manager_instance = screen_manager_instance

        self.elevationbar_inner_grid = MDGridLayout(cols=3, pos_hint={"center_x": .5, "center_y": .5},
                                                    padding=20, spacing=50)
        self.elevationbar_inner_grid.add_widget(
            ImageButton(source='./img/profile_section_logo.png', size_hint=[.1, .1],
                        on_release_func=self.item_on_press, allow_stretch=True, inner_data='Account')
        )
        self.elevationbar_inner_grid.add_widget(
            ImageButton(source='./img/stock_section_logo.png', size_hint=[.1, .1],
                        on_release_func=self.item_on_press, allow_stretch=True, inner_data='Stocks')
        )
        self.elevationbar_inner_grid.add_widget(
            ImageButton(source='./img/info_section_logo.png', size_hint=[.1, .1],
                        on_release_func=self.item_on_press, allow_stretch=True, inner_data='Info')
        )

        self.add_widget(self.elevationbar_inner_grid)

    def item_on_press(self, *args):
        if self.screen_manager_instance.current != args[-1]:
            self.screen_manager_instance.transition = NoTransition()
            self.screen_manager_instance.current = args[-1]
            self.screen_manager_instance.transition = hardconfig.DEFAULT_TRANSITION


class BuySellButotns(MDGridLayout):
    def __init__(self, on_release_func, is_aval_for_sell=True):
        super(BuySellButotns, self).__init__()
        self.cols = 2
        self.rows = 1
        # self.padding = [0, 20, 0, 20]
        self.spacing = 20
        self.size_hint_y = .7
        self.buy_button = self.BuyButton(on_release_func)
        self.sell_button = self.SellButton(on_release_func)
        self.add_widget(self.buy_button)
        self.add_widget(self.sell_button)

    class BuyButton(MDCard):
        def __init__(self, on_release_func):
            super().__init__()
            self.radius = hardconfig.PRIMARY_CARD_RADIUS
            self.ripple_behavior = True
            self.ripple_alpha = hardconfig.RIPPLE_ALPHA
            self.on_release_func = on_release_func
            self.disabled = True
            self.md_bg_color = get_color_from_hex(appcolor.green_buy_hex)
            self.buy_title = SFLabel(text=f'[ref=buy][color=FFFFFF]{"Купить".upper()}[/color][/ref]', size_hint=[1, 1],
                                     font_style='Light', pos_hint={'center_x': .5, 'center_y': .5})
            self.buy_title.bind(on_ref_press = on_release_func)
            self.add_widget(self.buy_title)

        def on_release(self):
            self.on_release_func("buy")

    class SellButton(MDCard):
        def __init__(self, on_release_func):
            super().__init__()
            self.radius = hardconfig.PRIMARY_CARD_RADIUS
            self.ripple_behavior = True
            self.ripple_alpha = hardconfig.RIPPLE_ALPHA
            self.disabled = True
            self.on_release_func = on_release_func
            self.md_bg_color = get_color_from_hex(appcolor.red_sell_hex)
            self.sell_title = SFLabel(text=f'[ref=sell][color=FFFFFF]{"Продать".upper()}[/color][/ref]', size_hint=[1, 1],
                                     font_style='Light', pos_hint={'center_x': .5, 'center_y': .5})
            self.sell_title.bind(on_ref_press = on_release_func)
            self.add_widget(self.sell_title)

        def on_release(self):
            self.on_release_func("sell")


class StockCardItem(MDCard):
    def __init__(self, image_path: str, item_name: str, item_ticker: str,
                 size_hint_y=None, height_dp=hardconfig.PROPERTY_CARD_HEIGHT_DP):
        super().__init__()
        inner_grid = MDGridLayout(cols=3, rows=1, spacing=30, padding=30)
        self.height = height_dp
        self.radius = hardconfig.PRIMARY_CARD_RADIUS
        if size_hint_y is not None:
            self.size_hint_y = size_hint_y
        self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
        self.stock_pfp = ImageButton(source=image_path, inner_data=item_ticker, size_hint=[.4, .4])
        self.item_name_label = custom_font.SFLabel(text=item_name, halign='left')
        self.price_data_label = custom_font.AKLabelLoader(text=f"", halign='right')
        inner_grid.add_widget(self.stock_pfp)
        inner_grid.add_widget(self.item_name_label)
        inner_grid.add_widget(self.price_data_label)

        self.add_widget(inner_grid)


class CardStockPropertyItem(MDCard):
    def __init__(self, image_path: str, item_name: str, item_ticker: str,
                 price_data: str, on_release_func, stockhaving_data=None,
                 size_hint_y=None,height_dp=hardconfig.PROPERTY_CARD_HEIGHT_DP):
        super().__init__()
        self.inner_data = item_ticker

        inner_grid = MDGridLayout(cols=3, rows=1, spacing=30, padding=30)
        self.height = height_dp
        self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
        self.on_release_func = on_release_func
        self.ripple_behavior = True
        self.ripple_alpha = hardconfig.RIPPLE_ALPHA
        if size_hint_y is not None:
            self.size_hint_y = size_hint_y
        self.stock_pfp = ImageButton(source=image_path, on_release_func=on_release_func,
                                            inner_data=item_ticker, size_hint=[.4, .4])
        self.item_name_label = custom_font.SFLabel(text=f"[size=15dp]{item_name}[/size]\n"
                f"[size=12dp]{stockhaving_data if stockhaving_data is not None else item_ticker}[/size]", halign='left')
        self.price_data_label = custom_font.SFLabel(text=f'{price_data}', halign='right', font_size="15dp")
        inner_grid.add_widget(self.stock_pfp)
        inner_grid.add_widget(self.item_name_label)
        inner_grid.add_widget(self.price_data_label)

        self.add_widget(inner_grid)

    def on_release(self):
        self.on_release_func(self.inner_data)

class MoneyPropertyItem(MDCard):
    def __init__(self, image_path: str, item_name: str,
                 item_ticker: str, having_data: str, height_dp=40):
        super().__init__()
        inner_grid = MDGridLayout(cols=3, rows=1, spacing=30, padding=30)
        self.height = dp(height_dp)
        self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
        self.stock_pfp = ImageButton(source=image_path, inner_data=item_ticker,
                                                 size_hint=[.4, .4])
        self.item_name_label = custom_font.SFLabel(text=f"[size=15dp]{item_name}[/size]", halign='left')
        self.price_data_label = custom_font.SFLabel(text=f'{having_data}', halign='right', font_size="15dp")
        inner_grid.add_widget(self.stock_pfp)
        inner_grid.add_widget(self.item_name_label)
        inner_grid.add_widget(self.price_data_label)

        self.add_widget(inner_grid)