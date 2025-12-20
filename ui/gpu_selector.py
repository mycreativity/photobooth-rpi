
import pygame
from ui.gpu_button import GPUButton

class GPUSelector:
    """A simple dropdown list selector."""
    
    def __init__(self, renderer, options, selected_value, position, width=200, font=None):
        self.renderer = renderer
        self.options = options # List of strings
        self.selected_value = selected_value
        self.position = position
        self.width = width
        self.font = font
        self.expanded = False
        
        # Main Button (Current Value)
        self.main_button = GPUButton(
            renderer, 
            text=f"{self.selected_value} ▼", 
            position=position, 
            font=font, 
            color=(0, 0, 0),
            size=(width, 50)
        )
        # Override rect size manually to fit width
        self.main_button.rect.width = width
        self.main_button.rect.height = 50
        self.main_button.bg_color = (200, 200, 200, 255)
        self.main_button.set_position(position) # Re-center text

        # Option Buttons (Created but hidden)
        self.option_buttons = []
        self._create_options()

    def _create_options(self):
        self.option_buttons = []
        start_y = self.position[1] + 55
        for opt in self.options:
            btn = GPUButton(
                self.renderer,
                text=opt,
                position=(self.position[0], start_y),
                font=self.font,
                color=(0,0,0)
            )
            btn.rect.width = self.width
            btn.rect.height = 50
            btn.bg_color = (230, 230, 230, 255)
            btn.set_position((self.position[0], start_y))
            
            self.option_buttons.append((opt, btn))
            start_y += 55

    def handle_event(self, event):
        # Click on Main Button
        if self.main_button.is_clicked(event):
            self.expanded = not self.expanded
            return True # Handled

        # Click on Options
        if self.expanded:
            for opt_val, btn in self.option_buttons:
                if btn.is_clicked(event):
                    self.selected_value = opt_val
                    self.main_button.label.update_text(f"{self.selected_value} ▼")
                    self.main_button.set_position(self.position) # Recenter
                    self.expanded = False
                    return True
        return False

    def get_value(self):
        return self.selected_value

    def draw(self):
        self.main_button.draw()
        if self.expanded:
            # Draw updated layer background for menu?
            for _, btn in self.option_buttons:
                btn.draw()
