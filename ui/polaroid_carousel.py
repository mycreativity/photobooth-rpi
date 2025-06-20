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
        img = pygame.image.load(path).convert()
        # Initial dummy position (will be updated dynamically)
        return Polaroid(x=0, y=0, image_surface=img)

    def update(self, dt):
        self.angle += self.speed * dt

    def draw(self, surface):
        for i, polaroid in enumerate(self.polaroids):
            theta = self.angle + self.static_offsets[i]
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)

            # Position
            x = self.center[0] + cos_theta * self.radius
            y = self.center[1] + sin_theta * self.radius * 0.7

            # Depth & transform properties
            depth = 1 - sin_theta
            scale = self.front_scale + (self.back_scale - self.front_scale) * depth * 0.5
            tilt_angle = int(10 * cos_theta)

            # Precompute scaled sizes
            photo_size = (int(280 * scale), int(320 * scale))
            shadow_size = (int(320 * scale), int(360 * scale))

            # Ensure rendered content
            polaroid.render()

            # Scale and rotate both surfaces
            rotated_surface = pygame.transform.rotate(
                pygame.transform.smoothscale(polaroid.surface, photo_size), tilt_angle
            )
            rotated_shadow = pygame.transform.rotate(
                pygame.transform.smoothscale(polaroid.shadow_surface, shadow_size), tilt_angle
            )

            # Compute rects and blit
            center_pos = (int(x), int(y))
            surface.blit(rotated_shadow, rotated_shadow.get_rect(center=center_pos))
            surface.blit(rotated_surface, rotated_surface.get_rect(center=center_pos))

