import pygame
from ui.shapes import create_blurred_shadow
from utils.image_utils import crop_to_square

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
        texture_path="assets/images/polaroid_paper_texture.png"
    ):
        self.rect = pygame.Rect(x, y, *frame_size)
        self.radius = radius
        self.shadow_color = shadow_color
        self.shadow_offset = (4, 4)
        self.blur_radius = blur_radius

        self.surface = pygame.Surface(frame_size, pygame.SRCALPHA)

        # Prepare shadow
        self.shadow_surface, self.shadow_padding = create_blurred_shadow(
            frame_size, radius=self.radius, blur_radius=self.blur_radius, color=self.shadow_color
        )

        # Prepare background
        self.texture = pygame.image.load(texture_path).convert()
        self.texture = pygame.transform.smoothscale(self.texture, frame_size)

        # Prepare image
        self.image = crop_to_square(image_surface)
        self.image = pygame.transform.smoothscale(self.image, (photo_size, photo_size))
        self.image_pos = (margin, margin)

    def render(self):
        """Pre-renders the internal surface (photo + texture)."""
        self.surface.fill((0, 0, 0, 0))  # Clear
        self.surface.blit(self.texture, (0, 0))
        self.surface.blit(self.image, self.image_pos)

    def draw(self, target_surface: pygame.Surface):
        # Step 1: draw to internal surface
        self.surface.blit(self.texture, (0, 0))
        self.surface.blit(self.image, self.image_pos)

        # Step 2: draw shadow first
        shadow_pos = (
            self.rect.x - self.shadow_padding + self.shadow_offset[0],
            self.rect.y - self.shadow_padding + self.shadow_offset[1],
        )
        target_surface.blit(self.shadow_surface, shadow_pos)

        # Step 3: draw photo with frame
        target_surface.blit(self.surface, self.rect.topleft)