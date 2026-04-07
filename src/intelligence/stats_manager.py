import json
import os
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATS_PATH = "user_stats.json"

class StatsManager:
    def __init__(self):
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

    def get_app_age_days(self):
        first_date = datetime.date.fromisoformat(self.stats["first_seen_date"])
        return (datetime.date.today() - first_date).days

    def get_summary(self):

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

    def record_minute(self, score):
        """ Records performance for a single minute. """
        today = datetime.date.today().isoformat()
        
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

    def get_summary(self):
        today = datetime.date.today().isoformat()
        day_data = self.stats["daily_history"].get(today, {"total_score": 0, "entries": 0, "ergonomic_minutes": 0})
        
        avg_score = day_data["total_score"] / day_data["entries"] if day_data["entries"] > 0 else 0
        
        return {
            "streak": self.stats["current_streak"],
            "today_avg_score": round(avg_score, 1),
            "today_ergonomic_minutes": day_data["ergonomic_minutes"],
            "total_ergonomic_minutes": self.stats["total_ergonomic_minutes"]
        }
