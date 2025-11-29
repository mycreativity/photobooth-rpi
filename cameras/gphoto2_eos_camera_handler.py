import io
import threading
import time
import gphoto2 as gp
from PIL import Image

class GPhoto2EOSCameraHandler(threading.Thread):
    """
    Handler for gphoto2 communication (Live View, photos)
    Inherits from threading.Thread for asynchronous Live View.
    """
    def __init__(self):
        # Initializes the thread functionality
        super().__init__() 
        self.running = False
        self.live_view_active = False
        self.latest_image = None # Stores the latest PIL Image object
        self.image_lock = threading.Lock() # Lock to safely access latest_image
        self._stop_event = threading.Event() # Event to stop the thread

        # Initialize camera
        self.camera = gp.Camera()
        self.camera.init()
        self.config = self.camera.get_config()
        self.old_capturetarget = None

        self._resolution = (640, 480) 
        self._aspect_ratio = self._resolution[0] / self._resolution[1]
        
        # get the camera model
        OK, camera_model = gp.gp_widget_get_child_by_name(
            self.config, 'cameramodel')
        if OK < gp.GP_OK:
            OK, camera_model = gp.gp_widget_get_child_by_name(
                self.config, 'model')
        if OK >= gp.GP_OK:
            self.camera_model = camera_model.get_value()
            print('Camera model:', self.camera_model)
        else:
            print('No camera model info')
            self.camera_model = ''
            
        # Old logic for 350D/unknown models (not relevant for 750D, but adapted from focus-gui.py)
        if self.camera_model == 'unknown':
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                self.config, 'capturesizeclass')
            if OK >= gp.GP_OK:
                value = capture_size_class.get_choice(2)
                capture_size_class.set_value(value)
                self.camera.set_config(self.config)
        else:
            # Set camera to preview mode to flip up mirror (important for Canon)
            try:
                gp.gp_camera_capture_preview(self.camera)
            except gp.GPhoto2Error as e:
                print(f"Warning: Cannot start preview. Error: {e}")

    # The 'run' method is automatically called when thread.start() is used
    def run(self):
        """
        The main loop for continuous Live View (if activated).
        """
        while not self._stop_event.is_set():
            if self.live_view_active:
                # Call the preview function. This is blocking per frame.
                image = self._do_preview()
                
                if image:
                    # Safely store the received image
                    with self.image_lock:
                        self.latest_image = image
                
                # Add a small pause to relieve CPU
                # and give camera breathing room (can be removed if needed)
                time.sleep(0.005) 
            else:
                # Sleep as long as Live View is not active
                time.sleep(0.1) 

    # --- Public Methods for External Calls ---

    def start_continuous(self):
        """
        Activates continuous Live View mode and starts thread if not running.
        """
        if not self._set_config():
            return
        
        self.live_view_active = True
        
        if not self.running:
            self.running = True
            self.start() # Start de thread

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

    def one_shot(self):
        """
        Requests a single preview (blocking).
        Returns the PIL Image.
        """
        if self.running:
            print("Kan geen one-shot doen: continuous mode is actief.")
            return None
            
        if not self._set_config():
            return None
        
        return self._do_preview()

    def take_photo(self):
        """
        Takes a full photo (blocking).
        Returns the PIL Image.
        """
        if self.running:
            print("Kan geen foto maken: continuous mode is actief.")
            return None
        
        self._reset_config()
        return self._do_capture()

    def shut_down(self):
        """
        Closes the thread and camera connection correctly.
        """
        self._stop_event.set()

        if self.is_alive():
            self.join() # Wait for thread to finish
        
        self._reset_config()
        self.camera.exit()

    # --- Internal Helper Functions ---
    
    def _do_preview(self):
        # Requests a preview frame
        try:
            _, camera_file = gp.gp_camera_capture_preview(self.camera)
            return self._send_file(camera_file)
        except gp.GPhoto2Error as e:
             print(f'Error requesting preview: {e}')
             # Turn off Live View on error
             self.live_view_active = False
             return None
             
    def _do_capture(self):
        # Requests a full photo (slow)
        try:
            _, camera_file_path = gp.gp_camera_capture(
                self.camera, gp.GP_CAPTURE_IMAGE)
            camera_file = self.camera.file_get(
                camera_file_path.folder, camera_file_path.name,
                gp.GP_FILE_TYPE_NORMAL)
            return self._send_file(camera_file)
        except gp.GPhoto2Error as e:
            print(f'Fout bij maken van foto: {e}')
            return None

    def _send_file(self, camera_file):
        """
        Processes binary camera data and returns a PIL Image object.
        """
        file_data = camera_file.get_data_and_size()
        image = Image.open(io.BytesIO(file_data))
        # Image.load() is needed to process data in thread before releasing lock
        image.load() 
        return image

    def _set_config(self):
        # ... (configuratie logica, ongewijzigd) ...
        # [Behoud de logica van _set_config hier]
        OK, capture_target = gp.gp_widget_get_child_by_name(
            self.config, 'capturetarget')
        if OK >= gp.GP_OK:
            if self.old_capturetarget is None:
                self.old_capturetarget = capture_target.get_value()
            choice_count = capture_target.count_choices()
            for n in range(choice_count):
                choice = capture_target.get_choice(n)
                if 'internal' in choice.lower():
                    capture_target.set_value(choice)
                    self.camera.set_config(self.config)
                    break
        OK, image_format = gp.gp_widget_get_child_by_name(
            self.config, 'imageformat')
        if OK >= gp.GP_OK:
            value = image_format.get_value()
            if 'raw' in value.lower():
                print('Cannot preview RAW images')
                return False
        return True

    def _reset_config(self):
        # ... (configuratie logica, ongewijzigd) ...
        # [Behoud de logica van _reset_config hier]
        if self.old_capturetarget is not None:
            OK, capture_target = gp.gp_widget_get_child_by_name(
                self.config, 'capturetarget')
            if OK >= gp.GP_OK:
                capture_target.set_value(self.old_capturetarget)
                self.camera.set_config(self.config)
                self.old_capturetarget = None

    def is_opened(self) -> bool:
        return self.running

    @property
    def resolution(self) -> tuple[int, int]:
        return self._resolution

    @property
    def aspect_ratio(self) -> float:
        return self._aspect_ratio