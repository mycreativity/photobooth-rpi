import pygame
from config import *
from ui.button import Button
from ui.photo_layout import PhotoLayoutPreview, PhotoFrame
from ui.live_preview import LivePreview
from .screen_interface import ScreenInterface
from utils.logger import get_logger

logger = get_logger("LayoutSelectionScreen")

from ui.text_label import TextLabel

class LayoutSelectionScreen(ScreenInterface):
    """
    Screen for selecting the photo layout: Single or Collage (4 photos).
    """
    
    def __init__(self, renderer, width, height, camera):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera = camera
        self.sizing_factor = width / 1280 
        
        # --- LIVE PREVIEW ---
        self.live_preview = LivePreview(renderer, width, height)

        # Style constants
        self.active_color = WHITE_COLOR
        self.inactive_color = (255, 255, 255, 100) # Dimmed white
        self.option_bg_color = (255, 255, 255, 150)
        self.selected_border_color = PRIMARY_COLOR # Or some highlight color
        self.default_border_color = WHITE_COLOR
        
        self.selected_layout = None # 'single' or 'collage'

        # --- LABELS ---
        self.lbl_option1 = TextLabel(renderer, "SINGLE PHOTO", FONT_DISPLAY_SMALL, color=WHITE_COLOR)
        self.lbl_option2 = TextLabel(renderer, "4 PHOTO COLLAGE", FONT_DISPLAY_SMALL, color=WHITE_COLOR)

        # --- BUTTON: NEXT ---
        self.btn_next = Button(
            renderer,
            text="NEXT",
            font=FONT_DISPLAY,
            color=self.inactive_color, # Initially inactive
            bg_color=(BLACK_COLOR[0], BLACK_COLOR[1], BLACK_COLOR[2], 51),
            border_color=self.inactive_color,
            border_radius=20,
            border_width=5,
            padding=30,
            text_offset=(0, 10)
        )
        
        start_x = (self.width - self.btn_next.rect.width) // 2
        start_y = int(self.height - self.btn_next.rect.height - 20) # Move down a bit to clear options
        
        self.btn_next.set_position((start_x, start_y))

        # --- PHOTO OPTIONS ---
        optionSize = (420, 280)
        optionSpacer = 150
        
        # Calculate positions
        opt1_x = self.width/2 - optionSize[0] - optionSpacer/2
        opt1_y = self.height/2 - optionSize[1]/2
        
        opt2_x = self.width/2 + optionSpacer/2
        opt2_y = self.height/2 - optionSize[1]/2

        self.option1 = PhotoLayoutPreview(
            renderer,
            frames=[
                PhotoFrame(renderer, size=(400,260), position=(10, 10), bg_color=self.option_bg_color, text="1", image_path="assets/images/photo_mock_1.png")
                ],
            position=(opt1_x, opt1_y),
            size=optionSize,
            border_width=5,
            border_color=self.inactive_color,
            bg_color=(0, 0, 0, 51)
        )

        self.option2 = PhotoLayoutPreview(
            renderer,
            frames=[
                PhotoFrame(renderer, size=(260,260), position=(10, 10), bg_color=self.option_bg_color, text="1", image_path="assets/images/photo_mock_1.png"), 
                PhotoFrame(renderer, size=(130,80), position=(280, 10), bg_color=self.option_bg_color, text="2", image_path="assets/images/photo_mock_2.png"), 
                PhotoFrame(renderer, size=(130,80), position=(280, 100), bg_color=self.option_bg_color, text="3", image_path="assets/images/photo_mock_3.png"), 
                PhotoFrame(renderer, size=(130,80), position=(280, 190), bg_color=self.option_bg_color, text="4", image_path="assets/images/photo_mock_4.png")
                ],
            position=(opt2_x, opt2_y),
            size=optionSize,
            border_width=5,
            border_color=self.inactive_color,
            bg_color=(0, 0, 0, 51)
        )
        
        # Position Labels above options
        # Center label relative to option
        l1_x = opt1_x + (optionSize[0] - self.lbl_option1.rect.width) // 2
        l1_y = opt1_y - self.lbl_option1.rect.height - 10
        self.lbl_option1.set_position((l1_x, l1_y))

        l2_x = opt2_x + (optionSize[0] - self.lbl_option2.rect.width) // 2
        l2_y = opt2_y - self.lbl_option2.rect.height - 10
        self.lbl_option2.set_position((l2_x, l2_y))


    def _update_ui_state(self):
        """Updates colors and states based on selection."""
        
        # Option 1 State
        if self.selected_layout == 'single':
            self.option1.border_color = self.active_color
            self.option1.bg_color = (255, 255, 255, 50) # Highlight bg slightly
        else:
            self.option1.border_color = self.inactive_color
            self.option1.bg_color = (0, 0, 0, 51)
        self.option1._update_texture() # Force redraw of border

        # Option 2 State
        if self.selected_layout == 'collage':
            self.option2.border_color = self.active_color
            self.option2.bg_color = (255, 255, 255, 50)
        else:
            self.option2.border_color = self.inactive_color
            self.option2.bg_color = (0, 0, 0, 51)
        self.option2._update_texture()

        # Next Button State
        if self.selected_layout:
            self.btn_next.color = self.active_color
            self.btn_next.border_color = self.active_color
        else:
            self.btn_next.color = self.inactive_color
            self.btn_next.border_color = self.inactive_color
        
        # Re-render button text label with new color? 
        # Button doesn't auto-update label color on property change yet.
        # We need to manually recreate/update the internal label if color changes.
        # Or ideally Button.set_color().
        # Better: let's just make a simple helper or assume Button handles it in next draw? No it doesn't.
        # Let's direct modify the label.
        if self.btn_next.label:
            self.btn_next.label.color = self.btn_next.color
            self.btn_next.label.update_text(self.btn_next.text)
        self.btn_next._update_texture() # For border color update

    def handle_event(self, event, switch_screen_callback):
        # Handle Option Selection
        if self.option1.is_clicked(event):
            self.selected_layout = 'single'
            self._update_ui_state()
            logger.info("Layout selected: Single")
        
        if self.option2.is_clicked(event):
            self.selected_layout = 'collage'
            self._update_ui_state()
            logger.info("Layout selected: Collage")

        # Handle Next Click (Only if selected)
        if self.selected_layout and self.btn_next.is_clicked(event):
            logger.info(f"Confirmed selection: {self.selected_layout}")
            
            photos_count = 1 if self.selected_layout == 'single' else 4
            
            switch_screen_callback('countdown', mode=self.selected_layout, total_photos=photos_count)
            return

    def update(self, dt, callback):
        # Update Live Preview
        if self.camera:
            frame = self.camera.get_latest_image()
            if frame:
                self.live_preview.update(frame)

    def draw(self, renderer):
        # 1. Clear Screen
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        self.live_preview.draw(0, 0, self.width, self.height)
        
        self.option1.draw()
        self.lbl_option1.draw()
        
        self.option2.draw()
        self.lbl_option2.draw()
        
        self.btn_next.draw()

    def on_enter(self, **context_data):
        logger.info("Entering LayoutSelectionScreen.")
        self.selected_layout = None
        self._update_ui_state()

    def on_exit(self):
        logger.info("Exiting LayoutSelectionScreen.")
