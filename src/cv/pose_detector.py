import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, static_image_mode=False, model_complexity=2, smooth_landmarks=True,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_pose(self, img, draw=True):
        """Finds the pose landmarks in the image."""
        # Ensure image is contiguous and RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb = np.ascontiguousarray(img_rgb)
        self.results = self.pose.process(img_rgb)
        
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        return img

    def get_landmarks(self):
        """Returns a list of all detected landmarks."""
        landmark_list = []
        if self.results and self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                landmark_list.append({
                    "id": id,
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                })
        return landmark_list

    def get_relevant_landmarks(self):
        """Returns only the landmarks relevant for posture analysis in a dictionary format."""
        # Relevant landmarks: 
        # Nose (0), Eyes (1-6)
        # Shoulders (11, 12), Elbows (13, 14), Wrists (15, 16)
        # Hips (23, 24)
        relevant_ids = {
            "nose": 0,
            "left_eye": 2, # Using eye center
            "right_eye": 5, # Using eye center
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_elbow": 13,
            "right_elbow": 14,
            "left_wrist": 15,
            "right_wrist": 16,
            "left_hip": 23,
            "right_hip": 24
        }
        
        all_lms = self.get_landmarks()
        if not all_lms:
            return {}
        
        relevant_data = {}
        for name, idx in relevant_ids.items():
            if idx < len(all_lms):
                relevant_data[name] = all_lms[idx]
        
        return relevant_data

if __name__ == "__main__":
    # Test on webcam
    cap = cv2.VideoCapture(0)
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        if not success:
            break
        
        img = detector.find_pose(img)
        lms = detector.get_relevant_landmarks()
        if lms:
            # Print shoulder positions as a quick check
            left_shoulder = lms[7] # ID 11
            right_shoulder = lms[8] # ID 12
            print(f"L-Shoulder: {left_shoulder['x']:.2f}, R-Shoulder: {right_shoulder['x']:.2f}")

        cv2.imshow("Pose Detection", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
