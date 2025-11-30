from .screen_interface import ScreenInterface

class ScreenManager:
    """Manages the application's current screen state."""
    def __init__(self):
        self.screens = {}
        self.current_screen = None

    def add_screen(self, name: str, screen_instance: ScreenInterface):
        """Registers a screen instance with a name."""
        self.screens[name] = screen_instance

    def set_initial_screen(self, name: str):
        """Sets the starting screen."""
        if name in self.screens:
            self.current_screen = self.screens[name]
            self.current_screen.on_enter()
        else:
            raise ValueError(f"Screen '{name}' not found.")

    def switch_to(self, screen_name: str, **context_data):
        """Switches the current screen by name, calling on_exit and on_enter."""
        if screen_name not in self.screens:
            print(f"Error: Screen '{screen_name}' not found.")
            return

        if self.current_screen:
            self.current_screen.on_exit()
        
        self.current_screen = self.screens[screen_name]
        self.current_screen.on_enter(**context_data)

    def handle_event(self, event):
        """Passes events to the current screen."""
        if self.current_screen:
            self.current_screen.handle_event(event, self.switch_to)

    def update(self, dt):
        """Updates the logic of the current screen."""
        if self.current_screen:
            self.current_screen.update(dt, self.switch_to)

    def draw(self, target_surface):
        """Draws the current screen onto the main surface."""
        if self.current_screen:
            self.current_screen.draw(target_surface)

    def exit(self):
        """Cleans up the current screen."""
        if self.current_screen:
            self.current_screen.on_exit()