import datetime
import os
import time
import cv2
import numpy as np
import pygame
import pygame.camera
import config
from screens.base_screen import BaseScreen
from screens.preview_screen import PreviewScreen

class CountdownScreen(BaseScreen):
    def __init__(self, screen, background):
        super().__init__(screen)
        self.count = 3
        self.timer = 1.0
        self.font = config.FONT_DISPLAY
        self.background = background
        self.shutter_sound = pygame.mixer.Sound("assets/sounds/shutter.wav")

    def save_photo(self, surface):
        # Format: photo_YYYYMMDD_HHMMSS.jpg
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        path = os.path.join("photos", filename)

        pygame.image.save(surface, path)
        print(f"📸 Photo saved to {path}")
        return path


    def handle_event(self, event, switch_screen):
        pass

    def update(self, context, switch_screen):
        dt = context["dt"]
        self.timer -= dt

        if self.timer <= 0:
            self.count -= 1
            self.timer = 1.0

            if self.count < 0:
                print("Countdown finished, taking photo!")
                self.shutter_sound.play()

                # ⬇️ Take photo using OpenCV
                cap = cv2.VideoCapture(0)  # camera index 0 = default

                # ✅ Set brightness and exposure
                cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.6)     # scale: 0–1 or camera-dependent
                cap.set(cv2.CAP_PROP_EXPOSURE, -6)        # often negative (manual mode)
                cap.set(cv2.CAP_PROP_CONTRAST, 0.4)

                # Optional warm-up frames for auto-adjust to kick in
                for _ in range(5):
                    ret, _ = cap.read()

                ret, frame = cap.read()
                cap.release()

                if not ret:
                    print("Failed to capture photo!")
                    return

                # Convert OpenCV BGR to RGB and to Pygame surface
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.image.frombuffer(
                    frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB"
                ).convert()

                # Save the photo
                self.save_photo(frame_surface)

                # Switch to preview screen with the captured photo
                switch_screen(PreviewScreen, self.background, frame_surface)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if self.count >= 0:
            txt = self.font.render(str(self.count + 1), True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=self.screen.get_rect().center))
