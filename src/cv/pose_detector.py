import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, static_image_mode=False, model_complexity=1, smooth_landmarks=True,
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
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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
        """Returns only the landmarks relevant for posture analysis."""
        # Relevant landmarks: Eyes (1-6), Shoulders (11, 12), Nose (0)
        relevant_ids = [0, 1, 2, 3, 4, 5, 6, 11, 12]
        all_lms = self.get_landmarks()
        if not all_lms:
            return []
        
        return [all_lms[i] for i in relevant_ids if i < len(all_lms)]

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
