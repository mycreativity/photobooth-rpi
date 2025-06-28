from kivy.uix.widget import Widget
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Rectangle, Color
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
import os, math

class PolaroidCarousel(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images = []
        self.angle = 0
        self.radius = 300
        self.center_pos = (540, 360)
        self.load_images()
        Clock.schedule_interval(self.update, 1/60)

    def load_images(self):
        folder = "photos"
        for filename in sorted(os.listdir(folder))[-8:]:
            if filename.endswith(".jpg"):
                path = os.path.join(folder, filename)
                self.images.append(CoreImage(path).texture)

    def update(self, dt):
        self.angle += 0.2
        self.canvas.clear()

        with self.canvas:
            for i, tex in enumerate(self.images):
                theta = self.angle + (i * (2 * math.pi / len(self.images)))
                x = self.center_pos[0] + math.cos(theta) * self.radius
                y = self.center_pos[1] + math.sin(theta) * self.radius * 0.5

                PushMatrix()
                Rotate(angle=math.degrees(theta), origin=(x, y))
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(x - 80, y - 100), size=(160, 200))
                PopMatrix()
