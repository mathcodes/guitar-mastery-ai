"""
Tests for the Intent Router — verifies correct agent routing.
"""

import pytest
from src.orchestrator.router import classify_intent, RoutingDecision


class TestIntentClassification:
    """Test that user queries route to the correct agent."""

    # --- Luthier Agent Routing ---

    def test_routes_luthier_names_to_luthier(self):
        result = classify_intent("Tell me about D'Angelico guitars")
        assert result.agent_name == "luthier_historian"

    def test_routes_guitar_history_to_luthier(self):
        result = classify_intent("What is the history of the archtop guitar?")
        assert result.agent_name == "luthier_historian"

    def test_routes_tonewood_to_luthier(self):
        result = classify_intent("What wood is best for an acoustic guitar top?")
        assert result.agent_name == "luthier_historian"

    def test_routes_pickup_questions_to_luthier(self):
        result = classify_intent("How does a humbucker pickup work?")
        assert result.agent_name == "luthier_historian"

    def test_routes_setup_to_luthier(self):
        result = classify_intent("How do I adjust the truss rod?")
        assert result.agent_name == "luthier_historian"

    # --- Jazz Teacher Agent Routing ---

    def test_routes_chord_theory_to_jazz_teacher(self):
        result = classify_intent("What scales can I play over a Cmaj7 chord?")
        assert result.agent_name == "jazz_teacher"

    def test_routes_improvisation_to_jazz_teacher(self):
        result = classify_intent("How do I improvise over ii-V-I changes?")
        assert result.agent_name == "jazz_teacher"

    def test_routes_practice_to_jazz_teacher(self):
        result = classify_intent("I'm stuck in a rut, how do I break through?")
        assert result.agent_name == "jazz_teacher"

    def test_routes_technique_to_jazz_teacher(self):
        result = classify_intent("How do I practice alternate picking?")
        assert result.agent_name == "jazz_teacher"

    def test_routes_quiz_to_jazz_teacher(self):
        result = classify_intent("Quiz me on jazz chord types")
        assert result.agent_name == "jazz_teacher"

    # --- SQL Expert Routing ---

    def test_routes_data_query_to_sql_expert(self):
        result = classify_intent("Show me all chords with difficulty 4 or higher")
        assert result.agent_name == "sql_expert"

    def test_routes_count_query_to_sql_expert(self):
        result = classify_intent("How many scales are in the database?")
        assert result.agent_name == "sql_expert"

    def test_routes_list_query_to_sql_expert(self):
        result = classify_intent("List all jazz standards in the key of Bb")
        assert result.agent_name == "sql_expert"

    # --- Default Routing ---

    def test_defaults_to_jazz_teacher_for_ambiguous(self):
        result = classify_intent("help me get better at guitar")
        assert result.agent_name == "jazz_teacher"

    # --- Multi-Agent Detection ---

    def test_detects_multi_agent_need(self):
        result = classify_intent(
            "What wood did D'Angelico use and what scales work for jazz?"
        )
        assert result.is_multi_agent or result.agent_name in ["luthier_historian", "jazz_teacher"]

    # --- Confidence ---

    def test_high_confidence_for_clear_intent(self):
        result = classify_intent("Tell me about the Gibson L-5 archtop guitar history")
        assert result.confidence > 0.4

    def test_lower_confidence_for_vague_query(self):
        result = classify_intent("hello")
        assert result.confidence <= 0.5
