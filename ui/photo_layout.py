import pygame
from pygame._sdl2 import Texture
from ui.image import Image
from ui.text_label import TextLabel
from config import *

class PhotoFrame:
    """
    Represents a single photo slot within a layout.
    Can display an image placeholder and an index/text label.
    """
    def __init__(self, 
                 renderer, 
                 image_path="assets/images/photo_mock_1.png",
                 text="1",
                 size=(300,200),
                 position=(0, 0), 
                 font_color=(0, 0, 0), 
                 bg_color=(255, 255, 0)):
        
        self.renderer = renderer
        self.rect = pygame.Rect(position[0], position[1], 1, 1)
        self.position = position    
        self.text = text
        self.font = FONT_DISPLAY_SMALL
        self.color = font_color
        self.bg_color = bg_color
        self.image_path = image_path
        
        self.label = None
        self.image = None

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
            self.image.resize_to_fit(self.rect.width, self.rect.height)        
        # 2. Text Content
        if self.text and self.font:
            self.label = TextLabel(renderer=self.renderer, text=self.text, font=self.font, color=self.color)

        self._update_texture()
    
    def _update_texture(self):
        """Creates a texture for the background if needed."""
        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        has_alpha = False
        if self.bg_color and len(self.bg_color) == 4 and self.bg_color[3] < 255:
            has_alpha = True
        
        # If we have alpha, simpler to draw to a surface and upload
        if has_alpha:
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # Draw Background
            if self.bg_color:
                pygame.draw.rect(surf, self.bg_color, (0, 0, self.rect.width, self.rect.height))
            
            self._bg_texture = Texture.from_surface(self.renderer, surf)
        else:
            self._bg_texture = None

    def set_position(self, position):
        self.rect.topleft = position

        if self.image:
            self.image.set_position(position)
        
        if self.label:
             # Center Label
             lx = self.rect.x + (self.rect.width * 0.75 - self.label.rect.width / 2)
             ly = self.rect.y + (self.rect.height * 0.75 - self.label.rect.height / 2)
             self.label.set_position((lx, ly))

    def resize(self, width, height):
        self.rect.width = width
        self.rect.height = height
        
        if self.image:
            self.image.resize(width, height)
            
        self._update_texture()

    def draw(self):
        # 1. Draw Background
        if self._bg_texture:
            self._bg_texture.draw(dstrect=self.rect)
        elif self.bg_color:
             self.renderer.draw_color = self.bg_color
             self.renderer.fill_rect(self.rect)

        # 2. Draw Image
        if self.image:
            self.image.draw()

        # 3. Draw Text
        if self.label:
            self.label.draw()


class PhotoLayoutPreview:
    """
    A container that displays a preview of a photo layout (e.g. single photo, grid).
    Contains multiple PhotoFrames.
    """
    def __init__(self, 
                 renderer, 
                 frames=[],
                 size=(300,200),
                 position=(0, 0), 
                 border_color=(255, 255, 255), 
                 border_radius=0,
                 border_width=0,
                 bg_color=(0, 0, 0, 51)):
        
        self.renderer = renderer
        self.rect = pygame.Rect(position[0], position[1], 1, 1)
        
        self.border_color = border_color
        self.bg_color = bg_color
        self.border_radius = border_radius
        self.border_width = border_width

        self.frames = frames

        # Set initial Size
        self.rect.width = size[0]
        self.rect.height = size[1]
        
        # Initialize Content
        self._init_content()

    def _init_content(self):
        # Set mocks positions relative to container
        for frame in self.frames:
            # frame.position is relative
            abs_x = self.rect.x + frame.position[0]
            abs_y = self.rect.y + frame.position[1]
            frame.set_position((abs_x, abs_y))

        self._update_texture()
    
    def _update_texture(self):
        """Creates a texture for the background if needed (rounded corners + alpha)."""
        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        has_alpha = False
        if self.bg_color and len(self.bg_color) == 4 and self.bg_color[3] < 255:
            has_alpha = True
        
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw Background
        if self.bg_color:
            pygame.draw.rect(surf, self.bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        
        # Draw Border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surf, self.border_color, (0, 0, self.rect.width, self.rect.height), width=self.border_width, border_radius=self.border_radius)

        self._bg_texture = Texture.from_surface(self.renderer, surf)

    def set_position(self, position):
        self.rect.topleft = position
        # Update children absolute positions
        self._init_content()

    def resize(self, width, height):
        self.rect.width = width
        self.rect.height = height
        
        self._update_texture()
        # Note: DOES NOT resize children automatically, assumes fixed layout relative to container

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
        
        # 2. Draw Frames
        for frame in self.frames:
            frame.draw()

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            return self.rect.collidepoint(x, y)
        elif event.type == pygame.FINGERDOWN:
             # Fingers are normalized, but for now assuming mouse logic
             # Or if using SDL2 window size...
             # Let's trust mouse emulation for fingers or add logic if needed.
             pass
        return False
