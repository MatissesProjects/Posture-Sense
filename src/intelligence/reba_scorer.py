import numpy as np

class REBAScorer:
    """ 
    Implements the Rapid Entire Body Assessment (REBA) scoring logic.
    Scores range from 1 (negligible risk) to 15 (very high risk).
    """
    def __init__(self):
        # Table A: Trunk (1-5), Neck (1-3), Leg (1-4)
        # Simplified representation: 3D lookup or nested dicts
        self.table_a = {
            # trunk_score: { neck_score: { leg_score: result } }
            1: {1: {1:1, 2:2, 3:3, 4:4}, 2: {1:2, 2:3, 3:4, 4:5}, 3: {1:3, 2:4, 3:5, 4:6}},
            2: {1: {1:2, 2:3, 3:4, 4:5}, 2: {1:3, 2:4, 3:5, 4:6}, 3: {1:4, 2:5, 3:6, 4:7}},
            3: {1: {1:3, 2:4, 3:5, 4:6}, 2: {1:4, 2:5, 3:6, 4:7}, 3: {1:5, 2:6, 3:7, 4:8}},
            4: {1: {1:4, 2:5, 3:6, 4:7}, 2: {1:5, 2:6, 3:7, 4:8}, 3: {1:6, 2:7, 3:8, 4:9}},
            5: {1: {1:6, 2:7, 3:8, 4:9}, 2: {1:7, 2:8, 3:9, 4:10}, 3: {1:8, 2:9, 3:10, 4:11}},
        }
        
        # Table B: Upper Arm (1-6), Lower Arm (1-2), Wrist (1-3)
        self.table_b = {
            1: {1: {1:1, 2:2, 3:3}, 2: {1:2, 2:3, 3:4}},
            2: {1: {1:1, 2:2, 3:3}, 2: {1:3, 2:4, 3:5}},
            3: {1: {1:3, 2:4, 3:5}, 2: {1:4, 2:5, 3:6}},
            4: {1: {1:4, 2:5, 3:6}, 2: {1:5, 2:6, 3:7}},
            5: {1: {1:6, 2:7, 3:8}, 2: {1:7, 2:8, 3:9}},
            6: {1: {1:7, 2:8, 3:9}, 2: {1:8, 2:9, 3:10}},
        }

        # Table C: Score A (1-12), Score B (1-12)
        # Just a snippet of the logic since it's a large matrix
        # Typically result = ScoreA + ScoreB adjustment from Table C
        pass

    def calculate_angle(self, a, b, c):
        a, b, c = np.array([a['x'], a['y']]), np.array([b['x'], b['y']]), np.array([b['x'], b['y']])
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def score_neck(self, pose_data):
        """ REBA Neck: 1 (0-20 deg flexion), 2 (>20 deg flexion or extension) """
        if "nose" not in pose_data or "left_shoulder" not in pose_data: return 1
        l_s, r_s, nose = pose_data["left_shoulder"], pose_data["right_shoulder"], pose_data["nose"]
        mid_s = {"x": (l_s['x'] + r_s['x'])/2, "y": (l_s['y'] + r_s['y'])/2}
        v_pt = {"x": mid_s["x"], "y": mid_s["y"] - 0.1}
        # In 2D, we estimate pitch via vertical offset
        angle = self.calculate_angle(v_pt, mid_s, nose)
        
        score = 1 if angle < 20 else 2
        # Extension adjustment: if nose is significantly high, it's extension
        if nose['y'] < mid_s['y'] - 0.15: score = 2
        return score

    def score_trunk(self, pose_data):
        """ REBA Trunk: 1 (upright), 2 (0-20), 3 (20-60), 4 (>60) """
        if "left_hip" not in pose_data or "left_shoulder" not in pose_data: return 1
        l_h, r_h = pose_data["left_hip"], pose_data["right_hip"]
        mid_h = {"x": (l_h['x'] + r_h['x'])/2, "y": (l_h['y'] + r_h['y'])/2}
        l_s, r_s = pose_data["left_shoulder"], pose_data["right_shoulder"]
        mid_s = {"x": (l_s['x'] + r_s['x'])/2, "y": (l_s['y'] + r_s['y'])/2}
        v_pt = {"x": mid_h["x"], "y": mid_h["y"] - 0.1}
        angle = self.calculate_angle(v_pt, mid_h, mid_s)
        
        if angle < 5: return 1
        if angle < 20: return 2
        if angle < 60: return 3
        return 4

    def score_legs(self, is_standing):
        """ REBA Legs: 1 (standing both legs), 2 (one leg/unstable) """
        return 1 if is_standing else 1 # Default to stable support for desk work

    def get_grand_score(self, pose_data, is_standing=False, static_duration=0):
        """ Simplified REBA aggregation. """
        s_neck = self.score_neck(pose_data)
        s_trunk = self.score_trunk(pose_data)
        s_leg = self.score_legs(is_standing)
        
        # Table A lookup
        score_a = self.table_a.get(s_trunk, self.table_a[1]).get(s_neck, {1:1})[s_leg]
        
        # Simplified Arm/Wrist score (Group B)
        # Assuming Upper Arm 1, Lower Arm 1, Wrist 1 for neutral
        score_b = 1 
        
        # Final Score C lookup (simplified as linear combination for now)
        final_score = score_a + (1 if static_duration > 60 else 0)
        
        return {
            "grand_score": final_score,
            "risk_level": self.get_risk_level(final_score),
            "breakdown": {"neck": s_neck, "trunk": s_trunk, "legs": s_leg}
        }

    def get_risk_level(self, score):
        if score <= 1: return "Negligible"
        if score <= 3: return "Low"
        if score <= 7: return "Medium"
        if score <= 10: return "High"
        return "Very High"

if __name__ == "__main__":
    scorer = REBAScorer()
    mock_pose = {"nose": {"x": 0.5, "y": 0.3}, "left_shoulder": {"x": 0.4, "y": 0.4}, "right_shoulder": {"x": 0.6, "y": 0.4}, "left_hip": {"x": 0.45, "y": 0.7}, "right_hip": {"x": 0.55, "y": 0.7}}
    print(scorer.get_grand_score(mock_pose))
