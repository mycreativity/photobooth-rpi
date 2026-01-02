
import pygame
from pygame._sdl2 import Texture
from utils.logger import get_logger

logger = get_logger("GPUTextLabel")

class GPUTextLabel:
    """Renders text as a GPU Texture."""
    
    def __init__(self, renderer, initial_text="Default", font=None, color=(255, 255, 255)):
        self.renderer = renderer
        self.font = font or pygame.font.Font(None, 20)
        self.color = color
        self.position = (0, 0)
        
        self.surface = None
        self.texture = None
        self.rect = None
        
        self.update_text(initial_text)

    def update_text(self, text):
        """Creates new surface and texture from text."""
        try:
            self.surface = self.font.render(text, True, self.color)
            self.rect = self.surface.get_rect(topleft=self.position)
            
            # Create/Update Texture
            if self.renderer:
                if self.texture:
                    del self.texture 
                self.texture = Texture.from_surface(self.renderer, self.surface)
                
        except pygame.error as e:
            logger.error(f"Error rendering text: {e}")

    def set_position(self, position):
        self.position = position
        if self.rect:
            self.rect.topleft = position

    def draw(self):
        if self.texture and self.rect:
            self.texture.draw(dstrect=self.rect)

    def cleanup(self):
        if self.texture:
            del self.texture
            self.texture = None
