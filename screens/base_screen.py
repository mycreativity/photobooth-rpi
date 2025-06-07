class BaseScreen:
    def __init__(self, screen):
        self.screen = screen

    def handle_event(self, event, switch_screen_callback):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass
