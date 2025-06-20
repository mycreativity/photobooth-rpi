import pygame
from ui.shapes import create_blurred_shadow
from utils.image_utils import crop_to_square
import os

class Polaroid:
    def __init__(
        self,
        x,
        y,
        image_surface,
        photo_size=240,
        frame_size=(280, 320),
        margin=20,
        radius=18,
        blur_radius=8,
        shadow_color=(0, 0, 0, 60),
        texture_path=None
    ):
        self.rect = pygame.Rect(x, y, *frame_size)
        self.radius = radius
        self.shadow_color = shadow_color
        self.shadow_offset = (4, 4)
        self.blur_radius = blur_radius
        self.margin = margin

        self.surface = pygame.Surface(frame_size, pygame.SRCALPHA)

        # Shadow
        self.shadow_surface, self.shadow_padding = create_blurred_shadow(
            frame_size, radius=self.radius, blur_radius=self.blur_radius, color=self.shadow_color
        )

        # Background texture or fallback
        if texture_path and os.path.exists(texture_path):
            self.texture = pygame.image.load(texture_path).convert()
            self.texture = pygame.transform.smoothscale(self.texture, frame_size)
        else:
            self.texture = None

        # Photo
        self.image = crop_to_square(image_surface)
        self.image = pygame.transform.smoothscale(self.image, (photo_size, photo_size))
        self.image_pos = (margin, margin)


    def render(self):
        """Pre-renders the internal surface (photo + texture or solid color)."""
        self.surface.fill((255, 255, 255))  # fallback background

        if self.texture:
            self.surface.blit(self.texture, (0, 0))

        self.surface.blit(self.image, self.image_pos)

    def draw(self, target_surface: pygame.Surface, rotation=0):
        self.render()

        rotated_photo = pygame.transform.rotate(self.surface, rotation)
        rotated_shadow = pygame.transform.rotate(self.shadow_surface, rotation)

        shadow_rect = rotated_shadow.get_rect(center=self.rect.center)
        photo_rect = rotated_photo.get_rect(center=self.rect.center)

        target_surface.blit(rotated_shadow, shadow_rect.topleft)
        target_surface.blit(rotated_photo, photo_rect.topleft)
