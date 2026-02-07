"""
SQLAlchemy ORM Models — Guitar Mastery AI

Defines all database tables for:
- Knowledge store (chords, scales, arpeggios, techniques, jazz standards, guitar history)
- User state (users, sessions, practice logs)
- Interactive features (quizzes, quiz attempts)
- System state (agent logs, benchmarks)
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ============================================================
# Knowledge Store Tables
# ============================================================

class Chord(Base):
    """Guitar chord definitions with voicings and theory data."""
    __tablename__ = "chords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    root = Column(String(10), nullable=False)
    chord_type = Column(String(50), nullable=False)  # maj7, min7, dom7, etc.
    formula = Column(String(100), nullable=False)     # 1 3 5 7
    intervals = Column(JSON, nullable=False)          # ["1", "3", "5", "7"]
    notes_in_c = Column(String(100))                  # C E G B (example in C)
    category = Column(String(50), nullable=False)     # jazz, blues, basic, altered
    voicings = Column(JSON)                           # [{frets: [...], fingers: [...]}]
    description = Column(Text)
    common_progressions = Column(JSON)                # ["ii-V-I", "I-vi-ii-V"]
    difficulty = Column(Integer, default=1)           # 1-5
    audio_ref = Column(String(255))
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_chords_category_type", "category", "chord_type"),
        Index("ix_chords_difficulty", "difficulty"),
    )


class Scale(Base):
    """Scale and mode definitions with positions and theory data."""
    __tablename__ = "scales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    scale_type = Column(String(50), nullable=False)   # mode, pentatonic, symmetric, etc.
    parent_scale = Column(String(100))                # e.g., "Major" for modes
    degree = Column(Integer)                          # Mode degree (1-7)
    formula = Column(String(100), nullable=False)     # 1 2 3 4 5 6 7
    intervals = Column(JSON, nullable=False)          # ["1", "2", "3", ...]
    notes_in_c = Column(String(100))                  # C D E F G A B
    category = Column(String(50), nullable=False)     # major_modes, minor_modes, etc.
    positions = Column(JSON)                          # Guitar fretboard positions
    chord_compatibility = Column(JSON)                # Which chords this scale fits
    description = Column(Text)
    character = Column(String(255))                   # "bright", "dark", "mysterious"
    common_usage = Column(Text)                       # When/where to use this scale
    difficulty = Column(Integer, default=1)
    audio_ref = Column(String(255))
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_scales_category_type", "category", "scale_type"),
        Index("ix_scales_difficulty", "difficulty"),
    )


class Arpeggio(Base):
    """Arpeggio definitions with fingering positions."""
    __tablename__ = "arpeggios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    arpeggio_type = Column(String(50), nullable=False)  # triad, seventh, extended
    formula = Column(String(100), nullable=False)
    intervals = Column(JSON, nullable=False)
    notes_in_c = Column(String(100))
    category = Column(String(50), nullable=False)
    positions = Column(JSON)
    related_chord = Column(String(100))
    related_scale = Column(String(100))
    description = Column(Text)
    applications = Column(Text)                         # Jazz improv applications
    difficulty = Column(Integer, default=1)
    audio_ref = Column(String(255))
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Technique(Base):
    """Guitar playing techniques with instructions and tips."""
    __tablename__ = "techniques"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False)       # picking, fretting, articulation
    subcategory = Column(String(50))                    # alternate, sweep, legato
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)         # Step-by-step how-to
    common_errors = Column(JSON)                        # List of common mistakes
    tips = Column(JSON)                                 # Pro tips
    exercises = Column(JSON)                            # Practice exercises
    difficulty = Column(Integer, default=1)
    prerequisites = Column(JSON)                        # Required prior techniques
    related_techniques = Column(JSON)
    famous_practitioners = Column(JSON)                 # Players known for this
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class JazzStandard(Base):
    """Jazz standard tunes with harmonic analysis."""
    __tablename__ = "jazz_standards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, unique=True, index=True)
    composer = Column(String(200), nullable=False)
    year = Column(Integer)
    key = Column(String(20), nullable=False)
    tempo_range = Column(String(50))                    # "medium swing 120-140"
    form = Column(String(50))                           # AABA, ABAC, blues, etc.
    measures = Column(Integer)                          # 32, 12, etc.
    changes = Column(JSON, nullable=False)              # Chord changes by measure
    analysis = Column(Text)                             # Harmonic analysis narrative
    common_substitutions = Column(JSON)                 # Reharmonization ideas
    key_concepts = Column(JSON)                         # ["ii-V-I", "tritone sub"]
    suggested_scales = Column(JSON)                     # Scale choices per section
    notable_recordings = Column(JSON)                   # Famous versions to study
    difficulty = Column(Integer, default=1)
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class GuitarHistory(Base):
    """Guitar history entries — eras, instruments, luthiers, innovations."""
    __tablename__ = "guitar_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    era = Column(String(100), nullable=False)           # "1920s-1930s", "Modern"
    category = Column(String(50), nullable=False)       # luthier, instrument, innovation
    content = Column(Text, nullable=False)              # Full article/entry
    summary = Column(Text)                              # Brief summary
    key_figures = Column(JSON)                          # People involved
    instruments = Column(JSON)                          # Instruments discussed
    materials = Column(JSON)                            # Woods, metals, etc.
    significance = Column(Text)                         # Why this matters
    related_entries = Column(JSON)                      # Links to other history entries
    images = Column(JSON)                               # Image references
    sources = Column(JSON)                              # Citations
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_guitar_history_era_cat", "era", "category"),
    )


# ============================================================
# Theory Links (Many-to-Many Relationships)
# ============================================================

class TheoryLink(Base):
    """Links between theory concepts (chord-scale, scale-arpeggio, etc.)."""
    __tablename__ = "theory_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(50), nullable=False)    # "chord", "scale", "arpeggio"
    source_id = Column(Integer, nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    relationship = Column(String(100), nullable=False)  # "compatible_scale", "parent_arpeggio"
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_theory_links_source", "source_type", "source_id"),
        Index("ix_theory_links_target", "target_type", "target_id"),
    )


# ============================================================
# User State Tables
# ============================================================

class User(Base):
    """Application users with preferences and goals."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100))
    skill_level = Column(String(20), default="intermediate")  # beginner/intermediate/advanced
    preferences = Column(JSON, default=dict)            # UI prefs, notation style, etc.
    goals = Column(JSON, default=list)                  # Learning goals
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    sessions = relationship("Session", back_populates="user")
    practice_logs = relationship("PracticeLog", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")


class Session(Base):
    """Conversation sessions tracking agent interactions."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_key = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    agents_used = Column(JSON, default=list)
    messages = Column(JSON, default=list)               # Conversation history
    context = Column(JSON, default=dict)                # Accumulated context
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")


class PracticeLog(Base):
    """User practice session tracking."""
    __tablename__ = "practice_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    topic = Column(String(200), nullable=False)
    category = Column(String(50))                       # theory, technique, repertoire
    duration_minutes = Column(Integer)
    notes = Column(Text)
    exercises_completed = Column(JSON)
    score = Column(Float)                               # 0-100 if applicable
    difficulty_level = Column(Integer)
    feedback = Column(Text)                             # Agent-generated feedback
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="practice_logs")


# ============================================================
# Interactive Features Tables
# ============================================================

class Quiz(Base):
    """Generated quizzes with questions and metadata."""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, default=1)
    question_count = Column(Integer, nullable=False)
    questions = Column(JSON, nullable=False)            # [{question, options, answer, explanation}]
    created_by = Column(String(50), default="jazz_teacher")  # Agent that created it
    time_limit_seconds = Column(Integer)
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QuizAttempt(Base):
    """User quiz attempt results."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False)              # User's answers
    score = Column(Float, nullable=False)               # Percentage correct
    time_taken_seconds = Column(Integer)
    feedback = Column(Text)                             # Agent-generated review
    areas_to_improve = Column(JSON)
    taken_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="quiz_attempts")


class Lesson(Base):
    """Interactive lesson definitions."""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)       # theory, technique, history, improv
    difficulty = Column(Integer, default=1)
    objectives = Column(JSON, nullable=False)           # Learning objectives
    prerequisites = Column(JSON, default=list)
    steps = Column(JSON, nullable=False)                # [{type, content, interaction}]
    estimated_minutes = Column(Integer)
    created_by = Column(String(50), default="jazz_teacher")
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================================================
# System State Tables
# ============================================================

class AgentLog(Base):
    """Detailed log of all agent actions for debugging and analytics."""
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)        # "think", "use_tool", "route"
    input_summary = Column(Text)                        # Summarized input (not full prompt)
    output_summary = Column(Text)                       # Summarized output
    tool_used = Column(String(100))
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    session_id = Column(String(64))
    extra_data = Column("metadata", JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Benchmark(Base):
    """Development benchmark tracking across project phases."""
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phase = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending/in_progress/completed/failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    failures = Column(JSON, default=list)               # [{error, timestamp, context}]
    solutions = Column(JSON, default=list)              # [{fix, timestamp, files_changed}]
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class KnowledgeGap(Base):
    """Tracks questions/topics the agents couldn't answer well."""
    __tablename__ = "knowledge_gaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(50), nullable=False)
    user_query = Column(Text, nullable=False)
    confidence_score = Column(Float)                    # Agent's self-assessed confidence
    category = Column(String(50))
    resolution_status = Column(String(20), default="open")  # open/resolved/wont_fix
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime)
