import random
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
from utils.image_utils import ImageUtils
from .screen_interface import ScreenInterface


class MainScreen(ScreenInterface):
    """The main photobooth screen."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.sizing_factor = 1280 / width
        self.aspect_ratio = width / height

        # --- INSTANTIE VAN BACKGROUND ---
        self.background_image = GLImage(image_path="assets/images/background.png", position=(0, 0)) 
        self.background_image.resize(self.width, self.height)
        self.background_image.set_position((0, 0), self.width, self.height, self.aspect_ratio)
        
        # --- INSTANTIE VAN TEXT LABEL ---
        self.fps_label = GLTextLabel(initial_text="Starten...", font=FONT_MONO, color=(0, 0, 0))
        self.fps_label.set_position((10, 10), self.width, self.height, self.aspect_ratio)

        # --- INSTANTIE VAN POLAROIDS ---
        self.orbit_angle = 0.0          # Start hoek in graden
        self.orbit_speed = 5.0         # Baansnelheid (Graden/seconde)
        NUM_POLAROIDS = 20
        self.polaroids = []
        self.angle_offset_step = 360.0 / NUM_POLAROIDS # De hoek tussen elke polaroid (360 graden / aantal)
        # Rotatiecentrum (C_x, C_y) - 300 pixels onder het midden van het scherm
        self.center_x = self.width // 2
        self.center_y = self.height + 900 
        self.orbit_radius = 1400         # Straal van de baan (R)

        for i in range(NUM_POLAROIDS):
            polaroid = GLPolaroid(
                photo_path="assets/images/party-pic.png", 
                frame_path="assets/images/polaroid_texture.png"
            )
            # Voeg een unieke eigenschap toe om de hoekoffset op te slaan
            polaroid.angle_offset = i * self.angle_offset_step
            polaroid.rotation_offset = random.randint(-10, 10) # Kleine random variatie
            
            # Stel de initiële positie in (nodig om de rect grootte te initialiseren)
            polaroid.set_position((0, 0), self.width, self.height, self.aspect_ratio)
            polaroid.set_rotation(angle=0) 
            self.polaroids.append(polaroid)

        # --- INSTANTIE VAN START BUTTON ---
        self.button = GLImage(image_path="assets/images/start_button.png", position=(0, 0)) 
        self.button.resize(int(self.button.image_rect.width / self.sizing_factor), int(self.button.image_rect.height / self.sizing_factor))
        self.button.set_position(
            (
                int((self.width / 2) - (self.button.image_rect.width / 2)), 
                int((self.height / 1.3) - (self.button.image_rect.height / 2))
            ), 
            self.width, 
            self.height, 
            self.aspect_ratio
        )

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
        
        # 1. Update de basis hoek die voor iedereen geldt
        self.orbit_angle += self.orbit_speed * dt
        self.orbit_angle %= 360 
        
        # 2. Iteratie over alle polaroids
        for polaroid in self.polaroids:
            
            # Bereken de actuele hoek voor deze specifieke polaroid
            current_polaroid_angle = (self.orbit_angle + polaroid.angle_offset) % 360
            
            # --- POSITIE BEREKENING ---
            rad = math.radians(current_polaroid_angle) 
            
            new_center_x = self.center_x + self.orbit_radius * math.cos(rad)
            new_center_y = self.center_y + self.orbit_radius * math.sin(rad)
            
            # Vertaal Centrum naar Top-Left Hoek
            frame_w = polaroid.frame.image_rect.width
            frame_h = polaroid.frame.image_rect.height
            
            polaroid_top_left_x = int(new_center_x - (frame_w // 2))
            polaroid_top_left_y = int(new_center_y - (frame_h // 2))
            
            # Stel de positie in
            polaroid.set_position(
                (polaroid_top_left_x, polaroid_top_left_y), 
                self.width, 
                self.height, 
                self.aspect_ratio
            )
            
            # --- ROTATIE BEREKENING (Bottom wijst naar Centrum) ---
            
            # De hoek van de P->C vector
            vector_x = self.center_x - new_center_x
            vector_y = self.center_y - new_center_y
            
            angle_rad = math.atan2(vector_y, vector_x)
            target_angle_deg = math.degrees(angle_rad)
            
            # +90.0 offset zorgt ervoor dat de onderkant naar het centrum wijst
            new_rotation = -target_angle_deg - 270.0

            new_rotation += polaroid.rotation_offset  # Voeg de kleine random variatie toe
            
            polaroid.set_rotation(new_rotation)
            # polaroid.set_rotation(angle=-self.orbit_angle-90)

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

        for polaroid in self.polaroids:
            polaroid.draw()

        self.fps_label.draw()
        self.button.draw()
        
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
        for polaroid in self.polaroids:
            polaroid.cleanup()
        self.fps_label.cleanup()
        