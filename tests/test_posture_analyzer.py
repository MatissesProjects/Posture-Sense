import unittest
from src.intelligence.posture_analyzer import PostureAnalyzer

class TestPostureAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PostureAnalyzer()
        # IDs: 0=Nose, 11=L-Shoulder (index 7), 12=R-Shoulder (index 8)
        self.perfect_pose = [
            {"id": 0, "x": 0.5, "y": 0.3}, # Nose
            {"id": 1, "x": 0.5, "y": 0.3}, # 1-6
            {"id": 2, "x": 0.5, "y": 0.3},
            {"id": 3, "x": 0.5, "y": 0.3},
            {"id": 4, "x": 0.5, "y": 0.3},
            {"id": 5, "x": 0.5, "y": 0.3},
            {"id": 6, "x": 0.5, "y": 0.3},
            {"id": 11, "x": 0.4, "y": 0.4}, # L-Shoulder
            {"id": 12, "x": 0.6, "y": 0.4}  # R-Shoulder
        ]

    def test_perfect_posture_score(self):
        """Tests that a perfect pose gets a score of 100."""
        result = self.analyzer.analyze(self.perfect_pose)
        self.assertEqual(result["score"], 100.0)

    def test_calibration(self):
        """Tests that calibration sets the baseline."""
        success = self.analyzer.calibrate(self.perfect_pose)
        self.assertTrue(success)
        self.assertIsNotNone(self.analyzer.baseline)
        self.assertEqual(self.analyzer.baseline["nose_y"], 0.3)

    def test_slouch_after_calibration(self):
        """Tests that slouching reduces the score after calibration."""
        self.analyzer.calibrate(self.perfect_pose)
        
        slouch_pose = list(self.perfect_pose)
        slouch_pose[0] = {"id": 0, "x": 0.5, "y": 0.35} # Nose dropped by 0.05
        
        result = self.analyzer.analyze(slouch_pose)
        self.assertLess(result["score"], 100.0)
        self.assertLess(result["metrics"]["slouch_score"], 100.0)

    def test_standing_after_calibration(self):
        """Tests sit/stand detection using calibrated baseline."""
        self.analyzer.calibrate(self.perfect_pose) # Calibrate at y=0.3
        
        # Stand up (nose moves up to y=0.1)
        standing_pose = list(self.perfect_pose)
        standing_pose[0] = {"id": 0, "x": 0.5, "y": 0.1}
        
        result = self.analyzer.analyze(standing_pose)
        self.assertTrue(result["is_standing"])
        
        # Sit down (nose moves down to y=0.5)
        sitting_pose = list(self.perfect_pose)
        sitting_pose[0] = {"id": 0, "x": 0.5, "y": 0.5}
        result = self.analyzer.analyze(sitting_pose)
        self.assertFalse(result["is_standing"])

    def test_empty_pose(self):
        """Tests handling of empty or insufficient pose data."""
        self.assertEqual(self.analyzer.analyze([])["score"], 0)

if __name__ == "__main__":
    unittest.main()
