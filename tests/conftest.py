"""
Shared Test Fixtures — Guitar Mastery AI

Provides:
- In-memory SQLite database sessions
- Mock Anthropic Claude client for agent testing
- FastAPI test client for integration testing
- Pre-seeded database for data-dependent tests
"""

import json
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from httpx import AsyncClient, ASGITransport

from src.db.models import Base


# ============================================================
# Database Fixtures
# ============================================================

@pytest_asyncio.fixture
async def db_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide a clean database session for each test."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


# ============================================================
# Mock Anthropic Claude Fixtures
# ============================================================

class MockTextBlock:
    """Mock Anthropic text content block."""
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class MockUsage:
    """Mock Anthropic usage data."""
    def __init__(self, input_tokens: int = 100, output_tokens: int = 50):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class MockAnthropicResponse:
    """Mock Anthropic messages.create() response."""
    def __init__(self, content: str, stop_reason: str = "end_turn"):
        self.content = [MockTextBlock(content)]
        self.stop_reason = stop_reason
        self.usage = MockUsage()


class MockAnthropicClient:
    """
    Mock Anthropic client that returns deterministic responses based on input patterns.

    Mimics the AsyncAnthropic interface: client.messages.create()

    Usage:
        mock = MockAnthropicClient(responses={
            r".*chord.*": "That's a chord question!",
            r".*scale.*": "That's a scale question!",
        })
    """
    def __init__(self, responses: dict[str, str] = None):
        self.responses = responses or {}
        self.call_history: list[dict] = []

    class _Messages:
        def __init__(self, parent):
            self.parent = parent

        async def create(self, **kwargs):
            messages = kwargs.get("messages", [])
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    content = msg["content"]
                    # Handle string content and list content (tool_result blocks)
                    if isinstance(content, str):
                        user_message = content
                        break

            self.parent.call_history.append({
                "messages": messages,
                "model": kwargs.get("model"),
                "temperature": kwargs.get("temperature"),
                "system": kwargs.get("system", ""),
            })

            # Match against patterns
            for pattern, response in self.parent.responses.items():
                if re.search(pattern, user_message, re.IGNORECASE):
                    return MockAnthropicResponse(content=response)

            return MockAnthropicResponse(content="I can help with that guitar question!")

    @property
    def messages(self):
        return self._Messages(self)


@pytest.fixture
def mock_llm():
    """Provide a mock Anthropic client with guitar-domain responses."""
    return MockAnthropicClient(responses={
        r".*chord.*interval.*1 3 5 b7.*": "That's a dominant 7th chord (1 3 5 b7).",
        r".*scale.*dorian.*": "The Dorian mode has the formula: 1 2 b3 4 5 6 b7",
        r".*history.*les paul.*": "The Gibson Les Paul was introduced in 1952.",
        r".*ii-v-i.*": "The ii-V-I is the most common progression in jazz.",
        r".*practice.*rut.*": "Here are strategies to break out of a playing rut.",
        r".*chord.*": "Here's information about that chord type.",
        r".*scale.*": "Here's information about that scale.",
    })


# ============================================================
# API Client Fixtures
# ============================================================

@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP client for API testing."""
    from src.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================================
# Seed Data Fixtures
# ============================================================

@pytest.fixture
def seed_data_path():
    """Path to seed data directory."""
    return Path(__file__).parent.parent / "data" / "seed"


@pytest.fixture
def sample_chord_data():
    """Sample chord data for testing."""
    return {
        "name": "Test Maj7",
        "root": "C",
        "chord_type": "maj7",
        "formula": "1 3 5 7",
        "intervals": ["1", "3", "5", "7"],
        "notes_in_c": "C E G B",
        "category": "jazz",
        "difficulty": 2,
    }
