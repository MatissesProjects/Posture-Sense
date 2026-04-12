import json
import os
import datetime
import logging

from src.intelligence.database_manager import DatabaseManager
from src.intelligence.fatigue_predictor import FatiguePredictor
from src.intelligence.transition_predictor import TransitionPredictor
from src.intelligence.gaze_analyzer import GazeAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATS_PATH = "user_stats.json"

class StatsManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.fatigue_predictor = FatiguePredictor()
        self.transition_predictor = TransitionPredictor()
        self.gaze_analyzer = GazeAnalyzer()
        self.last_train_time = 0
        self.stats = {
            "daily_history": {}, 
            "current_streak": 0,
            "last_active_date": None,
            "total_ergonomic_minutes": 0,
            "first_seen_date": None
        }
        self.load_stats()
        if not self.stats.get("first_seen_date"):
            self.stats["first_seen_date"] = datetime.date.today().isoformat()
            self.save_stats()

    def load_stats(self):
        if os.path.exists(STATS_PATH):
            try:
                with open(STATS_PATH, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")

    def save_stats(self):
        try:
            with open(STATS_PATH, 'w') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def record_minute(self, analysis_data, gaze_data=None):
        """ Records performance for a single minute. """
        today = datetime.date.today().isoformat()
        score = analysis_data.get("score", 0)
        
        # Log to Database
        self.db_manager.log_metrics(analysis_data)
        self.transition_predictor.update(analysis_data.get('is_standing', False), score)
        if gaze_data:
            self.gaze_analyzer.update(gaze_data)
        
        if today not in self.stats["daily_history"]:
            self.stats["daily_history"][today] = {"total_score": 0, "entries": 0, "ergonomic_minutes": 0}
            self._update_streak(today)

        day_data = self.stats["daily_history"][today]
        day_data["total_score"] += score
        day_data["entries"] += 1
        
        if score >= 85:
            day_data["ergonomic_minutes"] += 1
            self.stats["total_ergonomic_minutes"] += 1
        
        self.save_stats()

    def _update_streak(self, today_str):
        if self.stats["last_active_date"]:
            last_date = datetime.date.fromisoformat(self.stats["last_active_date"])
            today = datetime.date.fromisoformat(today_str)
            delta = (today - last_date).days
            
            if delta == 1:
                self.stats["current_streak"] += 1
            elif delta > 1:
                self.stats["current_streak"] = 1
        else:
            self.stats["current_streak"] = 1
            
        self.stats["last_active_date"] = today_str

    def get_app_age_days(self):
        first_date = datetime.date.fromisoformat(self.stats["first_seen_date"])
        return (datetime.date.today() - first_date).days

    def generate_daily_report(self):
        """ Generates a summary report for the current day. """
        summary = self.get_summary()
        today = datetime.date.today().isoformat()
        
        report = {
            "date": today,
            "overall_avg_score": summary["today_avg_score"],
            "ergonomic_minutes": summary["today_ergonomic_minutes"],
            "streak": summary["streak"],
            "status": "Healthy" if summary["today_avg_score"] > 80 else "Needs Improvement",
            "recommendation": "Maintain neutral neck position." if summary["today_avg_score"] < 80 else "Excellent work!"
        }
        
        # Save report to a separate log
        try:
            with open(f"reports/report_{today}.json", "w") as f:
                json.dump(report, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save daily report: {e}")
            
        return report

    def get_summary(self, current_score=None):
        today = datetime.date.today().isoformat()
        day_data = self.stats["daily_history"].get(today, {"total_score": 0, "entries": 0, "ergonomic_minutes": 0})
        
        avg_score = day_data["total_score"] / day_data["entries"] if day_data["entries"] > 0 else 0
        
        # Periodic Model Training (every 60 minutes)
        import time
        now = time.time()
        if now - self.last_train_time > 3600:
            if self.fatigue_predictor.train():
                self.last_train_time = now

        # Calculate short-term moving averages from database
        recent_logs = self.db_manager.get_recent_history(limit=60)
        avg_5m = sum(l[2] for l in recent_logs[:5]) / min(5, len(recent_logs)) if len(recent_logs) > 0 else avg_score
        avg_15m = sum(l[2] for l in recent_logs[:15]) / min(15, len(recent_logs)) if len(recent_logs) > 0 else avg_score
        avg_60m = sum(l[2] for l in recent_logs[:60]) / min(60, len(recent_logs)) if len(recent_logs) > 0 else avg_score

        fatigue_prediction = None
        if current_score is not None:
            # Pass all features for advanced prediction
            prediction_features = {
                "score": current_score,
                "avg_15m": avg_15m,
                "slump_freq_5m": sum(1 for l in recent_logs[:5] if l[2] < 70)
            }
            fatigue_prediction = self.fatigue_predictor.predict_slump(prediction_features)

        return {
            "streak": self.stats["current_streak"],
            "today_avg_score": round(avg_score, 1),
            "avg_5m": round(avg_5m, 1),
            "avg_15m": round(avg_15m, 1),
            "avg_60m": round(avg_60m, 1),
            "today_ergonomic_minutes": day_data["ergonomic_minutes"],
            "total_ergonomic_minutes": self.stats["total_ergonomic_minutes"],
            "fatigue_prediction": fatigue_prediction,
            "transition_data": self.transition_predictor.get_predictions(),
            "recovery_boost": self.transition_predictor.calculate_recovery_boost(),
            "gaze_stats": self.gaze_analyzer.get_distribution_stats()
        }
