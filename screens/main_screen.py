import pygame
import pygame.font
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from config import *
from ui.gl_image import GLImage
from ui.gl_polaroid import GLPolaroid
from ui.gl_text_label import GLTextLabel
from .screen_interface import ScreenInterface


class MainScreen(ScreenInterface):
    """The main photobooth screen."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self.font_size = 40

        # --- INSTANTIE VAN BACKGROUND ---
        self.background_image = GLImage(image_path="assets/images/background.png", position=(0, 0)) 
        self.background_image.set_position((0, 0), self.width, self.height, self.aspect_ratio)
        
        # --- INSTANTIE VAN TEXT LABEL ---
        self.fps_label = GLTextLabel(initial_text="Starten...", font=FONT_DISPLAY, color=PRIMARY_COLOR) 
        self.fps_label.set_position((10, 10), self.width, self.height, self.aspect_ratio)

        # --- INSTANTIE VAN POLAROID ---
        self.polaroid = GLPolaroid(
            photo_path="assets/images/party-pic.png", 
            frame_path="assets/images/polaroid_texture.png"
        )
        self.polaroid_pos_x = (width // 2) - (self.polaroid.frame.image_rect.width // 2) # Centreer de X
        self.polaroid_pos_y = (height // 2) - (self.polaroid.frame.image_rect.height // 2) # Centreer de Y
        self.polaroid.set_position(
            (self.polaroid_pos_x, self.polaroid_pos_y), 
            self.width, 
            self.height, 
            self.aspect_ratio
        )

        # --- POLAROID ANIMATIE INSTELLINGEN ---
        self.orbit_angle = 0.0          # Start hoek in graden
        self.orbit_speed = 30.0         # Baansnelheid (Graden/seconde)

        # Rotatiecentrum (C_x, C_y) - 300 pixels onder het midden van het scherm
        self.center_x = self.width // 2
        self.center_y = self.height + 900 
        self.orbit_radius = 1500         # Straal van de baan (R)
        self.polaroid.set_rotation(angle=-5)  # Kleine draaiing voor effect

        self.setup_opengl_2d()


    def setup_opengl_2d(self):
        # Schakel 2D-texturing en alpha-blending in
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_MULTISAMPLE) 
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND) 
        

        # Stel de projectie matrix één keer in
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity() 
        # Stel 2D orthografische projectie in: (links, rechts, onder, boven)
        # De Y-as is omgekeerd t.o.v. Pygame (boven is 0)
        # Boven = 0, Onder = Schermhoogte (self.height)
        gluOrtho2D(-self.aspect_ratio, self.aspect_ratio, -1.0, 1.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POLYGON_SMOOTH)

    def handle_event(self, event, switch_screen_callback):
        # ... (onveranderd)
        pass

    def update_polaroid_position(self, dt):
        """
        Berekent de nieuwe positie op de excentrische baan en roteert de polaroid.
        dt: Delta Time in seconden.
        """
        
        # 1. Update de hoeken
        self.orbit_angle += self.orbit_speed * dt
        self.orbit_angle %= 360 
        
        # Converteer de hoek naar radialen voor math.cos/sin
        rad = math.radians(self.orbit_angle) 
        
        new_center_x = self.center_x + self.orbit_radius * math.cos(rad)
        new_center_y = self.center_y + self.orbit_radius * math.sin(rad)
        
        # 3. Vertaal het Centrum naar de Top-Left Hoek (die nodig is voor set_position)
        frame_w = self.polaroid.frame.image_rect.width
        frame_h = self.polaroid.frame.image_rect.height
        
        polaroid_top_left_x = int(new_center_x - (frame_w // 2))
        polaroid_top_left_y = int(new_center_y - (frame_h // 2))
        
        # 4. Stel de positie en interne rotatie in
        self.polaroid.set_position(
            (polaroid_top_left_x, polaroid_top_left_y), 
            self.width, 
            self.height, 
            self.aspect_ratio
        )
        
        # 5. Gebruik angle om de hoek van de polaroid te bepalen
        self.polaroid.set_rotation(angle=-self.orbit_angle-90)

    def update(self, dt, callback):
        # De logica om de tekst bij te werken blijft hier, maar roept de label-methode aan
        if dt > 0:
            fps = 1.0 / dt
            text = f"FPS: {fps:.2f}"
            self.fps_label.update_text(text)

        self.update_polaroid_position(dt)
        pass

    def draw(self, target_surface):
        # 1. Clear
        glClearColor(0.2, 0.2, 0.2, 1.0) 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)     
        
        # 2. Reset (Modelview Matrix)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # 3. Teken de label (gebruik de helper functie als argument)
        # A. Update de positie van de interne rect van de label
        # Dit is nodig omdat de helper functie de rect's afmetingen en positie nodig heeft
        self.background_image.draw()
        self.polaroid.draw()
        self.fps_label.draw()
        
        
        # 4. Swap Buffers
        pygame.display.flip()


    def on_enter(self, **context_data):
        print("Entering MainScreen.")
        if "message" in context_data:
            print(f"Status: {context_data['message']}")

    def on_exit(self):
        print("Exiting MainScreen.")
        # Ruim de label op
        self.background_image.cleanup()
        self.polaroid.cleanup()
        self.fps_label.cleanup()