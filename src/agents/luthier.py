"""
Guitar Luthier & Historian Agent

Expert in guitar construction, tonewood science, instrument history,
famous luthiers, pickup technology, and the evolution of guitar design.
"""

from src.agents.base import BaseAgent, AgentResponse, Tool


class LuthierHistorianAgent(BaseAgent):
    """Agent specializing in guitar construction, history, and lutherie."""

    def __init__(self, db_session_factory=None, **kwargs):
        self._db_factory = db_session_factory
        # Default config — can be overridden via kwargs or agents.yaml
        defaults = {
            "name": "luthier_historian",
            "role": "Guitar Luthier & Historian",
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.3,
            "max_tokens": 2000,
            "knowledge_base_path": "data/training/luthier_knowledge.md",
            "system_prompt": self._default_system_prompt(),
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def _register_tools(self) -> None:
        """Register luthier-specific database query tools."""

        self.register_tool(Tool(
            name="query_guitar_history",
            description="Search the guitar history database for entries about specific eras, luthiers, instruments, or innovations",
            parameters={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "The topic to search for (e.g., 'D'Angelico', 'archtop', '1950s')"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["luthier", "instrument", "innovation", "all"],
                        "description": "Category filter"
                    }
                },
                "required": ["search_term"],
            },
            handler=self._query_guitar_history,
        ))

        self.register_tool(Tool(
            name="query_wood_types",
            description="Query the database for information about tonewoods used in guitar construction",
            parameters={
                "type": "object",
                "properties": {
                    "wood_name": {
                        "type": "string",
                        "description": "Name of the wood (e.g., 'spruce', 'mahogany', 'rosewood')"
                    }
                },
                "required": ["wood_name"],
            },
            handler=self._query_wood_types,
        ))

        self.register_tool(Tool(
            name="search_knowledge_base",
            description="Search the luthier knowledge base for detailed information on any guitar construction or history topic",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"],
            },
            handler=self._search_knowledge_base,
        ))

    async def _query_guitar_history(self, search_term: str, category: str = "all") -> dict:
        """Query guitar history from the database."""
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_guitar_history, get_guitar_history
        async with self._db_factory() as session:
            if category and category != "all":
                results = await get_guitar_history(session, category=category)
            else:
                results = await search_guitar_history(session, search_term)
            return {"results": [
                {"title": h.title, "era": h.era, "category": h.category,
                 "content": h.content[:500], "summary": h.summary or "",
                 "key_figures": h.key_figures or [],
                 "instruments": h.instruments or []}
                for h in results
            ], "count": len(results)}

    async def _query_wood_types(self, wood_name: str) -> dict:
        """Query tonewood information from history entries."""
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_guitar_history
        async with self._db_factory() as session:
            results = await search_guitar_history(session, wood_name)
            return {"results": [
                {"title": h.title, "era": h.era, "content": h.content[:500],
                 "materials": h.materials or []}
                for h in results
            ], "count": len(results)}

    async def _search_knowledge_base(self, query: str) -> dict:
        """Search the knowledge base."""
        if self._knowledge_base:
            # Simple keyword search — will be replaced with vector search
            lines = self._knowledge_base.split("\n")
            relevant = [
                line for line in lines
                if query.lower() in line.lower()
            ]
            return {"results": relevant[:20], "total": len(relevant)}
        return {"results": [], "total": 0}

    def _generate_suggestions(self, content: str, context: dict | None = None) -> list[str]:
        """Generate luthier-specific follow-up suggestions."""
        suggestions = []
        content_lower = content.lower()

        if "archtop" in content_lower:
            suggestions.append("Would you like to know about archtop tonewoods?")
            suggestions.append("Want to hear about modern archtop builders?")
        if "fender" in content_lower or "telecaster" in content_lower or "stratocaster" in content_lower:
            suggestions.append("Interested in the differences between Fender body woods?")
        if "pickup" in content_lower:
            suggestions.append("Want to compare single-coil vs humbucker characteristics?")
        if "wood" in content_lower or "tonewood" in content_lower:
            suggestions.append("Should I explain how wood choice affects tone?")

        if not suggestions:
            suggestions = [
                "Ask me about any guitar brand or luthier",
                "Want to know about guitar construction techniques?",
                "Curious about the history of a specific guitar model?",
            ]

        return suggestions[:3]

    @staticmethod
    def _default_system_prompt() -> str:
        return """You are a world-class Guitar Luthier and Historian with decades of
experience building and restoring guitars, and encyclopedic knowledge
of guitar history.

## Your Expertise
- Guitar construction: acoustic, classical, archtop, electric, bass
- Tonewood science: spruce, mahogany, rosewood, maple, ebony, koa, cedar
- Historical evolution: Baroque guitar → classical → steel-string → archtop → electric
- Famous luthiers: Torres, Martin, Gibson, Fender, D'Angelico, D'Aquisto, Benedetto, PRS
- Pickup technology: single-coil, humbucker, P-90, piezo, active
- Setup, maintenance, repair: action, intonation, truss rod, fret work
- String science: gauge, material, tension, winding types

## Response Guidelines
- Be factual and precise — cite specific dates, names, and details
- Explain WHY materials and designs were chosen, not just WHAT was used
- Connect historical context to tone and playability
- Use analogies to help explain complex concepts
- If the question is about playing technique or music theory, acknowledge it
  but suggest consulting the Jazz Teacher for detailed guidance

## Boundaries
- Do not provide medical advice about playing injuries
- Do not fabricate historical facts — say "I'm not certain" if unsure
- For music theory or playing technique, defer to the Jazz Teacher agent"""
