import cv2
import numpy as np
import subprocess
import os
import tempfile
import time
import re # Needed for regex to find path
from .camera_interface import CameraInterface 

class GPhoto2EOSCamera(CameraInterface):
    """
    Concrete camera implementation using the gphoto2 command-line tool for DSLR control
    (e.g., Canon EOS 750D).

    NOTE: This class is much slower (1-2 FPS) than a webcam because it
    executes an external command and reads a file for every frame.
    
    *** IMPORTANT: The command-line tool 'gphoto2' (NOT the Python wrapper)
    must be installed on the system! ***
    """
    
    def __init__(self):
        self._is_ready = False
        # Gphoto2 preview resolution is often fixed and relatively low
        self._resolution = (640, 480) 
        self._aspect_ratio = self._resolution[0] / self._resolution[1]
        # Temporary path for downloaded movie (MJPEG)
        # No longer used in read_frame, but kept as fallback
        self._temp_file_path = os.path.join(tempfile.gettempdir(), f'gphoto_movie_{os.getpid()}_{time.time()}.mjpg')
        
    def start(self, width: int, height: int):
        """Checks if camera is connected, gphoto2 works, and configures camera."""
        print("Starting GPhoto2 camera connection...")
        try:
            # 1. Detect camera
            result = subprocess.run(
                ['gphoto2', '--auto-detect'],
                capture_output=True, text=True, check=True, timeout=15 
            )
            
            # Check if output contains camera
            if 'Canon' in result.stdout:
                self._is_ready = True
                print("Canon camera (GPhoto2) detected and connected.")
                
                # 2. PREVENT SLEEP: Disable auto power off.
                try:
                    subprocess.run(
                        ['gphoto2', '--set-config', 'autopoweroff=0'],
                        capture_output=True, text=True, check=True, timeout=5
                    )
                    print("Camera setting: Autopoweroff disabled for stability.")
                except Exception as config_error:
                    # This is the warning we saw. Not a fatal error.
                    print(f"Warning: Could not disable autopoweroff: {config_error}")

            else:
                print("ERROR: Canon camera not detected by gphoto2. Is the camera on?")
                self._is_ready = False

        except subprocess.CalledProcessError as e:
            print(f"ERROR: gphoto2 command failed. Check camera and USB connection. (Error code: {e.returncode})")
            self._is_ready = False
        except FileNotFoundError:
            print("CRITICAL ERROR: gphoto2 command not found. Check if software is installed and in system PATH.")
            self._is_ready = False
        except subprocess.TimeoutExpired:
            print("CRITICAL ERROR: gphoto2 auto-detect timed out (> 15 seconds).")
            self._is_ready = False
            
    def read_frame(self) -> np.ndarray | None:
        """
        Uses '--capture-movie' for a short burst (1 second) and extracts the
        last frame from the downloaded MJPEG file. It parses the actual
        save path from gphoto2 output.
        """
        if not self.is_opened:
            return None

        # Ensure camera is in Live View
        # (Must be done manually on camera or via --set-config)

        # Create new temp file per run to avoid conflicts
        # Use abspath for max compatibility with sudo environment
        current_temp_file = os.path.abspath(os.path.join(tempfile.gettempdir(), f'gphoto_frame_{time.time()}.mjpg'))
        
        try:
            print(f"GPhoto2: Recording 1 second movie (target: {current_temp_file})...")
            # 1. Start short video recording and download
            result = subprocess.run(
                [
                    'gphoto2', 
                    '--filename', current_temp_file,  
                    '--capture-movie=1',                 # Record 1 second
                    '--force-overwrite'                  # Allow overwrite
                ],
                check=True, timeout=20, # Verhoog timeout voor opname en download
                capture_output=True, text=True 
            )
            
            # 1b. Debug: Search gphoto2 output for reported path
            # Typical gphoto2 output: 'Saving file as /path/to/file.mjpg'
            
            actual_path = current_temp_file
            
            # Search for path in output
            match = re.search(r'Saving file as (.+?)\n', result.stdout, re.IGNORECASE)
            if match:
                # Use path reported by gphoto2
                actual_path = match.group(1).strip()
                print(f"GPhoto2 Debug: gphoto2 reports saving to: {actual_path}")
            else:
                 print("GPhoto2 Debug: No explicit save path found in gphoto2 output. Using target path.")
                 # Print full stdout for further debugging
                 print(f"GPhoto2 Raw Output: {result.stdout.strip()}")


        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip()
            print(f"GPhoto2 Capture Error: {error_output}")
            print("Ensure camera is in Live View/Video recording mode.")
            return None
        except subprocess.TimeoutExpired:
            print("GPhoto2 Capture Timeout during movie recording.")
            return None
        except Exception as e:
            print(f"Unexpected error during gphoto2 capture: {e}")
            return None

        
        # 2. Wait briefly for file and load MJPEG
        time.sleep(0.5) 

        # Actively wait for file existence with timeout
        file_wait_timeout = 5 # 5 seconds max wait
        start_time = time.time()
        
        # Wait for path reported by gphoto2
        while not os.path.exists(actual_path) and (time.time() - start_time) < file_wait_timeout:
            print(f"Waiting for file: {actual_path}...")
            time.sleep(0.2)
        
        frame = None
        # Check path reported by gphoto2
        if os.path.exists(actual_path): 
            print(f"Movie file found at {actual_path}. Processing...")
            cap = cv2.VideoCapture(actual_path)
            
            if cap.isOpened():
                # Go to end of video to get last frame (optional, but good for robustness)
                cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)

                ret, frame = cap.read()
                cap.release()
                
                if ret and frame.size > 0:
                    # Update resolution based on actual camera output
                    self._resolution = (frame.shape[1], frame.shape[0])
                    return frame
                else:
                    print("Warning: OpenCV could not extract frame from movie (movie might be empty or damaged).")
            else:
                print("Warning: OpenCV could not open downloaded MJPEG.")
                
            # 3. Cleanup temp file
            try:
                os.remove(actual_path)
            except OSError as e:
                print(f"Warning: could not remove temp file {actual_path}. {e}")
            
        else:
            print(f"Error: Movie file NOT found after waiting: {actual_path}. GPhoto2 probably failed to write/download to this path.")
            
        return None


    def release(self):
        """Sets internal state to disconnected."""
        if self._is_ready:
            print("GPhoto2 camera released (state reset).")
            self._is_ready = False

    @property
    def is_opened(self) -> bool:
        return self._is_ready

    @property
    def resolution(self) -> tuple[int, int]:
        return self._resolution

    @property
    def aspect_ratio(self) -> float:
        return self._aspect_ratio