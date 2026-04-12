import pygetwindow as gw
import win32gui
import win32con
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

    def move_active_window(self, x, y, width=None, height=None):
        """ Moves the currently active window to a specific (x, y) coordinate. """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd: return False
            
            # Don't move if it's the desktop or taskbar
            title = win32gui.GetWindowText(hwnd)
            if not title or title in ["Program Manager", ""]: return False

            curr_x, curr_y, curr_r, curr_b = win32gui.GetWindowRect(hwnd)
            w = width if width else (curr_r - curr_x)
            h = height if height else (curr_b - curr_y)
            
            # SWP_NOSIZE if we don't want to change size
            flags = win32con.SWP_NOZORDER | win32con.SWP_NOSIZE if (not width and not height) else win32con.SWP_NOZORDER
            
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, int(x), int(y), int(w), int(h), flags)
            return True
        except Exception as e:
            logger.error(f"Failed to move window: {e}")
            return False

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
