import pygame
from ui.shapes import draw_rounded_rect_aa

class RetroButton:
    def __init__(self, rect, text, icon_surface, font, base_color, shadow_color, text_color=(255, 240, 220)):
        """
        Create a 3D retro-style button.

        Parameters:
            rect (tuple or pygame.Rect): (x, y, width, height)
            text (str): The label to show
            icon_surface (pygame.Surface): The loaded camera icon image
            font (pygame.font.Font): The font to use for text
            base_color (tuple): Button color (e.g. orange)
            shadow_color (tuple): Darker color for 3D shadow
            text_color (tuple): Text and icon color (default light cream)
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.icon = icon_surface
        self.font = font
        self.base_color = base_color
        self.shadow_color = shadow_color
        self.text_color = text_color

    def draw(self, surface):
        """Draw the 3D button with icon and text."""
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        radius = 30  # Rounded corner radius
        draw_rounded_rect_aa(surface, shadow_rect, self.shadow_color, radius=30)

        # Main button
        draw_rounded_rect_aa(surface, self.rect, self.base_color, radius=radius)

        # Icon
        icon_w = 0
        spacing = 0
        icon_scaled = None

        if self.icon:
            icon_aspect = self.icon.get_width() / self.icon.get_height()
            icon_height = self.rect.height - 20
            icon_w = int(icon_height * icon_aspect)
            icon_scaled = pygame.transform.smoothscale(self.icon, (icon_w, icon_height))
            spacing = 12

        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)

        # Layout calculation
        spacing = 12
        total_width = icon_w + spacing + text_surf.get_width()
        icon_x = self.rect.x + (self.rect.width - total_width) // 2
        # icon_y = self.rect.y + (self.rect.height - icon_scaled.get_height()) // 2
        text_x = icon_x + icon_w + spacing
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2

        # Blit
        if icon_scaled:
            surface.blit(icon_scaled, (icon_x, self.rect.y + (self.rect.height - icon_scaled.get_height()) // 2))
            icon_x += icon_w + spacing

        # Blit text
        surface.blit(text_surf, (text_x, text_y))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(event.pos)


class CircularRetroButton:
    def __init__(
        self,
        center,
        diameter,
        icon_surface,
        base_color,
        shadow_color,
        icon_scale=0.6,
        label_text=None,
        label_font=None,
        label_color=(60, 40, 20),
        label_margin=10
    ):
        """
        A circular retro-style button with a drop shadow and centered icon,
        optionally with a text label underneath.

        Args:
            center: (x, y) center of the button
            diameter: Diameter of the circular button
            icon_surface: Pygame Surface for the icon (can be None)
            base_color: Button face color
            shadow_color: Drop shadow color
            icon_scale: Icon size as fraction of diameter
            label_text: Optional string label below the button
            label_font: Pygame Font object for label
            label_color: Text color
            label_margin: Pixels between button and label
        """
        self.diameter = diameter
        self.radius = diameter // 2
        self.center = center
        self.base_color = base_color
        self.shadow_color = shadow_color
        self.icon = icon_surface
        self.icon_scale = icon_scale

        # Label config
        self.label_text = label_text
        self.label_font = label_font
        self.label_color = label_color
        self.label_margin = label_margin

        x, y = center
        self.rect = pygame.Rect(x - self.radius, y - self.radius, diameter, diameter)

    def draw(self, surface):
        shadow_offset = 4
        scale = 4
        hr_size = self.diameter * scale
        shadow_height = hr_size + shadow_offset * scale

        # Supersampled shadow + base
        hr_shadow_surf = pygame.Surface((hr_size, int(shadow_height)), pygame.SRCALPHA)
        hr_base_surf = pygame.Surface((hr_size, int(shadow_height)), pygame.SRCALPHA)

        pygame.draw.circle(hr_shadow_surf, self.shadow_color, (hr_size // 2, hr_size // 2 + shadow_offset * scale), hr_size // 2)
        pygame.draw.circle(hr_base_surf, self.base_color, (hr_size // 2, hr_size // 2), hr_size // 2)

        shadow_surf = pygame.transform.smoothscale(hr_shadow_surf, (self.diameter, self.diameter))
        base_surf = pygame.transform.smoothscale(hr_base_surf, (self.diameter, self.diameter))

        top_left = (self.center[0] - self.radius, self.center[1] - self.radius)
        surface.blit(shadow_surf, top_left)
        surface.blit(base_surf, top_left)

        # Draw icon
        if self.icon:
            target_size = int(self.diameter * self.icon_scale)
            icon = pygame.transform.smoothscale(self.icon, (target_size, target_size))
            icon_rect = icon.get_rect(center=self.center)
            surface.blit(icon, icon_rect)

        # Draw label below
        if self.label_text and self.label_font:
            label_surf = self.label_font.render(self.label_text, True, self.label_color)
            label_rect = label_surf.get_rect(midtop=(self.center[0], self.center[1] + self.radius + self.label_margin))
            surface.blit(label_surf, label_rect)

    def is_hovered(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(event.pos)
