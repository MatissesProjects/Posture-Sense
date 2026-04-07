import unittest
from src.intelligence.posture_analyzer import PostureAnalyzer

class TestPostureAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PostureAnalyzer()
        self.perfect_pose = {
            "nose": {"x": 0.5, "y": 0.3},
            "left_shoulder": {"x": 0.4, "y": 0.4},
            "right_shoulder": {"x": 0.6, "y": 0.4},
            "left_elbow": {"x": 0.35, "y": 0.55},
            "left_wrist": {"x": 0.4, "y": 0.6},
            "left_hip": {"x": 0.4, "y": 0.7},
            "right_hip": {"x": 0.6, "y": 0.7}
        }

    def test_perfect_posture_score(self):
        """Tests that a perfect pose (after calibration) gets a high score."""
        self.analyzer.calibrate(self.perfect_pose)
        result = self.analyzer.analyze(self.perfect_pose)
        self.assertGreaterEqual(result["score"], 95.0)

    def test_calibration(self):
        """Tests that calibration sets the baseline."""
        success = self.analyzer.calibrate(self.perfect_pose)
        self.assertTrue(success)
        self.assertIsNotNone(self.analyzer.baseline)
        self.assertEqual(self.analyzer.baseline["nose_y"], 0.3)

    def test_slouch_after_calibration(self):
        """Tests that slouching reduces the score after calibration."""
        self.analyzer.calibrate(self.perfect_pose)
        
        slouch_pose = self.perfect_pose.copy()
        slouch_pose["nose"] = {"x": 0.5, "y": 0.35} # Nose dropped by 0.05
        
        result = self.analyzer.analyze(slouch_pose)
        self.assertLess(result["score"], 90.0)
        self.assertLess(result["metrics"]["slouch_score"], 90.0)

    def test_neck_tilt(self):
        """Tests that lateral neck tilt reduces the score."""
        self.analyzer.calibrate(self.perfect_pose)
        
        tilt_pose = self.perfect_pose.copy()
        tilt_pose["nose"] = {"x": 0.55, "y": 0.3} # Nose moved laterally
        
        result = self.analyzer.analyze(tilt_pose)
        self.assertLess(result["score"], 95.0)

    def test_shoulder_unlevel(self):
        """Tests that unlevel shoulders reduce the score."""
        self.analyzer.calibrate(self.perfect_pose)
        
        unlevel_pose = self.perfect_pose.copy()
        unlevel_pose["left_shoulder"] = {"x": 0.4, "y": 0.42}
        
        result = self.analyzer.analyze(unlevel_pose)
        self.assertLess(result["score"], 95.0)

    def test_standing_after_calibration(self):
        """Tests sit/stand detection using calibrated baseline."""
        self.analyzer.calibrate(self.perfect_pose) # Calibrate at y=0.3
        
        # Stand up (nose moves up to y=0.1)
        standing_pose = self.perfect_pose.copy()
        standing_pose["nose"] = {"x": 0.5, "y": 0.1}
        
        result = self.analyzer.analyze(standing_pose)
        self.assertTrue(result["is_standing"])
        
        # Sit down (nose moves down to y=0.45)
        sitting_pose = self.perfect_pose.copy()
        sitting_pose["nose"] = {"x": 0.5, "y": 0.45}
        result = self.analyzer.analyze(sitting_pose)
        self.assertFalse(result["is_standing"])

    def test_empty_pose(self):
        """Tests handling of empty or insufficient pose data."""
        self.assertEqual(self.analyzer.analyze({})["score"], 0)

if __name__ == "__main__":
    unittest.main()
