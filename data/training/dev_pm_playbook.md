# Full Stack Developer & Project Manager — Playbook

## Development Lifecycle Phases

### Phase 0: Foundation
- [x] Project directory structure created
- [x] Dependencies defined (requirements.txt)
- [x] Configuration system (settings.py, agents.yaml)
- [x] Cursor rules created (.cursor/rules/)
- [x] Git initialized with .gitignore

### Phase 1: Database
- [ ] SQLAlchemy models defined (models.py)
- [ ] Connection management (connection.py)
- [ ] Query library (queries.py)
- [ ] Seed data created (data/seed/*.json)
- [ ] Database initialization script
- [ ] Seed data loading script

### Phase 2: Base Agent
- [ ] BaseAgent abstract class
- [ ] Tool registration system
- [ ] LLM integration (OpenAI API)
- [ ] Structured logging
- [ ] Confidence scoring
- [ ] Error handling

### Phases 3-6: Individual Agents
- [ ] Luthier & Historian agent
- [ ] Jazz Guitar Teacher agent
- [ ] SQL Expert agent
- [ ] Dev/PM agent

### Phase 7: Orchestrator
- [ ] Intent classifier (router.py)
- [ ] Agent coordinator (coordinator.py)
- [ ] Context management (context.py)
- [ ] Multi-agent coordination patterns

### Phase 8: API
- [ ] Chat endpoint
- [ ] Quiz endpoints
- [ ] Practice tracking endpoints
- [ ] Admin/health endpoints
- [ ] Pydantic schemas

### Phase 9: Frontend
- [ ] Base template (HTML/CSS)
- [ ] Chat interface
- [ ] Quiz interface
- [ ] Practice dashboard

### Phase 10: Interactive Features
- [ ] Quiz generation engine
- [ ] Lesson engine
- [ ] Practice tracking
- [ ] Progress analytics

### Phase 11: Integration Testing
- [ ] Unit tests for all agents
- [ ] Integration tests for API
- [ ] E2E tests for user journeys
- [ ] Performance benchmarks

### Phase 12: Polish & Deploy
- [ ] Error handling hardened
- [ ] Logging complete
- [ ] Documentation finalized
- [ ] Docker containerization
- [ ] Deployment scripts

## Error Documentation Template

```markdown
## Error: [ERROR-XXX] Title

**Phase:** Phase X — Name
**Date:** YYYY-MM-DD
**Severity:** Low / Medium / High / Critical

### Problem
What happened and what was expected.

### Root Cause
Why it happened.

### Solution
What was done to fix it.

### Prevention
How to prevent it from happening again.

### Files Changed
- file1.py (description of change)
- file2.py (description of change)
```

## Architecture Decision Record (ADR) Template

```markdown
## ADR-XXX: Decision Title

**Date:** YYYY-MM-DD
**Status:** Proposed / Accepted / Deprecated / Superseded

### Context
What is the background and why is a decision needed?

### Decision
What is the decision and its rationale?

### Consequences
What are the positive and negative consequences?

### Alternatives Considered
What other options were evaluated?
```

## Quality Gates

Before advancing to the next phase:
1. All tests pass (`pytest -v`)
2. No linting errors
3. Documentation updated
4. Benchmark logged to database
5. Any failures documented with solutions
6. Code reviewed (by Cursor agent or human)

## Metrics to Track

- **Response latency**: Time from request to response (target: <3s)
- **Token usage**: Input + output tokens per request (target: minimize)
- **Error rate**: Percentage of failed requests (target: <1%)
- **Routing accuracy**: Correct agent selected (target: >90%)
- **Quiz completion rate**: Users who finish started quizzes (target: >70%)
- **User satisfaction**: Response helpfulness (target: >4/5)
