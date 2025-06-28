from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.utils import get_color_from_hex
import os

class UICard(BoxLayout):
    

    def __init__(self, size=(500, 300), padding=20, orientation='vertical', color_hex='#eedabaff', **kwargs):
        super().__init__(**kwargs)
        self.orientation = orientation
        self.padding = padding
        self.size_hint = (None, None)  # Required to see size-based rendering
        self.size = size
        self.bg_color = get_color_from_hex(color_hex) 

        # Load shadow texture
        
        with self.canvas.before:
            # Shadow image
            self.shadow_image = Image(
                        source='assets/images/shadow.png',
                        allow_stretch=True,
                        keep_ratio=False,
                        size_hint=(1, 1),
                        pos=(0, 0)
                    )
            
            # Background card
            self.bg_color_instr = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(radius=[20], size=self.size)

        # React to layout changes
        # self.bind(pos=self.update_canvas, size=self.update_canvas, bg_color=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        shadow_padding = 87
        sizing_factor_x = self.width/500
        sizing_factor_y = self.height/500
        shadow_padding_x = shadow_padding * sizing_factor_x
        shadow_padding_y = shadow_padding * sizing_factor_y
        # self.shadow_image.pos = (self.x - shadow_padding, self.y - shadow_padding)
        # self.shadow_image.size = (self.width + 2 * shadow_padding, self.height + 2 * shadow_padding)
        self.shadow_image.pos = (self.x - shadow_padding_x, self.y - shadow_padding_y)
        self.shadow_image.size = (self.width + 2 * shadow_padding_x, self.height + 2 * shadow_padding_y)

        self.bg_color_instr.rgba = self.bg_color
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
