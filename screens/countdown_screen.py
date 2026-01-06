import os
import datetime
import pygame
from pygame._sdl2 import Texture
from PIL import Image
from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
from screens.screen_interface import ScreenInterface 
from utils.logger import get_logger
from ui.text_label import TextLabel
from ui.live_preview import LivePreview
from config import FONT_DISPLAY, WHITE_COLOR

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
        
        
        # Countdown Labels
        self.countdown_images = {
            'ready': TextLabel(renderer, "GET READY!", FONT_DISPLAY, WHITE_COLOR),
            'text_3': TextLabel(renderer, "3", FONT_DISPLAY, WHITE_COLOR),
            'text_2': TextLabel(renderer, "2", FONT_DISPLAY, WHITE_COLOR),
            'text_1': TextLabel(renderer, "1", FONT_DISPLAY, WHITE_COLOR),
            'smile': TextLabel(renderer, "SMILE!", FONT_DISPLAY, WHITE_COLOR)
        }
        
        # Position all elements (Center them)
        for key, img in self.countdown_images.items():
            # For text, we don't resize images, we just center using current rect
            # If sizing factor is drastically different, we might want to scale, 
            # but FONT_DISPLAY (100px) is standard.
            
            # Center
            new_w = img.rect.width
            new_h = img.rect.height
            img.set_position(((self.width - new_w) // 2, (self.height - new_h) // 2))
            
            # Init state
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
            callback('photo', photo_index=self.photo_index, total_photos=self.total_photos, polaroids=self.polaroids_list, mode=self.mode)

    def draw(self, renderer):
        # Clear back buffer
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        # Draw Camera Preview
        if self.preview.texture:
            self.preview.draw()

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
        self.total_photos = context_data.get('total_photos', 3)
        self.polaroids_list = context_data.get('polaroids', [])
        self.mode = context_data.get('mode', 'single')
        
        # Dynamic Text Update
        if self.photo_index == 1:
            self.countdown_images['ready'].update_text("GET READY!")
        elif self.photo_index == self.total_photos:
            self.countdown_images['ready'].update_text("LAST ONE!")
        else:
            self.countdown_images['ready'].update_text(f"PHOTO {self.photo_index} OF {self.total_photos}")
            
        # Re-center 'ready' label as text length changed
        r_lbl = self.countdown_images['ready']
        r_lbl.set_position(((self.width - r_lbl.rect.width) // 2, (self.height - r_lbl.rect.height) // 2))
        
    def on_exit(self):
        logger.info("Exiting CountdownScreen.")
        pass