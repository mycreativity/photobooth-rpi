import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
# Importeer de eerder gedefinieerde GLImage class (aangenomen dat deze beschikbaar is)
# from .gl_image import GLImage 
from ui.gl_image import GLImage
from utils.gl_utils import GLUtils
from utils.image_utils import ImageUtils # Voor pixel_to_gl conversie

# ----------------------------------------------------------------------
# Vereenvoudigde, samengestelde klasse GLPolaroid
# ----------------------------------------------------------------------

class GLPolaroid:
    """
    Combineert een foto en een transparante frame (beide GLImage objecten)
    om een Polaroid-effect te creëren.
    """

    def __init__(self, photo_path, size = 448):
        
        self.rotation_angle = 0.0 # Hoek in graden
        # Het rotatiecentrum moet het midden van de totale frame zijn
        self.center_pixel_x = 0
        self.center_pixel_y = 0

        frame_path = "assets/images/polaroid-frame.png"

        self.photo_width = int(size)
        self.photo_height = int(size)
        self.factor = float(size/448) # 448 is original photo width/height

        self.frame_padding_top = int((130) * self.factor)
        self.frame_padding_sides = int((153) * self.factor)
        self.frame_padding_bottom = int((350) * self.factor)
        
        # PHOTO
        self.photo = GLImage(photo_path, position=(0, 0))
        
        # Load and resize photo
        if self.photo.image_surface:
            self.photo.image_surface = ImageUtils.resize_and_crop_to_fit(
                self.photo.image_surface, 
                new_width=self.photo_width,
                new_height=self.photo_height
            ).convert_alpha()

            self.photo.update_texture() # Update de GPU met de nieuwe, geschaalde textuur

        
        # FRAME
        frame_width = (self.frame_padding_sides * 2 + self.photo_width)
        frame_height = (self.frame_padding_top + self.frame_padding_bottom + self.photo_height)
        
        self.frame = GLImage(frame_path, position=(0, 0))
        
        # Scale frame to fit photo
        if self.frame.image_surface:
            self.frame.image_surface = pygame.transform.scale(
                self.frame.image_surface, (frame_width, frame_height)
            ).convert_alpha()
            self.frame.update_texture()
        
        self.position = (0, 0)


    def set_position(self, position, screen_width, screen_height, aspect_ratio):
        """
        Set the position of the polaroid.
        """
        self.position = position

        # Determine frame position
        frame_x = position[0]
        frame_y = position[1]
        
        # Determine photo position to be placed exactly in the center of the frame
        photo_x = frame_x + self.frame_padding_sides
        photo_y = frame_y + self.frame_padding_top

        # Size of the frame are required to define center of polaroid
        if self.frame.image_surface:
            frame_w, frame_h = self.frame.image_surface.get_size()
            
            # Determine center of polaroid in PIXEL-coördinates
            self.center_pixel_x = frame_x + (frame_w // 2)
            self.center_pixel_y = frame_y + (frame_h // 2)

        # Update the photo and frame position
        self.photo.set_position((photo_x, photo_y), screen_width, screen_height, aspect_ratio)
        self.frame.set_position((frame_x, frame_y), screen_width, screen_height, aspect_ratio)

    def set_rotation(self, angle):
        """Set the rotation angle of the polaroid."""
        self.rotation_angle = angle

    def draw(self):
        """
        Draws frame first, then photo on top.
        Rotates the polaroid around the center of the frame.
        """
        # Rotatie wordt toegepast op de Modelview matrix, die in MainScreen al is gereset (glLoadIdentity)
        glPushMatrix() 
        
        if self.frame.image_rect:
            gl_center_x = (self.frame.gl_left + self.frame.gl_right) / 2 
            gl_center_y = (self.frame.gl_top + self.frame.gl_bottom) / 2
            
            glTranslatef(gl_center_x, gl_center_y, 0.0)
            glRotatef(self.rotation_angle, 0.0, 0.0, 1.0)
            glTranslatef(-gl_center_x, -gl_center_y, 0.0)
            
        # Draw frame first
        self.frame.draw()

        # Draw photo on top
        self.photo.draw()
        
        # Herstel de Modelview matrix (alles wat hierna getekend wordt, roteert niet mee)
        glPopMatrix()


    def cleanup(self):
        """Ruimt de OpenGL textures van beide componenten op."""
        self.photo.cleanup()
        self.frame.cleanup()