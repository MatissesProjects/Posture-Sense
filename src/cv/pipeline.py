import cv2
import json
import numpy as np
from src.cv.pose_detector import PoseDetector
from src.cv.eye_tracker import EyeTracker
from src.cv.hand_tracker import HandTracker
from src.cv.workstation_analyzer import WorkstationAnalyzer
from src.intelligence.posture_analyzer import PostureAnalyzer

class CVPipeline:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.eye_tracker = EyeTracker()
        self.hand_tracker = HandTracker()
        self.workstation_analyzer = WorkstationAnalyzer()
        self.posture_analyzer = PostureAnalyzer()

    def process_frame(self, img, static_duration=0, viewing_angle=0):
        """Processes a single frame and returns all landmark data and analysis."""
        h, w, _ = img.shape
        
        # Environmental Audit: Brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = round(float(np.mean(gray)), 2)

        # Pose detection
        img = self.pose_detector.find_pose(img, draw=False)
        pose_lms = self.pose_detector.get_relevant_landmarks()
        
        # Eye tracking
        self.eye_tracker.find_face_mesh(img)
        iris_lms = self.eye_tracker.get_iris_landmarks(w, h)
        gaze_ratio = self.eye_tracker.get_gaze_ratio(iris_lms, w, h)
        head_pose = self.eye_tracker.get_head_pose()
        eye_data = self.eye_tracker.get_blink_status()

        # Hand tracking (Track 011)
        self.hand_tracker.find_hands(img)
        hand_lms = self.hand_tracker.get_hand_landmarks(w, h)
        
        # Posture Analysis
        analysis = self.posture_analyzer.analyze(pose_lms, iris_lms, hand_lms, static_duration, viewing_angle, brightness, eye_data)
        
        # Workstation Analysis (Track 018)
        env_data = self.workstation_analyzer.analyze_environment(img, pose_lms, analysis.get('physical_pose'))

        data = {
            "pose": pose_lms,
            "iris": iris_lms,
            "hands": hand_lms,
            "gaze_ratio": gaze_ratio,
            "head_pose": head_pose,
            "eye_data": eye_data,
            "brightness": brightness,
            "analysis": analysis,
            "environment": env_data,
            "resolution": {"width": w, "height": h}
        }

        
        return data

    def calibrate(self):
        """Triggers calibration on the next processed frame (if pose detected)."""
        # This is a bit tricky with the current structure. 
        # For now, we'll just have run.py call it directly if it has pose data.
        pass

    def to_json(self, data):
        """Serializes the data structure to JSON."""
        return json.dumps(data)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    pipeline = CVPipeline()
    while True:
        success, img = cap.read()
        if not success:
            break
        
        data = pipeline.process_frame(img)
        print(pipeline.to_json(data))
        
        cv2.imshow("CV Pipeline", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
