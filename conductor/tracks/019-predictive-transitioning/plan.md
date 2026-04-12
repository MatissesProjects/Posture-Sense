# Implementation Plan: Track 019 - Predictive Transitioning

## Phase 1: Contextual Modeling
- [x] Record separate "decay rates" for posture scores while sitting vs. standing (implemented in `TransitionPredictor`).
- [x] Identify the user's "Critical Fatigue Point" (minutes before score drops below threshold).

## Phase 2: Predictive Engine
- [x] Implement a model to estimate time remaining until the next required transition.
- [x] Add transition nudges: "You've been sitting for X minutes; transition to standing now."

## Phase 3: Transition Tracking
- [x] Measure the "recovery boost" (score improvement) after a sit-to-stand change.

