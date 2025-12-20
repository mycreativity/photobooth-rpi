import random
import pygame
import pygame.font
import math
import numpy as np

from config import *
from ui.gpu_image import GPUImage
from ui.gpu_polaroid import GPUPolaroid
from ui.gpu_text_label import GPUTextLabel
from .screen_interface import ScreenInterface
from utils.logger import get_logger

logger = get_logger("MainScreen")


class MainScreen(ScreenInterface):
    """The main photobooth screen using hardware-accelerated SDL2 Renderer."""
    
    def __init__(self, renderer, width, height):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.sizing_factor = width / 1280 
        self.aspect_ratio = width / height

        # --- INSTANCE OF BACKGROUND ---
        self.background_image = GPUImage(renderer, image_path="assets/images/background-image.png", position=(0, 0)) 
        # Resize background to fit screen
        self.background_image.resize(self.width, self.height)
        
        # --- INSTANCE OF TEXT LABEL ---
        self.fps_label = GPUTextLabel(renderer, initial_text="Starting...", font=FONT_MONO, color=(0, 0, 0))
        self.fps_label.set_position((10, 10))

        # --- INSTANCE OF POLAROIDS ---
        self.orbit_angle = 0.0          
        self.orbit_speed = 10.0         # Degrees/second
        NUM_POLAROIDS = 20
        self.polaroids = []
        self.angle_offset_step = 360.0 / NUM_POLAROIDS 
        
        self.center_x = self.width // 2
        self.center_y = self.height + 900 
        self.orbit_radius = 1400         

        for i in range(NUM_POLAROIDS):
            picture_number = i % 5
            polaroid = GPUPolaroid(renderer, photo_path=f"assets/images/party-pic-{picture_number + 1}.png", size=300)
            polaroid.angle_offset = i * self.angle_offset_step
            polaroid.rotation_offset = random.randint(-10, 10) 
            
            polaroid.set_position((0, 0))
            polaroid.set_rotation(0) 
            self.polaroids.append(polaroid)

        # --- INSTANCE OF PRESS-TO-START ---
        self.button_press_to_start = GPUImage(
            renderer,
            image_path="assets/images/button_press-to-start.png", 
            position=(0,0)
        )
        self.button_press_to_start.set_position(
            (
                int((self.width / 2) - (self.button_press_to_start.image_rect.width / 2)), 
                int((self.height - 400) * self.sizing_factor)
            )
        )

        # --- INSTANCE OF START BUTTON ---
        self.button_take_photo = GPUImage(
            renderer,
            image_path="assets/images/button_take-photo.png", 
            position=(0,0)
        )
        self.button_take_photo.set_position(
            (
                int((self.width / 2) - (self.button_take_photo.image_rect.width / 2)), 
                int((self.height - 300) * self.sizing_factor)
            )
        )
        
        # --- INSTANCE OF SETTINGS BUTTON ---
        from ui.gpu_button import GPUButton
        self.settings_btn = GPUButton(
            renderer,
            image_path="assets/images/icon-settings.png",
            position=(self.width - 60, 20),
            size=(40, 40)
        )
        self.settings_btn.bg_color = None # Transparent

    def handle_event(self, event, switch_screen_callback):
        # Handle Settings Click
        if self.settings_btn.is_clicked(event):
            logger.info("Go to Settings")
            switch_screen_callback('settings')
            return

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            logger.info("Screen touched! Starting procedure...")
            switch_screen_callback('countdown')

    def update_polaroid_position(self, dt):
        """Calculates polaroid positions on orbit."""
        
        self.orbit_angle += self.orbit_speed * dt
        self.orbit_angle %= 360 
        
        for polaroid in self.polaroids:
            current_polaroid_angle = (self.orbit_angle + polaroid.angle_offset) % 360
            
            rad = math.radians(current_polaroid_angle) 
            
            new_center_x = self.center_x + self.orbit_radius * math.cos(rad)
            new_center_y = self.center_y + self.orbit_radius * math.sin(rad)
            
            # Top-Left Position of Frame
            frame_w = polaroid.frame.image_rect.width
            frame_h = polaroid.frame.image_rect.height
            
            polaroid_top_left_x = new_center_x - (frame_w / 2)
            polaroid_top_left_y = new_center_y - (frame_h / 2)
            
            polaroid.set_position((polaroid_top_left_x, polaroid_top_left_y))
            
            # Calculate Rotation (Bottom pointing to Center)
            vector_x = self.center_x - new_center_x
            vector_y = self.center_y - new_center_y
            
            angle_rad = math.atan2(vector_y, vector_x)
            target_angle_deg = math.degrees(angle_rad)
            
            # +90 offset (or -270) to align bottom to center
            # Note: Pygame rotation is counter-clockwise. GL was also CCW?
            # We might need to invert sign if logic differs.
            # GL: glRotatef(angle, 0, 0, 1) -> CCW
            # SDL2: angle -> CW? Usually SDL2 angle is Degrees Clockwise.
            # Pygame `transform.rotate` is CCW.
            # Pygame `Texture.draw(angle=...)`?
            # SDL_RenderCopyEx takes angle in degrees clockwise.
            # So I probably need to invert the angle sign compared to GL/Math.
            
            # Math: CCW positive.
            # SDL: CW positive.
            # So: new_rotation = - (math_angle) 
            
            # Original GL: 
            # new_rotation = -target_angle_deg - 270.0
            # new_rotation += offset
            
            # If SDL is CW (opposite of math/GL), we negate.
            # new_rotation_sdl = - (-target_angle_deg - 270.0) = target_angle_deg + 270.0
            
            # We want bottom of polaroid pointing to center.
            # Let's try mirroring the logic first, and if it spins wrong way, negate.
            # But usually `math.degrees` -> CCW.
            
            new_rotation = target_angle_deg + 90 # Point top to center? No bottom.
            # Let's stick to the GL logic negated for now.
            
            gl_rotation = -target_angle_deg - 270.0 + polaroid.rotation_offset
            sdl_rotation = -gl_rotation 
            
            polaroid.set_rotation(sdl_rotation)

    def update(self, dt, callback):
        if dt > 0:
            fps = 1.0 / dt
            text = f"FPS: {fps:.2f}"
            self.fps_label.update_text(text)

        self.update_polaroid_position(dt)

    def draw(self, renderer):
        # 1. Clear Screen
        renderer.draw_color = (50, 50, 50, 255)
        renderer.clear()
        
        # 2. Draw Elements
        self.background_image.draw()

        for polaroid in self.polaroids:
            polaroid.draw()

        self.fps_label.draw()
        self.button_press_to_start.draw()
        self.button_take_photo.draw()
        self.settings_btn.draw()
        
        # 3. Present (Handled by main loop typically, but if manager calls draw, it might expect us to just draw)
        # Main loop calls pygame.display.flip() or renderer.present()? 
        # In SDL2 renderer, we must call renderer.present().
        # Main loop will handle it.

    def on_enter(self, **context_data):
        logger.info("Entering MainScreen.")

    def on_exit(self):
        logger.info("Exiting MainScreen.")
        # Cleanup if needed
        # self.background_image.cleanup() 
        # (Usually we keep textures if we return, but for memory we can clean)
        pass

        