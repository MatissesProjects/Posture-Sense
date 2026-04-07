import numpy as np
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.baseline = None  # Set during calibration
        self.is_standing = False
        
        # Scoring weights
        self.weights = {
            "shoulder_level": 0.20,
            "neck_tilt": 0.25,
            "slouch": 0.35,
            "elbow_angle": 0.10,
            "spine_alignment": 0.10
        }

    def calculate_angle(self, a, b, c):
        """Calculates the angle between three points (b is the vertex)."""
        a = np.array([a['x'], a['y']])
        b = np.array([b['x'], b['y']])
        c = np.array([c['x'], c['y']])

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def calibrate(self, pose_data):
        """Sets the baseline posture for the user."""
        if not pose_data or "nose" not in pose_data or "left_shoulder" not in pose_data:
            return False
        
        nose = pose_data["nose"]
        l_shoulder = pose_data["left_shoulder"]
        r_shoulder = pose_data["right_shoulder"]
        
        self.baseline = {
            "nose_y": nose['y'],
            "shoulder_y": (l_shoulder['y'] + r_shoulder['y']) / 2,
            "shoulder_width": abs(l_shoulder['x'] - r_shoulder['x']),
            "landmarks": pose_data.copy()
        }
        logger.info(f"Calibration successful: {self.baseline}")
        return True

    def analyze(self, pose_data):
        """
        Analyzes pose data to determine posture score and sit/stand status.
        pose_data: dict of named landmarks from PoseDetector.
        """
        if not pose_data or "nose" not in pose_data:
            return {
                "score": 0, 
                "status": "No Person Detected", 
                "is_standing": self.is_standing,
                "feedback": "No person detected in frame."
            }

        # 1. Shoulder Levelness
        l_shoulder = pose_data["left_shoulder"]
        r_shoulder = pose_data["right_shoulder"]
        shoulder_diff = abs(l_shoulder['y'] - r_shoulder['y'])
        shoulder_score = max(0, 100 - (shoulder_diff * 1000))

        # 2. Neck Tilt (Lateral)
        nose = pose_data["nose"]
        mid_shoulder_x = (l_shoulder['x'] + r_shoulder['x']) / 2
        mid_shoulder_y = (l_shoulder['y'] + r_shoulder['y']) / 2
        neck_tilt_lat = abs(nose['x'] - mid_shoulder_x)
        neck_score = max(0, 100 - (neck_tilt_lat * 2000))

        # 3. Slouching (Vertical distance Nose to Shoulders)
        current_nose_to_shoulder = mid_shoulder_y - nose['y']
        slouch_score = 100
        if self.baseline:
            baseline_dist = self.baseline["shoulder_y"] - self.baseline["nose_y"]
            dist_diff = max(0, baseline_dist - current_nose_to_shoulder)
            slouch_score = max(0, 100 - (dist_diff * 1500))

        # 4. Elbow Angle (Ergonomic 90-120 degrees)
        elbow_score = 100
        if "left_elbow" in pose_data and "left_wrist" in pose_data:
            l_elbow_angle = self.calculate_angle(
                pose_data["left_shoulder"], 
                pose_data["left_elbow"], 
                pose_data["left_wrist"]
            )
            # Penalize if far from 105 degrees (midpoint of 90-120)
            elbow_diff = abs(l_elbow_angle - 105)
            elbow_score = max(0, 100 - (elbow_diff * 2))

        # 5. Spine/Hip Alignment
        spine_score = 100
        if "left_hip" in pose_data and "right_hip" in pose_data:
            mid_hip_x = (pose_data["left_hip"]['x'] + pose_data["right_hip"]['x']) / 2
            # Deviation of shoulder midpoint from hip midpoint
            spine_dev = abs(mid_shoulder_x - mid_hip_x)
            spine_score = max(0, 100 - (spine_dev * 1000))

        # 6. Sit/Stand Detection
        if self.baseline:
            # If nose is significantly higher (lower Y) than baseline
            if nose['y'] < self.baseline["nose_y"] - 0.08:
                self.is_standing = True
            elif nose['y'] > self.baseline["nose_y"] + 0.08:
                self.is_standing = False
        else:
            # Heuristic
            self.is_standing = nose['y'] < 0.38

        # Weighted Total Score
        total_score = (
            shoulder_score * self.weights["shoulder_level"] +
            neck_score * self.weights["neck_tilt"] +
            slouch_score * self.weights["slouch"] +
            elbow_score * self.weights["elbow_angle"] +
            spine_score * self.weights["spine_alignment"]
        )

        analysis = {
            "score": round(total_score, 2),
            "is_standing": self.is_standing,
            "calibrated": self.baseline is not None,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4),
                "neck_tilt_lat": round(neck_tilt_lat, 4),
                "slouch_score": round(slouch_score, 2),
                "elbow_score": round(elbow_score, 2),
                "spine_score": round(spine_score, 2)
            },
            "feedback": self._generate_feedback(total_score, slouch_score, neck_score, shoulder_score)
        }
        
        return analysis

    def _generate_feedback(self, total_score, slouch, neck, shoulder):
        if total_score >= 90:
            return "Excellent Posture! Keep it up."
        
        feedback_items = []
        if slouch < 70:
            feedback_items.append("Sit up straighter, you're slouching.")
        if neck < 70:
            feedback_items.append("Align your head with your spine.")
        if shoulder < 70:
            feedback_items.append("Level your shoulders.")
            
        if not feedback_items:
            if total_score < 80:
                return "Minor postural adjustments needed."
            return "Good posture."
            
        return " ".join(feedback_items)

if __name__ == "__main__":
    analyzer = PostureAnalyzer()
    # Mock data: Dictionary format
    mock_pose = {
        "nose": {"x": 0.5, "y": 0.3},
        "left_shoulder": {"x": 0.4, "y": 0.4},
        "right_shoulder": {"x": 0.6, "y": 0.4},
        "left_elbow": {"x": 0.35, "y": 0.55},
        "left_wrist": {"x": 0.4, "y": 0.6},
        "left_hip": {"x": 0.42, "y": 0.7},
        "right_hip": {"x": 0.58, "y": 0.7}
    }
    analyzer.calibrate(mock_pose)
    print(analyzer.analyze(mock_pose))
