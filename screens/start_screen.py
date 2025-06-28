from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
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
            source='assets/images/background.png',
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos=(0, 0)
        )
        layout.add_widget(background)

        # Card in center
        card_size = (window_width / 2, window_height / 2)
        card_x = (window_width - card_size[0]) / 2
        card_y = -12  # from bottom
        card = UICard(
            color_hex=config.SURFACE_COLOR,
            size_hint=(None, None),
            size=card_size,
            pos=(card_x, card_y)
        )

        card.add_widget(Label(
            text="Take Your Photo!", 
            font_name=config.FONT_HEADING, 
            font_size='60sp', 
            color=get_color_from_hex(config.SECONDARY_COLOR), 
            size_hint=(1, 0.05),
            pos_hint={'y': 0.7}
            ))
        
        button = Button(text="TAKE PHOTO", size_hint=(1, 0.2), font_size='32sp')
        button.bind(on_press=self.on_take_photo)
        card.add_widget(button)

        card.add_widget(Label(
            text="Press any button to start", 
            font_name=config.FONT_LABEL, 
            font_size='30sp', 
            color=get_color_from_hex(config.SECONDARY_COLOR), 
            size_hint=(1, 0.1)
            ))

        

        layout.add_widget(card)

        self.add_widget(layout)  # Add layout to screen

        # Add carousel in background (or behind layout with z-index logic)
        # self.carousel = PolaroidCarousel()
        # self.add_widget(self.carousel)

    def on_take_photo(self, instance):
        print("Button pressed — countdown coming soon")
