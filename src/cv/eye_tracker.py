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
        img_rgb = np.ascontiguousarray(img_rgb)
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

    def get_gaze_ratio(self, iris_data, img_w, img_h):
        """
        Calculates a vertical and horizontal gaze ratio.
        Returns a normalized point where (0.5, 0.5) is centered.
        """
        if not self.results or not self.results.multi_face_landmarks:
            return {"x": 0.5, "y": 0.5}
            
        face_lms = self.results.multi_face_landmarks[0].landmark
        
        # Reference points for Left Eye
        # Vertical: Top (159), Bottom (145)
        # Horizontal: Inner (133), Outer (33)
        l_top = face_lms[159].y
        l_bottom = face_lms[145].y
        l_inner = face_lms[133].x
        l_outer = face_lms[33].x
        
        iris_center_y = face_lms[468].y
        iris_center_x = face_lms[468].x
        
        # Calculate Ratios
        # Vertical: 0.0 at top lid, 1.0 at bottom lid
        v_ratio = (iris_center_y - l_top) / (l_bottom - l_top) if (l_bottom - l_top) != 0 else 0.5
        
        # Horizontal: 0.0 at outer, 1.0 at inner (for left eye front view)
        # We'll normalize this so < 0.5 is looking LEFT, > 0.5 is looking RIGHT
        h_ratio = (iris_center_x - l_outer) / (l_inner - l_outer) if (l_inner - l_outer) != 0 else 0.5
        
        return {"x": round(h_ratio, 3), "y": round(v_ratio, 3)}

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
