from .screen_interface import ScreenInterface

class ScreenManager:
    """Manages the application's current screen state."""
    def __init__(self, start_screen: ScreenInterface):
        self.current_screen = start_screen
        self.current_screen.on_enter()

    def switch_to(self, new_screen_instance: ScreenInterface, **context_data):
        """Switches the current screen, calling on_exit and on_enter."""
        self.current_screen.on_exit() 
        self.current_screen = new_screen_instance
        self.current_screen.on_enter(**context_data)

    def handle_event(self, event):
        """Passes events to the current screen."""
        self.current_screen.handle_event(event, self.switch_to)

    def update(self, dt):
        """Updates the logic of the current screen."""
        self.current_screen.update(dt, self.switch_to)

    def draw(self, target_surface):
        """Draws the current screen onto the main surface."""
        self.current_screen.draw(target_surface)

    def exit(self):
        """Draws the current screen onto the main surface."""
        self.current_screen.on_exit() 