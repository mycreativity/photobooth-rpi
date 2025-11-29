import io
import threading
import time
import gphoto2 as gp
from PIL import Image

class GPhoto2EOSCameraHandler(threading.Thread):
    """
    Handler voor gphoto2-communicatie (Live View, foto's)
    Erft van threading.Thread voor asynchrone Live View.
    """
    def __init__(self):
        # Initialiseert de thread functionaliteit
        super().__init__() 
        self.running = False
        self.live_view_active = False
        self.latest_image = None # Slaat het laatste PIL Image object op
        self.image_lock = threading.Lock() # Lock om veilig toegang te krijgen tot latest_image
        self._stop_event = threading.Event() # Event om de thread te stoppen

        # Initialiseer camera
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
            
        # Oude logica voor 350D/onbekende modellen (niet relevant voor 750D, maar overgenomen uit focus-gui.py)
        if self.camera_model == 'unknown':
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                self.config, 'capturesizeclass')
            if OK >= gp.GP_OK:
                value = capture_size_class.get_choice(2)
                capture_size_class.set_value(value)
                self.camera.set_config(self.config)
        else:
            # Zet de camera in preview-modus om de spiegel op te klappen (belangrijk voor Canon)
            try:
                gp.gp_camera_capture_preview(self.camera)
            except gp.GPhoto2Error as e:
                print(f"Waarschuwing: Kan preview niet starten. Fout: {e}")

    # De 'run' methode wordt automatisch aangeroepen wanneer thread.start() wordt gebruikt
    def run(self):
        """
        De hoofd lus voor continue Live View (als deze geactiveerd is).
        """
        while not self._stop_event.is_set():
            if self.live_view_active:
                # Roep de preview functie aan. Deze is blokkerend per frame.
                image = self._do_preview()
                
                if image:
                    # Sla het ontvangen beeld veilig op
                    with self.image_lock:
                        self.latest_image = image
                
                # Voeg een kleine pauze toe om de CPU te ontlasten
                # en de camera ademruimte te geven (kan eventueel worden verwijderd)
                time.sleep(0.005) 
            else:
                # Slaapt zolang er geen Live View actief is
                time.sleep(0.1) 

    # --- Publieke Methoden voor Externe Aanroepen ---

    def start_continuous(self):
        """
        Activeert de continue Live View modus en start de thread als deze nog niet draait.
        """
        if not self._set_config():
            return
        
        self.live_view_active = True
        
        if not self.running:
            self.running = True
            self.start() # Start de thread

    def stop_continuous(self):
        """
        Deactiveert de continue Live View modus.
        """
        self.live_view_active = False

    def get_latest_image(self):
        """
        Haalt het laatst ontvangen PIL Image object op.
        """
        with self.image_lock:
            return self.latest_image

    def one_shot(self):
        """
        Vraagt één enkele preview op (blokkerend).
        Geeft de PIL Image terug.
        """
        if self.running:
            print("Kan geen one-shot doen: continuous mode is actief.")
            return None
            
        if not self._set_config():
            return None
        
        return self._do_preview()

    def take_photo(self):
        """
        Maakt een volledige foto (blokkerend).
        Geeft de PIL Image terug.
        """
        if self.running:
            print("Kan geen foto maken: continuous mode is actief.")
            return None
        
        self._reset_config()
        return self._do_capture()

    def shut_down(self):
        """
        Sluit de thread en de camera-verbinding correct af.
        """
        self._stop_event.set()

        if self.is_alive():
            self.join() # Wacht tot de thread klaar is
        
        self._reset_config()
        self.camera.exit()

    # --- Interne Hulpfuncties ---
    
    def _do_preview(self):
        # Vraagt een preview frame aan
        try:
            _, camera_file = gp.gp_camera_capture_preview(self.camera)
            return self._send_file(camera_file)
        except gp.GPhoto2Error as e:
             print(f'Fout bij opvragen preview: {e}')
             # Zet Live View uit bij fout
             self.live_view_active = False
             return None
             
    def _do_capture(self):
        # Vraagt een volledige foto aan (traag)
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
        Verwerkt de binaire camera data en geeft een PIL Image object terug.
        """
        file_data = camera_file.get_data_and_size()
        image = Image.open(io.BytesIO(file_data))
        # Image.load() is nodig om de data in de thread te verwerken voordat we het lock vrijgeven
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
                print('Kan geen preview van RAW-afbeeldingen weergeven')
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