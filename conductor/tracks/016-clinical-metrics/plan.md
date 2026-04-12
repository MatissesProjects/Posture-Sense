# Implementation Plan: Track 016 - Clinical Metrics

## Phase 1: CVA Implementation
- [ ] Research landmark mapping for C7 vertebra vs. Tragus of the ear in MediaPipe.
- [ ] Implement `calculate_cva()` logic in `PostureAnalyzer`.
- [ ] Add CVA threshold alerts (< 50 degrees indicating significant FHP).

## Phase 2: Protraction Analysis
- [ ] Calculate shoulder-to-ear horizontal offset.
- [ ] Implement Protraction Index based on acromion process relative to spinal vertical.

## Phase 3: Dashboard Integration
- [ ] Add "Clinical View" to the dashboard.
- [ ] Visualize CVA trend over time.
