import pygame
from pygame._sdl2 import Texture
from ui.image import Image
from ui.text_label import TextLabel

class Button:
    """
    A unified button class that supports both native Pygame rendering (rounded rects, borders)
    and image-based buttons.
    """
    def __init__(self, 
                 renderer, 
                 position=(0, 0), 
                 size=None,
                 text=None, 
                 font=None, 
                 color=(255, 255, 255), 
                 bg_color=None,
                 border_color=None,
                 border_radius=0,
                 border_width=0,
                 padding=0,
                 image_path=None,
                 text_offset=(0, 0),
                 **kwargs):
        
        self.renderer = renderer
        self.rect = pygame.Rect(position[0], position[1], 1, 1)
        
        self.text = text
        self.font = font
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.padding = padding
        self.image_path = image_path
        self.text_offset = text_offset
        
        self.label = None
        self.image = None
        self._bg_texture = None # For caching the background if it has complex alpha/radius

        # Set initial Size if provided
        if size:
            self.rect.width = size[0]
            self.rect.height = size[1]
        
        # Initialize Content
        self._init_content()

    def _init_content(self):
        # 1. Image Content
        if self.image_path:
            self.image = Image(self.renderer, self.image_path, self.rect.topleft)
            # If size was not set, take image size
            if self.rect.width <= 1 and self.image.image_rect:
                 self.rect.size = self.image.image_rect.size
            else:
                 self.image.resize(self.rect.width, self.rect.height)
        
        # 2. Text Content
        if self.text and self.font:
            self.label = TextLabel(self.renderer, self.text, self.font, self.color)
            
            # Auto-size if no explicit size and no image
            if self.rect.width <= 1 and not self.image:
                lbl_w = self.label.rect.width + (self.padding * 2)
                lbl_h = self.label.rect.height + (self.padding * 2)
                self.rect.width = lbl_w
                self.rect.height = lbl_h

        self._update_texture()
        self.center_content()
    
    def _update_texture(self):
        """Creates a texture for the background if needed (rounded corners + alpha)."""
        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        has_alpha = False
        if self.bg_color and len(self.bg_color) == 4 and self.bg_color[3] < 255:
            has_alpha = True
        
        # If we have rounded corners OR alpha, simpler to draw to a surface and upload
        if self.border_radius > 0 or has_alpha:
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # Draw Background
            if self.bg_color:
                pygame.draw.rect(surf, self.bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
            
            # Draw Border
            if self.border_color and self.border_width > 0:
                 pygame.draw.rect(surf, self.border_color, (0, 0, self.rect.width, self.rect.height), width=self.border_width, border_radius=self.border_radius)

            self._bg_texture = Texture.from_surface(self.renderer, surf)
        else:
            self._bg_texture = None

    def set_position(self, position):
        self.rect.topleft = position
        if self.image:
            self.image.set_position(position)
        
        self.center_content()

    def resize(self, width, height):
        self.rect.width = width
        self.rect.height = height
        
        if self.image:
            self.image.resize(width, height)
            
        self._update_texture()
        self.center_content()

    def center_content(self):
        # Center Label
        if self.label:
             lx = self.rect.x + (self.rect.width - self.label.rect.width) // 2 + self.text_offset[0]
             ly = self.rect.y + (self.rect.height - self.label.rect.height) // 2 + self.text_offset[1]
             self.label.set_position((lx, ly))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
             if event.type == pygame.MOUSEBUTTONDOWN:
                 x, y = event.pos
             else:
                 # Simplified finger pos
                 x, y = pygame.mouse.get_pos()
                 
             return self.rect.collidepoint(x, y)
        return False

    def draw(self):
        # 1. Draw Background/Border
        if self._bg_texture:
            self._bg_texture.draw(dstrect=self.rect)
        else:
            if self.bg_color:
                self.renderer.draw_color = self.bg_color
                self.renderer.fill_rect(self.rect)
            if self.border_color and self.border_width > 0:
                self.renderer.draw_color = self.border_color
                self.renderer.draw_rect(self.rect)

        # 2. Draw Image
        if self.image:
            self.image.draw()

        # 3. Draw Text
        if self.label:
            self.label.draw()
