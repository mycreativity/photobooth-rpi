import os
import datetime
import pygame
from pygame._sdl2 import Texture
from PIL import Image
from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
from screens.screen_interface import ScreenInterface 
from utils.logger import get_logger
from ui.image import Image
from ui.live_preview import LivePreview

logger = get_logger("CountdownScreen")


class CountdownScreen(ScreenInterface):
    
    def __init__(self, renderer, width, height, camera):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera_handler = camera
        self.preview = LivePreview(renderer, width, height)
        self.polaroids_list = [] # From previous shots
        self.photo_index = 1
        
        # Sizing factor calculation
        self.sizing_factor = width / 1280
        
        # Load Overlay
        self.overlay = Image(renderer, "assets/images/preview-border.png")
        margin = int(10 * self.sizing_factor)
        overlay_width = self.width - (2 * margin)
        overlay_height = self.height - (2 * margin)
        self.overlay.resize(overlay_width, overlay_height)
        self.overlay.set_position((margin, margin))
        
        # Countdown Images
        # We quote 'ready' to fix the NameError.
        self.countdown_images = {
            'ready': Image(renderer, "assets/images/countdown_text_ready.png"),
            'text_3': Image(renderer, "assets/images/countdown_text_3.png"),
            'text_2': Image(renderer, "assets/images/countdown_text_2.png"),
            'text_1': Image(renderer, "assets/images/countdown_text_1.png"),
            'smile': Image(renderer, "assets/images/countdown_text_smile.png")
        }
        
        # Resize and position all elements
        for img in self.countdown_images.values():
            new_w = int(img.image_rect.width * self.sizing_factor)
            new_h = int(img.image_rect.height * self.sizing_factor)
            img.resize(new_w, new_h)
            img.set_position(((self.width - new_w) // 2, (self.height - new_h) // 2))
            img.alpha = 0
            img.scale = 1.0

        self.current_number = None
        self.elapsed_time = 0.0

    def handle_event(self, event, switch_screen_callback):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                switch_screen_callback('main')
    
    def update(self, dt, callback):
        self.elapsed_time += dt

        fade_speed = 2.0

        # Update Camera Preview
        img = self.camera_handler.get_latest_image()
        self.preview.update(img)    

        # --- ANIMATION LOGIC ---
        if self.elapsed_time < 3.0:
            self.countdown_images['ready'].alpha = 255
            self.countdown_images['ready'].scale = 1.0
            
        elif self.elapsed_time < 4.0:
            anim_progress = self.elapsed_time - 3.0 # Growing to 1 second
            self.countdown_images['ready'].alpha = int(255 * (1.0 - anim_progress * fade_speed)) if anim_progress < 1.0 else 0
            self.countdown_images['ready'].scale = 1.0 + (1 * anim_progress)
            
            self.countdown_images['text_3'].alpha = 255
            
        elif self.elapsed_time < 5.0:
            anim_progress = self.elapsed_time - 4.0 # Growing to 1 second
            self.countdown_images['text_3'].alpha = int(255 * (1.0 - anim_progress * fade_speed)) if anim_progress < 1.0 else 0
            self.countdown_images['text_3'].scale = 1.0 + (1 * anim_progress)

            self.countdown_images['text_2'].alpha = 255
            
        elif self.elapsed_time < 6.0:
            anim_progress = self.elapsed_time - 5.0 # Growing to 1 second
            self.countdown_images['text_2'].alpha = int(255 * (1.0 - anim_progress * fade_speed)) if anim_progress < 1.0 else 0
            self.countdown_images['text_2'].scale = 1.0 + (0.5 * anim_progress)
            
            self.countdown_images['text_1'].alpha = 255
            
        elif self.elapsed_time < 7.0:
            anim_progress = self.elapsed_time - 6.0 # Growing to 1 second
            self.countdown_images['text_1'].alpha = int(255 * (1.0 - anim_progress * fade_speed)) if anim_progress < 1.0 else 0
            self.countdown_images['text_1'].scale = 1.0 + (0.5 * anim_progress)
            
            self.countdown_images['smile'].alpha = 255

        elif self.elapsed_time < 8.0:
            anim_progress = self.elapsed_time - 7.0 
            self.countdown_images['smile'].alpha = int(255 * (1.0 - anim_progress * fade_speed)) if anim_progress < 1.0 else 0
            self.countdown_images['smile'].scale = 1.0 + (0.5 * anim_progress)
            
        else:
            # Animation finished, move to capturing phase
            # Pass persistence data
            callback('photo', photo_index=self.photo_index, polaroids=self.polaroids_list)

    def draw(self, renderer):
        # Clear back buffer
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        # Draw Camera Preview
        if self.preview.texture:
            self.preview.draw()

        # Overlay
        self.overlay.draw()

        # Draw images only if visible
        # Draw images only if visible
        for img in self.countdown_images.values():
            if img.alpha > 0:
                img.draw()
                
        # Draw previous polaroids (at bottom)
        for p in self.polaroids_list:
            p.draw()
        
    def on_enter(self, **context_data):
        logger.info("Entering CountdownScreen.")
        self.camera_handler.start_continuous()
        
        self.elapsed_time = 0.0
        # Reset all alphas and scales
        for img in self.countdown_images.values():
            img.alpha = 0
            img.scale = 1.0
        self.countdown_images['ready'].alpha = 255
        self.current_number = None
        
        # Context Data
        self.photo_index = context_data.get('photo_index', 1)
        self.polaroids_list = context_data.get('polaroids', [])
        
    def on_exit(self):
        logger.info("Exiting CountdownScreen.")
        pass