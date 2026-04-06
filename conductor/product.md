# Product Definition: Posture-Sense

## Objective
A desktop application that optimizes user posture at a standing desk with stacked monitors. It uses a webcam to monitor posture and eye-level, then suggests (or dynamically places) text and windows at the optimal position to prevent neck and back strain.

## Core Features
1. **Pose & Eye Tracking**: Real-time monitoring of shoulders, neck, and eye-gaze using MediaPipe.
2. **Posture Scoring**: Calculating the "Posture Score" based on neck-monitor alignment.
3. **Sit/Stand Detection**: Automatically detecting or allowing input for the user's current working mode (sitting vs standing), accounting for the webcam's fixed position on the monitor.
4. **Monitor Awareness**: Integration with Windows API to understand the layout of stacked monitors.
5. **Optimal Placement Suggestion**: Guiding the user to place their active text/window at the best possible point for their current posture and height.

## User Persona
Users with standing desks and multiple (stacked) monitors who want to maintain ergonomic alignment without manual adjustments.
