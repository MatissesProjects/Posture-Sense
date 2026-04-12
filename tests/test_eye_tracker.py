import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from src.cv.eye_tracker import EyeTracker

class TestEyeTracker(unittest.TestCase):
    @patch('mediapipe.solutions.face_mesh.FaceMesh')
    def test_find_face_mesh_calls_process(self, mock_fm_class):
        """Tests that find_face_mesh calls the MediaPipe process method."""
        mock_fm_instance = mock_fm_class.return_value
        tracker = EyeTracker()
        
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        tracker.find_face_mesh(img)
        
        self.assertTrue(mock_fm_instance.process.called)

    @patch('mediapipe.solutions.face_mesh.FaceMesh')
    def test_get_iris_landmarks(self, mock_fm_class):
        """Tests that get_iris_landmarks correctly formats iris landmarks."""
        mock_fm_instance = mock_fm_class.return_value
        
        # Mocking the results structure: results.multi_face_landmarks[0].landmark
        mock_face_landmarks = MagicMock()
        mock_landmark = MagicMock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = 0.1
        
        # Mediapipe expects at least 478 landmarks (including irises 468-477)
        mock_face_landmarks.landmark = [mock_landmark] * 478
        
        mock_results = MagicMock()
        mock_results.multi_face_landmarks = [mock_face_landmarks]
        mock_fm_instance.process.return_value = mock_results
        
        tracker = EyeTracker()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        tracker.find_face_mesh(img)
        
        iris = tracker.get_iris_landmarks(640, 480)
        self.assertEqual(len(iris["left"]), 5)
        self.assertEqual(len(iris["right"]), 5)
        # Check coordinates (0.5 * 640 = 320)
        self.assertEqual(iris["left"][0]["x"], 320.0)

    def test_get_gaze_ratio_none_if_missing(self):
        """Tests that get_gaze_ratio returns None if landmarks are missing."""
        tracker = EyeTracker()
        iris_data = {"left": [], "right": []}
        self.assertIsNone(tracker.get_gaze_ratio(iris_data, 640, 480))

if __name__ == "__main__":
    unittest.main()
