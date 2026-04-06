# Tech Stack: Posture-Sense

## Backend
- **Language**: Python 3.10+
- **API Framework**: FastAPI (for real-time websocket/SSE support)
- **Computer Vision**:
  - `mediapipe`: Pose estimation and eye tracking.
  - `opencv-python`: Image capture and processing.
- **System Integration**:
  - `pywin32` / `ctypes`: For Windows-specific monitor and window management.
  - `screeninfo`: To retrieve multi-monitor geometry.

## Frontend
- **Framework**: React.js / Next.js
- **Visualization**: Canvas API or Three.js for 3D skeleton representation (optional).
- **Styling**: Tailwind CSS for a clean, modern UI.

## Data & Communication
- **WebSockets**: To stream pose data from the backend to the UI in real-time.
- **JSON**: Standard for API communication.
