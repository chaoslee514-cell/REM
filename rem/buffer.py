"""Experience Buffer — local-first trajectory storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from .models import Trajectory, TrajectoryStep, ToolCall, StepStatus
from .config import get_config


class ExperienceBuffer:
    """Local Experience Buffer backed by SQLite."""

    def __init__(self, data_dir: str | Path | None = None):
        cfg = get_config()
        self.data_dir = Path(data_dir) if data_dir else cfg.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "rem.db"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trajectories (
                    trajectory_id TEXT PRIMARY KEY,
                    session_id    TEXT NOT NULL,
                    task          TEXT,
                    success       INTEGER NOT NULL DEFAULT 0,
                    total_tokens  INTEGER NOT NULL DEFAULT 0,
                    total_latency_ms REAL NOT NULL DEFAULT 0,
                    created_at    TEXT NOT NULL,
                    raw_json      TEXT NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session ON trajectories(session_id)"
            )
            conn.commit()

    def add(self, trajectory: Trajectory) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO trajectories
                (trajectory_id, session_id, task, success, total_tokens,
                 total_latency_ms, created_at, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trajectory.trajectory_id,
                    trajectory.session_id,
                    trajectory.task,
                    int(trajectory.success),
                    trajectory.total_tokens,
                    trajectory.total_latency_ms,
                    trajectory.created_at.isoformat(),
                    trajectory.model_dump_json(),
                ),
            )
            conn.commit()

    def get(self, trajectory_id: str) -> Optional[Trajectory]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT raw_json FROM trajectories WHERE trajectory_id = ?",
                (trajectory_id,),
            ).fetchone()
            if row:
                return Trajectory.model_validate_json(row[0])
        return None

    def list_by_session(self, session_id: str) -> list[Trajectory]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT raw_json FROM trajectories WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
            return [Trajectory.model_validate_json(r[0]) for r in rows]

    def all_sessions(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT session_id FROM trajectories ORDER BY session_id"
            ).fetchall()
            return [r[0] for r in rows]

    def count(self, session_id: str | None = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            if session_id:
                row = conn.execute(
                    "SELECT COUNT(*) FROM trajectories WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) FROM trajectories").fetchone()
            return row[0] if row else 0

    def delete_session(self, session_id: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "DELETE FROM trajectories WHERE session_id = ?", (session_id,)
            )
            conn.commit()
            return cur.rowcount

    def ingest_jsonl(self, path: str | Path, session_id: str) -> int:
        """Ingest a JSONL file. Supports full Trajectory objects or simplified step lists."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        count = 0
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_no}: {e}") from e

                if "trajectory_id" in data and "steps" in data:
                    # Full trajectory
                    traj = Trajectory.model_validate(data)
                    traj.session_id = session_id
                else:
                    # Simplified format
                    raw_steps = data.get("steps", [data])
                    steps: list[TrajectoryStep] = []
                    for i, item in enumerate(raw_steps):
                        status_str = item.get("status", "success")
                        try:
                            status = StepStatus(status_str)
                        except ValueError:
                            status = StepStatus.SUCCESS

                        tc = ToolCall(
                            name=item.get("name", item.get("tool", "unknown")),
                            arguments=item.get("arguments", item.get("args", {})),
                            result=item.get("result"),
                            error=item.get("error"),
                            latency_ms=item.get("latency_ms"),
                            tokens=item.get("tokens"),
                            status=status,
                        )
                        steps.append(TrajectoryStep(step_id=i, tool_call=tc))

                    traj = Trajectory(
                        trajectory_id=str(data.get("id", data.get("trajectory_id", f"{session_id}-{count}"))),
                        session_id=session_id,
                        task=data.get("task"),
                        steps=steps,
                        success=bool(data.get("success", True)),
                        total_tokens=int(data.get("total_tokens", 0)),
                        total_latency_ms=float(data.get("total_latency_ms", 0)),
                    )

                self.add(traj)
                count += 1
        return count

    def export_jsonl(self, session_id: str, path: str | Path) -> int:
        path = Path(path)
        trajs = self.list_by_session(session_id)
        with path.open("w", encoding="utf-8") as f:
            for t in trajs:
                f.write(t.model_dump_json() + "\n")
        return len(trajs)
