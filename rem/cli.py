"""REM Command Line Interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .buffer import ExperienceBuffer
from .consolidator import Consolidator
from .distill import SkillDistiller
from .metrics import print_report, print_sessions
from .config import get_config

app = typer.Typer(
    name="rem",
    help="REM — Replay Experience Module. From agent runs to production-ready Skills.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def get_buffer() -> ExperienceBuffer:
    return ExperienceBuffer()


@app.command()
def record(
    file: Path = typer.Argument(..., exists=True, readable=True, help="JSONL trajectory file"),
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
):
    """Ingest trajectories from a JSONL file into the Experience Buffer."""
    buf = get_buffer()
    try:
        count = buf.ingest_jsonl(file, session_id=session)
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Ingested [bold]{count}[/bold] trajectory(s) into session [cyan]{session}[/cyan]")


@app.command()
def consolidate(
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
):
    """Run consolidation: filter noise, extract critical paths, mine failure patterns."""
    buf = get_buffer()
    consolidator = Consolidator(buf)

    try:
        filtered, patterns, report = consolidator.run(session)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Write cleaned trajectories back
    for t in filtered:
        buf.add(t)

    console.print(f"[green]✓[/green] Consolidated session [cyan]{session}[/cyan]")
    if patterns:
        console.print(f"   Top failure patterns: {len(patterns)}")
        for p in patterns[:3]:
            console.print(f"   • {p.tool_name} ({p.occurrence_count}x)")

    print_report(report)


@app.command()
def distill(
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output directory for skills"),
):
    """Distill consolidated experience into Skill Markdown files."""
    buf = get_buffer()
    consolidator = Consolidator(buf)

    try:
        filtered, patterns, report = consolidator.run(session)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    distiller = SkillDistiller()
    skills = distiller.distill(filtered, patterns, out_dir=out)

    out_dir = out or get_config().skills_dir
    console.print(f"[green]✓[/green] Generated [bold]{len(skills)}[/bold] skill(s) → [cyan]{out_dir}[/cyan]")
    for s in skills:
        console.print(f"   • {s.name}.md")

    print_report(report, skills_count=len(skills))


@app.command()
def stats(
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID (omit for overview)"),
):
    """Show buffer statistics."""
    buf = get_buffer()

    if session:
        trajs = buf.list_by_session(session)
        if not trajs:
            console.print(f"[yellow]No data for session '{session}'[/yellow]")
            return
        total_steps = sum(len(t.steps) for t in trajs)
        successes = sum(1 for t in trajs if t.success)
        failures = sum(1 for t in trajs if not t.success)
        console.print(f"\n[bold]Session:[/bold] {session}")
        console.print(f"  Trajectories : {len(trajs)}")
        console.print(f"  Total steps  : {total_steps}")
        console.print(f"  Successes    : {successes}")
        console.print(f"  Failures     : {failures}")
    else:
        sessions = buf.all_sessions()
        counts = {s: buf.count(s) for s in sessions}
        print_sessions(sessions, counts)


@app.command("list")
def list_sessions():
    """List all sessions in the buffer."""
    buf = get_buffer()
    sessions = buf.all_sessions()
    counts = {s: buf.count(s) for s in sessions}
    print_sessions(sessions, counts)


@app.command()
def export(
    session: str = typer.Option(..., "--session", "-s", help="Session ID"),
    out: Path = typer.Option("export.jsonl", "--out", "-o", help="Output JSONL path"),
):
    """Export cleaned trajectories of a session to JSONL."""
    buf = get_buffer()
    count = buf.export_jsonl(session, out)
    console.print(f"[green]✓[/green] Exported {count} trajectory(s) → {out}")


@app.command()
def install(
    skill_file: Path = typer.Argument(..., exists=True, help="Path to a distilled skill .md file"),
):
    """Install a skill file into ./installed_skills."""
    cfg = get_config()
    dest_dir = cfg.installed_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / skill_file.name
    dest.write_text(skill_file.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"[green]✓[/green] Installed → {dest}")


@app.command()
def serve():
    """Start the MCP server (requires: pip install 'rem-agent[mcp]')."""
    try:
        from .mcp_server import run_server
        console.print("[cyan]Starting REM MCP server...[/cyan]")
        run_server()
    except ImportError:
        console.print("[red]MCP extra not installed.[/red] Run: [bold]pip install 'rem-agent[mcp]'[/bold]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
