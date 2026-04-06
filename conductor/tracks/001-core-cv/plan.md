# Implementation Plan: Track 001 - Core CV Engine

## Phase 1: Environment Setup
- [x] Create a virtual environment and install `mediapipe`, `opencv-python`, `numpy`.
- [x] Implement a basic `capture.py` to test webcam access.

## Phase 2: MediaPipe Pose Integration
- [x] Integrate MediaPipe Pose solution to detect 33 landmarks.
- [x] Filter landmarks to only include relevant ones (shoulders, neck, eyes).
- [x] Implement a visualizer for real-time verification.

## Phase 3: Eye & Iris Tracking
- [x] Integrate MediaPipe Iris or Face Mesh (refine iris detection).
- [x] Calculate gaze direction vector (relative to the screen).

## Phase 4: Data Pipeline
- [x] Create a data structure to hold pose/eye landmarks.
- [x] Serialize landmarks to JSON for the backend API.
