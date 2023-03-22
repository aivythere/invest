from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from temo import tmp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import Color, Rectangle, Line
from tinkoff.invest import Quotation
from collections import defaultdict


def convertPrice(input: Quotation):
    rub = input.units
    decimals = input.nano
    max_quotation_nano = 1_000_000_000
    return rub + decimals / max_quotation_nano


candle_dict = defaultdict(dict)
lines = []


def generate_graph_info(tmp=tmp):
    for iter_, value in enumerate(tmp.candles):
        candle_dict[str(iter_)]['open'] = convertPrice(value.open)
        candle_dict[str(iter_)]['high'] = convertPrice(value.high)
        candle_dict[str(iter_)]['low'] = convertPrice(value.low)
        candle_dict[str(iter_)]['close'] = convertPrice(value.close)

generate_graph_info()

for i in candle_dict.keys():
    lines.append(
        Line(
            width=2,
            rectange=(candle_dict[i]['open']/100, candle_dict[i]['close']/100, i*5, i*5)
        )
    )

print(lines)

class Graph(MDBoxLayout):
    def __init__(self):
        super().__init__()
        self.pos_hint = {'center_x': .5, 'center_y': .5}
        self.size_hint = [1, 1]
        for i in lines:
            with self.canvas.before:
                Color(1, 1, 1, 1)
                self.line = i


class App(MDApp):
    def build(self):
        main_bl = MDGridLayout(cols=2, rows=2)
        self.theme_cls.theme_style = 'Dark'
        main_bl.add_widget(Graph())
        main_bl.add_widget(MDBoxLayout())

        return main_bl

App().run()
