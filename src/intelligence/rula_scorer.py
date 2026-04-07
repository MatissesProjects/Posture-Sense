import numpy as np
import logging

class RULAScorer:
    """ 
    Implements the Rapid Upper Limb Assessment (RULA) scoring logic.
    Scores range from 1 (low risk) to 7 (high risk).
    """
    def __init__(self):
        pass

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

    def score_neck(self, pose_data):
        """ RULA Neck Score: 1-4 """
        if "nose" not in pose_data or "left_shoulder" not in pose_data:
            return 1
        
        # Calculate neck flex/extension angle relative to vertical
        # In a 2D front view, we mostly detect lateral tilt
        l_shoulder = pose_data["left_shoulder"]
        r_shoulder = pose_data["right_shoulder"]
        mid_shoulder = {"x": (l_shoulder['x'] + r_shoulder['x'])/2, "y": (l_shoulder['y'] + r_shoulder['y'])/2}
        nose = pose_data["nose"]
        
        # Angle of nose relative to vertical line from mid-shoulder
        vertical_pt = {"x": mid_shoulder["x"], "y": mid_shoulder["y"] - 0.1}
        angle = self.calculate_angle(vertical_pt, mid_shoulder, nose)
        
        if angle < 10: return 1
        if angle < 20: return 2
        return 3 # 3+ for severe tilt

    def score_trunk(self, pose_data, is_standing=False):
        """ RULA Trunk Score: 1-4 """
        if is_standing: return 1 # Standing is handled by REBA usually, but for RULA we assume neutral
        
        if "left_hip" not in pose_data or "left_shoulder" not in pose_data:
            return 1
            
        l_hip = pose_data["left_hip"]
        r_hip = pose_data["right_hip"]
        mid_hip = {"x": (l_hip['x'] + r_hip['x'])/2, "y": (l_hip['y'] + r_hip['y'])/2}
        
        l_shoulder = pose_data["left_shoulder"]
        r_shoulder = pose_data["right_shoulder"]
        mid_shoulder = {"x": (l_shoulder['x'] + r_shoulder['x'])/2, "y": (l_shoulder['y'] + r_shoulder['y'])/2}
        
        # Trunk angle relative to vertical
        vertical_pt = {"x": mid_hip["x"], "y": mid_hip["y"] - 0.1}
        angle = self.calculate_angle(vertical_pt, mid_hip, mid_shoulder)
        
        if angle < 5: return 1
        if angle < 20: return 2
        if angle < 60: return 3
        return 4

    def score_upper_arm(self, pose_data):
        """ RULA Upper Arm Score: 1-4 """
        if "left_shoulder" not in pose_data or "left_elbow" not in pose_data:
            return 1
            
        l_shoulder = pose_data["left_shoulder"]
        l_elbow = pose_data["left_elbow"]
        
        # Upper arm angle relative to trunk (vertical)
        vertical_pt = {"x": l_shoulder["x"], "y": l_shoulder["y"] + 0.1}
        angle = self.calculate_angle(vertical_pt, l_shoulder, l_elbow)
        
        if angle < 20: return 1
        if angle < 45: return 2
        if angle < 90: return 3
        return 4

    def get_grand_score(self, pose_data, is_standing=False):
        """ 
        Simplified Grand Score calculation.
        In a full RULA, this involves Table A and Table B.
        """
        s_neck = self.score_neck(pose_data)
        s_trunk = self.score_trunk(pose_data, is_standing)
        s_arm = self.score_upper_arm(pose_data)
        
        # Simplified aggregation
        raw_score = (s_neck + s_trunk + s_arm) / 3.0
        # Map to 1-7
        grand_score = int(np.clip(raw_score * 2, 1, 7))
        
        return {
            "grand_score": grand_score,
            "breakdown": {
                "neck": s_neck,
                "trunk": s_trunk,
                "upper_arm": s_arm
            },
            "risk_level": self.get_risk_level(grand_score)
        }

    def get_risk_level(self, score):
        if score <= 2: return "Negligible Risk"
        if score <= 4: return "Low Risk (Further investigation needed)"
        if score <= 6: return "Medium Risk (Investigate and change soon)"
        return "High Risk (Investigate and change immediately)"

if __name__ == "__main__":
    scorer = RULAScorer()
    mock_pose = {"nose": {"x": 0.5, "y": 0.3}, "left_shoulder": {"x": 0.4, "y": 0.4}, "right_shoulder": {"x": 0.6, "y": 0.4}}
    print(scorer.get_grand_score(mock_pose))
