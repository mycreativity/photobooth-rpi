from abc import ABC, abstractmethod

class ScreenInterface(ABC):
    
    @abstractmethod
    def handle_event(self, event, callback):
        """
        Handle incoming Pygame events. 
        'callback' is the screen manager's switch_to method.
        """
        pass
    
    @abstractmethod
    def update(self, dt, callback):
        """
        Update current screen logic and state (dt is delta time).
        'callback' is the screen manager's switch_to method, used for state transitions.
        """
        pass

    @abstractmethod
    def draw(self, target_surface):
        """
        Draws current state of the screen onto the provided target_surface.
        """
        pass

    @abstractmethod
    def on_enter(self, **context_data):
        """
        Called when the screen is first entered/activated. 
        'context_data' allows receiving data (e.g., a score) from the previous screen.
        """
        pass

    @abstractmethod
    def on_exit(self):
        """
        Called when the screen is exited/deactivated. 
        Used for cleanup, saving state, or stopping music.
        """
        pass