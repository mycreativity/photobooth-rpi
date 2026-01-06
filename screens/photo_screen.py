import os
import datetime
import pygame
from screens.screen_interface import ScreenInterface
from utils.logger import get_logger
from ui.image import Image
from ui.live_preview import LivePreview
from ui.polaroid import Polaroid
from utils.layout_composer import LayoutComposer

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
        self.flash_overlay = Image(renderer, "assets/images/white_flash.png")
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

            self.preview_image = self.camera_handler.get_latest_image()
            
            # Stop live view for capture (critical for DSLR)
            self.camera_handler.stop_continuous()
            
            # (Wait is already handled inside stop_continuous)
            
            high_res_img = self.camera_handler.take_photo()
            if high_res_img:
                if not os.path.exists("photos"):
                    os.makedirs("photos")
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photos/photo_{timestamp}.jpg"
                high_res_img.save(filename, "JPEG", quality=95)
                logger.info(f"Photo saved to {filename}")

                filename = f"photos/photo_{timestamp}_p.jpg"
                self.preview_image.save(filename, "JPEG", quality=95)
                
                # Create Polaroid (Size 500 scaled)
                self.polaroid = Polaroid(self.renderer, filename, size=int(500 * self.sizing_factor))
                
                # Center Polaroid
                p_w = self.polaroid.frame.image_rect.width
                p_h = self.polaroid.frame.image_rect.height
                self.polaroid.set_position(((self.width - p_w) // 2, (self.height - p_h) // 2))
            else:
                logger.error("Failed to capture photo!")
            
            # Resume live view for background
            self.camera_handler.start_continuous()
            
            # Reset timeline so animation starts cleanly from NOW, ignoring capture delay
            self.elapsed_time = 0.0

        # 2. Update Live Preview (background)
        self.preview_image = self.camera_handler.get_latest_image()
        self.preview.update(self.preview_image)

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
                
                # Layout logic: generic for N polaroids
                # We want them to fit in width with some padding.
                # Maximum width for row = screen_width * 0.9
                # Individual Width = scaled_w.
                # total_w = (N * scaled_w) + ((N-1) * gap)
                
                # Base scale guess
                base_scale = 0.4 
                if self.total_photos == 1:
                    base_scale = 0.6 # Larger for single photo
                
                # Calculate if it fits
                p_rect_w = self.polaroid.frame.image_rect.width
                final_w = int(p_rect_w * base_scale)
                gap = 20
                
                total_group_width = (self.total_photos * final_w) + ((self.total_photos - 1) * gap)
                max_width = self.width * 0.95
                
                if total_group_width > max_width:
                    # Scale down to fit
                    # max_width = (N * w) + (N-1)*gap
                    # max_width - (N-1)*gap = N * w
                    # w = (max_width - (N-1)*gap) / N
                    available_w = max_width - ((self.total_photos - 1) * gap)
                    final_w = int(available_w / self.total_photos)
                    # Recalculate scale
                    base_scale = final_w / p_rect_w
                    total_group_width = (self.total_photos * final_w) + ((self.total_photos - 1) * gap)

                self.polaroid_target_scale = base_scale
                final_h = int(self.polaroid.frame.image_rect.height * base_scale)
                
                start_x = (self.width - total_group_width) // 2
                
                # Calculate Target X based on current photo index (1, 2, 3...)
                target_x = start_x + (self.photo_index - 1) * (final_w + gap)
                
                # Target Y: Bottom center. Bottom aligned.
                target_y = self.height - final_h - 20
                
                self.polaroid_target_pos = (target_x, target_y)
                self.polaroid_target_rot = 0

        # Process Fall Animation
        if self.animation_phase == 'fall':
            self.anim_timer += dt
            duration = 1.0 # 1 second fall
            t = min(1.0, self.anim_timer / duration)
            
            start_x, start_y = self.polaroid_start_pos
            target_x, target_y = self.polaroid_target_pos
            
            # X Movement (Linear)
            curr_x = start_x + (target_x - start_x) * t
            
            # Y Movement (Parabolic)
            import math
            curr_y = start_y + (target_y - start_y) * (t*t) - (200 * self.sizing_factor * math.sin(t * math.pi))
            
            if self.polaroid:
                self.polaroid.set_position((curr_x, curr_y))
                
                # Rotation
                start_rot = 3.0
                curr_rot = start_rot + (self.polaroid_target_rot - start_rot) * t
                self.polaroid.set_rotation(curr_rot)
                
                # Scale
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
            
            if self.photo_index < self.total_photos:
                # Go to next photo
                callback('countdown', photo_index=self.photo_index + 1, total_photos=self.total_photos, polaroids=self.polaroids_list, mode=self.mode)
            else:
                pass
                # Finished session stays on screen
                # --> PROCESS AND GO TO RESULT
                if not self.is_processing:
                    self.is_processing = True
                    logger.info("Session complete. Composing layout...")
                    
                    # Offload to composer
                    composer = LayoutComposer()
                    final_path = composer.compose(
                        self.mode, 
                        [p.image_path for p in self.polaroids_list]
                    )
                    
                    callback('result', image_path=final_path)

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
        self.total_photos = context_data.get('total_photos', 3)
        self.total_photos = context_data.get('total_photos', 3)
        self.polaroids_list = context_data.get('polaroids', [])
        self.mode = context_data.get('mode', 'single')
        self.is_processing = False
        
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
