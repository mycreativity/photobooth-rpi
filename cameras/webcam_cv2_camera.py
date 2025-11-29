import cv2
import numpy as np
from .camera_interface import CameraInterface # Assuming they are in the same directory/package

class WebcamCV2Camera(CameraInterface):
    """Concrete implementation for standard USB or built-in webcams using OpenCV."""
    
    def __init__(self, camera_index: int = 0):
        self._index = camera_index
        self._camera = None
        self._resolution = (0, 0)
        self._aspect_ratio = 1.0

    def start(self, width: int, height: int):
        """Initializes and starts the webcam."""
        self._camera = cv2.VideoCapture(self._index)

        # Attempt to set the desired resolution
        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if self.is_opened:
            # Get the actual resolution the camera defaulted to
            w = int(self._camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self._resolution = (w, h)
            self._aspect_ratio = w / h
            print(f"WebcamCV2Camera started: {w}x{h}")
        else:
            print(f"ERROR: Failed to open WebcamCV2Camera at index {self._index}")
            self._camera = None

    def read_frame(self) -> np.ndarray | None:
        """Reads the latest frame from the camera."""
        if self.is_opened:
            ret, frame = self._camera.read()
            if ret:
                # Returns frame as NumPy array in BGR format
                return frame
        return None

    def release(self):
        """Releases the camera hardware."""
        if self._camera:
            self._camera.release()
            self._camera = None
            self._resolution = (0, 0)
            self._aspect_ratio = 1.0

    @property
    def is_opened(self) -> bool:
        """Checks if the camera is currently running."""
        return self._camera is not None and self._camera.isOpened()

    @property
    def resolution(self) -> tuple[int, int]:
        """Returns the actual frame resolution (W, H)."""
        return self._resolution

    @property
    def aspect_ratio(self) -> float:
        """Returns the aspect ratio (W/H)."""
        return self._aspect_ratio