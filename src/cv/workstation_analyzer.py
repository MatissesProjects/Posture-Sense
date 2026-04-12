import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class WorkstationAnalyzer:
    """
    Analyzes the physical workstation environment (monitors, keyboard, desk)
    using computer vision and heuristics.
    """
    def __init__(self):
        self.last_env_data = {}

    def analyze_environment(self, frame, pose_data=None, physical_pose=None):
        """
        Attempts to detect workstation components in the frame.
        """
        if frame is None: return {}
        
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 1. Screen Detection (Looking for high-contrast rectangles)
        # Often screens are bright or have distinct borders
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rects = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4: # Rectangle
                area = cv2.contourArea(c)
                if area > (w * h * 0.05): # At least 5% of frame
                    rects.append(approx)

        # 2. Desk Plane Estimation (Looking for horizontal lines in lower 1/3)
        lines = cv2.HoughLinesP(edged[int(h*0.6):, :], 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        desk_y = None
        if lines is not None:
            # Find the most consistent horizontal-ish line
            y_coords = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y1 - y2) < 10: # Horizontal
                    y_coords.append(y1 + int(h*0.6))
            if y_coords:
                desk_y = int(np.median(y_coords))

        # 3. Generate Recommendations
        recommendations = []
        if pose_data and "nose" in pose_data:
            eye_y = pose_data["nose"]["y"] * h
            
            # Monitor Height Recommendation
            # Ideal: Top 1/3 of monitor at eye level
            if rects:
                # Find the largest/most centered rectangle as primary monitor
                main_rect = sorted(rects, key=cv2.contourArea, reverse=True)[0]
                m_top = np.min(main_rect[:, 0, 1])
                m_bottom = np.max(main_rect[:, 0, 1])
                m_height = m_bottom - m_top
                
                ideal_eye_y = m_top + (m_height * 0.2) # Top 20%
                if eye_y > ideal_eye_y + 50:
                    recommendations.append("Monitor is too LOW. Raise it by ~5-10cm.")
                elif eye_y < ideal_eye_y - 50:
                    recommendations.append("Monitor is too HIGH. Lower it slightly.")

            # Desk Height Recommendation
            if desk_y and "left_elbow" in pose_data:
                elbow_y = pose_data["left_elbow"]["y"] * h
                if desk_y < elbow_y - 30:
                    recommendations.append("Desk is too HIGH. Lower your desk or raise your chair.")
                elif desk_y > elbow_y + 100:
                    recommendations.append("Desk is too LOW. Raise your desk.")

        self.last_env_data = {
            "monitor_detected": len(rects) > 0,
            "desk_detected": desk_y is not None,
            "desk_y": desk_y / h if desk_y else None,
            "recommendations": recommendations
        }
        return self.last_env_data
