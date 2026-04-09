import sqlite3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "posture_data.db"

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Table for raw minute-by-minute metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posture_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                score REAL,
                is_standing BOOLEAN,
                distance_cm REAL,
                viewing_angle REAL,
                blink_rate INTEGER,
                slouch_duration REAL,
                rula_score INTEGER,
                reba_score INTEGER,
                raw_metrics_json TEXT
            )
        ''')
        # Table for session summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                avg_score REAL,
                total_ergonomic_minutes INTEGER
            )
        ''')
        self.conn.commit()

    def log_metrics(self, analysis_data):
        """ Logs a snapshot of the current analysis. """
        try:
            cursor = self.conn.cursor()
            metrics = analysis_data.get('metrics', {})
            cursor.execute('''
                INSERT INTO posture_logs (
                    score, is_standing, distance_cm, viewing_angle, 
                    blink_rate, slouch_duration, rula_score, reba_score, raw_metrics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('score'),
                analysis_data.get('is_standing'),
                analysis_data.get('distance_cm'),
                analysis_data.get('viewing_angle'),
                analysis_data.get('blink_rate'),
                analysis_data.get('slouch_duration'),
                analysis_data.get('rula', {}).get('grand_score'),
                analysis_data.get('reba', {}).get('grand_score'),
                json.dumps(metrics)
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Database log error: {e}")

    def get_recent_history(self, limit=100):
        """ Retrieves the last N logs for trend analysis. """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM posture_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.log_metrics({"score": 95, "is_standing": True})
    print("Test log inserted.")
