import numpy as np
import logging

from src.intelligence.rula_scorer import RULAScorer
from src.intelligence.reba_scorer import REBAScorer

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.baseline = None  # Set during calibration
        self.is_standing = False
        self.rula_scorer = RULAScorer()
        self.reba_scorer = REBAScorer()
        
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

    def estimate_distance(self, iris_data):
        """
        Estimates the distance from the camera in centimeters using iris diameter.
        Formula: Distance = (Known Iris Diameter * Focal Length) / Iris Diameter in Pixels
        For most webcams, we use a heuristic focal length if not calibrated.
        """
        if not iris_data or not iris_data["left"]:
            return None
        
        # Calculate iris diameter in pixels (Left eye)
        l_iris = iris_data["left"]
        # Diameter is distance between landmarks 469 and 471 in MediaPipe Iris
        p1 = np.array([l_iris[1]['x'], l_iris[1]['y']]) # 469
        p2 = np.array([l_iris[3]['x'], l_iris[3]['y']]) # 471
        dist_px = np.linalg.norm(p1 - p2)
        
        if dist_px == 0:
            return None

        # Constant: Avg human iris is ~11.7mm (1.17cm)
        # Constant: Focal length heuristic for standard webcams ~500-700
        focal_length = 600 
        distance_cm = (1.17 * focal_length) / dist_px
        return round(distance_cm, 1)

    def calculate_viewing_angle(self, eye_y_pixel, target_y_pixel, distance_cm):
        """
        Calculates the vertical viewing angle (theta) in degrees.
        Assumes the screen is vertical and the user is looking at target_y.
        """
        if distance_cm == 0:
            return 0
            
        # 1 cm is roughly 38 pixels at 96 DPI, but we should use monitor height for accuracy
        # Heuristic: 1cm ~ 35 pixels
        y_diff_px = target_y_pixel - eye_y_pixel
        y_diff_cm = y_diff_px / 35.0
        
        # tan(theta) = y_diff / distance
        angle_rad = np.arctan2(y_diff_cm, distance_cm)
        angle_deg = angle_rad * 180.0 / np.pi
        
        return round(angle_deg, 1)

    def calculate_typing_strain(self, pose_data, hand_data=None):
        """
        Calculates typing strain score (0-100).
        Uses actual hand landmarks if available, otherwise approximates based on arm angle.
        """
        # 1. Direct Measurement (If hands visible)
        if hand_data and len(hand_data) > 0:
            # Simple heuristic: measure spread between wrist and fingertips
            # and wrist angle relative to forearm
            return 90.0 # Placeholder for direct measurement

        # 2. Heuristic Approximation (If hands out of frame)
        # We look at the angle of the upper arm (Shoulder -> Elbow) 
        # and its horizontal reach. If elbows are "winged" out or 
        # arms are extended far forward, typing strain is higher.
        if "left_shoulder" in pose_data and "left_elbow" in pose_data:
            l_s = pose_data["left_shoulder"]
            l_e = pose_data["left_elbow"]
            
            # Angle of upper arm relative to vertical
            v_pt = {"x": l_s["x"], "y": l_s["y"] + 0.1}
            arm_reach_angle = self.calculate_angle(v_pt, l_s, l_e)
            
            # Ideal typing position: elbows close to ribs (angle < 20 deg)
            # Penalize heavily if arms are reaching far forward (> 45 deg)
            strain_score = max(0, 100 - (max(0, arm_reach_angle - 15) * 2))
            return round(strain_score, 1)
            
        return 100.0 # Default if no data

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

    def analyze(self, pose_data, iris_data=None, hand_data=None, static_duration=0):
        """
        Analyzes pose data to determine posture score and sit/stand status.
        """
        if not pose_data or "nose" not in pose_data:
            return {
                "score": 0, 
                "status": "No Person Detected", 
                "is_standing": self.is_standing,
                "feedback": "No person detected in frame."
            }

        # ... (landmarks extraction) ...
        
        # 7. Typing Strain (Track 011 - Hybrid)
        typing_score = self.calculate_typing_strain(pose_data, hand_data)

        # ... (rest of logic) ...

        # Weighted Total Score
        total_score = (
            shoulder_score * 0.15 +
            neck_score * 0.20 +
            slouch_score * 0.30 +
            elbow_score * 0.10 +
            spine_score * 0.10 +
            typing_score * 0.15
        )

        analysis = {
            "score": round(total_score, 2),
            "is_standing": self.is_standing,
            "calibrated": self.baseline is not None,
            "distance_cm": distance_cm,
            "typing_score": typing_score,
            "rula": rula_result,
            "reba": reba_result,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4),
                "neck_tilt_lat": round(neck_tilt_lat, 4),
                "slouch_score": round(slouch_score, 2),
                "elbow_score": round(elbow_score, 2),
                "spine_score": round(spine_score, 2),
                "typing_score": typing_score
            },
            "feedback": self._generate_feedback(total_score, slouch_score, neck_score, shoulder_score, typing_score)
        }
        
        return analysis

    def _generate_feedback(self, total_score, slouch, neck, shoulder, typing=100):
        if total_score >= 90:
            return "✅ Excellent alignment. Keep this position."
        
        feedback_items = []
        if slouch < 70:
            feedback_items.append("🪑 Slouching: Sit up straighter or raise your monitor.")
        if neck < 70:
            feedback_items.append("🦒 Neck Tilt: Align your head.")
        if shoulder < 70:
            feedback_items.append("⚖️ Unlevel Shoulders: Level your arms.")
        if typing < 75:
            feedback_items.append("⌨️ Typing Strain: Keep elbows closer to your body.")
            
        if not feedback_items:
            if total_score < 80: return "⚠️ Minor adjustments needed."
            return "👍 Good posture."
            
        return " | ".join(feedback_items)

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
