# Tracks Registry: Posture-Sense

The project is divided into four main tracks to ensure focused development and robust integration.

## Track List

| ID | Name | Description | Status | Link |
| :--- | :--- | :--- | :--- | :--- |
| **001** | [**Core CV Engine**](./tracks/001-core-cv/index.md) | Mediapipe integration, webcam capture, and basic joint tracking. | *Completed* | [Plan](./tracks/001-core-cv/plan.md) |
| **002** | [**Posture Intelligence**](./tracks/002-posture-intelligence/index.md) | Scoring logic, neck/back alignment, sit/stand detection, and advanced joint/spine metrics. | *Completed* | [Plan](./tracks/002-posture-intelligence/plan.md) |
| **003** | [**Web Interface**](./tracks/003-web-interface/index.md) | React frontend and FastAPI backend for real-time user feedback and historical posture reporting. | *Completed* | [Plan](./tracks/003-web-interface/plan.md) |
| **004** | [**System Integration**](./tracks/004-system-monitor-integration/index.md) | Monitor layout detection, viewing angle optimization, and eye-tracking contextualization for Windows. | *Completed* | [Plan](./tracks/004-system-monitor-integration/plan.md) |
| **005** | [**Standardized Ergonomics**](./tracks/005-standardized-ergonomics/index.md) | Implementation of RULA/REBA scoring frameworks and industry-standard ergonomic metrics. | *Completed* | [Plan](./tracks/005-standardized-ergonomics/plan.md) |
| **006** | [**Behavioral Gamification**](./tracks/006-behavioral-gamification/index.md) | Micro-interventions, 20-20-20 rule for eye strain, and habit-forming gamification. | *Completed* | [Plan](./tracks/006-behavioral-gamification/plan.md) |
| **007** | [**Predictive Analytics**](./tracks/007-predictive-analytics/index.md) | Longitudinal posture data storage, fatigue prediction modeling, and gaze heatmaps. | *Completed* | [Plan](./tracks/007-predictive-analytics/plan.md) |
| **008** | [**Privacy & Security**](./tracks/008-privacy-security/index.md) | Formalized on-device processing, data encryption, and user privacy dashboards. | *Not Started* | [Plan](./tracks/008-privacy-security/plan.md) |
| **009** | [**Smart Stretch Interventions**](./tracks/009-stretch-interventions/index.md) | Posture-aware stretch suggestions, guided micro-breaks, and recovery tracking. | *Completed* | [Plan](./tracks/009-stretch-interventions/plan.md) |
| **010** | [**Workspace Refinement**](./tracks/010-workspace-refinement/index.md) | Support for asymmetrical monitor layouts, webcam anchoring, and UI geometry editor. | *Completed* | [Plan](./tracks/010-workspace-refinement/plan.md) |
| **011** | [**Hand & Wrist Ergonomics**](./tracks/011-hand-wrist-ergonomics/index.md) | Monitoring typing strain, wrist deviation, and RSI risk factors. | *Completed* | [Plan](./tracks/011-hand-wrist-ergonomics/plan.md) |
| **012** | [**Biomechanical Modeling**](./tracks/012-biomechanical-modeling/index.md) | 3D physical modeling, Center of Mass (CoM), and kinematic spine chain analysis. | *Completed* | [Plan](./tracks/012-biomechanical-modeling/plan.md) |
| **013** | [**Predictive Fatigue**](./tracks/013-predictive-fatigue/index.md) | Machine learning models to forecast and prevent postural and eye fatigue. | *Not Started* | [Plan](./tracks/013-predictive-fatigue/plan.md) |
| **014** | [**Corporate Reporting**](./tracks/014-corporate-reporting/index.md) | High-fidelity analytics, strain heatmaps, and professional PDF reports. | *Not Started* | [Plan](./tracks/014-corporate-reporting/plan.md) |
| **015** | [**Adaptive Calibration**](./tracks/015-adaptive-calibration/index.md) | Robustness to environment, lighting, and camera orientation changes. | *Not Started* | [Plan](./tracks/015-adaptive-calibration/plan.md) |


## Track Conventions
- Use descriptive commit messages: `track-xxx: message`.
- Each track should have its own `plan.md` and `index.md`.
- Keep track-specific code in its own directory if possible (e.g., `src/cv/`, `src/api/`).
