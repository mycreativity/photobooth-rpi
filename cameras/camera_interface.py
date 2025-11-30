from abc import ABC, abstractmethod
from PIL import Image

class CameraInterface(ABC):
    """
    Abstract base class for camera implementations.
    Defines the interface for both threaded (handler) and blocking cameras.
    """

    @abstractmethod
    def start_continuous(self):
        """Starts the continuous capture thread (Live View)."""
        pass

    @abstractmethod
    def stop_continuous(self):
        """Stops the continuous capture thread."""
        pass

    @abstractmethod
    def get_latest_image(self) -> Image.Image | None:
        """
        Returns the latest available frame as a PIL Image.
        Returns None if no frame is available yet.
        """
        pass

    @abstractmethod
    def take_photo(self) -> Image.Image | None:
        """
        Takes a high-quality photo (blocking).
        Returns the photo as a PIL Image.
        """
        pass
    
    @abstractmethod
    def shut_down(self):
        """Releases all resources and stops threads."""
        pass