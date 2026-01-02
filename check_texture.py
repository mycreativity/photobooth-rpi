import pygame
from pygame._sdl2 import Window, Texture
pygame.init()
window = Window()
tex = Texture(pygame._sdl2.Renderer(window), (10, 10))
print(dir(tex))
pygame.quit()
