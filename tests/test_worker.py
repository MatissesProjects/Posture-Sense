import unittest
from unittest.mock import MagicMock, patch
from src.cv.worker import CVWorker

class TestWorker(unittest.TestCase):
    @patch('src.cv.worker.CVPipeline')
    @patch('src.cv.worker.MonitorManager')
    @patch('src.cv.worker.WindowManager')
    @patch('src.cv.worker.StatsManager')
    @patch('src.cv.worker.NotificationManager')
    def setUp(self, mock_nm, mock_sm, mock_wm, mock_mm, mock_cp):
        self.worker = CVWorker()

    def test_toggle_mirror(self):
        """Tests that toggle_mirror changes the state."""
        initial = self.worker.mirror_mode
        self.worker.toggle_mirror()
        self.assertNotEqual(initial, self.worker.mirror_mode)

    def test_toggle_privacy(self):
        """Tests that toggle_privacy changes the state."""
        initial = self.worker.privacy_mode
        self.worker.toggle_privacy()
        self.assertNotEqual(initial, self.worker.privacy_mode)

    def test_toggle_auto_align(self):
        """Tests that toggle_auto_align changes the state."""
        initial = self.worker.auto_align
        self.worker.toggle_auto_align()
        self.assertNotEqual(initial, self.worker.auto_align)

    def test_get_layout_info(self):
        """Tests that get_layout_info includes mirror_mode."""
        self.worker.monitor_manager.get_layout_info.return_value = {"monitors": []}
        info = self.worker.get_layout_info()
        self.assertIn("mirror_mode", info)
        self.assertIn("monitors", info)

if __name__ == "__main__":
    unittest.main()
