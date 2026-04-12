import numpy as np
import logging
import time
from src.intelligence.rula_scorer import RULAScorer
from src.intelligence.reba_scorer import REBAScorer

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.baselines = {}  # Map of context -> baseline (e.g. 'neutral', 'top', 'bottom')
        self.active_context = 'neutral'
        self.is_standing = False
        self.rula_scorer = RULAScorer()
        self.reba_scorer = REBAScorer()
        
        # Temporal Smoothing
        self.smoothed_lms = {}
        self.EMA_ALPHA = 0.35 # Smoothing factor (lower = more smooth, but more lag)
        
        # Track 017: Micro-Compensation / Fidget Buffer
        # Stores last 30 frames of RAW (un-smoothed) landmarks
        self.raw_buffer = []
        self.BUFFER_SIZE = 30
        
        # Track 021: Respiration Tracking
        self.respiration_buffer = []
        self.RESP_BUFFER_SIZE = 300 # ~10 seconds at 30fps
        self.last_resp_rate = 0
        self.last_resp_calc_time = 0
        
        # Dynamic Camera Pitch (Auto-Leveling)
        self.camera_pitch_offset = 0
        self.pitch_ema_alpha = 0.05 # Slow adjustment to physical movement

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

    def calculate_viewing_angle(self, eye_y_cam_norm, gaze_y_work_norm, distance_cm):
        """
        Calculates vertical viewing angle based on normalized eye position and gaze.
        """
        workspace_height_cm = 60.0
        # Assume eye is at webcam level (seam) per user configuration
        y_diff_cm = (gaze_y_work_norm - 0.5) * workspace_height_cm
        angle_rad = np.arctan2(y_diff_cm, distance_cm) if distance_cm > 0 else 0
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
            norm = np.linalg.norm(vec)
            if norm < 1e-6: return 0
            v_unit = vec / norm
            dot = np.dot(v_unit, vertical)
            return np.arccos(np.clip(dot, -1.0, 1.0)) * 180.0 / np.pi
        neck_flexion = angle_with_vertical(cervical_vec)
        trunk_flexion = angle_with_vertical(torso_vec)
        slump_depth = mid_s[2] - mid_h[2]
        return {"neck_flexion": round(float(neck_flexion), 1), "trunk_flexion": round(float(trunk_flexion), 1), "slump_depth_cm": round(float(slump_depth), 2), "is_slumping": slump_depth > 5.0}

    def calculate_biomechanical_risk(self, com, spine):
        if not com or not spine: return 100
        com_strain = abs(com["x"]) * 5 + abs(com["z"]) * 10
        spine_strain = max(0, spine["neck_flexion"] - 10) * 2 + max(0, spine["trunk_flexion"] - 10) * 3
        total_strain = com_strain + spine_strain
        load_score = max(0, 100 - total_strain)
        return round(load_score, 1)

    def calibrate(self, pose_data, context='neutral'):
        if not pose_data or "nose" not in pose_data or "left_shoulder" not in pose_data: return False
        nose, l_s, r_s = pose_data["nose"], pose_data["left_shoulder"], pose_data["right_shoulder"]
        self.baselines[context] = {
            "nose_y": nose['y'],
            "shoulder_y": (l_s['y'] + r_s['y']) / 2,
            "shoulder_width": abs(l_s['x'] - r_s['x']),
            "landmarks": pose_data.copy()
        }
        self.active_context = context
        return True

    def calculate_cva(self, pose_data, physical_pose=None):
        if "nose" not in pose_data or "left_shoulder" not in pose_data: return 60.0
        if physical_pose and "left_ear" in physical_pose:
            mid_s_y = (physical_pose["left_shoulder"]['y'] + physical_pose["right_shoulder"]['y']) / 2
            mid_s_z = (physical_pose["left_shoulder"]['z'] + physical_pose["right_shoulder"]['z']) / 2
            mid_e_y = (physical_pose["left_ear"]['y'] + physical_pose["right_ear"]['y']) / 2
            mid_e_z = (physical_pose["left_ear"]['z'] + physical_pose["right_ear"]['z']) / 2
            dy = mid_s_y - mid_e_y
            dz = abs(mid_e_z - mid_s_z)
            angle_rad = np.arctan2(dy, dz) if dz != 0 else np.pi/2
            return round(angle_rad * 180.0 / np.pi, 1)
        return 60.0

    def calculate_fidget_score(self, distance_cm=60):
        if len(self.raw_buffer) < self.BUFFER_SIZE: return 100.0
        dist_factor = max(1.0, distance_cm / 60.0)
        instability = 0
        for name in ['nose', 'left_shoulder', 'right_shoulder']:
            pts = [b[name] for b in self.raw_buffer if name in b]
            if len(pts) < 10: continue
            std_x, std_y = np.std([p['x'] for p in pts]), np.std([p['y'] for p in pts])
            instability += (std_x + std_y) * (1000 / dist_factor)
        fidget_score = max(0, 100 - ( (instability / 3) * 5))
        return round(fidget_score, 2)

    def calculate_lateral_lean(self, pose_data):
        if "left_shoulder" not in pose_data or "left_hip" not in pose_data: return 0.0
        mid_s_x = (pose_data["left_shoulder"]['x'] + pose_data["right_shoulder"]['x']) / 2
        mid_h_x = (pose_data["left_hip"]['x'] + pose_data["right_hip"]['x']) / 2
        return round(mid_s_x - mid_h_x, 4)

    def calculate_respiration_rate(self, distance_cm=60):
        if len(self.respiration_buffer) < 150: return 0.0
        dist_factor = max(1.0, distance_cm / 60.0)
        data = np.array(self.respiration_buffer)
        data = data - np.mean(data)
        peaks, threshold = 0, 0.0005 * dist_factor
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1] and data[i] > threshold:
                peaks += 1
        return round(np.clip((peaks / (len(self.respiration_buffer) / 30.0)) * 60, 0, 40), 1)

    def analyze(self, pose_data, iris_data=None, hand_data=None, static_duration=0, viewing_angle=0, brightness=100, eye_data=None):
        if not pose_data or "nose" not in pose_data:
            return {"score": 0, "status": "No Person Detected", "feedback": "No person detected."}

        # 0. Self-Leveling Camera (Adjust pitch physically)
        if "nose" in pose_data and "left_shoulder" in pose_data:
            l_s, r_s = pose_data["left_shoulder"], pose_data["right_shoulder"]
            current_pitch = (pose_data["nose"]['y'] - (l_s['y'] + r_s['y'])/2)
            # EMA adjust to physical camera movement
            self.camera_pitch_offset = (self.pitch_ema_alpha * current_pitch) + (1 - self.pitch_ema_alpha) * self.camera_pitch_offset

        self.raw_buffer.append(pose_data.copy())
        if len(self.raw_buffer) > self.BUFFER_SIZE: self.raw_buffer.pop(0)
        distance_cm = self.estimate_distance(iris_data) if iris_data else 60
        fidget_score = self.calculate_fidget_score(distance_cm)

        if "left_shoulder" in pose_data:
            mid_s_y = (pose_data["left_shoulder"]['y'] + pose_data["right_shoulder"]['y']) / 2
            self.respiration_buffer.append(mid_s_y)
            if len(self.respiration_buffer) > self.RESP_BUFFER_SIZE: self.respiration_buffer.pop(0)
            if time.time() - self.last_resp_calc_time > 5:
                self.last_resp_rate = self.calculate_respiration_rate(distance_cm)
                self.last_resp_calc_time = time.time()
        
        is_screen_apnea = self.last_resp_rate > 0 and self.last_resp_rate < 8
        stress_feedback = "🌬️ Breath check: Try deep belly breathing." if is_screen_apnea else None

        for name, lm in pose_data.items():
            if name not in self.smoothed_lms: self.smoothed_lms[name] = lm.copy()
            else:
                for axis in ['x', 'y', 'z']:
                    self.smoothed_lms[name][axis] = self.EMA_ALPHA * lm[axis] + (1 - self.EMA_ALPHA) * self.smoothed_lms[name][axis]
        pose_data = self.smoothed_lms

        is_squinting = eye_data.get('is_squinting', False) if eye_data else False
        is_dim = brightness < 50
        env_feedback = "💡 Room is too dim. Squinting detected." if is_squinting and is_dim else None

        webcam_pitch_correction = 0
        if "left_hip" in pose_data:
            mid_h_y = (pose_data["left_hip"]['y'] + pose_data["right_hip"]['y']) / 2
            if self.is_standing and (mid_h_y - pose_data["nose"]['y']) < 0.3:
                webcam_pitch_correction = 0.05

        if viewing_angle > 15 and 'top' in self.baselines: self.active_context = 'top'
        elif viewing_angle < -15 and 'bottom' in self.baselines: self.active_context = 'bottom'
        else: self.active_context = 'neutral'
        baseline = self.baselines.get(self.active_context, self.baselines.get('neutral'))

        physical_pose = self.normalize_to_physical(pose_data, distance_cm)
        com, spine = self.calculate_com(physical_pose), self.analyze_spine_kinematics(physical_pose)
        bio_score = self.calculate_biomechanical_risk(com, spine)

        l_s, r_s = pose_data["left_shoulder"], pose_data["right_shoulder"]
        shoulder_diff = abs(l_s['y'] - r_s['y'])
        shoulder_score = max(0, 100 - (shoulder_diff * 1000))
        cva_deg = self.calculate_cva(pose_data, physical_pose)
        cva_score = max(0, 100 - (max(0, 55 - cva_deg) * 4))

        protraction_score = 100
        if physical_pose and "left_ear" in pose_data:
            depth_offset = physical_pose["nose"]['z'] - physical_pose["left_shoulder"]['z']
            protraction_score = max(0, 100 - (max(0, depth_offset) * 10))

        nose = pose_data["nose"]
        mid_s_x, mid_s_y = (l_s['x'] + r_s['x'])/2, (l_s['y'] + r_s['y'])/2
        neck_tilt_lat = abs(nose['x'] - mid_s_x)
        neck_score = max(0, 100 - (neck_tilt_lat * 2000))

        slouch_score = 100
        if baseline:
            dist_diff = max(0, (baseline["shoulder_y"] - baseline["nose_y"]) - (mid_s_y + webcam_pitch_correction - nose['y']))
            slouch_score = max(0, 100 - (dist_diff * 1500))

        elbow_score = 100
        if "left_elbow" in pose_data and "left_wrist" in pose_data:
            elbow_score = max(0, 100 - (abs(self.calculate_angle(l_s, pose_data["left_elbow"], pose_data["left_wrist"]) - 105) * 2))

        lateral_lean = self.calculate_lateral_lean(pose_data)
        lateral_lean_score = max(0, 100 - (abs(lateral_lean) * 1000))
        spine_score = 100
        if "left_hip" in pose_data:
            spine_score = max(0, 100 - (abs(mid_s_x - (pose_data["left_hip"]['x'] + pose_data["right_hip"]['x'])/2) * 1000))

        typing_score = self.calculate_typing_strain(pose_data, hand_data)
        self.is_standing = nose['y'] < (baseline["nose_y"] - 0.08 if baseline else 0.38)

        total_score = (bio_score * 0.30 + cva_score * 0.15 + protraction_score * 0.10 + lateral_lean_score * 0.10 + 
                       slouch_score * 0.10 + neck_score * 0.10 + fidget_score * 0.05 + typing_score * 0.05 + shoulder_score * 0.05)

        return {
            "score": round(total_score, 2), "is_standing": self.is_standing, "calibrated": len(self.baselines) > 0,
            "active_context": self.active_context, "distance_cm": distance_cm, "bio_score": bio_score,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4), "shoulder_score": round(shoulder_score, 2),
                "neck_tilt_lat": round(neck_tilt_lat, 4), "slouch_score": round(slouch_score, 2),
                "elbow_score": round(elbow_score, 2), "spine_score": round(spine_score, 2),
                "typing_score": typing_score, "cva": cva_deg, "cva_score": round(cva_score, 2),
                "protraction_score": round(protraction_score, 2), "fidget_score": fidget_score,
                "lateral_lean": lateral_lean, "lateral_lean_score": lateral_lean_score, "respiration_rate": self.last_resp_rate
            },
            "feedback": self._generate_feedback(total_score, slouch_score, neck_score, shoulder_score, typing_score, spine, env_feedback, cva_score, protraction_score, fidget_score, lateral_lean_score, stress_feedback)
        }

    def _generate_feedback(self, total_score, slouch, neck, shoulder, typing=100, spine=None, env=None, cva=100, protraction=100, fidget=100, lateral_lean=100, stress=None):
        if total_score >= 90 and not env and not stress: return "✅ Excellent alignment."
        items = []
        if env: items.append(env)
        if stress: items.append(stress)
        if fidget < 75: items.append("📉 Fatigue alert: High micro-movement/restlessness.")
        if cva < 70: items.append("🐢 Forward head posture.")
        if protraction < 70: items.append("🏹 Shoulders rounded forward.")
        if lateral_lean < 75: items.append("⚖️ Leaning to one side.")
        if slouch < 70: items.append("🪑 Slouching detected.")
        if neck < 70: items.append("🦒 Check neck tilt.")
        if shoulder < 70: items.append("⚖️ Level shoulders.")
        if typing < 75: items.append("⌨️ Typing strain.")
        if spine and spine.get("is_slumping"): items.append("📉 Spine load: Leaning forward.")
        return " | ".join(items) if items else "👍 Good posture."

if __name__ == "__main__":
    analyzer = PostureAnalyzer()
    mock_pose = {"nose": {"x": 0.5, "y": 0.3, "z": 0}, 
                 "left_eye": {"x": 0.48, "y": 0.28, "z": 0}, "right_eye": {"x": 0.52, "y": 0.28, "z": 0},
                 "left_ear": {"x": 0.45, "y": 0.3, "z": 0}, "right_ear": {"x": 0.55, "y": 0.3, "z": 0},
                 "left_shoulder": {"x": 0.4, "y": 0.4, "z": 0}, "right_shoulder": {"x": 0.6, "y": 0.4, "z": 0},
                 "left_elbow": {"x": 0.35, "y": 0.55, "z": 0}, "left_wrist": {"x": 0.4, "y": 0.6, "z": 0}, 
                 "left_hip": {"x": 0.42, "y": 0.7, "z": 0}, "right_hip": {"x": 0.58, "y": 0.7, "z": 0}}
    analyzer.calibrate(mock_pose)
    print(analyzer.analyze(mock_pose))
