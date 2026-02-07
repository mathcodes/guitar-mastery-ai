"""
Database Seed Script — Loads JSON seed data into SQLite.

Usage:
    python -m src.db.seed           # Seed all tables
    python -m src.db.seed --table chords  # Seed specific table
    python -m src.db.seed --reset   # Drop + recreate + seed

Reads JSON files from data/seed/ and inserts them into the
corresponding database tables.
"""

import sys
import json
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select, func
from src.db.connection import async_session, init_db, drop_db
from src.db.models import (
    Chord, Scale, Technique, JazzStandard,
    GuitarHistory, Quiz, Lesson,
)

SEED_DIR = PROJECT_ROOT / "data" / "seed"

# Map JSON filenames to ORM models and their field mappings
SEED_MAP = {
    "chords.json": Chord,
    "scales.json": Scale,
    "techniques.json": Technique,
    "jazz_standards.json": JazzStandard,
    "guitar_history.json": GuitarHistory,
    "quizzes.json": Quiz,
}


async def seed_table(model_class, json_file: Path, force: bool = False) -> int:
    """Load a single JSON seed file into its database table."""
    if not json_file.exists():
        print(f"  [SKIP] {json_file.name} — file not found")
        return 0

    with open(json_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        print(f"  [SKIP] {json_file.name} — empty file")
        return 0

    async with async_session() as session:
        # Check if table already has data
        count_result = await session.execute(
            select(func.count()).select_from(model_class)
        )
        existing_count = count_result.scalar()

        if existing_count > 0 and not force:
            print(f"  [SKIP] {model_class.__tablename__} — already has {existing_count} records (use --force to overwrite)")
            return 0

        # If forcing, we don't delete — just skip duplicates
        inserted = 0
        for record in records:
            try:
                # For quizzes, map question_count from questions list
                if model_class == Quiz and "questions" in record:
                    record["question_count"] = len(record.get("questions", []))

                obj = model_class(**record)
                session.add(obj)
                await session.flush()
                inserted += 1
            except Exception as e:
                await session.rollback()
                # Skip duplicates silently, report other errors
                if "UNIQUE" in str(e).upper():
                    pass
                else:
                    print(f"  [WARN] {model_class.__tablename__}: {e}")

        await session.commit()
        print(f"  [OK]   {model_class.__tablename__} — inserted {inserted} records")
        return inserted


async def seed_practice_routines() -> int:
    """Seed practice routines as lessons."""
    json_file = SEED_DIR / "practice_routines.json"
    if not json_file.exists():
        print(f"  [SKIP] practice_routines.json — file not found")
        return 0

    with open(json_file, "r", encoding="utf-8") as f:
        routines = json.load(f)

    async with async_session() as session:
        count_result = await session.execute(
            select(func.count()).select_from(Lesson)
        )
        if count_result.scalar() > 0:
            print(f"  [SKIP] lessons (practice_routines) — already has data")
            return 0

        inserted = 0
        for routine in routines:
            try:
                lesson = Lesson(
                    title=routine["title"],
                    topic="practice_routine",
                    category="practice",
                    difficulty={"beginner": 1, "intermediate": 2, "advanced": 3, "any": 2}.get(
                        routine.get("skill_level", "intermediate"), 2
                    ),
                    objectives=[f"Complete {routine['total_minutes']}-minute practice session"],
                    steps=[
                        {
                            "type": "exercise",
                            "name": section["name"],
                            "minutes": section["minutes"],
                            "content": section["description"],
                            "goals": section.get("goals", []),
                        }
                        for section in routine.get("sections", [])
                    ],
                    estimated_minutes=routine.get("total_minutes", 30),
                    created_by="jazz_teacher",
                    tags=routine.get("tags", []),
                )
                session.add(lesson)
                await session.flush()
                inserted += 1
            except Exception as e:
                await session.rollback()
                if "UNIQUE" not in str(e).upper():
                    print(f"  [WARN] lessons: {e}")

        await session.commit()
        print(f"  [OK]   lessons (practice_routines) — inserted {inserted} records")
        return inserted


async def seed_all(force: bool = False):
    """Seed all tables from JSON files."""
    print("\n[SEED] Loading seed data into database...\n")

    total = 0
    for json_filename, model_class in SEED_MAP.items():
        json_path = SEED_DIR / json_filename
        count = await seed_table(model_class, json_path, force=force)
        total += count

    # Seed practice routines as lessons
    total += await seed_practice_routines()

    print(f"\n[SEED] Done — {total} total records inserted.\n")
    return total


async def reset_and_seed():
    """Drop all tables, recreate, and seed."""
    print("[SEED] Resetting database...")
    await drop_db()
    await init_db()
    await seed_all(force=True)


# CLI
if __name__ == "__main__":
    if "--reset" in sys.argv:
        asyncio.run(reset_and_seed())
    elif "--table" in sys.argv:
        idx = sys.argv.index("--table")
        if idx + 1 < len(sys.argv):
            table_name = sys.argv[idx + 1]
            json_file = f"{table_name}.json"
            if json_file in SEED_MAP:
                asyncio.run(seed_table(SEED_MAP[json_file], SEED_DIR / json_file, force=True))
            else:
                print(f"Unknown table: {table_name}. Available: {list(SEED_MAP.keys())}")
        else:
            print("Usage: python -m src.db.seed --table <table_name>")
    else:
        asyncio.run(seed_all(force="--force" in sys.argv))
