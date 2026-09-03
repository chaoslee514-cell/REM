"""MCP Server for REM."""

from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # type: ignore


def run_server() -> None:
    if FastMCP is None:
        raise ImportError("Please install the mcp package: pip install 'rem-agent[mcp]'")

    mcp = FastMCP("REM")

    @mcp.tool()
    def rem_stats(session_id: str = "default") -> str:
        """Return statistics for a REM session."""
        from .buffer import ExperienceBuffer
        buf = ExperienceBuffer()
        trajs = buf.list_by_session(session_id)
        if not trajs:
            return f"No data for session '{session_id}'"
        total_steps = sum(len(t.steps) for t in trajs)
        successes = sum(1 for t in trajs if t.success)
        return (
            f"Session: {session_id}\n"
            f"Trajectories: {len(trajs)}\n"
            f"Total steps: {total_steps}\n"
            f"Successes: {successes}"
        )

    @mcp.tool()
    def rem_list_sessions() -> str:
        """List all available REM sessions."""
        from .buffer import ExperienceBuffer
        buf = ExperienceBuffer()
        sessions = buf.all_sessions()
        if not sessions:
            return "No sessions found."
        lines = [f"- {s} ({buf.count(s)} trajectories)" for s in sessions]
        return "Sessions:\n" + "\n".join(lines)

    @mcp.tool()
    def rem_consolidate(session_id: str = "default") -> str:
        """Run consolidation on a session and return a short summary."""
        from .buffer import ExperienceBuffer
        from .consolidator import Consolidator
        buf = ExperienceBuffer()
        consolidator = Consolidator(buf)
        try:
            filtered, patterns, report = consolidator.run(session_id)
            for t in filtered:
                buf.add(t)
            return (
                f"Consolidated '{session_id}'\n"
                f"Reduction: {report.memory_reduction_ratio:.1%}\n"
                f"Est. token savings: {report.estimated_token_savings}\n"
                f"Failure patterns: {len(patterns)}"
            )
        except ValueError as e:
            return str(e)

    mcp.run()
