import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from src.cv.pose_detector import PoseDetector

class TestPoseDetector(unittest.TestCase):
    @patch('mediapipe.solutions.pose.Pose')
    def test_find_pose_calls_process(self, mock_pose_class):
        """Tests that find_pose calls the MediaPipe process method."""
        mock_pose_instance = mock_pose_class.return_value
        detector = PoseDetector()
        
        # Create a mock image (3 channel, uint8)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        detector.find_pose(img, draw=False)
        
        self.assertTrue(mock_pose_instance.process.called)

    @patch('mediapipe.solutions.pose.Pose')
    def test_get_landmarks_returns_list(self, mock_pose_class):
        """Tests that get_landmarks correctly formats landmarks."""
        mock_pose_instance = mock_pose_class.return_value
        
        # Mocking the results structure: results.pose_landmarks.landmark
        mock_landmarks = MagicMock()
        mock_landmark = MagicMock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = 0.1
        mock_landmark.visibility = 0.9
        
        # Mediapipe expects a sequence of landmarks
        mock_landmarks.landmark = [mock_landmark] * 33
        
        mock_results = MagicMock()
        mock_results.pose_landmarks = mock_landmarks
        mock_pose_instance.process.return_value = mock_results
        
        detector = PoseDetector()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        detector.find_pose(img, draw=False)
        
        lms = detector.get_landmarks()
        self.assertEqual(len(lms), 33)
        self.assertEqual(lms[0]['x'], 0.5)
        self.assertEqual(lms[0]['visibility'], 0.9)

    @patch('mediapipe.solutions.pose.Pose')
    def test_get_relevant_landmarks(self, mock_pose_class):
        """Tests that get_relevant_landmarks returns the correct subset of landmarks."""
        mock_pose_instance = mock_pose_class.return_value
        mock_landmarks = MagicMock()
        mock_landmark_template = MagicMock()
        mock_landmark_template.x = 0.5
        mock_landmark_template.y = 0.5
        mock_landmark_template.z = 0.1
        mock_landmark_template.visibility = 1.0
        
        mock_landmarks.landmark = [mock_landmark_template] * 33
        mock_results = MagicMock()
        mock_results.pose_landmarks = mock_landmarks
        mock_pose_instance.process.return_value = mock_results
        
        detector = PoseDetector()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        detector.find_pose(img, draw=False)
        
        relevant_lms = detector.get_relevant_landmarks()
        # Should be 9 landmarks (IDs: 0-6, 11, 12)
        self.assertEqual(len(relevant_lms), 9)

if __name__ == "__main__":
    unittest.main()
