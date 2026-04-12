import unittest
from unittest.mock import MagicMock, patch
from src.intelligence.fatigue_predictor import FatiguePredictor
from src.intelligence.transition_predictor import TransitionPredictor

class TestPredictors(unittest.TestCase):
    def setUp(self):
        # Mock database for FatiguePredictor
        self.patcher = patch('sqlite3.connect')
        self.mock_conn = self.patcher.start()
        self.fatigue = FatiguePredictor(db_path=":memory:")
        self.transition = TransitionPredictor()

    def tearDown(self):
        self.patcher.stop()

    def test_fatigue_predictor_not_trained(self):
        """Tests that fatigue predictor handles untrained state gracefully."""
        prediction = self.fatigue.predict_slump({"avg_15m": 80})
        self.assertFalse(prediction["imminent"])
        self.assertEqual(prediction["confidence"], 0)

    @patch('pandas.read_sql_query')
    def test_fatigue_predictor_train_insufficient_data(self, mock_read_sql):
        """Tests that training fails with insufficient data."""
        import pandas as pd
        mock_read_sql.return_value = pd.DataFrame(columns=['timestamp', 'score', 'slouch_duration', 'raw_metrics_json'])
        success = self.fatigue.train()
        self.assertFalse(success)

    def test_transition_predictor_cold_start(self):
        """Tests transition predictor default values for cold start."""
        # Start sitting
        self.transition.update(is_standing=False, current_score=90)
        preds = self.transition.get_predictions()
        self.assertEqual(preds["current_mode"], "sitting")
        self.assertEqual(preds["limit_minutes"], 50)
        self.assertGreaterEqual(preds["remaining_minutes"], 0)

    def test_transition_predictor_mode_change(self):
        """Tests that mode change resets active session and records decay data."""
        # Start sitting
        self.transition.update(is_standing=False, current_score=90)
        # Change to standing
        self.transition.update(is_standing=True, current_score=85)
        
        self.assertEqual(len(self.transition.decay_data["sitting"]), 1)
        self.assertEqual(self.transition.active_session["mode"], "standing")
        
        preds = self.transition.get_predictions()
        self.assertEqual(preds["current_mode"], "standing")
        self.assertEqual(preds["limit_minutes"], 25)

if __name__ == "__main__":
    unittest.main()
