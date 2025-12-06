import sys
import pygame
import faulthandler
# Import OpenGL necessary for setting up the context
from OpenGL.GL import *
from OpenGL.GLU import * 
from screens.countdown_screen import CountdownScreen
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen
from utils.logger import get_logger

logger = get_logger("Main")

# Enable traceback dump on segmentation fault
faulthandler.enable()

# Configuration
APP_TITLE = "Loomo Photobooth"
FPS = 60

def init_gl(width, height):
    """Initializes the base OpenGL context."""
    # # Set the viewport to cover the entire window
    # if (width == 1280 and height == 800):
    #     glViewport(0, 0, width, height)
    logger.info(f"Initializing OpenGL viewport to {width}x{height}...")
    # Set the Projection and Modelview modes
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Enable blending for transparency
    glEnable(GL_MULTISAMPLE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def main():
    """
    Main entry point. 
    Initializes Pygame, detects screen size, creates window.
    """
    # 1. Initialize Pygame FIRST (needed to get screen info)
    pygame.init()

    # Configuration for OpenGL buffers
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    if not pygame.font.get_init():
        pygame.font.init()

    # --- CHANGE: Detect screen size ---
    info_object = pygame.display.Info()
    screen_width = info_object.current_w
    screen_height = info_object.current_h
    
    # Optional: If you want a window that doesn't fill the entire screen,
    # you can hardcode e.g. screen_width = 1280 here as fallback.
    screen_width = 1280
    screen_height = 800

    # Set flags
    # pygame.FULLSCREEN is added so the screen is filled borderless.
    display_flags = pygame.OPENGL | pygame.DOUBLEBUF #| pygame.FULLSCREEN

    screen = pygame.display.set_mode(
        (screen_width, screen_height), 
        display_flags
    )
    pygame.display.set_caption(APP_TITLE)
    clock = pygame.time.Clock()
    
    # Initialize base OpenGL settings using the detected size
    init_gl(screen_width, screen_height)

    logger.info(f"Starting {APP_TITLE} (Detected: {screen_width}x{screen_height})...")

    # 2. Show Loading Screen (Before Camera Init)
    try:
        # Setup Ortho 2D for pixel coordinates
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, screen_width, screen_height, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClear(GL_COLOR_BUFFER_BIT)
        
        def draw_temp_texture(path, x, y, target_w=None, target_h=None):
            try:
                surf = pygame.image.load(path).convert_alpha()
                if target_w and target_h:
                    surf = pygame.transform.scale(surf, (target_w, target_h))
                
                w, h = surf.get_size()
                # Use False for vertical flip to keep top-left origin consistent with Pygame
                data = pygame.image.tostring(surf, "RGBA", False)
                
                tex_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
                
                glEnable(GL_TEXTURE_2D)
                
                # Enable Blending for transparency
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
                glColor3f(1, 1, 1)
                
                glBegin(GL_QUADS)
                # Map texture coordinates to match Pygame's Top-Left origin
                # (0,0) in texture is now Top-Left of image because we didn't flip in tostring
                glTexCoord2f(0, 0); glVertex2f(x, y)
                glTexCoord2f(1, 0); glVertex2f(x + w, y)
                glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
                glTexCoord2f(0, 1); glVertex2f(x, y + h)
                glEnd()
                
                glDisable(GL_BLEND) # Disable after drawing
                
                glDeleteTextures([tex_id])
            except Exception as e:
                logger.error(f"Loading screen error ({path}): {e}", exc_info=True)

        # Draw Background
        draw_temp_texture("assets/images/background-loading.png", 0, 0, screen_width, screen_height)
        
        # Draw Logo (Centered)
        try:
            logo_surf = pygame.image.load("assets/images/logo-loomo.png")
            lw, lh = logo_surf.get_size()
            lx = (screen_width - lw) // 2
            ly = (screen_height - lh) // 2
            draw_temp_texture("assets/images/logo-loomo.png", lx, ly)
        except:
            pass

        pygame.display.flip()
        pygame.event.pump()
        
    except Exception as e:
        logger.warn(f"Warning: Could not show loading screen: {e}")

    # 3. Initialize Camera
    # Choose your camera handler here
    # from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
    from cameras.webcam_camera_handler import WebcamCameraHandler
    
    # camera = GPhoto2EOSCameraHandler()
    camera = WebcamCameraHandler(camera_index=0)
    
    # Start camera thread
    camera.start_continuous()

    # 4. Initialize Screens & Manager
    try:
        manager = ScreenManager()
        
        # Create screen instances
        main_screen = MainScreen(screen_width, screen_height)
        countdown_screen = CountdownScreen(screen_width, screen_height, camera)
        
        # Register screens
        manager.add_screen('main', main_screen)
        manager.add_screen('countdown', countdown_screen)
        
        # Set initial screen
        manager.set_initial_screen('main')
        
    except Exception as e:
        logger.fatal(f"Error initializing screens: {e}", exc_info=True)
        sys.exit(1)

    # 5. Main Game Loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Ensure ESCAPE can close the fullscreen app
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen) 
        
    # 6. Cleanup
    logger.info("Application closing...")
    manager.exit()
    if camera:
        logger.info("Shutting down camera...")
        camera.shut_down()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()