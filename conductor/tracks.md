# Tracks Registry: Posture-Sense

The project is divided into four main tracks to ensure focused development and robust integration.

## Track List

| ID | Name | Description | Status | Link |
| :--- | :--- | :--- | :--- | :--- |
| **001** | [**Core CV Engine**](./tracks/001-core-cv/index.md) | Mediapipe integration, webcam capture, and basic joint tracking. | *Not Started* | [Plan](./tracks/001-core-cv/plan.md) |
| **002** | [**Posture Intelligence**](./tracks/002-posture-intelligence/index.md) | Scoring logic, neck/back alignment, and sit/stand detection. | *Not Started* | [Plan](./tracks/002-posture-intelligence/plan.md) |
| **003** | [**Web Interface**](./tracks/003-web-interface/index.md) | React frontend and FastAPI backend for real-time user feedback. | *Not Started* | [Plan](./tracks/003-web-interface/plan.md) |
| **004** | [**System Integration**](./tracks/004-system-monitor-integration/index.md) | Monitor layout detection and text placement optimization for Windows. | *Not Started* | [Plan](./tracks/004-system-monitor-integration/plan.md) |

## Track Conventions
- Use descriptive commit messages: `track-xxx: message`.
- Each track should have its own `plan.md` and `index.md`.
- Keep track-specific code in its own directory if possible (e.g., `src/cv/`, `src/api/`).
