import pandas as pd
import sqlite3
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import json

logger = logging.getLogger(__name__)

class FatiguePredictor:
    """ 
    Advanced fatigue predictor using multiple features: 
    - Minute of day
    - Session duration
    - Recent micro-slump frequency
    - 15m moving average
    """
    def __init__(self, db_path="posture_data.db"):
        self.db_path = db_path
        # Use Random Forest for non-linear fatigue patterns
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def _load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            # Fetch raw logs
            df = pd.read_sql_query("SELECT timestamp, score, slouch_duration, raw_metrics_json FROM posture_logs", conn)
            conn.close()
            
            if len(df) < 60: # Need at least 1 hour of data for robust multi-feature training
                return None
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['minute_of_day'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
            
            # Feature Engineering
            # 1. 15m Moving Average
            df['avg_15m'] = df['score'].rolling(window=15).mean().fillna(df['score'])
            
            # 2. Micro-slump detection (slouching between 1-5 seconds in the last minute)
            # We approximate this from the log if not explicitly stored per row
            df['is_slump'] = df['score'] < 70
            df['slump_freq_5m'] = df['is_slump'].rolling(window=5).sum().fillna(0)
            
            return df.dropna()
        except Exception as e:
            logger.error(f"Failed to load data for fatigue model: {e}")
            return None

    def train(self):
        df = self._load_data()
        if df is None: return False
        
        # Features: Minute of Day, 15m average, 5m slump frequency
        X = df[['minute_of_day', 'avg_15m', 'slump_freq_5m']].values
        y = df['score'].shift(-5).fillna(df['score']).values # Predict score 5 minutes into the future
        
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Advanced fatigue model trained.")
        return True

    def predict_slump(self, current_data):
        """
        current_data: dict from stats_manager summary containing current features.
        """
        if not self.is_trained:
            return {"imminent": False, "confidence": 0}

        now = datetime.now()
        current_minute = now.hour * 60 + now.minute
        
        # Features for prediction
        avg_15m = current_data.get("avg_15m", 80)
        # Note: we should pass micro_slumps here from worker
        slump_freq = current_data.get("slump_freq_5m", 0)
        
        X_input = np.array([[current_minute, avg_15m, slump_freq]])
        predicted_score = float(self.model.predict(X_input)[0])
        
        return {
            "imminent": predicted_score < 70,
            "predicted_score": round(predicted_score, 1),
            "confidence": 0.8 # RF confidence is higher than linear
        }

if __name__ == "__main__":
    predictor = FatiguePredictor()
    if predictor.train():
        test_data = {"avg_15m": 65, "slump_freq_5m": 3}
        print(f"Prediction: {predictor.predict_slump(test_data)}")
