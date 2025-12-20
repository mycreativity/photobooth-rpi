import sys
import pygame
import faulthandler
from pygame._sdl2 import Window, Renderer, Texture

from screens.countdown_screen import CountdownScreen
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen
from ui.gpu_image import GPUImage
from utils.logger import get_logger

logger = get_logger("Main")

# Enable traceback dump on segmentation fault
faulthandler.enable()

# Configuration
APP_TITLE = "Loomo Photobooth"
FPS = 60

def main():
    """
    Main entry point using SDL2 Renderer.
    """
    # 1. Initialize Pygame
    pygame.init()

    # Detect screen size
    info_object = pygame.display.Info()
    screen_width = info_object.current_w
    screen_height = info_object.current_h
    
    # Optional hardcode fallback
    screen_width = 1280
    screen_height = 800

    # 2. Setup Window and Renderer
    logger.info(f"Initializing SDL2 Window and Renderer ({screen_width}x{screen_height})...")
    
    # Create SDL2 Window
    window = Window(APP_TITLE, (screen_width, screen_height))
    # window.maximize() # If handling fullscreen
    window.focus()
    
    # Create Renderer (Hardware Accelerated)
    # vsync=True prevents tearing and caps FPS to refresh rate
    renderer = Renderer(window, vsync=True)
    
    logger.info("Renderer created. Showing loading screen...")
    
    # 3. Show Loading Screen (Renderer Version)
    try:
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        # Load Background
        bg = GPUImage(renderer, "assets/images/background-loading.png")
        bg.resize(screen_width, screen_height)
        bg.draw()
        
        renderer.present()
        
        # Pump events to show window immediately
        for _ in range(10):
            pygame.event.pump()
            pygame.time.delay(10) # Small delay to let OS process window creation

        
        # Load Logo
        try:
            logo = GPUImage(renderer, "assets/images/logo-loomo.png")
            # Center logo
            if logo.image_rect:
                lw = logo.image_rect.width
                lh = logo.image_rect.height
                lx = (screen_width - lw) // 2
                ly = (screen_height - lh) // 2
                logo.set_position((lx, ly))
                logo.draw()
        except Exception:
            pass

        renderer.present()
        
        # Pump events to show window
        pygame.event.pump()
        
    except Exception as e:
        logger.warn(f"Warning: Could not show loading screen: {e}")

    # 4. Initialize Camera
    from cameras.webcam_camera_handler import WebcamCameraHandler
    # from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
    
    camera = WebcamCameraHandler(camera_index=0)
    # camera = GPhoto2EOSCameraHandler()
    
    camera.start_continuous()

    # 5. Initialize Screens & Manager
    try:
        manager = ScreenManager()
        
        # Create screen instances - PASS RENDERER
        main_screen = MainScreen(renderer, screen_width, screen_height)
        countdown_screen = CountdownScreen(renderer, screen_width, screen_height, camera)
        
        # Register screens
        manager.add_screen('main', main_screen)
        manager.add_screen('countdown', countdown_screen)
        
        # Set initial screen
        manager.set_initial_screen('main')
        
    except Exception as e:
        logger.fatal(f"Error initializing screens: {e}", exc_info=True)
        sys.exit(1)

    # 6. Main Game Loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            manager.handle_event(event)

        manager.update(dt)
        
        # DRAW Call - Pass Renderer if needed, but screens have it stored.
        # MainScreen.draw now takes renderer as arg.
        manager.draw(renderer) 
        
        # Present the frame
        renderer.present()
        
    # 7. Cleanup
    logger.info("Application closing...")
    manager.exit()
    if camera:
        logger.info("Shutting down camera...")
        camera.shut_down()
        
    # Window/Renderer cleanup is automatic on quit
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()