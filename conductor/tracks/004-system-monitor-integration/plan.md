# Implementation Plan: Track 004 - System Integration

## Phase 1: Workspace Geometry Detection
- [x] Use `screeninfo` to get monitor resolution and position.
- [x] Analyze `monitors_and_webcam_layout.png` to understand the relative position of the webcam and monitors.
- [x] Detect "stacked" layout (one monitor's Y-coordinate above the other).
- [ ] **Monitor Geometry Input**: Allow users to input physical dimensions (cm/inches) for accurate distance calculations.

## Phase 2: Active Window Tracking
- [x] Use `pygetwindow` to track the "active" window's position.
- [x] Implement a function to calculate the "Ergonomic Sweet Spot" (ESS) on the stacked monitors.

## Phase 3: Viewing Angle & Distance Calculation
- [x] Implement logic to calculate **Viewing Angle** ($\theta$) between the user's eyes and the active text area.
- [x] Implement **Viewing Distance** ($D$) estimation using head/eye tracking data.
- [x] Ensure $\theta$ is within the ergonomic safe range ($15^\circ$ to $30^\circ$ downward).

## Phase 4: Text Placement Suggestion
- [ ] Create a logic to suggest window movement/text adjustment if it's too high/low.
- [ ] Visualize the "Sweet Spot" on the dashboard UI.

## Phase 5: Advanced Integration & Context
- [ ] **Eye-Tracking Contextualization**: Use gaze data to confirm if the user is looking at the primary or secondary monitor, adjusting warning urgency accordingly.
- [ ] Implement detection of sustained posture vs. intentional movement.
- [ ] Integrate "neutral baseline" calibration (as per Phase 4 of original plan).
- [ ] Store/Log posture metrics over time for reporting.
