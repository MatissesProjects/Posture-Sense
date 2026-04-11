# Privacy Policy: Posture-Sense

Posture-Sense is built with a **Privacy-First** architecture. As a tool that uses your webcam, we take your data security seriously.

## 🔒 Local-Only Processing Mandate
- **No Cloud Uploads**: Your video feed is processed entirely on your local machine. No images, frames, or video data are ever sent to any remote server.
- **On-Device AI**: Landmarks (Pose, Face, Iris) are extracted locally using MediaPipe.
- **Local Storage**: Your posture stats and history are stored in a local SQLite database (`posture_data.db`) and a JSON file (`user_stats.json`) on your hard drive.

## 🛡️ Privacy Shield Features
- **Instant Kill**: You can disable the camera feed at any time via the "Privacy Mode" toggle in the dashboard.
- **Visual Transparency**: The application only tracks mathematical landmarks (coordinates). It does not store actual photos of you.
- **Encrypted History**: (Phase 2) Historical data will be encrypted using AES-256 to prevent unauthorized local access.

## 🔎 Data Audit
The `CVPipeline` only returns coordinate-based JSON data to the API. The API only broadcasts this data to `127.0.0.1` (localhost).
