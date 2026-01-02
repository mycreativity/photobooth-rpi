import pygame
from utils.logger import get_logger

logger = get_logger("FontUtils")


class FontUtils:
    @staticmethod
    def load_font(font_path, font_size):
        # Initialiseer Pygame font module als dat nog niet is gebeurd
        if not pygame.font.get_init():
            pygame.font.init()

        try:
            font = pygame.font.Font(font_path, font_size)
        except Exception as e:
            logger.warn(f"Waarschuwing: Kan font op pad '{font_path}' niet laden. Gebruik standaard font. Fout: {e}")
            font = pygame.font.Font(None, font_size) # Fallback naar standaard
        return font