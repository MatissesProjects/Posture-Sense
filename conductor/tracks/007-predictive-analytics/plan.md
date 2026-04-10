# Implementation Plan: Track 007 - Predictive Analytics

## Phase 1: Longitudinal Data Storage
- [x] Create a local SQLite database (`posture_data.db`) in `src/intelligence/database_manager.py`.
- [x] Store joint angles, risk scores, and durations via `StatsManager`.
- [x] Implement minute-by-minute data aggregation.

## Phase 2: Predictive Models
- [x] Implement a Linear Regression model in `src/intelligence/fatigue_predictor.py` to analyze daily trends.
- [x] Predict imminent posture slumps based on time-of-day.
- [x] Provide "Pre-Fatigue Alerts" (Track 007) to suggest breaks *before* posture degrades.

## Phase 3: Advanced Visualizations
- [x] Create a historical data endpoint in the FastAPI backend.
- [x] Implement real-time trend charts using `recharts` in `PostureTrends.tsx`.
- [x] Visualize "Neutral Time" vs "Risk Time" via a distribution pie chart.
- [ ] Create a "Neck Strain Heatmap" based on gaze and tilt data (Future Expansion).
