import json
import certifi
from kivy.animation import Animation
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from investing import hardconfig, common_libs, data_types
from investing.font import custom_font
import sqlite3


class AccountScreen(MDScreen):
    def __init__(self, screen_manager_instance, generic_screen_reload_func):
        #
        #    TODO
        #    Создаешь файлы это изи и пишешь туда данные типо айди после авторизации,
        #    сторится все ахуенно приватно в скрытых папках куда нельзя зайти без рута
        #
        super().__init__()
        self.name = "Account"
        self.screen_manager_instance = screen_manager_instance
        self.generic_screen_reload_func = generic_screen_reload_func

        self.main_gl = MDGridLayout(cols=1, spacing=30, padding=30)
        self.balance_card_instance = self.BalanceCard()
        self.middle_propertylist_instance = self.MiddleMyStockList()
        self.main_gl.add_widget(self.balance_card_instance)
        self.main_gl.add_widget(self.middle_propertylist_instance)
        # self.main_gl.add_widget(MDCard())
        self.slist = []
        self.main_gl.add_widget(common_libs.NavigationBar(screen_manager_instance))

        self.add_widget(self.main_gl)

    def on_enter(self, *args):
        Clock.schedule_once(self.getAsyncData, 0)
        Clock.schedule_interval(self.update, 5)
        # self.balance_card_instance.balance_label._start_animate()
        # self.middle_propertylist_instance.scrollable_placeholder._start_animate()

    def update(self, *args):
        # TODO ПЕРЕРАБОТАТЬ, получать только баланс, вместо всего портфеля
        if self.screen_manager_instance.current == self.name:
            cursor = sqlite3.connect('mydata.db').cursor()
            try:
                row = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
                UrlRequest(url=hardconfig.PORTFOLIO_SERVER_REQUEST.format(row),
                           on_success=self.success_update, on_error=self.error,
                           timeout=hardconfig.URL_REQUEST_TIMEOUT,
                           ca_file=certifi.where())

            except TypeError as e:
                print(e)
                # LOG OUT NAHUY NA REGU HZ SESSIYA MERTVA
                ...

    def success_update(self, *args):
        text = json.loads(args[-1])
        total_balance = text["balance_data"]["total"]
        update_anim = Animation(text_color=hardconfig.TEXT_UPDATE_COLOR, duration=.5) + \
                      Animation(text_color=hardconfig.PRIMARY_TEXT_COLOR, duration=.5)
        self.balance_card_instance.balance_label.text = f'[size=15dp]Сумма активов[/size]' \
                                                        f'\n{data_types.PriceData(price=total_balance, currency="RUB").price_text}'
        update_anim.start(self.balance_card_instance.balance_label)

    def error_update(self, *args):
        print('error update (account_screen) 60 - ', args)

    def on_leave(self, *args):
        Clock.schedule_once(self.clear_on_leave, 0)

    def clear_on_leave(self, clock_dt):
        for i in self.slist:
            self.middle_propertylist_instance.scrollable_layout.remove_widget(i)
        self.slist.clear()

    def error(self, *args):
        print('error', args)

    def ticker_choose(self, ticker):
        print(ticker)
        self.generic_screen_reload_func(ticker=ticker, last_screen="Account")
        self.screen_manager_instance.current = "StockViewing"

    def success(self, *args):
        text = json.loads(args[-1])
        self.middle_propertylist_instance.scrollable_layout.remove_widget\
            (self.middle_propertylist_instance.scrollable_placeholder)
        self.middle_propertylist_instance.scrollable_layout.height = hardconfig.PROPERTY_CARD_HEIGHT_DP*(len(text)+1)
        self.balance_card_instance.balance_label.font_size = dp(35)
        total_balance = text["balance_data"]["total"]
        money_available = text["balance_data"]["money_avl"]
        self.balance_card_instance.balance_label.text = f'[size=15dp]Сумма активов[/size]' \
                                                        f'\n{data_types.PriceData(price=total_balance, currency="RUB").price_text}'
        if len(self.middle_propertylist_instance.scrollable_layout.children) == 0:
            for i in text.keys():
                if i != "balance_data":
                    print(i)
                    property_item = common_libs.CardStockPropertyItem(
                        image_path=text[i]['logo_path'],
                        item_name=text[i]['name'],
                        item_ticker=i,
                        price_data=data_types.PriceData(currency=text[i]['currency'],
                                                        price=text[i]['total_stock_price']).price_text,
                        on_release_func=self.ticker_choose,
                        stockhaving_data=data_types.StockHavingData(
                            currency=text[i]['currency'], current_price=text[i]['current_price'],
                            count=text[i]['stock_count']).stockhaving_text
                    )

                    self.middle_propertylist_instance.scrollable_layout.add_widget(property_item)
                    self.slist.append(property_item)
            self.middle_propertylist_instance.scrollable_layout.add_widget(
                mpi := common_libs.MoneyPropertyItem(
                    image_path='./img/money_logo.png',
                    item_name="Рубли",
                    item_ticker="RUB",
                    having_data=data_types.PriceData(currency="RUB", price=money_available).price_text
                )
            )
            self.slist.append(mpi)

    def getAsyncData(self, clock_dt):
        cursor = sqlite3.connect('mydata.db').cursor()
        try:
            row = cursor.execute("SELECT UID FROM DATA;").fetchone()[0]
            UrlRequest(url=hardconfig.PORTFOLIO_SERVER_REQUEST.format(row),
                       on_success=self.success, on_error=self.error,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())

        except TypeError as e:
            print(e)
            # LOG OUT NAHUY NA REGU HZ SESSIYA MERTVA
            ...

    class BalanceCard(MDCard):
        def __init__(self):
            super().__init__()
            # self.size_hint_y = .5
            self.spacing = 30
            self.padding = 30
            self.size_hint_y = .5
            self.radius = hardconfig.PRIMARY_CARD_RADIUS
            self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
            self.balance_card_inner_grid = MDGridLayout(cols=1, rows=2, spacing = 30)

            self.balance_label = custom_font.AKLabelLoader(text='', halign='left', valign='top', bold=True)
            self.balance_card_inner_grid.add_widget(self.balance_label)
            self.balance_card_inner_grid.add_widget(self.BalanceCardButtons())

            self.add_widget(self.balance_card_inner_grid)


        class BalanceCardButtons(MDGridLayout):
            def __init__(self):
                super().__init__()
                self.cols = 2
                self.rows = 1
                self.spacing = 30
                self.size_hint_y = .5
                self.add_widget(
                    MDCard(
                        custom_font.SFLabel(text="Пополнить"),
                        md_bg_color = hardconfig.PRIMARY_INACTIVE_COLOR,
                        radius = hardconfig.PRIMARY_CARD_RADIUS,
                        ripple_behavior = True,
                        ripple_alpha = hardconfig.RIPPLE_ALPHA
                          )
                                )
                self.add_widget(
                    MDCard(
                        custom_font.SFLabel(text="Вывести"),
                        md_bg_color=hardconfig.PRIMARY_INACTIVE_COLOR,
                        radius=hardconfig.PRIMARY_CARD_RADIUS,
                        ripple_behavior=True,
                        ripple_alpha=hardconfig.RIPPLE_ALPHA
                    )
                )

    class MiddleMyStockList(MDCard):
        def __init__(self):
            super().__init__()
            self.radius = hardconfig.PRIMARY_CARD_RADIUS
            self.padding = [0, 10, 0, 10]
            middle_property_scrollview = MDScrollView(radius=hardconfig.PRIMARY_CARD_RADIUS)

            self.scrollable_layout = MDGridLayout(cols=1, size_hint_y=None, spacing=20,
                                                  height=dp(210),
                                                  radius=hardconfig.PRIMARY_CARD_RADIUS)
            self.scrollable_placeholder = custom_font.AKLabelLoader(text='')
            self.scrollable_layout.add_widget(self.scrollable_placeholder)

            middle_property_scrollview.add_widget(self.scrollable_layout)
            self.add_widget(middle_property_scrollview)