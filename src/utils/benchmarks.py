"""
Benchmark Tracker — Tracks development progress and generates reports.

Usage:
    tracker = BenchmarkTracker(db_session)
    await tracker.start_phase("Phase 1", "Database schema and seed data")
    ...
    await tracker.complete_phase("Phase 1", notes="All tables created")
"""

from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("benchmarks")


class BenchmarkTracker:
    """Track development progress against defined phases."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._in_memory_log: list[dict] = []

    async def start_phase(self, phase: str, description: str) -> dict:
        """Mark a phase as started."""
        entry = {
            "phase": phase,
            "description": description,
            "status": "in_progress",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "failures": [],
            "solutions": [],
            "notes": "",
        }
        self._in_memory_log.append(entry)
        logger.info("phase_started", phase=phase, description=description)

        if self.db:
            from src.db.queries import create_benchmark
            await create_benchmark(self.db, phase, description)

        return entry

    async def complete_phase(self, phase: str, notes: str = "") -> Optional[dict]:
        """Mark a phase as completed."""
        for entry in self._in_memory_log:
            if entry["phase"] == phase and entry["status"] == "in_progress":
                entry["status"] = "completed"
                entry["completed_at"] = datetime.now(timezone.utc).isoformat()
                entry["notes"] = notes
                logger.info("phase_completed", phase=phase, notes=notes)

                if self.db:
                    from src.db.queries import complete_benchmark
                    await complete_benchmark(self.db, phase, notes)

                return entry
        return None

    async def log_failure(self, phase: str, error: str, solution: str = "") -> dict:
        """Log a failure within a phase."""
        failure = {
            "error": error,
            "solution": solution,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for entry in self._in_memory_log:
            if entry["phase"] == phase:
                entry["failures"].append(failure)
                if solution:
                    entry["solutions"].append({"fix": solution, "timestamp": failure["timestamp"]})
                break

        logger.warning("phase_failure", phase=phase, error=error, solution=solution)
        return failure

    def generate_report(self) -> str:
        """Generate a markdown report of all benchmarks."""
        lines = ["# Benchmark Report", "", "| Phase | Status | Started | Completed | Failures |", "|-------|--------|---------|-----------|----------|"]

        for entry in self._in_memory_log:
            started = entry["started_at"][:10] if entry["started_at"] else "—"
            completed = entry["completed_at"][:10] if entry["completed_at"] else "—"
            failures = len(entry["failures"])
            status_emoji = {"completed": "Done", "in_progress": "Active", "failed": "FAILED"}.get(entry["status"], entry["status"])

            lines.append(f"| {entry['phase']} | {status_emoji} | {started} | {completed} | {failures} |")

        return "\n".join(lines)
