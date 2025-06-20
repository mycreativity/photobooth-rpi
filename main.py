import pygame
pygame.init()
import config
import moderngl
from OpenGL.GL import glEnable, GL_MULTISAMPLE
from screens.preview_screen import PreviewScreen
from screens.screen_manager import ScreenManager
from screens.start_screen import StartScreen
from ui.fps_counter import FPSCounter

# 1. Init pygame with OpenGL settings
pygame.display.set_caption("Photobooth")
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

# 2. Create an OpenGL window
screen = pygame.display.set_mode((1080, 600), pygame.OPENGL | pygame.DOUBLEBUF)
# 3. Now ModernGL can hook into the OpenGL context
ctx = moderngl.create_context()
glEnable(GL_MULTISAMPLE)
print("ModernGL context created. Version:", ctx.version_code)

# Load assets
background = pygame.image.load("assets/images/background.png").convert()
background = pygame.transform.scale(background, screen.get_size())

# Screen & FPS manager
screen_manager = ScreenManager(screen, StartScreen, background)
# img = pygame.image.load("photos/photo_20250603_180140.jpg").convert()
# screen_manager = ScreenManager(screen, PreviewScreen, background, img)
fps_counter = FPSCounter(screen)

running = True
while running:
    dt = fps_counter.tick(60)
    context = {"dt": dt/1000}  # Convert milliseconds to seconds
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        screen_manager.handle_event(event)

    screen_manager.update(context)
    screen_manager.draw()
    fps_counter.draw()

    pygame.display.flip()

pygame.quit()
