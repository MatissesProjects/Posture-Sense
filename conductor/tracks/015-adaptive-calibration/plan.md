# Implementation Plan: Track 015 - Adaptive Calibration

## Phase 1: Contextual Neutral Baselines
- [x] Implement "Dual-Neutral" calibration: one for Top monitor focus, one for Bottom monitor focus.
- [x] Automatically switch active baseline based on Gaze Point.

## Phase 2: Environmental Light Audit
- [x] Implement a lighting level check using CV pixel intensity.
- [x] Detect "Squinting" patterns (high eyelid closure without blinking) and correlate with low light.
- [x] Suggest lighting adjustments: "Your room is too dim, causing you to lean forward."

## Phase 3: Angle Compensation
- [x] Calculate "Webcam Pitch" (camera tilt) relative to the user's vertical axis.
- [x] Correct landmark coordinates for "Foreshortening" when the camera looks up at a standing user.

## Phase 4: Robust Filtering
- [x] Implement "Primary User" focus (ignore background people) - handled by MediaPipe Pose defaults.
- [x] Add temporal smoothing to landmarks to prevent jitter in low light.

