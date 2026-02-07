# SQL Expert — Training Knowledge Base

## Common Natural Language → SQL Patterns

### Pattern 1: Simple Lookup
**NL**: "What is the formula for a minor 7th chord?"
**SQL**: `SELECT name, formula, intervals, description FROM chords WHERE chord_type = 'min7' LIMIT 1`

### Pattern 2: Filtered List
**NL**: "Show me all jazz chords with difficulty 3 or higher"
**SQL**: `SELECT name, formula, category, difficulty FROM chords WHERE category = 'jazz' AND difficulty >= 3 ORDER BY difficulty`

### Pattern 3: Search by Content
**NL**: "Find chords that use the b9 interval"
**SQL**: `SELECT name, formula, intervals FROM chords WHERE intervals LIKE '%b9%'`

### Pattern 4: Cross-Reference
**NL**: "What scales work over a dominant 7th chord?"
**SQL**: `SELECT name, formula, chord_compatibility FROM scales WHERE chord_compatibility LIKE '%dom7%'`

### Pattern 5: Aggregation
**NL**: "How many scales are in each category?"
**SQL**: `SELECT category, COUNT(*) as count FROM scales GROUP BY category ORDER BY count DESC`

### Pattern 6: JSON Column Queries
**NL**: "Which jazz standards have notable recordings by Miles Davis?"
**SQL**: `SELECT title, composer, notable_recordings FROM jazz_standards WHERE notable_recordings LIKE '%Miles Davis%'`

### Pattern 7: Complex Filters
**NL**: "Show me beginner-friendly scales that work over minor chords"
**SQL**: `SELECT name, formula, character, chord_compatibility FROM scales WHERE difficulty <= 2 AND (chord_compatibility LIKE '%min7%' OR chord_compatibility LIKE '%min9%')`

## SQLite-Specific Optimization Tips

1. **JSON Functions**: Use `json_extract(column, '$.key')` for precise JSON queries
2. **LIKE for JSON arrays**: `column LIKE '%value%'` works for simple JSON array searches
3. **GROUP_CONCAT**: Aggregate multiple values into comma-separated strings
4. **COALESCE**: Handle NULL values gracefully: `COALESCE(column, 'default')`
5. **WAL Mode**: Enables concurrent reads, essential for multi-user scenarios
6. **Indexes**: Always check `EXPLAIN QUERY PLAN` for slow queries

## Security Checklist

- [ ] Query starts with SELECT
- [ ] No DROP, DELETE, UPDATE, INSERT, ALTER, CREATE keywords
- [ ] All user values use parameterized placeholders (?)
- [ ] LIMIT clause present (default 50)
- [ ] No SQL comments (--) or multi-statement separators (;)
- [ ] No UNION-based injection patterns
- [ ] Query execution timeout enforced
