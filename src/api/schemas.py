"""
Pydantic Schemas — Request/response models for all API endpoints.

These schemas provide:
- Automatic validation
- OpenAPI documentation
- Type safety
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ============================================================
# Quiz Schemas
# ============================================================

class QuizGenerateRequest(BaseModel):
    """Request to generate a new quiz."""
    topic: str = Field(..., description="Quiz topic (chords, scales, history, technique)")
    num_questions: int = Field(5, ge=3, le=15, description="Number of questions")
    difficulty: int = Field(2, ge=1, le=5, description="Difficulty level 1-5")
    skill_level: str = Field("intermediate", description="User skill level")


class QuizQuestion(BaseModel):
    """A single quiz question."""
    question: str
    type: str = "multiple_choice"
    options: list[str]
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    """Generated quiz response."""
    id: int
    title: str
    topic: str
    difficulty: int
    questions: list[QuizQuestion]
    time_limit_seconds: Optional[int] = 300


class QuizSubmitRequest(BaseModel):
    """Submit quiz answers."""
    quiz_id: int
    answers: list[str] = Field(..., description="List of selected answers")
    time_taken_seconds: Optional[int] = None


class QuizResultResponse(BaseModel):
    """Quiz attempt results."""
    score: float
    total_questions: int
    correct_count: int
    feedback: str
    areas_to_improve: list[str]
    suggestions: list[str]


# ============================================================
# Practice Schemas
# ============================================================

class PracticeLogRequest(BaseModel):
    """Log a practice session."""
    topic: str
    category: str = Field(..., description="theory, technique, repertoire, etc.")
    duration_minutes: int = Field(..., ge=1, description="Practice duration")
    notes: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=100)


class PracticeLogResponse(BaseModel):
    """Practice session record."""
    id: int
    topic: str
    category: str
    duration_minutes: int
    notes: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    created_at: datetime


class PracticeStatsResponse(BaseModel):
    """Aggregated practice statistics."""
    total_practice_minutes: int
    total_sessions: int
    average_score: float
    topics_covered: list[str]
    streak_days: int


# ============================================================
# Reference Data Schemas
# ============================================================

class ChordResponse(BaseModel):
    """Chord data response."""
    id: int
    name: str
    chord_type: str
    formula: str
    intervals: list[str]
    notes_in_c: Optional[str]
    category: str
    description: Optional[str]
    difficulty: int
    voicings: Optional[list[dict]] = None


class ScaleResponse(BaseModel):
    """Scale data response."""
    id: int
    name: str
    scale_type: str
    formula: str
    intervals: list[str]
    notes_in_c: Optional[str]
    category: str
    character: Optional[str]
    description: Optional[str]
    difficulty: int
    chord_compatibility: Optional[list[str]] = None


class TechniqueResponse(BaseModel):
    """Technique data response."""
    id: int
    name: str
    category: str
    description: str
    difficulty: int
    instructions: str
    common_errors: Optional[list[str]] = None
    tips: Optional[list[str]] = None
