import pygame

class ImageUtils:
    @staticmethod
    def fit_image_to_rect(image, target_size, background=(255, 255, 255, 255)):
        """
        Resize image to fit within target_size (preserving aspect ratio).
        Pads with background color.
        range_size: (width, height)
        """
        img_w, img_h = image.get_size()
        target_w, target_h = target_size
        
        scale = min(target_w / img_w, target_h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        scaled_img = pygame.transform.smoothscale(image, (new_w, new_h))

        # Center the scaled image on a surface
        surface = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
        surface.fill(background)
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        surface.blit(scaled_img, (x, y))

        return surface

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def resize_and_crop_to_fit(image, new_width, new_height):
        """
        Resize an image to cover the target dimensions while preserving
        aspect ratio, then crop the excess from the center.
        No padding/space is filled.

        Args:
            image: a pygame.Surface
            new_width: target width in pixels
            new_height: target height in pixels

        Returns:
            pygame.Surface of size (new_width, new_height)
        """
        img_w, img_h = image.get_size()
        
        # 1. Bepaal de schaalfactor ('Cover' of 'Aspect Fill')
        # We gebruiken de GROOTSTE ratio (target/original) om te garanderen dat 
        # de geschaalde afbeelding zowel de nieuwe breedte als de nieuwe hoogte 'bedekt'.
        width_scale = new_width / img_w
        height_scale = new_height / img_h
        
        # De schaalfactor is de grootste van de twee verhoudingen
        scale = max(width_scale, height_scale)

        # 2. Bereken de afmetingen van de geschaalde afbeelding
        scaled_w = int(img_w * scale)
        scaled_h = int(img_h * scale)

        # 3. Schaal de afbeelding
        scaled_img = pygame.transform.smoothscale(image, (scaled_w, scaled_h))

        # 4. Crop de geschaalde afbeelding naar de doelafmetingen vanuit het midden
        
        # Bereken de offset om in het midden te beginnen met croppen
        # offset_x is hoeveel breder de geschaalde afbeelding is dan de doelbreedte
        offset_x = (scaled_w - new_width) // 2
        offset_y = (scaled_h - new_height) // 2
        
        # De crop_rect begint bij de offset en heeft de doelafmetingen
        crop_rect = pygame.Rect(offset_x, offset_y, new_width, new_height)

        # Gebruik subsurface om te croppen
        return scaled_img.subsurface(crop_rect).copy()

