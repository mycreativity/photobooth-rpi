import pygame
from config import *
from ui.button import Button
from ui.live_preview import LivePreview
from .screen_interface import ScreenInterface
from utils.logger import get_logger

logger = get_logger("MainScreen")

class MainScreen(ScreenInterface):
    """The main photobooth screen using hardware-accelerated SDL2 Renderer."""
    
    def __init__(self, renderer, width, height, camera=None):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera = camera
        self.sizing_factor = width / 1280 
        
        # --- LIVE PREVIEW ---
        self.live_preview = LivePreview(renderer, width, height)

        # --- TAKE PHOTO BUTTON ---
        btn_bg_color = (BLACK_COLOR[0], BLACK_COLOR[1], BLACK_COLOR[2], 51)
        
        self.btn_take_photo = Button(
            renderer,
            text="PRESS TO START!",
            font=FONT_DISPLAY,
            color=WHITE_COLOR,
            bg_color=btn_bg_color,
            border_color=WHITE_COLOR,
            border_radius=20,
            border_width=5, # Assuming a visible border width
            padding=20,
            text_offset=(0, 10)
        )
        
        # Center the button
        # Button with text calculates its size based on content + padding
        # We can center it now
        btn_w = self.btn_take_photo.rect.width
        btn_h = self.btn_take_photo.rect.height
        
        center_x = (self.width - btn_w) // 2
        center_y = (self.height - btn_h) // 2
        
        self.btn_take_photo.set_position((center_x, center_y))
        
        # --- SETTINGS BUTTON (Keep for navigation) ---
        # Small icon top-right
        self.settings_btn = Button(
            renderer,
            image_path="assets/images/icon-settings.png",
            position=(self.width - 60, 20),
            size=(40, 40),
            bg_color=None
        )
        # Resize based on scale
        new_size = int(40 * self.sizing_factor)
        self.settings_btn.resize(new_size, new_size)
        self.settings_btn.set_position((self.width - new_size - 20, 20))


    def handle_event(self, event, switch_screen_callback):
        # Handle Settings Click
        if self.settings_btn.is_clicked(event):
            logger.info("Go to Settings")
            switch_screen_callback('settings')
            return

        # Handle Take Photo Click
        if self.btn_take_photo.is_clicked(event):
            logger.info("START! Going to selection screen...")
            switch_screen_callback('layout_selection')

    def update(self, dt, callback):
        # Update Live Preview
        if self.camera:
            frame = self.camera.get_latest_image()
            if frame:
                self.live_preview.update(frame)

    def draw(self, renderer):
        # 1. Clear Screen
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        # 2. Draw Live Preview
        self.live_preview.draw(0, 0, self.width, self.height)

        # 3. Draw UI
        self.btn_take_photo.draw()
        self.settings_btn.draw()

    def on_enter(self, **context_data):
        logger.info("Entering MainScreen.")

    def on_exit(self):
        logger.info("Exiting MainScreen.")


        