import pygame

class UIText:
    def __init__(self, text, font, color=(50, 50, 50), pos=(0, 0), max_width=None, align="topleft"):
        """
        UI text component.

        Args:
            text: The string to render
            font: A pygame.font.Font object
            color: Text color (RGB)
            pos: Position tuple relative to surface
            max_width: Optional width for wrapping/clipping
            align: Alignment: "topleft", "center", "midtop", etc.
        """
        self.text = text
        self.font = font
        self.color = color
        self.pos = pos
        self.max_width = max_width
        self.align = align

        # Pre-rendered lines if multiline
        self.rendered_lines = self._render_lines()

    def _render_lines(self):
        if not self.max_width:
            return [self.font.render(self.text, True, self.color)]

        words = self.text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, self.color)
            if test_surface.get_width() > self.max_width:
                lines.append(self.font.render(current_line.strip(), True, self.color))
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            lines.append(self.font.render(current_line.strip(), True, self.color))

        return lines

    def draw(self, surface):
        y_offset = 0
        for line in self.rendered_lines:
            line_rect = line.get_rect()
            setattr(line_rect, self.align, (self.pos[0], self.pos[1] + y_offset))
            surface.blit(line, line_rect)
            y_offset += line.get_height()

