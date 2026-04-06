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

## Phase 4: Feedback Generation
- [ ] Define score-based thresholds for feedback (e.g., "Adjust monitor height").
- [ ] Create a "Correction Prompt" generator for the UI.
