"""Skill Distillation — turn consolidated experience into usable Skills."""

from __future__ import annotations

from pathlib import Path

from .models import Trajectory, DistilledSkill, FailurePattern, StepStatus
from .config import get_config


class SkillDistiller:
    """Rule-based distiller that produces practical Markdown skills."""

    def distill(
        self,
        trajectories: list[Trajectory],
        failure_patterns: list[FailurePattern],
        out_dir: str | Path | None = None,
    ) -> list[DistilledSkill]:
        cfg = get_config()
        out_dir = Path(out_dir) if out_dir else cfg.skills_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        skills: list[DistilledSkill] = []

        # 1. Success path skill
        success_trajs = [t for t in trajectories if t.success and t.success_steps]
        if success_trajs:
            skill = self._build_success_skill(success_trajs)
            skills.append(skill)
            self._write(skill, out_dir)

        # 2. Failure avoidance skills (top patterns)
        for pattern in failure_patterns[:8]:  # limit to most frequent
            skill = self._build_failure_skill(pattern)
            skills.append(skill)
            self._write(skill, out_dir)

        # 3. Combined session summary skill if both exist
        if success_trajs and failure_patterns:
            skill = self._build_session_summary(success_trajs, failure_patterns)
            skills.append(skill)
            self._write(skill, out_dir)

        return skills

    def _build_success_skill(self, trajectories: list[Trajectory]) -> DistilledSkill:
        # Prefer the shortest successful trajectory as canonical
        best = min(trajectories, key=lambda t: len(t.success_steps))
        steps_md = []
        for i, s in enumerate(best.success_steps, 1):
            args = s.tool_call.arguments
            args_str = ", ".join(f"{k}={v!r}" for k, v in list(args.items())[:4])
            steps_md.append(f"{i}. `{s.tool_call.name}`({args_str})")

        task = best.task or "the task"
        content = f"""# Skill: Successful Path

## When to use
Use this sequence when solving similar tasks to: **{task}**

## Recommended tool sequence
{chr(10).join(steps_md)}

## Notes
- This path was distilled from {len(trajectories)} successful trajectory(ies).
- Prefer the shortest reliable path; avoid unnecessary retries.

## Source trajectories
{', '.join(t.trajectory_id for t in trajectories[:6])}
"""
        return DistilledSkill(
            name="successful-path",
            description=f"Canonical successful sequence for: {task}",
            content=content.strip(),
            source_trajectory_ids=[t.trajectory_id for t in trajectories],
            tags=["success", "auto-distilled", "critical-path"],
        )

    def _build_failure_skill(self, pattern: FailurePattern) -> DistilledSkill:
        examples = "\n".join(f"- `{e}`" for e in pattern.example_errors[:4])
        content = f"""# Skill: Avoid Failure — {pattern.tool_name}

## Problem
{pattern.description} (seen {pattern.occurrence_count} times)

## Observed errors
{examples}

## Recommended action
{pattern.suggested_fix}

## Prevention checklist
- Validate inputs and preconditions before calling `{pattern.tool_name}`
- Handle the specific error patterns listed above
- Prefer alternative tools or approaches when this error is likely

## Related trajectories
{', '.join(pattern.related_trajectory_ids[:5]) or 'n/a'}
"""
        return DistilledSkill(
            name=pattern.pattern_id,
            description=pattern.description,
            content=content.strip(),
            source_trajectory_ids=pattern.related_trajectory_ids,
            tags=["failure-pattern", "auto-distilled", pattern.tool_name],
        )

    def _build_session_summary(
        self,
        success_trajs: list[Trajectory],
        patterns: list[FailurePattern],
    ) -> DistilledSkill:
        top_failures = "\n".join(
            f"- `{p.tool_name}` ({p.occurrence_count}x): {p.example_errors[0][:60]}..."
            for p in patterns[:5]
        )
        content = f"""# Skill: Session Lessons

## Summary
This session produced {len(success_trajs)} successful trajectory(ies) and {len(patterns)} failure pattern(s).

## What worked
- Prefer the distilled successful-path skill for similar tasks.

## What repeatedly failed
{top_failures}

## Practical advice
1. Reuse the successful tool sequence when the task is similar.
2. Explicitly guard against the top failure patterns above.
3. Keep trajectories short and focused; drop pure retry noise.
"""
        return DistilledSkill(
            name="session-lessons",
            description="High-level lessons from the consolidated session",
            content=content.strip(),
            source_trajectory_ids=[t.trajectory_id for t in success_trajs],
            tags=["summary", "auto-distilled"],
        )

    def _write(self, skill: DistilledSkill, out_dir: Path) -> None:
        path = out_dir / f"{skill.name}.md"
        path.write_text(skill.content + "\n", encoding="utf-8")
