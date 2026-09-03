# Examples

## sample_trajectory.jsonl

A small but realistic set of trajectories for the `rem demo` command.

It contains:

- 2 successful paths (auth fix + rate limiting)
- 3 failed attempts that share the same root error (`Permission denied` in CI)

This lets the consolidator and distiller demonstrate:

- Critical path extraction
- Failure pattern mining (repeated permission errors)
- Generation of `successful-path.md`, failure-avoidance skills, and `session-lessons.md`

### Try it

```bash
rem demo
```

or manually:

```bash
rem record examples/sample_trajectory.jsonl --session demo
rem consolidate --session demo
rem distill --session demo
```
