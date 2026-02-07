"""
Intent Router — Classifies user intent and routes to the appropriate agent.

Uses a combination of keyword matching (fast) and LLM classification (accurate)
to determine which agent should handle a request.
"""

import re
from dataclasses import dataclass
from typing import Optional

import structlog

logger = structlog.get_logger("orchestrator.router")


@dataclass
class RoutingDecision:
    """Result of intent classification."""
    agent_name: str
    confidence: float
    intent_category: str
    reasoning: str
    is_multi_agent: bool = False
    secondary_agents: list[str] | None = None


# Known entity names that should trigger specific agents
LUTHIER_ENTITIES = {
    "torres", "martin", "gibson", "fender", "d'angelico", "d'aquisto",
    "benedetto", "prs", "paul reed smith", "rickenbacker", "gretsch",
    "epiphone", "ibanez", "yamaha", "taylor", "collings", "santa cruz",
    "bourgeois", "huss and dalton", "lowden", "mcpherson", "lloyd loar",
    "leo fender", "les paul", "orville gibson", "ted mccarty", "seth lover",
    "telecaster", "stratocaster", "les paul", "sg", "es-335", "l-5",
    "dreadnought", "parlor guitar", "archtop",
}

JAZZ_THEORY_PATTERNS = [
    r"\b(chord|scale|mode|arpeggio|interval|key)\b",
    r"\b(dorian|mixolydian|lydian|phrygian|locrian|ionian|aeolian)\b",
    r"\b(bebop|altered|diminished|whole\s*tone|pentatonic|chromatic)\b",
    r"\b(ii-v-i|ii\s*v\s*i|2-5-1|two\s*five\s*one)\b",
    r"\b(improvise|improvisation|solo|comping|voicing)\b",
    r"\b(practice|routine|exercise|lesson|warmup|warm-up)\b",
    r"\b(rut|plateau|stuck|bored|stale|uninspired)\b",
    r"\b(jazz|swing|bebop|bossa|ballad|blues)\b",
    r"\b(wes montgomery|joe pass|pat metheny|jim hall|grant green)\b",
    r"\b(charlie parker|miles davis|john coltrane|bill evans)\b",
    r"\b(quiz|test|question)\b",
    r"\b(voice\s*lead|guide\s*tone|enclosure|targeting)\b",
]

DATA_QUERY_PATTERNS = [
    r"\b(how many|list all|show me|find all|search for|count)\b",
    r"\b(which ones|what are all|give me all|display)\b",
    r"\b(database|query|data|records|entries)\b",
    r"\b(filter|sort|between|greater than|less than)\b",
    r"\b(difficulty \d|category|type)\b",
]

HISTORY_PATTERNS = [
    r"\b(history|historical|evolution|origin|invented|created)\b",
    r"\b(luthier|builder|craftsman|workshop|shop)\b",
    r"\b(tonewood|wood|spruce|mahogany|rosewood|maple|ebony)\b",
    r"\b(pickup|humbucker|single.coil|p-90|piezo|active)\b",
    r"\b(construction|bracing|neck\s*joint|frets|nut|saddle)\b",
    r"\b(setup|intonation|action|truss\s*rod|string\s*gauge)\b",
    r"\b(repair|restore|maintenance|restring|adjust)\b",
]

SYSTEM_PATTERNS = [
    r"\b(benchmark|progress|status|health|error|bug)\b",
    r"\b(documentation|changelog|log|report)\b",
    r"\b(test|deploy|build|version)\b",
]


def classify_intent(user_message: str) -> RoutingDecision:
    """
    Classify user intent using keyword/pattern matching.

    For production, this would be augmented with an LLM classifier
    for ambiguous cases. The keyword approach handles ~80% of queries
    efficiently without an API call.
    """
    message_lower = user_message.lower().strip()

    scores = {
        "luthier_historian": 0.0,
        "jazz_teacher": 0.0,
        "sql_expert": 0.0,
        "dev_pm": 0.0,
    }

    # Check for known luthier/brand entities (high priority)
    for entity in LUTHIER_ENTITIES:
        if entity in message_lower:
            scores["luthier_historian"] += 3.0
            break

    # Pattern matching scores
    for pattern in HISTORY_PATTERNS:
        if re.search(pattern, message_lower):
            scores["luthier_historian"] += 1.0

    for pattern in JAZZ_THEORY_PATTERNS:
        if re.search(pattern, message_lower):
            scores["jazz_teacher"] += 1.0

    for pattern in DATA_QUERY_PATTERNS:
        if re.search(pattern, message_lower):
            scores["sql_expert"] += 1.5

    for pattern in SYSTEM_PATTERNS:
        if re.search(pattern, message_lower):
            scores["dev_pm"] += 1.0

    # Determine winner
    max_score = max(scores.values())
    if max_score == 0:
        # Default to jazz teacher for unclassified music questions
        return RoutingDecision(
            agent_name="jazz_teacher",
            confidence=0.5,
            intent_category="general",
            reasoning="No strong pattern match; defaulting to jazz teacher as the most general music agent.",
        )

    winner = max(scores, key=scores.get)
    confidence = min(1.0, max_score / 5.0)

    # Check for multi-agent need
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    is_multi = (
        len(sorted_scores) > 1
        and sorted_scores[1][1] > 0
        and sorted_scores[1][1] >= sorted_scores[0][1] * 0.6
    )

    secondary = None
    if is_multi:
        secondary = [s[0] for s in sorted_scores[1:] if s[1] > 0]

    # Determine intent category
    intent_map = {
        "luthier_historian": "guitar_history" if any(
            re.search(p, message_lower) for p in HISTORY_PATTERNS[:2]
        ) else "guitar_setup",
        "jazz_teacher": "music_theory",
        "sql_expert": "data_query",
        "dev_pm": "system",
    }

    return RoutingDecision(
        agent_name=winner,
        confidence=confidence,
        intent_category=intent_map.get(winner, "general"),
        reasoning=f"Pattern scores: {scores}",
        is_multi_agent=is_multi,
        secondary_agents=secondary,
    )


def needs_llm_classification(decision: RoutingDecision) -> bool:
    """Determine if the routing decision is ambiguous enough to need LLM help."""
    return decision.confidence < 0.4 or decision.is_multi_agent
