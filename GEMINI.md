# Posture-Sense: Gemini CLI Mandates

These instructions are foundational for this workspace and take precedence over general defaults.

## Operational Standards

- **Environment & Shell**: This project is developed on Windows. Always use **Windows PowerShell** compatible commands. Use `;` instead of `&&` for command chaining.
- **Test-Driven Development**: ALWAYS create or update automated tests (e.g., `pytest` for Python, `vitest` or `jest` for React) as you implement new features or fix bugs. A task is not complete without verification.
- **Atomic Commits**: Commit changes in small, logical "chunks" rather than one large commit at the end. Each commit should represent a single functional or structural update.
  - Always propose a draft commit message and verify the commit with `git status`.

## Project Context
- **Stacked Monitors**: The user has two monitors stacked vertically. This is a critical factor for posture alignment and eye-tracking logic. See `monitors_and_webcam_layout.png` for reference.
- **Sit/Stand Detection**: The application must account for both sitting and standing positions, even though the webcam remains fixed on the monitor.
- **Architecture**: Follow the [Conductor Index](./conductor/index.md) and [Tracks Registry](./conductor/tracks.md) for project structure and planning.
