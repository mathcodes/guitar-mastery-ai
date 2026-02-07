"""
Jazz Guitar Teacher Agent (Mastery Level)

Master jazz guitar educator covering theory, technique, improvisation,
repertoire, practice methodology, and helping players break through plateaus.
"""

from src.agents.base import BaseAgent, AgentResponse, Tool


class JazzTeacherAgent(BaseAgent):
    """Agent specializing in jazz guitar education at the mastery level."""

    def __init__(self, db_session_factory=None, **kwargs):
        self._db_factory = db_session_factory
        defaults = {
            "name": "jazz_teacher",
            "role": "Jazz Guitar Teacher (Mastery Level)",
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.5,
            "max_tokens": 2500,
            "knowledge_base_path": "data/training/jazz_teacher_knowledge.md",
            "system_prompt": self._default_system_prompt(),
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def _register_tools(self) -> None:
        """Register jazz teacher tools for theory queries, exercises, and quizzes."""

        self.register_tool(Tool(
            name="query_chords",
            description="Search the chord database by type, category, or difficulty",
            parameters={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Chord name or type to search"},
                    "category": {"type": "string", "description": "Category: jazz, altered, basic, modern-jazz"},
                    "difficulty_max": {"type": "integer", "description": "Maximum difficulty (1-5)"},
                },
                "required": ["search_term"],
            },
            handler=self._query_chords,
        ))

        self.register_tool(Tool(
            name="query_scales",
            description="Search the scale/mode database by name, type, or chord compatibility",
            parameters={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Scale name or type to search"},
                    "chord_compatibility": {"type": "string", "description": "Find scales for this chord type"},
                },
                "required": ["search_term"],
            },
            handler=self._query_scales,
        ))

        self.register_tool(Tool(
            name="query_jazz_standards",
            description="Search the jazz standards database by title, composer, or key",
            parameters={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Song title, composer, or key"},
                },
                "required": ["search_term"],
            },
            handler=self._query_jazz_standards,
        ))

        self.register_tool(Tool(
            name="query_techniques",
            description="Search the technique database for guitar techniques and practice methods",
            parameters={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Technique name or category"},
                },
                "required": ["search_term"],
            },
            handler=self._query_techniques,
        ))

        self.register_tool(Tool(
            name="generate_exercise",
            description="Generate a practice exercise for a specific topic and difficulty level",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic for the exercise"},
                    "difficulty": {"type": "integer", "description": "Difficulty 1-5"},
                    "skill_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                },
                "required": ["topic"],
            },
            handler=self._generate_exercise,
        ))

        self.register_tool(Tool(
            name="generate_quiz",
            description="Generate an interactive quiz on a music theory or guitar topic",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Quiz topic"},
                    "num_questions": {"type": "integer", "description": "Number of questions (3-10)"},
                    "difficulty": {"type": "integer", "description": "Difficulty 1-5"},
                },
                "required": ["topic"],
            },
            handler=self._generate_quiz,
        ))

    async def _query_chords(self, search_term: str, category: str = None, difficulty_max: int = 5) -> dict:
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_chords, get_chords
        async with self._db_factory() as session:
            if category:
                results = await get_chords(session, category=category, difficulty_max=difficulty_max)
            else:
                results = await search_chords(session, search_term)
            return {"results": [
                {"name": c.name, "formula": c.formula, "category": c.category,
                 "description": c.description or "", "difficulty": c.difficulty,
                 "intervals": c.intervals}
                for c in results
            ], "count": len(results)}

    async def _query_scales(self, search_term: str, chord_compatibility: str = None) -> dict:
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_scales, get_scales
        async with self._db_factory() as session:
            results = await search_scales(session, search_term)
            return {"results": [
                {"name": s.name, "formula": s.formula, "category": s.category,
                 "character": s.character or "", "description": s.description or "",
                 "chord_compatibility": s.chord_compatibility or [],
                 "common_usage": s.common_usage or "", "difficulty": s.difficulty}
                for s in results
            ], "count": len(results)}

    async def _query_jazz_standards(self, search_term: str) -> dict:
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_jazz_standards
        async with self._db_factory() as session:
            results = await search_jazz_standards(session, search_term)
            return {"results": [
                {"title": s.title, "composer": s.composer, "key": s.key,
                 "form": s.form, "analysis": s.analysis or "",
                 "difficulty": s.difficulty}
                for s in results
            ], "count": len(results)}

    async def _query_techniques(self, search_term: str) -> dict:
        if not self._db_factory:
            return {"results": [], "note": "Database not connected"}
        from src.db.queries import search_techniques
        async with self._db_factory() as session:
            results = await search_techniques(session, search_term)
            return {"results": [
                {"name": t.name, "category": t.category,
                 "description": t.description, "difficulty": t.difficulty,
                 "instructions": t.instructions,
                 "tips": t.tips or [], "exercises": t.exercises or []}
                for t in results
            ], "count": len(results)}

    async def _generate_exercise(self, topic: str, difficulty: int = 2, skill_level: str = "intermediate") -> dict:
        return {"tool": "generate_exercise", "topic": topic, "difficulty": difficulty, "skill_level": skill_level}

    async def _generate_quiz(self, topic: str, num_questions: int = 5, difficulty: int = 2) -> dict:
        return {"tool": "generate_quiz", "topic": topic, "num_questions": num_questions, "difficulty": difficulty}

    def _generate_suggestions(self, content: str, context: dict | None = None) -> list[str]:
        """Generate teaching-oriented follow-up suggestions."""
        suggestions = []
        content_lower = content.lower()

        if "chord" in content_lower:
            suggestions.append("Want me to quiz you on chord types?")
            suggestions.append("Should I show you voicings for this chord?")
        if "scale" in content_lower or "mode" in content_lower:
            suggestions.append("Want a practice exercise for this scale?")
            suggestions.append("Should I show you which chords this scale works over?")
        if "solo" in content_lower or "improvise" in content_lower or "improvisation" in content_lower:
            suggestions.append("Want some specific licks to practice over this?")
        if "rut" in content_lower or "plateau" in content_lower or "stuck" in content_lower:
            suggestions.append("Want a customized plateau-busting practice plan?")
        if "standard" in content_lower or "tune" in content_lower:
            suggestions.append("Want me to analyze the chord changes for this tune?")

        if not suggestions:
            suggestions = [
                "Quiz me on jazz theory",
                "Give me a practice exercise",
                "Help me with improvisation",
                "Recommend jazz standards to learn",
            ]

        return suggestions[:3]

    @staticmethod
    def _default_system_prompt() -> str:
        return """You are a Master Jazz Guitar Teacher with 30+ years of performing
and teaching experience. You've studied with legends, performed at major
festivals, and taught students from beginners to professionals.

## Your Expertise
- **Chord Theory**: Triads → seventh chords → extensions → alterations → polychords
- **Scale Systems**: All modes (major, melodic minor, harmonic minor); symmetric scales;
  bebop scales; pentatonic applications; exotic scales
- **Arpeggio Mastery**: Chord-tone arpeggios, superimposition, targeting, enclosures
- **Improvisation**: Guide tones, voice leading, motivic development, rhythmic
  displacement, tension and release
- **Comping**: Freddie Green, chord melody, rootless voicings, quartal voicings
- **Repertoire**: 200+ jazz standards with analysis
- **Technique**: All picking styles, legato, chord melody, walking bass
- **Practice Methodology**: Structured routines, plateau-busting strategies
- **Player Styles**: Wes Montgomery, Joe Pass, Pat Metheny, Jim Hall, etc.

## Teaching Philosophy
- Meet the student where they are — adapt to their level
- Explain WHY, not just WHAT
- Provide practical, immediately usable examples
- Connect theory to real musical situations
- When a student is stuck, find the root cause first

## Response Format
- Use interval numbers (1 b3 5 b7) alongside note names
- Suggest recordings to listen to when relevant
- Offer follow-up exercises when teaching concepts
- For guitar history/construction questions, defer to the Luthier agent

## Boundaries
- No medical advice about playing injuries
- For guitar construction/repair, defer to the Luthier
- Acknowledge non-jazz genres but help when possible"""
