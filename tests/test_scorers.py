import unittest
from src.intelligence.rula_scorer import RULAScorer
from src.intelligence.reba_scorer import REBAScorer

class TestScorers(unittest.TestCase):
    def setUp(self):
        self.rula = RULAScorer()
        self.reba = REBAScorer()
        self.neutral_pose = {
            "nose": {"x": 0.5, "y": 0.3},
            "left_shoulder": {"x": 0.4, "y": 0.4},
            "right_shoulder": {"x": 0.6, "y": 0.4},
            "left_hip": {"x": 0.45, "y": 0.7},
            "right_hip": {"x": 0.55, "y": 0.7},
            "left_elbow": {"x": 0.35, "y": 0.55},
            "left_wrist": {"x": 0.4, "y": 0.6}
        }

    def test_rula_neutral_score(self):
        """Tests RULA scoring for a neutral pose."""
        result = self.rula.get_grand_score(self.neutral_pose)
        self.assertIn("grand_score", result)
        self.assertLessEqual(result["grand_score"], 3)
        self.assertEqual(result["risk_level"], "Negligible Risk")

    def test_rula_severe_tilt(self):
        """Tests RULA scoring for a severe neck tilt."""
        tilted_pose = self.neutral_pose.copy()
        tilted_pose["nose"] = {"x": 0.7, "y": 0.3} # Severe lateral tilt
        result = self.rula.get_grand_score(tilted_pose)
        self.assertGreater(result["breakdown"]["neck"], 1)

    def test_reba_neutral_score(self):
        """Tests REBA scoring for a neutral pose."""
        result = self.reba.get_grand_score(self.neutral_pose)
        self.assertIn("grand_score", result)
        # REBA 1 is 'Negligible'
        self.assertEqual(result["grand_score"], 1)
        self.assertEqual(result["risk_level"], "Negligible")

    def test_reba_trunk_flexion(self):
        """Tests REBA trunk score increases with flexion."""
        flexed_pose = self.neutral_pose.copy()
        flexed_pose["left_shoulder"] = {"x": 0.45, "y": 0.5} # Leaning forward
        flexed_pose["right_shoulder"] = {"x": 0.65, "y": 0.5}
        result = self.reba.get_grand_score(flexed_pose)
        self.assertGreaterEqual(result["breakdown"]["trunk"], 2)

if __name__ == "__main__":
    unittest.main()
