"""Skill Distillation — turn consolidated experience into usable Skills."""

from __future__ import annotations

from pathlib import Path

from .models import Trajectory, DistilledSkill, FailurePattern, StepStatus
from .config import get_config


class SkillDistiller:
    """Rule-based distiller that produces practical, actionable Markdown skills."""

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

        success_trajs = [t for t in trajectories if t.success and t.success_steps]
        if success_trajs:
            skill = self._build_success_skill(success_trajs)
            skills.append(skill)
            self._write(skill, out_dir)

        for pattern in failure_patterns[:6]:
            skill = self._build_failure_skill(pattern)
            skills.append(skill)
            self._write(skill, out_dir)

        if success_trajs or failure_patterns:
            skill = self._build_session_summary(success_trajs, failure_patterns)
            skills.append(skill)
            self._write(skill, out_dir)

        return skills

    def _build_success_skill(self, trajectories: list[Trajectory]) -> DistilledSkill:
        best = min(trajectories, key=lambda t: len(t.success_steps))
        steps_md = []
        for i, s in enumerate(best.success_steps, 1):
            args = s.tool_call.arguments
            # Keep argument display readable
            items = list(args.items())[:5]
            args_str = ", ".join(f"{k}={v!r}" for k, v in items)
            if len(args) > 5:
                args_str += ", ..."
            steps_md.append(f"{i}. **{s.tool_call.name}**({args_str})")

        task = best.task or "similar tasks"
        content = f"""# Skill: Successful Path

## When to use
Apply this sequence when working on: **{task}**

## Recommended tool sequence
{chr(10).join(steps_md)}

## Why this path
- Distilled from {len(trajectories)} successful trajectory(ies)
- Prefers the shortest reliable path
- Strips retries and dead-ends

## Tips
- Follow the order above unless the environment has changed
- If a step fails, check the related failure-avoidance skills before retrying

## Source
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
        content = f"""# Skill: Avoid Failure — `{pattern.tool_name}`

## Problem
{pattern.description}  
Observed **{pattern.occurrence_count}** time(s).

## Concrete errors seen
{examples}

## What to do instead
{pattern.suggested_fix}

## Prevention checklist
- [ ] Validate preconditions before calling `{pattern.tool_name}`
- [ ] Handle the exact error patterns listed above
- [ ] Prefer an alternative approach when this failure is likely
- [ ] Log the failure context so future consolidations can improve

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
        success_count = len(success_trajs)
        fail_count = len(patterns)

        top_failures = "\n".join(
            f"- **{p.tool_name}** ({p.occurrence_count}x): {p.example_errors[0][:70]}..."
            for p in patterns[:5]
        ) or "- None recorded"

        content = f"""# Skill: Session Lessons

## Snapshot
- Successful trajectories: **{success_count}**
- Failure patterns: **{fail_count}**

## What worked
- Reuse the `successful-path` skill for similar tasks
- Prefer short, high-signal tool sequences

## What repeatedly failed
{top_failures}

## Practical rules for next runs
1. Start from the successful-path skill when the task looks similar
2. Explicitly guard against the top failure patterns above
3. Keep new trajectories focused — drop pure retry noise before storing
4. Re-run consolidation after a batch of new experience

## How to use these skills
Feed the generated `.md` files back into your agent as Skills / custom instructions.
"""
        return DistilledSkill(
            name="session-lessons",
            description="High-level lessons distilled from the session",
            content=content.strip(),
            source_trajectory_ids=[t.trajectory_id for t in success_trajs],
            tags=["summary", "auto-distilled"],
        )

    def _write(self, skill: DistilledSkill, out_dir: Path) -> None:
        path = out_dir / f"{skill.name}.md"
        path.write_text(skill.content + "\n", encoding="utf-8")
