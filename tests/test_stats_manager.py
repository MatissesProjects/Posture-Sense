import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
from src.intelligence.stats_manager import StatsManager

class TestStatsManager(unittest.TestCase):
    @patch('src.intelligence.stats_manager.DatabaseManager')
    @patch('src.intelligence.stats_manager.FatiguePredictor')
    @patch('src.intelligence.stats_manager.TransitionPredictor')
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    @patch('os.path.exists', return_value=True)
    def setUp(self, mock_exists, mock_file, mock_tp, mock_fp, mock_db):
        self.stats_manager = StatsManager()
        # Ensure stats dictionary is fully initialized even with empty mock file
        self.stats_manager.stats = {
            "daily_history": {}, 
            "current_streak": 0,
            "last_active_date": None,
            "total_ergonomic_minutes": 0,
            "first_seen_date": "2026-01-01"
        }
        self.stats_manager.db_manager = mock_db.return_value
        self.stats_manager.fatigue_predictor = mock_fp.return_value
        self.stats_manager.transition_predictor = mock_tp.return_value

    def test_record_minute_updates_day_data(self):
        """Tests that record_minute correctly updates daily score and ergonomic minutes."""
        # Initial score 90 (ergonomic)
        self.stats_manager.record_minute({"score": 90, "is_standing": False})
        
        from datetime import date
        today = date.today().isoformat()
        
        self.assertIn(today, self.stats_manager.stats["daily_history"])
        day_data = self.stats_manager.stats["daily_history"][today]
        self.assertEqual(day_data["entries"], 1)
        self.assertEqual(day_data["ergonomic_minutes"], 1)
        self.assertEqual(self.stats_manager.stats["total_ergonomic_minutes"], 1)

    def test_record_minute_low_score(self):
        """Tests that low scores don't increase ergonomic minutes."""
        self.stats_manager.record_minute({"score": 50, "is_standing": False})
        
        from datetime import date
        today = date.today().isoformat()
        day_data = self.stats_manager.stats["daily_history"][today]
        self.assertEqual(day_data["ergonomic_minutes"], 0)

    def test_streak_update_new_day(self):
        """Tests that the streak is updated correctly for a new day."""
        from datetime import date, timedelta
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        self.stats_manager.stats["last_active_date"] = yesterday
        self.stats_manager.stats["current_streak"] = 5
        
        today = date.today().isoformat()
        self.stats_manager._update_streak(today)
        
        self.assertEqual(self.stats_manager.stats["current_streak"], 6)
        self.assertEqual(self.stats_manager.stats["last_active_date"], today)

    def test_streak_reset_after_gap(self):
        """Tests that the streak resets after more than 1 day of inactivity."""
        from datetime import date, timedelta
        long_ago = (date.today() - timedelta(days=3)).isoformat()
        
        self.stats_manager.stats["last_active_date"] = long_ago
        self.stats_manager.stats["current_streak"] = 10
        
        today = date.today().isoformat()
        self.stats_manager._update_streak(today)
        
        self.assertEqual(self.stats_manager.stats["current_streak"], 1)

if __name__ == "__main__":
    unittest.main()
