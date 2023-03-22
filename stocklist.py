import certifi
from kivy.animation import Animation
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import TwoLineAvatarListItem, MDList
from kivy.clock import Clock
from kivymd.uix.scrollview import MDScrollView
from kivy.network.urlrequest import UrlRequest
import hardconfig
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import NoTransition
from font import custom_font
import data_types
from kivymd.uix.list import ImageLeftWidget
import json

from investing import common_libs


class IconCard(MDCard):
    def __init__(self, text: str, screen_change_func):
        super().__init__()
        self.id = f"{text}_IconCard"
        card_label = custom_font.SFLabel(text=f"[ref={text}]{text}[/ref]", valign='center',
                                         halign='center', markup=True, font_style='Medium')
        card_label.bind(on_ref_press=screen_change_func)
        self.size_hint_x = len(text) / 100
        self.minimum_width = 96
        self.ripple_behavior = True
        self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
        self.add_widget(card_label)
        self.ripple_alpha = hardconfig.RIPPLE_ALPHA
        self.bind(
            on_release=lambda sc: screen_change_func(text)
        )


class StockItem(TwoLineAvatarListItem):
    def __init__(self, ticker: str, stock_name: str, logo_path, chooseItemFunc):
        super().__init__()
        self.choose_item_func = chooseItemFunc
        self.logo_path = logo_path
        self.ticker = ticker

        self.img = ImageLeftWidget(
            source=self.logo_path,
            on_release=lambda x: self.choose_item_func(self.ticker))

        self.add_widget(self.img)
        self.text = f"[b][font=./font/SF_Medium]{stock_name}[/b][/font]"
        self.secondary_text = f"[font=./font/SF_Light]{ticker}[/font]"

        self.right_price_label = custom_font.AKLabelLoader(text='', halign='right', size_hint = [.3,.6],
                                                           pos_hint={'center_x': .8, 'center_y': .5})
        self.add_widget(self.right_price_label)
        self.bind(
            on_release=lambda x: self.choose_item_func(self.ticker, "Stocks")
        )


class StockScreen(MDScreen):
    def __init__(self, screen_manager_instance, screen_change_func, choose_item_func):
        super(StockScreen, self).__init__()
        self.name = "Stocks"
        self.on_init_clock = Clock.schedule_once(self.getAsyncData, 0)
        self.update_clock = Clock.schedule_interval(self.idle_update, 10)
        # on INIT clock!
        self.screen_change_func = screen_change_func
        self.choose_item_func = choose_item_func
        self.screen_manager_instance = screen_manager_instance

        self.main_layout = MDGridLayout(cols=1, rows=3, padding=[30, 0, 30, 20], spacing=20)
        self.main_layout.add_widget(
            self.TopMenu(self.screen_change_func)
                                   )
        self.big_placeholder = custom_font.AKLabelLoader(text="", size_hint = [1, 1] ,
                                                         round_ = 10)
        self.navigation_bar_instance = common_libs.NavigationBar(self.screen_manager_instance)

        self.main_layout.add_widget(self.big_placeholder)
        self.add_widget(self.main_layout)

        self.on_enter_clock = None
        self.error_clock = None
        self.stocklist_scrollview = None
        self.is_initialized = 0

    def on_enter(self, *args):
        def resume_anim(clock_dt):
            if self.stocklist_scrollview is not None:
                for row in self.stocklist_scrollview.stock_MDList.children:
                    row.right_price_label._start_animate()
            return False
        Clock.schedule_once(lambda x: self.getAsyncData(init=False), 0)
        Clock.schedule_once(resume_anim, 0)
        ...

    def idle_update(self, clock_dt):
        if self.screen_manager_instance.current == self.name:
            Clock.schedule_once(lambda x: self.getAsyncData(False), 0)

    def update_prices(self, *args):
        data = json.loads(args[-1])
        if len(self.stocklist_scrollview.stock_MDList.children) > 0:
            for ticker in data.keys():
                for i in self.stocklist_scrollview.stock_MDList.children:
                    if i.ticker == ticker:
                        update_anim = Animation(text_color=hardconfig.TEXT_UPDATE_COLOR, duration=.5) +\
                                      Animation(text_color=hardconfig.PRIMARY_TEXT_COLOR, duration=.5)
                        update_anim.start(i.right_price_label)
                        i.right_price_label.text = data_types.PriceData(currency=data[ticker]['currency'],
                                                                price=data[ticker]['current_price'],
                                                                last_change_amount=data[ticker]['last_change_amount'],
                                                                last_change_percent=data\
                                                                [ticker]['last_change_percent']).combined_full
                        i.right_price_label.size_hint=[.4,.6]

        return False


    def on_pre_leave(self, *args):
        def clear_price_data(clock_dt):
            for row in self.stocklist_scrollview.stock_MDList.children:
                row.right_price_label.text = ''
                row.right_price_label.size_hint = [.3, .6]
                Animation.cancel_all(row.right_price_label)
            return False
        Clock.schedule_once(clear_price_data, 0)

    def error(self, *args):
        print('error', args)
        self.error_clock = Clock.schedule_once(self.getAsyncData, 2)

    def success_on_init(self, *args):
        # TODO здесь может быть ошибка, оффни сервер и проверь, похоже на спам виджетами
        self.is_initialized += 1
        if self.error_clock is not None:
            self.error_clock.cancel()
        if self.on_enter_clock is not None:
            self.on_enter_clock.cancel()
        # TODO КОСТЫЛЬ ПИЗДЕЦ НО РАБОТАЕТ
        if self.is_initialized <= 1:
            Animation.cancel_all(self.big_placeholder)
            self.main_layout.remove_widget(self.big_placeholder)
            self.stocklist_scrollview = self.StockList_ScrollView(server_response=args[-1],
                                                                  item_choose_func=self.choose_item_func)
            self.main_layout.add_widget(self.stocklist_scrollview)
            self.main_layout.add_widget(self.navigation_bar_instance)

    def getAsyncData(self, init=True):
        if init:
            UrlRequest(url=hardconfig.LSV_SERVER_REQUEST,
                   on_success=self.success_on_init, on_error=self.error,
                   timeout=hardconfig.URL_REQUEST_TIMEOUT,
                   ca_file=certifi.where())
            return False
        else:
            UrlRequest(url=hardconfig.LSV_SERVER_REQUEST,
                       on_success=self.update_prices, on_error=self.error,
                       timeout=hardconfig.URL_REQUEST_TIMEOUT,
                       ca_file=certifi.where())
            return False

    class TopMenu(MDGridLayout):

        def __init__(self, screen_change_func):
            super().__init__()
            self.cols = 1
            self.rows = 2
            self.size_hint_y = .2
            # self.spacing = 20
            self.title_label = custom_font.SFLabel(text="Акции", font_size="20dp", font_style='Bold')
            self.add_widget(self.title_label)
            self.cards = ['Акции', 'Криптовалюты']  # не используется, тупо для инфы
            self.upper_cards_layout = MDGridLayout(cols=2, rows=1, spacing = 20)
            # карты тут если че добавь больше
            self.upper_cards_layout.add_widget(IconCard(text="Акции",
                                                        screen_change_func=screen_change_func))
            self.upper_cards_layout.add_widget(IconCard(text="Криптовалюта",
                                                        screen_change_func=screen_change_func))
            self.add_widget(self.upper_cards_layout)

    class StockList_ScrollView(MDScrollView):
        def __init__(self, server_response, item_choose_func):
            super().__init__()
            server_response = json.loads(server_response)
            self.item_choose_func = item_choose_func
            self.stock_MDList = MDList()

            for i in server_response.keys():
                SI = StockItem(
                    ticker=i,
                    stock_name=server_response[i]['name'],
                    chooseItemFunc=self.item_choose_func,
                    logo_path=server_response[i]['logo_path']
                )

                SI.right_price_label.text = data_types.PriceData(currency=server_response[i]['currency'],
                                                            price=server_response[i]['current_price'],
                                                            last_change_amount=server_response[i]['last_change_amount'],
                                                            last_change_percent=server_response\
                                                            [i]['last_change_percent']).combined_full
                SI.right_price_label.size_hint = [.4, .6]
                SI.right_price_label.font_size=dp(15)

                self.stock_MDList.add_widget(SI)

            self.add_widget(self.stock_MDList)


    class NavigationBar(MDFloatLayout):
        def __init__(self, screen_manager_instance):
            super().__init__()
            self.size_hint_y = .1
            self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
            self.radius = 20
            self.screen_manager_instance = screen_manager_instance

            self.elevationbar_inner_grid = MDGridLayout(cols=3, pos_hint={"center_x": .5, "center_y": .5},
                                                        padding=20, spacing=50)
            self.elevationbar_inner_grid.add_widget(
                common_libs.ImageButton(source='./img/profile_section_logo.png', size_hint=[.1, .1],
                                 on_release_func=self.item_on_press, allow_stretch=True, inner_data='Account')
            )
            self.elevationbar_inner_grid.add_widget(
                common_libs.ImageButton(source='./img/stock_section_logo.png', size_hint=[.1, .1],
                                 on_release_func=self.item_on_press, allow_stretch=True, inner_data='Stocks')
            )
            self.elevationbar_inner_grid.add_widget(
                common_libs.ImageButton(source='./img/info_section_logo.png', size_hint=[.1, .1],
                                 on_release_func=self.item_on_press, allow_stretch=True, inner_data='Info')
            )

            self.add_widget(self.elevationbar_inner_grid)

        def item_on_press(self, *args):
            if self.screen_manager_instance.current != args[-1]:
                self.screen_manager_instance.transition = NoTransition()
                self.screen_manager_instance.current = args[-1]
                self.screen_manager_instance.transition = hardconfig.DEFAULT_TRANSITION

