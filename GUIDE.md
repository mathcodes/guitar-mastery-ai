# Comprehensive Guide: Building an Agentic AI Guitar Mastery App in Cursor

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure & Setup](#2-project-structure--setup)
3. [Database Design & SQLite Integration](#3-database-design--sqlite-integration)
4. [Agent Design & Specialization](#4-agent-design--specialization)
5. [Agent Training & Knowledge Bases](#5-agent-training--knowledge-bases)
6. [Orchestration Layer](#6-orchestration-layer)
7. [API Layer (FastAPI)](#7-api-layer-fastapi)
8. [Frontend (Interactive Lessons & Quizzes)](#8-frontend-interactive-lessons--quizzes)
9. [Cursor Rules & Agentic Development](#9-cursor-rules--agentic-development)
10. [Scalability Patterns](#10-scalability-patterns)
11. [Customizability & Extension](#11-customizability--extension)
12. [Testing Strategy](#12-testing-strategy)
13. [Development Lifecycle & Documentation](#13-development-lifecycle--documentation)
14. [Deployment & Operations](#14-deployment--operations)
15. [Troubleshooting & Debugging Playbook](#15-troubleshooting--debugging-playbook)

---

## 1. Architecture Overview

### 1.1 System Philosophy

This application follows a **Subagent Orchestration Pattern** — a central orchestrator (the Full Stack Developer / Project Manager agent) coordinates specialized domain agents. Each agent has a single responsibility, its own context window, and access to specific tools.

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                         │
│            (Web App / CLI / API Client)                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR / ROUTER                        │
│         (Full Stack Dev / Project Manager)                │
│                                                           │
│  • Intent Classification                                  │
│  • Agent Routing                                          │
│  • Response Aggregation                                   │
│  • Progress Documentation                                 │
│  • Error Handling & Recovery                              │
└────┬──────────┬──────────┬──────────┬───────────────────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│ LUTHIER ││  JAZZ   ││  SQL    ││ DEV/PM  │
│ & HIST  ││ TEACHER ││ EXPERT  ││  AGENT  │
│ AGENT   ││ AGENT   ││ AGENT   ││         │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────┐
│                   TOOL LAYER                              │
│                                                           │
│  SQLite DB │ Knowledge Base │ Quiz Engine │ Logger        │
│  Vector Store │ Practice Tracker │ Doc Generator          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Core Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each agent owns one domain; tools are atomic functions |
| **Tool-First Design** | Agents access capabilities through well-defined tool interfaces |
| **Externalized Prompts** | System prompts stored in versioned files, not hardcoded |
| **Pure-Function Tools** | Database queries, quiz generation, etc. are deterministic where possible |
| **KISS** | Start with the simplest working version, then layer complexity |
| **Observable** | Every agent action is logged with timestamps, inputs, and outputs |

### 1.3 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Language** | Python 3.11+ | Mature AI/ML ecosystem, async support |
| **API Framework** | FastAPI | Async-first, auto-docs, type safety |
| **Database** | SQLite + sqlite-vec | Zero-config, portable, vector search capable |
| **ORM** | SQLAlchemy 2.0 | Async support, migration-friendly |
| **Migrations** | Alembic | Version-controlled schema changes |
| **LLM Interface** | LiteLLM / OpenAI SDK | Provider-agnostic, swap models freely |
| **Agent Framework** | Custom (lightweight) | Full control, no framework lock-in |
| **Frontend** | HTML/CSS/JS + HTMX | Progressive enhancement, minimal JS |
| **Testing** | pytest + pytest-asyncio | Industry standard, async test support |
| **Containerization** | Docker + Compose | Dev/prod parity |

---

## 2. Project Structure & Setup

### 2.1 Directory Layout

```
today_agent/
├── .cursor/
│   └── rules/                    # Cursor AI rules for agentic development
│       ├── project-wide.mdc      # Global project conventions
│       ├── agents.mdc            # Agent development patterns
│       ├── database.mdc          # Database conventions
│       └── testing.mdc           # Testing standards
├── config/
│   ├── agents.yaml               # Agent configurations (prompts, tools, models)
│   ├── settings.py               # App settings (env-driven)
│   └── logging.yaml              # Structured logging config
├── data/
│   ├── seed/                     # Initial database seed data
│   │   ├── chords.json
│   │   ├── scales.json
│   │   ├── arpeggios.json
│   │   ├── guitar_history.json
│   │   ├── techniques.json
│   │   ├── jazz_standards.json
│   │   ├── practice_routines.json
│   │   └── quizzes.json
│   └── training/                 # Agent training/reference data
│       ├── luthier_knowledge.md
│       ├── jazz_teacher_knowledge.md
│       ├── sql_patterns.md
│       └── dev_pm_playbook.md
├── docs/
│   ├── GUIDE.md                  # This guide (symlinked from root)
│   ├── ARCHITECTURE.md           # Living architecture document
│   ├── CHANGELOG.md              # Auto-generated from benchmarks
│   ├── DECISIONS.md              # Architecture Decision Records
│   ├── BENCHMARKS.md             # Progress benchmarks
│   └── DEBUGGING.md              # Failures + solutions reference
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base agent class
│   │   ├── luthier.py            # Guitar Luthier & Historian agent
│   │   ├── jazz_teacher.py       # Jazz Guitar Teacher agent
│   │   ├── sql_expert.py         # SQL Expert with NL-to-SQL
│   │   └── dev_pm.py             # Full Stack Dev / Project Manager
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── router.py             # Intent classification & routing
│   │   ├── coordinator.py        # Multi-agent coordination
│   │   └── context.py            # Shared context management
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   ├── connection.py         # Database connection management
│   │   ├── queries.py            # Pre-built query library
│   │   └── migrations/           # Alembic migrations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py           # Chat/conversation endpoints
│   │   │   ├── lessons.py        # Interactive lesson endpoints
│   │   │   ├── quizzes.py        # Quiz endpoints
│   │   │   ├── practice.py       # Practice tracking endpoints
│   │   │   └── admin.py          # Admin/debug endpoints
│   │   ├── middleware.py         # Auth, rate limiting, logging
│   │   └── schemas.py           # Pydantic request/response models
│   ├── frontend/
│   │   ├── templates/            # Jinja2 HTML templates
│   │   │   ├── base.html
│   │   │   ├── chat.html
│   │   │   ├── lesson.html
│   │   │   ├── quiz.html
│   │   │   └── dashboard.html
│   │   └── static/
│   │       ├── css/
│   │       ├── js/
│   │       └── img/
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Structured logging
│       ├── benchmarks.py         # Benchmark tracking
│       └── doc_generator.py      # Auto-documentation
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── test_agents/
│   ├── test_db/
│   ├── test_api/
│   └── test_orchestrator/
├── .env.example                  # Environment variable template
├── .gitignore
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml
├── Dockerfile
├── GUIDE.md                      # This file
├── pyproject.toml                # Project metadata & dependencies
├── README.md                     # Quick start
└── requirements.txt              # Pinned dependencies
```

### 2.2 Initial Setup Commands

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env
# Edit .env with your API keys

# 4. Initialize the database
python -m src.db.connection --init

# 5. Seed the database
python -m src.db.seed

# 6. Run the application
uvicorn src.main:app --reload --port 8000
```

### 2.3 Dependencies

See `requirements.txt` for the full pinned dependency list. Key packages:

- `fastapi[standard]` — Web framework + Uvicorn
- `sqlalchemy[asyncio]` — Async ORM
- `aiosqlite` — Async SQLite driver
- `alembic` — Database migrations
- `openai` — LLM API client
- `litellm` — Multi-provider LLM abstraction
- `pydantic` — Data validation
- `jinja2` — HTML templating
- `python-dotenv` — Environment management
- `pyyaml` — YAML config parsing
- `structlog` — Structured logging
- `pytest` / `pytest-asyncio` — Testing

---

## 3. Database Design & SQLite Integration

### 3.1 Schema Philosophy

The database serves three purposes:
1. **Knowledge Store** — Guitar theory, history, techniques, and jazz content
2. **User State** — Practice progress, quiz scores, conversation history
3. **System State** — Agent logs, benchmarks, error tracking

### 3.2 Entity-Relationship Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    chords    │     │    scales    │     │  arpeggios   │
│──────────────│     │──────────────│     │──────────────│
│ id           │     │ id           │     │ id           │
│ name         │     │ name         │     │ name         │
│ formula      │     │ formula      │     │ formula      │
│ intervals    │     │ intervals    │     │ intervals    │
│ category     │     │ category     │     │ category     │
│ voicings JSON│     │ positions JSON│    │ positions JSON│
│ audio_ref    │     │ audio_ref    │     │ audio_ref    │
│ difficulty   │     │ difficulty   │     │ difficulty   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                     │
       └────────────┬───────┴─────────────────────┘
                    │
              ┌─────┴──────┐
              │ theory_links│  (many-to-many relationships)
              └─────┬──────┘
                    │
       ┌────────────┼────────────────┐
       ▼            ▼                ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│  techniques  ││jazz_standards││guitar_history│
│──────────────││──────────────││──────────────│
│ id           ││ id           ││ id           │
│ name         ││ title        ││ title        │
│ category     ││ composer     ││ era          │
│ description  ││ key          ││ category     │
│ difficulty   ││ tempo        ││ content      │
│ instructions ││ changes JSON ││ figures JSON │
│ common_errors││ analysis     ││ instruments  │
│ tips         ││ difficulty   ││ significance │
└──────────────┘└──────────────┘└──────────────┘

┌──────────────┐┌──────────────┐┌──────────────┐
│    users     ││   sessions   ││practice_logs │
│──────────────││──────────────││──────────────│
│ id           ││ id           ││ id           │
│ username     ││ user_id (FK) ││ user_id (FK) │
│ skill_level  ││ started_at   ││ session_id   │
│ preferences  ││ agent_used   ││ topic        │
│ created_at   ││ messages JSON││ duration_min │
│ goals JSON   ││ context JSON ││ notes        │
└──────────────┘└──────────────┘│ score        │
                                │ created_at   │
┌──────────────┐┌──────────────┐└──────────────┘
│   quizzes    ││quiz_attempts │
│──────────────││──────────────│┌──────────────┐
│ id           ││ id           ││  agent_logs  │
│ title        ││ quiz_id (FK) ││──────────────│
│ topic        ││ user_id (FK) ││ id           │
│ difficulty   ││ answers JSON ││ agent_name   │
│ questions JSON│ score        ││ action       │
│ created_by   ││ feedback     ││ input        │
└──────────────┘│ taken_at     ││ output       │
                └──────────────┘│ tokens_used  │
                                │ latency_ms   │
┌──────────────┐                │ success      │
│  benchmarks  │                │ error        │
│──────────────│                │ timestamp    │
│ id           │                └──────────────┘
│ phase        │
│ description  │
│ status       │
│ started_at   │
│ completed_at │
│ failures JSON│
│ solutions JSON│
│ notes        │
└──────────────┘
```

### 3.3 Key Design Decisions

1. **JSON columns for flexible data**: Chord voicings, scale positions, and quiz questions use JSON columns. SQLite handles JSON natively with `json_extract()`.

2. **Denormalized for read speed**: Guitar knowledge is read-heavy. We denormalize where it reduces JOIN complexity.

3. **Soft deletes**: All tables include `is_active` flags rather than hard deletes.

4. **Timestamps everywhere**: `created_at` and `updated_at` on every table for auditability.

5. **Vector extension ready**: Schema accommodates `sqlite-vec` for semantic similarity search on descriptions and content.

### 3.4 Natural Language to SQL Pipeline

The SQL Expert agent translates user questions to SQL queries:

```
User: "What jazz chords use the b9 interval?"
         │
         ▼
┌─────────────────────┐
│  Intent Detection    │  → Identifies: database query needed
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Schema Context      │  → Injects relevant table schemas
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  NL → SQL Generation │  → SELECT * FROM chords WHERE
│                      │    json_extract(intervals, '$') LIKE '%b9%'
│                      │    AND category = 'jazz'
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  SQL Validation      │  → Syntax check, injection prevention
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Query Execution     │  → Run against SQLite, return results
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Result Formatting   │  → Natural language response with data
└─────────────────────┘
```

**Security**: All generated SQL is validated against an allowlist of operations (SELECT only for user queries). Parameterized queries prevent injection. A query sandbox limits execution time and result size.

---

## 4. Agent Design & Specialization

### 4.1 Base Agent Architecture

Every agent inherits from a common base class that provides:

```python
class BaseAgent:
    """Abstract base for all specialized agents."""

    name: str                    # Unique identifier
    role: str                    # Human-readable role description
    system_prompt: str           # Loaded from external file
    model: str                   # LLM model identifier
    temperature: float           # Response creativity control
    tools: list[Tool]            # Available tool functions
    max_tokens: int              # Response length limit
    knowledge_base: str | None   # Path to training data

    async def think(self, message, context) -> AgentResponse
    async def use_tool(self, tool_name, **kwargs) -> ToolResult
    async def reflect(self, response) -> AgentResponse  # Self-check
```

### 4.2 Agent Specifications

#### Agent 1: Guitar Luthier & Historian

| Property | Value |
|----------|-------|
| **Name** | `luthier_historian` |
| **Role** | Expert in guitar construction, wood science, instrument history, and the evolution of guitar design |
| **Model** | `gpt-4o` (or equivalent) |
| **Temperature** | 0.3 (factual, precise) |
| **Tools** | `query_guitar_history`, `query_instruments`, `query_luthiers`, `query_wood_types`, `search_knowledge_base` |

**Domain Coverage:**
- Guitar construction (acoustic, electric, classical, archtop)
- Tonewood science (spruce, mahogany, rosewood, maple properties)
- Historical evolution from Baroque guitar → modern electric
- Famous luthiers (Torres, Martin, Gibson, Fender, D'Angelico, Benedetto)
- Pickup technology and electronics
- Setup, maintenance, and repair guidance
- String theory (gauge, material, tension relationships)

#### Agent 2: Jazz Guitar Teacher (Mastery Level)

| Property | Value |
|----------|-------|
| **Name** | `jazz_teacher` |
| **Role** | Master jazz guitar educator covering theory, technique, improvisation, repertoire, and practice methodology |
| **Model** | `gpt-4o` (or equivalent) |
| **Temperature** | 0.5 (balanced: creative for musical examples, precise for theory) |
| **Tools** | `query_chords`, `query_scales`, `query_arpeggios`, `query_jazz_standards`, `query_techniques`, `generate_exercise`, `generate_quiz`, `track_practice` |

**Domain Coverage:**
- Chord theory: triads → extended → altered → polychords
- Scale systems: modes, bebop scales, symmetric scales, pentatonic applications
- Arpeggio superimposition and targeting
- Voice leading and chord melody
- Improvisation concepts (guide tones, enclosures, rhythmic displacement)
- Jazz standards analysis (form, harmony, common substitutions)
- Practice methodology and breaking through plateaus
- Ear training guidance
- Comping patterns and rhythmic vocabulary
- Legendary players' styles (Wes Montgomery, Joe Pass, Pat Metheny, Jim Hall, etc.)

#### Agent 3: SQL Expert with NL Recognition

| Property | Value |
|----------|-------|
| **Name** | `sql_expert` |
| **Role** | Translates natural language to optimized SQL queries, manages database operations, ensures data integrity |
| **Model** | `gpt-4o-mini` (fast, cost-effective for structured tasks) |
| **Temperature** | 0.1 (deterministic, precise) |
| **Tools** | `execute_query`, `validate_sql`, `get_schema`, `explain_query`, `format_results` |

**Domain Coverage:**
- Natural language understanding → SQL translation
- SQLite-specific syntax and optimization
- JSON column querying (`json_extract`, `json_each`)
- Query validation and injection prevention
- Result formatting for human consumption
- Schema introspection and documentation
- Performance optimization (EXPLAIN QUERY PLAN)

#### Agent 4: Full Stack Developer / Project Manager

| Property | Value |
|----------|-------|
| **Name** | `dev_pm` |
| **Role** | Orchestrates development workflow, documents progress, manages agent coordination, handles errors and recovery |
| **Model** | `gpt-4o` (or equivalent) |
| **Temperature** | 0.2 (systematic, structured) |
| **Tools** | `log_benchmark`, `log_error`, `generate_docs`, `route_to_agent`, `aggregate_responses`, `health_check` |

**Domain Coverage:**
- Development lifecycle management
- Benchmark tracking and progress documentation
- Error logging with solution documentation
- Agent health monitoring and recovery
- API design and integration patterns
- Code review and quality gates
- Documentation generation

### 4.3 Agent Communication Protocol

Agents communicate through a standardized message format:

```python
@dataclass
class AgentMessage:
    sender: str              # Agent name
    recipient: str           # Target agent or "orchestrator"
    intent: str              # What the message is about
    content: str             # The actual message
    context: dict            # Shared state
    metadata: dict           # Timestamps, token counts, etc.
    requires_response: bool  # Whether a reply is expected
```

---

## 5. Agent Training & Knowledge Bases

### 5.1 Training Data Strategy

Each agent is "trained" through three mechanisms:

1. **System Prompt** — Core personality, capabilities, and behavioral rules
2. **Knowledge Base** — Structured reference data loaded into context
3. **Database Access** — Dynamic querying of the SQLite knowledge store

### 5.2 System Prompt Engineering Principles

Follow these rules for every agent prompt:

```
1. IDENTITY:     Define WHO the agent is (role, expertise level, personality)
2. CAPABILITIES: Define WHAT the agent can do (tools, knowledge areas)
3. BOUNDARIES:   Define WHAT THE AGENT CANNOT do (limitations, handoff triggers)
4. FORMAT:       Define HOW responses should be structured
5. EXAMPLES:     Provide few-shot examples of ideal responses
6. SAFETY:       Define guardrails (no medical advice, no harmful content)
```

### 5.3 Knowledge Base Structure

Each agent's training data is stored in Markdown files under `data/training/`:

```markdown
# Agent: Jazz Guitar Teacher — Knowledge Base

## Section 1: Chord Theory

### 1.1 Triad Types
- Major: 1 3 5 (bright, resolved)
- Minor: 1 b3 5 (dark, melancholic)
- Diminished: 1 b3 b5 (tense, unstable)
- Augmented: 1 3 #5 (mysterious, unresolved)

### 1.2 Seventh Chord Types
- Major 7: 1 3 5 7 (lush, dreamy — Cmaj7 = C E G B)
- Dominant 7: 1 3 5 b7 (bluesy, wants to resolve — C7 = C E G Bb)
- Minor 7: 1 b3 5 b7 (smooth, mellow — Cm7 = C Eb G Bb)
- Half-Diminished: 1 b3 b5 b7 (yearning — Cm7b5 = C Eb Gb Bb)
- Diminished 7: 1 b3 b5 bb7 (symmetric, tense — Cdim7 = C Eb Gb Bbb)
...
```

### 5.4 Dynamic Training via Database

The seed data in `data/seed/` is loaded into SQLite tables at initialization. Agents query this data at runtime, meaning the knowledge base grows as users interact:

- New practice routines are saved
- Quiz results inform adaptive difficulty
- User questions that stump agents are logged for knowledge base expansion

### 5.5 Continuous Improvement Loop

```
User asks question
    │
    ▼
Agent attempts answer
    │
    ├─── Success → Log response quality metrics
    │
    └─── Failure/Low confidence → Log to "knowledge gaps" table
                                   │
                                   ▼
                          Dev/PM agent flags gap
                                   │
                                   ▼
                          Human reviews & adds data
                                   │
                                   ▼
                          Knowledge base updated
```

---

## 6. Orchestration Layer

### 6.1 Intent Classification

The orchestrator first classifies user intent to route to the correct agent:

```python
INTENT_CATEGORIES = {
    "guitar_history":     "luthier_historian",   # Construction, history, luthiers
    "guitar_setup":       "luthier_historian",   # Setup, maintenance, repair
    "music_theory":       "jazz_teacher",        # Chords, scales, theory
    "technique":          "jazz_teacher",         # Playing technique
    "improvisation":      "jazz_teacher",         # Soloing, improvisation
    "practice":           "jazz_teacher",         # Practice routines, plateau help
    "jazz_repertoire":    "jazz_teacher",         # Standards, tunes
    "data_query":         "sql_expert",           # Specific data lookups
    "quiz":               "jazz_teacher",         # Quiz generation/taking
    "lesson":             "jazz_teacher",         # Interactive lessons
    "system":             "dev_pm",               # System status, docs, errors
    "multi_domain":       "orchestrator",         # Requires multiple agents
}
```

### 6.2 Multi-Agent Coordination Patterns

**Pattern 1: Sequential Pipeline**
```
User: "What wood did D'Angelico use for his archtops, and what scales work
       best over the jazz tones those guitars produce?"

Orchestrator detects: multi_domain (history + theory)
    │
    ▼
Step 1: Luthier Agent → D'Angelico's wood choices (spruce top, maple back/sides)
    │
    ▼
Step 2: Jazz Teacher Agent → Scales for archtop jazz tones (given context from Step 1)
    │
    ▼
Step 3: Orchestrator → Combines into cohesive response
```

**Pattern 2: Parallel Execution**
```
User: "Give me a quiz on jazz chords and also tell me about
       the history of the Gibson L-5"

Orchestrator detects: two independent requests
    │
    ├──→ Jazz Teacher Agent → Generates chord quiz (async)
    │
    └──→ Luthier Agent → Gibson L-5 history (async)
    │
    ▼
Orchestrator → Combines both results
```

**Pattern 3: Tool-Assisted Single Agent**
```
User: "What dominant 7th chords are in the database with
       difficulty level 3 or higher?"

Orchestrator detects: data_query
    │
    ▼
SQL Expert Agent:
    1. Translates to SQL
    2. Validates query
    3. Executes against SQLite
    4. Formats results
    │
    ▼
Returns formatted chord list
```

### 6.3 Context Management

A shared context object travels with every request:

```python
@dataclass
class ConversationContext:
    session_id: str
    user_id: str | None
    user_skill_level: str          # beginner, intermediate, advanced
    conversation_history: list     # Last N messages
    current_topic: str | None      # Active discussion topic
    active_lesson: dict | None     # If in a lesson
    active_quiz: dict | None       # If taking a quiz
    agent_routing_history: list    # Which agents have been consulted
    metadata: dict                 # Timestamps, token budget, etc.
```

---

## 7. API Layer (FastAPI)

### 7.1 Endpoint Design

```
POST   /api/v1/chat                    # Main conversational endpoint
POST   /api/v1/chat/stream             # SSE streaming responses

GET    /api/v1/lessons                  # List available lessons
GET    /api/v1/lessons/{id}             # Get specific lesson
POST   /api/v1/lessons/{id}/start      # Begin interactive lesson
POST   /api/v1/lessons/{id}/respond    # Submit lesson response

GET    /api/v1/quizzes                  # List available quizzes
POST   /api/v1/quizzes/generate        # Generate a new quiz
POST   /api/v1/quizzes/{id}/submit     # Submit quiz answers
GET    /api/v1/quizzes/{id}/results    # Get quiz results

GET    /api/v1/practice/log             # Get practice history
POST   /api/v1/practice/log             # Log a practice session
GET    /api/v1/practice/stats           # Practice statistics

GET    /api/v1/reference/chords         # Browse chord library
GET    /api/v1/reference/scales         # Browse scale library
GET    /api/v1/reference/arpeggios      # Browse arpeggio library
GET    /api/v1/reference/standards      # Browse jazz standards

GET    /api/v1/admin/health             # System health check
GET    /api/v1/admin/logs               # Agent activity logs
GET    /api/v1/admin/benchmarks         # Development benchmarks
```

### 7.2 Request/Response Models

```python
# Request
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = None
    preferred_agent: str | None = None  # Optional: force specific agent
    context: dict | None = None

# Response
class ChatResponse(BaseModel):
    message: str
    agent_used: str
    session_id: str
    suggestions: list[str] | None = None  # Follow-up suggestions
    data: dict | None = None              # Structured data (chords, etc.)
    quiz: dict | None = None              # If a quiz was generated
    metadata: dict                        # Timing, tokens, etc.
```

### 7.3 Streaming with Server-Sent Events

For long responses, use SSE streaming:

```python
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        async for chunk in orchestrator.stream_response(request):
            yield {
                "event": "message",
                "data": json.dumps({"content": chunk.content, "done": chunk.is_final})
            }
    return EventSourceResponse(event_generator())
```

---

## 8. Frontend (Interactive Lessons & Quizzes)

### 8.1 UI Architecture

The frontend uses **server-rendered HTML with HTMX** for dynamic interactions. This keeps the stack simple while providing a responsive, modern feel.

```
┌─────────────────────────────────────────┐
│  Navigation Bar                          │
│  [Chat] [Lessons] [Quizzes] [Practice]  │
├─────────────────────────────────────────┤
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  Chat Interface                  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Conversation History     │  │    │
│  │  │  (scrollable)             │  │    │
│  │  └───────────────────────────┘  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Agent Indicator          │  │    │
│  │  │  🎸 Jazz Teacher          │  │    │
│  │  └───────────────────────────┘  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Input + Send Button      │  │    │
│  │  └───────────────────────────┘  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Quick Actions            │  │    │
│  │  │  [Quiz Me] [Practice]     │  │    │
│  │  │  [Random Tip] [Standards] │  │    │
│  │  └───────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
│                                          │
├─────────────────────────────────────────┤
│  Sidebar: Practice Stats & Progress     │
└─────────────────────────────────────────┘
```

### 8.2 Interactive Quiz Flow

```
1. User requests quiz → POST /api/v1/quizzes/generate
   - Topic selection (chords, scales, history, etc.)
   - Difficulty adapts to user's history

2. Quiz rendered with HTMX partial swap
   - Multiple choice, fill-in-blank, or "name that chord/scale"
   - Timer (optional)

3. Each answer submitted → POST /api/v1/quizzes/{id}/submit
   - Immediate feedback per question
   - Explanation of correct answer

4. Final results → GET /api/v1/quizzes/{id}/results
   - Score, time, areas for improvement
   - Suggested practice material
   - Results saved to practice_logs
```

### 8.3 Interactive Lesson Flow

```
1. Browse lessons → GET /api/v1/lessons
   - Categorized: Theory, Technique, History, Improvisation

2. Start lesson → POST /api/v1/lessons/{id}/start
   - Lesson plan presented (objectives, prerequisites)

3. Step-by-step interaction:
   - Agent presents concept + example
   - User responds (answer question, confirm understanding)
   - Agent adapts based on response
   - Mini-quiz checkpoints embedded in lesson

4. Lesson completion:
   - Summary of what was covered
   - Practice assignments generated
   - Progress saved to database
```

---

## 9. Cursor Rules & Agentic Development

### 9.1 Rule Hierarchy for This Project

Create the following `.cursor/rules/` files to guide AI-assisted development:

#### `project-wide.mdc` — Global Standards

```markdown
---
description: Global project conventions for the Guitar Mastery AI app
globs: ["**/*.py", "**/*.html", "**/*.js"]
alwaysApply: true
---

# Project Standards

## Architecture
- This is a multi-agent AI application with 4 specialized agents
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Jinja2 + HTMX
- All agents inherit from BaseAgent in src/agents/base.py

## Code Style
- Python 3.11+ with type hints on all functions
- Use async/await for all I/O operations
- Pydantic models for all data validation
- Structured logging via structlog (never print())
- Docstrings on all public functions (Google style)

## Database
- SQLite via SQLAlchemy async
- All queries must use parameterized statements
- Never construct SQL strings with f-strings or concatenation
- Use JSON columns for flexible/nested data

## Error Handling
- All errors logged to agent_logs table
- Agents must gracefully degrade (never crash on bad input)
- Use custom exception classes in src/utils/exceptions.py
```

#### `agents.mdc` — Agent Development Patterns

```markdown
---
description: Patterns for developing and modifying AI agents
globs: ["src/agents/**/*.py"]
alwaysApply: false
---

# Agent Development Rules

## Creating a New Agent
1. Inherit from BaseAgent
2. Define system prompt in config/agents.yaml
3. Register tools as typed async functions
4. Add training data to data/training/
5. Register in orchestrator router (src/orchestrator/router.py)
6. Add tests in tests/test_agents/

## Agent Design Principles
- Single responsibility: one domain per agent
- Tools are pure functions where possible
- System prompts are externalized (never hardcoded)
- All agent actions are logged to agent_logs table
- Agents must include confidence scores in responses
- Low-confidence responses trigger handoff to orchestrator
```

### 9.2 Using Cursor Agents Effectively

When developing this app in Cursor:

1. **Use Agent Mode** for implementation tasks (writing code, running tests)
2. **Use Plan Mode** for architectural decisions (adding new agents, changing schemas)
3. **Reference rules with `@`** — e.g., `@agents.mdc` when working on agent code
4. **Leverage multi-file edits** — Agent mode can modify multiple files atomically
5. **Use terminal for testing** — Run `pytest` and `uvicorn` from integrated terminal

---

## 10. Scalability Patterns

### 10.1 Horizontal Scaling Strategy

```
Phase 1: Single Process (MVP)
├── SQLite file database
├── In-process agents
├── Single Uvicorn worker
└── Good for: 1-10 concurrent users

Phase 2: Multi-Worker (Growth)
├── SQLite with WAL mode (concurrent reads)
├── Multiple Uvicorn workers (--workers 4)
├── Redis for session state
├── Nginx reverse proxy
└── Good for: 10-100 concurrent users

Phase 3: Distributed (Scale)
├── PostgreSQL (replaces SQLite)
├── Agent workers via Celery/ARQ task queue
├── Redis for caching + sessions
├── CDN for static assets
├── Docker Swarm / Kubernetes
└── Good for: 100-10,000+ concurrent users
```

### 10.2 Database Scaling

```python
# Phase 1: SQLite with WAL mode for concurrent reads
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./guitar_mastery.db"

# Enable WAL mode for better concurrency
async def configure_sqlite(connection):
    await connection.execute("PRAGMA journal_mode=WAL")
    await connection.execute("PRAGMA busy_timeout=5000")
    await connection.execute("PRAGMA synchronous=NORMAL")
    await connection.execute("PRAGMA cache_size=-64000")  # 64MB cache
    await connection.execute("PRAGMA foreign_keys=ON")
```

### 10.3 LLM Call Optimization

```python
# 1. Caching: Cache identical queries
from functools import lru_cache
import hashlib

class LLMCache:
    """Cache LLM responses for identical inputs."""
    async def get_or_call(self, prompt_hash, call_fn):
        cached = await self.db.get_cached_response(prompt_hash)
        if cached and not cached.is_expired:
            return cached.response
        response = await call_fn()
        await self.db.cache_response(prompt_hash, response)
        return response

# 2. Model Tiering: Use cheaper models for simple tasks
MODEL_TIERS = {
    "complex":   "gpt-4o",        # Multi-step reasoning, teaching
    "standard":  "gpt-4o-mini",   # SQL generation, classification
    "simple":    "gpt-3.5-turbo", # Formatting, summarization
}

# 3. Prompt Compression: Minimize token usage
def compress_context(history: list, max_tokens: int) -> list:
    """Keep only the most relevant context within token budget."""
    ...
```

### 10.4 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat")
@limiter.limit("30/minute")
async def chat(request: ChatRequest):
    ...
```

---

## 11. Customizability & Extension

### 11.1 Adding a New Agent

To add a new specialized agent (e.g., a "Blues Guitar Expert"):

```bash
# 1. Create agent file
touch src/agents/blues_expert.py

# 2. Add training data
touch data/training/blues_expert_knowledge.md

# 3. Add seed data
touch data/seed/blues_vocabulary.json

# 4. Add configuration
# Edit config/agents.yaml — add blues_expert section

# 5. Register in router
# Edit src/orchestrator/router.py — add routing rules

# 6. Add tests
touch tests/test_agents/test_blues_expert.py

# 7. Run seed migration
python -m src.db.seed --agent blues_expert
```

### 11.2 Plugin Architecture

```python
# src/agents/base.py

class AgentPlugin:
    """Base class for agent plugins/extensions."""
    name: str
    version: str

    async def on_before_think(self, context): ...
    async def on_after_think(self, response): ...
    async def on_tool_call(self, tool_name, kwargs): ...
    async def on_error(self, error): ...

# Example: Analytics plugin that tracks all interactions
class AnalyticsPlugin(AgentPlugin):
    name = "analytics"
    version = "1.0.0"

    async def on_after_think(self, response):
        await self.track_response_quality(response)
        await self.update_topic_popularity(response.topic)
```

### 11.3 Custom Tool Registration

```python
# Anyone can add new tools for agents:

@tool(name="generate_chord_diagram", agent="jazz_teacher")
async def generate_chord_diagram(chord_name: str, position: int = 0) -> dict:
    """Generate an ASCII chord diagram for the given chord."""
    chord = await db.get_chord(chord_name)
    return {
        "diagram": render_ascii_chord(chord, position),
        "notes": chord.notes,
        "intervals": chord.intervals,
    }
```

### 11.4 User Customization

```python
# Users can customize their experience:
class UserPreferences(BaseModel):
    skill_level: Literal["beginner", "intermediate", "advanced"]
    preferred_genres: list[str]          # ["jazz", "blues", "classical"]
    practice_goals: list[str]           # ["improvisation", "sight_reading"]
    quiz_difficulty: Literal["easy", "medium", "hard", "adaptive"]
    response_detail: Literal["concise", "standard", "detailed"]
    notation_preference: Literal["tab", "standard", "both"]
    tuning: str = "standard"            # Standard, Drop D, DADGAD, etc.
```

---

## 12. Testing Strategy

### 12.1 Test Pyramid

```
                    ┌──────────┐
                    │   E2E    │  ← Few: Full user flows
                   ┌┤          ├┐
                  ┌┤│Integration│├┐  ← Some: API + DB + Agents
                 ┌┤│├──────────┤│├┐
                ┌┤│││   Unit   │││├┐  ← Many: Individual functions
                └┴┴┴┴──────────┴┴┴┴┘
```

### 12.2 Test Categories

```python
# Unit Tests — test individual components in isolation
class TestChordQuery:
    async def test_query_major_seventh_chords(self, db_session):
        results = await queries.get_chords(db_session, category="jazz", chord_type="maj7")
        assert len(results) > 0
        assert all(c.formula == "1 3 5 7" for c in results)

# Agent Tests — test agent reasoning with mocked LLM
class TestJazzTeacherAgent:
    async def test_identifies_chord_from_intervals(self, mock_llm):
        agent = JazzTeacherAgent(llm=mock_llm)
        response = await agent.think("What chord has the intervals 1 3 5 b7?")
        assert "dominant" in response.content.lower()

# Integration Tests — test full request flow
class TestChatEndpoint:
    async def test_chat_routes_to_correct_agent(self, client):
        response = await client.post("/api/v1/chat", json={
            "message": "Tell me about the history of the Les Paul"
        })
        assert response.json()["agent_used"] == "luthier_historian"

# E2E Tests — test complete user journeys
class TestQuizFlow:
    async def test_complete_quiz_journey(self, client):
        # Generate quiz
        quiz = await client.post("/api/v1/quizzes/generate", json={"topic": "jazz_chords"})
        quiz_id = quiz.json()["id"]

        # Submit answers
        result = await client.post(f"/api/v1/quizzes/{quiz_id}/submit", json={...})
        assert result.json()["score"] >= 0

        # Check it was saved
        history = await client.get("/api/v1/practice/log")
        assert any(log["quiz_id"] == quiz_id for log in history.json())
```

### 12.3 Testing Agents Without Real LLM Calls

```python
# conftest.py
@pytest.fixture
def mock_llm():
    """Mock LLM that returns deterministic responses based on input patterns."""
    return MockLLM(responses={
        r".*chord.*intervals.*1 3 5 b7.*": "That's a dominant 7th chord.",
        r".*history.*Les Paul.*": "The Gibson Les Paul was introduced in 1952...",
        r".*scale.*dorian.*": "The Dorian mode is: 1 2 b3 4 5 6 b7",
    })
```

---

## 13. Development Lifecycle & Documentation

### 13.1 Phase-Based Development

| Phase | Benchmark | Deliverables |
|-------|-----------|-------------|
| **Phase 0: Foundation** | Project scaffolding complete | Directory structure, dependencies, configs, Cursor rules |
| **Phase 1: Database** | Schema + seed data complete | Models, migrations, seed scripts, query library |
| **Phase 2: Base Agent** | Base agent class working | BaseAgent, tool registration, logging |
| **Phase 3: Luthier Agent** | Guitar history queries working | Agent + training data + tools + tests |
| **Phase 4: Jazz Teacher** | Theory + technique responses working | Agent + training data + tools + tests |
| **Phase 5: SQL Expert** | NL-to-SQL pipeline working | Agent + validation + security + tests |
| **Phase 6: Dev/PM Agent** | Documentation auto-generation working | Agent + benchmark tracking + tests |
| **Phase 7: Orchestrator** | Multi-agent routing working | Router + coordinator + context + tests |
| **Phase 8: API** | All endpoints functional | Routes + schemas + middleware + tests |
| **Phase 9: Frontend** | UI complete and interactive | Templates + HTMX + quiz engine |
| **Phase 10: Quizzes & Lessons** | Interactive features working | Quiz generation + lesson engine + progress tracking |
| **Phase 11: Integration** | Full system integration tested | E2E tests + performance benchmarks |
| **Phase 12: Polish** | Production-ready | Error handling + logging + documentation + Docker |

### 13.2 Automated Benchmark Tracking

```python
# src/utils/benchmarks.py

class BenchmarkTracker:
    """Track development progress and log to database."""

    async def start_phase(self, phase: str, description: str):
        await self.db.insert_benchmark(phase=phase, description=description, status="in_progress")

    async def complete_phase(self, phase: str, notes: str = ""):
        await self.db.update_benchmark(phase=phase, status="completed", notes=notes)

    async def log_failure(self, phase: str, error: str, solution: str = ""):
        await self.db.update_benchmark(
            phase=phase,
            failures={"error": error, "timestamp": now()},
            solutions={"fix": solution, "timestamp": now()} if solution else None
        )

    async def generate_report(self) -> str:
        """Generate markdown report of all benchmarks."""
        benchmarks = await self.db.get_all_benchmarks()
        return render_benchmark_report(benchmarks)
```

### 13.3 Error Documentation Pattern

Every failure is documented with this structure:

```markdown
## Error: [ERROR-001] Agent Routing Failure

**Phase:** Phase 7 — Orchestrator
**Date:** 2026-02-07
**Severity:** Medium

### Problem
User query "What strings does a D'Angelico use?" was routed to jazz_teacher
instead of luthier_historian because "strings" triggered the technique classifier.

### Root Cause
Intent classifier weighted the word "strings" too heavily toward technique/playing.
The word "D'Angelico" (a luthier name) should have been the primary signal.

### Solution
Added named entity recognition for known luthier/brand names to the intent
classifier. Luthier/brand detection now takes priority over generic musical terms.

### Prevention
Added test case to test_orchestrator/test_routing.py to verify luthier name
detection overrides generic term classification.

### Files Changed
- src/orchestrator/router.py (added luthier_names set)
- data/seed/luthier_names.json (new)
- tests/test_orchestrator/test_routing.py (added test)
```

### 13.4 Living Documentation

The Dev/PM agent automatically maintains:

- `docs/CHANGELOG.md` — Updated after each phase completion
- `docs/BENCHMARKS.md` — Auto-generated from benchmark database
- `docs/DEBUGGING.md` — Accumulated error + solution pairs
- `docs/DECISIONS.md` — Architecture Decision Records (ADRs)

---

## 14. Deployment & Operations

### 14.1 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize database
RUN python -m src.db.connection --init && python -m src.db.seed

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.9"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data          # Persist database
      - ./.env:/app/.env          # Environment variables
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/admin/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 14.2 Environment Configuration

```bash
# .env.example
ENVIRONMENT=development
DEBUG=true

# LLM Configuration
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4o
FALLBACK_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/guitar_mastery.db

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 14.3 Health Monitoring

```python
@router.get("/admin/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_db_connection(),
        "agents": {
            "luthier_historian": await check_agent_health("luthier_historian"),
            "jazz_teacher": await check_agent_health("jazz_teacher"),
            "sql_expert": await check_agent_health("sql_expert"),
            "dev_pm": await check_agent_health("dev_pm"),
        },
        "uptime_seconds": get_uptime(),
        "version": APP_VERSION,
    }
```

---

## 15. Troubleshooting & Debugging Playbook

### 15.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent returns generic response | System prompt too vague | Add more specific examples and boundaries |
| SQL injection warning | Raw string interpolation | Use parameterized queries exclusively |
| Slow response time | Large context window | Compress conversation history, use model tiering |
| Wrong agent selected | Ambiguous user intent | Improve intent classifier with more training examples |
| Database locked | Concurrent writes in SQLite | Enable WAL mode, add busy_timeout |
| Quiz generates invalid questions | Insufficient seed data | Expand quiz template library in seed data |
| Agent hallucination | No relevant data in knowledge base | Add missing data, implement confidence scoring |
| Frontend not updating | HTMX swap target mismatch | Verify hx-target and hx-swap attributes |

### 15.2 Debug Mode

```python
# Enable debug mode for verbose agent logging
# In .env: DEBUG=true

# This enables:
# 1. Full prompt logging (system + user + context)
# 2. Token count tracking per request
# 3. Latency breakdown (routing, LLM, DB, formatting)
# 4. SQL query logging with execution plans
# 5. Agent decision trace (why a particular agent was chosen)
```

### 15.3 Agent Debugging Commands

```bash
# Test a specific agent directly (bypass orchestrator)
python -m src.agents.jazz_teacher --query "Explain the Dorian mode"

# Test SQL generation without execution
python -m src.agents.sql_expert --query "List all minor 7 chords" --dry-run

# Test intent classification
python -m src.orchestrator.router --classify "What wood is best for acoustic guitars?"

# Run all agent tests
pytest tests/test_agents/ -v

# Check database integrity
python -m src.db.connection --check
```

---

## Appendix A: Step-by-Step Build Order

For developers building this from scratch in Cursor, follow this exact order:

```
Step  1: Create project structure (directories, configs)           ⬜
Step  2: Set up dependencies (requirements.txt, .env)              ⬜
Step  3: Create Cursor rules (.cursor/rules/*.mdc)                 ⬜
Step  4: Design and create SQLite schema (models.py)               ⬜
Step  5: Create seed data JSON files (data/seed/*.json)            ⬜
Step  6: Build database connection + seed script                   ⬜
Step  7: Build BaseAgent class (src/agents/base.py)                ⬜
Step  8: Build Luthier & Historian agent + training data           ⬜
Step  9: Build Jazz Teacher agent + training data                  ⬜
Step 10: Build SQL Expert agent + training data                    ⬜
Step 11: Build Dev/PM agent + training data                        ⬜
Step 12: Build Orchestrator (router + coordinator + context)       ⬜
Step 13: Build FastAPI endpoints (routes + schemas)                ⬜
Step 14: Build frontend templates (Jinja2 + HTMX)                 ⬜
Step 15: Build quiz engine                                         ⬜
Step 16: Build lesson engine                                       ⬜
Step 17: Build practice tracking                                   ⬜
Step 18: Write unit tests for all agents                           ⬜
Step 19: Write integration tests for API                           ⬜
Step 20: Write E2E tests for user journeys                         ⬜
Step 21: Add benchmark tracking + documentation generation         ⬜
Step 22: Docker containerization                                   ⬜
Step 23: Performance optimization + caching                        ⬜
Step 24: Final documentation pass                                  ⬜
```

---

## Appendix B: Sample Interactions

### Interaction 1: Theory Question

```
User: "What scales can I play over a Cmaj7 chord?"

Orchestrator: Routes to jazz_teacher (intent: music_theory)

Jazz Teacher Response:
"Great question! Over a Cmaj7 chord, you have several scale options:

1. **C Ionian (Major Scale)** — 1 2 3 4 5 6 7
   The most consonant choice. The natural home scale.

2. **C Lydian** — 1 2 3 #4 5 6 7
   A favorite in jazz! The #4 adds a bright, floating quality.
   Works especially well when Cmaj7 is NOT functioning as the I chord.

3. **C Major Pentatonic** — 1 2 3 5 6
   Safe and melodic. Great for beginners or lyrical playing.

4. **C Major Bebop Scale** — 1 2 3 4 5 6 b7 7
   Adds a passing chromatic tone. Essential for bebop-style lines.

Would you like me to:
- Show you fingering patterns for any of these?
- Generate a practice exercise using these scales?
- Quiz you on scale-chord relationships?"
```

### Interaction 2: History Question

```
User: "Who built the first archtop guitar?"

Orchestrator: Routes to luthier_historian (intent: guitar_history)

Luthier Response:
"The first archtop guitar is credited to Orville Gibson, who began
building mandolins and guitars with carved, arched tops in the 1890s
in Kalamazoo, Michigan. His innovation was applying violin construction
principles — carved spruce tops and maple backs — to the guitar.

However, it was Lloyd Loar, working at the Gibson company in the early
1920s, who refined the archtop concept with the Gibson L-5 (1922),
which featured f-holes instead of a round soundhole, a floating
pickguard, and a more violin-like construction that became the template
for all jazz guitars to follow.

The archtop design was later perfected by independent luthiers like
John D'Angelico (1932-1964) in New York City, whose handmade instruments
are considered the pinnacle of archtop construction."
```

### Interaction 3: Database Query

```
User: "Show me all the jazz chords with a b9 in them"

Orchestrator: Routes to sql_expert (intent: data_query)

SQL Expert Process:
1. NL → SQL: SELECT name, formula, intervals, category FROM chords
              WHERE json_extract(intervals, '$') LIKE '%b9%'
              AND category IN ('jazz', 'altered', 'extended')
2. Validates: SELECT only, parameterized, no injection risk
3. Executes: Returns 12 results
4. Formats: Clean table with chord names, formulas, and intervals

Response:
"Here are the jazz chords containing a b9 interval:

| Chord Type      | Formula           | Example |
|-----------------|-------------------|---------|
| 7b9             | 1 3 5 b7 b9      | C7b9    |
| 7#9b9           | 1 3 5 b7 b9 #9   | C7#9b9  |
| 7b9#11          | 1 3 5 b7 b9 #11  | C7b9#11 |
| 13b9            | 1 3 5 b7 b9 13   | C13b9   |
| dim(maj7)       | 1 b3 b5 7        | Cdim(M7)|
..."
```

---

## Appendix C: Cursor Workflow Tips

1. **Start each session** by telling Cursor: "Read @GUIDE.md and @config/agents.yaml for project context"
2. **When adding features**, reference the relevant `.mdc` rule: "Follow @agents.mdc to add a new Blues agent"
3. **For debugging**, ask Cursor to "Check docs/DEBUGGING.md for known solutions"
4. **For benchmarks**, ask Cursor to "Update BENCHMARKS.md with Phase X completion"
5. **Use Plan Mode** before major architectural changes
6. **Use Agent Mode** for implementation of well-defined features
7. **Run tests frequently**: `pytest -x --tb=short` after every significant change

---

*This guide is a living document. The Dev/PM agent will update it as the project evolves.*
