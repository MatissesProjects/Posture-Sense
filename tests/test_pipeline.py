import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import json
from src.cv.pipeline import CVPipeline

class TestPipeline(unittest.TestCase):
    @patch('src.cv.pipeline.PoseDetector')
    @patch('src.cv.pipeline.EyeTracker')
    def test_process_frame_unifies_data(self, mock_et_class, mock_pd_class):
        """Tests that process_frame combines pose and eye data."""
        mock_pd = mock_pd_class.return_value
        mock_et = mock_et_class.return_value
        
        mock_pd.get_relevant_landmarks.return_value = [{"id": 0, "x": 0.5}]
        mock_et.get_iris_landmarks.return_value = {"left": [{"id": 468, "x": 100}], "right": []}
        
        pipeline = CVPipeline()
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        data = pipeline.process_frame(img)
        
        self.assertIn("pose", data)
        self.assertIn("iris", data)
        self.assertIn("resolution", data)
        self.assertEqual(data["pose"][0]["id"], 0)
        self.assertEqual(data["iris"]["left"][0]["id"], 468)

    def test_to_json_serializes_correctly(self):
        """Tests that to_json returns a valid JSON string."""
        pipeline = CVPipeline()
        data = {"test": 123}
        json_str = pipeline.to_json(data)
        self.assertEqual(json_str, '{"test": 123}')

if __name__ == "__main__":
    unittest.main()
