import pygame

import config

class FPSCounter:
    def __init__(self, screen, font=None, color=(50, 50, 50), pos=(10, -30)):
        """
        screen:     Pygame surface to draw on
        font:       Optional pygame.font.Font object (uses default if None)
        color:      RGB tuple for text color
        pos:        Tuple (x, y). Use -30 for y to pin to bottom of 600px screen.
        """
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = config.FONT_MONO
        self.color = color
        self.pos = pos

    def tick(self, fps=60):
        return self.clock.tick(fps)

    def draw(self):
        fps = int(self.clock.get_fps())
        text = self.font.render(f"FPS: {fps}", True, self.color)
        x, y = self.pos
        if y < 0:
            y = self.screen.get_height() + y  # e.g. -30 → bottom
        self.screen.blit(text, (x, y))
