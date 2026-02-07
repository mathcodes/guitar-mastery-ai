# Architecture Decision Records (ADRs)

## ADR-001: SQLite as Primary Database

**Date:** 2026-02-07
**Status:** Accepted

### Context
The application needs a database for storing guitar knowledge, user data, and system state. Options considered: PostgreSQL, SQLite, MongoDB.

### Decision
Use SQLite with WAL mode as the primary database for MVP and growth phases.

### Consequences
**Positive:**
- Zero configuration — no separate database server needed
- Portable — entire database is a single file
- Fast for read-heavy workloads (which this app is)
- WAL mode supports concurrent reads
- JSON functions available for flexible data

**Negative:**
- Single-writer limitation (one write at a time)
- No built-in replication
- Will need migration to PostgreSQL at scale (100+ concurrent users)

### Migration Path
The application uses SQLAlchemy as an abstraction layer, making the PostgreSQL migration straightforward when needed.

---

## ADR-002: Custom Agent Framework (No LangChain/CrewAI)

**Date:** 2026-02-07
**Status:** Accepted

### Context
Multiple agent frameworks exist (LangChain, CrewAI, AutoGen, Google ADK). We need to decide whether to use one or build custom.

### Decision
Build a lightweight custom agent framework using a BaseAgent abstract class.

### Consequences
**Positive:**
- Full control over agent behavior and debugging
- No framework lock-in or dependency churn
- Simpler mental model — agents are just classes with tools
- Easier to customize for domain-specific needs
- No unnecessary abstraction layers

**Negative:**
- More initial code to write
- Must implement own tool registration, logging, coordination
- No community plugins or pre-built integrations

### Rationale
Industry best practice (2025-2026) recommends "tool-first design" and KISS principle. External frameworks add complexity and abstraction that hinder debugging. Our agent needs are well-defined enough that a custom solution is cleaner.

---

## ADR-003: HTMX for Frontend Instead of React/Vue

**Date:** 2026-02-07
**Status:** Accepted

### Context
The frontend needs to support: chat interface, quizzes, lessons, practice tracking.

### Decision
Use server-rendered HTML with Jinja2 templates and HTMX for dynamic interactions.

### Consequences
**Positive:**
- No JavaScript build step
- Server-side rendering is simpler to reason about
- HTMX provides SPA-like experience with minimal JS
- Same Python codebase for frontend and backend
- Progressive enhancement — works without JS enabled

**Negative:**
- Less suitable for highly interactive real-time UIs
- HTMX has a learning curve for developers from React/Vue background
- Limited client-side state management

---

## ADR-004: Keyword-First Intent Classification

**Date:** 2026-02-07
**Status:** Accepted

### Context
The orchestrator needs to classify user intent to route to the correct agent. Options: pure LLM classification, keyword matching, hybrid.

### Decision
Use keyword/pattern matching as the primary classifier with LLM fallback for ambiguous cases.

### Consequences
**Positive:**
- ~0ms latency for 80% of queries (no API call needed)
- Deterministic and debuggable
- No token cost for classification
- Easy to add new patterns

**Negative:**
- Can misclassify ambiguous queries
- Requires manual pattern maintenance
- Doesn't understand semantic nuance

### Fallback
When confidence < 0.4, the system falls back to an LLM classification call using the cheaper gpt-4o-mini model.
