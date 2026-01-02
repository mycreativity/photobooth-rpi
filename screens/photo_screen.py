import os
import datetime
import pygame
from screens.screen_interface import ScreenInterface
from utils.logger import get_logger
from ui.gpu_image import GPUImage
from ui.live_preview import LivePreview
from ui.gpu_polaroid import GPUPolaroid

logger = get_logger("PhotoScreen")

class PhotoScreen(ScreenInterface):
    """
    Shows a white flash, captures a high-res photo, and displays it as a polaroid 
    with a live preview in the background.
    """
    def __init__(self, renderer, width, height, camera):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera_handler = camera
        self.preview = LivePreview(renderer, width, height)
        
        self.sizing_factor = width / 1280
        
        # White Flash Overlay
        self.flash_overlay = GPUImage(renderer, "assets/images/white_flash.png")
        self.flash_overlay.resize(width, height)
        self.flash_overlay.set_position((0, 0))
        self.flash_overlay.alpha = 255
        
        self.polaroid = None
        self.polaroids_list = [] # List of previously captured polaroids
        self.photo_index = 1
        
        self.elapsed_time = 0.0
        self.is_captured = False
        
        # Animation State
        self.animation_phase = 'flash' # flash, hold, fall, done
        self.anim_timer = 0.0
        self.polaroid_target_pos = (0, 0)
        self.polaroid_start_pos = (0, 0)
        self.polaroid_target_rot = 0
        self.polaroid_target_scale = 1.0

    def handle_event(self, event, switch_screen_callback):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                switch_screen_callback('main')
        elif event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            switch_screen_callback('main')

    def update(self, dt, callback):
        self.elapsed_time += dt
        
        # 1. Capture the photo immediately on the first frame
        if not self.is_captured:
            self.is_captured = True
            logger.info("Taking high-res photo...")
            
            # Stop live view for capture (critical for DSLR)
            self.camera_handler.stop_continuous()
            
            # Wait a brief moment to ensure the preview thread has fully released the camera
            import time
            time.sleep(0.5)
            
            high_res_img = self.camera_handler.take_photo()
            if high_res_img:
                if not os.path.exists("photos"):
                    os.makedirs("photos")
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photos/photo_{timestamp}.jpg"
                high_res_img.save(filename, "JPEG", quality=95)
                logger.info(f"Photo saved to {filename}")
                
                # Create Polaroid (Size 500 scaled)
                self.polaroid = GPUPolaroid(self.renderer, filename, size=int(500 * self.sizing_factor))
                
                # Center Polaroid
                p_w = self.polaroid.frame.image_rect.width
                p_h = self.polaroid.frame.image_rect.height
                self.polaroid.set_position(((self.width - p_w) // 2, (self.height - p_h) // 2))
                # self.polaroid.set_rotation(3.0) # Slight festive tilt
            else:
                logger.error("Failed to capture photo!")
            
            # Resume live view for background
            self.camera_handler.start_continuous()
            
            # Reset timeline so animation starts cleanly from NOW, ignoring capture delay
            self.elapsed_time = 0.0

        # 2. Update Live Preview (background)
        img = self.camera_handler.get_latest_image()
        self.preview.update(img)

        # 3. Handle Flash Fade (Fade out over 1.0 second)
        # 3. Handle Flash Fade (Fade out over 0.5 second)
        fade_duration = 0.5
        if self.elapsed_time < fade_duration:
            alpha = int(255 * (1.0 - self.elapsed_time / fade_duration))
            self.flash_overlay.alpha = max(0, alpha)
        else:
            self.flash_overlay.alpha = 0
            
        # 4. Animation Logic
        # Phase 1: Hold (0.5s to 2.5s)
        if self.elapsed_time > 0.5 and self.animation_phase == 'flash':
             self.animation_phase = 'hold'
        
        # Phase 2: Fall (Starts at 2.5s)
        if self.elapsed_time > 2.5 and self.animation_phase == 'hold':
            self.animation_phase = 'fall'
            self.anim_timer = 0.0
            if self.polaroid:
                self.polaroid_start_pos = self.polaroid.position
                
                # Layout logic for 3 polaroids
                # Final Size approx 300px wide. Original is ~840 wide (at scale=1.0)
                # target_scale = 300 / 840 ~= 0.36. Let's use 0.4 for simplicity.
                self.polaroid_target_scale = 0.4
                
                # Approximate dimensions of FINAL scaled polaroid
                final_w = int(self.polaroid.frame.image_rect.width * self.polaroid_target_scale)
                final_h = int(self.polaroid.frame.image_rect.height * self.polaroid_target_scale)
                gap = 20
                
                total_group_width = (3 * final_w) + (2 * gap)
                start_x = (self.width - total_group_width) // 2
                
                # Calculate Target X based on current photo index (1, 2, 3)
                # indices are 1-based. (i-1) -> 0, 1, 2
                target_x = start_x + (self.photo_index - 1) * (final_w + gap)
                
                # Target Y: Bottom center. Bottom aligned.
                # height - margin - final_h
                target_y = self.height - 40 - final_h
                
                self.polaroid_target_pos = (target_x, target_y)
                
                # Random rotation -5 to 5
                import random
                self.polaroid_target_rot = random.uniform(-5.0, 5.0)

        # Process Fall Animation
        if self.animation_phase == 'fall':
            self.anim_timer += dt
            duration = 1.0 # 1 second fall
            t = min(1.0, self.anim_timer / duration)
            
            # Simple ease-in-out for fall? Or just ease-in.
            
            start_x, start_y = self.polaroid_start_pos
            target_x, target_y = self.polaroid_target_pos
            
            # X Movement (Linear)
            curr_x = start_x + (target_x - start_x) * t
            
            # Y Movement (Parabolic)
            # y(t) = start_y + (target_y - start_y)*t*t - (UpToss * sin)
            import math
            curr_y = start_y + (target_y - start_y) * (t*t) - (200 * self.sizing_factor * math.sin(t * math.pi))
            
            if self.polaroid:
                self.polaroid.set_position((curr_x, curr_y))
                
                # Rotation
                start_rot = 3.0
                curr_rot = start_rot + (self.polaroid_target_rot - start_rot) * t
                self.polaroid.set_rotation(curr_rot)
                
                # Scale (Linear from 1.0 to 0.4)
                start_scale = 1.0
                curr_scale = start_scale + (self.polaroid_target_scale - start_scale) * t
                self.polaroid.set_scale(curr_scale)
            
            if t >= 1.0:
                self.animation_phase = 'done'
                
        # 5. Next Step
        if self.animation_phase == 'done':
            # Add current to list
            if self.polaroid:
                self.polaroids_list.append(self.polaroid)
                self.polaroid = None # Transferred ownership
            
            if self.photo_index < 3:
                # Go to next photo
                callback('countdown', photo_index=self.photo_index + 1, polaroids=self.polaroids_list)
            else:
                # Finished session
                # Wait a bit? Or show 'done' screen. 
                # User asked: "eventually 3 polaroids... so let the first photo 'fall'..."
                # If we go to main, they disappear. Maybe stay here for 5s then main.
                # Finished session
                # Stay on screen indefinitely. User clicks to exit (handled in handle_event).
                pass

    def draw(self, renderer):
        # Background: Live Preview
        if self.preview.texture:
            self.preview.draw()
            
        # Previous Polaroids
        for p in self.polaroids_list:
            p.draw()

        # Current Polaroid
        if self.polaroid:
            self.polaroid.draw()
            
        # Flash Overlay (on top)
        if self.flash_overlay.alpha > 0:
            self.flash_overlay.draw()

    def on_enter(self, **context_data):
        logger.info("Entering PhotoScreen.")
        self.elapsed_time = 0.0
        self.is_captured = False
        self.flash_overlay.alpha = 255
        self.polaroid = None
        
        # Retrieve Context
        self.photo_index = context_data.get('photo_index', 1)
        self.polaroids_list = context_data.get('polaroids', [])
        
        self.animation_phase = 'flash'
        
    def on_exit(self):
        logger.info("Exiting PhotoScreen.")
        if self.polaroid:
            self.polaroid.cleanup()
        
        # Don't cleanup the list if we are just switching back and forth,
        # BUT if we go to Main, we should.
        # ScreenManager calls on_exit when switching.
        # If we switch to 'countdown', we pass ownership.
        # So we clear our own reference?
        self.polaroids_list = []
