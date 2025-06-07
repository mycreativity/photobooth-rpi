import pygame
from screens.screen_manager import ScreenManager
from screens.start_screen import StartScreen
from ui.fps_counter import FPSCounter

pygame.init()
screen = pygame.display.set_mode((1080, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Photobooth")

# Load assets
background = pygame.image.load("assets/images/background.png").convert()
background = pygame.transform.scale(background, screen.get_size())

# Screen & FPS manager
screen_manager = ScreenManager(screen, StartScreen, background)
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
