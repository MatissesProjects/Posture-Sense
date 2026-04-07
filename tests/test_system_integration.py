import unittest
from src.system.monitor_manager import MonitorManager
from src.system.window_manager import WindowManager
from unittest.mock import MagicMock, patch

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Mock screeninfo.get_monitors
        self.mock_monitors = [
            MagicMock(x=0, y=0, width=1920, height=1080, is_primary=True),
            MagicMock(x=0, y=1080, width=1920, height=1080, is_primary=False)
        ]
        
    @patch('src.system.monitor_manager.get_monitors')
    def test_monitor_layout_detection(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        
        self.assertEqual(manager.top_monitor.y, 0)
        self.assertEqual(manager.bottom_monitor.y, 1080)
        
        layout = manager.get_layout_info()
        self.assertEqual(layout["total_height"], 2160)
        self.assertEqual(layout["top"]["height"], 1080)

    @patch('src.system.monitor_manager.get_monitors')
    def test_coordinate_conversion(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        
        # Center of the stack (0.5, 0.5) should be (960, 1080)
        coords = manager.get_screen_coords(0.5, 0.5)
        self.assertEqual(coords["x"], 960)
        self.assertEqual(coords["y"], 1080)

    @patch('src.system.monitor_manager.get_monitors')
    def test_window_identification(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        wm = WindowManager(manager)
        
        # Window at y=500 should be on "top" monitor
        self.assertEqual(wm._identify_monitor(0, 500), "top")
        
        # Window at y=1500 should be on "bottom" monitor
        self.assertEqual(wm._identify_monitor(0, 1500), "bottom")
        
        # Window at y=3000 should be "unknown"
        self.assertEqual(wm._identify_monitor(0, 3000), "unknown")

    @patch('src.system.monitor_manager.get_monitors')
    def test_ess_calculation(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        wm = WindowManager(manager)
        
        # Eye level at normalized 0.3 (roughly top monitor middle)
        # 0.3 * 2160 = 648
        ess = wm.get_ergonomic_sweet_spot(0.3)
        self.assertEqual(ess["target_y"], 648)
        self.assertEqual(ess["center_x"], 960)

if __name__ == "__main__":
    unittest.main()
