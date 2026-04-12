import unittest
from src.intelligence.posture_analyzer import PostureAnalyzer

class TestPostureAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PostureAnalyzer()
        self.perfect_pose = {
            "nose": {"x": 0.5, "y": 0.3, "z": 0},
            "left_eye": {"x": 0.48, "y": 0.28, "z": 0},
            "right_eye": {"x": 0.52, "y": 0.28, "z": 0},
            "left_ear": {"x": 0.45, "y": 0.3, "z": 0},
            "right_ear": {"x": 0.55, "y": 0.3, "z": 0},
            "left_shoulder": {"x": 0.4, "y": 0.4, "z": 0},
            "right_shoulder": {"x": 0.6, "y": 0.4, "z": 0},
            "left_elbow": {"x": 0.35, "y": 0.55, "z": 0},
            "left_wrist": {"x": 0.4, "y": 0.6, "z": 0},
            "left_hip": {"x": 0.4, "y": 0.7, "z": 0},
            "right_hip": {"x": 0.6, "y": 0.7, "z": 0}
        }

    def test_perfect_posture_score(self):
        """Tests that a perfect pose (after calibration) gets a high score."""
        self.analyzer.calibrate(self.perfect_pose)
        result = self.analyzer.analyze(self.perfect_pose)
        self.assertGreaterEqual(result["score"], 90.0)

    def test_calibration(self):
        """Tests that calibration sets the baseline."""
        success = self.analyzer.calibrate(self.perfect_pose)
        self.assertTrue(success)
        self.assertIn('neutral', self.analyzer.baselines)
        self.assertEqual(self.analyzer.baselines['neutral']["nose_y"], 0.3)

    def test_slouch_after_calibration(self):
        """Tests that slouching reduces the score after calibration."""
        self.analyzer.calibrate(self.perfect_pose)
        
        slouch_pose = self.perfect_pose.copy()
        slouch_pose["nose"] = {"x": 0.5, "y": 0.35, "z": 0} # Nose dropped by 0.05
        
        result = self.analyzer.analyze(slouch_pose)
        self.assertLess(result["score"], 95.0)
        self.assertLess(result["metrics"]["slouch_score"], 95.0)

    def test_neck_tilt(self):
        """Tests that lateral neck tilt reduces the score."""
        self.analyzer.calibrate(self.perfect_pose)
        
        tilt_pose = self.perfect_pose.copy()
        tilt_pose["nose"] = {"x": 0.55, "y": 0.3, "z": 0} # Nose moved laterally
        
        result = self.analyzer.analyze(tilt_pose)
        self.assertLess(result["score"], 95.0)

    def test_shoulder_unlevel(self):
        """Tests that unlevel shoulders reduce the score."""
        self.analyzer.calibrate(self.perfect_pose)
        
        unlevel_pose = self.perfect_pose.copy()
        unlevel_pose["left_shoulder"] = {"x": 0.4, "y": 0.42, "z": 0}
        
        result = self.analyzer.analyze(unlevel_pose)
        self.assertLess(result["metrics"]["shoulder_score"], 90.0)

    def test_standing_after_calibration(self):
        """Tests sit/stand detection using calibrated baseline."""
        self.analyzer.calibrate(self.perfect_pose) # Calibrate at y=0.3
        
        # Stand up (nose moves up to y=0.1)
        standing_pose = self.perfect_pose.copy()
        standing_pose["nose"] = {"x": 0.5, "y": 0.1, "z": 0}
        
        result = self.analyzer.analyze(standing_pose)
        self.assertTrue(result["is_standing"])
        
        # Sit down (nose moves down to y=0.45)
        sitting_pose = self.perfect_pose.copy()
        sitting_pose["nose"] = {"x": 0.5, "y": 0.45, "z": 0}
        result = self.analyzer.analyze(sitting_pose)
        self.assertFalse(result["is_standing"])

    def test_empty_pose(self):
        """Tests handling of empty or insufficient pose data."""
        self.assertEqual(self.analyzer.analyze({})["score"], 0)

    def test_distance_estimation(self):
        """Tests distance estimation from iris landmarks."""
        # 11.7mm iris at 600 focal length.
        # If iris diameter is 11.7 pixels, distance should be 60cm.
        # MediaPipe iris ids: 469 (x=100), 471 (x=111.7)
        mock_iris = {
            "left": [
                {}, # 468
                {"x": 100, "y": 100}, # 469
                {}, # 470
                {"x": 111.7, "y": 100}, # 471
                {} # 472
            ]
        }
        dist = self.analyzer.estimate_distance(mock_iris)
        self.assertAlmostEqual(dist, 60.0, delta=1.0)

    def test_viewing_angle(self):
        """Tests viewing angle calculation."""
        # Eye at 500px, target at 700px, distance 40cm.
        # y_diff = 200px. y_diff_cm = 200 / 35 = 5.71cm.
        # tan(theta) = 5.71 / 40 = 0.142. theta = 8.1 degrees.
        angle = self.analyzer.calculate_viewing_angle(500, 700, 40)
        self.assertAlmostEqual(angle, 8.1, delta=0.5)


if __name__ == "__main__":
    unittest.main()
