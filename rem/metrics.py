"""Metrics helpers and pretty printing."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .models import ConsolidationReport

console = Console()


def print_report(report: ConsolidationReport, skills_count: int = 0) -> None:
    report.skills_generated = skills_count

    table = Table(title="REM Consolidation Report", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Session", report.session_id)
    table.add_row("Trajectories processed", str(report.trajectories_processed))
    table.add_row("Original steps", str(report.original_steps))
    table.add_row("Kept steps", str(report.kept_steps))
    table.add_row("Memory reduction", f"{report.memory_reduction_ratio:.1%}")
    table.add_row("Est. token savings", str(report.estimated_token_savings))
    table.add_row("Skills generated", str(report.skills_generated))
    table.add_row("Failure patterns", str(report.failure_patterns_found))
    table.add_row("Policy", report.policy_used)

    console.print(table)
