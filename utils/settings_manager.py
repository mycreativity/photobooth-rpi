
import json
import os
from utils.logger import get_logger

logger = get_logger("SettingsManager")

DEFAULT_SETTINGS = {
    "camera_type": "webcam", # Options: 'webcam', 'dslr'
    "camera_index": 0,
    "screen_size": "1280x800" # Options: "1280x800", "1024x600"
}

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in data.items():
                        self.settings[key] = value
                logger.info(f"Settings loaded: {self.settings}")
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        else:
            logger.info("No settings file found. Using defaults.")
            self.save()

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
