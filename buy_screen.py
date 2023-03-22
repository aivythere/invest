import json
import math
import certifi
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen
import sqlite3
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.transition import MDSlideTransition
from investing import hardconfig, appcolor, common_libs, data_types
from investing.font import custom_font


class BuySellScreen(MDScreen):
    def __init__(self, screen_manager_instance, upper_screen_reload_func):
        super().__init__()
        self.name = "BuyScreen"
        self.blur = 10

        self.screen_manager_instance = screen_manager_instance
        self.upper_screen_reload_func = upper_screen_reload_func
        self.main_scrollview = MDScrollView(do_scroll_x=True, do_scroll_y=False)
        self.bscreen_inner_grid = MDGridLayout(cols=1, spacing=50, padding=30,
                                               size_hint_x=None, width=hardconfig.WINDOW_SIZE[0] * 1.99)

        self.section_title = custom_font.SFLabel(text='Покупка', font_style="Heavy", font_size="30dp",
                                                 valign='top', halign='left')
        self.upper_grid = MDGridLayout(cols=2, rows=1, size_hint_y=.15, spacing=30)

        self.ticker = None
        self.money_available = None
        self.chosen_stock_price = None

        self.AvailableBalanceCard_instance = self.AvailableBalanceCard()
        self.LowerLayout_instance = self.LowerLayout(buy_approve_func=self.buyStocks, calc_func=self.calc_prebuy_sum)
        self.StockCardItem_instance = common_libs.StockCardItem(
            image_path="./img/blank.png", item_name="", item_ticker=self.ticker, size_hint_y=.35
        )

        self.upper_grid.add_widget(common_libs.ImageButton(
            source="./img/back_button.png", size_hint=[.2, 1], inner_data=None,
            on_release_func=self.goBackScreen, pos_hint={'center_x': .01}))
        self.upper_grid.add_widget(self.section_title)

        self.bscreen_inner_grid.add_widget(self.upper_grid)
        self.bscreen_inner_grid.add_widget(self.AvailableBalanceCard_instance)
        self.bscreen_inner_grid.add_widget(self.StockCardItem_instance)
        self.bscreen_inner_grid.add_widget(self.LowerLayout_instance)
        self.bscreen_inner_grid.add_widget(MDGridLayout(size_hint_y=.3))

        self.main_scrollview.add_widget(self.bscreen_inner_grid)
        self.add_widget(self.main_scrollview)

    def on_leave(self, *args):
        self.LowerLayout_instance.count_textfield.helper_text = f""
        self.LowerLayout_instance.count_textfield.disabled = True
        self.LowerLayout_instance.approve_button.disabled = True
        self.AvailableBalanceCard_instance.aval_bal_label.text = ''
        self.StockCardItem_instance.stock_pfp.source = './img/blank.png'
        self.StockCardItem_instance.item_name_label.text = ''
        self.StockCardItem_instance.price_data_label.text = ''

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        super(BuySellScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        try:
            if (touch.x - self.touch_start_x) > 200 and (touch.y - self.touch_start_y) < 250:
                self.goBackScreen()
            super(BuySellScreen, self).on_touch_up(touch)
        except TypeError:
            pass

    def calc_prebuy_sum(self, textfield_instance):
        if textfield_instance.text.isdigit():
            _am = int(textfield_instance.text)
            if _am > 0:
                cl_price = self.chosen_stock_price * _am
                cl_price = data_types.PriceData(currency="RUB", price=cl_price).price_text
                self.LowerLayout_instance.prebuy_calc_label.text = f"Итог: {cl_price}"

    def goBackScreen(self, *args):
        if self.screen_manager_instance.current == self.name:
            self.screen_manager_instance.transition = MDSlideTransition(direction='right',
                                                                        duration=hardconfig.ANY_TRANSITION_DURATION)
            self.upper_screen_reload_func(self.ticker)
            self.screen_manager_instance.current = "StockViewing"
            self.screen_manager_instance.transition = hardconfig.DEFAULT_TRANSITION

    def buyStocks(self, *args):
        cursor = sqlite3.connect('mydata.db').cursor()
        try:
            _id = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
        except TypeError as e:
            print("LOGIN ERROR")
        if _id:
            buy_amount = self.LowerLayout_instance.count_textfield.text
            if buy_amount.isdigit():
                buy_amount = round(float(buy_amount))
                if buy_amount > 0:
                    self.buy_amount = buy_amount
                    self._id = _id
                    UrlRequest(url=hardconfig.BUY_SERVER_REQUEST.format(_id, self.ticker, buy_amount),
                               on_success=self.success_buy, on_error=self.error_buy,
                               timeout=hardconfig.URL_REQUEST_TIMEOUT,
                               ca_file=certifi.where())

    def success_buy(self, *args):
        try:
            text = json.loads(args[-1])
            if text['response'] == "FALSE":
                error_popup = MDDialog(
                    title=appcolor.red_downprice_html_bb.format("Ошибка"),
                    text="Покупка не удалась, [b]недостаточно средств[/b], попробуйте меньшее количество",
                    # md_bg_color = appcolor.dark_red_fail
                )
                error_popup.open()
            else:
                # success_popup = MDDialog(
                #     title=appcolor.green_upprice_html_bb.format("Успешно"),
                #     text="Вы успешно купили акции!\n\nСписок акций, которыми вы владеете доступен [b]в личном кабинете[/b]",
                # md_bg_color =appcolor.dark_green_success
                successPopup = MDDialog(
                    type="custom",
                    content_cls=self.PopupContent(amount_data=text['amount'],
                                                  logo_path=text['logo_path'],
                                                  sum_data=data_types.PriceData(
                                                      price=text['spend_amount'],
                                                      currency="RUB").price_text,
                                                  ),
                    on_pre_dismiss=lambda x: Clock.schedule_once(lambda x: self.reload(self.ticker))
                )
                successPopup.open()
                self.LowerLayout_instance.count_textfield.text = ''
        except json.decoder.JSONDecodeError:
            UrlRequest(url=hardconfig.BUY_SERVER_REQUEST.format(self._id, self.ticker, self.buy_amount),
                       on_success=self.success_buy, on_error=self.error_buy,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())


    def error_buy(self, *args):
        print('BUY ERROR', args)

    def reload(self, ticker):
        Clock.schedule_once(lambda x: self.getAsyncData(ticker), 0)
        self.ticker = ticker

    def success(self, *args):
        text = json.loads(args[-1])
        money_available = text['money_aval']
        self.chosen_stock_price = text['current_price']
        self.LowerLayout_instance.count_textfield.helper_text = f"Доступно {math.floor(money_available / self.chosen_stock_price)}"
        self.LowerLayout_instance.count_textfield.disabled = False
        self.LowerLayout_instance.approve_button.disabled = False
        update_anim = Animation(text_color=hardconfig.TEXT_UPDATE_COLOR, duration=.5) + \
                      Animation(text_color=hardconfig.PRIMARY_TEXT_COLOR, duration=.5)
        self.AvailableBalanceCard_instance.aval_bal_label.text = f'{data_types.PriceData(price=money_available, currency="RUB").price_text}' \
                                                                 f'[size=13dp]\nДоступнo[/size]'
        update_anim.start(self.AvailableBalanceCard_instance.aval_bal_label)
        self.StockCardItem_instance.stock_pfp.source = text['logo_path']
        self.StockCardItem_instance.item_name_label.text = text['name']
        self.StockCardItem_instance.price_data_label.text = data_types.PriceData(price=text['current_price'],
                                                                                 currency="RUB").price_text

    def error(self, *args):
        print('error', args)

    def getAsyncData(self, ticker, *args):
        cursor = sqlite3.connect('mydata.db').cursor()
        try:
            id = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
            UrlRequest(url=hardconfig.PREBUY_SERVER_REQUEST.format(id, ticker),
                       on_success=self.success, on_error=self.error,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())
        except TypeError as e:
            print(e)
            # LOG OUT NAHUY NA REGU HZ SESSIYA MERTVA
            ...

    class AvailableBalanceCard(MDCard):
        def __init__(self):
            super().__init__()
            self.size_hint_y = .5
            self.padding = 30
            self.radius = hardconfig.PRIMARY_CARD_RADIUS
            self.aval_bal_label = custom_font.AKLabelLoader(text='', halign='left', valign='top', bold=True)
            self.aval_bal_label.font_size = dp(25)
            self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
            self.add_widget(self.aval_bal_label)

    class LowerLayout(MDGridLayout):
        def __init__(self, buy_approve_func, calc_func):
            super().__init__()
            self.cols = 1
            self.spacing = 100
            self.padding = [0, 30, 0, 0]
            self.prebuy_calc_label = custom_font.SFLabel(text='Нажмите "Enter"', size_hint=[.1, .5])
            self.inner_data = "buy"
            self.count_textfield = MDTextField(
                hint_text="Количество",
                helper_text="",
                helper_text_mode="persistent",
                multiline=False,
                disabled=True,
                cursor_color=hardconfig.PRIMARY_ACTIVE_COLOR,
                text_color_normal=hardconfig.PRIMARY_INACTIVE_COLOR,
                hint_text_color_normal=hardconfig.PRIMARY_INACTIVE_COLOR,
                on_text_validate=calc_func
                # TODO Ввод только цифр
            )
            self.approve_button = MDCard(
                custom_font.SFLabel(text=f'[color=FFFFFF]{"Купить" if self.inner_data == "buy" else "Продать"}[/color]',
                                    font_size="20dp", font_style="Light"),
                md_bg_color=get_color_from_hex(appcolor.green_buy_hex),
                radius=hardconfig.PRIMARY_CARD_RADIUS,
                on_release=buy_approve_func,
                ripple_behavior=True,
                disabled=True
            )

            self.approve_button.size_hint_y = None

            self.add_widget(self.count_textfield)
            self.add_widget(self.prebuy_calc_label)
            self.add_widget(self.approve_button)

    class PopupContent(MDBoxLayout):
        def __init__(self, amount_data, logo_path, sum_data):
            super().__init__()
            self.size_hint_y = None
            self.height = dp(150)
            self.md_bg_color = (0, 0, 0, 0)
            self.BoughtCard_instance = self.BoughtCard()

            bought_stock_image = Image(source=logo_path, allow_stretch=True,
                                       size_hint=[.8, .8])
            bought_stock_label = custom_font.SFLabel(
                text=f'[size=20dp][font=./font/SF_Bold]Куплено {amount_data} шт.[/font][/size][size=25dp]\n[/size]'
                     f'[size=17dp]на {sum_data}[/size]', halign='center',
                valign='center')

            self.BoughtCard_instance.inner_grid.add_widget(bought_stock_image)
            self.BoughtCard_instance.inner_grid.add_widget(bought_stock_label)

            self.add_widget(self.BoughtCard_instance)

        class BoughtCard(MDCard):
            def __init__(self):
                super().__init__()
                self.md_bg_color = (0, 0, 0, 0)
                self.inner_grid = MDGridLayout(cols=1, rows=2, spacing=50, size_hint_y=None, height=dp(150))
                self.padding = [50, 50, 50, 50]
                self.radius = 30
                self.size_hint = [.5, .5]
                self.add_widget(self.inner_grid)
