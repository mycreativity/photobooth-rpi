import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from utils.gl_utils import GLUtils
from utils.logger import get_logger

logger = get_logger("GLImage")

class GLImage:
    """Rendert en beheert een afbeelding van de schijf als OpenGL textuur op basis van Pygame Surface."""
    
    def __init__(self, image_path, position=(0, 0)):
        
        self.image_path = image_path
        self.position = position 
        
        self.image_surface = None # De Pygame Surface van de afbeelding
        self.image_rect = None    # De rect voor afmetingen en positie
        
        # GL Positie
        self.gl_left, self.gl_right, self.gl_top, self.gl_bottom = (0, 0, 0, 0)
        
        # 2. OpenGL Textuur Setup
        self.texture_id = glGenTextures(1)
        
        # Laad en initialiseerd de textuur
        self.load_image(self.image_path)


    def load_image(self, path):
        """Laadt de afbeelding van de schijf en maakt de Pygame Surface aan."""
        try:
            # 1. Laad de afbeelding
            # .convert_alpha() is belangrijk voor afbeeldingen met transparantie (PNG)
            loaded_image = pygame.image.load(path).convert_alpha() 
            self.image_surface = loaded_image
            
            # 2. Update de rect (positie en afmetingen)
            self.image_rect = self.image_surface.get_rect(topleft=self.position)
            
            # 3. Laad de textuur naar de GPU
            self.update_texture()
            
            return True
            
        except pygame.error as e:
            logger.error(f"Fout bij het laden van afbeelding '{path}': {e}")
            self.image_surface = None
            self.image_rect = None
            return False

    # --- NIEUWE METHODE ---
    def resize(self, new_width, new_height):
        """
        Schaalt de afbeelding naar de opgegeven breedte en hoogte 
        en update direct de GPU textuur.
        """
        if not self.image_surface:
            return

        # Gebruik smoothscale voor betere kwaliteit, of scale voor snelheid
        self.image_surface = pygame.transform.smoothscale(
            self.image_surface, 
            (int(new_width), int(new_height))
        )

        # BELANGRIJK: De textuur op de videokaart moet nu ververst worden
        # met de nieuwe pixeldata en afmetingen.
        self.update_texture()
    # ----------------------

    def update_texture(self):
        """Laadt de Pygame Surface naar de GPU-textuur (moet na load_image())."""
        if not self.image_surface:
            return
            
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Stel parameters in
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            # Vraag de maximale ondersteunde anisotropie op
            max_anisotropy = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_anisotropy)
            
        except (NameError, OpenGL.error.GLError):
            # Extensie is niet beschikbaar, val terug op GL_LINEAR
            pass
        
        # Gebruik de Pygame surface data (RGBA met flipped Y voor OpenGL)
        texture_data = pygame.image.tostring(self.image_surface, 'RGBA', True)
        
        # Laad de textuurgegevens naar de GPU
        # Let op: we gebruiken hier dynamisch de width/height van de surface
        # dus als resize() is aangeroepen, pakt hij hier automatisch de nieuwe maten.
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                    self.image_surface.get_width(), 
                    self.image_surface.get_height(), 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        glGenerateMipmap(GL_TEXTURE_2D)
        
        # 2. Update de rect (positie en afmetingen)
        # Dit zorgt dat self.image_rect ook de nieuwe breedte/hoogte heeft
        self.image_rect = self.image_surface.get_rect(topleft=self.position)

        glBindTexture(GL_TEXTURE_2D, 0) # Unbind


    def set_position(self, position, screen_width, screen_height, aspect_ratio):
        """Stelt de positie van de afbeelding in en converteert naar GL-coördinaten."""
        self.position = position

        if self.image_rect:
            # Update de pixelpositie
            self.image_rect.topleft = position

            # Converteer naar OpenGL-coördinaten met behulp van de helper functie
            self.gl_left, self.gl_right, self.gl_top, self.gl_bottom = GLUtils.pixel_to_gl(
                self.image_rect, 
                screen_width,
                screen_height,
                aspect_ratio
            )


    def draw(self):
        """Tekent de textuur op het scherm."""
        if not self.image_rect:
            return
            
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        
        # Textuur Coördinaten (correct gespiegeld voor Pygame -> GL)
        glTexCoord2f(0.0, 0.0); glVertex2f(self.gl_left, self.gl_bottom)  # Bottom-Left
        glTexCoord2f(1.0, 0.0); glVertex2f(self.gl_right, self.gl_bottom) # Bottom-Right
        glTexCoord2f(1.0, 1.0); glVertex2f(self.gl_right, self.gl_top)    # Top-Right
        glTexCoord2f(0.0, 1.0); glVertex2f(self.gl_left, self.gl_top)     # Top-Left

        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0) # Unbind de textuur
        
        
    def cleanup(self):
        """Ruimt de OpenGL textuur op."""
        if self.texture_id:
            glDeleteTextures(1, [self.texture_id])
            self.texture_id = None