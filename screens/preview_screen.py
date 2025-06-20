import datetime
import os
import pygame
import config
from ui.button import CircularRetroButton, RetroButton
from ui.card import UICard
from ui.polaroid import Polaroid
from ui.shapes import create_blurred_shadow
from ui.text import UIText
from utils.image_utils import crop_to_square

class PreviewScreen:
    def __init__(self, screen, background, photo_surface):
        self.screen = screen
        self.background = background
        screen_w, screen_h = screen.get_size()
        
        # Title text
        self.title = UIText(
            text="Here's Your Photo!",
            font=config.FONT_HEADING,
            color=(101, 56, 29),
            pos=(screen_w // 2 // 2, 30),
            align="midtop"
        )

        self.photo = Polaroid(
            x=40, 
            y=15, 
            image_surface=photo_surface,
            photo_size=500, 
            frame_size=(540, 610), 
            margin=20, 
            radius=18, 
            blur_radius=8,
            shadow_color=(0, 0, 0, 60),
            texture_path=None
        )
        
        self.card = PreviewCard(screen_w - 420, 20, 440, screen_h - 40)

        # Again button
        self.remove_button = CircularRetroButton(
            center=(60, 530),
            diameter=75,
            icon_surface=pygame.image.load("assets/images/delete_icon.png").convert_alpha(),
            base_color=config.PRIMARY_COLOR,
            shadow_color=config.PRIMARY_COLOR_DARK,
        )

    def handle_event(self, event, switch_screen):
        local_pos = self.card.handle_event(event)
        if local_pos:
            # Create a fake event with local coordinates
            fake_event = pygame.event.Event(event.type, {"pos": local_pos, "button": event.button})

            if self.card.print_button.is_clicked(fake_event):
                print("✅ Photo is being printed!")
            elif self.card.retake_button.is_clicked(fake_event):
                print("🔁 Retaking photo")
                from screens.start_screen import StartScreen
                switch_screen(StartScreen, self.background)

    def update(self, context, switch_screen):
        pass

    def draw(self):
        self.photo.draw(self.screen, rotation=3)
        self.title.draw(self.screen)
        self.remove_button.draw(self.screen)
        self.card.draw(self.screen)


class PreviewCard(UICard):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,
                         color=(240, 224, 191),
                         radius=20,
                         shadow_offset=(6, 6),
                         blur_radius=8,
                         shadow_color=(0, 0, 0, 40))
        
        card_w, card_h = self.surface.get_size()

        # Title text
        self.title = UIText(
            text="Options:",
            font=config.FONT_HEADING,
            color=(101, 56, 29),
            pos=(card_w // 2, 10),
            align="midtop"
        )

        # Again button
        self.retake_button = CircularRetroButton(
            center=(card_w // 2, 180),
            diameter=150,
            icon_surface=pygame.image.load("assets/images/camera_icon2.png").convert_alpha(),
            base_color=config.PRIMARY_COLOR,
            shadow_color=config.PRIMARY_COLOR_DARK,
            label_text="Another Photo",
            label_font=config.FONT_LABEL,
            label_color=(50, 30, 20)
        )

        # Print button
        self.print_button = CircularRetroButton(
            center=(card_w // 2, 420),
            diameter=150,
            icon_surface=pygame.image.load("assets/images/print_icon.png").convert_alpha(),
            base_color=config.SECONDARY_COLOR,
            shadow_color=config.SECONDARY_COLOR_DARK,
            label_text="Print Photo",
            label_font=config.FONT_LABEL,
            label_color=(50, 30, 20)
        )


    def draw_content(self, surface: pygame.Surface):
        self.title.draw(surface)
        self.retake_button.draw(surface)
        self.print_button.draw(surface)