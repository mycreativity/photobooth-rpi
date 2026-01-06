import json
import os
from utils.logger import get_logger

logger = get_logger("LayoutManager")

class LayoutManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
           cls._instance = super(LayoutManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path="layouts.json"):
        # Prevent re-initialization if using singleton pattern implicitly
        if hasattr(self, 'layouts'):
            return
            
        self.config_path = config_path
        self.layouts = []
        self.layout_map = {}
        self.load_layouts()

    def load_layouts(self):
        """Reads layouts.json and parses configurations."""
        if not os.path.exists(self.config_path):
            logger.error(f"Layout config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.layouts = data.get("layouts", [])
                
                # Create a map for quick lookup
                self.layout_map = {l['id']: l for l in self.layouts}
                
            logger.info(f"Loaded {len(self.layouts)} layouts from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load layouts: {e}")
            self.layouts = []
            self.layout_map = {}

    def get_layouts(self):
        """Returns the list of all available layouts."""
        return self.layouts

    def get_layout(self, layout_id):
        """Returns a specific layout configuration by ID."""
        return self.layout_map.get(layout_id)
