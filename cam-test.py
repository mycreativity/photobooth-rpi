import subprocess
import cv2
import numpy as np
import sys
import time

def setup_camera_liveview():
    """
    Stelt de camera in staat om Live View te starten. 
    Dit commando werkt mogelijk niet voor alle Canon modellen, maar is het proberen waard.
    """
    print("Camera voorbereiden voor Live View...")
    try:
        # Optionele stap: forceer de Live View modus in te schakelen
        # Sommige camera's hebben dit nodig om continu frames te versturen
        subprocess.run(
            ['gphoto2', '--set-config', '/main/actions/viewfinder=1'], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print("Camera Live View instelling aangepast. Start preview...")
    except subprocess.CalledProcessError as e:
        # Negeer deze fout als de camera het commando niet ondersteunt,
        # we proberen het preview commando alsnog.
        print(f"Waarschuwing: Kan Live View config niet instellen ({e.stderr.strip()}). Ga verder...")
    except FileNotFoundError:
        print("FATALE FOUT: gphoto2 is niet gevonden.")
        sys.exit(1)


def streaming_live_preview_gphoto2():
    """
    Toont een continue live preview door gphoto2 in een strakke lus aan te roepen.
    """
    
    # Roep de setup functie aan
    setup_camera_liveview()
    
    print("Continue Live Preview gestart. Druk op 'q' in het venster om te stoppen.")
    
    frame_count = 0
    start_time = time.time()
    
    # De lus blijft actief totdat de gebruiker op 'q' drukt
    while True:
        try:
            # 1. Roep gphoto2 aan voor EEN preview en stuur deze naar stdout
            # Dit is de snelst mogelijke manier om een frame te krijgen.
            gphoto_command = ['gphoto2', '--capture-preview', '--stdout', '--quiet']
            
            # Voer het commando uit en vang de binaire output
            result = subprocess.run(
                gphoto_command, 
                capture_output=True, 
                check=True,  # Gooi een fout als gphoto2 mislukt
                timeout=2    # Geef op na 2 seconden als er geen frame komt
            )
            
            jpeg_data = result.stdout
            
            if jpeg_data:
                # 2. Decodeer en toon de afbeelding met OpenCV
                np_arr = np.frombuffer(jpeg_data, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    frame_count += 1
                    
                    # Optioneel: Toon FPS in de console om de snelheid te meten
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                    window_title = f'Canon EOS 750D Live Preview | FPS: {fps:.2f}'
                    
                    cv2.imshow(window_title, frame)
                    
                    # Wacht 1 milliseconde en controleer op 'q'
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    print("Waarschuwing: Kon JPEG-frame niet decoderen.")
            
            # Korte pauze is hier niet nodig, want subprocess.run is al blokkerend 
            # en wacht tot gphoto2 klaar is met het ene frame.
            
        except subprocess.TimeoutExpired:
            # Dit gebeurt als de camera te lang doet over het leveren van een frame
            print("Waarschuwing: Time-out bij frame-wacht. Camera reageert traag.")
        except subprocess.CalledProcessError as e:
            # Fout in gphoto2 (bijv. camera losgekoppeld)
            print(f"\nFOUT: Gphoto2-oproep mislukt: {e.stderr.decode().strip()}.")
            time.sleep(1) # Pauzeer en probeer opnieuw
        except Exception as e:
            print(f"\nOnverwachte fout: {e}")
            break
            
    # 3. Opruimen
    print("\nSluit OpenCV vensters en reset camera...")
    cv2.destroyAllWindows()
    
    try:
        # Reset de Live View modus naar 0 (uit) bij het afsluiten
        subprocess.run(
            ['gphoto2', '--set-config', '/main/actions/viewfinder=0'], 
            capture_output=True
        )
    except Exception:
        pass # Negeer fouten tijdens het opruimen
    
    print("Opruiming voltooid.")

if __name__ == '__main__':
    streaming_live_preview_gphoto2()