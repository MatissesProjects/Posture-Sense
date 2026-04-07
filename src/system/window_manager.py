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
        """ Determines which monitor a point (x, y) belongs to using bounding boxes. """
        for m in self.monitor_manager.monitors:
            if (m["x"] <= x < m["x"] + m["width"]) and \
               (m["y"] <= y < m["y"] + m["height"]):
                return f"monitor_{m['id']}"
        return "unknown"

    def get_ergonomic_sweet_spot(self, eye_y_normalized):
        """ 
        Calculates the 'Ergonomic Sweet Spot' (ESS) relative to the WEBCAM.
        eye_y_normalized: Vertical position of eyes in the webcam feed (0=top, 1=bottom).
        """
        layout = self.monitor_manager.get_layout_info()
        cam_pos = self.monitor_manager.get_webcam_global_pos()
        
        # Heuristic: 1 normalized unit in CV space ~ 500 pixels in vertical world space 
        # (This will be refined once physical dimensions are added)
        # eye_y_normalized=0.5 means eyes are level with the webcam.
        eye_offset_px = (eye_y_normalized - 0.5) * 500
        
        # Target Y is eye level (which is Webcam Y + eye offset)
        target_y = cam_pos["y"] + eye_offset_px
        
        return {
            "center_x": cam_pos["x"],
            "target_y": int(target_y),
            "range_y": [int(target_y), int(target_y + 250)]
        }

if __name__ == "__main__":
    from src.system.monitor_manager import MonitorManager
    m_manager = MonitorManager()
    w_manager = WindowManager(m_manager)
    print(f"Active Window: {w_manager.get_active_window_info()}")
