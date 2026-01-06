import pygame
import json
import os
from config import *
from ui.button import Button
from ui.photo_layout import PhotoLayoutPreview, PhotoFrame
from ui.live_preview import LivePreview
from .screen_interface import ScreenInterface
from utils.logger import get_logger
from ui.text_label import TextLabel

logger = get_logger("LayoutSelectionScreen")

class LayoutSelectionScreen(ScreenInterface):
    """
    Screen for selecting the photo layout, loaded from layouts.json.
    """
    
    def __init__(self, renderer, width, height, camera, layout_mgr, session_mgr):
        self.renderer = renderer
        self.width = width
        self.height = height
        self.camera = camera
        self.layout_mgr = layout_mgr
        self.session_mgr = session_mgr
        self.sizing_factor = width / 1280 
        
        # --- LIVE PREVIEW ---
        self.live_preview = LivePreview(renderer, width, height)

        # Style constants
        self.active_color = WHITE_COLOR
        self.inactive_color = (255, 255, 255, 100) # Dimmed white
        self.option_bg_color = (255, 255, 255, 150)
        self.selected_border_color = PRIMARY_COLOR 
        self.default_border_color = WHITE_COLOR
        
        self.selected_layout_id = None
        
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
        start_y = int(self.height - self.btn_next.rect.height - 20)
        self.btn_next.set_position((start_x, start_y))

        # --- LOAD LAYOUTS ---
        self.layout_options = [] # List of {'id': .., 'preview': Widget, 'label': Widget, 'data': ..}
        self.load_layouts()

    def load_layouts(self):
        """Reads layouts from LayoutManager and creates UI elements."""
        layouts_data = self.layout_mgr.get_layouts()

        num_layouts = len(layouts_data)
        if num_layouts == 0:
            return

        # Base Geometry
        base_w = 420
        base_h = 280
        spacer = 50 
        
        safe_area_w = self.width * 0.9
        
        # 1. Try with default size
        total_w = (num_layouts * base_w) + ((num_layouts - 1) * spacer)
        
        scale = 1.0
        if total_w > safe_area_w:
            scale = safe_area_w / total_width_raw if (total_width_raw := total_w) > 0 else 1.0
            total_w = safe_area_w

        # Apply sizes
        final_w = int(base_w * scale)
        final_h = int(base_h * scale)
        final_spacer = int(spacer * scale)
        
        # Center X
        start_x = (self.width - total_w) // 2
        # Center Y (Visual center slightly higher than absolute middle to leave room for button)
        opt_y = (self.height - final_h) // 2 - 20

        self.layout_options = []

        for i, layout in enumerate(layouts_data):
            # Calculate Position
            opt_x = int(start_x + i * (final_w + final_spacer))
            
            # Create Label
            lbl = TextLabel(self.renderer, layout.get("name", "Unknown").upper(), FONT_DISPLAY_SMALL, color=WHITE_COLOR)
            lbl_x = opt_x + (final_w - lbl.rect.width) // 2
            lbl_y = opt_y - lbl.rect.height - 10
            lbl.set_position((lbl_x, lbl_y))
            
            # Create Preview Widget
            preview_data = layout.get("preview", {})
            frames = []
            
            for fdata in preview_data.get("frames", []):
                fx = int(fdata.get("x") * scale)
                fy = int(fdata.get("y") * scale)
                fw = int(fdata.get("width") * scale)
                fh = int(fdata.get("height") * scale)
                
                frames.append(PhotoFrame(
                    self.renderer,
                    size=(fw, fh),
                    position=(fx, fy),
                    bg_color=self.option_bg_color,
                    text=fdata.get("text", ""),
                    image_path=fdata.get("image_path")
                ))

            # Create the Preview Container
            preview_widget = PhotoLayoutPreview(
                self.renderer,
                frames=frames,
                position=(opt_x, opt_y),
                size=(final_w, final_h),
                border_width=max(2, int(5 * scale)),
                border_color=self.inactive_color,
                bg_color=(0, 0, 0, 51)
            )

            self.layout_options.append({
                'id': layout.get("id"),
                'data': layout,
                'preview': preview_widget,
                'label': lbl
            })

    def _update_ui_state(self):
        """Updates selections."""
        for opt in self.layout_options:
            is_selected = (opt['id'] == self.selected_layout_id)
            
            widget = opt['preview']
            if is_selected:
                widget.border_color = self.active_color
                widget.bg_color = (255, 255, 255, 50)
            else:
                widget.border_color = self.inactive_color
                widget.bg_color = (0, 0, 0, 51)
            widget._update_texture()

        # Next Button
        if self.selected_layout_id:
            self.btn_next.color = self.active_color
            self.btn_next.border_color = self.active_color
        else:
            self.btn_next.color = self.inactive_color
            self.btn_next.border_color = self.inactive_color
        
        if self.btn_next.label:
            self.btn_next.label.color = self.btn_next.color
            self.btn_next.label.update_text(self.btn_next.text)
        self.btn_next._update_texture()

    def handle_event(self, event, switch_screen_callback):
        # Handle Layout Clicks
        for opt in self.layout_options:
            if opt['preview'].is_clicked(event):
                self.selected_layout_id = opt['id']
                self._update_ui_state()
                logger.info(f"Layout selected: {self.selected_layout_id}")
                return

        # Handle Next Click
        if self.selected_layout_id and self.btn_next.is_clicked(event):
            # Find data
            selected_opt = next((x for x in self.layout_options if x['id'] == self.selected_layout_id), None)
            if selected_opt:
                layout_data = selected_opt['data']
                logger.info(f"Confirmed layout: {layout_data['name']}")
                
                # Start Session
                self.session_mgr.start_session(
                    layout_id=self.selected_layout_id,
                    total_photos=layout_data.get("photo_count", 1)
                )
                
                # Switch Screen
                switch_screen_callback('countdown')

    def update(self, dt, callback):
        # Update Live Preview
        if self.camera:
            frame = self.camera.get_latest_image()
            if frame:
                self.live_preview.update(frame)

    def draw(self, renderer):
        renderer.draw_color = (0, 0, 0, 255)
        renderer.clear()
        
        self.live_preview.draw(0, 0, self.width, self.height)
        
        for opt in self.layout_options:
            opt['preview'].draw()
            opt['label'].draw()
        
        self.btn_next.draw()

    def on_enter(self, **context_data):
        logger.info("Entering LayoutSelectionScreen.")
        self.selected_layout_id = None
        self._update_ui_state()

    def on_exit(self):
        logger.info("Exiting LayoutSelectionScreen.")
