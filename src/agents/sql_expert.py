"""
SQL Expert Agent with Natural Language Recognition

Translates natural language queries to optimized, safe SQL queries,
executes them against the SQLite database, and formats results.
"""

from src.agents.base import BaseAgent, AgentResponse, Tool


class SQLExpertAgent(BaseAgent):
    """Agent specializing in NL-to-SQL translation and database operations."""

    def __init__(self, db_session_factory=None, **kwargs):
        self._db_factory = db_session_factory
        defaults = {
            "name": "sql_expert",
            "role": "SQL & Data Expert with Natural Language Recognition",
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.1,
            "max_tokens": 1500,
            "knowledge_base_path": "data/training/sql_patterns.md",
            "system_prompt": self._default_system_prompt(),
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def _register_tools(self) -> None:
        """Register SQL-specific tools."""

        self.register_tool(Tool(
            name="execute_query",
            description="Execute a validated SELECT query against the SQLite database and return results",
            parameters={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SQL SELECT query to execute"},
                    "params": {
                        "type": "object",
                        "description": "Query parameters for parameterized queries",
                        "additionalProperties": True,
                    },
                },
                "required": ["sql"],
            },
            handler=self._execute_query,
        ))

        self.register_tool(Tool(
            name="get_schema",
            description="Get the schema (column names and types) for a specific database table",
            parameters={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to inspect",
                        "enum": [
                            "chords", "scales", "arpeggios", "techniques",
                            "jazz_standards", "guitar_history", "users",
                            "sessions", "practice_logs", "quizzes",
                            "quiz_attempts", "agent_logs", "benchmarks",
                        ],
                    },
                },
                "required": ["table_name"],
            },
            handler=self._get_schema,
        ))

        self.register_tool(Tool(
            name="validate_sql",
            description="Validate a SQL query for safety (injection prevention) and correctness",
            parameters={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SQL query to validate"},
                },
                "required": ["sql"],
            },
            handler=self._validate_sql,
        ))

        self.register_tool(Tool(
            name="format_results",
            description="Format raw query results into a readable table or summary",
            parameters={
                "type": "object",
                "properties": {
                    "results": {"type": "array", "description": "Array of result rows"},
                    "format": {
                        "type": "string",
                        "enum": ["table", "list", "summary"],
                        "description": "Output format",
                    },
                },
                "required": ["results"],
            },
            handler=self._format_results,
        ))

    async def _execute_query(self, sql: str, params: dict = None) -> dict:
        """Execute a validated SELECT query against the database."""
        # Validation first
        validation = await self._validate_sql(sql)
        if not validation["is_valid"]:
            return {"error": validation["reason"], "results": []}

        if not self._db_factory:
            return {"error": "Database not connected", "results": []}

        from src.db.queries import execute_safe_select
        try:
            async with self._db_factory() as session:
                results = await execute_safe_select(session, sql, params)
                return {
                    "results": results,
                    "count": len(results),
                    "sql": sql,
                }
        except Exception as e:
            return {"error": str(e), "results": []}

    async def _get_schema(self, table_name: str) -> dict:
        """Return schema information for a table."""
        # Schema definitions matching our models.py
        schemas = {
            "chords": {
                "columns": [
                    "id INTEGER PRIMARY KEY",
                    "name TEXT NOT NULL UNIQUE",
                    "root TEXT NOT NULL",
                    "chord_type TEXT NOT NULL",
                    "formula TEXT NOT NULL",
                    "intervals JSON NOT NULL",
                    "notes_in_c TEXT",
                    "category TEXT NOT NULL",
                    "voicings JSON",
                    "description TEXT",
                    "common_progressions JSON",
                    "difficulty INTEGER DEFAULT 1",
                    "tags JSON",
                ],
                "indexes": ["ix_chords_category_type (category, chord_type)", "ix_chords_difficulty (difficulty)"],
                "notes": "Use json_extract() to query JSON columns. Category values: jazz, altered, basic, modern-jazz",
            },
            "scales": {
                "columns": [
                    "id INTEGER PRIMARY KEY",
                    "name TEXT NOT NULL UNIQUE",
                    "scale_type TEXT NOT NULL",
                    "parent_scale TEXT",
                    "degree INTEGER",
                    "formula TEXT NOT NULL",
                    "intervals JSON NOT NULL",
                    "notes_in_c TEXT",
                    "category TEXT NOT NULL",
                    "chord_compatibility JSON",
                    "description TEXT",
                    "character TEXT",
                    "common_usage TEXT",
                    "difficulty INTEGER DEFAULT 1",
                    "tags JSON",
                ],
                "indexes": ["ix_scales_category_type (category, scale_type)"],
                "notes": "Categories: major_modes, melodic_minor_modes, symmetric, bebop, pentatonic",
            },
            "jazz_standards": {
                "columns": [
                    "id INTEGER PRIMARY KEY",
                    "title TEXT NOT NULL UNIQUE",
                    "composer TEXT NOT NULL",
                    "year INTEGER",
                    "key TEXT NOT NULL",
                    "tempo_range TEXT",
                    "form TEXT",
                    "measures INTEGER",
                    "changes JSON NOT NULL",
                    "analysis TEXT",
                    "common_substitutions JSON",
                    "key_concepts JSON",
                    "suggested_scales JSON",
                    "notable_recordings JSON",
                    "difficulty INTEGER DEFAULT 1",
                    "tags JSON",
                ],
                "indexes": [],
                "notes": "Changes are stored as JSON objects with section keys (A1, A2, B, C)",
            },
        }
        return schemas.get(table_name, {"error": f"Schema not found for '{table_name}'"})

    async def _validate_sql(self, sql: str) -> dict:
        """Validate SQL for safety."""
        sql_upper = sql.strip().upper()

        # Must be SELECT
        if not sql_upper.startswith("SELECT"):
            return {"is_valid": False, "reason": "Only SELECT queries are allowed"}

        # Check for forbidden keywords
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
                      "EXEC", "TRUNCATE", "--", ";--", "/*"]
        for keyword in forbidden:
            if keyword in sql_upper:
                return {"is_valid": False, "reason": f"Forbidden keyword: {keyword}"}

        return {"is_valid": True, "reason": "Query passed validation"}

    async def _format_results(self, results: list, format: str = "table") -> dict:
        """Format query results."""
        if not results:
            return {"formatted": "No results found.", "count": 0}

        if format == "summary":
            return {"formatted": f"Found {len(results)} results.", "count": len(results)}

        # Table format
        if isinstance(results[0], dict):
            headers = list(results[0].keys())
            rows = [list(row.values()) for row in results]
        else:
            headers = [f"col_{i}" for i in range(len(results[0]))]
            rows = results

        # Build markdown table
        header_row = "| " + " | ".join(str(h) for h in headers) + " |"
        separator = "| " + " | ".join("---" for _ in headers) + " |"
        data_rows = "\n".join(
            "| " + " | ".join(str(v) for v in row) + " |"
            for row in rows
        )

        return {
            "formatted": f"{header_row}\n{separator}\n{data_rows}",
            "count": len(results),
        }

    @staticmethod
    def _default_system_prompt() -> str:
        return """You are an expert SQL developer specializing in SQLite databases.
Your job is to translate natural language questions into accurate, optimized,
and SAFE SQL queries against the Guitar Mastery knowledge base.

## Available Tables
- **chords**: name, root, chord_type, formula, intervals (JSON), category, voicings (JSON), difficulty
- **scales**: name, scale_type, parent_scale, formula, intervals (JSON), category, chord_compatibility (JSON), difficulty
- **arpeggios**: name, arpeggio_type, formula, intervals (JSON), category, difficulty
- **techniques**: name, category, description, difficulty, instructions
- **jazz_standards**: title, composer, year, key, form, changes (JSON), analysis, difficulty
- **guitar_history**: title, era, category, content, key_figures (JSON), instruments (JSON)
- **practice_logs**: user_id, topic, duration_minutes, score
- **quizzes**: title, topic, difficulty, questions (JSON)

## Security Rules (ABSOLUTE)
1. ONLY generate SELECT statements
2. NEVER use DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
3. ALL values must use parameterized placeholders (?)
4. NEVER concatenate user input into SQL strings
5. Always add LIMIT (default 50) unless user specifies
6. Validate ALL generated SQL before execution

## SQLite JSON Functions
- json_extract(column, '$.key') — extract a value
- json_each(column) — iterate JSON arrays
- column LIKE '%term%' — search within JSON string representation

## Workflow
1. Understand the user's intent
2. Identify which table(s) to query
3. Generate optimized SQL with parameters
4. Validate the query
5. Execute and format results
6. Provide a natural language summary"""
