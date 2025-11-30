import threading
import time
import cv2
from PIL import Image
from .camera_interface import CameraInterface

class WebcamCameraHandler(CameraInterface, threading.Thread):
    """
    Handler for Webcam communication (Live View, photos).
    Inherits from threading.Thread for asynchronous Live View.
    """
    def __init__(self, camera_index=0):
        # Initializes the thread functionality
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.live_view_active = False
        self.latest_image = None # Stores the latest PIL Image object
        self.image_lock = threading.Lock() # Lock to safely access latest_image
        self._stop_event = threading.Event() # Event to stop the thread

        # Initialize camera (OpenCV VideoCapture)
        self.camera = None
        # We don't open the camera here immediately to allow for lazy initialization if needed,
        # but typically we want it ready. For consistency with GPhoto handler, we can init here.
        # However, OpenCV camera opening is fast, so we can do it in start_continuous or __init__.
        # Let's do it in start_continuous to be safe.

    def run(self):
        """
        The main loop for continuous Live View (if activated).
        """
        while not self._stop_event.is_set():
            if self.live_view_active and self.camera and self.camera.isOpened():
                # Read frame from OpenCV
                ret, frame = self.camera.read()
                
                if ret:
                    # Convert BGR (OpenCV) to RGB (PIL)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    
                    # Safely store the received image
                    with self.image_lock:
                        self.latest_image = image
                
                # Add a small pause to relieve CPU
                time.sleep(0.01) 
            else:
                if self.live_view_active and (not self.camera or not self.camera.isOpened()):
                     print("WebcamHandler Warning: Camera not opened yet or failed to open.")
                # Sleep as long as Live View is not active
                time.sleep(0.1) 

    # --- Public Methods for External Calls ---

    def start_continuous(self):
        """
        Activates continuous Live View mode and starts thread if not running.
        """
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(self.camera_index)
            # Optional: Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if not self.camera.isOpened():
                print(f"WebcamHandler Error: Could not open camera index {self.camera_index}")
            else:
                print(f"WebcamHandler: Camera index {self.camera_index} opened successfully.")
        
        self.live_view_active = True
        
        if not self.running:
            self.running = True
            self.start() # Start the thread

    def stop_continuous(self):
        """
        Deactivates continuous Live View mode.
        """
        self.live_view_active = False

    def get_latest_image(self):
        """
        Retrieves the latest received PIL Image object.
        """
        with self.image_lock:
            return self.latest_image

    def take_photo(self):
        """
        Takes a full photo (blocking).
        For a webcam, this is just getting the latest frame (or reading a new one).
        Returns the PIL Image.
        """
        # For webcam, we can just grab the latest frame or read a fresh one.
        # Reading a fresh one is better for "taking a photo" feel.
        if self.camera and self.camera.isOpened():
             # Flush buffer (read a few frames)
            for _ in range(5):
                self.camera.read()
            
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame_rgb)
        return None

    def shut_down(self):
        """
        Closes the thread and camera connection correctly.
        """
        self._stop_event.set()

        if self.is_alive():
            self.join(timeout=2.0) # Wait max 2 seconds
            if self.is_alive():
                print("WebcamHandler: Thread did not exit in time. Forcing shutdown.")
        
        if self.camera:
            self.camera.release()
            print("WebcamHandler: Camera released.")
