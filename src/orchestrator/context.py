"""
Conversation Context — Manages shared state across agent interactions.

Tracks session data, conversation history, user preferences,
and active interactive features (quizzes, lessons).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ConversationContext:
    """Shared context that travels with every request through the agent system."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    user_skill_level: str = "intermediate"
    conversation_history: list[dict] = field(default_factory=list)
    current_topic: str | None = None
    active_lesson: dict | None = None
    active_quiz: dict | None = None
    agent_routing_history: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: str, content: str, agent: str | None = None) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_recent_messages(self, n: int = 10) -> list[dict]:
        """Get the last N messages in Anthropic message format."""
        recent = self.conversation_history[-n:]
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent
        ]

    def record_agent_used(self, agent_name: str) -> None:
        """Track which agents have been used in this session."""
        self.agent_routing_history.append(agent_name)

    def to_dict(self) -> dict:
        """Convert to dictionary for passing to agents."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "user_skill_level": self.user_skill_level,
            "current_topic": self.current_topic,
            "active_lesson": self.active_lesson,
            "active_quiz": self.active_quiz,
            "agent_history": self.agent_routing_history[-5:],
            "message_count": len(self.conversation_history),
        }

    def start_quiz(self, quiz_data: dict) -> None:
        """Set the active quiz state."""
        self.active_quiz = quiz_data

    def end_quiz(self) -> dict | None:
        """Clear and return the active quiz state."""
        quiz = self.active_quiz
        self.active_quiz = None
        return quiz

    def start_lesson(self, lesson_data: dict) -> None:
        """Set the active lesson state."""
        self.active_lesson = lesson_data

    def end_lesson(self) -> dict | None:
        """Clear and return the active lesson state."""
        lesson = self.active_lesson
        self.active_lesson = None
        return lesson
