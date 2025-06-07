import pygame


def fit_image_to_square(image, size, background=(255, 255, 255, 255)):
    """
    Resize an image to fit within a square while preserving aspect ratio.
    Pads with the specified background color.

    Args:
        image: a pygame.Surface
        size: target square size (width and height)
        background: fill color (default white)

    Returns:
        pygame.Surface of size (size, size)
    """
    img_w, img_h = image.get_size()
    scale = size / max(img_w, img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    scaled_img = pygame.transform.smoothscale(image, (new_w, new_h))

    # Center the scaled image on a square surface
    square = pygame.Surface((size, size), pygame.SRCALPHA)
    square.fill(background)
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    square.blit(scaled_img, (x, y))

    return square

def crop_to_square(image):
    """
    Crops the given image to a centered square based on the shortest side.

    Args:
        image: a pygame.Surface

    Returns:
        A square-cropped pygame.Surface
    """
    w, h = image.get_size()
    if w == h:
        return image.copy()

    if w > h:
        offset = (w - h) // 2
        crop_rect = pygame.Rect(offset, 0, h, h)
    else:
        offset = (h - w) // 2
        crop_rect = pygame.Rect(0, offset, w, w)

    return image.subsurface(crop_rect).copy()

