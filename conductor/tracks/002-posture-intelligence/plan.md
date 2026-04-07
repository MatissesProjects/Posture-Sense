# Implementation Plan: Track 002 - Posture Intelligence

## Phase 1: Metric Definition
- [ ] Research and define ergonomic angles for a standing desk with stacked monitors.
- [ ] Map MediaPipe landmarks to these metrics (e.g., neck-to-shoulder angle).

## Phase 2: Scoring Algorithm
- [ ] Implement a scoring function that weights different postural elements.
- [ ] Normalize the score to a 0-100 range.

## Phase 3: Sit/Stand Detection
- [ ] Design a detection mechanism based on head height relative to shoulders/webcam.
- [ ] Add an interface to manually toggle/input sit-stand status for calibration.

## Phase 4: Feedback & Severity Logic
- [ ] Define score-based thresholds for feedback (e.g., "Adjust monitor height").
- [ ] Implement **Severity Levels** (Low, Medium, High Risk) for each postural issue.
- [ ] Create a **Specific Remediation Tip** generator (e.g., "Raise your screen," "Keep elbows at 90°").

## Phase 5: Advanced Posture Metrics
- [ ] **Elbow/Wrist Angle**: Extract landmarks 13-16 to assess typing/interaction strain.
- [ ] **Spine Curvature/Torso Angle**: Calculate angles using Hip -> Mid-Back -> Neck points for slouching detection.
- [ ] **Head Tilt/Rotation**: Implement precise 3D head orientation relative to the vertical axis.
