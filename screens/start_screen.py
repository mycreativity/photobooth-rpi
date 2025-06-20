import os
import pygame
import config
from screens.base_screen import BaseScreen
from screens.countdown_screen import CountdownScreen
from ui.button import RetroButton
from ui.card import UICard
from ui.polaroid_carousel import PolaroidCarousel
from ui.shapes import create_blurred_shadow
from ui.text import UIText

class StartScreen(BaseScreen):
    def __init__(self, screen, background):
        super().__init__(screen)
        self.background = background

        # Set up the card positions
        card_width = screen.get_width() // 2
        card_height = 400
        card_x = (screen.get_width() - card_width) // 2
        card_y = screen.get_height() // 2 - 50

        # Create start card with button
        self.card = StartCard(
            card_x, 
            card_y, 
            card_width, 
            card_height
        )

        # Load screensaver images
        paths = [os.path.join("photos", f) for f in sorted(os.listdir("photos")) if f.endswith(".jpg")]
        self.carousel = PolaroidCarousel(image_paths=paths, speed=0.1)


    def handle_event(self, event, switch_screen):
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Screen clicked — starting countdown!")
            switch_screen(CountdownScreen, self.background)

    def update(self, context, switch_screen):
        self.carousel.update(context["dt"])
        # self.card.button.is_clicked(context["event"])
        pass

    def draw(self):
        self.carousel.draw(self.screen)
        self.card.draw(self.screen)
        
class StartCard(UICard):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,
                         color=(240, 224, 191),
                         radius=20,
                         shadow_offset=(6, 6),
                         blur_radius=8,
                         shadow_color=(0, 0, 0, 60))
        # Title text
        self.title = UIText(
            text="Take Your Photo!",
            font=config.FONT_DISPLAY,
            color=(101, 56, 29),
            pos=(self.rect.width // 2, 20),
            align="midtop"
        )

        # button
        self.button = RetroButton(
            rect=((self.surface.get_width() / 2) - (450 // 2), 140, 450, 100),
            text="TAKE PHOTO",
            text_color=(240, 224, 191),
            icon_surface=pygame.image.load("assets/images/camera_icon2.png").convert_alpha(),
            font=config.FONT_BUTTON_LARGE,
            base_color=config.PRIMARY_COLOR,
            shadow_color=config.PRIMARY_COLOR_DARK
        )

        self.button_shadow, padding = create_blurred_shadow(
            (self.button.rect.width, self.button.rect.height),
            radius=10,
            blur_radius=10,
            color=(0, 0, 0, 40)
        )

        # Subtitle text
        self.subtitle = UIText(
            text="Touch the screen to start!",
            font=config.FONT_LABEL,
            color=(101, 56, 29),
            pos=(self.rect.width // 2, 280),
            align="midtop"
        )

    def draw_content(self, surface: pygame.Surface):
        self.title.draw(surface)
        surface.blit(self.button_shadow, self.button.rect.topleft)
        self.button.draw(surface)
        self.subtitle.draw(surface)