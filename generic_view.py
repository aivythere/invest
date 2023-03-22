import json
import certifi
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.utils import get_color_from_hex
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.transition import MDSlideTransition
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.graphics import Color, Rectangle
import hardconfig
from font import custom_font
from investing import data_types, appcolor, common_libs
from common_libs import ImageButton


class GenericScreen(MDScreen):
    def __init__(self, screen_manager, last_screen, buy_screen_reload_func, sell_screen_reload_func):
        super(GenericScreen, self).__init__()
        self.name = 'StockViewing'
        self.ticker = None
        self.touch_start_x = None
        self.touch_start_y = None
        self.yandex_predicted_price = None
        self.sber_predicted_price = None
        self.gpt_predicted_price = None
        self.AI_Info_Popup_instance = None

        self.scroll_view = MDScrollView(do_scroll_x=True, do_scroll_y=True)
        self.main_gl = MDGridLayout(cols=1, size_hint_y=None, size_hint_x=None, spacing=0,
                                    height=hardconfig.WINDOW_SIZE[1] * 2.5,
                                    width=hardconfig.WINDOW_SIZE[0] * 1.99)

        self.screen_manager_instance = screen_manager
        self.last_screen = last_screen
        self.buy_screen_reload_func = buy_screen_reload_func
        self.sell_screen_reload_func = sell_screen_reload_func
        self.sell_screen_reload_func = sell_screen_reload_func

        self.TopTitleBar_instance = self.TopTitleBar(goBackScreen=self.goBackScreen)
        self.MiddlePriceSection_instance = self.MiddlePriceSection(buy_sell_handler=self.buy_sell_handler)
        self.LowerHintSection_instance = self.LowerHintSection()
        self.UnderMiddleSection_instance = self.UnderMiddleAIPredictSection()

        self.main_gl.add_widget(self.TopTitleBar_instance)
        self.main_gl.add_widget(self.MiddlePriceSection_instance)
        self.main_gl.add_widget(self.UnderMiddleSection_instance)
        self.main_gl.add_widget(self.LowerHintSection_instance)

        self.scroll_view.add_widget(self.main_gl)
        self.add_widget(self.scroll_view)

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        super(GenericScreen, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        try:
            if (touch.x - self.touch_start_x) > 200 and (touch.y - self.touch_start_y) < 250:
                self.goBackScreen()
            super(GenericScreen, self).on_touch_up(touch)
        except TypeError:
            pass

    def on_leave(self, *args):
        self.TopTitleBar_instance.stock_name_title.text = ''
        self.MiddlePriceSection_instance.middle_price_label.text = ''
        self.LowerHintSection_instance.lowercard_instance.lowerhintcard_price_label.text = ''
        self.LowerHintSection_instance.lowercard_instance.price_verdict_label.text = ''
        self.MiddlePriceSection_instance.middle_price_label.pos_hint = {'center_y': .5, 'center_x': .5}
        with self.TopTitleBar_instance.canvas.before:
            Color(*hardconfig.PRIMARY_CARD_COLOR)
            self.rect = Rectangle(size=self.TopTitleBar_instance.size, pos=self.TopTitleBar_instance.pos)
        self.UnderMiddleSection_instance.ChatGPT_Card.disabled = True
        self.UnderMiddleSection_instance.SberAI_Card.disabled = True
        self.UnderMiddleSection_instance.YandexAI_Card.disabled = True

        self.UnderMiddleSection_instance.ChatGPT_Card.AI_predicted_change.text = ''
        self.UnderMiddleSection_instance.SberAI_Card.AI_predicted_change.text = ''  # t
        self.UnderMiddleSection_instance.YandexAI_Card.AI_predicted_change.text = ''
        self.MiddlePriceSection_instance.buy_sell_buttons.buy_button.disabled = True
        self.MiddlePriceSection_instance.buy_sell_buttons.sell_button.disabled = True
        ...  # ! ON ENTER НЕ НУЖЕН !

    def reload(self, ticker, last_screen=None):
        Clock.schedule_once(lambda x: self.asyncDataLoad(ticker=ticker))
        self.ticker = ticker
        if last_screen is not None: self.last_screen = last_screen

    def error(self, *args):
        print('error', args
              )

    def asyncDataLoad(self, ticker, *args):
        UrlRequest(url=hardconfig.TICKER_SERVER_REQUEST.format(ticker),
                   on_success=self.success, on_error=self.error,
                   timeout=hardconfig.URL_REQUEST_TIMEOUT,
                   ca_file=certifi.where())

    def success(self, *args):
        data = json.loads(args[-1])
        currency = data['currency']
        current_price = data['current_price']
        last_price = data['last_price']
        last_change_amount = data['last_change_amount']
        last_change_percent = data['last_change_percent']
        market_state = data['market_state']
        primary_color_hex = data['primary_color_rgba']
        name = data['name']

        self.yandex_predicted_price = data['yandex_predicted_price']
        self.sber_predicted_price = data['sber_predicted_price']
        self.gpt_predicted_price = data['gpt_predicted_price']

        with self.TopTitleBar_instance.canvas.before:
            Color(*tuple(get_color_from_hex(str(primary_color_hex))))
            self.rect = Rectangle(size=self.TopTitleBar_instance.size,
                                  pos=self.TopTitleBar_instance.pos)

        self.TopTitleBar_instance.stock_name_title.text = f'[size=25dp]{name}[/size]\n' \
                                                          f'[size=15dp]{self.ticker}[/size]'

        self.MiddlePriceSection_instance.middle_price_label.text = f"" \
                                                                   f"[size=25dp]{data_types.PriceData(currency=currency, price=current_price).price_text}[/size]" \
                                                                   f"\n[size=15dp]{data_types.PriceData(currency=currency, last_change_amount=last_change_amount, last_change_percent=last_change_percent).last_change_text}[/size]"
        self.MiddlePriceSection_instance.middle_price_label.font_size = dp(20)
        self.MiddlePriceSection_instance.middle_price_label.pos_hint = {'center_y': .8, 'center_x': .5}
        self.MiddlePriceSection_instance.buy_sell_buttons.buy_button.disabled = False
        self.MiddlePriceSection_instance.buy_sell_buttons.sell_button.disabled = False

        self.LowerHintSection_instance.lowercard_instance.lowerhintcard_price_label.text = data_types.PriceData(
            currency=currency, price=current_price, last_change_amount=last_change_amount,
            last_change_percent=last_change_percent
        ).combined_full
        self.LowerHintSection_instance.lowercard_instance.price_verdict_label.text = \
            appcolor.green_upprice_html_bb.format("Покупать")

        self.UnderMiddleSection_instance.ChatGPT_Card.disabled = False
        self.UnderMiddleSection_instance.SberAI_Card.disabled = False
        self.UnderMiddleSection_instance.YandexAI_Card.disabled = False

        self.UnderMiddleSection_instance.ChatGPT_Card.AI_predicted_change.text = data_types.PriceData(
            ai_change=self.gpt_predicted_price, currency=currency).ai_change_text
        self.UnderMiddleSection_instance.SberAI_Card.AI_predicted_change.text = data_types.PriceData(
            ai_change=self.sber_predicted_price, currency=currency).ai_change_text
        self.UnderMiddleSection_instance.YandexAI_Card.AI_predicted_change.text = data_types.PriceData(
            ai_change=self.yandex_predicted_price, currency=currency).ai_change_text

    def buy_sell_handler(self, *args):
        if args[-1] == "buy":
            self.buy_screen_reload_func(self.ticker)
            self.screen_manager_instance.current = "BuyScreen"
        else:
            self.sell_screen_reload_func(self.ticker)
            self.screen_manager_instance.current = "SellScreen"


    def goBackScreen(self, *args):
        if self.screen_manager_instance.current == self.name:
            self.screen_manager_instance.transition = MDSlideTransition(direction='right',
                                                                        duration=hardconfig.ANY_TRANSITION_DURATION)
            self.screen_manager_instance.current = self.last_screen
            self.screen_manager_instance.transition = hardconfig.DEFAULT_TRANSITION

    class TopTitleBar(MDFloatLayout):
        def __init__(self, goBackScreen):
            super().__init__()
            self.size_hint_y = None
            self.height = dp(hardconfig.WINDOW_SIZE[1] / 4)

            self.back_button = ImageButton(source='./img/back_button.png', pos_hint={'center_x': .1, 'top': .6},
                                           size_hint=[.2, .2], on_release_func=goBackScreen, inner_data='back')
            self.stock_name_title = custom_font.AKLabelLoader(text='', size_hint=[1, 1],
                                                              pos_hint={'center_x': .5, 'center_y': .5},
                                                              halign='center', valign='center',
                                                              color=appcolor.white_rgba)
            self.add_widget(self.back_button)
            self.add_widget(self.stock_name_title)

    class MiddlePriceSection(MDGridLayout):
        def __init__(self, buy_sell_handler):
            super().__init__()
            self.cols = 1
            # self.rows = 2
            self.spacing = 20
            self.padding = 30  # указываю отдельно чтгбы верх норм отображался
            self.size_hint_y = None
            self.height = dp(hardconfig.WINDOW_SIZE[1] / 3)

            self.middle_label = custom_font.SFLabel(text='Текущая цена', halign='left', size_hint=[.8, .8],
                                                    font_style='Heavy', font_size="25dp")
            self.middle_price_label = custom_font.AKLabelLoader(text='', halign='left', valign='top', bold=True,
                                                                pos_hint={'center_y': .5, 'center_x': .5})
            self.buy_sell_buttons = common_libs.BuySellButotns(on_release_func=buy_sell_handler)
            self.add_widget(self.middle_label)
            self.add_widget(self.middle_price_label)
            self.add_widget(self.buy_sell_buttons)

    class UnderMiddleAIPredictSection(MDGridLayout):
        def __init__(self):
            super().__init__()
            self.cols = 1
            self.padding = 30
            self.spacing = 20
            self.size_hint_y = None
            self.height = dp(300)

            self.undermiddle_title = custom_font.SFLabel(text='Прогнозы цен от ИИ', font_style="Heavy",
                                                         font_size="25dp", halign='left')
            self.add_widget(self.undermiddle_title)
            self.ai_popup_instance = self.AI_Info_Popup()

            self.ChatGPT_Card = self.AI_Element(ai_logo_path='./img/chatgpt_logo.png',
                                                ai_accuracy=97.82, ai_name="ChatGPTv4 (OpenAI)",
                                                ai_hidden_code='chatgpt', ai_choose_func=self.ai_choose_func,
                                                ai_popup_instance=self.ai_popup_instance)
            self.SberAI_Card = self.AI_Element(ai_logo_path='./img/sber_ai_logo.png',
                                               ai_accuracy=79.21, ai_name="SberBank AI (Сбер)",
                                               ai_hidden_code='sberai', ai_choose_func=self.ai_choose_func,
                                               ai_popup_instance=self.ai_popup_instance)
            self.YandexAI_Card = self.AI_Element(ai_logo_path='./img/yandexai_logo.png',
                                                 ai_accuracy=87.10, ai_name="Yandex AI (Яндекс)",
                                                 ai_hidden_code='yandexai', ai_choose_func=self.ai_choose_func,
                                                 ai_popup_instance=self.ai_popup_instance)
            self.add_widget(self.ChatGPT_Card)
            self.add_widget(self.SberAI_Card)
            self.add_widget(self.YandexAI_Card)

        def ai_choose_func(self, *args):
            print(args)
            # if args == yandex / sber / gpt open(self.ya_popup), (sber.popup) etc < - методы родительского класса

        class AI_Element(MDCard):
            def __init__(self, ai_logo_path, ai_accuracy, ai_name,
                         ai_hidden_code, ai_choose_func, ai_popup_instance):
                super().__init__()
                self.ai_hd_code = ai_hidden_code
                self.ai_choose_func = ai_choose_func
                self.ai_popup_instance = ai_popup_instance
                self.radius = hardconfig.PRIMARY_CARD_RADIUS

                self.size_hint_y = None
                self.height = 140

                self.disabled = True
                self.inner_ai_card_grid = MDGridLayout(cols=3, rows=1, padding=30, spacing=40)
                self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR

                self.AI_pfp = ImageButton(source=ai_logo_path, size_hint=[.2, .2],
                                          on_release_func=ai_choose_func, inner_data=self.ai_hd_code)
                self.AI_info_label = custom_font.SFLabel(text=f"[size=13dp]{ai_name}[/size]\n"
                                                              f"[size=11dp]Точность: {ai_accuracy}%[/size]",
                                                         halign='left', valign='top')
                self.AI_predicted_change = custom_font.AKLabelLoader(text='', halign='right', valign='center')
                self.inner_ai_card_grid.add_widget(self.AI_pfp)
                self.inner_ai_card_grid.add_widget(self.AI_info_label)
                self.inner_ai_card_grid.add_widget(self.AI_predicted_change)
                self.add_widget(self.inner_ai_card_grid)

            def on_release(self, *args):
                self.ai_choose_func(self.ai_hd_code)
                self.ai_popup_instance.open(self.ai_hd_code)

        class AI_Info_Popup(MDDialog):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.padding = 30
                self.size_hint_y = .5
                self.ai_popup_label = custom_font.AKLabelLoader(text='')
                self.ai_popup_label._stop_animate()
                self.add_widget(self.ai_popup_label)

            def on_dismiss(self):
                Animation.cancel_all(self.ai_popup_label)

            def on_pre_open(self):
                self.ai_popup_label._start_animate()

    class LowerHintSection(MDGridLayout):
        def __init__(self):
            super().__init__()
            self.cols = 1
            self.rows = 2
            self.size_hint_y = None
            self.pos_hint = {"bottom": 1, "center_y:": 1}
            self.height = dp(hardconfig.WINDOW_SIZE[1] / 4)
            self.padding = 30  # указываю отедльно чтгбы верх норм отображался
            self.spacing = 20
            self.lowerhint_title = custom_font.SFLabel(text='Прогноз цены', halign='left', font_style='Heavy',
                                                       font_size="25dp")
            self.add_widget(self.lowerhint_title)
            self.lowercard_instance = self.LowerHindCard()
            self.add_widget(self.lowercard_instance)

        class LowerHindCard(MDCard):
            def __init__(self):
                super().__init__()
                # self.radius = 20
                self.radius = hardconfig.PRIMARY_CARD_RADIUS
                self.text_grid = MDGridLayout(cols=2, rows=1, padding=50)
                self.size_hint_y = None
                self.height = dp(100)
                self.md_bg_color = hardconfig.PRIMARY_CARD_COLOR
                self.lowerhintcard_price_label = custom_font.AKLabelLoader(
                    text='', halign='left', valign='center'
                )
                self.price_verdict_label = custom_font.AKLabelLoader(text='', halign='right', bold=True)
                self.text_grid.add_widget(self.lowerhintcard_price_label)
                self.text_grid.add_widget(self.price_verdict_label)
                self.add_widget(self.text_grid)
