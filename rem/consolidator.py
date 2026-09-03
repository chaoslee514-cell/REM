"""Consolidation Pipeline — the core offline engine."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from .buffer import ExperienceBuffer
from .models import (
    Trajectory,
    FailurePattern,
    ConsolidationReport,
    StepStatus,
)


PolicyFn = Callable[[list[Trajectory]], list[Trajectory]]


def default_policy(trajectories: list[Trajectory]) -> list[Trajectory]:
    """Simple but useful default policy.

    - Prefer successful trajectories
    - Keep trajectories that contain failures (for pattern mining)
    - Drop pure-noise trajectories with zero successful steps
    """
    kept = []
    for t in trajectories:
        has_success = any(s.tool_call.status == StepStatus.SUCCESS for s in t.steps)
        has_failure = any(s.tool_call.status == StepStatus.FAILURE for s in t.steps)
        if has_success or has_failure:
            kept.append(t)
    # Prefer successes first
    kept.sort(key=lambda t: (not t.success, -len(t.steps)))
    return kept


class Consolidator:
    def __init__(self, buffer: ExperienceBuffer, policy: PolicyFn = default_policy):
        self.buffer = buffer
        self.policy = policy

    def run(self, session_id: str) -> tuple[list[Trajectory], list[FailurePattern], ConsolidationReport]:
        trajectories = self.buffer.list_by_session(session_id)
        if not trajectories:
            raise ValueError(f"No trajectories found for session '{session_id}'")

        original_steps = sum(len(t.steps) for t in trajectories)
        filtered = self.policy(trajectories)

        # Extract critical paths (in-place simplification for MVP)
        for t in filtered:
            critical = t.critical_path
            if critical and len(critical) < len(t.steps):
                t.steps = critical  # keep only successful path for distillation

        kept_steps = sum(len(t.steps) for t in filtered)
        reduction = 1.0 - (kept_steps / original_steps) if original_steps else 0.0

        # Simple failure pattern mining
        patterns = self._mine_failures(filtered)

        report = ConsolidationReport(
            session_id=session_id,
            trajectories_processed=len(trajectories),
            original_steps=original_steps,
            kept_steps=kept_steps,
            memory_reduction_ratio=round(reduction, 4),
            estimated_token_savings=int(original_steps * 40 * reduction),  # rough heuristic
            skills_generated=0,  # filled later by distiller
            failure_patterns_found=len(patterns),
            policy_used="default",
        )

        return filtered, patterns, report

    def _mine_failures(self, trajectories: list[Trajectory]) -> list[FailurePattern]:
        error_map: dict[str, list[str]] = defaultdict(list)
        for t in trajectories:
            for step in t.steps:
                if step.tool_call.status == StepStatus.FAILURE and step.tool_call.error:
                    key = step.tool_call.name
                    error_map[key].append(step.tool_call.error[:200])

        patterns = []
        for tool_name, errors in error_map.items():
            patterns.append(
                FailurePattern(
                    pattern_id=f"fail-{tool_name}",
                    description=f"Frequent failures on tool `{tool_name}`",
                    example_errors=errors[:5],
                    suggested_fix=f"Add explicit error handling or precondition checks before calling `{tool_name}`.",
                    occurrence_count=len(errors),
                )
            )
        return patterns
