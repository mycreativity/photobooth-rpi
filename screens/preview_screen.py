import pygame
from ui.button import CircularRetroButton
from ui.shapes import create_blurred_shadow
from ui.text import UIText
from utils.image_utils import crop_to_square

class PreviewScreen:
    def __init__(self, screen, background, photo_surface):
        self.screen = screen
        self.background = background
        self.photo = self._make_polaroid(photo_surface)

        screen_w, screen_h = screen.get_size()

        # Load icons (replace with your own if needed)
        confirm_icon = pygame.image.load("assets/images/confirm_icon.png").convert_alpha()
        retake_icon = pygame.image.load("assets/images/confirm_icon.png").convert_alpha()

        # Circular buttons
        self.confirm_button = CircularRetroButton(
            center=(screen_w // 2 + 100, 500),
            diameter=100,
            icon_surface=confirm_icon,
            base_color=(36, 160, 84),
            shadow_color=(24, 100, 52)
        )

        self.retake_button = CircularRetroButton(
            center=(screen_w // 2 - 100, 500),
            diameter=100,
            icon_surface=retake_icon,
            base_color=(200, 60, 60),
            shadow_color=(130, 30, 30)
        )

        self.instruction = UIText(
            text="Do you want to keep this photo?",
            font=pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 28),
            color=(60, 40, 30),
            pos=(screen_w // 2, 460),
            align="midtop"
        )

    def _make_polaroid(self, image):
        scale = 1.2
        w, h = int(360 * scale), int(400 * scale)
        img_size = int(320 * scale)
        img_margin = int(20 * scale)
        radius = int(18 * scale)
        blur = int(10 * scale)

        image = crop_to_square(image)
        image = pygame.transform.smoothscale(image, (img_size, img_size))

        # Create polaroid surface
        framed = pygame.Surface((w, h), pygame.SRCALPHA)
        texture = pygame.image.load("assets/images/polaroid_paper_texture.png").convert()
        texture = pygame.transform.smoothscale(texture, (w, h))
        framed.blit(texture, (0, 0))
        framed.blit(image, (img_margin, img_margin))

        shadow_surface, shadow_padding = create_blurred_shadow(
            (w, h), radius=radius, blur_radius=blur, color=(0, 0, 0, 60)
        )

        return {"image": framed.convert_alpha(), "shadow": shadow_surface, "padding": shadow_padding}

    def handle_event(self, event, switch_screen):
        if self.confirm_button.is_clicked(event):
            print("✅ Photo confirmed!")
            # TODO: Save the photo here
            switch_screen("start")  # Replace with actual screen name or class
        elif self.retake_button.is_clicked(event):
            print("🔁 Retaking photo")
            switch_screen("start")  # Replace with actual screen name or class

    def update(self, context, switch_screen):
        pass

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        img = self.photo["image"]
        shadow = self.photo["shadow"]
        pad = self.photo["padding"]
        cx, cy = self.screen.get_width() // 2, 250

        # Draw shadow
        scaled_shadow = pygame.transform.smoothscale(shadow, (img.get_width() + pad * 2, img.get_height() + pad * 2))
        shadow_rect = scaled_shadow.get_rect(center=(cx, cy))
        self.screen.blit(scaled_shadow, shadow_rect.topleft)

        # Draw photo
        photo_rect = img.get_rect(center=(cx, cy))
        self.screen.blit(img, photo_rect.topleft)

        self.instruction.draw(self.screen)
        self.confirm_button.draw(self.screen)
        self.retake_button.draw(self.screen)
