import pygame
# import threading # Needed for Threading
# import time # Needed for initial sleep
import gphoto2 as gp # Needed for gphoto2
from PIL import Image # Needed for image processing
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame.font # Ensure font is imported

from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
from screens.screen_interface import ScreenInterface 


class CountdownScreen():
    """The main screen for the photobooth with live camera feed."""
    
    def __init__(self, width, height, camera):
        self.width = width
        self.height = height
        self.camera_handler = camera
        self.screen_aspect_ratio = width / height
        
        self.camera_texture_id = None # glGenTextures(1) - Delayed to _initialize_camera_texture
        
        # 🚨 ADDED: Safe default values for camera dimensions
        self.cam_width = 0 
        self.cam_height = 0
        self.cam_aspect_ratio = 1.0
        self.setup_complete = False # Flag to indicate texture is allocated

        # --- INITIALIZE UV ATTRIBUTES WITH SAFE DEFAULTS ---
        self.uv_left = 0.0
        self.uv_right = 1.0
        self.uv_top = 0.0
        self.uv_bottom = 1.0

        # Do NOT wait for the first frame here. We do this asynchronously in update().
        # This prevents the app from freezing at startup.
        self.setup_complete = False 

        # self.setup_opengl_2d() # Moved to on_enter
        
        # Initialize font for loading text
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 36)

    def handle_event(self, event, switch_screen_callback):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Example: Switch back to main screen
                switch_screen_callback('main')
    # --- De ontbrekende of benodigde methode toevoegen ---

    def _initialize_camera_texture(self):
        """Initialization of OpenGL Texture space (one-time in __init__)."""
        if not self.setup_complete: # Prevent double init
            if self.camera_texture_id is None:
                 self.camera_texture_id = glGenTextures(1)
            
            glBindTexture(GL_TEXTURE_2D, self.camera_texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Allocation of space based on the FIRST received frame
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.cam_width, self.cam_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
            glBindTexture(GL_TEXTURE_2D, 0)
    
    def _calculate_crop_uvs(self):
        """Calculates UV coordinates for Crop-to-Fit."""
        # Assuming this logic is defined correctly elsewhere and inserted here.
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

    # --- Improved `update_camera_texture` ---
    
    def update_camera_texture(self, pil_image):
        
        # --- 1. Preparation of PIL Image and Formats ---
        if pil_image.mode not in ('RGB', 'L'):
             pil_image = pil_image.convert('RGB')
             
        frame_bytes = pil_image.tobytes()
        
        if pil_image.mode == 'L':
             gl_format = GL_LUMINANCE
             gl_internal_format = GL_LUMINANCE8
        else:
             gl_format = GL_RGB 
             gl_internal_format = GL_RGB8 
        
        
        # --- 2. Dynamic Resolution Check (ADJUSTED) ---
        current_width, current_height = pil_image.size
        needs_reallocation = False

        if current_width != self.cam_width or current_height != self.cam_height:
            # Resolution changed, must reallocate
            self.cam_width = current_width
            self.cam_height = current_height
            self.cam_aspect_ratio = current_width / current_height
            self._calculate_crop_uvs() 
            needs_reallocation = True
            
        
        # --- 3. Texture Upload ---
        
        glBindTexture(GL_TEXTURE_2D, self.camera_texture_id)
        
        # 🚨 CRITICAL FIX: FORCE 1-BYTE PIXEL ALIGNMENT
        # This is the most common solution for GLError 1282 at glTexSubImage2D
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if needs_reallocation:
            # Allocate new space and upload data
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
            # Update only data in existing space (faster)
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

    # --- draw and other methods are otherwise OK ---

    def draw(self, target_surface):
        """Draws the full-screen cropped camera texture."""
        
        glClearColor(0.0, 0.0, 0.0, 1.0) 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)     
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glDisable(GL_BLEND) # Disable blending for opaque camera feed
        glDisable(GL_LIGHTING) # Ensure lighting is off
        glDisable(GL_DEPTH_TEST) # Ensure depth test is off
        
        pil_image = self.camera_handler.get_latest_image()
        
        # 🚨 USE self.setup_complete HERE AGAIN FOR STABILITY
        if self.setup_complete and pil_image: # Only draw if texture is allocated
            
            # 1. UPLOAD THE NEW FRAME
            # print(f"CountdownScreen: Drawing frame {pil_image.size}")
            self.update_camera_texture(pil_image)

            # Bind the texture before starting to draw
            glBindTexture(GL_TEXTURE_2D, self.camera_texture_id) 
            
            # 🚨 FIX: Ensure draw color is white, otherwise texture is multiplied by black
            glColor3f(1.0, 1.0, 1.0)
            glEnable(GL_TEXTURE_2D) # Ensure textures are on

            # Draw full-screen quad with pixel coordinates (since gluOrtho2D is set to 0..width, height..0)
            # Note: gluOrtho2D(0, width, height, 0) means:
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
            # If setup not ready, draw loading screen or placeholder
            if not self.setup_complete or not pil_image:
                 # Draw a red placeholder box
                 glColor3f(1.0, 0.0, 0.0) # Red
                 glBegin(GL_QUADS)
                 glVertex2f(0, 0)
                 glVertex2f(self.width, 0)
                 glVertex2f(self.width, self.height)
                 glVertex2f(0, self.height)
                 glEnd()
                 
                 # Optional: Print once
                 # print("Waiting for camera frame...")
            
            # ... (Unbind en herstel matrices) ...
        
        pygame.display.flip()
        
    def on_exit(self):
        print("Exiting CountdownScreen.")
        # Do NOT shut down the camera thread here, as we want to reuse it.
        # Just stop the continuous capture (Live View) to save resources if needed.
        # However, for instant switching, we might want to keep it running.
        # For now, let's pause it.
        # self.camera_handler.stop_continuous() 
        pass


    def setup_opengl_2d(self):
        """Initializes the OpenGL 2D environment."""
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
        # Try to initialize camera if not done yet
        if not self.setup_complete:
            initial_frame = self.camera_handler.get_latest_image()
            if initial_frame:
                print("Camera frame received! Initializing OpenGL texture...")
                self.cam_width, self.cam_height = initial_frame.size
                self.cam_aspect_ratio = self.cam_width / self.cam_height
                
                self._initialize_camera_texture()
                self._calculate_crop_uvs()
                self.setup_complete = True
            else:
                # print("CountdownScreen: Waiting for initial frame...")
                pass



    def on_enter(self, **context_data):
        print("Entering CountdownScreen.")
        # Ensure camera is running
        self.camera_handler.start_continuous()
        
        # Restore the OpenGL state for this screen
        self.setup_opengl_2d()