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
        self.last_result = None
        
        # Behavioral Tracking (Track 006)
        self.slouch_start_time = None
        self.slouch_duration = 0
        
        # Eye Fatigue Tracking
        self.session_start_time = time.time()
        self.last_break_time = time.time()
        self.blink_count = 0
        self.last_blink_state = False
        self.blink_timestamps = [] 

        # --- Movement & Movement Breaks (Track 009) ---
        self.last_pose_landmarks = None
        self.last_movement_time = time.time()
        self.static_duration = 0
        self.MOVEMENT_THRESHOLD = 0.015 # Landmark variance to count as "moved"

        # Stats Interval
        self.last_stats_record_time = time.time()

    def start(self):
        """ Starts the CV processing thread. """
        if self.is_running: return
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {self.camera_id}")
            return False
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

    def calibrate(self):
        if self.last_result and self.last_result.get('pose'):
            return self.pipeline.posture_analyzer.calibrate(self.last_result['pose'])
        return False

    def get_layout_info(self):
        info = self.monitor_manager.get_layout_info()
        info["mirror_mode"] = self.mirror_mode
        return info

    def _sanitize_data(self, data):
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(v) for v in data]
        elif isinstance(data, np.bool_): return bool(data)
        elif isinstance(data, np.integer): return int(data)
        elif isinstance(data, np.floating): return float(data)
        return data

    def _run(self):
        while self.is_running:
            success, frame = self.cap.read()
            if not success:
                time.sleep(0.1); continue
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)
            
            result = self.pipeline.process_frame(frame)
            result['workspace'] = self.get_layout_info()
            result['window'] = self.window_manager.get_active_window_info()
            
            now = time.time()
            if result.get('pose') and 'nose' in result['pose']:
                pose = result['pose']
                eye_y = pose['nose']['y']
                result['ess'] = self.window_manager.get_ergonomic_sweet_spot(eye_y)
                
                # --- Track 009: Movement Detection ---
                if self.last_pose_landmarks:
                    # Check if nose and shoulders have moved significantly
                    move_dist = 0
                    for key in ['nose', 'left_shoulder', 'right_shoulder']:
                        move_dist += np.sqrt((pose[key]['x'] - self.last_pose_landmarks[key]['x'])**2 + 
                                           (pose[key]['y'] - self.last_pose_landmarks[key]['y'])**2)
                    
                    if move_dist > self.MOVEMENT_THRESHOLD:
                        self.last_movement_time = now
                
                self.last_pose_landmarks = pose.copy()
                self.static_duration = now - self.last_movement_time
                result['analysis']['static_duration'] = round(self.static_duration, 1)

                # --- Track 006: Adaptive Thresholding & Behavioral ---
                score = result['analysis'].get('score', 100)
                app_age = self.stats_manager.get_app_age_days()
                
                # Adaptive Threshold: For the first 14 days, be more lenient
                # Threshold starts at 50% and climbs to 75% over 2 weeks
                current_threshold = min(75, 50 + (app_age * 2))
                
                if score < current_threshold:
                    if self.slouch_start_time is None: self.slouch_start_time = now
                    self.slouch_duration = now - self.slouch_start_time
                else:
                    self.slouch_start_time = None
                    self.slouch_duration = 0
                
                result['analysis']['slouch_duration'] = round(self.slouch_duration, 1)
                
                # Nudges & Notifications
                if self.slouch_duration > 10:
                    msg = "⚠️ Posture Check: Take a deep breath and realign."
                    result['analysis']['nudge'] = msg
                    self.notification_manager.notify("Posture-Sense", msg, "slouch")

                # Movement Break Nudge (20 minutes of static posture)
                if self.static_duration > 1200: # 20 mins
                    msg = "🔄 Movement Break: You've been stationary for 20m. Try a shoulder roll or thoracic stretch!"
                    result['analysis']['nudge'] = msg
                    self.notification_manager.notify("Movement Break", msg, "movement")

                # Blink Detection & Eye Strain
                is_blinking = result.get('is_blinking', False)
                if is_blinking and not self.last_blink_state:
                    self.blink_count += 1
                    self.blink_timestamps.append(now)
                self.last_blink_state = is_blinking
                self.blink_timestamps = [t for t in self.blink_timestamps if now - t < 60]
                blink_rate = len(self.blink_timestamps)
                result['analysis']['blink_rate'] = blink_rate
                
                if blink_rate > 0 and blink_rate < 8:
                    msg = "Low blink rate detected. Take a moment to blink!"
                    result['analysis']['eye_strain_warning'] = msg
                    self.notification_manager.notify("Eye Strain", msg, "blink")

                # 20-20-20 Rule Timer
                time_since_break = now - self.last_break_time
                result['analysis']['session_duration'] = round(time_since_break, 0)
                if time_since_break > 1200:
                    msg = "👁️ 20-20-20 RULE: Look 20 feet away for 20 seconds!"
                    result['analysis']['nudge'] = msg
                    self.notification_manager.notify("Break Time", msg, "break")

                # Stats Recording
                if now - self.last_stats_record_time > 60:
                    self.stats_manager.record_minute(score)
                    self.last_stats_record_time = now
                result['analysis']['stats'] = self.stats_manager.get_summary()

                # Window Placement
                ess_y = result['ess']['target_y']
                target_y = result['window']['y'] + (result['window']['height'] / 2) if result['window'] else 0
                if target_y < ess_y - 150:
                    result['analysis']['placement_suggestion'] = "Move active window DOWN for better neck alignment."
                elif target_y > ess_y + 150:
                    result['analysis']['placement_suggestion'] = "Move active window UP for better neck alignment."
                else:
                    result['analysis']['placement_suggestion'] = "Window is in the Ergonomic Sweet Spot."
            else:
                # User Not Detected
                self.slouch_start_time = None
                self.slouch_duration = 0
                self.static_duration = 0
                self.last_movement_time = now
                result['analysis']['status'] = "User Not Present"
                result['analysis']['score'] = 100
            
            self.last_result = result
            if self.callback: self.callback(self._sanitize_data(result), frame)
