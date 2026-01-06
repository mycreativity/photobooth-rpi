import pygame
from pygame._sdl2 import Texture
from utils.logger import get_logger

logger = get_logger("TextLabel")
 
class TextLabel:
    """Renders text as a GPU Texture."""
    
    def __init__(self, renderer, text="Default", font=None, color=(255, 255, 255)):
        self.renderer = renderer
        self.font = font or pygame.font.Font(None, 20)
        self.color = color
        self.position = (0, 0)
        
        self.surface = None
        self.texture = None
        self.rect = None
        
        self.update_text(text)
        
        # Animation properties
        self.alpha = 255
        self.scale = 1.0

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
                # Enable alpha blending
                self.texture.blend_mode = 1
                
        except pygame.error as e:
            logger.error(f"Error rendering text: {e}")

    def set_position(self, position):
        self.position = position
        if self.rect:
            self.rect.topleft = position

    def draw(self):
        if self.texture and self.rect:
            # Update texture alpha
            self.texture.alpha = int(max(0, min(255, self.alpha)))
            
            if self.scale == 1.0:
                self.texture.draw(dstrect=self.rect)
            else:
                # Calculate scaled rect centered at original position center
                w = int(self.rect.width * self.scale)
                h = int(self.rect.height * self.scale)
                cx, cy = self.rect.center
                scaled_rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
                self.texture.draw(dstrect=scaled_rect)

    def cleanup(self):
        if self.texture:
            del self.texture
            self.texture = None
