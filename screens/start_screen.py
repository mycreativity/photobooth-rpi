from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp
from ui.card import UICard
from ui.polaroid_carousel import PolaroidCarousel
import config

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        window_width, window_height = Window.size

        layout = FloatLayout()  # 🔑 Allows absolute pos + size

        # Background image
        background = Image(
            source='assets/images/background3.png',
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos=(0, 0)
        )
        layout.add_widget(background)

        # Arrow left
        arrow = Image(
            source='assets/images/arrow-down.png',
            keep_ratio=False,
            size_hint=(dp(201), dp(202)),
            pos_hint={"center_x": 0.5, "y": 0}
        )
        layout.add_widget(arrow)

        # Arrow right
        arrow = Image(
            source='assets/images/arrow-down.png',
            # allow_stretch=True,
            # keep_ratio=False,
            # size_hint=(1, 1),
            pos=(300, 0)
        )
        layout.add_widget(arrow)

        self.add_widget(layout)  # Add layout to screen

        # Add carousel in background (or behind layout with z-index logic)
        # self.carousel = PolaroidCarousel()
        # self.add_widget(self.carousel)

    def on_take_photo(self, instance):
        print("Button pressed — countdown coming soon")
