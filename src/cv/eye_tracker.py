import cv2
import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self, static_image_mode=False, max_num_faces=1, 
                 refine_landmarks=True, min_detection_confidence=0.5, 
                 min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.results = None

    def find_face_mesh(self, img):
        """Finds face mesh landmarks in the image."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        return self.results

    def get_iris_landmarks(self, img_w, img_h):
        """Returns the iris landmarks for left and right eyes."""
        # Iris landmark indices for MediaPipe FaceMesh (refine_landmarks=True)
        LEFT_IRIS_IDS = [468, 469, 470, 471, 472]
        RIGHT_IRIS_IDS = [473, 474, 475, 476, 477]
        
        iris_data = {"left": [], "right": []}
        
        if self.results and self.results.multi_face_landmarks:
            face_lms = self.results.multi_face_landmarks[0].landmark
            
            for i in LEFT_IRIS_IDS:
                iris_data["left"].append({
                    "id": i,
                    "x": face_lms[i].x * img_w,
                    "y": face_lms[i].y * img_h,
                    "z": face_lms[i].z
                })
            
            for i in RIGHT_IRIS_IDS:
                iris_data["right"].append({
                    "id": i,
                    "x": face_lms[i].x * img_w,
                    "y": face_lms[i].y * img_h,
                    "z": face_lms[i].z
                })
        
        return iris_data

    def get_gaze_ratio(self, iris_data):
        """Calculates a simple gaze ratio (horizontal and vertical)."""
        # This is a placeholder for more complex gaze vector logic.
        # It currently just returns the center of the iris.
        if not iris_data["left"] or not iris_data["right"]:
            return None
        
        l_iris = np.array([[lm["x"], lm["y"]] for lm in iris_data["left"]])
        r_iris = np.array([[lm["x"], lm["y"]] for lm in iris_data["right"]])
        
        l_center = np.mean(l_iris, axis=0)
        r_center = np.mean(r_iris, axis=0)
        
        return {"left_center": l_center.tolist(), "right_center": r_center.tolist()}

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    tracker = EyeTracker()
    while True:
        success, img = cap.read()
        if not success:
            break
        
        tracker.find_face_mesh(img)
        h, w, _ = img.shape
        iris = tracker.get_iris_landmarks(w, h)
        
        if iris["left"]:
            for pt in iris["left"] + iris["right"]:
                cv2.circle(img, (int(pt["x"]), int(pt["y"])), 2, (0, 255, 0), -1)
        
        cv2.imshow("Eye Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
