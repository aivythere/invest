import json
import sqlite3
import certifi
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.transition import MDSlideTransition
from investing import common_libs, hardconfig, appcolor, data_types
from investing.font import custom_font


class SellScreen(MDScreen):
    def __init__(self, screen_manager_instance, upper_screen_reload_func):
        super().__init__()
        self.name = "SellScreen"
        self.main_scrollview = MDScrollView(do_scroll_x=True, do_scroll_y=False)
        self.maingrid = MDGridLayout(cols=1, rows=5, spacing=50, padding=30,
                                     size_hint_x=None, width=hardconfig.WINDOW_SIZE[0] * 1.99)
        self.ticker = None
        self.screen_manager_instance = screen_manager_instance
        self.upper_screen_reload_func = upper_screen_reload_func

        self.Title_instance = self.Title(self.goBack)
        self.stock_card_instance = common_libs.CardStockPropertyItem(
            image_path='./img/blank.png', item_name='',
            item_ticker='', stockhaving_data='',
            price_data='', size_hint_y=.2,
            on_release_func=self.goBack
        )
        self.LowerLayout_instance = self.LowerLayout(buy_approve_func=self.sellStocks)
        self.maingrid.add_widget(self.Title_instance)
        self.maingrid.add_widget(self.stock_card_instance)
        self.maingrid.add_widget(self.LowerLayout_instance)
        self.maingrid.add_widget(MDGridLayout(size_hint_y=.5))

        self.main_scrollview.add_widget(self.maingrid)
        self.add_widget(self.main_scrollview)

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        super(SellScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        try:
            if (touch.x - self.touch_start_x) > 200 and (touch.y - self.touch_start_y) < 250:
                self.goBack()
            super(SellScreen, self).on_touch_up(touch)
        except TypeError:
            pass

    def on_leave(self, *args):
        self.LowerLayout_instance.count_textfield.text = ''
        self.LowerLayout_instance.approve_button.disabled = True
        self.stock_card_instance.stock_pfp.source = './img/blank.png'
        self.stock_card_instance.item_name_label.text = ''
        self.stock_card_instance.price_data_label.text = ''

    def goBack(self, *args):
        if self.screen_manager_instance.current == self.name:
            self.screen_manager_instance.transition = MDSlideTransition(direction='right',
                                                                        duration=hardconfig.ANY_TRANSITION_DURATION)
            self.upper_screen_reload_func(self.ticker)
            self.screen_manager_instance.current = "StockViewing"
            self.screen_manager_instance.transition = hardconfig.DEFAULT_TRANSITION

    def reload(self, ticker):
        Clock.schedule_once(lambda x:self.getAsyncData(ticker))
        self.ticker = ticker

    def success_prebuy(self, *args):
        response = json.loads(args[-1])
        self.stock_card_instance.stock_pfp.source = response['logo_path']
        self.stock_card_instance.price_data_label.text = data_types.PriceData(currency='RUB',price=response['current_price']).price_text
        if response['response'] == "FALSE":
            ...
            self.LowerLayout_instance.approve_button.disabled = True
            self.LowerLayout_instance.count_textfield.text = ''
            self.LowerLayout_instance.count_textfield.helper_text = f'Доступно 0'

            self.stock_card_instance.item_name_label.text = f"{response['name']}" \
                                                            f"\n[size=13dp][color={appcolor.light_grey_hex}]0 шт.[/color][/size]"
        else:
            self.property_count = response["property_count"]
            self.LowerLayout_instance.approve_button.disabled = False
            self.LowerLayout_instance.count_textfield.text = ''
            self.stock_card_instance.item_name_label.text = f"{response['name']}\n" \
                                                       f"[color={appcolor.light_grey_hex}][size=13dp]{data_types.StockHavingData(currency='RUB', count=response['property_count'], current_price=response['current_price'], multiply=True).stockhaving_text}[/color][/size]"
            self.LowerLayout_instance.count_textfield.helper_text = f'Доступно {response["property_count"]}'
            self.LowerLayout_instance.count_textfield.disabled = False

    def error_prebuy(self, *args):
        print('error prebuy ', args)

    def getAsyncData(self, ticker, *args):
        cursor = sqlite3.connect('mydata.db').cursor()
        try:
            id = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
            UrlRequest(url=hardconfig.PRESELL_SERVER_REQUEST.format(id, ticker),
                       on_success=self.success_prebuy, on_error=self.error_prebuy,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())
        except TypeError as e:
            print(e)
            # LOG OUT NAHUY NA REGU HZ SESSIYA MERTVA
            ...

    def success_sell(self, *args):
        try:
            text = json.loads(args[-1])
            if text['response'] == "FALSE":
                error_popup = MDDialog(
                    title=appcolor.red_downprice_html_bb.format("Ошибка"),
                    text="Покупка не удалась, [b]недостаточно средств[/b], попробуйте меньшее количество",
                )
                error_popup.open()
            else:
                successPopup = MDDialog(
                    type="custom",
                    content_cls=self.PopupContent(amount_data=text['amount'],
                                                  logo_path=text['logo_path'],
                                                  sum_data=data_types.PriceData(
                                                      price=text['sum'],
                                                      currency="RUB").price_text,
                                                  ),
                    on_pre_dismiss=lambda x: Clock.schedule_once(lambda x: self.reload(self.ticker))
                )
                successPopup.open()

        except json.decoder.JSONDecodeError:
            UrlRequest(url=hardconfig.BUY_SERVER_REQUEST.format(self._id, self.ticker, self.buy_amount),
                       on_success=self.success_sell, on_error=self.error_sell,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())

    def error_sell(self, *args):
        print('error sell', args)

    def sellStocks(self, *args):
        cursor = sqlite3.connect('mydata.db').cursor()
        try:
            _id = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
        except TypeError as e:
            print("LOGIN ERROR")
        if _id:
            sell_amount = self.LowerLayout_instance.count_textfield.text
            if sell_amount.isdigit():
                sell_amount = round(float(sell_amount))
                if sell_amount > 0 and sell_amount <= self.property_count:
                    self.sell_amount = sell_amount
                    self._id = _id
                    UrlRequest(url=hardconfig.SELL_SERVER_REQUEST.format(_id, self.ticker, sell_amount),
                               on_success=self.success_sell, on_error=self.error_sell,
                               timeout=hardconfig.URL_REQUEST_TIMEOUT,
                               ca_file=certifi.where())

    class Title(MDGridLayout):
        def __init__(self, go_back_func):
            super().__init__()
            self.cols = 2
            self.rows = 1
            self.size_hint_y = .2
            self.title_label = custom_font.SFLabel(text='Продажа', font_size="30dp", font_style="Heavy")
            self.back_button = common_libs.ImageButton(source="./img/back_button.png", size_hint=[.15, .01],
                                                       inner_data="backbutton", on_release_func=go_back_func,
                                                       pos_hint={'center_x': .1})
            self.add_widget(self.back_button)
            self.add_widget(self.title_label)

    class LowerLayout(MDGridLayout):
        def __init__(self, buy_approve_func):
            super().__init__()
            self.cols = 1
            self.size_hint_y = .4
            self.spacing = 30
            self.count_textfield = MDTextField(
                hint_text="Количество",
                helper_text="",
                helper_text_mode="persistent",
                multiline=False,
                disabled=True,
                cursor_color=hardconfig.PRIMARY_ACTIVE_COLOR,
                text_color_normal=hardconfig.PRIMARY_INACTIVE_COLOR,
                hint_text_color_normal=hardconfig.PRIMARY_INACTIVE_COLOR,
                # TODO Ввод только цифр
            )
            # self.calc_available_stock_to_sell = custom_font.SFLabel(text='Итого: 1992.71 ₽', halign='left')
            self.approve_button = MDCard(
                custom_font.SFLabel(text=f'[color=FFFFFF]Продать[/color]',
                                    font_size="20dp", font_style="Light"),
                md_bg_color=get_color_from_hex(appcolor.green_buy_hex),
                radius=hardconfig.PRIMARY_CARD_RADIUS,
                on_release=buy_approve_func,
                ripple_behavior=True,
                disabled=True
            )
            self.add_widget(self.count_textfield)
            # self.add_widget(self.calc_available_stock_to_sell)
            self.add_widget(self.approve_button)

    class PopupContent(MDBoxLayout):
        def __init__(self, amount_data, logo_path, sum_data):
            super().__init__()
            self.size_hint_y = None
            self.height = dp(150)
            self.md_bg_color = (0, 0, 0, 0)
            self.SoldCard_instance = self.SoldCard()

            bought_stock_image = Image(source=logo_path, allow_stretch=True,
                                       size_hint=[.8, .8])
            bought_stock_label = custom_font.SFLabel(
                text=f'[size=20dp][font=./font/SF_Bold]Продано {amount_data} шт.[/font][/size][size=25dp]\n[/size]'
                     f'[size=17dp]на {sum_data}[/size]', halign='center',
                valign='center')

            self.SoldCard_instance.inner_grid.add_widget(bought_stock_image)
            self.SoldCard_instance.inner_grid.add_widget(bought_stock_label)

            self.add_widget(self.SoldCard_instance)

        class SoldCard(MDCard):
            def __init__(self):
                super().__init__()
                self.md_bg_color = (0, 0, 0, 0)
                self.inner_grid = MDGridLayout(cols=1, rows=2, spacing=50, size_hint_y=None, height=dp(150))
                self.padding = [50, 50, 50, 50]
                self.radius = 30
                self.size_hint = [.5, .5]
                self.add_widget(self.inner_grid)

