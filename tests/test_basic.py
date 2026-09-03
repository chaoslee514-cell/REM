"""Basic tests for REM core functionality."""

from pathlib import Path

import pytest

from rem.buffer import ExperienceBuffer
from rem.consolidator import Consolidator
from rem.distill import SkillDistiller
from rem.models import Trajectory, TrajectoryStep, ToolCall, StepStatus


@pytest.fixture
def tmp_buffer(tmp_path: Path):
    return ExperienceBuffer(data_dir=tmp_path / "data")


def _make_traj(tid: str, session: str, success: bool, steps_data: list) -> Trajectory:
    steps = []
    for i, (name, status, error) in enumerate(steps_data):
        steps.append(
            TrajectoryStep(
                step_id=i,
                tool_call=ToolCall(
                    name=name,
                    status=StepStatus(status),
                    error=error,
                ),
            )
        )
    return Trajectory(
        trajectory_id=tid,
        session_id=session,
        task="test task",
        steps=steps,
        success=success,
        total_tokens=100,
    )


def test_buffer_add_and_list(tmp_buffer: ExperienceBuffer):
    t = _make_traj("t1", "s1", True, [("read", "success", None)])
    tmp_buffer.add(t)
    assert tmp_buffer.count("s1") == 1
    trajs = tmp_buffer.list_by_session("s1")
    assert len(trajs) == 1
    assert trajs[0].trajectory_id == "t1"


def test_critical_path():
    t = _make_traj(
        "t1",
        "s1",
        False,
        [
            ("read", "success", None),
            ("edit", "failure", "permission denied"),
            ("test", "failure", "auth error"),
        ],
    )
    path = t.critical_path(keep_context=1)
    assert len(path) >= 2  # at least the failure + some context


def test_consolidator(tmp_buffer: ExperienceBuffer):
    t1 = _make_traj("t1", "demo", True, [("read", "success", None), ("edit", "success", None)])
    t2 = _make_traj("t2", "demo", False, [("edit", "failure", "permission denied")])
    tmp_buffer.add(t1)
    tmp_buffer.add(t2)

    consolidator = Consolidator(tmp_buffer)
    filtered, patterns, report = consolidator.run("demo")

    assert report.trajectories_processed == 2
    assert report.original_steps == 3
    assert len(patterns) >= 1
    assert patterns[0].tool_name == "edit"


def test_distiller(tmp_buffer: ExperienceBuffer, tmp_path: Path):
    t1 = _make_traj("t1", "demo", True, [("read", "success", None), ("edit", "success", None)])
    t2 = _make_traj("t2", "demo", False, [("edit", "failure", "permission denied")])
    tmp_buffer.add(t1)
    tmp_buffer.add(t2)

    consolidator = Consolidator(tmp_buffer)
    filtered, patterns, _ = consolidator.run("demo")

    distiller = SkillDistiller()
    out = tmp_path / "skills"
    skills = distiller.distill(filtered, patterns, out_dir=out)

    assert len(skills) >= 1
    assert (out / "successful-path.md").exists() or any(out.iterdir())
