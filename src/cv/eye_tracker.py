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

    def get_head_pose(self):
        """
        Calculates 3D head pose (Yaw, Pitch, Roll) in degrees.
        """
        if not self.results or not self.results.multi_face_landmarks:
            return {"pitch": 0, "yaw": 0, "roll": 0}
            
        face_lms = self.results.multi_face_landmarks[0].landmark
        
        # Landmarks for pose: 
        # Nose tip (4), Chin (152), Left eye left corner (33), Right eye right corner (263)
        # Left mouth corner (61), Right mouth corner (291)
        
        # Simplified Pitch calculation (Up/Down) using relative Z-depth
        # When nose is closer than forehead/chin, head is tilted
        nose = face_lms[4]
        forehead = face_lms[10]
        chin = face_lms[152]
        
        # Pitch: angle of nose-forehead-chin line
        # Yaw: difference in Z between left and right eyes
        l_eye = face_lms[33]
        r_eye = face_lms[263]
        
        pitch = (nose.y - (forehead.y + chin.y)/2) * 100
        yaw = (l_eye.z - r_eye.z) * 100
        roll = (l_eye.y - r_eye.y) * 100
        
        return {
            "pitch": round(pitch, 2), # Negative is UP, Positive is DOWN
            "yaw": round(yaw, 2),     # Negative is LEFT, Positive is RIGHT
            "roll": round(roll, 2)
        }

    def get_blink_status(self):
        """
        Detects if eyes are currently closed (blink) or narrowed (squint) using EAR.
        """
        if not self.results or not self.results.multi_face_landmarks:
            return {"is_blinking": False, "is_squinting": False, "ear": 0.3}
            
        face_lms = self.results.multi_face_landmarks[0].landmark
        
        def calculate_ear(top, bottom, left, right):
            v_dist = np.sqrt((top.x - bottom.x)**2 + (top.y - bottom.y)**2)
            h_dist = np.sqrt((left.x - right.x)**2 + (left.y - right.y)**2)
            return v_dist / h_dist if h_dist != 0 else 0

        # Left Eye EAR
        l_ear = calculate_ear(face_lms[159], face_lms[145], face_lms[33], face_lms[133])
        # Right Eye EAR
        r_ear = calculate_ear(face_lms[386], face_lms[374], face_lms[263], face_lms[362])
        
        avg_ear = (l_ear + r_ear) / 2
        
        # EAR < 0.18: Closed (Blink)
        # 0.18 < EAR < 0.23: Narrowed (Squint)
        # EAR > 0.23: Open
        return {
            "is_blinking": bool(avg_ear < 0.18),
            "is_squinting": bool(0.18 <= avg_ear < 0.23),
            "ear": round(float(avg_ear), 3)
        }

    def get_gaze_ratio(self, iris_data, img_w, img_h):
        """
        Calculates a vertical and horizontal gaze ratio, 
        combining iris position and head tilt (pitch).
        """
        if not self.results or not self.results.multi_face_landmarks:
            return {"x": 0.5, "y": 0.5, "head_pitch": 0}
            
        face_lms = self.results.multi_face_landmarks[0].landmark
        
        # 1. Iris Gaze (relative to eye socket)
        l_top = face_lms[159].y
        l_bottom = face_lms[145].y
        l_inner = face_lms[133].x
        l_outer = face_lms[33].x
        iris_center = face_lms[468]
        
        v_iris_ratio = (iris_center.y - l_top) / (l_bottom - l_top) if (l_bottom - l_top) != 0 else 0.5
        h_iris_ratio = (iris_center.x - l_outer) / (l_inner - l_outer) if (l_inner - l_outer) != 0 else 0.5
        
        # 2. Head Pitch (Up/Down Tilt)
        # Ratio of Nose Tip (4) to the line between forehead (10) and chin (152)
        forehead = face_lms[10].y
        chin = face_lms[152].y
        nose = face_lms[4].y
        
        # 0.0 at forehead, 1.0 at chin. Neutral is usually around 0.3-0.4
        head_pitch_ratio = (nose - forehead) / (chin - forehead) if (chin - forehead) != 0 else 0.5
        
        # 3. Combine signals for vertical projection
        # Head pitch is a much stronger indicator for stacked monitors
        # Neutral pitch (~0.35) should map to 0.5 (the webcam level / monitor seam)
        # Looking UP (< 0.35) decreases Y, looking DOWN (> 0.35) increases Y.
        # Reduced multiplier from 4.0 to 2.5 to keep it on screen.
        combined_y = 0.5 + (head_pitch_ratio - 0.35) * 2.5 + (v_iris_ratio - 0.5) * 0.4
        
        return {
            "x": round(h_iris_ratio, 3), 
            "y": round(combined_y, 3),
            "head_pitch": round(head_pitch_ratio, 3)
        }

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
