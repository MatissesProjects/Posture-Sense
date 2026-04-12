import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

class GazeAnalyzer:
    """
    Analyzes gaze distribution across multiple monitors (Track 024).
    Specifically monitors neck extension strain for stacked layouts.
    """
    def __init__(self):
        # Time spent on each region (Top, Neutral/Seam, Bottom)
        self.distribution = {"top": 0, "neutral": 0, "bottom": 0}
        self.last_update_time = time.time()
        
        # Tracking continuous top monitor usage
        self.top_start_time = None
        self.MAX_CONTINUOUS_TOP_MINUTES = 15 # Warning after 15m of continuous neck extension
        self.total_top_threshold_pct = 40.0 # Warning if > 40% of day is spent on top monitor

    def update(self, gaze_data):
        """ Updates gaze distribution based on vertical gaze ratio. """
        if not gaze_data: return
        
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        
        y = gaze_data.get("y", 0.5)
        
        # 0.0 is Top, 1.0 is Bottom. Seam is 0.5.
        if y < 0.4:
            region = "top"
            if self.top_start_time is None:
                self.top_start_time = now
        elif y > 0.6:
            region = "bottom"
            self.top_start_time = None
        else:
            region = "neutral"
            self.top_start_time = None
            
        self.distribution[region] += dt

    def get_distribution_stats(self):
        """ Returns percentage breakdown and strain warnings. """
        total = sum(self.distribution.values())
        if total == 0: return {"top_pct": 0, "neutral_pct": 0, "bottom_pct": 0, "warnings": []}
        
        top_pct = (self.distribution["top"] / total) * 100
        
        warnings = []
        
        # Continuous strain check
        if self.top_start_time:
            continuous_top_mins = (time.time() - self.top_start_time) / 60
            if continuous_top_mins > self.MAX_CONTINUOUS_TOP_MINUTES:
                warnings.append(f"⚠️ Neck Strain: Continuous top monitor use ({round(continuous_top_mins)}m).")
                
        # Aggregate strain check
        if top_pct > self.total_top_threshold_pct:
            warnings.append(f"⚖️ High Gaze Bias: {round(top_pct)}% time on top monitor. Lower it or use bottom more.")
            
        return {
            "top_pct": round(top_pct, 1),
            "neutral_pct": round((self.distribution["neutral"] / total) * 100, 1),
            "bottom_pct": round((self.distribution["bottom"] / total) * 100, 1),
            "warnings": warnings
        }

    def reset_daily(self):
        self.distribution = {"top": 0, "neutral": 0, "bottom": 0}
        self.top_start_time = None
        self.last_update_time = time.time()
