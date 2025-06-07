# Photobooth

A retro-inspired photobooth application built with Pygame, featuring a countdown timer, animated polaroid carousel, and a stylish UI for taking and previewing photos.

## Features

- **Animated Start Screen**: Carousel of recent photos in polaroid frames.
- **Touch/Click to Start**: Large retro button to begin photo session.
- **Countdown Timer**: Visual countdown before capturing a photo.
- **Live Camera Capture**: Uses OpenCV to take photos from your webcam.
- **Photo Preview**: Approve or retake your photo with stylish buttons.
- **Polaroid-Style Frames**: Photos are displayed in realistic polaroid frames with shadows and textures.
- **FPS Counter**: For performance monitoring.

## Folder Structure

```
assets/         # Fonts, images, sounds (UI textures, icons, shutter sound)
photos/         # Saved photos (auto-ignored by git)
screens/        # Screen classes (start, countdown, preview, etc.)
ui/             # UI components (buttons, cards, polaroid, carousel, etc.)
utils/          # Utility functions (image processing, etc.)
main.py         # Application entry point
```

## Requirements

- Python 3.8+
- [Pygame](https://www.pygame.org/)
- [OpenCV](https://opencv.org/) (`opencv-python`)
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)

Install dependencies:

```sh
pip install pygame opencv-python numpy scipy
```

## Usage

1. Place your assets (fonts, images, sounds) in the [`assets`](assets) directory.
2. Run the application:

```sh
python main.py
```

3. Photos taken will be saved in the [`photos`](photos) directory.

## Customization

- **UI Text & Fonts**: Change text and font files in [`ui/card.py`](ui/card.py), [`ui/text.py`](ui/text.py), etc.
- **Photo Frame Textures**: Replace images in [`assets/images`](assets/images).
- **Sounds**: Replace [`assets/sounds/shutter.wav`](assets/sounds/shutter.wav) for custom shutter sound.

## Notes

- The [`photos`](photos) directory is git-ignored by default.
- Make sure your webcam is connected and accessible.
- For best results, use high-resolution assets and fonts.

---

**Made with ❤️ using Pygame and OpenCV.**
