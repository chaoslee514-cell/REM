"""Core data models for REM."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, computed_field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StepStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    tokens: Optional[int] = None
    status: StepStatus = StepStatus.SUCCESS


class TrajectoryStep(BaseModel):
    step_id: int
    tool_call: ToolCall
    thought: Optional[str] = None
    timestamp: datetime = Field(default_factory=utcnow)
    importance: float = 1.0  # higher = more worth keeping


class Trajectory(BaseModel):
    trajectory_id: str
    session_id: str
    task: Optional[str] = None
    steps: list[TrajectoryStep] = Field(default_factory=list)
    success: bool = False
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def failure_steps(self) -> list[TrajectoryStep]:
        return [s for s in self.steps if s.tool_call.status == StepStatus.FAILURE]

    @computed_field
    @property
    def success_steps(self) -> list[TrajectoryStep]:
        return [s for s in self.steps if s.tool_call.status == StepStatus.SUCCESS]

    def critical_path(self, keep_context: int = 1) -> list[TrajectoryStep]:
        """Keep successful steps + limited context around failures."""
        if not self.steps:
            return []

        keep_ids: set[int] = set()
        for s in self.steps:
            if s.tool_call.status == StepStatus.SUCCESS:
                keep_ids.add(s.step_id)
            elif s.tool_call.status == StepStatus.FAILURE:
                # keep the failure itself + nearby steps for context
                for delta in range(-keep_context, keep_context + 1):
                    keep_ids.add(s.step_id + delta)

        return [s for s in self.steps if s.step_id in keep_ids]


class FailurePattern(BaseModel):
    pattern_id: str
    tool_name: str
    description: str
    example_errors: list[str] = Field(default_factory=list)
    suggested_fix: str = ""
    occurrence_count: int = 1
    related_trajectory_ids: list[str] = Field(default_factory=list)


class DistilledSkill(BaseModel):
    name: str
    description: str
    content: str
    source_trajectory_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: str = "0.2.0"


class ConsolidationReport(BaseModel):
    session_id: str
    trajectories_processed: int = 0
    original_steps: int = 0
    kept_steps: int = 0
    memory_reduction_ratio: float = 0.0
    estimated_token_savings: int = 0
    skills_generated: int = 0
    failure_patterns_found: int = 0
    policy_used: str = "default"
    created_at: datetime = Field(default_factory=utcnow)
