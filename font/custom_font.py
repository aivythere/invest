from investing import hardconfig
from kivy.metrics import dp
import re
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.animation import Animation

def bbClearText(text: str):
    return re.sub('\[.*?]', '', text)

class UnexpectedFontStyle(Exception):
    pass

class SFLabel(MDLabel):
    def __init__(self, text: str, color = hardconfig.PRIMARY_TEXT_COLOR, markup=True, halign='center', valign='center',
                 font_style="Regular", pos_hint=None, font_size=None, size_hint=None):
        super().__init__()
        """
        Font_size если указывается то ТОЛЬКО custom17, или четотакое
        """
        self.theme_text_color = "Custom"
        self.text_color = color
        self.valign = valign
        self.halign = halign
        self.markup = markup
        self.text = text
        if size_hint is not None:
            self.size_hint = size_hint
        if pos_hint is not None:
            self.pos_hint = pos_hint
        self.font_name = f"./font/SF_{font_style}"

        if font_size is not None:
            if font_size == "dynamic":
                clear_len = len(bbClearText(self.text))
                self.font_size = dp(16) if self.text == "" else 48 - (clear_len / 5)
            elif "dp" in font_size:
                self.font_size = dp(int(font_size.replace("dp", "")))
            else:
                self.font_size = dp(32)
                print("! using hardcoded font style !")

builder_str = """

<AKLabelLoader>:
    canvas.before:
        Color:
            rgba: root.theme_cls.bg_darkest
            a: root.fr_rec_opacity
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [(dp({}),dp({})) , (dp({}),dp({})),(dp({}),dp({})),(dp({}),dp({})) ]
        Color:
            rgba: root.theme_cls.bg_dark
            a: root.bg_rec_opacity
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [(dp({}),dp({})) , (dp({}),dp({})),(dp({}),dp({})),(dp({}),dp({})) ]

            """


class AKLabelLoader(MDLabel):
    bg_rec_opacity = NumericProperty(0)
    fr_rec_opacity = NumericProperty(0)

    def __init__(self, markup=True, bold=False, round_=10, color=hardconfig.PRIMARY_TEXT_COLOR, **kwargs):
        builder_str_format = tuple(f'{round_}' for _ in range(builder_str.count("{}")))
        Builder.load_string(builder_str.format(*builder_str_format))  #  89
        self.start_anim = None
        super().__init__(**kwargs)
        self.markup = markup
        self.theme_text_color = "Custom"
        self.text_color = color
        self.bold = bold
        self.font_name = './font/SF_Regular' if not self.bold else './font/SF_Bold'
        Clock.schedule_once(lambda x: self._update(self.text))

    def _update(self, text):
        if self._check_text(text):
            self._stop_animate()
        else:
            self._start_animate()

    def _check_text(self, text):
        if not text:
            return False
        else:
            return True

    def _start_animate(self):
        if not self._check_text(self.text):
            self.bg_rec_opacity = 1
            self.fr_rec_opacity = 1
            duration = hardconfig.ANIMATION_RUNNING_SPEED
            self.start_anim = Animation(bg_rec_opacity=1, t='in_quad', duration=duration)\
                + Animation(bg_rec_opacity=hardconfig.LOADING_ANIMATION_OPACITY, t='out_quad', duration=duration)
                # + Animation(bg_rec_opacity=0, t='out_quad', duration=duration)
            self.start_anim.repeat = True
            self.start_anim.start(self)

    def _stop_animate(self):
        if self.start_anim is not None:
            Animation.cancel_all(self)
            self.bg_rec_opacity = 0
            self.fr_rec_opacity = 0

    def on_text(self, *args):
        if self._check_text(self.text):
            self._stop_animate()

        else:
            self._start_animate()
