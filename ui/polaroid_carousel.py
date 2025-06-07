import pygame
import math
import os

from ui.polaroid import Polaroid  # ← use the new class

class PolaroidCarousel:
    def __init__(
        self,
        image_paths,
        max_photos=12,
        radius=900,
        center=(540, 900),
        speed=0.3,
        front_scale=0.6,
        back_scale=1.2,
        fade=True,
    ):
        self.center = center
        self.radius = radius
        self.speed = speed
        self.angle = 0
        self.front_scale = front_scale
        self.back_scale = back_scale
        self.fade = fade

        self.image_paths = image_paths[-max_photos:]
        self.static_offsets = [i * (2 * math.pi / len(self.image_paths)) for i in range(len(self.image_paths))]

        self.polaroids = [self._make_polaroid(path) for path in self.image_paths]

    def _make_polaroid(self, path):
        img = pygame.image.load(path).convert_alpha()
        # Initial dummy position (will be updated dynamically)
        return Polaroid(x=0, y=0, image_surface=img)

    def update(self, dt):
        self.angle += self.speed * dt

    def draw(self, surface):
        for i, polaroid in enumerate(self.polaroids):
            theta = self.angle + self.static_offsets[i]

            # Virtual 3D orbit calculation
            x = self.center[0] + math.cos(theta) * self.radius
            y = self.center[1] + math.sin(theta) * self.radius * 0.7

            depth = (1 - math.sin(theta))  # back = 2, front = 0
            scale = self.front_scale + (self.back_scale - self.front_scale) * depth * 0.5
            tilt = int(10 * math.cos(theta))

            # ✅ Ensure content is drawn
            polaroid.render()

            # Scale and rotate internal surfaces
            scaled_surface = pygame.transform.smoothscale(polaroid.surface, (int(280 * scale), int(320 * scale)))
            rotated_surface = pygame.transform.rotate(scaled_surface, tilt)

            # Likewise scale and rotate shadow
            scaled_shadow = pygame.transform.smoothscale(polaroid.shadow_surface, (int(320 * scale), int(360 * scale)))
            rotated_shadow = pygame.transform.rotate(scaled_shadow, tilt)

            # Draw shadow
            shadow_rect = rotated_shadow.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_shadow, shadow_rect.topleft)

            # Draw polaroid
            photo_rect = rotated_surface.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_surface, photo_rect.topleft)
