import sys
import pygame
import faulthandler
# Import OpenGL necessary for setting up the context
from OpenGL.GL import *
from OpenGL.GLU import * 
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen

# Enable traceback dump on segmentation fault, useful for low-level issues
faulthandler.enable()

# Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
APP_TITLE = "Application"
FPS = 60

def init_gl(width, height):
    """Initializes the base OpenGL context."""
    # Set the viewport to cover the entire window
    glViewport(0, 0, width, height)
    
    # Set the Projection and Modelview modes
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Enable blending for transparency, often needed for text/UI blitting on top
    glEnable(GL_MULTISAMPLE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    

def main():
    """
    Main entry point. 
    Initializes Pygame, creates the window, and runs the game loop
    driving the ScreenManager.
    """
    # 1. Initialize Pygame and Window
    pygame.init()

    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    if not pygame.font.get_init():
        pygame.font.init()

    # CRITICAL FIX: Add OPENGL and DOUBLEBUF flags to enable OpenGL context.
    # Running OpenGL code without these flags is the likely cause of the SegFault.
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), 
        pygame.OPENGL | pygame.DOUBLEBUF # <-- Added Flags
    )
    pygame.display.set_caption(APP_TITLE)
    clock = pygame.time.Clock()
    
    # Initialize base OpenGL settings after the screen is created
    init_gl(SCREEN_WIDTH, SCREEN_HEIGHT)

    print(f"Starting {APP_TITLE} ({SCREEN_WIDTH}x{SCREEN_HEIGHT})...")

    # 2. Initialize Screens
    try:
        # Instantiating MainScreen (requires width and height in its __init__)
        start_screen = MainScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize Manager (calls on_enter() of start_screen)
        manager = ScreenManager(start_screen)
    except Exception as e:
        print(f"Error initializing screens: {e}")
        pygame.quit()
        sys.exit(1)

    # 3. Main Game Loop
    running = True
    while running:
        # Calculate delta time (dt) in seconds
        dt = clock.tick(FPS) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            manager.handle_event(event)

        # --- Update ---
        manager.update(dt)

        # --- Draw ---
        # The screen manager calls the screen's draw method, which handles 
        # clearing the buffer, drawing OpenGL, blitting Pygame text, and calling flip.
        manager.draw(screen) 
        
    # 4. Cleanup
    print("Application closing...")
    manager.exit()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()