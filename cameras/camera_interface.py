import abc
import numpy as np

class CameraInterface(abc.ABC):
    """Abstract interface for all camera implementations."""

    @abc.abstractmethod
    def start(self, width, height):
        """Initializes the camera and attempts to set resolution."""
        pass

    @abc.abstractmethod
    def read_frame(self) -> np.ndarray | None:
        """Reads a new frame from the camera, returning it as a NumPy array (BGR format)."""
        pass

    @abc.abstractmethod
    def release(self):
        """Releases the camera hardware."""
        pass

    @property
    @abc.abstractmethod
    def is_opened(self) -> bool:
        """Returns True if the camera is currently open and ready."""
        pass

    @property
    @abc.abstractmethod
    def resolution(self) -> tuple[int, int]:
        """Returns the actual resolution (width, height) of the captured frames."""
        pass

    @property
    @abc.abstractmethod
    def aspect_ratio(self) -> float:
        """Returns the aspect ratio (width / height) of the captured frames."""
        pass