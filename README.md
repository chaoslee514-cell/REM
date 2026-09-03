# REM — Replay Experience Module

**From agent runs to production-ready Skills.**

REM captures structured agent trajectories, removes noise, extracts critical paths, mines failure patterns, and distills them into **installable Skills** + clean memory.

It is not another vector store. It is an offline experience-replay and skill-distillation engine designed for engineers who run agents seriously.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/chaoslee514-cell/REM)

---

## Why REM

Real problems when running agents in 2026:

- Agents repeat the same mistakes across sessions
- Successful tool sequences are never turned into reusable Skills
- Long trajectories are full of retries and dead-ends → context pollution + higher cost
- Most memory systems only store & retrieve; almost none systematically **distill executable knowledge** from real runs

REM treats every agent run as experience in a Replay Buffer and runs a measurable consolidation pipeline.

---

## What you get

| Capability | Description |
|------------|-------------|
| Trajectory Capture | Structured recording of tool calls, results, errors, latency, tokens |
| Experience Buffer | Local-first (SQLite + JSONL), queryable by session |
| Consolidation | Configurable filtering, critical-path extraction, failure clustering |
| Skill Distillation | Generates usable Markdown Skills with clear guidance |
| Metrics | Memory reduction ratio, estimated token savings, pattern counts |
| CLI | `record / consolidate / distill / stats / list / export / install` |
| MCP Server | Basic integration point for agent runtimes |

---

## Quick Start

```bash
git clone https://github.com/chaoslee514-cell/REM.git
cd REM
pip install -e .

# Run the demo end-to-end
rem record examples/sample_trajectory.jsonl --session demo
rem consolidate --session demo
rem distill --session demo --out ./skills
rem stats --session demo
```

Generated skills appear in `./skills/`.

---

## CLI Reference

```bash
rem record <file.jsonl> [--session ID]     # Ingest trajectories
rem consolidate [--session ID]             # Filter + extract + mine patterns
rem distill [--session ID] [--out DIR]     # Generate Skill files
rem stats [--session ID]                   # Show metrics
rem list                                   # List all sessions
rem export --session ID [--out file]       # Export cleaned trajectories
rem install <skill.md>                     # Copy skill to installed_skills/
rem serve                                  # Start MCP server (optional extra)
```

---

## Architecture

```
Agent Runtime / JSONL
        │
        ▼
+---------------------+
|  Experience Buffer  |  SQLite + JSONL
+----------│----------+
           │  consolidate
           ▼
+---------------------+
| Consolidation Engine|
| • Filter & score    |
| • Critical path     |
| • Failure patterns  |
+----------│----------+
           │  distill
     ┌-----┴-----┐
     ▼           ▼
Skill Files    Clean Memory
```

---

## Design Principles

1. **Local-first** — Data never leaves your machine by default
2. **Measurable** — Every run produces concrete numbers
3. **Skill-native** — Output is immediately useful to current agent ecosystems
4. **Engineer-centric** — CLI-first, explicit, minimal magic
5. **Incremental** — Start simple (rules), add LLM distillation later

---

## Current Limitations (honest)

- Trajectory capture is still manual (JSONL import). Automatic hooks for Claude Code / Cursor are planned.
- Skill quality is rule-based and template-driven. Real production quality needs better critical-path algorithms + optional LLM refinement.
- Failure clustering is currently tool-name based. Semantic clustering is on the roadmap.
- No large-scale benchmark suite yet.

---

## Project Structure

```
REM/
├── rem/
│   ├── models.py          # Data models
│   ├── buffer.py          # Experience Buffer
│   ├── consolidator.py    # Consolidation engine
│   ├── distill.py         # Skill distillation
│   ├── metrics.py         # Reporting
│   ├── cli.py             # CLI
│   ├── mcp_server.py      # MCP stub
│   └── config.py          # Simple config
├── examples/
├── tests/
├── pyproject.toml
└── README.md
```

---

## Roadmap

- [x] Core buffer + consolidation + distillation
- [x] Usable CLI + metrics
- [x] Basic tests
- [ ] Automatic trajectory capture from popular runtimes
- [ ] Better critical-path & importance scoring
- [ ] Optional LLM-assisted distillation
- [ ] Semantic failure clustering
- [ ] Reproducible benchmark suite
- [ ] Policy plugins

---

## Contributing

PRs and issues welcome. Highest value contributions right now:

1. Runtime adapters (Claude Code, Cursor, etc.)
2. Better scoring / critical-path algorithms
3. Higher-quality skill templates
4. Benchmarks on repeated-error tasks

---

## License

MIT
