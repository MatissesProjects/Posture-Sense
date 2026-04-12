import unittest
from unittest.mock import MagicMock, patch
from src.system.monitor_manager import MonitorManager
from src.system.window_manager import WindowManager

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Mock monitors: Top (1920x1080 at 0,0) and Bottom (1920x1080 at 0,1080)
        self.mock_monitors = [
            MagicMock(x=0, y=0, width=1920, height=1080, name="monitor_0", is_primary=True),
            MagicMock(x=0, y=1080, width=1920, height=1080, name="monitor_1", is_primary=False)
        ]

    @patch('src.system.monitor_manager.get_monitors')
    def test_monitor_layout_detection(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        
        # Check if 2 monitors were detected
        self.assertEqual(len(manager.monitors), 2)
        # Top monitor should be at y=0
        self.assertEqual(min(m['y'] for m in manager.monitors), 0)
        # Bottom monitor should be at y=1080
        self.assertEqual(max(m['y'] for m in manager.monitors), 1080)

    @patch('src.system.monitor_manager.get_monitors')
    def test_window_identification(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        wm = WindowManager(manager)
        
        # Window at y=500 should be on monitor_0 (Top)
        self.assertEqual(wm._identify_monitor(0, 500), "monitor_0")
        # Window at y=1500 should be on monitor_1 (Bottom)
        self.assertEqual(wm._identify_monitor(0, 1500), "monitor_1")

    @patch('src.system.monitor_manager.get_monitors')
    def test_ess_calculation(self, mock_get):
        mock_get.return_value = self.mock_monitors
        manager = MonitorManager()
        # Default webcam config: anchor_monitor_index=1 (Bottom), y_offset=0
        manager.webcam_config = {
            "anchor_monitor_index": 1,
            "offset_x_pct": 0.5,
            "offset_y_px": 0
        }
        wm = WindowManager(manager)
        
        # Eye level at normalized 0.5 (level with webcam)
        # Webcam global Y is bottom monitor top edge = 1080
        ess = wm.get_ergonomic_sweet_spot(0.5)
        self.assertEqual(ess["target_y"], 1080)
        
        # Eye level at normalized 0.3 (above webcam)
        # 0.3 - 0.5 = -0.2. -0.2 * 500 = -100px.
        # Target Y = 1080 - 100 = 980
        ess = wm.get_ergonomic_sweet_spot(0.3)
        self.assertEqual(ess["target_y"], 980)

if __name__ == "__main__":
    unittest.main()
