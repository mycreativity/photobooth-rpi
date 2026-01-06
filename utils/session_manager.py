
from utils.logger import get_logger

logger = get_logger("SessionManager")

class SessionManager:
    """
    Manages the state of the current user session (Photoshoot).
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
           cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-init
        if hasattr(self, 'session_active'):
             return

        self.reset_session()

    def reset_session(self):
        """Clears all session data."""
        self.session_active = False
        self.layout_id = None
        self.total_photos = 0
        self.captured_polaroids = [] # List of Polaroid objects or metadata
        self.final_image_path = None
        logger.info("Session reset.")

    def start_session(self, layout_id, total_photos):
        self.reset_session()
        self.session_active = True
        self.layout_id = layout_id
        self.total_photos = total_photos
        logger.info(f"Session started: Layout={layout_id}, Expecting={total_photos}")

    def add_polaroid(self, polaroid_obj):
        """Adds a captured polaroid to the session."""
        self.captured_polaroids.append(polaroid_obj)
        logger.info(f"Photo added. Total captured: {len(self.captured_polaroids)}/{self.total_photos}")

    def is_complete(self):
        return len(self.captured_polaroids) >= self.total_photos

    def get_photo_count(self):
        return len(self.captured_polaroids)
        
    def get_current_index(self):
        """Returns 1-based index for the NEXT photo."""
        return len(self.captured_polaroids) + 1
