"""MCP Server stub for REM.

This is a minimal skeleton. Install the `mcp` extra and expand tools as needed.
"""

from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # type: ignore


def run_server() -> None:
    if FastMCP is None:
        raise ImportError("Please install the mcp package: pip install mcp")

    mcp = FastMCP("REM")

    @mcp.tool()
    def rem_stats(session_id: str = "default") -> str:
        """Return basic statistics for a REM session."""
        from .buffer import ExperienceBuffer
        buf = ExperienceBuffer()
        trajs = buf.list_by_session(session_id)
        if not trajs:
            return f"No data for session '{session_id}'"
        total_steps = sum(len(t.steps) for t in trajs)
        return (
            f"Session: {session_id}\n"
            f"Trajectories: {len(trajs)}\n"
            f"Total steps: {total_steps}"
        )

    @mcp.tool()
    def rem_consolidate(session_id: str = "default") -> str:
        """Trigger consolidation for a session and return a short report."""
        from .buffer import ExperienceBuffer
        from .consolidator import Consolidator
        buf = ExperienceBuffer()
        consolidator = Consolidator(buf)
        try:
            _, patterns, report = consolidator.run(session_id)
            return (
                f"Consolidated session '{session_id}'\n"
                f"Reduction: {report.memory_reduction_ratio:.1%}\n"
                f"Failure patterns: {len(patterns)}"
            )
        except ValueError as e:
            return str(e)

    mcp.run()
