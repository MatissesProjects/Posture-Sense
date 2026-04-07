import cv2
import threading
import time
import logging
from src.cv.pipeline import CVPipeline
from src.system.monitor_manager import MonitorManager
from src.system.window_manager import WindowManager

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
        self.cap = None
        self.is_running = False
        self.thread = None
        self.mirror_mode = False
        self.last_result = None

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
            result['workspace'] = self.monitor_manager.get_layout_info()
            result['window'] = self.window_manager.get_active_window_info()
            
            # Calculate ESS, Distance, and Viewing Angle
            if result.get('pose') and 'nose' in result['pose']:
                eye_y = result['pose']['nose']['y'] # Use nose as proxy for eye level
                result['ess'] = self.window_manager.get_ergonomic_sweet_spot(eye_y)
                
                # Distance Estimation (cm)
                distance = self.pipeline.posture_analyzer.estimate_distance(result.get('iris'))
                result['analysis']['distance_cm'] = distance
                
                # Viewing Angle (theta) and Placement Suggestion
                if distance and result['window'] and result['ess']:
                    # Use center of active window as point of interest
                    target_y = result['window']['y'] + (result['window']['height'] / 2)
                    # Convert eye normalized Y to global screen Y
                    eye_y_pixel = eye_y * result['workspace']['total_height']
                    
                    angle = self.pipeline.posture_analyzer.calculate_viewing_angle(
                        eye_y_pixel, target_y, distance
                    )
                    result['analysis']['viewing_angle'] = angle

                    # Placement Suggestion based on ESS
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
            
            # time.sleep(0.01) 

if __name__ == "__main__":
    def simple_callback(data, frame):
        score = data['analysis'].get('score', 0)
        cv2.putText(frame, f"Score: {score}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("CV Worker Test", frame)
        cv2.waitKey(1)

    worker = CVWorker(callback=simple_callback)
    worker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        worker.stop()
        cv2.destroyAllWindows()
