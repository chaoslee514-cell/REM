"""Experience Buffer — local-first trajectory storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterator, Optional

from .models import Trajectory, TrajectoryStep, ToolCall, StepStatus


class ExperienceBuffer:
    """Simple but solid local buffer using SQLite + optional JSONL mirror."""

    def __init__(self, data_dir: str | Path = ".data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "rem.db"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trajectories (
                    trajectory_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    task TEXT,
                    success INTEGER,
                    total_tokens INTEGER,
                    total_latency_ms REAL,
                    created_at TEXT,
                    raw_json TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session
                ON trajectories(session_id)
            """)
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

    def ingest_jsonl(self, path: str | Path, session_id: str) -> int:
        """Ingest a JSONL file of trajectories or steps."""
        path = Path(path)
        count = 0
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                # Support both full trajectory objects and simple step lists
                if "trajectory_id" in data:
                    traj = Trajectory.model_validate(data)
                    traj.session_id = session_id
                else:
                    # Minimal synthetic trajectory from a list of tool calls
                    steps = []
                    for i, item in enumerate(data.get("steps", [data])):
                        tc = ToolCall(
                            name=item.get("name", "unknown"),
                            arguments=item.get("arguments", {}),
                            result=item.get("result"),
                            error=item.get("error"),
                            status=StepStatus(item.get("status", "success")),
                        )
                        steps.append(TrajectoryStep(step_id=i, tool_call=tc))
                    traj = Trajectory(
                        trajectory_id=data.get("id", f"{session_id}-{count}"),
                        session_id=session_id,
                        task=data.get("task"),
                        steps=steps,
                        success=data.get("success", True),
                        total_tokens=data.get("total_tokens", 0),
                    )
                self.add(traj)
                count += 1
        return count
