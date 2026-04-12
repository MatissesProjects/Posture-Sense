import cv2
import threading
import time
import logging
import numpy as np
from src.cv.pipeline import CVPipeline
from src.system.monitor_manager import MonitorManager
from src.system.window_manager import WindowManager
from src.intelligence.stats_manager import StatsManager
from src.system.notification_manager import NotificationManager

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class CVWorker:
    """ Manages the camera and CVPipeline in a separate thread. """
    def __init__(self, camera_id=0, callback=None):
        self.camera_id = camera_id
        self.callback = callback
        self.pipeline = CVPipeline()
        self.monitor_manager = MonitorManager()
        self.window_manager = WindowManager(self.monitor_manager)
        self.stats_manager = StatsManager()
        self.notification_manager = NotificationManager()
        self.cap = None
        self.is_running = False
        self.thread = None
        self.mirror_mode = False
        self.privacy_mode = False
        self.last_result = None
        
        # Behavioral Tracking
        self.slouch_start_time = None
        self.slouch_duration = 0
        self.micro_slumps = 0
        
        # Eye Fatigue Tracking
        self.session_start_time = time.time()
        self.last_break_time = time.time()
        self.blink_count = 0
        self.last_blink_state = False
        self.blink_timestamps = [] 

        # Movement Tracking
        self.last_pose_landmarks = None
        self.last_movement_time = time.time()
        self.static_duration = 0
        self.MOVEMENT_THRESHOLD = 0.015

        # --- Track 009: Specialized Stretches ---
        self.top_monitor_time = 0
        self.standing_time = 0
        self.active_stretch_type = None
        self.stretch_start_time = None
        self.stretch_move_detected = False

        # Stats Interval
        self.last_stats_record_time = time.time()

    def start(self):
        if self.is_running: return
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened(): return False
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.is_running = False
        if self.thread: self.thread.join()
        if self.cap: self.cap.release()

    def toggle_mirror(self):
        self.mirror_mode = not self.mirror_mode
        return self.mirror_mode

    def toggle_privacy(self):
        self.privacy_mode = not self.privacy_mode
        return self.privacy_mode

    def calibrate(self):
        if self.last_result and self.last_result.get('pose'):
            return self.pipeline.posture_analyzer.calibrate(self.last_result['pose'])
        return False

    def get_layout_info(self):
        info = self.monitor_manager.get_layout_info()
        info["mirror_mode"] = self.mirror_mode
        return info

    def _sanitize_data(self, data):
        if isinstance(data, dict): return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list): return [self._sanitize_data(v) for v in data]
        elif isinstance(data, np.bool_): return bool(data)
        elif isinstance(data, np.integer): return int(data)
        elif isinstance(data, np.floating): return float(data)
        return data

    def _run(self):
        while self.is_running:
            if self.privacy_mode:
                result = {
                    "analysis": { "status": "Privacy Mode Active", "score": 100 },
                    "workspace": self.get_layout_info(), "pose": {}, "iris": {}
                }
                if self.callback: self.callback(result, None)
                time.sleep(0.5); continue

            success, frame = self.cap.read()
            if not success: time.sleep(0.1); continue
            if self.mirror_mode: frame = cv2.flip(frame, 1)
            
            result = self.pipeline.process_frame(frame, self.static_duration)
            result['workspace'] = self.get_layout_info()
            result['window'] = self.window_manager.get_active_window_info()
            
            now = time.time()
            if result.get('pose') and 'nose' in result['pose']:
                pose = result['pose']
                eye_y = pose['nose']['y']
                result['ess'] = self.window_manager.get_ergonomic_sweet_spot(eye_y)
                
                # --- Track 009: Specialized Stretches ---
                move_dist = 0
                if self.last_pose_landmarks:
                    for key in ['nose', 'left_shoulder', 'right_shoulder']:
                        move_dist += np.sqrt((pose[key]['x'] - self.last_pose_landmarks[key]['x'])**2 + 
                                           (pose[key]['y'] - self.last_pose_landmarks[key]['y'])**2)
                    if move_dist > self.MOVEMENT_THRESHOLD: 
                        self.last_movement_time = now
                        if self.active_stretch_type: self.stretch_move_detected = True
                
                self.last_pose_landmarks = pose.copy()
                self.static_duration = now - self.last_movement_time
                result['analysis']['static_duration'] = round(self.static_duration, 1)

                # --- Behavior & Adaptive ---
                score = result['analysis'].get('score', 100)
                app_age = self.stats_manager.get_app_age_days()
                
                # --- Track 013: AI Fatigue & Proactive Interventions ---
                result['analysis']['stats'] = self.stats_manager.get_summary(score)
                prediction = result['analysis']['stats'].get('fatigue_prediction')
                
                # Base threshold (gradually increases over 14 days)
                base_threshold = min(75, 50 + (app_age * 2))
                
                # Proactive Intervention: If fatigue is high, tighten threshold by up to 10%
                fatigue_penalty = 0
                if prediction and prediction.get('imminent'):
                    # The more tired the AI predicts you are, the stricter we get
                    predicted_score = prediction.get('predicted_score', 100)
                    fatigue_penalty = max(0, (75 - predicted_score) / 2)
                
                current_threshold = base_threshold + fatigue_penalty
                result['analysis']['active_threshold'] = round(current_threshold, 1)

                if score < current_threshold:
                    if self.slouch_start_time is None: self.slouch_start_time = now
                    self.slouch_duration = now - self.slouch_start_time
                else:
                    if self.slouch_start_time is not None and 1 < self.slouch_duration < 10:
                        self.micro_slumps += 1
                    self.slouch_start_time = None
                    self.slouch_duration = 0
                
                # Proactive Micro-Break Trigger
                if prediction and prediction.get('imminent') and not self.active_stretch_type:
                    if now - self.last_break_time > 600: # Max one proactive break every 10 mins
                        msg = "📉 PREDICTIVE ALERT: Posture fatigue detected. Let's reset before you slump!"
                        result['analysis']['stretch_type'] = "realign"
                        result['analysis']['nudge'] = msg
                        self.notification_manager.notify("AI Coaching", msg, "fatigue")
                        self.last_break_time = now # Treat as a break

                # Existing Alerts
                if self.slouch_duration > 10:
                    msg = "⚠️ Posture Check: Take a deep breath."
                    result['analysis']['nudge'] = msg
                    result['analysis']['stretch_type'] = "realign"
                    self.notification_manager.notify("Posture-Sense", msg, "slouch")

                if self.static_duration > 1200:
                    msg = "🔄 Movement Break: Try a shoulder roll!"
                    result['analysis']['nudge'] = msg
                    result['analysis']['stretch_type'] = "thoracic_extension"
                    self.notification_manager.notify("Movement Break", msg, "movement")

                # Window Suggester
                ess_y = result['ess']['target_y']
                target_y = result['window']['y'] + (result['window']['height'] / 2) if result['window'] else 0
                if target_y < ess_y - 150: result['analysis']['placement_suggestion'] = "Move active window DOWN."
                elif target_y > ess_y + 150: result['analysis']['placement_suggestion'] = "Move active window UP."
                else: result['analysis']['placement_suggestion'] = "Window is in the Ergonomic Sweet Spot."
            else:
                self.slouch_start_time = None
                self.slouch_duration = 0
                result['analysis']['status'] = "User Not Present"
                result['analysis']['score'] = 100
            
            self.last_result = result
            if self.callback: self.callback(self._sanitize_data(result), frame)
