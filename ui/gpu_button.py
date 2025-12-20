
import pygame
from ui.gpu_image import GPUImage
from ui.gpu_text_label import GPUTextLabel

class GPUButton:
    """A button that can contain an image or text and handles clicks."""
    def __init__(self, renderer, text=None, image_path=None, position=(0,0), font=None, color=(255,255,255), size=None):
        self.renderer = renderer
        self.rect = pygame.Rect(position[0], position[1], 1, 1) # Placeholder
        self.image = None
        self.label = None
        self.bg_color = None
        
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
            self.bg_color = (100, 100, 100, 255)

    def set_position(self, position):
        self.rect.topleft = position
        if self.image:
            self.image.set_position(position)
        if self.label:
            # Center label in rect
            lx = position[0] + (self.rect.width - self.label.rect.width) // 2
            ly = position[1] + (self.rect.height - self.label.rect.height) // 2
            self.label.set_position((lx, ly))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
             # Logic for mouse/touch
             if event.type == pygame.MOUSEBUTTONDOWN:
                 x, y = event.pos
             else:
                 # Minimal touch logic assumption (normalize 0-1 to screen?)
                 # For now assuming standard mouse events work for simplicity
                 # Pygame often maps touch to mouse
                 x, y = pygame.mouse.get_pos()
                 
             return self.rect.collidepoint(x, y)
        return False

    def draw(self):
        if self.bg_color:
            self.renderer.draw_color = self.bg_color
            self.renderer.fill_rect(self.rect)
            
        if self.image:
            self.image.draw()
        if self.label:
            self.label.draw()
