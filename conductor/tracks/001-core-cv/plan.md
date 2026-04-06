# Implementation Plan: Track 001 - Core CV Engine

## Phase 1: Environment Setup
- [ ] Create a virtual environment and install `mediapipe`, `opencv-python`, `numpy`.
- [ ] Implement a basic `capture.py` to test webcam access.

## Phase 2: MediaPipe Pose Integration
- [ ] Integrate MediaPipe Pose solution to detect 33 landmarks.
- [ ] Filter landmarks to only include relevant ones (shoulders, neck, eyes).
- [ ] Implement a visualizer for real-time verification.

## Phase 3: Eye & Iris Tracking
- [ ] Integrate MediaPipe Iris or Face Mesh (refine iris detection).
- [ ] Calculate gaze direction vector (relative to the screen).

## Phase 4: Data Pipeline
- [ ] Create a data structure to hold pose/eye landmarks.
- [ ] Serialize landmarks to JSON for the backend API.
