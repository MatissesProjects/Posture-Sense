# Posture-Sense

An intelligent desktop application designed to optimize user posture at standing desks with **stacked monitor** configurations. Using computer vision, it monitors your ergonomic alignment and dynamically suggests the best placement for your active windows.

![Dashboard Preview](web/public/next.svg) <!-- Placeholder for actual screenshot -->

## 🚀 Key Features

- **Real-Time Pose Tracking**: Monitors neck tilt, shoulder levelness, and slouching using MediaPipe.
- **Stacked Monitor Awareness**: Automatically detects your monitor layout and handles asymmetrical vertical stacks.
- **Active Window Tracking**: Identifies where you are currently working and calculates the "Ergonomic Sweet Spot" (ESS) relative to your eye level.
- **Gaze Contextualization**: Uses eye tracking to detect which monitor you are looking at and adjusts feedback accordingly.
- **Modern Dashboard**: A Next.js-powered interface with a live skeleton visualizer, posture score gauge, and actionable tips.

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, OpenCV, MediaPipe.
- **Frontend**: React, Next.js, TypeScript, Tailwind CSS, Lucide Icons.
- **System**: `pygetwindow` for window management, `screeninfo` for monitor geometry.

## 🏃 Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Node.js & npm
- A webcam

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/posture-sense.git
cd posture-sense

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd web
npm install
```

## 🖥 How to Run

You need two terminal windows:

**Terminal 1 (Backend):**
```bash
# From the project root
PYTHONPATH=. python src/api/main.py
```

**Terminal 2 (Frontend):**
```bash
cd web
npm run dev
```

Visit `http://localhost:3000` to view the dashboard.

## ⌨️ Controls
- **'c'** (in terminal or UI): Calibrate your neutral "good" posture.
- **'m'** (in terminal or UI): Toggle mirror mode if your webcam is flipped.
- **'q'**: Quit the application.

## 🛤 Roadmap
- [x] Track 001: Core CV Engine
- [x] Track 002: Posture Intelligence
- [x] Track 003: Web Interface
- [x] Track 004: System Integration
- [x] Track 010: Workspace Geometry Refinement
- [ ] Track 005: Standardized Ergonomics (RULA/REBA)
- [ ] Track 006: Behavioral Gamification
- [ ] Track 009: Smart Stretch Interventions

---
Developed with ❤️ for better backs.
