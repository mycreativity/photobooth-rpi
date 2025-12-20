
import pygame
from utils.image_utils import ImageUtils
from ui.gpu_image import GPUImage

class GPUPolaroid:
    """
    Combines a photo and a frame into a Polaroid-effect using GPU Textures.
    """

    def __init__(self, renderer, photo_path, size=448):
        self.renderer = renderer
        self.rotation_angle = 0.0 
        self.position = (0, 0)
        
        # 448 is the reference original photo width
        self.factor = float(size / 448) 
        
        self.frame_padding_top = int(130 * self.factor)
        self.frame_padding_sides = int(153 * self.factor)
        self.frame_padding_bottom = int(350 * self.factor)
        
        # --- PHOTO ---
        self.photo_width = int(size)
        self.photo_height = int(size)
        
        self.photo = GPUImage(renderer, photo_path)
        
        # Crop and Resize Photo Surface
        if self.photo.surface:
            self.photo.surface = ImageUtils.resize_and_crop_to_fit(
                self.photo.surface,
                new_width=self.photo_width,
                new_height=self.photo_height
            )
            self.photo.update_texture()
            
        # --- FRAME ---
        frame_path = "assets/images/polaroid-frame.png"
        frame_w_ref = self.frame_padding_sides * 2 + self.photo_width
        frame_h_ref = self.frame_padding_top + self.frame_padding_bottom + self.photo_height
        
        self.frame = GPUImage(renderer, frame_path)
        if self.frame.surface:
             self.frame.surface = pygame.transform.scale(
                self.frame.surface, (frame_w_ref, frame_h_ref)
            )
             self.frame.update_texture()
             
    def set_position(self, position):
        """Sets the top-left position of the Frame."""
        self.position = position
        
        frame_x, frame_y = position
        
        # Update Frame
        self.frame.set_position((frame_x, frame_y))
        
        # Update Photo
        photo_x = frame_x + self.frame_padding_sides
        photo_y = frame_y + self.frame_padding_top
        self.photo.set_position((photo_x, photo_y))

    def set_rotation(self, angle):
        self.rotation_angle = angle

    def draw(self):
        """Draws the rotated polaroid."""
        # 1. Determine the Center of Rotation (The Frame's center)
        if not self.frame.image_rect or not self.photo.image_rect:
            return

        # Frame Center relative to Frame Top-Left
        frame_w = self.frame.image_rect.width
        frame_h = self.frame.image_rect.height
        origin_frame = (frame_w // 2, frame_h // 2)
        
        # Frame Center relative to Photo Top-Left
        # (Center_X_Frame - Photo_X)
        frame_center_x_abs = self.frame.image_rect.x + (frame_w // 2)
        frame_center_y_abs = self.frame.image_rect.y + (frame_h // 2)
        
        photo_x = self.photo.image_rect.x
        photo_y = self.photo.image_rect.y
        
        origin_photo = (
            frame_center_x_abs - photo_x,
            frame_center_y_abs - photo_y
        )
        
        # Draw Frame
        if self.frame.texture:
            self.frame.texture.draw(
                dstrect=self.frame.image_rect,
                angle=self.rotation_angle,
                origin=origin_frame
            )
            
        # Draw Photo
        if self.photo.texture:
            self.photo.texture.draw(
                dstrect=self.photo.image_rect,
                angle=self.rotation_angle,
                origin=origin_photo
            )
            
    def cleanup(self):
        self.frame.cleanup()
        self.photo.cleanup()
