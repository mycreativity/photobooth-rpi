import pygame
from utils.image_utils import ImageUtils
from ui.image import Image

class Polaroid:
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
        
        self.photo = Image(renderer, photo_path)
        
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
        
        self.frame = Image(renderer, frame_path)
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

    def set_scale(self, scale):
        self.scale = scale

    def draw(self):
        """Draws the rotated polaroid."""
        if not self.frame.image_rect or not self.photo.image_rect:
            return

        # Apply Scale
        current_scale = getattr(self, 'scale', 1.0)
        
        # Frame
        frame_w = int(self.frame.image_rect.width * current_scale)
        frame_h = int(self.frame.image_rect.height * current_scale)
        
        # Rect for drawing
        frame_dst = (
            self.frame.image_rect.x, 
            self.frame.image_rect.y, 
            frame_w, 
            frame_h
        )
        
        # Photo
        photo_w = int(self.photo.image_rect.width * current_scale)
        photo_h = int(self.photo.image_rect.height * current_scale)
        
        # We need to render the photo at the correct relative position
        # The positions set in object are Top-Left unscaled.
        # But wait, if we scale, we usually scale around center or logical origin?
        # The `set_position` sets the Top-Left of the FRAME.
        # If we just scale the W/H, the Top-Left remains, so it shrinks towards Top-Left.
        # This is acceptable for "falling", we just adjust Target X/Y.
        
        photo_dst = (
            self.photo.image_rect.x, # Photo absolute X (calculated in set_pos)
            self.photo.image_rect.y, 
            photo_w, 
            photo_h
        )
        
        # BUT: The relative offset of photo inside frame must also scale.
        # self.photo.image_rect.x is FrameX + PaddingSides.
        # If we scale, the visual padding shrinks.
        # So we must recalculate the Photo DST X/Y based on Scaled Padding.
        
        # Recalculate offsets based on scale
        scaled_sides = int(self.frame_padding_sides * current_scale)
        scaled_top = int(self.frame_padding_top * current_scale)
        
        photo_dst_x = self.frame.image_rect.x + scaled_sides
        photo_dst_y = self.frame.image_rect.y + scaled_top
        
        photo_dst = (photo_dst_x, photo_dst_y, photo_w, photo_h)

        # Origins for Rotation (Centers of the SCALED rects)
        origin_frame = (frame_w // 2, frame_h // 2)
        
        # Frame Center (SCALED) relative to Photo Top-Left (SCALED)
        frame_center_x = self.frame.image_rect.x + (frame_w // 2)
        frame_center_y = self.frame.image_rect.y + (frame_h // 2)
        
        origin_photo = (
            frame_center_x - photo_dst_x,
            frame_center_y - photo_dst_y
        )
        
        # Draw Frame
        if self.frame.texture:
            self.frame.texture.draw(
                dstrect=frame_dst,
                angle=self.rotation_angle,
                origin=origin_frame
            )
            
        # Draw Photo
        if self.photo.texture:
            self.photo.texture.draw(
                dstrect=photo_dst,
                angle=self.rotation_angle,
                origin=origin_photo
            )
            
    def cleanup(self):
        self.frame.cleanup()
        self.photo.cleanup()
