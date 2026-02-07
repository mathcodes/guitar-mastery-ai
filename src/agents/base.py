"""
Base Agent — Abstract foundation for all specialized agents.

All agents in the Guitar Mastery app inherit from BaseAgent, which provides:
- LLM interaction via Anthropic Claude SDK
- Tool registration and execution
- Structured logging
- Confidence scoring
- Error handling and graceful degradation
"""

import time
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Optional
from pathlib import Path

import structlog
from anthropic import AsyncAnthropic

logger = structlog.get_logger("agents")


# ============================================================
# Data Classes
# ============================================================

@dataclass
class Tool:
    """Represents a callable tool available to an agent."""
    name: str
    description: str
    parameters: dict  # JSON Schema for parameters
    handler: Callable[..., Awaitable[Any]]

    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool-use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class AgentResponse:
    """Structured response from an agent."""
    content: str
    agent_name: str
    confidence: float = 1.0            # 0.0 to 1.0
    tools_used: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)  # Structured data (query results, etc.)
    suggestions: list[str] = field(default_factory=list)
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    error: str | None = None


@dataclass
class AgentMessage:
    """Message passed between agents via the orchestrator."""
    sender: str
    recipient: str
    intent: str
    content: str
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    requires_response: bool = True


# ============================================================
# Base Agent Class
# ============================================================

class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.

    Subclasses must implement:
    - _register_tools(): Define agent-specific tools
    - Optionally override _build_context() for custom context injection
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.5,
        max_tokens: int = 2000,
        knowledge_base_path: str | None = None,
        client: AsyncAnthropic | None = None,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.knowledge_base_path = knowledge_base_path
        self.client = client or AsyncAnthropic()
        self.tools: dict[str, Tool] = {}
        self._knowledge_base: str | None = None

        # Register agent-specific tools
        self._register_tools()

        # Load knowledge base if provided
        if knowledge_base_path:
            self._load_knowledge_base(knowledge_base_path)

    @abstractmethod
    def _register_tools(self) -> None:
        """Register tools specific to this agent. Must be implemented by subclasses."""
        pass

    def register_tool(self, tool: Tool) -> None:
        """Register a tool for this agent."""
        self.tools[tool.name] = tool
        logger.info("tool_registered", agent=self.name, tool=tool.name)

    def _load_knowledge_base(self, path: str) -> None:
        """Load training/reference data from a markdown file."""
        try:
            kb_path = Path(path)
            if kb_path.exists():
                self._knowledge_base = kb_path.read_text(encoding="utf-8")
                logger.info("knowledge_base_loaded", agent=self.name, path=path,
                            size=len(self._knowledge_base))
            else:
                logger.warning("knowledge_base_not_found", agent=self.name, path=path)
        except Exception as e:
            logger.error("knowledge_base_load_error", agent=self.name, error=str(e))

    def _build_system_message(self, context: dict | None = None) -> str:
        """Build the full system message including knowledge base and context."""
        parts = [self.system_prompt]

        if self._knowledge_base:
            parts.append(f"\n\n## Reference Knowledge Base\n{self._knowledge_base}")

        if context:
            user_level = context.get("user_skill_level", "intermediate")
            parts.append(f"\n\n## Current Context\n- User skill level: {user_level}")
            if context.get("current_topic"):
                parts.append(f"- Current topic: {context['current_topic']}")

        return "\n".join(parts)

    async def think(
        self,
        message: str,
        context: dict | None = None,
        conversation_history: list[dict] | None = None,
    ) -> AgentResponse:
        """
        Process a user message and generate a response.

        This is the main entry point for agent interaction. It:
        1. Builds the system message with context
        2. Sends to Claude with tool definitions
        3. Handles any tool_use blocks
        4. Returns a structured AgentResponse
        """
        start_time = time.time()

        try:
            # Build the messages list (Anthropic format: no system role in messages)
            messages = []

            # Add conversation history (last N messages)
            if conversation_history:
                for msg in conversation_history[-10:]:
                    # Anthropic only allows "user" and "assistant" roles in messages
                    if msg.get("role") in ("user", "assistant"):
                        messages.append(msg)

            messages.append({"role": "user", "content": message})

            # Prepare tool definitions
            tools = [tool.to_anthropic_tool() for tool in self.tools.values()] if self.tools else None

            # Build API call kwargs
            api_kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": self._build_system_message(context),
                "messages": messages,
            }
            if tools:
                api_kwargs["tools"] = tools

            # Iterative tool-use loop (up to MAX_TOOL_ROUNDS)
            MAX_TOOL_ROUNDS = 5
            tools_used = []
            tool_data = {}
            tokens_in = 0
            tokens_out = 0

            response = await self.client.messages.create(**api_kwargs)
            tokens_in += response.usage.input_tokens
            tokens_out += response.usage.output_tokens

            for _round in range(MAX_TOOL_ROUNDS):
                text_content = ""
                has_tool_use = False

                for block in response.content:
                    if block.type == "text":
                        text_content += block.text
                    elif block.type == "tool_use":
                        has_tool_use = True
                        result = await self.use_tool(block.name, **block.input)
                        tools_used.append(block.name)
                        tool_data[block.name] = result

                # If Claude didn't ask for tools, we're done
                if response.stop_reason != "tool_use" or not has_tool_use:
                    break

                # Build tool results and continue the conversation
                tool_result_content = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_result_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_data.get(block.name, {}), default=str),
                        })

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_result_content})

                next_kwargs = {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "system": self._build_system_message(context),
                    "messages": messages,
                }
                if tools:
                    next_kwargs["tools"] = tools

                response = await self.client.messages.create(**next_kwargs)
                tokens_in += response.usage.input_tokens
                tokens_out += response.usage.output_tokens

            # Extract final text from the last response
            text_content = ""
            for block in response.content:
                if block.type == "text":
                    text_content += block.text

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "agent_response",
                agent=self.name,
                model=self.model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=latency_ms,
                tools_used=tools_used,
            )

            return AgentResponse(
                content=text_content,
                agent_name=self.name,
                confidence=self._estimate_confidence(text_content, tools_used),
                tools_used=tools_used,
                data=tool_data,
                suggestions=self._generate_suggestions(text_content, context),
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("agent_error", agent=self.name, error=str(e))

            return AgentResponse(
                content=f"I encountered an issue processing your request. "
                        f"Please try rephrasing or ask a different question.",
                agent_name=self.name,
                confidence=0.0,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool by name."""
        if tool_name not in self.tools:
            logger.warning("tool_not_found", agent=self.name, tool=tool_name)
            return {"error": f"Tool '{tool_name}' not available"}

        try:
            result = await self.tools[tool_name].handler(**kwargs)
            logger.info("tool_executed", agent=self.name, tool=tool_name)
            return result
        except Exception as e:
            logger.error("tool_error", agent=self.name, tool=tool_name, error=str(e))
            return {"error": str(e)}

    def _estimate_confidence(self, content: str, tools_used: list[str]) -> float:
        """
        Estimate confidence in the response.

        Heuristic-based: higher confidence when tools were used (data-backed),
        lower when the response contains hedging language.
        """
        confidence = 0.8  # Base confidence

        # Higher confidence if tools were used (data-driven response)
        if tools_used:
            confidence += 0.1

        # Lower confidence for hedging language
        hedging_phrases = [
            "i'm not sure", "i think", "might be", "possibly",
            "i don't know", "not certain", "may not be accurate",
        ]
        content_lower = content.lower()
        for phrase in hedging_phrases:
            if phrase in content_lower:
                confidence -= 0.15
                break

        return max(0.1, min(1.0, confidence))

    def _generate_suggestions(
        self, content: str, context: dict | None = None
    ) -> list[str]:
        """Generate follow-up suggestions based on the response. Override in subclasses."""
        return []

    async def reflect(self, response: AgentResponse) -> AgentResponse:
        """
        Self-check mechanism — review own response for quality.
        Override in subclasses for domain-specific reflection.
        """
        return response

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} model={self.model}>"
