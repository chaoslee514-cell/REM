# REM — Replay Experience Module

**From agent runs to production-ready Skills.**

REM is an offline experience replay + consolidation engine for AI agents.  
It captures structured execution trajectories, filters noise, extracts critical paths, clusters failure patterns, and distills them into **installable Skills** and clean compressed memory.

> Not another vector memory.  
> A measurable pipeline that turns real runs into reusable agent skills.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why REM exists

Current agent stacks have strong Skills and Memory layers, but lack a reliable way to **automatically convert real execution experience into high-quality Skills**.

Common problems REM targets:

- Agents repeat the same mistakes across sessions
- Trajectories are noisy (retries, dead-ends, partial failures)
- Skills are mostly hand-written
- Long-running agents suffer from context pollution and rising token cost
- Almost no system gives measurable improvement metrics after “learning”

REM treats agent runs as an **Experience Replay Buffer** (inspired by RL) and runs a configurable offline consolidation pipeline.

---

## Core Features (MVP)

| Feature | Description |
|---------|-------------|
| **Trajectory Capture** | Structured recording of tool calls, args, results, errors, latency, tokens, success/failure |
| **Experience Buffer** | Local-first storage (JSONL + SQLite) |
| **Consolidation Pipeline** | Configurable filtering, critical-path extraction, failure clustering |
| **Skill Distillation** | Generates installable Skill files compatible with current agent ecosystems |
| **Clean Memory Output** | Compressed semantic memory with provenance |
| **Metrics & Observability** | Memory reduction ratio, estimated token savings, skill count, failure coverage |
| **CLI First** | `rem record / consolidate / distill / stats / install` |
| **MCP Server** | Drop-in integration for Claude Code, Cursor, OpenClaw and other MCP clients |

---

## Quick Start

```bash
# Install (editable)
pip install -e .

# Record a sample trajectory
rem record examples/sample_trajectory.jsonl --session demo-001

# Run consolidation
rem consolidate --session demo-001 --policy default

# Distill skills
rem distill --session demo-001 --out ./skills

# View metrics
rem stats --session demo-001
```

---

## Architecture Overview

```
Agent Runtime
      |
      | structured trajectory
      v
+-----------------------+
|   Experience Buffer   |   JSONL + SQLite
+-----------+-----------+
            |
            | trigger (manual / threshold / end-of-task)
            v
+-----------------------+
| Consolidation Pipeline|
| 1. Filter & Prioritize|
| 2. Critical Path      |
| 3. Failure Clustering |
| 4. Skill Distillation |
| 5. Memory Compression |
+-----------+-----------+
            |
     +------+------+
     v             v
 Skill Packs   Clean Memory
 (installable) (with citations)
```

---

## CLI Reference

```bash
rem record <file> [--session ID]          # Ingest trajectory
rem consolidate [--session ID] [--policy] # Run consolidation
rem distill [--session ID] [--out DIR]    # Generate Skill files
rem stats [--session ID]                  # Show metrics
rem install <skill-file>                  # Install a distilled skill
rem serve                                 # Start MCP server
```

---

## Project Structure

```
REM/
├── rem/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── buffer.py
│   ├── consolidator.py
│   ├── distill.py
│   ├── metrics.py
│   └── mcp_server.py
├── examples/
│   └── sample_trajectory.jsonl
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Design Principles

1. **Local-first** — All data stays on disk by default.
2. **Measurable** — Every consolidation run produces hard numbers.
3. **Skill-native** — Output is immediately usable in current Skill ecosystems.
4. **Configurable** — Policies are pluggable; start with rules, add LLM later.
5. **Engineer-friendly** — CLI + clear metrics + no magic.

---

## Roadmap

- [x] Experience Buffer + basic consolidation
- [x] Skill distillation skeleton
- [x] CLI + metrics
- [ ] Real runtime adapters (Claude Code / Cursor hooks)
- [ ] Better failure clustering algorithms
- [ ] Policy marketplace / community strategies
- [ ] Multi-agent shared experience pools
- [ ] Benchmark suite against repeated-error tasks

---

## Contributing

Issues and PRs are welcome.  
Focus areas: better scoring functions, distillation quality, runtime adapters, and reproducible benchmarks.

---

## License

MIT
