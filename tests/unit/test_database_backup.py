import sqlite3
from pathlib import Path

import pytest

from scripts.database_backup import backup, restore


def _create_database(path: Path, value: str) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE records (value TEXT NOT NULL)")
        connection.execute("INSERT INTO records (value) VALUES (?)", (value,))
        connection.commit()
    finally:
        connection.close()


def _read_value(path: Path) -> str:
    connection = sqlite3.connect(path)
    try:
        row = connection.execute("SELECT value FROM records").fetchone()
        assert row is not None
        return str(row[0])
    finally:
        connection.close()


def test_sqlite_backup_and_restore_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    backup_path = tmp_path / "backup.db"
    _create_database(source, "before")

    backup(f"sqlite:///{source}", backup_path)
    source.unlink()
    restore(f"sqlite:///{source}", backup_path, confirmed=True)

    assert _read_value(source) == "before"


def test_restore_requires_explicit_confirmation(tmp_path: Path) -> None:
    backup_path = tmp_path / "backup.db"
    _create_database(backup_path, "before")

    with pytest.raises(ValueError, match="--confirm"):
        restore(f"sqlite:///{tmp_path / 'target.db'}", backup_path, confirmed=False)
