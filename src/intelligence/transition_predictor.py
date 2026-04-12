import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

class TransitionPredictor:
    """
    Analyzes how long a user can maintain good posture in sitting vs standing modes.
    Predicts when a transition is needed to prevent strain.
    """
    def __init__(self):
        self.decay_data = {
            "sitting": [], # list of (duration_minutes, end_score)
            "standing": []
        }
        self.active_session = {
            "mode": None,
            "start_time": None,
            "scores": []
        }
        self.critical_threshold = 75 # Score below which we consider the user "fatigued"

    def update(self, is_standing, current_score):
        """ Tracks real-time mode-specific decay. """
        now = time.time()
        mode = "standing" if is_standing else "sitting"
        
        # Mode changed?
        if self.active_session["mode"] != mode:
            if self.active_session["mode"] is not None:
                # Close out previous session
                duration = (now - self.active_session["start_time"]) / 60
                self.decay_data[self.active_session["mode"]].append({
                    "duration": duration,
                    "avg_score": np.mean(self.active_session["scores"]) if self.active_session["scores"] else 100,
                    "end_score": current_score
                })
            
            # Start new session
            self.active_session = {
                "mode": mode,
                "start_time": now,
                "scores": [current_score]
            }
        else:
            self.active_session["scores"].append(current_score)

    def get_predictions(self):
        """ Returns predicted time remaining in current mode. """
        if not self.active_session["mode"]: return {}
        
        mode = self.active_session["mode"]
        current_duration = (time.time() - self.active_session["start_time"]) / 60
        
        # Calculate typical duration before slump for this mode
        past_sessions = self.decay_data[mode]
        if len(past_sessions) < 3:
            # Cold start: defaults based on ergonomic literature
            # Sit: 45-60m, Stand: 20-30m
            limit = 50 if mode == "sitting" else 25
        else:
            # Average duration where score stayed above critical
            limit = np.mean([s["duration"] for s in past_sessions if s["end_score"] >= self.critical_threshold - 5])
            # Cap it to sane defaults if data is noisy
            limit = np.clip(limit, 15, 90)

        remaining = max(0, limit - current_duration)
        
        return {
            "current_mode": mode,
            "duration_minutes": round(current_duration, 1),
            "limit_minutes": round(limit, 1),
            "remaining_minutes": round(remaining, 1),
            "recommendation": "Transition to " + ("SITTING" if mode == "standing" else "STANDING") + " in " + str(round(remaining)) + "m" if remaining < 5 else "Maintain current mode."
        }

    def calculate_recovery_boost(self):
        """ Measures if standing up actually improved scores. """
        if len(self.decay_data["sitting"]) < 1 or len(self.decay_data["standing"]) < 1:
            return 0
        
        # Compare avg score of last standing vs last sitting
        last_sit = self.decay_data["sitting"][-1]["avg_score"]
        last_stand = self.decay_data["standing"][-1]["avg_score"]
        
        return round(max(0, last_stand - last_sit), 1)
