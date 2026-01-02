import sys
import pygame
import faulthandler
from pygame._sdl2 import Window, Renderer, Texture

from screens.countdown_screen import CountdownScreen
from screens.screen_manager import ScreenManager
from screens.main_screen import MainScreen
from screens.settings_screen import SettingsScreen
from screens.photo_screen import PhotoScreen
from ui.gpu_image import GPUImage
from utils.logger import get_logger
from utils.settings_manager import SettingsManager

logger = get_logger("Main")

# Enable traceback dump on segmentation fault
faulthandler.enable()

# Configuration
APP_TITLE = "Loomo Photobooth"
FPS = 60

# Global State
camera = None
manager = None
settings_manager = None
window = None
renderer = None
screen_width = 1280
screen_height = 800
current_is_fullscreen = False

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
        except Exception as e:
            logger.error(f"Failed to initialize DSLR: {e}")
            logger.info("Falling back to Webcam.")
            from cameras.webcam_camera_handler import WebcamCameraHandler
            camera = WebcamCameraHandler(camera_index=0)
    else:
        logger.warn(f"Unknown camera type {cam_type}, defaulting to webcam.")
        from cameras.webcam_camera_handler import WebcamCameraHandler
        camera = WebcamCameraHandler(camera_index=0)

    # Start
    camera.start_continuous()
    return camera

def parse_resolution(res_str):
    if res_str.lower() == "fullscreen":
        # Get native display size
        info = pygame.display.Info()
        return info.current_w, info.current_h, True
        
    try:
        w, h = map(int, res_str.split('x'))
        return w, h, False # False = Windowed
    except:
        return 1280, 800, False

def init_screens(renderer, width, height, camera, settings_mgr, cb):
    """Initializes and registers all screens."""
    mgr = ScreenManager()
    
    main_screen = MainScreen(renderer, width, height)
    countdown_screen = CountdownScreen(renderer, width, height, camera)
    settings_screen = SettingsScreen(renderer, width, height, settings_mgr, cb)
    
    photo_screen = PhotoScreen(renderer, width, height, camera)
    
    mgr.add_screen('main', main_screen)
    mgr.add_screen('countdown', countdown_screen)
    mgr.add_screen('settings', settings_screen)
    mgr.add_screen('photo', photo_screen)
    
    mgr.set_initial_screen('main')
    return mgr

def apply_settings_callback():
    """Called when settings are saved. Re-initializes components."""
    global camera, manager, renderer, screen_width, screen_height, settings_manager, window, current_is_fullscreen
    
    logger.info("Applying new settings...")
    
    # 1. Update Camera
    camera = init_camera()
    
    # 2. Update Resolution
    new_res_str = settings_manager.get("screen_size", "1280x800")
    new_w, new_h, is_fullscreen = parse_resolution(new_res_str)
    
    res_changed = (new_w != screen_width or new_h != screen_height)
    
    if res_changed or is_fullscreen != current_is_fullscreen:
        logger.info(f"Resolution changed to {new_w}x{new_h} (Fullscreen: {is_fullscreen}). Updating window...")
        screen_width = new_w
        screen_height = new_h
        
        # Resize Window
        try:
             # Windowed -> Fullscreen
             if is_fullscreen:
                 window.set_fullscreen(True)
                 current_is_fullscreen = True
                 # After setting fullscreen, check actual size? 
                 # Usually matches native, which we tried to guess in parse_resolution
             else:
                 # Fullscreen -> Windowed
                 # Use set_windowed to ensure decorations return
                 window.set_windowed()
                 current_is_fullscreen = False
                     
                 window.size = (screen_width, screen_height)
                 window.position = (pygame.WINDOWPOS_CENTERED, pygame.WINDOWPOS_CENTERED)
                 window.focus() # Ensure focus comes back to window
                 
        except Exception as e:
             logger.error(f"Failed to resize window: {e}")
             
    # 3. Re-init Screens (Layout depends on W/H)
    logger.info("Recreating screen layouts...")
    try:
        manager = init_screens(renderer, screen_width, screen_height, camera, settings_manager, apply_settings_callback)
    except Exception as e:
        logger.error(f"Failed to re-init screens: {e}")

def main():
    global camera, manager, settings_manager, renderer, screen_width, screen_height, window, current_is_fullscreen

    # 1. Initialize Pygame
    pygame.init()

    # 4. Initialize Settings (Early load to get resolution)
    settings_manager = SettingsManager("settings.json")
    
    # Detect / Load Resolution
    res_str = settings_manager.get("screen_size", "1280x800")
    screen_width, screen_height, is_start_fullscreen = parse_resolution(res_str)
    current_is_fullscreen = is_start_fullscreen

    # 2. Setup Window and Renderer
    logger.info(f"Initializing SDL2 Window ({screen_width}x{screen_height}, Fullscreen={is_start_fullscreen})...")
    
    # Create SDL2 Window
    window = Window(APP_TITLE, (screen_width, screen_height))
    if is_start_fullscreen:
        window.set_fullscreen(True)
    else:
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


    # 5. Initialize Camera
    init_camera()

    # 6. Initialize Screens & Manager
    try:
        manager = init_screens(renderer, screen_width, screen_height, camera, settings_manager, apply_settings_callback)
        
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