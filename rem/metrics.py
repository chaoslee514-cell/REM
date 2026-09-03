"""Metrics and reporting."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .models import ConsolidationReport

console = Console()


def print_report(report: ConsolidationReport, skills_count: int = 0) -> None:
    report.skills_generated = skills_count

    table = Table(
        title="REM Consolidation Report",
        show_header=True,
        header_style="bold cyan",
        title_style="bold magenta",
    )
    table.add_column("Metric", style="dim", min_width=22)
    table.add_column("Value", justify="right")

    table.add_row("Session", report.session_id)
    table.add_row("Trajectories processed", str(report.trajectories_processed))
    table.add_row("Original steps", str(report.original_steps))
    table.add_row("Kept steps", str(report.kept_steps))
    table.add_row("Memory reduction", f"{report.memory_reduction_ratio:.1%}")
    table.add_row("Est. token savings", f"{report.estimated_token_savings:,}")
    table.add_row("Skills generated", str(report.skills_generated))
    table.add_row("Failure patterns", str(report.failure_patterns_found))
    table.add_row("Policy", report.policy_used)

    console.print()
    console.print(table)
    console.print()


def print_sessions(sessions: list[str], counts: dict[str, int]) -> None:
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    table = Table(title="REM Sessions", show_header=True, header_style="bold cyan")
    table.add_column("Session ID")
    table.add_column("Trajectories", justify="right")

    for sid in sessions:
        table.add_row(sid, str(counts.get(sid, 0)))

    console.print(table)
