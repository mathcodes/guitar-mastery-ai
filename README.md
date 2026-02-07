# Guitar Mastery AI

A multi-agent AI application for comprehensive guitar education — covering history, construction, jazz theory, technique, improvisation, and interactive practice.

## Quick Start

```bash
# 1. Clone and enter project
cd today_agent

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# 5. Initialize database
python -m src.db.connection --init

# 6. Run the application
uvicorn src.main:app --reload --port 8000

# 7. Open in browser
open http://localhost:8000/docs
```

## Agents

| Agent | Expertise |
|-------|-----------|
| **Guitar Luthier & Historian** | Construction, tonewoods, instrument history, famous luthiers, pickup technology |
| **Jazz Guitar Teacher** | Theory, scales, chords, improvisation, technique, practice methodology, plateau-busting |
| **SQL & Data Expert** | Natural language to SQL queries, database operations on the knowledge base |
| **Full Stack Dev & PM** | Development coordination, benchmarks, documentation, system health |

## API

- **Chat**: `POST /api/v1/chat` — Send a message, get a response from the appropriate agent
- **Agents**: `GET /api/v1/chat/agents` — List available agents
- **Health**: `GET /api/v1/admin/health` — System health check
- **Docs**: `GET /docs` — Interactive API documentation (Swagger)

## Project Structure

```
src/
  agents/       # Specialized AI agents (one per file)
  orchestrator/ # Intent routing and agent coordination
  db/           # SQLAlchemy models, queries, connection
  api/          # FastAPI routes and schemas
  frontend/     # Jinja2 templates + HTMX
  utils/        # Logging, benchmarks, helpers
data/
  seed/         # JSON seed data for the knowledge base
  training/     # Agent training/reference data (Markdown)
config/         # Settings, agent configs, logging
docs/           # Architecture, changelog, debugging guide
tests/          # pytest test suite
```

## Development Guide

See **[GUIDE.md](GUIDE.md)** for the comprehensive step-by-step development guide covering architecture, database design, agent training, scalability, and the full development lifecycle.

## Tech Stack

Python 3.11+ | FastAPI | SQLAlchemy | SQLite | Anthropic Claude | Pydantic | HTMX | structlog | Docker
