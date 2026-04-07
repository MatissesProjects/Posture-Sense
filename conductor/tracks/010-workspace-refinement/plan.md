# Implementation Plan: Track 010 - Workspace Refinement

## Phase 1: Backend Geometry Update
- [x] Refactor `MonitorManager` to use raw X/Y offsets from `screeninfo`.
- [x] Implement `WebcamAnchor`: Allow defining which monitor the webcam is on (e.g., "bottom_monitor", "top") and its relative X-offset.
- [x] Add a `save_config` / `load_config` mechanism (JSON file).

## Phase 2: UI Workspace Visualization
- [x] Create a robust `WorkspaceVisualizer` supporting asymmetrical offsets.
- [x] Add a visual representation of the Webcam in the `WorkspaceVisualizer`.
- [ ] Create a "Workspace Settings" modal in React for manual "Nudge" refinement.

## Phase 3: Coordinate Mapping Fix
- [x] Update `WindowManager` to use the refined offsets for monitor identification.
- [x] Fix the "Sweet Spot" calculation to be relative to the *webcam* position rather than just the top of the stack.
- [ ] Update Gaze mapping to account for the actual X/Y position of the screens.
