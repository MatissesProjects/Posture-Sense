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
- [ ] Create a "Neck Strain Heatmap" based on gaze and tilt data.
- [ ] Generate a weekly "Gaze Distribution Map" (where you look on your stacked monitors).
- [ ] Visualize "Neutral Time" vs "Risk Time" in a professional dashboard.
