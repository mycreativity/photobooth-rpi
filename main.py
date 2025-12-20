import sys
import pygame
import faulthandler
from pygame._sdl2 import Window, Renderer, Texture

from screens.countdown_screen import CountdownScreen
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen
from screens.settings_screen import SettingsScreen
from ui.gpu_image import GPUImage
from utils.logger import get_logger
from utils.settings_manager import SettingsManager

logger = get_logger("Main")

# Enable traceback dump on segmentation fault
faulthandler.enable()

# Configuration
APP_TITLE = "Loomo Photobooth"
FPS = 60

# Global State for dynamic reconfiguration
camera = None
countdown_screen = None
manager = None
settings_manager = None
renderer = None
screen_width = 0
screen_height = 0

def init_camera():
    """Initializes the camera based on settings."""
    global camera, settings_manager
    
    cam_type = settings_manager.get("camera_type", "webcam")
    logger.info(f"Initializing camera type: {cam_type}")
    
    # Teardown existing
    if camera:
        try:
            camera.shut_down()
        except:
             pass
             
    if cam_type == "webcam":
        from cameras.webcam_camera_handler import WebcamCameraHandler
        camera = WebcamCameraHandler(camera_index=0)
    elif cam_type == "dslr":
        try:
            from cameras.gphoto2_eos_camera_handler import GPhoto2EOSCameraHandler
            camera = GPhoto2EOSCameraHandler()
        except ImportError:
            logger.error("GPhoto2 handler not found or dependencies missing.")
            # Fallback
            from cameras.webcam_camera_handler import WebcamCameraHandler
            camera = WebcamCameraHandler(camera_index=0)
    else:
        logger.warn(f"Unknown camera type {cam_type}, defaulting to webcam.")
        from cameras.webcam_camera_handler import WebcamCameraHandler
        camera = WebcamCameraHandler(camera_index=0)

    # Start
    camera.start_continuous()
    return camera

def apply_settings_callback():
    """Called when settings are saved. Re-initializes components."""
    logger.info("Applying new settings...")
    new_cam = init_camera()
    
    # Update CountdownScreen with new camera
    if countdown_screen:
        countdown_screen.camera_handler = new_cam
        # Trigger any specific camera update logic if needed
        logger.info("CountdownScreen: Camera handler updated.")

def main():
    global camera, countdown_screen, manager, settings_manager, renderer, screen_width, screen_height

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
        pygame.event.pump()
        
    except Exception as e:
        logger.warn(f"Warning: Could not show loading screen: {e}")

    # 4. Initialize Settings
    settings_manager = SettingsManager("settings.json")

    # 5. Initialize Camera
    init_camera()

    # 6. Initialize Screens & Manager
    try:
        manager = ScreenManager()
        
        # Create screen instances - PASS RENDERER
        main_screen = MainScreen(renderer, screen_width, screen_height)
        # MainScreen needs to know about SettingsScreen to show the button? 
        # Actually MainScreen logic is inside MainScreen class. We just need to add the button there.
        
        countdown_screen = CountdownScreen(renderer, screen_width, screen_height, camera)
        settings_screen = SettingsScreen(renderer, screen_width, screen_height, settings_manager, apply_settings_callback)
        
        # Register screens
        manager.add_screen('main', main_screen)
        manager.add_screen('countdown', countdown_screen)
        manager.add_screen('settings', settings_screen)
        
        # Set initial screen
        manager.set_initial_screen('main')
        
    except Exception as e:
        logger.fatal(f"Error initializing screens: {e}", exc_info=True)
        sys.exit(1)

    # 7. Main Game Loop
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
        
    # 8. Cleanup
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