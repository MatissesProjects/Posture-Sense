import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.baseline = None  # To be set during calibration
        self.is_standing = False

    def calculate_angle(self, a, b, c):
        """Calculates the angle between three points (b is the vertex)."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def calibrate(self, pose_data):
        """Sets the baseline posture for the user."""
        if not pose_data or len(pose_data) < 9:
            return False
        
        nose = pose_data[0]
        l_shoulder = pose_data[7]
        r_shoulder = pose_data[8]
        
        self.baseline = {
            "nose_y": nose['y'],
            "shoulder_y": (l_shoulder['y'] + r_shoulder['y']) / 2,
            "shoulder_width": abs(l_shoulder['x'] - r_shoulder['x'])
        }
        logger.info(f"Calibration successful: {self.baseline}")
        return True

    def analyze(self, pose_data):
        """
        Analyzes pose data to determine posture score and sit/stand status.
        pose_data is expected to be a list of landmarks from CVPipeline.
        IDs: 0=Nose, 11=L-Shoulder, 12=R-Shoulder
        """
        if not pose_data or len(pose_data) < 9:
            return {"score": 0, "status": "No Person Detected", "is_standing": self.is_standing}

        # Landmarks (normalized 0.0 to 1.0)
        nose = pose_data[0]
        l_shoulder = pose_data[7]  # ID 11
        r_shoulder = pose_data[8]  # ID 12

        # 1. Shoulder Levelness (lower is better)
        shoulder_diff = abs(l_shoulder['y'] - r_shoulder['y'])
        shoulder_score = max(0, 100 - (shoulder_diff * 500)) # 0.2 diff = 0 score

        # 2. Neck Tilt (approximation using nose and mid-shoulder)
        mid_shoulder_x = (l_shoulder['x'] + r_shoulder['x']) / 2
        mid_shoulder_y = (l_shoulder['y'] + r_shoulder['y']) / 2
        
        # Vertical alignment: Nose should be roughly above mid-shoulder
        neck_tilt = abs(nose['x'] - mid_shoulder_x)
        neck_score = max(0, 100 - (neck_tilt * 1000)) # 0.1 diff = 0 score

        # 3. Slouching (Nose height relative to shoulders)
        # Using baseline if available
        current_nose_to_shoulder = mid_shoulder_y - nose['y']
        slouch_score = 100
        if self.baseline:
            baseline_dist = self.baseline["shoulder_y"] - self.baseline["nose_y"]
            # If current distance is much smaller than baseline, they are slouching
            dist_diff = max(0, baseline_dist - current_nose_to_shoulder)
            slouch_score = max(0, 100 - (dist_diff * 1000))

        # 4. Head Height (for sit/stand detection)
        # If calibrated, compare against baseline. Otherwise use heuristic.
        if self.baseline:
            # If nose is significantly higher (lower Y) than baseline, assume they stood up
            # If they calibrated while sitting, standing will be ~0.2-0.3 difference
            if nose['y'] < self.baseline["nose_y"] - 0.1:
                self.is_standing = True
            elif nose['y'] > self.baseline["nose_y"] + 0.1:
                self.is_standing = False
        else:
            # Heuristic fallback
            if nose['y'] < 0.35:
                self.is_standing = True
            else:
                self.is_standing = False

        total_score = (shoulder_score + neck_score + slouch_score) / 3
        
        return {
            "score": round(total_score, 2),
            "is_standing": self.is_standing,
            "calibrated": self.baseline is not None,
            "metrics": {
                "shoulder_diff": round(shoulder_diff, 4),
                "neck_tilt": round(neck_tilt, 4),
                "slouch_score": round(slouch_score, 2)
            }
        }

if __name__ == "__main__":
    analyzer = PostureAnalyzer()
    # Mock data: Perfect posture
    mock_pose = [
        {"id": 0, "x": 0.5, "y": 0.3}, # Nose
        {"id": 1, "x": 0.5, "y": 0.3}, # Placeholder 1-6
        {"id": 2, "x": 0.5, "y": 0.3},
        {"id": 3, "x": 0.5, "y": 0.3},
        {"id": 4, "x": 0.5, "y": 0.3},
        {"id": 5, "x": 0.5, "y": 0.3},
        {"id": 6, "x": 0.5, "y": 0.3},
        {"id": 11, "x": 0.4, "y": 0.4}, # L-Shoulder
        {"id": 12, "x": 0.6, "y": 0.4}  # R-Shoulder
    ]
    analyzer.calibrate(mock_pose)
    print(analyzer.analyze(mock_pose))
