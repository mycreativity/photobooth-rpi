import pygame
from .screen_interface import ScreenInterface
from ui.button import Button
from ui.image import Image
from utils.logger import get_logger
from config import *

logger = get_logger("ResultScreen")

class ResultScreen(ScreenInterface):
    """
    Displays the final composed image and offers sharing options.
    """
    
    def __init__(self, renderer, width, height, camera, session_mgr):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.session_mgr = session_mgr
        # Camera not used here but kept for signature consistency
        
        self.bg_color = (0, 0, 0, 255)
        self.final_image = None
        self.final_image_path = None
        
        # Calculate Layout
        # Left 70% for Image, Right 30% for Options
        self.split_x = int(width * 0.70)
        
        # --- UI ELEMENTS ---
        
        # BUTTONS (Right Side)
        btn_width = 250
        btn_height = 80
        btn_x = self.split_x + (self.width - self.split_x - btn_width) // 2
        
        start_y = (self.height - (btn_height * 2 + 40)) // 2
        
        self.btn_email = Button(
            renderer,
            text="SEND TO EMAIL",
            font=FONT_DISPLAY_MEDIUM,
            color=WHITE_COLOR,
            bg_color=(50, 50, 50, 255),
            border_radius=15,
            size=(btn_width, btn_height),
            position=(btn_x, start_y)
        )
        
        self.btn_qr = Button(
            renderer,
            text="SCAN QR CODE",
            font=FONT_DISPLAY_MEDIUM,
            color=WHITE_COLOR,
            bg_color=(50, 50, 50, 255),
            border_radius=15,
            size=(btn_width, btn_height),
            position=(btn_x, start_y + btn_height + 40)
        )
        
        self.btn_home = Button(
            renderer,
            text="DONE / HOME",
            font=FONT_DISPLAY_SMALL,
            color=(200, 200, 200),
            bg_color=None,
            position=(self.width - 150, 20)
        )

    def handle_event(self, event, switch_screen_callback):
        if self.btn_email.is_clicked(event):
            logger.info("Email button clicked (Stub)")
            # TODO: Implement Email logic
            
        if self.btn_qr.is_clicked(event):
            logger.info("QR button clicked (Stub)")
            # TODO: Implement QR logic
            
        if self.btn_home.is_clicked(event):
            switch_screen_callback('main')
            
    def update(self, dt, callback):
        pass

    def draw(self, renderer):
        renderer.draw_color = self.bg_color
        renderer.clear()
        
        # Draw Final Image
        if self.final_image:
            self.final_image.draw()
            
        # Draw Buttons
        self.btn_email.draw()
        self.btn_qr.draw()
        self.btn_home.draw()

    def on_enter(self, **context_data):
        logger.info("Entering ResultScreen.")
        
        self.final_image_path = self.session_mgr.final_image_path
        
        if self.final_image_path:
            # Load and Fit Image
            self.final_image = Image(self.renderer, self.final_image_path)
            
            # Determine available space for image
            # Width: 0 to split_x
            # Height: full height
            # Add some margin
            margin = 50
            avail_w = self.split_x - (2 * margin)
            avail_h = self.height - (2 * margin)
            
            # Use ImageUtils logic or manual resizing? 
            # Image class has resize_to_fit now!
            self.final_image.resize_to_fit(avail_w, avail_h)
            
            # Center in the left area
            img_rect = self.final_image.image_rect
            
            # Center X in the Left Zone (0 to split_x)
            center_x = self.split_x // 2
            center_y = self.height // 2
            
            pos_x = center_x - (img_rect.width // 2)
            pos_y = center_y - (img_rect.height // 2)
            
            self.final_image.set_position((pos_x, pos_y))
            
        else:
            logger.error("No image path provided to ResultScreen!")

    def on_exit(self):
        logger.info("Exiting ResultScreen.")
        if self.final_image:
            self.final_image.cleanup()
            self.final_image = None
