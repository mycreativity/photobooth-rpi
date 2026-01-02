
import pygame
from ui.gpu_button import GPUImageButton

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
        
        # Style Constants
        self.border_color = (180, 180, 180, 255)
        self.bg_color = (255, 255, 255, 255)
        self.text_color = (50, 50, 50)
        
        # Main Button (Current Value)
        # We start with a generic button but will customize drawing
        self.main_button = GPUImageButton(
            renderer, 
            text=f"{self.selected_value}", 
            position=position, 
            font=font, 
            color=self.text_color,
            size=(width, 40)
        )
        self.main_button.rect.width = width
        self.main_button.rect.height = 40
        self.main_button.bg_color = self.bg_color
        self.main_button.set_position(position)

        # Option Buttons (Created but hidden)
        self.option_buttons = []
        self._create_options()

    def _create_options(self):
        self.option_buttons = []
        # Draw options immediately below main button
        start_y = self.position[1] + 40 
        
        for opt in self.options:
            btn = GPUImageButton(
                self.renderer,
                text=opt,
                position=(self.position[0], start_y),
                font=self.font,
                color=self.text_color
            )
            btn.rect.width = self.width
            btn.rect.height = 40
            btn.bg_color = (255, 255, 255, 255) # White bg
            btn.set_position((self.position[0], start_y))
            
            self.option_buttons.append((opt, btn))
            start_y += 40

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
                    self.main_button.label.update_text(f"{self.selected_value}")
                    # Recenter text in button if needed, simpler to just re-set pos
                    self.main_button.set_position(self.position) 
                    self.expanded = False
                    return True
            
            # Close if clicked outside?
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Calculate full rect of expanded menu
                total_h = 40 + (len(self.option_buttons) * 40)
                full_rect = pygame.Rect(self.position[0], self.position[1], self.width, total_h)
                if not full_rect.collidepoint(x, y):
                    self.expanded = False
                    
        return False

    def get_value(self):
        return self.selected_value

    def draw(self):
        # Draw Main Button Body
        self.main_button.draw()
        
        # Draw Border
        self.renderer.draw_color = self.border_color
        self.renderer.draw_rect(self.main_button.rect)

    def draw_options(self):
        """Explicitly draw the expanded options list. Call this LAST in your render loop."""
        if self.expanded:
            # Draw a shadow or border for the whole list
            total_h = len(self.option_buttons) * 40
            list_rect = pygame.Rect(self.position[0], self.position[1] + 40, self.width, total_h)
            
            # Shadow (primitive)
            shadow_rect = list_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            self.renderer.draw_color = (0, 0, 0, 50)
            self.renderer.fill_rect(shadow_rect)

            for i, (opt_val, btn) in enumerate(self.option_buttons):
                btn.draw()
                # Draw separator line or border
                self.renderer.draw_color = (230, 230, 230, 255)
                # Bottom line
                line_y = btn.rect.bottom - 1
                self.renderer.fill_rect(pygame.Rect(btn.rect.x, line_y, btn.rect.width, 1))
            
            # Outer Border for list
            self.renderer.draw_color = self.border_color
            self.renderer.draw_rect(list_rect)
