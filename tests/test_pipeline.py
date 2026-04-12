import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from src.cv.pipeline import CVPipeline

class TestPipeline(unittest.TestCase):
    @patch('src.cv.pipeline.PoseDetector')
    @patch('src.cv.pipeline.EyeTracker')
    @patch('src.cv.pipeline.HandTracker')
    @patch('src.cv.pipeline.WorkstationAnalyzer')
    def test_process_frame_unifies_data(self, mock_wa_class, mock_ht_class, mock_et_class, mock_pd_class):
        """Tests that process_frame combines pose and eye data."""
        mock_pd = mock_pd_class.return_value
        mock_et = mock_et_class.return_value
        mock_ht = mock_ht_class.return_value
        mock_wa = mock_wa_class.return_value

        # Ensure find_pose returns the image (not a mock)
        mock_pd.find_pose.side_effect = lambda img, draw=False: img
        mock_pd.get_relevant_landmarks.return_value = {
            "nose": {"x": 0.5, "y": 0.5, "z": 0},
            "left_shoulder": {"x": 0.4, "y": 0.6, "z": 0},
            "right_shoulder": {"x": 0.6, "y": 0.6, "z": 0}
        }
        mock_et.get_iris_landmarks.return_value = {
            "left": [
                {"x": 100, "y": 100}, # 468
                {"x": 100, "y": 100}, # 469
                {"x": 100, "y": 100}, # 470
                {"x": 111.7, "y": 100}, # 471
                {"x": 100, "y": 100}  # 472
            ], 
            "right": []
        }
        mock_et.get_blink_status.return_value = {"is_blinking": False}
        mock_wa.analyze_environment.return_value = {"recommendations": []}

        pipeline = CVPipeline()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        data = pipeline.process_frame(img)

        self.assertIn("pose", data)
        self.assertIn("iris", data)
        self.assertIn("analysis", data)
        self.assertIn("environment", data)

    def test_to_json(self):
        """Tests JSON serialization."""
        pipeline = CVPipeline()
        sample_data = {"test": 123}
        json_str = pipeline.to_json(sample_data)
        self.assertEqual(json_str, '{"test": 123}')

if __name__ == "__main__":
    unittest.main()
