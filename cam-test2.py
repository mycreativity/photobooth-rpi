import sys
import os
import signal
import time
from io import BytesIO

# Third-party libraries
try:
    import pygame
    from PIL import Image
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install them using: pip install pygame pillow")
    sys.exit(1)


# --- Constants ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FRAME_RATE = 30
FRAME_DELAY_MS = 1000 / FRAME_RATE

# --- Global State (Equivalent to static C variables) ---
# Pygame manages the window and surface internally, so we use global variables for convenience
# of access in the C-like structure.
window_surface = None

def handle_signal(sig, frame):
    """
    Equivalent to handle_signal() in C. Cleans up and exits gracefully.
    """
    print("\nInterrupted! Exiting program..")
    # Pygame's quit handles both SDL_DestroyWindow and SDL_Quit
    pygame.quit()
    sys.exit(0)

def draw(frame_buffer: bytes):
    """
    Equivalent to draw() in C. Takes the raw JPEG bytes and displays them.
    """
    global window_surface
    if not window_surface:
        # Should not happen if main is structured correctly
        print("Error: Pygame surface not initialized.")
        return

    try:
        # 1. Use BytesIO as a memory buffer (equivalent to SDL_RWFromMem)
        rw_ops = BytesIO(frame_buffer)
        
        # 2. Use PIL to load the JPEG image from the buffer (equivalent to IMG_Load_RW)
        # Note: If the JPEG is corrupt, Image.open will raise an exception.
        pil_image = Image.open(rw_ops)
        
        # 3. Scale the image to the window size if necessary (optional, C code implies stretching to window size)
        # In the C code, SDL_BlitSurface handles scaling if the source/dest rects are different, 
        # but here we'll assume the loaded image should fit.
        # This converts the PIL image to a Pygame Surface
        image_surface = pygame.image.frombuffer(pil_image.tobytes(), pil_image.size, pil_image.mode)

        # 4. Blit/Scale the image surface onto the window surface (equivalent to SDL_BlitSurface)
        # The C code uses SDL_BlitSurface which doesn't scale. 
        # pygame.transform.scale is needed if the JPEG isn't already WINDOW_WIDTH x WINDOW_HEIGHT.
        scaled_surface = pygame.transform.scale(image_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        window_surface.blit(scaled_surface, (0, 0))

        # 5. Update the display (equivalent to SDL_UpdateWindowSurface)
        pygame.display.update()

    except Exception as e:
        # Pygame/PIL errors are caught here (equivalent to checking SDL_GetError())
        print(f"Drawing error: {e}", file=sys.stderr)

def read_jpeg(file):
    """
    Equivalent to read_jpeg(FILE *file) in C.
    Reads bytes from the file object until the JPEG End of Image marker (0xFFD9) is found.
    This function blocks until a full JPEG frame is read.
    """
    frame_buffer = bytearray()
    started = False

    try:
        while True:
            # Reads 2 bytes at a time (equivalent to two fgetc in C)
            chunk = file.read(2)
            if not chunk:
                # End of file reached
                break

            c1, c2 = chunk[0], chunk[1]
            code = (c1 << 8) | c2 # Combines into a 16-bit code (equivalent to ((c1 << 8) | c2))

            if started:
                frame_buffer.extend(chunk)
                if code == 0xffd9: # EOI (End of Image) marker
                    break
            else:
                if code == 0xffd8: # SOI (Start of Image) marker
                    frame_buffer.extend(chunk)
                    started = True
        
        return bytes(frame_buffer)

    except EOFError:
        print("Error reading from file: End of file reached prematurely.", file=sys.stderr)
        return b''
    except Exception as e:
        print(f"Error reading JPEG data: {e}", file=sys.stderr)
        return b''

def main():
    """
    Equivalent to main() in C. Handles file opening, initialization, and the main loop.
    """
    global window_surface

    # --- Setup Signal Handling ---
    # Register the Python handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, handle_signal)

    # --- File/Input Setup ---
    # Default to standard input
    input_file = sys.stdin.buffer # Use buffer for binary I/O on stdin

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            # Open file in read binary mode 'rb'
            input_file = open(file_path, 'rb')
        except OSError as e:
            # Equivalent to strerror(errno) in C
            print(f"Error opening file '{file_path}': {os.strerror(e.errno)}", file=sys.stderr)
            sys.exit(-1)
    
    # --- SDL/Pygame Initialization ---
    try:
        # Initialises all the Pygame modules (equivalent to SDL_Init(SDL_INIT_VIDEO))
        pygame.init()
    except pygame.error as e:
        print(f"SDL Initialization error: {e}", file=sys.stderr)
        sys.exit(-1)

    # --- Window Creation ---
    try:
        # Equivalent to SDL_CreateWindow and SDL_GetWindowSurface
        window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SHOWN)
        pygame.display.set_caption("gPhoto2 LiveView Example")
    except pygame.error as e:
        print(f"Window creation error: {pygame.get_error()}", file=sys.stderr)
        pygame.quit()
        sys.exit(-1)

    # Pygame's clock helps manage the frame rate
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # --- Event Polling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        
        # --- Read Frame ---
        # The C code implies an infinite loop reading continuous JPEGs from the input source.
        # It's important that the file/stream provides valid, continuous JPEG data.
        frame_data = read_jpeg(input_file)

        if frame_data:
            # --- Draw Frame ---
            draw(frame_data)

        # --- Frame Rate Delay ---
        # Equivalent to SDL_Delay(1000 / FRAME_RATE). 
        # tick(FRAME_RATE) will pause to match the target FPS.
        clock.tick(FRAME_RATE)

    # --- Cleanup ---
    if input_file is not sys.stdin.buffer:
        input_file.close()
    
    # Clean up SDL resources (equivalent to SDL_DestroyWindow and SDL_Quit)
    pygame.quit()

if __name__ == "__main__":
    main()