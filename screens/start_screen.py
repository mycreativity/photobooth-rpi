import os
import pygame
from screens.base_screen import BaseScreen
from screens.countdown_screen import CountdownScreen
from ui.button import RetroButton
from ui.card import StartCard
from ui.polaroid_carousel import PolaroidCarousel

class StartScreen(BaseScreen):
    def __init__(self, screen, background):
        super().__init__(screen)
        self.background = background

        # Set up the card positions
        card_width = screen.get_width() // 2
        card_height = 400
        card_x = (screen.get_width() - card_width) // 2
        card_y = screen.get_height() // 2 - 50

        # Create start card with button
        self.card = StartCard(card_x, card_y, card_width, card_height)

        # Load screensaver images
        paths = [os.path.join("photos", f) for f in sorted(os.listdir("photos")) if f.endswith(".jpg")]
        self.carousel = PolaroidCarousel(image_paths=paths, speed=0.1)


    def handle_event(self, event, switch_screen):
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Screen clicked — starting countdown!")
            switch_screen(CountdownScreen, self.background)

    def update(self, context, switch_screen):
        self.carousel.update(context["dt"])
        # self.card.button.is_clicked(context["event"])
        pass

    def draw(self):
        self.carousel.draw(self.screen)
        self.card.draw(self.screen)
        
