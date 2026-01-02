import pygame
from pygame._sdl2 import Texture
from ui.gpu_image import GPUImage
from ui.gpu_text_label import GPUTextLabel

class GPUImageButton:
    """A button that can contain an image or text and handles clicks."""
    def __init__(self, renderer, text=None, image_path=None, position=(0,0), font=None, color=(255,255,255), size=None, border_radius=0):
        self.renderer = renderer
        self.rect = pygame.Rect(position[0], position[1], 1, 1) # Placeholder
        self.image = None
        self.label = None
        self._bg_color = None
        self._border_radius = border_radius
        self._bg_texture = None
        
        # Priority: Image > Text
        if image_path:
            self.image = GPUImage(renderer, image_path, position)
            if size:
                self.image.resize(size[0], size[1])
            if self.image.image_rect:
                self.rect = self.image.image_rect
        elif text:
            self.label = GPUTextLabel(renderer, text, font, color)
            self.label.set_position(position)
            # Add some padding background
            if self.label.rect:
                self.rect = self.label.rect.inflate(20, 10)
                self.rect.topleft = position
            self._bg_color = (100, 100, 100, 255)

        if self._border_radius > 0:
            self._update_bg_texture()

    @property
    def bg_color(self):
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = value
        self._update_bg_texture()

    @property
    def border_radius(self):
        return self._border_radius
    
    @border_radius.setter
    def border_radius(self, value):
        self._border_radius = value
        self._update_bg_texture()

    def _update_bg_texture(self):
        """Creates a texture for the rounded background."""
        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        if self._bg_color is None or self._border_radius <= 0:
            self._bg_texture = None
            return

        # Create a surface with transparency
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw rounded rect onto surface
        pygame.draw.rect(surf, self._bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=self._border_radius)
        
        # Upload to texture
        self._bg_texture = Texture.from_surface(self.renderer, surf)

    def set_position(self, position):
        self.rect.topleft = position
        if self.image:
            self.image.set_position(position)
        if self.label:
            # Center label in rect
            lx = position[0] + (self.rect.width - self.label.rect.width) // 2
            ly = position[1] + (self.rect.height - self.label.rect.height) // 2
            self.label.set_position((lx, ly))

    def resize(self, display_width, display_height):
        """Scales the button and its contents."""
        w = int(display_width)
        h = int(display_height)
        
        self.rect.width = w
        self.rect.height = h
        
        if self.image:
            self.image.resize(w, h)
            if self.image.image_rect:
                self.rect = self.image.image_rect
        
        # Update background texture if needed
        self._update_bg_texture()

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
             if event.type == pygame.MOUSEBUTTONDOWN:
                 x, y = event.pos
             else:
                 x, y = pygame.mouse.get_pos()
                 
             return self.rect.collidepoint(x, y)
        return False

    def draw(self):
        if self._bg_color:
            if self._bg_texture:
                self._bg_texture.draw(dstrect=self.rect)
            else:
                self.renderer.draw_color = self._bg_color
                self.renderer.fill_rect(self.rect)
            
        if self.image:
            self.image.draw()
        if self.label:
            self.label.draw()
