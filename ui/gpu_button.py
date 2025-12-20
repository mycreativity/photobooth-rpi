
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

    def resize(self, display_width, display_height):
        """
        Scales the button based on the screen size ratio compared to a base resolution.
        Currently this method signature suggests direct width/height usage, but the user call
        passed `width*factor`, `height*factor`. 
        Ideally we just want to resize the internal image or rect.
        
        However, based on the user's manual call logic: "resize(self.width * self.sizing_factor...)"
        it seems they might be passing the TARGET width/height? Or scaling factors?
        Let's assume they might be passing just random args or we need a proper resize method
        that takes `width, height` to force the button to that size.
        """
        # NOTE: The user called `resize(w * factor, h * factor)`.
        # But `GPUImage.resize` takes absolute pixels.
        # But `sizing_factor` is usually ratio like 1.0 or 0.8.
        # If user passed `width * factor` (e.g. 1280 * 1.0) that is huge for a button?
        # Ah wait, in `MainScreen` resizing logic:
        # `size=300 * self.sizing_factor` for polaroid (w, h not specified?)
        # For button start: `resize(self.width * factor, ...)` -> This looks like they want to scale RELATIVE to screen?
        # WAIT. `GPUImage.resize(w, h)` resizes the image.
        
        # Let's implement a safe `resize(w, h)` that resizes the rect and internal content.
        # If w, h are floats, cast to int.
        w = int(display_width)
        h = int(display_height)
        
        # But wait, looking at user code: `self.settings_btn.resize(self.width * self.sizing_factor, self.height * self.sizing_factor)`
        # `settings_btn` is 40x40. If screen is 1280x800, that call becomes resize(1280, 800)... 
        # that will make the settings button full screen!
        
        # Correction: The user likely COPIED the params from somewhere else or misunderstood.
        # However, to be helpful, maybe the user INTENDS to scale it BY that factor?
        # But `resize` usually implies "set to this size".
        
        # Let's implement a standard `resize(width, height)` method.
        # Takes new Absolute Width and Height.
        
        # IF the user is passing "Factor", we might break it. 
        # But standard API is `resize(w, h)`.
        
        self.rect.width = w
        self.rect.height = h
        
        if self.image:
            self.image.resize(w, h)
            # Update rect from image to be sure
            if self.image.image_rect:
                self.rect = self.image.image_rect
                
        # If it's a label, strict resizing might distort text, but we can't easily font-size change strictly from W/H.
        # We will just update the hit-rect.


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
