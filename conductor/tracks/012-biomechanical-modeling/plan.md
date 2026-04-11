# Implementation Plan: Track 012 - Biomechanical Modeling

## Phase 1: 3D Normalization
- [x] Implement robust Z-axis (depth) normalization for pose landmarks in `PostureAnalyzer.normalize_to_physical`.
- [x] Create a "Physical Workspace" coordinate system (mapping pixels to estimated cm).

## Phase 2: Center of Mass (CoM)
- [x] Implement CoM estimation using weighted body segment averages in `PostureAnalyzer.calculate_com`.
- [x] Detect "Leaning" (CoM deviation from the stable base of support).
- [ ] Visualize the CoM vector on the live dashboard.

## Phase 3: Kinematic Chain Analysis
- [x] Model the spine as three distinct segments: Lumbar, Thoracic, and Cervical in `PostureAnalyzer.analyze_spine_kinematics`.
- [x] Calculate the relative rotation (flexion) between these segments.
- [x] Detect "Slump Projection" (where the torso collapses forward even if the head is level).

## Phase 4: Biomechanical Risk Score
- [x] Replace simple weighted scoring with a model-based "Structural Load" score in `PostureAnalyzer.calculate_biomechanical_risk`.
- [x] Identify high-shear moments (flexion/leaning) in the analysis loop.
- [x] Refactor `total_score` to prioritize biomechanical data (40% weight).
