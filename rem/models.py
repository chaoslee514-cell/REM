"""Core data models for REM."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


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
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Trajectory(BaseModel):
    trajectory_id: str
    session_id: str
    task: Optional[str] = None
    steps: list[TrajectoryStep] = Field(default_factory=list)
    success: bool = False
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def failure_steps(self) -> list[TrajectoryStep]:
        return [s for s in self.steps if s.tool_call.status == StepStatus.FAILURE]

    @property
    def critical_path(self) -> list[TrajectoryStep]:
        """Simple critical path: keep only successful steps in order."""
        return [s for s in self.steps if s.tool_call.status == StepStatus.SUCCESS]


class FailurePattern(BaseModel):
    pattern_id: str
    description: str
    example_errors: list[str] = Field(default_factory=list)
    suggested_fix: Optional[str] = None
    occurrence_count: int = 1


class DistilledSkill(BaseModel):
    name: str
    description: str
    content: str  # Markdown / skill body
    source_trajectory_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: str = "0.1.0"


class ConsolidationReport(BaseModel):
    session_id: str
    trajectories_processed: int
    original_steps: int
    kept_steps: int
    memory_reduction_ratio: float
    estimated_token_savings: int
    skills_generated: int
    failure_patterns_found: int
    policy_used: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
