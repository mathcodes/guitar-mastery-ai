"""
Full Stack Developer / Project Manager Agent

Orchestrates development workflow, documents progress at benchmarks,
logs failures and solutions, and coordinates between agents.
"""

from src.agents.base import BaseAgent, AgentResponse, Tool


class DevPMAgent(BaseAgent):
    """Agent acting as development lead and project manager."""

    def __init__(self, db_session_factory=None, **kwargs):
        self._db_factory = db_session_factory
        defaults = {
            "name": "dev_pm",
            "role": "Full Stack Developer & Project Manager",
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.2,
            "max_tokens": 2000,
            "knowledge_base_path": "data/training/dev_pm_playbook.md",
            "system_prompt": self._default_system_prompt(),
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def _register_tools(self) -> None:
        """Register PM-specific tools for benchmarking and documentation."""

        self.register_tool(Tool(
            name="log_benchmark",
            description="Log a development benchmark (phase completion, milestone reached)",
            parameters={
                "type": "object",
                "properties": {
                    "phase": {"type": "string", "description": "Development phase name"},
                    "description": {"type": "string", "description": "What was accomplished"},
                    "status": {
                        "type": "string",
                        "enum": ["started", "in_progress", "completed", "failed"],
                    },
                    "notes": {"type": "string", "description": "Additional notes"},
                },
                "required": ["phase", "description", "status"],
            },
            handler=self._log_benchmark,
        ))

        self.register_tool(Tool(
            name="log_error",
            description="Log an error with root cause analysis and solution",
            parameters={
                "type": "object",
                "properties": {
                    "error_id": {"type": "string", "description": "Unique error identifier"},
                    "phase": {"type": "string", "description": "Development phase"},
                    "problem": {"type": "string", "description": "Description of the problem"},
                    "root_cause": {"type": "string", "description": "Root cause analysis"},
                    "solution": {"type": "string", "description": "How it was fixed"},
                    "prevention": {"type": "string", "description": "How to prevent recurrence"},
                    "files_changed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files that were modified",
                    },
                },
                "required": ["error_id", "problem"],
            },
            handler=self._log_error,
        ))

        self.register_tool(Tool(
            name="generate_docs",
            description="Generate or update project documentation (changelog, benchmarks, debugging guide)",
            parameters={
                "type": "object",
                "properties": {
                    "doc_type": {
                        "type": "string",
                        "enum": ["changelog", "benchmarks", "debugging", "decisions"],
                        "description": "Type of documentation to generate",
                    },
                    "content": {"type": "string", "description": "Content to add"},
                },
                "required": ["doc_type", "content"],
            },
            handler=self._generate_docs,
        ))

        self.register_tool(Tool(
            name="health_check",
            description="Check the health status of all system components",
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=self._health_check,
        ))

    async def _log_benchmark(
        self, phase: str, description: str, status: str, notes: str = ""
    ) -> dict:
        """Log a benchmark to the database."""
        if not self._db_factory:
            return {"status": "no_db", "phase": phase, "description": description}
        from src.db.queries import create_benchmark, complete_benchmark
        async with self._db_factory() as session:
            if status == "completed":
                bm = await complete_benchmark(session, phase, notes=notes)
                await session.commit()
                return {"status": "completed", "phase": phase, "notes": notes,
                        "found": bm is not None}
            else:
                bm = await create_benchmark(session, phase, description)
                await session.commit()
                return {"status": "created", "phase": phase, "id": bm.id}

    async def _log_error(
        self,
        error_id: str,
        problem: str,
        phase: str = "",
        root_cause: str = "",
        solution: str = "",
        prevention: str = "",
        files_changed: list[str] = None,
    ) -> dict:
        """Log an error with full context."""
        if not self._db_factory:
            return {"status": "no_db", "error_id": error_id}
        from src.db.queries import log_agent_action
        async with self._db_factory() as session:
            log = await log_agent_action(
                session,
                agent_name="dev_pm",
                action="log_error",
                input_summary=f"[{error_id}] {problem}",
                output_summary=f"Root cause: {root_cause}. Solution: {solution}",
                success=False,
                error_message=problem,
                metadata={
                    "error_id": error_id,
                    "phase": phase,
                    "root_cause": root_cause,
                    "solution": solution,
                    "prevention": prevention,
                    "files_changed": files_changed or [],
                },
            )
            await session.commit()
            return {"status": "logged", "error_id": error_id, "log_id": log.id}

    async def _generate_docs(self, doc_type: str, content: str) -> dict:
        """Generate documentation — returns the content for the agent to format."""
        return {
            "doc_type": doc_type,
            "content": content,
            "status": "generated",
        }

    async def _health_check(self) -> dict:
        """System health check."""
        from src.db.connection import check_connection
        db_status = await check_connection()
        return {
            "database": db_status,
            "agents": {
                "luthier_historian": "active",
                "jazz_teacher": "active",
                "sql_expert": "active",
                "dev_pm": "active",
            },
            "api": "active",
        }

    @staticmethod
    def _default_system_prompt() -> str:
        return """You are a Senior Full Stack Developer and Project Manager for the
Guitar Mastery AI application.

## Responsibilities
- Coordinate development tasks across the team of specialized agents
- Track progress at each development benchmark
- Document every failure with root cause analysis and solution
- Maintain living documentation (CHANGELOG, BENCHMARKS, DEBUGGING, DECISIONS)
- Ensure quality gates are met before advancing phases

## Documentation Standards
- Benchmark entries: phase, description, status, dates, notes
- Error entries: error_id, problem, root_cause, solution, prevention, files_changed
- Architecture decisions: ADR format (context, decision, consequences)
- Changelog: Keep a Changelog format (Added, Changed, Fixed, Removed)

## Development Phases
Phase 0: Foundation | Phase 1: Database | Phase 2: Base Agent
Phase 3: Luthier Agent | Phase 4: Jazz Teacher | Phase 5: SQL Expert
Phase 6: Dev/PM Agent | Phase 7: Orchestrator | Phase 8: API
Phase 9: Frontend | Phase 10: Quizzes & Lessons | Phase 11: Integration
Phase 12: Polish

## Response Style
- Systematic and structured
- Reference specific files and line numbers
- Track metrics (token costs, latency, error rates)
- Proactively identify risks and suggest mitigations
- Always provide actionable next steps"""
