# REM — Replay Experience Module

**From agent runs to production-ready Skills.**

REM turns real agent execution trajectories into reusable Skills and clean memory.  
It filters noise, extracts critical paths, mines failure patterns, and distills them into installable Markdown skills.

> Not another vector memory.  
> An offline experience-replay engine that makes agents stop repeating the same mistakes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/chaoslee514-cell/REM)

---

## Quick Demo (30 seconds)

```bash
pip install -e .
rem demo
```

This single command will:

1. Load sample trajectories
2. Run consolidation (noise removal + critical path)
3. Mine failure patterns
4. Generate Skills into `./skills/`
5. Print a clear metrics report

Then open the generated files:

```bash
ls skills/
cat skills/successful-path.md
cat skills/session-lessons.md
```

---

## The Problem

When you run coding agents seriously, you keep seeing the same issues:

- The agent retries the same failing tool call across sessions
- Successful sequences are never captured as reusable knowledge
- Long trajectories are full of dead-ends → context gets dirty and expensive
- Most memory tools only store & retrieve; almost none **distill executable Skills** from real runs

REM treats every run as experience in a Replay Buffer and runs a measurable offline consolidation pipeline.

---

## What REM Does

| Step | What happens |
|------|----------------|
| **Capture** | Ingest structured trajectories (tool calls, results, errors, tokens) |
| **Consolidate** | Filter noise, keep critical path + failure context, mine patterns |
| **Distill** | Generate practical Markdown Skills |
| **Measure** | Report memory reduction, estimated token savings, pattern counts |

---

## Installation

```bash
git clone https://github.com/chaoslee514-cell/REM.git
cd REM
pip install -e .
```

Requirements: Python 3.10+

---

## Usage

### One-command demo
```bash
rem demo
```

### Manual workflow
```bash
# 1. Ingest trajectories
rem record examples/sample_trajectory.jsonl --session my-task

# 2. Consolidate
rem consolidate --session my-task

# 3. Distill into Skills
rem distill --session my-task --out ./skills

# 4. Inspect
rem stats --session my-task
rem list
```

### Other useful commands
```bash
rem export --session my-task --out cleaned.jsonl
rem install skills/successful-path.md
```

---

## Example Output (from `rem demo`)

After running the demo you typically get:

- `skills/successful-path.md` — canonical successful tool sequence
- `skills/fail-*.md` — failure avoidance skills with concrete errors
- `skills/session-lessons.md` — high-level lessons from the session

Plus a report showing memory reduction and estimated token savings.

---

## Architecture

```
JSONL / Agent Runtime
         │
         ▼
+----------------------+
|  Experience Buffer   |   SQLite (local-first)
+----------│-----------+
           │ consolidate
           ▼
+----------------------+
| Consolidation Engine |
| • Filter & score     |
| • Critical path      |
| • Failure patterns   |
+----------│-----------+
           │ distill
     ┌-----┴-----┐
     ▼           ▼
 Skill Files    Metrics
```

---

## Design Principles

1. **Local-first** — Data stays on your machine
2. **Measurable** — Every run produces concrete numbers
3. **Skill-native** — Output is immediately usable
4. **Engineer-centric** — CLI-first, explicit, minimal magic
5. **Honest** — Limitations are documented, not hidden

---

## Current Limitations

- Trajectory capture is still manual (JSONL). Automatic hooks for Claude Code / Cursor are planned.
- Skill generation is rule-based. Higher quality will come from better critical-path algorithms + optional LLM refinement.
- Failure clustering is currently signature-based, not full semantic clustering.
- No large public benchmark suite yet.

These are known and actively being improved.

---

## Project Structure

```
REM/
├── rem/
│   ├── cli.py
│   ├── buffer.py
│   ├── consolidator.py
│   ├── distill.py
│   ├── models.py
│   ├── metrics.py
│   ├── config.py
│   └── mcp_server.py
├── examples/
├── tests/
├── pyproject.toml
└── README.md
```

---

## Roadmap

- [x] Core buffer + consolidation + distillation
- [x] One-command demo
- [x] Usable CLI + metrics
- [x] Basic tests
- [ ] Automatic trajectory capture from popular agent runtimes
- [ ] Better critical-path & importance scoring
- [ ] Optional LLM-assisted distillation
- [ ] Semantic failure clustering
- [ ] Public benchmark on repeated-error tasks

---

## Contributing

Issues and PRs are welcome. Highest-impact areas right now:

1. Runtime adapters (Claude Code, Cursor, etc.)
2. Better scoring / critical-path logic
3. Higher-quality skill templates
4. Real-world usage reports and benchmarks

---

## License

MIT
