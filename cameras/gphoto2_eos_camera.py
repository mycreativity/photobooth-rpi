import cv2
import numpy as np
import subprocess
import os
import tempfile
import time
import re # Nodig voor reguliere expressies om het pad te vinden
from .camera_interface import CameraInterface 

class GPhoto2EOSCamera(CameraInterface):
    """
    Concrete camera implementation using the gphoto2 command-line tool for DSLR control
    (e.g., Canon EOS 750D).

    LET OP: Deze klasse is veel langzamer (1-2 FPS) dan een webcam omdat deze 
    een extern commando uitvoert en een bestand leest voor elke frame. 
    
    *** BELANGRIJK: De command-line tool 'gphoto2' (NIET de Python-wrapper) 
    moet geïnstalleerd zijn op het systeem! ***
    """
    
    def __init__(self):
        self._is_ready = False
        # Gphoto2 preview resolutie is vaak vast en relatief laag
        self._resolution = (640, 480) 
        self._aspect_ratio = self._resolution[0] / self._resolution[1]
        # Tijdelijk pad voor de gedownloade film (MJPEG)
        # Wordt niet meer gebruikt in read_frame, maar blijft als fallback
        self._temp_file_path = os.path.join(tempfile.gettempdir(), f'gphoto_movie_{os.getpid()}_{time.time()}.mjpg')
        
    def start(self, width: int, height: int):
        """Controleert of de camera is aangesloten, gphoto2 werkt, en stelt de camera in."""
        print("Starting GPhoto2 camera connection...")
        try:
            # 1. Detecteer camera
            result = subprocess.run(
                ['gphoto2', '--auto-detect'],
                capture_output=True, text=True, check=True, timeout=15 
            )
            
            # Controleer of de uitvoer de camera bevat
            if 'Canon' in result.stdout:
                self._is_ready = True
                print("Canon camera (GPhoto2) gedetecteerd en verbonden.")
                
                # 2. VOORKOM SLAAPSTAND: Schakel automatische uitschakeling uit.
                try:
                    subprocess.run(
                        ['gphoto2', '--set-config', 'autopoweroff=0'],
                        capture_output=True, text=True, check=True, timeout=5
                    )
                    print("Camera instelling: Autopoweroff uitgeschakeld voor stabiliteit.")
                except Exception as config_error:
                    # Dit is de waarschuwing die we zagen. Dit is geen fatale fout.
                    print(f"Waarschuwing: Kon autopoweroff niet uitschakelen: {config_error}")

            else:
                print("ERROR: Canon camera niet gedetecteerd door gphoto2. Is de camera aan?")
                self._is_ready = False

        except subprocess.CalledProcessError as e:
            print(f"ERROR: gphoto2 commando mislukt. Controleer de camera en de USB-verbinding. (Foutcode: {e.returncode})")
            self._is_ready = False
        except FileNotFoundError:
            print("CRITIEKE FOUT: gphoto2 commando niet gevonden. Controleer of de software is geïnstalleerd en in de systeem PATH staat.")
            self._is_ready = False
        except subprocess.TimeoutExpired:
            print("CRITIEKE FOUT: gphoto2 auto-detect is verlopen (timeout > 15 seconden).")
            self._is_ready = False
            
    def read_frame(self) -> np.ndarray | None:
        """
        Gebruikt '--capture-movie' voor een korte burst (1 seconde) en extraheert het 
        laatste frame uit het gedownloade MJPEG-bestand. Het zoekt het daadwerkelijke 
        opslaanpad uit de gphoto2-output.
        """
        if not self.is_opened:
            return None

        # Zorg ervoor dat de camera in Live View staat
        # (Dit moet handmatig op de camera gebeuren, of geconfigureerd worden via --set-config)

        # We maken een nieuw tijdelijk bestand per run om conflicten te voorkomen
        # Gebruik abspath voor maximale compatibiliteit met de sudo environment
        current_temp_file = os.path.abspath(os.path.join(tempfile.gettempdir(), f'gphoto_frame_{time.time()}.mjpg'))
        
        try:
            print(f"GPhoto2: Opnemen van 1 seconde film (target: {current_temp_file})...")
            # 1. Start een korte video-opname en download deze
            result = subprocess.run(
                [
                    'gphoto2', 
                    '--filename', current_temp_file,  
                    '--capture-movie=1',                 # Neem 1 seconde op
                    '--force-overwrite'                  # Zorg dat we kunnen overschrijven
                ],
                check=True, timeout=20, # Verhoog timeout voor opname en download
                capture_output=True, text=True 
            )
            
            # 1b. Debug: Zoek in de output van gphoto2 of deze een ander pad rapporteert
            # Typische gphoto2 output: 'Saving file as /path/to/file.mjpg'
            
            actual_path = current_temp_file
            
            # Zoek naar het pad in de output
            match = re.search(r'Saving file as (.+?)\n', result.stdout, re.IGNORECASE)
            if match:
                # Gebruik het pad dat gphoto2 zelf gerapporteerd heeft
                actual_path = match.group(1).strip()
                print(f"GPhoto2 Debug: gphoto2 rapporteert opslag naar: {actual_path}")
            else:
                 print("GPhoto2 Debug: Geen expliciet opslagpad gevonden in gphoto2 output. Gebruiken target pad.")
                 # Print de volledige stdout voor verdere debugging door de gebruiker
                 print(f"GPhoto2 Raw Output: {result.stdout.strip()}")


        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip()
            print(f"GPhoto2 Capture Error: {error_output}")
            print("Zorg ervoor dat de camera in de Live View/Video-opnamemodus staat.")
            return None
        except subprocess.TimeoutExpired:
            print("GPhoto2 Capture Timeout tijdens het opnemen van de film.")
            return None
        except Exception as e:
            print(f"Onverwachte fout tijdens gphoto2 capture: {e}")
            return None

        
        # 2. Wacht kort op het bestand en laad het MJPEG-bestand
        time.sleep(0.5) 

        # We proberen nu actief te wachten of het bestand er is, met een korte timeout
        file_wait_timeout = 5 # 5 seconden max wachten
        start_time = time.time()
        
        # Wachten op het door gphoto2 gerapporteerde pad
        while not os.path.exists(actual_path) and (time.time() - start_time) < file_wait_timeout:
            print(f"Wachten op bestand: {actual_path}...")
            time.sleep(0.2)
        
        frame = None
        # Controleer het door gphoto2 gerapporteerde pad
        if os.path.exists(actual_path): 
            print(f"Filmbestand gevonden op {actual_path}. Verwerken...")
            cap = cv2.VideoCapture(actual_path)
            
            if cap.isOpened():
                # Ga naar het einde van de video om het laatste frame te krijgen (optioneel, maar goed voor robuustheid)
                cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)

                ret, frame = cap.read()
                cap.release()
                
                if ret and frame.size > 0:
                    # Update resolutie op basis van de daadwerkelijke output van de camera
                    self._resolution = (frame.shape[1], frame.shape[0])
                    return frame
                else:
                    print("Waarschuwing: OpenCV kon geen frame uit de film halen (mogelijk is de film leeg of beschadigd).")
            else:
                print("Waarschuwing: OpenCV kon de gedownloade MJPEG niet openen.")
                
            # 3. Ruim het tijdelijke bestand op
            try:
                os.remove(actual_path)
            except OSError as e:
                print(f"Waarschuwing: kon tijdelijk bestand {actual_path} niet verwijderen. {e}")
            
        else:
            print(f"Fout: Filmbestand NIET gevonden na wachten: {actual_path}. GPhoto2 kon het bestand waarschijnlijk niet schrijven/downloaden naar dit pad.")
            
        return None


    def release(self):
        """Zet de interne status op niet-verbonden."""
        if self._is_ready:
            print("GPhoto2 camera vrijgegeven (state reset).")
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