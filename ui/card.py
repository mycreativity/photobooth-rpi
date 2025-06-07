import pygame
import numpy as np
from scipy.ndimage import gaussian_filter
from ui.button import RetroButton
from ui.shapes import create_blurred_shadow, draw_rounded_rect_aa
from ui.text import UIText

class UICard:
    def __init__(self, x, y, width, height, color=(240, 224, 191), radius=20,
                 shadow_offset=(8, 8), blur_radius=10, shadow_color=(0, 0, 0, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.radius = radius
        self.shadow_offset = shadow_offset
        self.blur_radius = blur_radius
        self.shadow_color = shadow_color

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.shadow_surface, self.shadow_padding = self._create_blurred_shadow()

    def _create_blurred_shadow(self):
        return create_blurred_shadow(
            (self.rect.width, self.rect.height),
            radius=self.radius,
            blur_radius=self.blur_radius,
            color=self.shadow_color
        )



    def draw_content(self, surface: pygame.Surface):
        """
        Override this method to draw widgets (e.g., buttons) onto the card.
        """
        pass

    def draw(self, target_surface: pygame.Surface):
        # Step 1: Clear the card surface
        self.surface.fill((0, 0, 0, 0))

        # Step 2: Draw rounded background
        draw_rounded_rect_aa(self.surface, self.surface.get_rect(), self.color, radius=self.radius)

        # Step 3: Draw custom content
        self.draw_content(self.surface)

        # Step 4: Draw shadow and card onto target
        shadow_pos = (
            self.rect.x - self.shadow_padding + self.shadow_offset[0],
            self.rect.y - self.shadow_padding + self.shadow_offset[1]
        )
        target_surface.blit(self.shadow_surface, shadow_pos)
        target_surface.blit(self.surface, self.rect.topleft)

class StartCard(UICard):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,
                         color=(240, 224, 191),
                         radius=20,
                         shadow_offset=(6, 6),
                         blur_radius=8,
                         shadow_color=(0, 0, 0, 40))
        # Title text
        self.title = UIText(
            text="Take Your Photo!",
            font=pygame.font.Font("assets/fonts/Pacifico-Regular.ttf", 60),
            color=(101, 56, 29),
            pos=(self.rect.width // 2, 20),
            align="midtop"
        )

        # button
        self.button = RetroButton(
            rect=((self.surface.get_width() / 2) - (450 // 2), 140, 450, 100),
            text="TAKE PHOTO",
            text_color=(240, 224, 191),
            icon_surface=pygame.image.load("assets/images/camera_icon.png").convert_alpha(),
            font=pygame.font.Font("assets/fonts/Roboto-ExtraBold.ttf", 50),
            base_color=(226, 85, 39),
            shadow_color=(180, 60, 25)
        )

        # Subtitle text
        self.subtitle = UIText(
            text="Touch the screen to start!",
            font=pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 32),
            color=(101, 56, 29),
            pos=(self.rect.width // 2, 280),
            align="midtop"
        )

    def draw_content(self, surface: pygame.Surface):
        self.title.draw(surface)
        self.button.draw(surface)
        self.subtitle.draw(surface)
