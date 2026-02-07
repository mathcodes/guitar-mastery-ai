"""
Agent Coordinator — Manages multi-agent interactions, context sharing,
and response aggregation.

Handles three coordination patterns:
1. Sequential Pipeline — agents process in order, passing context forward
2. Parallel Execution — independent requests processed simultaneously
3. Tool-Assisted Single Agent — one agent with database tool access
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional

import structlog

from src.agents.base import BaseAgent, AgentResponse
from src.orchestrator.router import classify_intent, RoutingDecision
from src.orchestrator.context import ConversationContext

logger = structlog.get_logger("orchestrator.coordinator")


@dataclass
class OrchestratorResponse:
    """Final response from the orchestrator to the API layer."""
    content: str
    primary_agent: str
    all_agents_used: list[str]
    session_id: str
    suggestions: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    quiz: dict | None = None
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_latency_ms: int = 0
    routing_decision: dict = field(default_factory=dict)


class AgentCoordinator:
    """
    Central coordinator that routes messages to agents and manages interactions.

    Usage:
        coordinator = AgentCoordinator(agents={...})
        response = await coordinator.process_message(message, context)
    """

    def __init__(
        self,
        agents: dict[str, BaseAgent],
        max_agents_per_request: int = 3,
        timeout_seconds: int = 30,
    ):
        self.agents = agents
        self.max_agents_per_request = max_agents_per_request
        self.timeout_seconds = timeout_seconds

    async def process_message(
        self,
        message: str,
        context: ConversationContext,
    ) -> OrchestratorResponse:
        """
        Main entry point — process a user message through the agent system.

        1. Classify intent
        2. Route to appropriate agent(s)
        3. Execute and aggregate responses
        4. Return unified response
        """
        start_time = time.time()

        # Step 1: Classify intent
        routing = classify_intent(message)
        logger.info(
            "intent_classified",
            agent=routing.agent_name,
            confidence=routing.confidence,
            category=routing.intent_category,
            is_multi=routing.is_multi_agent,
        )

        # Step 2: Execute based on routing decision
        if routing.is_multi_agent and routing.secondary_agents:
            response = await self._execute_multi_agent(message, routing, context)
        else:
            response = await self._execute_single_agent(message, routing, context)

        # Step 3: Record routing info
        response.routing_decision = {
            "agent": routing.agent_name,
            "confidence": routing.confidence,
            "category": routing.intent_category,
            "is_multi": routing.is_multi_agent,
        }
        response.total_latency_ms = int((time.time() - start_time) * 1000)

        return response

    async def _execute_single_agent(
        self,
        message: str,
        routing: RoutingDecision,
        context: ConversationContext,
    ) -> OrchestratorResponse:
        """Route to a single agent and return its response."""
        agent = self.agents.get(routing.agent_name)
        if not agent:
            logger.error("agent_not_found", agent_name=routing.agent_name)
            return OrchestratorResponse(
                content="I'm sorry, I couldn't find the right expert to help with that. Could you rephrase your question?",
                primary_agent="orchestrator",
                all_agents_used=[],
                session_id=context.session_id,
            )

        try:
            result = await asyncio.wait_for(
                agent.think(
                    message=message,
                    context=context.to_dict(),
                    conversation_history=context.get_recent_messages(10),
                ),
                timeout=self.timeout_seconds,
            )

            return OrchestratorResponse(
                content=result.content,
                primary_agent=result.agent_name,
                all_agents_used=[result.agent_name],
                session_id=context.session_id,
                suggestions=result.suggestions,
                data=result.data,
                total_tokens_input=result.tokens_input,
                total_tokens_output=result.tokens_output,
            )

        except asyncio.TimeoutError:
            logger.error("agent_timeout", agent=routing.agent_name)
            return OrchestratorResponse(
                content="The request took too long. Please try a simpler question or try again.",
                primary_agent="orchestrator",
                all_agents_used=[routing.agent_name],
                session_id=context.session_id,
            )

        except Exception as e:
            logger.error("agent_execution_error", agent=routing.agent_name, error=str(e))
            return OrchestratorResponse(
                content="I encountered an error processing your request. Please try again.",
                primary_agent="orchestrator",
                all_agents_used=[routing.agent_name],
                session_id=context.session_id,
            )

    async def _execute_multi_agent(
        self,
        message: str,
        routing: RoutingDecision,
        context: ConversationContext,
    ) -> OrchestratorResponse:
        """
        Execute multiple agents and aggregate their responses.

        Uses parallel execution for independent queries.
        """
        agent_names = [routing.agent_name]
        if routing.secondary_agents:
            agent_names.extend(routing.secondary_agents[:self.max_agents_per_request - 1])

        # Execute all agents in parallel
        tasks = []
        for name in agent_names:
            agent = self.agents.get(name)
            if agent:
                tasks.append(
                    asyncio.wait_for(
                        agent.think(
                            message=message,
                            context=context.to_dict(),
                            conversation_history=context.get_recent_messages(10),
                        ),
                        timeout=self.timeout_seconds,
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        contents = []
        all_suggestions = []
        all_data = {}
        total_tokens_in = 0
        total_tokens_out = 0
        agents_used = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("multi_agent_error", agent=agent_names[i], error=str(result))
                continue

            if isinstance(result, AgentResponse):
                agent_label = self.agents[agent_names[i]].role
                contents.append(f"**{agent_label}:**\n{result.content}")
                all_suggestions.extend(result.suggestions)
                all_data.update(result.data)
                total_tokens_in += result.tokens_input
                total_tokens_out += result.tokens_output
                agents_used.append(result.agent_name)

        combined_content = "\n\n---\n\n".join(contents) if contents else "I couldn't get a response. Please try again."

        return OrchestratorResponse(
            content=combined_content,
            primary_agent=routing.agent_name,
            all_agents_used=agents_used,
            session_id=context.session_id,
            suggestions=all_suggestions[:5],
            data=all_data,
            total_tokens_input=total_tokens_in,
            total_tokens_output=total_tokens_out,
        )
