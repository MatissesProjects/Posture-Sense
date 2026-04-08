# Implementation Plan: Track 015 - Adaptive Calibration

## Phase 1: Contextual Neutral Baselines
- [ ] Implement "Dual-Neutral" calibration: one for Top monitor focus, one for Bottom monitor focus.
- [ ] Automatically switch active baseline based on Gaze Point.

## Phase 2: Environmental Light Audit
- [ ] Implement a lighting level check using CV pixel intensity.
- [ ] Detect "Squinting" patterns (high eyelid closure without blinking) and correlate with low light.
- [ ] Suggest lighting adjustments: "Your room is too dark, causing you to lean forward."

## Phase 3: Angle Compensation
- [ ] Calculate "Webcam Pitch" (camera tilt) relative to the user's vertical axis.
- [ ] Correct landmark coordinates for "Foreshortening" when the camera looks up at a standing user.

## Phase 4: Robust Filtering
- [ ] Implement "Primary User" focus (ignore background people).
- [ ] Add temporal smoothing to landmarks to prevent jitter in low light.
