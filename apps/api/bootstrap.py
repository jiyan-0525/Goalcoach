"""Database bootstrap that tolerates read-only and ephemeral serverless filesystems.

Locally the application uses the SQLite files in the repository. On Vercel the
project directory is read-only and ``/tmp`` is the only writable location, so both
databases are relocated there. The curriculum database is not tracked in git (it is
ignored by ``*.db``), so it is rebuilt from the tracked SQL dump when missing.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from goalcoach.infrastructure.config import Settings

CONTENT_DUMP_PATH = (
    "data/database1/GoalCoach_HSK1_Learning_DB_Package/data/goalcoach_hsk1_learning_db_sqlite.sql"
)


def prepare_databases(settings: Settings) -> None:
    """Relocate SQLite files to writable storage when running on Vercel."""
    if not os.environ.get("VERCEL"):
        return

    writable_root = Path(os.environ.get("GOALCOACH_WRITABLE_DIR", "/tmp"))
    writable_root.mkdir(parents=True, exist_ok=True)

    learner_database = writable_root / "goalcoach.db"
    content_database = writable_root / "goalcoach_content.db"

    seed_content_database(content_database, Path(CONTENT_DUMP_PATH))

    settings.database_url = f"sqlite:///{learner_database}"
    settings.content_database_url = f"sqlite:///{content_database}"
    settings.learner_database_path = str(learner_database)
    settings.content_database_path = str(content_database)


def seed_content_database(target: Path, dump_path: Path) -> None:
    """Build the curriculum SQLite file from the tracked SQL dump if it is absent."""
    if target.exists():
        return

    if not dump_path.is_file():
        raise FileNotFoundError(f"Curriculum SQL dump not found at {dump_path}")

    staging = target.with_suffix(".db.building")
    staging.unlink(missing_ok=True)

    connection = sqlite3.connect(staging)
    try:
        connection.executescript(dump_path.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()

    os.replace(staging, target)
