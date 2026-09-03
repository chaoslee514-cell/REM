"""Consolidation Pipeline — offline experience processing."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from .buffer import ExperienceBuffer
from .models import Trajectory, FailurePattern, ConsolidationReport, StepStatus
from .config import get_config


PolicyFn = Callable[[list[Trajectory]], list[Trajectory]]


def default_policy(trajectories: list[Trajectory]) -> list[Trajectory]:
    """Keep trajectories that contain useful signal (success or failure)."""
    kept = []
    for t in trajectories:
        has_signal = any(
            s.tool_call.status in (StepStatus.SUCCESS, StepStatus.FAILURE)
            for s in t.steps
        )
        if has_signal and t.steps:
            kept.append(t)

    # Prefer successful trajectories, then shorter ones
    kept.sort(key=lambda t: (not t.success, len(t.steps)))
    return kept


class Consolidator:
    def __init__(
        self,
        buffer: ExperienceBuffer,
        policy: PolicyFn = default_policy,
        keep_context: int = 1,
    ):
        self.buffer = buffer
        self.policy = policy
        self.keep_context = keep_context

    def run(self, session_id: str) -> tuple[list[Trajectory], list[FailurePattern], ConsolidationReport]:
        trajectories = self.buffer.list_by_session(session_id)
        if not trajectories:
            raise ValueError(f"No trajectories found for session '{session_id}'")

        original_steps = sum(len(t.steps) for t in trajectories)
        filtered = self.policy(trajectories)

        # Apply critical-path reduction
        for t in filtered:
            critical = t.critical_path(keep_context=self.keep_context)
            if critical:
                t.steps = critical

        kept_steps = sum(len(t.steps) for t in filtered)
        reduction = 1.0 - (kept_steps / original_steps) if original_steps > 0 else 0.0

        patterns = self._mine_failures(filtered)

        cfg = get_config()
        report = ConsolidationReport(
            session_id=session_id,
            trajectories_processed=len(trajectories),
            original_steps=original_steps,
            kept_steps=kept_steps,
            memory_reduction_ratio=round(reduction, 4),
            estimated_token_savings=int(original_steps * cfg.tokens_per_step_estimate * reduction),
            skills_generated=0,
            failure_patterns_found=len(patterns),
            policy_used="default",
        )

        return filtered, patterns, report

    def _mine_failures(self, trajectories: list[Trajectory]) -> list[FailurePattern]:
        # Group by tool name + simplified error signature
        buckets: dict[str, dict] = defaultdict(lambda: {
            "errors": [],
            "traj_ids": set(),
            "count": 0,
        })

        for t in trajectories:
            for step in t.steps:
                if step.tool_call.status != StepStatus.FAILURE:
                    continue
                error = (step.tool_call.error or "unknown error").strip()
                # Simple signature: first 80 chars normalized
                sig = error[:80].lower()
                key = f"{step.tool_call.name}::{sig}"
                buckets[key]["errors"].append(error[:200])
                buckets[key]["traj_ids"].add(t.trajectory_id)
                buckets[key]["count"] += 1

        patterns: list[FailurePattern] = []
        for key, data in buckets.items():
            tool_name = key.split("::", 1)[0]
            patterns.append(
                FailurePattern(
                    pattern_id=f"fail-{tool_name}-{abs(hash(key)) % 10000:04d}",
                    tool_name=tool_name,
                    description=f"Repeated failure on tool `{tool_name}`",
                    example_errors=list(dict.fromkeys(data["errors"]))[:5],
                    suggested_fix=(
                        f"Before calling `{tool_name}`, verify preconditions and handle the error: "
                        f"{data['errors'][0][:100]}..."
                    ),
                    occurrence_count=data["count"],
                    related_trajectory_ids=list(data["traj_ids"]),
                )
            )

        # Sort by frequency
        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)
        return patterns
