import unittest
from unittest.mock import MagicMock, patch
from src.cv.capture import WebcamTester

class TestCV(unittest.TestCase):
    @patch('cv2.VideoCapture')
    def test_webcam_connection_success(self, mock_vc):
        """Tests that the connection succeeds when the webcam can be opened and read."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "mock_frame")
        mock_vc.return_value = mock_cap
        
        tester = WebcamTester()
        self.assertTrue(tester.test_connection())
        self.assertTrue(mock_cap.isOpened.called)
        self.assertTrue(mock_cap.read.called)
        self.assertTrue(mock_cap.release.called)

    @patch('cv2.VideoCapture')
    def test_webcam_connection_fail_not_opened(self, mock_vc):
        """Tests that the connection fails when the webcam cannot be opened."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_vc.return_value = mock_cap
        
        tester = WebcamTester()
        self.assertFalse(tester.test_connection())
        self.assertTrue(mock_cap.isOpened.called)

    @patch('cv2.VideoCapture')
    def test_webcam_connection_fail_no_frame(self, mock_vc):
        """Tests that the connection fails when no frame can be read."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_vc.return_value = mock_cap
        
        tester = WebcamTester()
        self.assertFalse(tester.test_connection())
        self.assertTrue(mock_cap.read.called)
        self.assertTrue(mock_cap.release.called)

if __name__ == "__main__":
    unittest.main()
