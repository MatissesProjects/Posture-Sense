import cv2
import json
from src.cv.pose_detector import PoseDetector
from src.cv.eye_tracker import EyeTracker

class CVPipeline:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.eye_tracker = EyeTracker()

    def process_frame(self, img):
        """Processes a single frame and returns all landmark data."""
        h, w, _ = img.shape
        
        # Pose detection
        img = self.pose_detector.find_pose(img, draw=False)
        pose_lms = self.pose_detector.get_relevant_landmarks()
        
        # Eye tracking
        self.eye_tracker.find_face_mesh(img)
        iris_lms = self.eye_tracker.get_iris_landmarks(w, h)
        
        data = {
            "pose": pose_lms,
            "iris": iris_lms,
            "resolution": {"width": w, "height": h}
        }
        
        return data

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
