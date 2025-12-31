import pygame
from pygame._sdl2 import Window, Renderer, Texture
pygame.init()
window = Window()
renderer = Renderer(window)
tex = Texture(renderer, (10, 10))
print(f"Default blend mode: {tex.blend_mode}")
tex.blend_mode = 1
print(f"Set blend mode to 1: {tex.blend_mode}")
pygame.quit()
