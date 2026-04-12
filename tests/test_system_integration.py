import unittest
from unittest.mock import MagicMock, patch
from src.system.monitor_manager import MonitorManager
from src.system.window_manager import WindowManager

class TestSystemIntegration(unittest.TestCase):
    @patch('src.system.monitor_manager.get_monitors')
    @patch('builtins.open', create=True)
    @patch('os.path.exists', return_value=False)
    def test_monitor_manager_detection(self, mock_exists, mock_file, mock_get_monitors):
        """Tests that monitor detection correctly identifies multiple monitors."""
        mock_monitor = MagicMock()
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_monitor.x = 0
        mock_monitor.y = 0
        mock_monitor.name = "Monitor 1"
        mock_monitor.is_primary = True
        
        mock_monitor2 = MagicMock()
        mock_monitor2.width = 1920
        mock_monitor2.height = 1080
        mock_monitor2.x = 0
        mock_monitor2.y = -1080 # Stacked above
        mock_monitor2.name = "Monitor 2"
        mock_monitor2.is_primary = False
        
        mock_get_monitors.return_value = [mock_monitor, mock_monitor2]
        
        manager = MonitorManager()
        self.assertEqual(len(manager.monitors), 2)
        self.assertEqual(manager.monitors[1]["y"], -1080)

    @patch('pygetwindow.getActiveWindow')
    def test_window_manager_info(self, mock_get_active):
        """Tests that window manager returns correct active window info."""
        mock_win = MagicMock()
        mock_win.title = "Test Window"
        mock_win.left = 100
        mock_win.top = 100
        mock_win.width = 800
        mock_win.height = 600
        mock_get_active.return_value = mock_win
        
        mock_monitor_manager = MagicMock()
        mock_monitor_manager.monitors = [{"id": 0, "x": 0, "y": 0, "width": 1920, "height": 1080}]
        
        manager = WindowManager(mock_monitor_manager)
        info = manager.get_active_window_info()
        
        self.assertEqual(info["title"], "Test Window")
        self.assertEqual(info["monitor"], "monitor_0")

    @patch('win32gui.GetForegroundWindow', return_value=12345)
    @patch('win32gui.GetWindowText', return_value="Active Window")
    @patch('win32gui.GetWindowRect', return_value=(0, 0, 800, 600))
    @patch('win32gui.SetWindowPos')
    def test_window_manager_move(self, mock_set_pos, mock_rect, mock_text, mock_fg):
        """Tests that move_active_window calls Win32 API correctly."""
        mock_monitor_manager = MagicMock()
        manager = WindowManager(mock_monitor_manager)
        
        success = manager.move_active_window(500, 500)
        self.assertTrue(success)
        self.assertTrue(mock_set_pos.called)

if __name__ == "__main__":
    unittest.main()
