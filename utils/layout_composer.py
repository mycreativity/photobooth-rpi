from PIL import Image, ImageOps
import os
import json
import datetime
from utils.layout_manager import LayoutManager
from utils.logger import get_logger

logger = get_logger("LayoutComposer")

class LayoutComposer:
    def __init__(self, output_dir="photos/composed"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.layout_mgr = LayoutManager()

    def compose(self, mode, photo_paths):
        """
        Composes multiple photos into a single layout image based on layouts.json definition.
        
        Args:
            mode (str): Layout ID (e.g. 'single', 'collage')
            photo_paths (list): List of absolute paths to the source photos.
            
        Returns:
            str: Path to the generated composed image.
        """
        if not photo_paths:
            logger.error("No photos provided for composition.")
            return None

        # Retrieve Layout Config
        layout_config = self.layout_mgr.get_layout(mode)
        if not layout_config:
            logger.error(f"Unknown layout mode '{mode}'. fallback to single.")
            # Fallback
            # layout_config = ... (could define default)
            return None

        CANVAS_WIDTH = layout_config.get("canvas_width", 1800)
        CANVAS_HEIGHT = layout_config.get("canvas_height", 1200)
        BACKGROUND_COLOR = (255, 255, 255) 
        
        canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
        
        slots = layout_config.get("slots", [])
        
        for i, slot in enumerate(slots):
            # If we run out of photos, just reuse the last one or stop?
            # Reusing last is safer to avoid gaps.
            p_idx = min(i, len(photo_paths) - 1)
            
            path = photo_paths[p_idx]
            try:
                source_img = Image.open(path)
                
                target_w = slot.get('width')
                target_h = slot.get('height')
                target_x = slot.get('x')
                target_y = slot.get('y')
                
                # Crop/Resize image to fill the slot
                cropped_img = ImageOps.fit(
                    source_img, 
                    (target_w, target_h), 
                    method=Image.Resampling.LANCZOS
                )
                
                canvas.paste(cropped_img, (target_x, target_y))
                
            except Exception as e:
                logger.error(f"Failed to process image {path} for slot {i}: {e}")
        
        # Save Result
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"composed_{mode}_{timestamp}.jpg"
        output_path = os.path.join(self.output_dir, filename)
        
        canvas.save(output_path, "JPEG", quality=95)
        logger.info(f"Composed image saved to {output_path}")
        
        return output_path
