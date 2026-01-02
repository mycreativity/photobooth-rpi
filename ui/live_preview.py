import pygame
from pygame._sdl2 import Texture
from utils.logger import get_logger

logger = get_logger("LivePreview")

class LivePreview:
    """
    Handles the conversion of camera frames to GPU textures 
    and manages 'Crop-to-Fill' logic for a specific display area.
    """
    
    def __init__(self, renderer, display_width, display_height):
        self.renderer = renderer
        self.display_w = display_width
        self.display_h = display_height
        self.display_ratio = display_width / display_height
        
        self.texture = None
        self.src_rect = None
        
        # Track frame dimensions to avoid redundant texture creation
        self.tex_w = 0
        self.tex_h = 0

    def _calculate_crop(self, frame_w, frame_h):
        """Calculates the srcrect to center-crop the camera frame to the screen ratio."""
        frame_ratio = frame_w / frame_h
        
        if frame_ratio > self.display_ratio:
            # Camera is wider than screen (Crop sides)
            crop_w = int(frame_h * self.display_ratio)
            offset_x = (frame_w - crop_w) // 2
            self.src_rect = pygame.Rect(offset_x, 0, crop_w, frame_h)
        else:
            # Camera is taller than screen (Crop top/bottom)
            crop_h = int(frame_w / self.display_ratio)
            offset_y = (frame_h - crop_h) // 2
            self.src_rect = pygame.Rect(0, offset_y, frame_w, crop_h)

    def update(self, pil_image):
        """Updates the GPU texture with a new PIL image."""
        if pil_image is None:
            return

        w, h = pil_image.size

        # 1. Initialize or Re-initialize texture if resolution changed
        if self.texture is None or w != self.tex_w or h != self.tex_h:
            self.tex_w, self.tex_h = w, h
            self._calculate_crop(w, h)
            
            if self.texture:
                # Proper cleanup for SDL2 textures
                self.texture.destroy()
            
            try:
                self.texture = Texture(self.renderer, (w, h), streaming=True)
                self.texture.blend_mode = 1
                logger.info(f"Created new {w}x{h} streaming texture.")
            except Exception as e:
                logger.error(f"Texture creation failed: {e}")
                return

        # 2. Upload Pixel Data
        try:
            # Note: pygame-ce Texture.update() can take a Surface
            # Convert PIL to Surface quickly via bytes
            mode = pil_image.mode
            surface = pygame.image.frombytes(pil_image.tobytes(), (w, h), mode)
            self.texture.update(surface)
        except Exception as e:
            logger.error(f"Texture update failed: {e}")

    def draw(self, x=0, y=0, width=None, height=None, flip_x=True):
        """Renders the cropped texture to the specified screen area."""
        if not self.texture:
            return

        # Default to full screen if no dimensions provided
        target_w = width if width is not None else self.display_w
        target_h = height if height is not None else self.display_h
        
        # dstrect is where on the screen it goes
        dst_rect = pygame.Rect(x, y, target_w, target_h)
        
        # Draw the cropped portion (src_rect) to the target area (dst_rect)
        self.texture.draw(srcrect=self.src_rect, dstrect=dst_rect, flip_x=flip_x)

    def release(self):
        """Explicitly release GPU resources."""
        if self.texture:
            self.texture.destroy()
            self.texture = None