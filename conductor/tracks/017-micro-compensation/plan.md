# Implementation Plan: Track 017 - Micro-Compensation

## Phase 1: High-Frequency Landmark Buffer
- [x] Increase sampling rate for specific landmarks (nose, shoulders) - handled by raw buffer implementation.
- [x] Implement a rolling buffer to store 30 frames (~1 sec) of raw, un-smoothed data.

## Phase 2: Signal Analysis
- [x] Apply standard deviation analysis to detect "fidget" frequency and micro-instability.
- [x] Map "micro-instability" patterns where the user makes frequent small corrections.

## Phase 3: Predictive Triggering
- [x] Correlate high fidgeting with future slouching events (integrated into scoring).
- [x] Trigger "Dynamic Reset" alerts: "You seem restless; try a 30-second movement break."
