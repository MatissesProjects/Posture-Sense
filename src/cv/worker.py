import cv2
import threading
import time
import logging
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

        # Stats Interval
        self.last_stats_record_time = time.time()

    def start(self):
        """ Starts the CV processing thread. """
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {self.camera_id}")
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("CV Worker started.")
        return True

    def stop(self):
        """ Stops the CV processing thread. """
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        logger.info("CV Worker stopped.")

    def toggle_mirror(self):
        """ Toggles mirroring of the image. """
        self.mirror_mode = not self.mirror_mode
        return self.mirror_mode

    def calibrate(self):
        """ Triggers calibration on the next frame with pose data. """
        if self.last_result and self.last_result.get('pose'):
            return self.pipeline.posture_analyzer.calibrate(self.last_result['pose'])
        return False

    def get_layout_info(self):
        """ Returns the full workspace model for the UI. """
        info = self.monitor_manager.get_layout_info()
        info["mirror_mode"] = self.mirror_mode
        return info

    def _sanitize_data(self, data):
        """ Recursively converts numpy types to native python types for JSON. """
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(v) for v in data]
        elif isinstance(data, np.bool_):
            return bool(data)
        elif isinstance(data, np.integer):
            return int(data)
        elif isinstance(data, np.floating):
            return float(data)
        return data

    def _run(self):
        """ The internal loop that captures and processes frames. """
        while self.is_running:
            success, frame = self.cap.read()
            if not success:
                logger.warning("Failed to capture frame.")
                time.sleep(0.1)
                continue
            
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)
            
            # Process the frame through the pipeline
            result = self.pipeline.process_frame(frame)
            
            # Add workspace context
            result['workspace'] = self.get_layout_info()
            result['window'] = self.window_manager.get_active_window_info()
            
            # Calculate ESS, Distance, and Viewing Angle
            if result.get('pose') and 'nose' in result['pose']:
                eye_y = result['pose']['nose']['y']
                result['ess'] = self.window_manager.get_ergonomic_sweet_spot(eye_y)
                
                # ... (rest of detection logic)
            else:
                # User not detected: Stop all timers and clear behavioral states
                self.slouch_start_time = None
                self.slouch_duration = 0
                self.blink_timestamps = []
                self.last_blink_state = False
                # Optionally reset break timer if user is gone for a long time
                # For now, we just pause incrementing session-based alerts
                self.last_break_time = time.time() - result['analysis'].get('session_duration', 0)
                
                result['analysis']['status'] = "User Not Present"
                result['analysis']['score'] = 100 # Default to perfect when away
                result['analysis']['feedback'] = "User away from desk. Timers paused."
                
                # Distance/Angle Calculation
                distance = result['analysis'].get('distance_cm')
                if distance and result['window'] and result['ess']:
                    target_y = result['window']['y'] + (result['window']['height'] / 2)
                    cam_pos = self.monitor_manager.get_webcam_global_pos()
                    eye_offset_px = (eye_y - 0.5) * 500 
                    eye_y_pixel = cam_pos["y"] + eye_offset_px
                    
                    angle = self.pipeline.posture_analyzer.calculate_viewing_angle(
                        eye_y_pixel, target_y, distance
                    )
                    result['analysis']['viewing_angle'] = angle

                    # Gaze Contextualization
                    gaze = result.get('gaze_ratio', {"x": 0.5, "y": 0.5})
                    h_focus = "left" if gaze["x"] < 0.45 else "right" if gaze["x"] > 0.55 else "center"
                    v_focus = "top" if gaze["y"] < 0.45 else "bottom" if gaze["y"] > 0.55 else "center"
                    result['analysis']['looking_at'] = f"{v_focus}_{h_focus}"
                    result['analysis']['gaze_point'] = gaze 

                    # --- Track 006: Behavioral & Fatigue ---
                    now = time.time()
                    # 1. Slouch Tracking
                    score = result['analysis'].get('score', 100)
                    if score < 70:
                        if self.slouch_start_time is None:
                            self.slouch_start_time = now
                        self.slouch_duration = now - self.slouch_start_time
                    else:
                        self.slouch_start_time = None
                        self.slouch_duration = 0
                    
                    result['analysis']['slouch_duration'] = round(self.slouch_duration, 1)
                    if self.slouch_duration > 10:
                        msg = "⚠️ SIT UP: Slouching detected for too long."
                        result['analysis']['nudge'] = msg
                        self.notification_manager.notify("Posture Alert", msg, "slouch")

                    # 2. Blink Detection & Eye Strain
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

                    # 3. 20-20-20 Rule Timer
                    time_since_break = now - self.last_break_time
                    result['analysis']['session_duration'] = round(time_since_break, 0)
                    if time_since_break > 1200:
                        msg = "👁️ 20-20-20 RULE: Look 20 feet away for 20 seconds!"
                        result['analysis']['nudge'] = msg
                        self.notification_manager.notify("Break Time", msg, "break")

                    # --- Stats & Summary ---
                    if now - self.last_stats_record_time > 60:
                        self.stats_manager.record_minute(score)
                        self.last_stats_record_time = now
                    
                    result['analysis']['stats'] = self.stats_manager.get_summary()

                    # Window Placement Suggestion
                    ess_y = result['ess']['target_y']
                    if target_y < ess_y - 150:
                        result['analysis']['placement_suggestion'] = "Move active window DOWN for better neck alignment."
                    elif target_y > ess_y + 150:
                        result['analysis']['placement_suggestion'] = "Move active window UP for better neck alignment."
                    else:
                        result['analysis']['placement_suggestion'] = "Window is in the Ergonomic Sweet Spot."
            
            self.last_result = result
            if self.callback:
                self.callback(result, frame)
