# Debugging Guide — Failures & Solutions

*Every failure encountered during development is documented here with its root cause and solution. This serves as a searchable reference for recurring issues.*

## Error Index

| Error ID | Phase | Severity | Summary |
|----------|-------|----------|---------|
| (none yet) | — | — | No errors documented yet |

---

## Error Template

When adding a new error, copy and fill in this template:

```
## Error: [ERROR-XXX] Brief Title

**Phase:** Phase X — Name
**Date:** YYYY-MM-DD
**Severity:** Low / Medium / High / Critical

### Problem
Clear description of what went wrong and what was expected.

### Root Cause
Analysis of WHY it happened.

### Solution
Step-by-step description of what was done to fix it.

### Prevention
Changes made to prevent this from happening again (tests, validation, etc.)

### Files Changed
- `path/to/file.py` — (what changed)
```

---

## Common Issue Categories

### Agent Issues
- Agent returns generic/unhelpful response → Improve system prompt specificity
- Wrong agent selected for query → Add patterns to router.py
- Agent hallucinates facts → Add confidence scoring, check knowledge base

### Database Issues
- "Database is locked" → Ensure WAL mode is enabled, check busy_timeout
- Slow queries → Run EXPLAIN QUERY PLAN, add indexes
- JSON column query returns nothing → Check json_extract syntax

### API Issues
- 422 Validation Error → Check Pydantic schema matches request format
- CORS errors → Add CORSMiddleware to FastAPI app
- Timeout on LLM calls → Increase timeout or use streaming

### Frontend Issues
- HTMX swap not working → Verify hx-target and hx-swap attributes match
- Stale content → Check hx-trigger settings
