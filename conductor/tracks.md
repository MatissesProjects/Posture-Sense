# Tracks Registry: Posture-Sense

The project is divided into four main tracks to ensure focused development and robust integration.

## Track List

| ID | Name | Description | Status | Link |
| :--- | :--- | :--- | :--- | :--- |
| **001** | [**Core CV Engine**](./tracks/001-core-cv/index.md) | Mediapipe integration, webcam capture, and basic joint tracking. | *Completed* | [Plan](./tracks/001-core-cv/plan.md) |
| **002** | [**Posture Intelligence**](./tracks/002-posture-intelligence/index.md) | Scoring logic, neck/back alignment, sit/stand detection, and advanced joint/spine metrics. | *Completed* | [Plan](./tracks/002-posture-intelligence/plan.md) |
| **003** | [**Web Interface**](./tracks/003-web-interface/index.md) | React frontend and FastAPI backend for real-time user feedback and historical posture reporting. | *Completed* | [Plan](./tracks/003-web-interface/plan.md) |
| **004** | [**System Integration**](./tracks/004-system-monitor-integration/index.md) | Monitor layout detection, viewing angle optimization, and eye-tracking contextualization for Windows. | *Completed* | [Plan](./tracks/004-system-monitor-integration/plan.md) |
| **005** | [**Standardized Ergonomics**](./tracks/005-standardized-ergonomics/index.md) | Implementation of RULA/REBA scoring frameworks and industry-standard ergonomic metrics. | *Not Started* | [Plan](./tracks/005-standardized-ergonomics/plan.md) |
| **006** | [**Behavioral Gamification**](./tracks/006-behavioral-gamification/index.md) | Micro-interventions, 20-20-20 rule for eye strain, and habit-forming gamification. | *Not Started* | [Plan](./tracks/006-behavioral-gamification/plan.md) |
| **007** | [**Predictive Analytics**](./tracks/007-predictive-analytics/index.md) | Longitudinal posture data storage, fatigue prediction modeling, and gaze heatmaps. | *Not Started* | [Plan](./tracks/007-predictive-analytics/plan.md) |
| **008** | [**Privacy & Security**](./tracks/008-privacy-security/index.md) | Formalized on-device processing, data encryption, and user privacy dashboards. | *Not Started* | [Plan](./tracks/008-privacy-security/plan.md) |
| **009** | [**Smart Stretch Interventions**](./tracks/009-stretch-interventions/index.md) | Posture-aware stretch suggestions, guided micro-breaks, and recovery tracking. | *Not Started* | [Plan](./tracks/009-stretch-interventions/plan.md) |

## Track Conventions
- Use descriptive commit messages: `track-xxx: message`.
- Each track should have its own `plan.md` and `index.md`.
- Keep track-specific code in its own directory if possible (e.g., `src/cv/`, `src/api/`).
