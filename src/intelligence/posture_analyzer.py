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
            "shoulder_level": 0.15,
            "neck_tilt": 0.20,
            "slouch": 0.30,
            "elbow_angle": 0.10,
            "spine_alignment": 0.10,
            "typing_strain": 0.15
        }

    def calculate_angle(self, a, b, c):
        """Calculates the angle between three points (b is the vertex)."""
        a = np.array([a['x'], a['y']])
        b = np.array([b['x'], b['y']])
        c = np.array([c['x'], c['y']])
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def estimate_distance(self, iris_data):
        if not iris_data or not iris_data.get("left"): return None
        l_iris = iris_data["left"]
        p1 = np.array([l_iris[1]['x'], l_iris[1]['y']])
        p2 = np.array([l_iris[3]['x'], l_iris[3]['y']])
        dist_px = np.linalg.norm(p1 - p2)
        if dist_px == 0: return None
        focal_length = 600 
        distance_cm = (1.17 * focal_length) / dist_px
        return round(distance_cm, 1)

    def calculate_viewing_angle(self, eye_y_pixel, target_y_pixel, distance_cm):
        if not distance_cm or distance_cm == 0: return 0
        y_diff_px = target_y_pixel - eye_y_pixel
        y_diff_cm = y_diff_px / 35.0
        angle_rad = np.arctan2(y_diff_cm, distance_cm)
        return round(angle_rad * 180.0 / np.pi, 1)

    def calculate_typing_strain(self, pose_data, hand_data=None):
        if hand_data and len(hand_data) > 0: return 90.0
        if "left_shoulder" in pose_data and "left_elbow" in pose_data:
            l_s, l_e = pose_data["left_shoulder"], pose_data["left_elbow"]
            v_pt = {"x": l_s["x"], "y": l_s["y"] + 0.1}
            arm_reach_angle = self.calculate_angle(v_pt, l_s, l_e)
            return round(max(0, 100 - (max(0, arm_reach_angle - 15) * 2)), 1)
        return 100.0

    def normalize_to_physical(self, pose_data, distance_cm):
        if not distance_cm: return None
        fov_width_at_60cm = 50.0
        scale_factor = (distance_cm / 60.0) * fov_width_at_60cm
        physical_pose = {}
        for name, lm in pose_data.items():
            physical_pose[name] = {
                "x": round((lm["x"] - 0.5) * scale_factor, 2),
                "y": round((lm["y"] - 0.5) * scale_factor, 2),
                "z": round(lm["z"] * scale_factor, 2)
            }
        return physical_pose

    def calibrate(self, pose_data):
        if not pose_data or "nose" not in pose_data or "left_shoulder" not in pose_data: return False
        nose, l_s, r_s = pose_data["nose"], pose_data["left_shoulder"], pose_data["right_shoulder"]
        self.baseline = {
            "nose_y": nose['y'],
            "shoulder_y": (l_s['y'] + r_s['y']) / 2,
            "shoulder_width": abs(l_s['x'] - r_s['x']),
            "landmarks": pose_data.copy()
        }
        return True

    def analyze(self, pose_data, iris_data=None, hand_data=None, static_duration=0):
        if not pose_data or "nose" not in pose_data:
            return {"score": 0, "status": "No Person Detected", "feedback": "No person detected."}

        # 1. Distance & Normalization
        distance_cm = self.estimate_distance(iris_data) if iris_data else None
        physical_pose = self.normalize_to_physical(pose_data, distance_cm)

        # 2. Shoulder Levelness
        l_s, r_s = pose_data["left_shoulder"], pose_data["right_shoulder"]
        shoulder_diff = abs(l_s['y'] - r_s['y'])
        shoulder_score = max(0, 100 - (shoulder_diff * 1000))

        # 3. Neck Tilt
        nose = pose_data["nose"]
        mid_s_x, mid_s_y = (l_s['x'] + r_s['x'])/2, (l_s['y'] + r_s['y'])/2
        neck_tilt_lat = abs(nose['x'] - mid_s_x)
        neck_score = max(0, 100 - (neck_tilt_lat * 2000))

        # 4. Slouching
        slouch_score = 100
        if self.baseline:
            baseline_dist = self.baseline["shoulder_y"] - self.baseline["nose_y"]
            dist_diff = max(0, baseline_dist - (mid_s_y - nose['y']))
            slouch_score = max(0, 100 - (dist_diff * 1500))

        # 5. Elbows
        elbow_score = 100
        if "left_elbow" in pose_data and "left_wrist" in pose_data:
            angle = self.calculate_angle(pose_data["left_shoulder"], pose_data["left_elbow"], pose_data["left_wrist"])
            elbow_score = max(0, 100 - (abs(angle - 105) * 2))

        # 6. Spine
        spine_score = 100
        if "left_hip" in pose_data:
            mid_h_x = (pose_data["left_hip"]['x'] + pose_data["right_hip"]['x'])/2
            spine_score = max(0, 100 - (abs(mid_s_x - mid_h_x) * 1000))

        # 7. Typing & Sit/Stand
        typing_score = self.calculate_typing_strain(pose_data, hand_data)
        if self.baseline: self.is_standing = nose['y'] < self.baseline["nose_y"] - 0.08
        else: self.is_standing = nose['y'] < 0.38

        # 8. Industry Standards
        rula = self.rula_scorer.get_grand_score(pose_data, self.is_standing)
        reba = self.reba_scorer.get_grand_score(pose_data, self.is_standing, static_duration)

        total_score = (shoulder_score * 0.15 + neck_score * 0.20 + slouch_score * 0.30 + 
                       elbow_score * 0.10 + spine_score * 0.10 + typing_score * 0.15)

        return {
            "score": round(total_score, 2), "is_standing": self.is_standing, "calibrated": self.baseline is not None,
            "distance_cm": distance_cm, "physical_pose": physical_pose, "typing_score": typing_score,
            "rula": rula, "reba": reba,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4), "neck_tilt_lat": round(neck_tilt_lat, 4),
                "slouch_score": round(slouch_score, 2), "elbow_score": round(elbow_score, 2),
                "spine_score": round(spine_score, 2), "typing_score": typing_score
            },
            "feedback": self._generate_feedback(total_score, slouch_score, neck_score, shoulder_score, typing_score)
        }

    def _generate_feedback(self, total_score, slouch, neck, shoulder, typing=100):
        if total_score >= 90: return "✅ Excellent alignment."
        items = []
        if slouch < 70: items.append("🪑 Slouching detected.")
        if neck < 70: items.append("🦒 Check neck tilt.")
        if shoulder < 70: items.append("⚖️ Level shoulders.")
        if typing < 75: items.append("⌨️ Typing strain.")
        return " | ".join(items) if items else "👍 Good posture."

if __name__ == "__main__":
    analyzer = PostureAnalyzer()
    mock_pose = {"nose": {"x": 0.5, "y": 0.3}, "left_shoulder": {"x": 0.4, "y": 0.4}, "right_shoulder": {"x": 0.6, "y": 0.4},
                 "left_elbow": {"x": 0.35, "y": 0.55}, "left_wrist": {"x": 0.4, "y": 0.6}, "left_hip": {"x": 0.42, "y": 0.7}, "right_hip": {"x": 0.58, "y": 0.7}}
    analyzer.calibrate(mock_pose)
    print(analyzer.analyze(mock_pose))
