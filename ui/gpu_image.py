
import pygame
from pygame._sdl2 import Texture
from utils.logger import get_logger

logger = get_logger("GPUImage")

class GPUImage:
    """
    Renders and manages an image as a hardware-accelerated texture using Pygame-CE's SDL2 Renderer.
    """
    
    def __init__(self, renderer, image_path, position=(0, 0)):
        self.renderer = renderer
        self.image_path = image_path
        self.position = position # (x, y)
        
        self.surface = None 
        self.texture = None
        self.image_rect = None 
        
        # Animation properties
        self.alpha = 255
        self.scale = 1.0
        
        # Load immediately
        self.load_image(self.image_path)

    def load_image(self, path):
        """Loads the image from disk and creates the GPU texture."""
        try:
            # 1. Load Surface
            self.surface = pygame.image.load(path)
            
            # 2. Update Rect
            self.image_rect = self.surface.get_rect(topleft=self.position)
            
            # 3. Create GPU Texture
            self.update_texture()
            
            return True
        except pygame.error as e:
            logger.error(f"Error loading image '{path}': {e}")
            self.surface = None
            return False

    def resize(self, new_width, new_height):
        """
        Scales the underlying surface and updates the texture.
        Use this for one-time resizing (e.g. initialization).
        For real-time zooming, use draw scaling.
        """
        if not self.surface:
            return

        self.surface = pygame.transform.smoothscale(
            self.surface, 
            (int(new_width), int(new_height))
        )
        self.update_texture()

    def update_texture(self):
        """Uploads the current surface to the GPU."""
        if not self.surface:
            return
            
        try:
            # Create a static texture (access=0 default)
            self.texture = Texture.from_surface(self.renderer, self.surface)
            # Enable alpha blending (1 = SDL_BLENDMODE_BLEND)
            self.texture.blend_mode = 1
            # Update rect size in case of resize
            self.image_rect = self.surface.get_rect(topleft=self.position)
        except Exception as e:
            logger.error(f"Failed to create texture: {e}")

    def set_position(self, position):
        """Updates the pixel position."""
        self.position = position
        if self.image_rect:
            self.image_rect.topleft = position

    def draw(self):
        """Draws the texture to the renderer with current scale and alpha."""
        if not self.texture:
            return
            
        # Update texture alpha
        self.texture.alpha = int(max(0, min(255, self.alpha)))
        
        if self.scale == 1.0:
            self.texture.draw(dstrect=self.image_rect)
        else:
            # Calculate scaled rect centered at original position center
            w = int(self.image_rect.width * self.scale)
            h = int(self.image_rect.height * self.scale)
            cx, cy = self.image_rect.center
            scaled_rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
            self.texture.draw(dstrect=scaled_rect)

    def cleanup(self):
        """Releases the texture."""
        if self.texture:
            # Pygame textures are auto-collected, but explicit is fine
            del self.texture
            self.texture = None
