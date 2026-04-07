from screeninfo import get_monitors
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorManager:
    """ Manages the layout and relative geometry of stacked monitors. """
    def __init__(self):
        self.monitors = []
        self.top_monitor = None
        self.bottom_monitor = None
        self.webcam_position = "monitor_top" # Default: webcam sits on top of the upper monitor
        self.refresh_layout()

    def refresh_layout(self):
        """ Detects and categorizes monitors by vertical position. """
        try:
            self.monitors = get_monitors()
            if len(self.monitors) < 2:
                logger.warning("Fewer than 2 monitors detected. Stacked layout features may be limited.")
            
            # Sort by Y-coordinate (Top to Bottom)
            sorted_m = sorted(self.monitors, key=lambda m: m.y)
            self.top_monitor = sorted_m[0]
            if len(sorted_m) > 1:
                self.bottom_monitor = sorted_m[1]
            
            logger.info(f"Monitor layout refreshed: Top={self.top_monitor.width}x{self.top_monitor.height}, Bottom={self.bottom_monitor.width if self.bottom_monitor else 'None'}")
        except Exception as e:
            logger.error(f"Error detecting monitors: {e}")

    def get_layout_info(self):
        """ Returns a JSON-serializable representation of the workspace layout. """
        return {
            "top": self._m_to_dict(self.top_monitor),
            "bottom": self._m_to_dict(self.bottom_monitor),
            "webcam_position": self.webcam_position,
            "total_height": (self.top_monitor.height + self.bottom_monitor.height) if self.top_monitor and self.bottom_monitor else 0
        }

    def _m_to_dict(self, m):
        if not m: return None
        return {"x": m.x, "y": m.y, "width": m.width, "height": m.height, "is_primary": m.is_primary}

    def get_screen_coords(self, normalized_x, normalized_y):
        """ 
        Converts normalized coordinates (from CV Engine) 
        to global pixel coordinates across the stacked monitors.
        Assumes normalized coordinates span the entire vertical stack.
        """
        if not self.top_monitor or not self.bottom_monitor:
            return None
        
        total_h = self.top_monitor.height + self.bottom_monitor.height
        global_y = normalized_y * total_h
        global_x = normalized_x * self.top_monitor.width # Assumes same width
        
        return {"x": int(global_x), "y": int(global_y)}

if __name__ == "__main__":
    manager = MonitorManager()
    print(manager.get_layout_info())
