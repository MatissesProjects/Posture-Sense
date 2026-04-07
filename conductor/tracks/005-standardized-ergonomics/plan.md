# Implementation Plan: Track 005 - Standardized Ergonomics

## Phase 1: RULA Logic Implementation
- [x] Research specific RULA scoring tables for neck, trunk, and upper limbs.
- [x] Map MediaPipe landmarks to RULA body part scores (1-6).
- [x] Implement the grand score (1-7) calculation in `src/intelligence/rula_scorer.py`.
- [x] Integrate RULA results into the main `PostureAnalyzer`.

## Phase 2: REBA for Standing Desk
- [ ] Implement REBA (Rapid Entire Body Assessment) specifically for standing postures.
- [ ] Integrate leg and foot position detection (if visible) or assume neutral for desk work.

## Phase 3: Metric Calibration
- [ ] Implement distance estimation using MediaPipe Iris (Iris-to-Camera distance).
- [ ] Calibrate "Neutral Position" vs "Risk Position" based on ISO 9241-5 standards.

## Phase 4: Professional Reporting
- [ ] Create a "Daily Ergonomic Summary" PDF/JSON export.
- [ ] Highlight specific high-risk moments in the posture timeline.
