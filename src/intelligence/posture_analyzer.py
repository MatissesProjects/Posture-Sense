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

    def calculate_com(self, physical_pose):
        if not physical_pose: return None
        weights = {"head": 0.15, "trunk": 0.60, "arms": 0.25}
        head_com = np.array([physical_pose["nose"]["x"], physical_pose["nose"]["y"], physical_pose["nose"]["z"]])
        l_s, r_s = physical_pose["left_shoulder"], physical_pose["right_shoulder"]
        l_h = physical_pose.get("left_hip", l_s)
        r_h = physical_pose.get("right_hip", r_s)
        trunk_pts = np.array([[l_s["x"], l_s["y"], l_s["z"]], [r_s["x"], r_s["y"], r_s["z"]], [l_h["x"], l_h["y"], l_h["z"]], [r_h["x"], r_h["y"], r_h["z"]]])
        trunk_com = np.mean(trunk_pts, axis=0)
        arm_pts = []
        for side in ["left", "right"]:
            if f"{side}_elbow" in physical_pose: arm_pts.append([physical_pose[f"{side}_elbow"]["x"], physical_pose[f"{side}_elbow"]["y"], physical_pose[f"{side}_elbow"]["z"]])
            if f"{side}_wrist" in physical_pose: arm_pts.append([physical_pose[f"{side}_wrist"]["x"], physical_pose[f"{side}_wrist"]["y"], physical_pose[f"{side}_wrist"]["z"]])
        arm_com = np.mean(arm_pts, axis=0) if arm_pts else trunk_com
        total_com = (head_com * weights["head"] + trunk_com * weights["trunk"] + arm_com * weights["arms"])
        return {"x": round(float(total_com[0]), 2), "y": round(float(total_com[1]), 2), "z": round(float(total_com[2]), 2)}

    def analyze_spine_kinematics(self, physical_pose):
        if not physical_pose or "left_hip" not in physical_pose: return None
        nose = np.array([physical_pose["nose"]["x"], physical_pose["nose"]["y"], physical_pose["nose"]["z"]])
        l_s, r_s = physical_pose["left_shoulder"], physical_pose["right_shoulder"]
        mid_s = np.array([(l_s["x"] + r_s["x"])/2, (l_s["y"] + r_s["y"])/2, (l_s["z"] + r_s["z"])/2])
        l_h, r_h = physical_pose["left_hip"], physical_pose["right_hip"]
        mid_h = np.array([(l_h["x"] + r_h["x"])/2, (l_h["y"] + r_h["y"])/2, (l_h["z"] + r_h["z"])/2])
        cervical_vec = nose - mid_s
        torso_vec = mid_s - mid_h
        vertical = np.array([0, -1, 0])
        def angle_with_vertical(vec):
            v_unit = vec / (np.linalg.norm(vec) + 1e-6)
            dot = np.dot(v_unit, vertical)
            return np.arccos(np.clip(dot, -1.0, 1.0)) * 180.0 / np.pi
        neck_flexion = angle_with_vertical(cervical_vec)
        trunk_flexion = angle_with_vertical(torso_vec)
        slump_depth = mid_s[2] - mid_h[2]
        return {"neck_flexion": round(float(neck_flexion), 1), "trunk_flexion": round(float(trunk_flexion), 1), "slump_depth_cm": round(float(slump_depth), 2), "is_slumping": slump_depth > 5.0}

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

        distance_cm = self.estimate_distance(iris_data) if iris_data else None
        physical_pose = self.normalize_to_physical(pose_data, distance_cm)
        com = self.calculate_com(physical_pose) if physical_pose else None
        spine = self.analyze_spine_kinematics(physical_pose) if physical_pose else None

        l_s, r_s = pose_data["left_shoulder"], pose_data["right_shoulder"]
        shoulder_diff = abs(l_s['y'] - r_s['y'])
        shoulder_score = max(0, 100 - (shoulder_diff * 1000))

        nose = pose_data["nose"]
        mid_s_x, mid_s_y = (l_s['x'] + r_s['x'])/2, (l_s['y'] + r_s['y'])/2
        neck_tilt_lat = abs(nose['x'] - mid_s_x)
        neck_score = max(0, 100 - (neck_tilt_lat * 2000))

        slouch_score = 100
        if self.baseline:
            baseline_dist = self.baseline["shoulder_y"] - self.baseline["nose_y"]
            dist_diff = max(0, baseline_dist - (mid_s_y - nose['y']))
            slouch_score = max(0, 100 - (dist_diff * 1500))

        elbow_score = 100
        if "left_elbow" in pose_data and "left_wrist" in pose_data:
            angle = self.calculate_angle(pose_data["left_shoulder"], pose_data["left_elbow"], pose_data["left_wrist"])
            elbow_score = max(0, 100 - (abs(angle - 105) * 2))

        spine_score = 100
        if "left_hip" in pose_data:
            mid_h_x = (pose_data["left_hip"]['x'] + pose_data["right_hip"]['x'])/2
            spine_score = max(0, 100 - (abs(mid_s_x - mid_h_x) * 1000))

        typing_score = self.calculate_typing_strain(pose_data, hand_data)
        if self.baseline: self.is_standing = nose['y'] < self.baseline["nose_y"] - 0.08
        else: self.is_standing = nose['y'] < 0.38

        rula = self.rula_scorer.get_grand_score(pose_data, self.is_standing)
        reba = self.reba_scorer.get_grand_score(pose_data, self.is_standing, static_duration)

        total_score = (shoulder_score * 0.15 + neck_score * 0.20 + slouch_score * 0.30 + 
                       elbow_score * 0.10 + spine_score * 0.10 + typing_score * 0.15)

        return {
            "score": round(total_score, 2), "is_standing": self.is_standing, "calibrated": self.baseline is not None,
            "distance_cm": distance_cm, "physical_pose": physical_pose, "com": com, "spine": spine, "typing_score": typing_score,
            "rula": rula, "reba": reba,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4), "neck_tilt_lat": round(neck_tilt_lat, 4),
                "slouch_score": round(slouch_score, 2), "elbow_score": round(elbow_score, 2),
                "spine_score": round(spine_score, 2), "typing_score": typing_score
            },
            "feedback": self._generate_feedback(total_score, slouch_score, neck_score, shoulder_score, typing_score, spine)
        }

    def _generate_feedback(self, total_score, slouch, neck, shoulder, typing=100, spine=None):
        if total_score >= 90: return "✅ Excellent alignment."
        items = []
        if slouch < 70: items.append("🪑 Slouching detected.")
        if neck < 70: items.append("🦒 Check neck tilt.")
        if shoulder < 70: items.append("⚖️ Level shoulders.")
        if typing < 75: items.append("⌨️ Typing strain.")
        if spine and spine.get("is_slumping"): items.append("📉 Torso leaning forward.")
        return " | ".join(items) if items else "👍 Good posture."

if __name__ == "__main__":
    analyzer = PostureAnalyzer()
    mock_pose = {"nose": {"x": 0.5, "y": 0.3, "z": 0}, "left_shoulder": {"x": 0.4, "y": 0.4, "z": 0}, "right_shoulder": {"x": 0.6, "y": 0.4, "z": 0},
                 "left_elbow": {"x": 0.35, "y": 0.55, "z": 0}, "left_wrist": {"x": 0.4, "y": 0.6, "z": 0}, "left_hip": {"x": 0.42, "y": 0.7, "z": 0}, "right_hip": {"x": 0.58, "y": 0.7, "z": 0}}
    analyzer.calibrate(mock_pose)
    print(analyzer.analyze(mock_pose))
