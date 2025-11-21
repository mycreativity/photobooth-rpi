class GLUtils:
    @staticmethod
    def pixel_to_gl(rect, width, height, aspect_ratio):
        gl_left = (rect.left / width) * (2 * aspect_ratio) - aspect_ratio
        gl_right = ((rect.left + rect.width) / width) * (2 * aspect_ratio) - aspect_ratio
        # Invert Y for OpenGL (where 0,0 is bottom-left in Pygame/top-left)
        # The actual GL coordinate system is often (0,0) bottom-left, so we calculate Y position
        # using (1.0 - y_ratio) to correctly map Pygame's top-down coordinates.
        gl_top = (1.0 - (rect.top / height)) * 2.0 - 1.0 
        gl_bottom = (1.0 - ((rect.top + rect.height) / height)) * 2.0 - 1.0
        return gl_left, gl_right, gl_top, gl_bottom