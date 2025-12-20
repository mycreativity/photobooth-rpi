
import pygame
from ui.gpu_image import GPUImage
from ui.gpu_button import GPUButton
from ui.gpu_selector import GPUSelector
from .screen_interface import ScreenInterface
from utils.logger import get_logger
from config import *

logger = get_logger("SettingsScreen")

class SettingsScreen(ScreenInterface):
    """Screen for configuring application settings."""
    
    def __init__(self, renderer, width, height, settings_manager, apply_callback):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.settings = settings_manager
        self.apply_callback = apply_callback
        
        self.font = pygame.font.SysFont("Arial", 24)
        
        # UI Elements
        self.background = GPUImage(renderer, "assets/images/background.png")
        self.background.resize(width, height)
        
        self.title = GPUButton(renderer, text="Settings", position=(50, 50), font=pygame.font.SysFont("Arial", 40), color=(0,0,0))
        self.title.bg_color = None
        
        # Camera Selector
        self.cam_label = GPUButton(renderer, text="Camera Source:", position=(100, 150), font=self.font, color=(0,0,0))
        self.cam_label.bg_color = None
        
        current_cam = self.settings.get("camera_type", "webcam")
        self.camera_selector = GPUSelector(
            renderer, 
            options=["webcam", "dslr"], 
            selected_value=current_cam, 
            position=(300, 140),
            width=200,
            font=self.font
        )
        
        # Resolution Selector
        self.res_label = GPUButton(renderer, text="Resolution:", position=(100, 220), font=self.font, color=(0,0,0))
        self.res_label.bg_color = None
        
        current_res = self.settings.get("screen_size", "1280x800")
        self.res_selector = GPUSelector(
            renderer,
            options=["1280x800", "1024x600", "fullscreen"],
            selected_value=current_res,
            position=(300, 210),
            width=200,
            font=self.font
        )
        
        # Apply Button
        self.apply_btn = GPUButton(
            renderer, text="Save & Apply", position=(100, 300), font=self.font, color=(255,255,255)
        )
        self.apply_btn.bg_color = (50, 150, 50, 255)
        self.apply_btn.rect.width = 200
        self.apply_btn.rect.height = 60
        self.apply_btn.set_position((100, 300))
        
        # Cancel/Back Button
        self.back_btn = GPUButton(
            renderer, text="Cancel", position=(350, 300), font=self.font, color=(255,255,255)
        )
        self.back_btn.bg_color = (150, 50, 50, 255)
        self.back_btn.rect.width = 150
        self.back_btn.rect.height = 60
        # Restart Button
        self.restart_btn = GPUButton(
            renderer, text="Restart App", position=(100, 380), font=self.font, color=(255,255,255)
        )
        self.restart_btn.bg_color = (200, 50, 50, 255)
        self.restart_btn.rect.width = 150
        self.restart_btn.rect.height = 60
        self.restart_btn.set_position((100, 380))

    def handle_event(self, event, switch_screen_callback):
        # Handle Selectors (Top one first if expanded logic was complex, but click detection handles it)
        # Check expansion to determine priority!
        
        # If camera selector expanded, it takes priority
        if self.camera_selector.expanded:
            if self.camera_selector.handle_event(event): return
            # Consume click if outside? Nah for now simple.
            
        if self.res_selector.expanded:
            if self.res_selector.handle_event(event): return
            
        # Normal detection
        if self.camera_selector.handle_event(event): return
        if self.res_selector.handle_event(event): return

        # Handle Buttons
        if self.back_btn.is_clicked(event):
            switch_screen_callback('main')
            
        if self.restart_btn.is_clicked(event):
             import sys
             import os
             logger.info("Restarting application...")
             pygame.quit()
             os.execv(sys.executable, [sys.executable] + sys.argv)
            
        if self.apply_btn.is_clicked(event):
            new_cam = self.camera_selector.get_value()
            new_res = self.res_selector.get_value()
            
            self.settings.set("camera_type", new_cam)
            self.settings.set("screen_size", new_res)
            self.settings.save()
            
            logger.info(f"Saving settings: Camera={new_cam}, Resolution={new_res}")
            
            # Trigger Apply Callback (re-init camera & screen)
            if self.apply_callback:
                self.apply_callback()
                
            switch_screen_callback('main')

    def update(self, dt, callback):
        pass

    def draw(self, renderer):
        renderer.draw_color = (240, 240, 240, 255)
        renderer.clear()
        
        self.background.draw()
        self.title.draw()
        
        self.cam_label.draw()
        self.camera_selector.draw()
        
        self.res_label.draw()
        self.res_selector.draw()
        
        self.apply_btn.draw()
        self.back_btn.draw()
        self.restart_btn.draw()
        
        # Z-ORDER: Draw options LAST so they appear on top
        if self.camera_selector.expanded:
            self.camera_selector.draw_options()
        if self.res_selector.expanded:
            self.res_selector.draw_options()

    def on_enter(self, **context_data):
        # Refresh values from settings in case they changed
        pass

    def on_exit(self):
        pass
