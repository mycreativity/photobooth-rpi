import pygame
import pygame.font
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from utils.gl_utils import GLUtils

class GLTextLabel:
    """Rendert en beheert een stuk tekst als OpenGL textuur op basis van Pygame Surface."""
    
    def __init__(self, initial_text="Default Text", font=pygame.font.Font(None, 20), color=(255, 255, 255)):
        
        self.font = font
        self.color = color
        self.position = (0,0) # set to, should be updated via set_position
        
        self.text_surface = None # Wordt ingesteld in update_text
        self.text_rect = None    # Wordt ingesteld in update_text

        # GL Pos
        self.gl_left, self.gl_right, self.gl_top, self.gl_bottom = (0, 0, 0, 0)
        
        # 2. OpenGL Textuur Setup
        self.text_texture_id = glGenTextures(1)
        
        # Initialiseer de textuur met de starttekst
        self.update_text(initial_text)

    def update_text_surface(self, text):
        """Maakt de Pygame Surface voor de tekst aan."""
        # 1. Maak de nieuwe tekst aan
        self.text_surface = self.font.render(text, True, self.color)
        
        # 2. Update de rect (positie)
        self.text_rect = self.text_surface.get_rect(topleft=self.position)
        # Andere position_types kunnen hier worden toegevoegd (bijv. topleft, bottomright)


    def update_text_texture(self):
        """Laadt de Pygame Surface naar de GPU-textuur."""
        if not self.text_surface:
            return
            
        glBindTexture(GL_TEXTURE_2D, self.text_texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        texture_data = pygame.image.tostring(self.text_surface, 'RGBA', True) # True voor flip y
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                    self.text_surface.get_width(), 
                    self.text_surface.get_height(), 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glBindTexture(GL_TEXTURE_2D, 0)
        
    
    def update_text(self, text):
        """Publieke methode om de tekst te veranderen en de textuur te updaten."""
        self.update_text_surface(text)
        self.update_text_texture()

    def set_position(self, position, screen_width, screen_height, aspect_ratio):
        """Stelt de positie van de tekst in."""
        self.position = position

        if self.text_rect:
            self.text_rect.topleft = position

            self.gl_left, self.gl_right, self.gl_top, self.gl_bottom = GLUtils.pixel_to_gl(
                self.text_rect, # Gebruik de rect van de label (met de bijgewerkte positie)
                screen_width,
                screen_height,
                aspect_ratio
            )


    def draw(self):
        """Tekent de textuur op het scherm."""
        if not self.text_rect:
            return
            
        glBindTexture(GL_TEXTURE_2D, self.text_texture_id)
        glBegin(GL_QUADS)
        
        # Textuur Coördinaten (correct gespiegeld)
        glTexCoord2f(0.0, 0.0); glVertex2f(self.gl_left, self.gl_bottom)  # Bottom-Left
        glTexCoord2f(1.0, 0.0); glVertex2f(self.gl_right, self.gl_bottom) # Bottom-Right
        glTexCoord2f(1.0, 1.0); glVertex2f(self.gl_right, self.gl_top)    # Top-Right
        glTexCoord2f(0.0, 1.0); glVertex2f(self.gl_left, self.gl_top)     # Top-Left

        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        
    def cleanup(self):
        """Ruimt de OpenGL textuur op."""
        if self.text_texture_id:
            glDeleteTextures(1, [self.text_texture_id])
            self.text_texture_id = None