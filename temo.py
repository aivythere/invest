from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from investing import hardconfig

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


class MyApp(MDApp): # PP
    def build(self):
        bl = MDBoxLayout()
        self.theme_cls.theme_style = hardconfig.APP_THEME
        bl.add_widget(AKLabelLoader(text=''))
        return bl

MyApp().run()