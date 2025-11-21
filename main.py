import sys
import pygame
import faulthandler
# Import OpenGL necessary for setting up the context
from OpenGL.GL import *
from OpenGL.GLU import * 
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen

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
    print (f"Initializing OpenGL viewport to {width}x{height}...")
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
    # 1. Initialize Pygame EERST (nodig om scherminfo op te halen)
    pygame.init()

    # Configuratie voor OpenGL buffers
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    if not pygame.font.get_init():
        pygame.font.init()

    # --- AANPASSING: Schermgrootte detecteren ---
    info_object = pygame.display.Info()
    screen_width = info_object.current_w
    screen_height = info_object.current_h
    
    # Optioneel: Als je wilt dat het een window is dat niet het hele scherm vult,
    # kun je hier bijvoorbeeld screen_width = 1280 hardcoden als fallback.

    # Flags instellen
    # pygame.FULLSCREEN is toegevoegd zodat het scherm randloos gevuld wordt.
    display_flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN

    screen = pygame.display.set_mode(
        (screen_width, screen_height), 
        display_flags
    )
    pygame.display.set_caption(APP_TITLE)
    clock = pygame.time.Clock()
    
    # Initialize base OpenGL settings using the detected size
    init_gl(screen_width, screen_height)

    print(f"Starting {APP_TITLE} (Detected: {screen_width}x{screen_height})...")

    # 2. Initialize Screens
    try:
        # MainScreen krijgt nu de dynamische width/height mee
        start_screen = MainScreen(screen_width, screen_height)
        
        manager = ScreenManager(start_screen)
    except Exception as e:
        print(f"Error initializing screens: {e}")
        pygame.quit()
        sys.exit(1)

    # 3. Main Game Loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Zorg dat ESCAPE de fullscreen app kan afsluiten
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen) 
        
    # 4. Cleanup
    print("Application closing...")
    manager.exit()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()