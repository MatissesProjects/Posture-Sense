import pygetwindow as gw
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowManager:
    """ Tracks the active window and its position relative to the workspace. """
    def __init__(self, monitor_manager):
        self.monitor_manager = monitor_manager
        self.last_active_window = None

    def get_active_window_info(self):
        """ Returns details about the currently focused window. """
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return None
            
            self.last_active_window = active_window
            
            # Get basic info
            info = {
                "title": active_window.title,
                "x": active_window.left,
                "y": active_window.top,
                "width": active_window.width,
                "height": active_window.height,
                "monitor": self._identify_monitor(active_window.left, active_window.top)
            }
            return info
        except Exception as e:
            # logger.error(f"Error tracking active window: {e}")
            return None

    def _identify_monitor(self, x, y):
        """ Determines which monitor a point (x, y) belongs to. """
        top = self.monitor_manager.top_monitor
        bottom = self.monitor_manager.bottom_monitor
        
        if top and (top.y <= y < top.y + top.height):
            return "top"
        if bottom and (bottom.y <= y < bottom.y + bottom.height):
            return "bottom"
        return "unknown"

    def get_ergonomic_sweet_spot(self, eye_y_normalized):
        """ 
        Calculates the 'Ergonomic Sweet Spot' (ESS) on the screen 
        based on the user's eye level.
        Guidelines: Top of text should be at eye level or slightly below (15-30 deg).
        """
        layout = self.monitor_manager.get_layout_info()
        if not layout["top"] or not layout["bottom"]:
            return None
        
        # Total height of the stack
        total_h = layout["total_height"]
        
        # Convert normalized eye Y to global pixel Y
        # Note: In CV, Y=0 is top. In Screen, Y=0 is top of TOP monitor.
        eye_y_pixel = eye_y_normalized * total_h
        
        # ESS is typically at eye level (y) and centered horizontally (x)
        # We suggest a range: eye_y_pixel to eye_y_pixel + 200px
        return {
            "center_x": layout["top"]["width"] // 2,
            "target_y": int(eye_y_pixel),
            "range_y": [int(eye_y_pixel), int(eye_y_pixel + 300)]
        }

if __name__ == "__main__":
    from src.system.monitor_manager import MonitorManager
    m_manager = MonitorManager()
    w_manager = WindowManager(m_manager)
    print(f"Active Window: {w_manager.get_active_window_info()}")
