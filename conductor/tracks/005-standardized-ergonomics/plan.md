# Implementation Plan: Track 005 - Standardized Ergonomics

## Phase 1: RULA Logic Implementation
- [x] Research specific RULA scoring tables for neck, trunk, and upper limbs.
- [x] Map MediaPipe landmarks to RULA body part scores (1-6).
- [x] Implement the grand score (1-7) calculation in `src/intelligence/rula_scorer.py`.
- [x] Integrate RULA results into the main `PostureAnalyzer`.

## Phase 2: REBA for Standing Desk
- [x] Implement REBA (Rapid Entire Body Assessment) specifically for standing postures in `src/intelligence/reba_scorer.py`.
- [x] Integrate leg and trunk position detection for whole-body risk.

## Phase 3: Metric Calibration
- [x] Implement distance estimation using MediaPipe Iris (Iris-to-Camera distance) in `PostureAnalyzer`.
- [x] Integrate "Neutral Position" vs "Risk Position" calibration.

## Phase 4: Professional Reporting
- [x] Create a "Daily Ergonomic Summary" JSON export in `StatsManager`.
- [x] Implement local report logging in the `reports/` directory.
