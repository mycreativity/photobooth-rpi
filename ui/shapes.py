import pygame
import numpy as np
from scipy.ndimage import gaussian_filter

def create_blurred_shadow(size, radius=20, blur_radius=10, color=(0, 0, 0, 80), scale=1.0):
    """
    Create a blurred shadow surface for any rectangular shape.
    
    Args:
        size: (width, height) tuple
        radius: corner radius for rounded shadow
        blur_radius: blur strength
        color: RGBA tuple
        scale: optional scale factor for super-sampling

    Returns:
        (shadow_surface, padding)
    """
    w, h = size
    padding = int(blur_radius * 2)
    surf_w, surf_h = w + padding * 2, h + padding * 2

    # 1. Base surface with filled rounded rect
    base = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(padding, padding, w, h)
    pygame.draw.rect(base, color, shadow_rect, border_radius=radius)

    # 2. Blur the alpha channel
    alpha_array = pygame.surfarray.pixels_alpha(base).astype(np.float32).T  # Transpose to (H, W)
    blurred_alpha = gaussian_filter(alpha_array, sigma=blur_radius)
    blurred_alpha = np.clip(blurred_alpha, 0, 255).astype(np.uint8)

    # 3. Combine RGBA
    rgba_array = np.empty((surf_h, surf_w, 4), dtype=np.uint8)
    rgba_array[:, :, :3] = color[:3]
    rgba_array[:, :, 3] = blurred_alpha

    shadow_surface = pygame.image.frombuffer(rgba_array.tobytes(), (surf_w, surf_h), "RGBA")

    return shadow_surface.copy(), padding


def draw_rounded_rect_aa(surface, rect, color, radius, scale=4):
    """
    Draws a smooth anti-aliased rounded rectangle using super-sampled scaling.

    Args:
        surface: Target Pygame surface
        rect: Target area as tuple or pygame.Rect
        color: Fill color (RGB or RGBA)
        radius: Corner radius at base scale
        scale: Supersample scale factor (default 4x)
    """
    if isinstance(rect, tuple):
        rect = pygame.Rect(rect)

    # High-res dimensions
    w, h = rect.width * scale, rect.height * scale
    hr_radius = radius * scale

    # Step 1: Render to a high-res surface
    highres_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(
        highres_surf,
        color,
        pygame.Rect(0, 0, w, h),
        border_radius=hr_radius
    )

    # Step 2: Smoothscale down
    smoothed = pygame.transform.smoothscale(highres_surf, (rect.width, rect.height))

    # Step 3: Blit onto destination
    surface.blit(smoothed, rect.topleft)

