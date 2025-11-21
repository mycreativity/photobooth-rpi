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

    def __init__(self, photo_path, frame_path):
        
        self.rotation_angle = 0.0 # Hoek in graden
        # Het rotatiecentrum moet het midden van de totale frame zijn
        self.center_pixel_x = 0
        self.center_pixel_y = 0

        # Vereiste Afmetingen voor de Foto binnen de Frame (voorbeeldwaarden)
        # Deze offsets bepalen hoeveel pixels de frame om de foto heen zit.
        # Een echte polaroid frame heeft een grotere offset aan de onderkant.
        self.frame_padding_top = 29 + 18 # Shadow
        self.frame_padding_sides = 26 + 18 # Shadow
        self.frame_padding_bottom = 110 # Extra marge voor de onderkant
        
        self.photo_width = 380
        self.photo_height = 395

        # 1. Component 1: De daadwerkelijke Foto (resizen we naar de gewenste grootte)
        self.photo = GLImage(photo_path, position=(0, 0))
        
        # We laden en resizen de photo surface
        if self.photo.image_surface:
            self.photo.image_surface = ImageUtils.resize_and_crop_to_fit(
                self.photo.image_surface, 
                new_width=self.photo_width,
                new_height=self.photo_height
            ).convert_alpha()

            self.photo.update_texture() # Update de GPU met de nieuwe, geschaalde textuur

        # 2. Component 2: De Frame (moet doorzichtig zijn en over de foto heen passen)
        # De totale frame afmeting is de foto + alle padding
        frame_width = self.photo_width + 2 * self.frame_padding_sides
        frame_height = self.photo_height + self.frame_padding_top + self.frame_padding_bottom
        
        self.frame = GLImage(frame_path, position=(0, 0))
        
        # Schaal de frame zodat deze om de geschaalde foto past.
        if self.frame.image_surface:
            self.frame.image_surface = pygame.transform.scale(
                self.frame.image_surface, (frame_width, frame_height)
            ).convert_alpha()
            self.frame.update_texture()
        
        self.position = (0, 0)


    def set_position(self, position, screen_width, screen_height, aspect_ratio):
        """
        Stelt de positie in van de HELE Polaroid (dit is de positie van de FRAME).
        De positie van de foto wordt afgeleid van de frame-positie en padding.
        """
        self.position = position

        # Bepaal de startpositie van de frame (deze komt op de opgegeven positie)
        frame_x = position[0]
        frame_y = position[1]
        
        # Bepaal de startpositie van de foto (ingesprongen binnen de frame)
        photo_x = frame_x + self.frame_padding_sides
        photo_y = frame_y + self.frame_padding_top

        # --- BEREKENING VAN HET ROTATIECENTRUM (NIEUW) ---
        # De afmetingen van de frame zijn nodig om het midden te vinden
        if self.frame.image_surface:
            frame_w, frame_h = self.frame.image_surface.get_size()
            
            # Het midden van de frame in PIXEL-coördinaten
            self.center_pixel_x = frame_x + (frame_w // 2)
            self.center_pixel_y = frame_y + (frame_h // 2)

        # 2. Update de Foto en Frame positie (blijft hetzelfde)
        self.photo.set_position((photo_x, photo_y), screen_width, screen_height, aspect_ratio)
        self.frame.set_position((frame_x, frame_y), screen_width, screen_height, aspect_ratio)

    def set_rotation(self, angle):
        """Stelt de rotatiehoek in (in graden)."""
        self.rotation_angle = angle

    def draw(self):
        """
        Tekent de foto EERST, daarna de frame (zodat de frame er overheen valt).
        Past rotatie toe met matrix transformaties.
        """
        # Rotatie wordt toegepast op de Modelview matrix, die in MainScreen al is gereset (glLoadIdentity)
        glPushMatrix() 
        
        if self.frame.image_rect:
            gl_center_x = (self.frame.gl_left + self.frame.gl_right) / 2 
            gl_center_y = (self.frame.gl_top + self.frame.gl_bottom) / 2
            
            glTranslatef(gl_center_x, gl_center_y, 0.0)
            glRotatef(self.rotation_angle, 0.0, 0.0, 1.0)
            glTranslatef(-gl_center_x, -gl_center_y, 0.0)
            
        # 4a. Teken de foto
        self.photo.draw()
        
        # 4b. Teken de frame er overheen
        self.frame.draw()
        
        # Herstel de Modelview matrix (alles wat hierna getekend wordt, roteert niet mee)
        glPopMatrix()


    def cleanup(self):
        """Ruimt de OpenGL textures van beide componenten op."""
        self.photo.cleanup()
        self.frame.cleanup()