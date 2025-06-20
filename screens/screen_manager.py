from ui.shapes import draw_rounded_rect_aa


class ScreenManager:
    def __init__(self, screen, initial_screen_cls, background, *args, **kwargs):
        self.screen = screen
        self.background = background
        self.current_screen = initial_screen_cls(screen, background, *args, **kwargs)

    def switch_to(self, screen_class, *args, **kwargs):
        self.current_screen = screen_class(self.screen, *args, **kwargs)

    def handle_event(self, event):
        self.current_screen.handle_event(event, self.switch_to)

    def update(self, context):
        self.current_screen.update(context, self.switch_to)

    def draw(self):
        self.screen.blit(self.background, (0, 0))  # <- Always draw background first
        self.current_screen.draw()
