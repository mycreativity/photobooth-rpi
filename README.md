# Loomo Photobooth

A Python-based photobooth application designed for Raspberry Pi (and macOS), featuring DSLR integration (Canon EOS) and a smooth OpenGL-based UI.

## Features
- **DSLR Live View**: Real-time high-quality preview using `gphoto2`.
- **Countdown UI**: Animated countdown screen.
- **OpenGL Rendering**: Efficient hardware-accelerated display using PyGame and OpenGL.
- **Cross-Platform**: Runs on Raspberry Pi (Linux) and macOS.

## Hardware Requirements
- **Camera**: Canon EOS DSLR (tested with 750D).
- **Computer**: Raspberry Pi 4/5 or macOS.
- **Connection**: USB cable between camera and computer.

## Installation

### Prerequisites
1.  **System Dependencies**:
    - **macOS**: `brew install gphoto2`
    - **Linux (RPi)**: `sudo apt install gphoto2 libgphoto2-dev`

2.  **Python Environment**:
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Python Packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Connect your DSLR camera via USB.
2.  Ensure the camera is ON and auto-power-off is disabled (or set to a long duration).
3.  Run the application:
    ```bash
    source venv/bin/activate
    python main.py
    ```
    *(Note: On some systems, you might need `sudo` if permissions are an issue, but standard user permissions should suffice with correct udev rules).*

## Troubleshooting
- **Black Screen**: Ensure the camera is in Live View mode or supported by `gphoto2`.
- **"Could not claim interface"**: Make sure no other process (like the OS file manager) has mounted the camera.