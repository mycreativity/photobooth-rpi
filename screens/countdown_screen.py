import pygame
import threading # Nodig voor Threading
import time # Nodig voor de initiële sleep
import gphoto2 as gp # Nodig voor gphoto2
from PIL import Image # Nodig voor beeldverwerking
from OpenGL.GL import *
from OpenGL.GLU import *

from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
from screens.screen_interface import ScreenInterface 

import pygame
# ... (alle andere imports zijn prima) ...

class CountdownScreen():
    """Het hoofdscherm voor de photobooth met live camerafeed."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen_aspect_ratio = width / height
        
        self.camera_texture_id = glGenTextures(1)

        # 🚨 VOEG DEZE TOE: Veilige standaardwaarden voor camera-afmetingen
        self.cam_width = 0 
        self.cam_height = 0
        self.cam_aspect_ratio = 1.0
        self.setup_complete = False # Vlag om aan te geven dat de textuur is gealloceerd

        # --- INITIALISEER UV ATTRIBUTEN MET VEILIGE STANDAARDWAARDEN ---
        self.uv_left = 0.0
        self.uv_right = 1.0
        self.uv_top = 0.0
        self.uv_bottom = 1.0

        self.camera_handler = GPhoto2EOSCameraHandler()
        self.camera_handler.start_continuous()

        # Wacht NIET op het eerste frame hier. We doen dit asynchroon in update().
        # Dit voorkomt dat de app bevriest bij het opstarten.
        self.setup_complete = False 

        self.setup_opengl_2d()

    def handle_event(self, event, switch_screen_callback):
        pass
    # --- De ontbrekende of benodigde methode toevoegen ---

    def _initialize_camera_texture(self):
        """Initialisatie van de OpenGL Texture ruimte (eenmalig in __init__)."""
        if not self.setup_complete: # Voorkom dubbele init.
            glBindTexture(GL_TEXTURE_2D, self.camera_texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Allocatie van de ruimte op basis van het EERSTE ontvangen frame
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.cam_width, self.cam_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
            glBindTexture(GL_TEXTURE_2D, 0)
    
    def _calculate_crop_uvs(self):
        """Berekent de UV-coördinaten voor Crop-to-Fit."""
        # Aangenomen dat deze logica elders correct is gedefinieerd en hier wordt ingevoegd.
        if self.cam_aspect_ratio > self.screen_aspect_ratio:
            ratio_factor = self.screen_aspect_ratio / self.cam_aspect_ratio 
            uv_x_offset = (1.0 - ratio_factor) / 2.0
            self.uv_left = uv_x_offset
            self.uv_right = 1.0 - uv_x_offset
            self.uv_top = 0.0  
            self.uv_bottom = 1.0 
        else:
            ratio_factor = self.cam_aspect_ratio / self.screen_aspect_ratio
            uv_y_offset = (1.0 - ratio_factor) / 2.0
            self.uv_left = 0.0 
            self.uv_right = 1.0 
            self.uv_top = uv_y_offset 
            self.uv_bottom = 1.0 - uv_y_offset

    # --- Verbeterde `update_camera_texture` ---
    
    def update_camera_texture(self, pil_image):
        
        # --- 1. Voorbereiding van PIL Image en Formaten ---
        if pil_image.mode not in ('RGB', 'L'):
             pil_image = pil_image.convert('RGB')
             
        frame_bytes = pil_image.tobytes()
        
        if pil_image.mode == 'L':
             gl_format = GL_LUMINANCE
             gl_internal_format = GL_LUMINANCE8
        else:
             gl_format = GL_RGB 
             gl_internal_format = GL_RGB8 
        
        
        # --- 2. Dynamische Resolutie-Check (AANGEPAST) ---
        current_width, current_height = pil_image.size
        needs_reallocation = False

        if current_width != self.cam_width or current_height != self.cam_height:
            # Resolutie is veranderd, moet opnieuw alloceren
            self.cam_width = current_width
            self.cam_height = current_height
            self.cam_aspect_ratio = current_width / current_height
            self._calculate_crop_uvs() 
            needs_reallocation = True
            
        
        # --- 3. Textuur Upload ---
        
        glBindTexture(GL_TEXTURE_2D, self.camera_texture_id)
        
        # 🚨 KRITIEKE CORRECTIE: FORCEER 1-BYTE PIXEL ALIGNMENT
        # Dit is de meest voorkomende oplossing voor GLError 1282 bij glTexSubImage2D
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if needs_reallocation:
            # Allocoer nieuwe ruimte en upload data
            glTexImage2D( 
                GL_TEXTURE_2D, 
                0, gl_internal_format, 
                self.cam_width, 
                self.cam_height, 
                0, gl_format, 
                GL_UNSIGNED_BYTE, 
                frame_bytes 
            )
        else:
            # Update alleen de data in de bestaande ruimte (sneller)
            glTexSubImage2D(
                GL_TEXTURE_2D, 
                0, 0, 0,
                self.cam_width, 
                self.cam_height, 
                gl_format, 
                GL_UNSIGNED_BYTE, 
                frame_bytes 
            )

        glBindTexture(GL_TEXTURE_2D, 0)

    # --- draw en andere methoden zijn verder OK ---

    def draw(self, target_surface):
        """Tekent de full-screen gecropte camera textuur."""
        
        glClearColor(0.0, 0.0, 0.0, 1.0) 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)     
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        pil_image = self.camera_handler.get_latest_image()
        
        # 🚨 GEBRUIK self.setup_complete HIER WEER VOOR STABILITEIT
        if self.setup_complete and pil_image: # Alleen tekenen als de textuur is gealloceerd
            
            # 1. UPLOAD HET NIEUWE FRAME
            self.update_camera_texture(pil_image)

            # ... (Rest van de NDC matrix setup) ...
            
            # Bind de textuur voordat je begint met tekenen
            glBindTexture(GL_TEXTURE_2D, self.camera_texture_id) 
            
            # 🚨 FIX: Zorg dat de tekenkleur wit is, anders wordt de textuur zwart vermenigvuldigd
            glColor3f(1.0, 1.0, 1.0)
            glEnable(GL_TEXTURE_2D) # Zeker weten dat textures aan staan

            # Teken de full-screen quad met pixel-coördinaten (want gluOrtho2D is ingesteld op 0..width, height..0)
            # Let op: gluOrtho2D(0, width, height, 0) betekent:
            # 0,0 = Top-Left
            # width, height = Bottom-Right
            
            glBegin(GL_QUADS)
            # Top-Left
            glTexCoord2f(self.uv_left, self.uv_top);     glVertex2f(0, 0)
            # Top-Right
            glTexCoord2f(self.uv_right, self.uv_top);    glVertex2f(self.width, 0)
            # Bottom-Right
            glTexCoord2f(self.uv_right, self.uv_bottom); glVertex2f(self.width, self.height)
            # Bottom-Left
            glTexCoord2f(self.uv_left, self.uv_bottom);  glVertex2f(0, self.height)
            glEnd()
            
            # ... (Unbind en herstel matrices) ...
            
            # ... (Unbind en herstel matrices) ...
        else:
            # Als setup nog niet klaar is, teken een laadscherm of placeholder
            if not self.setup_complete:
                 pass # Of teken tekst "Loading..."
            elif not pil_image:
                 print("Warning: Setup complete but no image to draw.")
            
            # ... (Unbind en herstel matrices) ...
        
        pygame.display.flip()
        
    def on_exit(self):
        print("Exiting CountdownScreen.")
        self.camera_handler.shut_down()


    def setup_opengl_2d(self):
        """Initialiseert de OpenGL 2D omgeving."""
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_MULTISAMPLE) 
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND) 
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity() 
        gluOrtho2D(0, self.width, self.height, 0) 
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POLYGON_SMOOTH)

    def update(self, dt, callback):
        # Probeer de camera te initialiseren als dat nog niet gebeurd is
        if not self.setup_complete:
            initial_frame = self.camera_handler.get_latest_image()
            if initial_frame:
                print("Camera frame ontvangen! Initialiseren van OpenGL texture...")
                self.cam_width, self.cam_height = initial_frame.size
                self.cam_aspect_ratio = self.cam_width / self.cam_height
                
                self._initialize_camera_texture()
                self._calculate_crop_uvs()
                self.setup_complete = True



    def on_enter(self, **context_data):
        print("Entering CountdownScreen.")