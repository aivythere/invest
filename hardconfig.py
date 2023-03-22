from kivy.metrics import dp
from kivymd.uix.transition import MDSlideTransition
import appcolor as ac

# TODO Оптимизация. Удалять виджеты из памяти, все клок-запросы надо чекать на актуальность, например:
#      В экране клок-функцией обновляется цена, тип с него выходит -> она отменяется
#      Также главный экран. Надо глянуть ошибки на запросах, пофиксить рандомно-появляющиеся карты загораживающие
#      цену и оптимизировать запросы, а то он подлагивает.
#
#      # (list) Source files to include (let empty to include all the files)
# s       ource.include_exts = py,png,jpg,kv,atlas,gif,json
#       Это для бульдозера если исопльщуешь lazyload
APP_THEME = "Dark"
APP_PRIMARY_COLOR = "Blue"
APP_MATERIAL_STYLE = "M2"
WINDOW_SIZE = (360, 650)
ANY_TRANSITION_DURATION = 0.4
DEFAULT_TRANSITION = MDSlideTransition(direction='left', duration=ANY_TRANSITION_DURATION)
PRIMARY_TEXT_COLOR = ac.white_rgba if APP_THEME == "Dark" else ac.black_rgba
TEXT_UPDATE_COLOR = ac.white_update if APP_THEME == "Dark" else ac.black_update
PRIMARY_CARD_COLOR = ac.card_color_dark_theme if APP_THEME == "Dark" else ac.card_color_light_theme
PRIMARY_CARD_RADIUS = 20
RIPPLE_ALPHA = .2
ANIMATION_SPEED_FADE_OUT = .01
ANIMATION_RUNNING_SPEED = 0.4
LOADING_ANIMATION_OPACITY = .5 if APP_THEME == "Dark" else 0
PROPERTY_CARD_HEIGHT_DP = dp(60)
PRIMARY_ACTIVE_COLOR = ac.card_color_dark_theme if APP_THEME == "Dark" else ac.card_color_light_theme
PRIMARY_INACTIVE_COLOR = ac.active_interval_button_bg_color_dark if APP_THEME == "Dark" else ac.active_interval_button_bg_color_light
upper_cards = ['Избранное', 'Акции', 'Криптовалюта']


DEFAULT_GRAPH_PERIOD = "graph_day"
SERVER_TIMEZONE = 'Europe/Moscow'

TINKOFF_TOKEN = "t.tA9KsrbSKkV4MNLid1Upq_CcfBTBQhC0mhUsgU1bY9U3H0gimvYpbd7HCWDkjYGW5dKi-xVAzsKmWieGn2X_rA"
SECURE_SERVER_REQUEST_HASH = "tXfb5LBXO"

URL_REQUEST_TIMEOUT = 20
TICKER_SERVER_REQUEST = 'http://localhost:8000/tc_lookup::{}'
LSV_SERVER_REQUEST = 'http://localhost:8000/LSV_lookup::'
COMMON_SERVER_REQUEST = 'http://localhost:8000/cm_lookup::'
PORTFOLIO_SERVER_REQUEST = 'http://localhost:8000/pf_lookup::{}'
PREBUY_SERVER_REQUEST = 'http://localhost:8000/pb_lookup::{}_{}'
PRESELL_SERVER_REQUEST = 'http://localhost:8000/ps_lookup::{}_{}'
BUY_SERVER_REQUEST = 'http://localhost:8000/BUY::{}_{}_{}' # id _ ticker _ count
SELL_SERVER_REQUEST = 'http://localhost:8000/SELL::{}_{}_{}' # id _ ticker _ count


# SQL TODO Перейти на совместимую БД, постгрес НЕ ПОЙДЕТ, зайдет например Firebase
STOCK_INFO_TABLE_NAME = "stocks"
USERS_INFO_TABLE_NAME = "users"
PROPERTY_INFO_TABLE_NAME = "property"
TEMP_DBFILE = "stocks.db"
LAST_PRICE_UPDATE_HOUR = 19

# [padding_left, padding_top, padding_right, padding_bottom]
# TODO Прила обращается ТОЛЬКО к бд, никаких вызовов к тинькофф апи, все лимиты по пизде пойдут.
#      А вот к БД - охуенно, мы спокойно во все лимиты уложимся и сможем каждые 5 секунд обновлять данные
#      Только надо сделать нормальное обновление цен через Clock - функции, щас этим и займусь
#
# TODO
#      Узнай по нижнему меню. Весь функционал потом наверн. Хотя мы по ходу делаем, хуле тут функционала
#
# TODO Доделай раздел крипты и подтяг данных в бд. В будущем весь уже премиум-дизайн, типо логичных переходов,
#      если ты с правого экрана в левый заходишь, то и соответствующий переход, и ссответсвующие на выход с
#      Гляну что еще можно спиздить у Тинькофф Инвестиций