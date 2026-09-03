# Changelog

## [0.2.0] - 2026-09-03

### Added
- `rem list` and `rem export` commands
- Better critical-path extraction (keeps limited context around failures)
- Improved failure pattern mining with error signatures
- Higher-quality Skill templates (success path, failure avoidance, session lessons)
- Basic test suite (`tests/test_basic.py`)
- `rem/config.py` for centralized settings
- Richer metrics and CLI output

### Changed
- Version bumped to 0.2.0
- Models improved with importance field and better helpers
- Distiller produces more practical, actionable Skill content
- README rewritten for clarity and honesty about current limitations
- Buffer ingest is more robust to different JSONL shapes

### Fixed
- Various edge cases in trajectory parsing and empty sessions
