# Implementation Plan: Track 016 - Clinical Metrics

## Phase 1: CVA Implementation
- [x] Research landmark mapping for C7 vertebra vs. Tragus of the ear in MediaPipe.
- [x] Implement `calculate_cva()` logic in `PostureAnalyzer`.
- [x] Add CVA threshold alerts (< 50 degrees indicating significant FHP).

## Phase 2: Protraction Analysis
- [x] Calculate shoulder-to-ear horizontal offset.
- [x] Implement Protraction Index based on acromion process relative to spinal vertical.

## Phase 3: Dashboard Integration
- [x] Add "Clinical View" to the dashboard (integrated into main metrics grid).
- [x] Visualize CVA trend over time.
