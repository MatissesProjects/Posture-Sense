import json
import os
import logging
from screeninfo import get_monitors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = "workspace_config.json"

class MonitorManager:
    """ 
    Manages the layout and relative geometry of asymmetrical stacked monitors.
    Supports persistent overrides for manual refinement.
    """
    def __init__(self):
        self.monitors = []
        self.layout_overrides = {}
        # Webcam sits on top of a specific monitor
        self.webcam_config = {
            "anchor_monitor_index": 1, # Default to the second monitor (Bottom)
            "offset_x_pct": 0.5,       # Center of the monitor
            "offset_y_px": 0           # Top edge
        }
        self.load_config()
        self.refresh_layout()

    def load_config(self):
        """ Loads manual workspace refinements from JSON. """
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    self.layout_overrides = config.get("overrides", {})
                    self.webcam_config = config.get("webcam", self.webcam_config)
                logger.info("Workspace config loaded.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")

    def save_config(self, overrides=None, webcam=None):
        """ Saves current refinements to JSON. """
        if overrides: self.layout_overrides = overrides
        if webcam: self.webcam_config = webcam
        
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump({
                    "overrides": self.layout_overrides,
                    "webcam": self.webcam_config
                }, f, indent=4)
            logger.info("Workspace config saved.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def refresh_layout(self):
        """ Detects monitors and applies manual offsets. """
        try:
            detected = get_monitors()
            self.monitors = []
            
            for i, m in enumerate(detected):
                m_dict = {
                    "id": i,
                    "name": m.name,
                    "width": m.width,
                    "height": m.height,
                    "x": m.x,
                    "y": m.y,
                    "is_primary": m.is_primary
                }
                # Apply overrides if they exist for this monitor ID/Name
                if str(i) in self.layout_overrides:
                    m_dict.update(self.layout_overrides[str(i)])
                
                self.monitors.append(m_dict)
            
            logger.info(f"Refreshed {len(self.monitors)} monitors.")
        except Exception as e:
            logger.error(f"Monitor detection failed: {e}")

    def get_layout_info(self):
        """ Returns the full workspace model for the UI. """
        return {
            "monitors": self.monitors,
            "webcam": self.webcam_config,
            "bounds": self._get_total_bounds()
        }

    def _get_total_bounds(self):
        """ Calculates the bounding box of the entire workspace. """
        if not self.monitors: return {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0}
        
        min_x = min(m["x"] for m in self.monitors)
        min_y = min(m["y"] for m in self.monitors)
        max_x = max(m["x"] + m["width"] for m in self.monitors)
        max_y = max(m["y"] + m["height"] for m in self.monitors)
        
        return {
            "min_x": min_x, "min_y": min_y, 
            "max_x": max_x, "max_y": max_y,
            "width": max_x - min_x,
            "height": max_y - min_y
        }

    def get_webcam_global_pos(self):
        """ Calculates the webcam's global pixel coordinates. """
        idx = self.webcam_config["anchor_monitor_index"]
        if idx >= len(self.monitors): return {"x": 0, "y": 0}
        
        m = self.monitors[idx]
        cam_x = m["x"] + (m["width"] * self.webcam_config["offset_x_pct"])
        cam_y = m["y"] + self.webcam_config["offset_y_px"]
        
        return {"x": int(cam_x), "y": int(cam_y)}

if __name__ == "__main__":
    mm = MonitorManager()
    print(json.dumps(mm.get_layout_info(), indent=2))
    print(f"Webcam Pos: {mm.get_webcam_global_pos()}")
