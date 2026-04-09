import pandas as pd
import sqlite3
import logging
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

logger = logging.getLogger(__name__)

class FatiguePredictor:
    """ 
    Analyzes historical data to predict when the user is likely 
    to experience postural fatigue or a 'slump'.
    """
    def __init__(self, db_path="posture_data.db"):
        self.db_path = db_path
        self.model = LinearRegression()
        self.is_trained = False

    def _load_data(self):
        """ Loads historical data from the SQLite database. """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT timestamp, score FROM posture_logs", conn)
            conn.close()
            
            if len(df) < 30: # Need at least 30 minutes of data to find a trend
                return None
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Feature engineering: Minute of day
            df['minute_of_day'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
            return df
        except Exception as e:
            logger.error(f"Failed to load data for prediction: {e}")
            return None

    def train(self):
        """ Trains a simple linear model on historical trends. """
        df = self._load_data()
        if df is None:
            return False
        
        X = df[['minute_of_day']].values
        y = df['score'].values
        
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Fatigue model trained on historical data.")
        return True

    def predict_slump(self, current_score):
        """ 
        Predicts if a slump is imminent.
        Returns a probability or a 'minutes until slump' estimate.
        """
        if not self.is_trained:
            # Fallback to simple heuristic if no model is trained
            if current_score < 75: return {"imminent": True, "confidence": 0.5}
            return {"imminent": False, "confidence": 0}

        now = datetime.now()
        current_minute = now.hour * 60 + now.minute
        
        # Predict score for the next 15 minutes
        future_minutes = np.array([[current_minute + i] for i in range(1, 16)])
        predicted_scores = self.model.predict(future_minutes)
        
        # Check if predicted scores drop below 70
        slump_indices = np.where(predicted_scores < 70)[0]
        
        if len(slump_indices) > 0:
            minutes_until = slump_indices[0] + 1
            return {
                "imminent": True, 
                "minutes_until": minutes_until,
                "predicted_score": round(float(predicted_scores[slump_indices[0]]), 1)
            }
        
        return {"imminent": False, "minutes_until": None}

if __name__ == "__main__":
    predictor = FatiguePredictor()
    if predictor.train():
        print(f"Prediction: {predictor.predict_slump(80)}")
    else:
        print("Not enough data to train model.")
