# Changelog

All notable changes to the Guitar Mastery AI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Initial project scaffolding and directory structure
- Comprehensive development guide (GUIDE.md)
- SQLAlchemy database models for all knowledge tables
- Database connection management with SQLite WAL mode optimization
- Pre-built parameterized query library
- Seed data: 15 jazz chords, 17 scales/modes, 8 guitar history entries
- Seed data: 6 technique guides, 5 jazz standards, 3 practice routines, 3 quizzes
- BaseAgent abstract class with LLM integration, tool system, and confidence scoring
- Guitar Luthier & Historian agent with history/wood/instrument tools
- Jazz Guitar Teacher agent with theory/technique/quiz tools
- SQL Expert agent with NL-to-SQL pipeline and security validation
- Dev/PM agent with benchmark tracking and documentation tools
- Intent classification router with keyword pattern matching
- Multi-agent coordinator supporting sequential and parallel execution
- Conversation context manager with session tracking
- FastAPI application with chat and admin endpoints
- Pydantic schemas for all API request/response models
- Agent training data: luthier knowledge base, jazz teacher knowledge base
- Agent training data: SQL patterns reference, dev/PM playbook
- Cursor rules: project-wide, agents, database, testing conventions
- Configuration system with YAML agent configs and environment variables
- Structured logging configuration
- Docker and docker-compose templates
- Development lifecycle documentation templates

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)
