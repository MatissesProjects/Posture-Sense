# Implementation Plan: Track 004 - System Integration

## Phase 1: Workspace Geometry Detection
- [ ] Use `screeninfo` to get monitor resolution and position.
- [ ] Analyze `monitors_and_webcam_layout.png` to understand the relative position of the webcam and monitors.
- [ ] Detect "stacked" layout (one monitor's Y-coordinate above the other).

## Phase 2: Active Window Tracking
- [ ] Use `pygetwindow` to track the "active" window's position.
- [ ] Implement a function to calculate the "Ergonomic Sweet Spot" (ESS) on the stacked monitors.

## Phase 3: Text Placement Suggestion
- [ ] Create a logic to suggest window movement/text adjustment if it's too high/low.
- [ ] Visualize the "Sweet Spot" on the dashboard UI.

## Phase 4: Contextual Logic
- [ ] Implement detection of sustain posture vs. intentional movement.
- [ ] Integrate "neutral baseline" calibration (as per Phase 4 of original plan).
- [ ] Store/Log posture metrics over time for reporting.
