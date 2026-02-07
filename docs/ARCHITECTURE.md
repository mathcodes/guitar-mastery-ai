# Architecture Document — Guitar Mastery AI

*Living document — updated as the architecture evolves.*

## System Overview

Guitar Mastery AI is a multi-agent application that provides comprehensive guitar education through specialized AI agents. It uses a **Subagent Orchestration Pattern** where a central coordinator routes user queries to domain-expert agents.

## Component Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application              │
│         (src/main.py)                    │
├─────────────────────────────────────────┤
│    API Routes    │    Middleware         │
│  (src/api/)      │  (auth, rate limit)  │
├──────────────────┴──────────────────────┤
│         Orchestrator Layer               │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐  │
│  │ Router  │ │Coordinator│ │ Context │  │
│  └─────────┘ └──────────┘ └─────────┘  │
├─────────────────────────────────────────┤
│         Agent Layer                      │
│  ┌────────┐┌────────┐┌───────┐┌──────┐ │
│  │Luthier ││ Jazz   ││ SQL   ││Dev/PM│ │
│  │Hist.   ││Teacher ││Expert ││      │ │
│  └────────┘└────────┘└───────┘└──────┘ │
├─────────────────────────────────────────┤
│         Tool Layer                       │
│  DB Queries │ Quiz Gen │ Practice Track  │
├─────────────────────────────────────────┤
│         Data Layer                       │
│  SQLite (WAL mode) │ JSON Seed Data     │
└─────────────────────────────────────────┘
```

## Data Flow

1. User sends message via `/api/v1/chat`
2. Router classifies intent using keyword patterns
3. Coordinator routes to appropriate agent(s)
4. Agent processes with LLM + tools
5. Response aggregated and returned

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite over PostgreSQL | Zero-config, portable, sufficient for MVP scale |
| Custom agent framework | Full control, no framework lock-in, simpler debugging |
| HTMX over React/Vue | Server-rendered simplicity, progressive enhancement |
| Keyword routing first | Fast, no API call needed for 80% of queries |
| JSON columns in SQLite | Flexible data without excessive normalization |
