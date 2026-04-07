# Implementation Plan: Track 003 - Web Interface

## Phase 1: Backend API Skeleton
- [x] Initialize a FastAPI project in `src/api`.
- [x] Set up a WebSocket endpoint for real-time landmark data.
- [x] Integrate `CVWorker` for live data streaming.

## Phase 2: Frontend Scaffold
- [x] Initialize a React/Next.js app in `web/`.
- [x] Install additional UI components (e.g., Lucide Icons).

## Phase 3: Visualization & Feedback
- [x] Develop a Canvas-based skeleton visualizer in `PostureCanvas.tsx`.
- [x] Create a "Posture Score" gauge component in `PostureDashboard.tsx`.
- [x] Implement real-time feedback messages and calibration/mirror controls.

## Phase 4: Full Loop Integration
- [x] Connect the CV engine (Track 001) output to the FastAPI WebSocket.
- [x] Integrate real-time scoring (Track 002) results into the UI.
