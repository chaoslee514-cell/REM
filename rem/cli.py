"""REM Command Line Interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .buffer import ExperienceBuffer
from .consolidator import Consolidator
from .distill import SkillDistiller
from .metrics import print_report

app = typer.Typer(
    name="rem",
    help="REM — Replay Experience Module. From agent runs to production-ready Skills.",
    add_completion=False,
)
console = Console()


def get_buffer() -> ExperienceBuffer:
    return ExperienceBuffer(data_dir=".data")


@app.command()
def record(
    file: Path = typer.Argument(..., help="JSONL trajectory file"),
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
):
    """Ingest a trajectory file into the Experience Buffer."""
    buf = get_buffer()
    count = buf.ingest_jsonl(file, session_id=session)
    console.print(f"[green]✓[/green] Ingested {count} trajectory(s) into session '{session}'")


@app.command()
def consolidate(
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    policy: str = typer.Option("default", "--policy", "-p", help="Consolidation policy"),
):
    """Run the consolidation pipeline on a session."""
    buf = get_buffer()
    consolidator = Consolidator(buf)
    try:
        filtered, patterns, report = consolidator.run(session)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Persist filtered trajectories back (overwrite with cleaned versions)
    for t in filtered:
        buf.add(t)

    console.print(f"[green]✓[/green] Consolidation complete for session '{session}'")
    console.print(f"   Failure patterns found: {len(patterns)}")
    print_report(report)


@app.command()
def distill(
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    out: Path = typer.Option("./skills", "--out", "-o", help="Output directory for skills"),
):
    """Distill consolidated trajectories into Skill files."""
    buf = get_buffer()
    consolidator = Consolidator(buf)
    try:
        filtered, patterns, report = consolidator.run(session)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    distiller = SkillDistiller()
    skills = distiller.distill(filtered, patterns, out_dir=out)

    console.print(f"[green]✓[/green] Generated {len(skills)} skill(s) → {out}")
    for s in skills:
        console.print(f"   • {s.name}.md")
    print_report(report, skills_count=len(skills))


@app.command()
def stats(
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID (omit for all)"),
):
    """Show buffer statistics."""
    buf = get_buffer()
    sessions = [session] if session else buf.all_sessions()
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    for sid in sessions:
        trajs = buf.list_by_session(sid)
        total_steps = sum(len(t.steps) for t in trajs)
        successes = sum(1 for t in trajs if t.success)
        console.print(f"\n[bold]Session:[/bold] {sid}")
        console.print(f"  Trajectories : {len(trajs)}")
        console.print(f"  Total steps  : {total_steps}")
        console.print(f"  Successes    : {successes}")


@app.command()
def install(
    skill_file: Path = typer.Argument(..., help="Path to a distilled skill .md file"),
):
    """Install a skill file (MVP: just copies to ./installed_skills)."""
    dest_dir = Path("./installed_skills")
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / skill_file.name
    dest.write_text(skill_file.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"[green]✓[/green] Installed → {dest}")


@app.command()
def serve():
    """Start the MCP server (requires optional mcp extra)."""
    try:
        from .mcp_server import run_server
        run_server()
    except ImportError:
        console.print("[red]MCP extra not installed. Run: pip install 'rem-agent[mcp]'[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
