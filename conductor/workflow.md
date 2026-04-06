# Project Workflow: Posture-Sense

To maintain a clean and robust codebase, follow these workflow guidelines:

## Development Cycle
1. **Choose a Track**: Pick an active track from `conductor/tracks.md`.
2. **Review Plan**: Read the track's `plan.md` to see the next task.
3. **Execute**: Work on the task in small, verifiable steps.
4. **Validate**: Test the implementation (e.g., run `capture.py`, check the FastAPI endpoint).
5. **Update**: Mark the task as completed in the track's `plan.md`.
6. **Commit**: Commit changes with a track-prefixed message: `track-001: implement mediapipe capture`.

## Branching & Commits
- Use descriptive branch names if working on a large feature: `feat/track-001-mediapipe`.
- Prefer small, atomic commits that focus on a single piece of functionality.

## Quality Standards
- **Python**: Use `black` for formatting and `flake8` for linting.
- **Frontend**: Follow React best practices (functional components, hooks).
- **Security**: Never commit API keys or personal data. Use `.env` files for configuration.
