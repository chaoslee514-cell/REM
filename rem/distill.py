"""Skill Distillation — turn consolidated trajectories into installable Skills."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import Trajectory, DistilledSkill, FailurePattern


class SkillDistiller:
    """MVP distiller: rule-based generation of Skill markdown files."""

    def distill(
        self,
        trajectories: list[Trajectory],
        failure_patterns: list[FailurePattern],
        out_dir: str | Path = "./skills",
    ) -> list[DistilledSkill]:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        skills: list[DistilledSkill] = []

        # 1. One skill from successful critical paths
        success_trajs = [t for t in trajectories if t.success and t.steps]
        if success_trajs:
            skill = self._from_success(success_trajs)
            skills.append(skill)
            self._write_skill(skill, out_dir)

        # 2. One skill per significant failure pattern
        for pattern in failure_patterns:
            if pattern.occurrence_count >= 1:
                skill = self._from_failure(pattern)
                skills.append(skill)
                self._write_skill(skill, out_dir)

        return skills

    def _from_success(self, trajectories: list[Trajectory]) -> DistilledSkill:
        # Take the shortest successful critical path as the canonical example
        best = min(trajectories, key=lambda t: len(t.steps))
        steps_md = "\n".join(
            f"{i+1}. Call `{s.tool_call.name}` with {s.tool_call.arguments}"
            for i, s in enumerate(best.steps)
        )
        content = f"""# Successful Path Skill

## Description
Auto-distilled from successful agent trajectories.

## Recommended Sequence
{steps_md}

## Source
Trajectory IDs: {', '.join(t.trajectory_id for t in trajectories[:5])}
"""
        return DistilledSkill(
            name="successful-path",
            description="Canonical successful tool sequence distilled from real runs",
            content=content,
            source_trajectory_ids=[t.trajectory_id for t in trajectories],
            tags=["success", "auto-distilled"],
        )

    def _from_failure(self, pattern: FailurePattern) -> DistilledSkill:
        examples = "\n".join(f"- {e}" for e in pattern.example_errors[:3])
        content = f"""# Failure Avoidance Skill: {pattern.pattern_id}

## Description
{pattern.description}

## Observed Errors
{examples}

## Suggested Fix
{pattern.suggested_fix or "Add precondition checks and better error handling."}

## Occurrence Count
{pattern.occurrence_count}
"""
        return DistilledSkill(
            name=pattern.pattern_id,
            description=pattern.description,
            content=content,
            source_trajectory_ids=[],
            tags=["failure-pattern", "auto-distilled"],
        )

    def _write_skill(self, skill: DistilledSkill, out_dir: Path) -> None:
        path = out_dir / f"{skill.name}.md"
        path.write_text(skill.content, encoding="utf-8")
