import pygame
from pygame._sdl2 import Texture
from PIL import Image

from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
from screens.screen_interface import ScreenInterface 
from utils.logger import get_logger

logger = get_logger("CountdownScreen")


class CountdownScreen(ScreenInterface):
    """The main screen for the photobooth with live camera feed using SDL2 Renderer."""
    
    def __init__(self, renderer, width, height, camera):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera_handler = camera
        self.screen_aspect_ratio = width / height
        
        self.camera_texture = None 
        
        # Safe default values
        self.cam_width = 0 
        self.cam_height = 0
        self.cam_aspect_ratio = 1.0
        
        # Crop Rect (Source Rect)
        self.src_rect = None

        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 36)
        
        # Load Overlay
        from ui.gpu_image import GPUImage
        self.overlay = GPUImage(renderer, "assets/images/preview-border.png")
        
        # Calculate Overlay Dimensions with 10px margin (scaled)
        # Margin is 10 pixels on all sides relative to "base" resolution?
        # User said: "Should be strectched to match the screen, but on all sides have 10 pixels margin (incorporate the scale factor here)"
        
        # Sizing factor calculation (similar to MainScreen)
        self.sizing_factor = width / 1280
        margin = int(10 * self.sizing_factor)
        
        # Target Size
        t_w = self.width - (2 * margin)
        t_h = self.height - (2 * margin)
        
        # Resize overlay once (or on resize event if we had one)
        self.overlay.resize(t_w, t_h)
        self.overlay.set_position((margin, margin))
        
        # Load Ready Text
        self.ready_text = GPUImage(renderer, "assets/images/countdown_text_ready.png")
        if self.ready_text.image_rect:
            # Resize based on scale factor
            orig_w = self.ready_text.image_rect.width
            orig_h = self.ready_text.image_rect.height
            new_w = int(orig_w * self.sizing_factor)
            new_h = int(orig_h * self.sizing_factor)
            self.ready_text.resize(new_w, new_h)
            
            # Center on screen
            cx = (self.width - new_w) // 2
            cy = (self.height - new_h) // 2
            self.ready_text.set_position((cx, cy))

    def handle_event(self, event, switch_screen_callback):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                switch_screen_callback('main')
    
    def _calculate_crop_rect(self):
        """Calculates the source rectangle for Crop-to-Fit."""
        if not self.camera_texture:
            return

        cam_w, cam_h = self.cam_width, self.cam_height
        
        if self.cam_aspect_ratio > self.screen_aspect_ratio:
            # Camera is wider than screen -> Crop sides
            # Target width based on height matches screen ratio
            target_w = int(cam_h * self.screen_aspect_ratio)
            target_h = cam_h
            
            x_offset = (cam_w - target_w) // 2
            y_offset = 0
            
            self.src_rect = pygame.Rect(x_offset, y_offset, target_w, target_h)
            
        else:
            # Camera is taller than screen -> Crop top/bottom
            target_w = cam_w
            target_h = int(cam_w / self.screen_aspect_ratio)
            
            x_offset = 0
            y_offset = (cam_h - target_h) // 2
            
            self.src_rect = pygame.Rect(x_offset, y_offset, target_w, target_h)

    def update_camera_texture(self, pil_image):
        
        if pil_image.mode != 'RGB':
             pil_image = pil_image.convert('RGB')
             
        # Check resolution
        current_width, current_height = pil_image.size
        
        # Re-create texture if size changed or not exists
        if (self.camera_texture is None or 
            current_width != self.cam_width or 
            current_height != self.cam_height):
            
            self.cam_width = current_width
            self.cam_height = current_height
            self.cam_aspect_ratio = current_width / current_height
            
            # Create Streaming Texture
            if self.camera_texture:
                del self.camera_texture
                
            try:
                # streaming=True is the correct arg for pygame-ce
                self.camera_texture = Texture(
                    self.renderer, 
                    (current_width, current_height), 
                    streaming=True
                )
            except Exception as e:
                logger.error(f"Failed to create camera texture: {e}")
                return

            self._calculate_crop_rect()

        # Update Texture using Surface (API Requirement)
        try:
            # Create a Surface from raw bytes (fast ops)
            frame_surface = pygame.image.frombytes(
                pil_image.tobytes(), 
                pil_image.size, 
                "RGB"
            )
            
            # Update texture from surface
            self.camera_texture.update(frame_surface)
            
        except Exception as e:
            logger.error(f"Failed to update camera texture: {e}")

    def draw(self, renderer):
        """Draws the full-screen cropped camera texture."""
        
        # Clear (Black)
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        pil_image = self.camera_handler.get_latest_image()
        
        if pil_image:
            self.update_camera_texture(pil_image)
            
            if self.camera_texture:
                # Draw Texture Cropped to Fill Screen
                # dstrect=None means fill the entire rendering target (the screen)
                self.camera_texture.draw(
                    srcrect=self.src_rect, 
                    dstrect=(0, 0, self.width, self.height)
                )
        else:
            # Draw placeholder (Red)
            renderer.draw_color = (255, 0, 0, 255)
            # Draw a filled rect
            renderer.fill_rect((0, 0, self.width, self.height))
            
        # Draw Overlay
        self.overlay.draw()
        
        # Draw Ready Text
        self.ready_text.draw()

    def update(self, dt, callback):
        # Logic update if needed
        pass

    def on_enter(self, **context_data):
        logger.info("Entering CountdownScreen.")
        self.camera_handler.start_continuous()
        
        # We can re-check scaling here if window resizing is dynamic during runtime, 
        # but for now init handles it assuming restart on resize usually.

    def on_exit(self):
        logger.info("Exiting CountdownScreen.")
        pass