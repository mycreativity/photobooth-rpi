class GLUtils:
    @staticmethod
    def pixel_to_gl(rect, width, height, aspect_ratio):
        return GLUtils.pixel_values_to_gl(rect.left, rect.top, rect.width, rect.height, width, height, aspect_ratio)

    @staticmethod
    def pixel_values_to_gl(x, y, w, h, screen_width, screen_height, aspect_ratio):
        gl_left = (x / screen_width) * (2 * aspect_ratio) - aspect_ratio
        gl_right = ((x + w) / screen_width) * (2 * aspect_ratio) - aspect_ratio
        # Invert Y for OpenGL (where 0,0 is bottom-left in Pygame/top-left)
        gl_top = (1.0 - (y / screen_height)) * 2.0 - 1.0 
        gl_bottom = (1.0 - ((y + h) / screen_height)) * 2.0 - 1.0
        return gl_left, gl_right, gl_top, gl_bottom