"""
Pre-built Query Library

Provides typed, parameterized query functions for all database operations.
These are the ONLY way agents should access the database — never raw SQL strings.

Usage:
    from src.db.queries import get_chords_by_category, search_scales

    chords = await get_chords_by_category(session, "jazz", difficulty_min=3)
"""

from typing import Optional
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import (
    Chord, Scale, Arpeggio, Technique, JazzStandard,
    GuitarHistory, User, Session, PracticeLog, Quiz,
    QuizAttempt, AgentLog, Benchmark, KnowledgeGap,
)


# ============================================================
# Chord Queries
# ============================================================

async def get_chords(
    db: AsyncSession,
    category: Optional[str] = None,
    chord_type: Optional[str] = None,
    difficulty_min: int = 1,
    difficulty_max: int = 5,
    limit: int = 50,
) -> list[Chord]:
    """Query chords with optional filters."""
    query = select(Chord).where(
        Chord.is_active == True,
        Chord.difficulty >= difficulty_min,
        Chord.difficulty <= difficulty_max,
    )
    if category:
        query = query.where(Chord.category == category)
    if chord_type:
        query = query.where(Chord.chord_type == chord_type)
    query = query.order_by(Chord.difficulty, Chord.name).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_chords(db: AsyncSession, search_term: str, limit: int = 20) -> list[Chord]:
    """Full-text search across chord names, descriptions, and formulas."""
    pattern = f"%{search_term}%"
    query = select(Chord).where(
        Chord.is_active == True,
        or_(
            Chord.name.ilike(pattern),
            Chord.description.ilike(pattern),
            Chord.formula.ilike(pattern),
        )
    ).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_chord_by_name(db: AsyncSession, name: str) -> Optional[Chord]:
    """Get a single chord by exact name."""
    query = select(Chord).where(Chord.name == name, Chord.is_active == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# ============================================================
# Scale Queries
# ============================================================

async def get_scales(
    db: AsyncSession,
    category: Optional[str] = None,
    scale_type: Optional[str] = None,
    difficulty_min: int = 1,
    difficulty_max: int = 5,
    limit: int = 50,
) -> list[Scale]:
    """Query scales with optional filters."""
    query = select(Scale).where(
        Scale.is_active == True,
        Scale.difficulty >= difficulty_min,
        Scale.difficulty <= difficulty_max,
    )
    if category:
        query = query.where(Scale.category == category)
    if scale_type:
        query = query.where(Scale.scale_type == scale_type)
    query = query.order_by(Scale.difficulty, Scale.name).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_scales(db: AsyncSession, search_term: str, limit: int = 20) -> list[Scale]:
    """Search scales by name, description, or character."""
    pattern = f"%{search_term}%"
    query = select(Scale).where(
        Scale.is_active == True,
        or_(
            Scale.name.ilike(pattern),
            Scale.description.ilike(pattern),
            Scale.character.ilike(pattern),
        )
    ).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_scales_for_chord(db: AsyncSession, chord_name: str) -> list[Scale]:
    """Find scales compatible with a given chord."""
    query = select(Scale).where(
        Scale.is_active == True,
        func.json_extract(Scale.chord_compatibility, "$").like(f"%{chord_name}%")
    )
    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================
# Arpeggio Queries
# ============================================================

async def get_arpeggios(
    db: AsyncSession,
    category: Optional[str] = None,
    difficulty_min: int = 1,
    difficulty_max: int = 5,
    limit: int = 50,
) -> list[Arpeggio]:
    """Query arpeggios with optional filters."""
    query = select(Arpeggio).where(
        Arpeggio.is_active == True,
        Arpeggio.difficulty >= difficulty_min,
        Arpeggio.difficulty <= difficulty_max,
    )
    if category:
        query = query.where(Arpeggio.category == category)
    query = query.order_by(Arpeggio.difficulty, Arpeggio.name).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================
# Technique Queries
# ============================================================

async def get_techniques(
    db: AsyncSession,
    category: Optional[str] = None,
    difficulty_min: int = 1,
    difficulty_max: int = 5,
    limit: int = 50,
) -> list[Technique]:
    """Query techniques with optional filters."""
    query = select(Technique).where(
        Technique.is_active == True,
        Technique.difficulty >= difficulty_min,
        Technique.difficulty <= difficulty_max,
    )
    if category:
        query = query.where(Technique.category == category)
    query = query.order_by(Technique.difficulty, Technique.name).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_techniques(db: AsyncSession, search_term: str, limit: int = 20) -> list[Technique]:
    """Search techniques by name or description."""
    pattern = f"%{search_term}%"
    query = select(Technique).where(
        Technique.is_active == True,
        or_(
            Technique.name.ilike(pattern),
            Technique.description.ilike(pattern),
        )
    ).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================
# Jazz Standards Queries
# ============================================================

async def get_jazz_standards(
    db: AsyncSession,
    key: Optional[str] = None,
    difficulty_min: int = 1,
    difficulty_max: int = 5,
    limit: int = 50,
) -> list[JazzStandard]:
    """Query jazz standards with optional filters."""
    query = select(JazzStandard).where(
        JazzStandard.is_active == True,
        JazzStandard.difficulty >= difficulty_min,
        JazzStandard.difficulty <= difficulty_max,
    )
    if key:
        query = query.where(JazzStandard.key == key)
    query = query.order_by(JazzStandard.title).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_jazz_standards(db: AsyncSession, search_term: str, limit: int = 20) -> list[JazzStandard]:
    """Search standards by title, composer, or analysis."""
    pattern = f"%{search_term}%"
    query = select(JazzStandard).where(
        JazzStandard.is_active == True,
        or_(
            JazzStandard.title.ilike(pattern),
            JazzStandard.composer.ilike(pattern),
            JazzStandard.analysis.ilike(pattern),
        )
    ).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================
# Guitar History Queries
# ============================================================

async def get_guitar_history(
    db: AsyncSession,
    era: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
) -> list[GuitarHistory]:
    """Query guitar history entries."""
    query = select(GuitarHistory).where(GuitarHistory.is_active == True)
    if era:
        query = query.where(GuitarHistory.era == era)
    if category:
        query = query.where(GuitarHistory.category == category)
    query = query.order_by(GuitarHistory.era, GuitarHistory.title).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_guitar_history(db: AsyncSession, search_term: str, limit: int = 20) -> list[GuitarHistory]:
    """Search history by title, content, or key figures."""
    pattern = f"%{search_term}%"
    query = select(GuitarHistory).where(
        GuitarHistory.is_active == True,
        or_(
            GuitarHistory.title.ilike(pattern),
            GuitarHistory.content.ilike(pattern),
        )
    ).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================
# User & Session Queries
# ============================================================

async def get_or_create_user(db: AsyncSession, username: str) -> User:
    """Get existing user or create a new one."""
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        user = User(username=username)
        db.add(user)
        await db.flush()
    return user


async def get_user_practice_stats(db: AsyncSession, user_id: int) -> dict:
    """Get aggregated practice statistics for a user."""
    total_time = await db.execute(
        select(func.sum(PracticeLog.duration_minutes))
        .where(PracticeLog.user_id == user_id)
    )
    total_sessions = await db.execute(
        select(func.count(PracticeLog.id))
        .where(PracticeLog.user_id == user_id)
    )
    avg_score = await db.execute(
        select(func.avg(PracticeLog.score))
        .where(PracticeLog.user_id == user_id, PracticeLog.score.isnot(None))
    )
    return {
        "total_practice_minutes": total_time.scalar() or 0,
        "total_sessions": total_sessions.scalar() or 0,
        "average_score": round(avg_score.scalar() or 0, 1),
    }


# ============================================================
# Agent Logging Queries
# ============================================================

async def log_agent_action(
    db: AsyncSession,
    agent_name: str,
    action: str,
    input_summary: str = "",
    output_summary: str = "",
    tool_used: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    latency_ms: int = 0,
    success: bool = True,
    error_message: str = "",
    session_id: str = "",
    metadata: dict = None,
) -> AgentLog:
    """Log an agent action to the database."""
    log = AgentLog(
        agent_name=agent_name,
        action=action,
        input_summary=input_summary,
        output_summary=output_summary,
        tool_used=tool_used,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        latency_ms=latency_ms,
        success=success,
        error_message=error_message,
        session_id=session_id,
        extra_data=metadata or {},
    )
    db.add(log)
    await db.flush()
    return log


# ============================================================
# Benchmark Queries
# ============================================================

async def create_benchmark(
    db: AsyncSession,
    phase: str,
    description: str,
) -> Benchmark:
    """Create a new development benchmark entry."""
    from datetime import datetime, timezone
    benchmark = Benchmark(
        phase=phase,
        description=description,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    db.add(benchmark)
    await db.flush()
    return benchmark


async def complete_benchmark(
    db: AsyncSession,
    phase: str,
    notes: str = "",
) -> Optional[Benchmark]:
    """Mark a benchmark phase as completed."""
    from datetime import datetime, timezone
    query = select(Benchmark).where(Benchmark.phase == phase, Benchmark.status == "in_progress")
    result = await db.execute(query)
    benchmark = result.scalar_one_or_none()
    if benchmark:
        benchmark.status = "completed"
        benchmark.completed_at = datetime.now(timezone.utc)
        benchmark.notes = notes
        await db.flush()
    return benchmark


# ============================================================
# Dynamic NL-to-SQL Query Execution (for SQL Expert Agent)
# ============================================================

async def execute_safe_select(db: AsyncSession, sql: str, params: dict = None) -> list[dict]:
    """
    Execute a validated SELECT query safely.

    SECURITY: Only SELECT statements are allowed. This function validates
    the SQL before execution and wraps results with LIMIT protection.
    """
    # Security validation
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for user requests.")

    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "EXEC", "TRUNCATE"]
    for keyword in forbidden:
        if keyword in sql_upper:
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    # Ensure LIMIT exists
    if "LIMIT" not in sql_upper:
        sql = f"{sql.rstrip().rstrip(';')} LIMIT 50"

    # Execute with parameters
    result = await db.execute(text(sql), params or {})
    columns = result.keys()
    rows = result.fetchall()

    return [dict(zip(columns, row)) for row in rows]
