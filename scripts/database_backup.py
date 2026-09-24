"""Backup e restore explícitos para os bancos suportados pelo Portal Cerrado."""

import argparse
import os
import sqlite3
import subprocess
from pathlib import Path

from sqlalchemy.engine import make_url


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "sqlite:///data/portal_cerrado.db")
    if not value:
        raise RuntimeError("DATABASE_URL não pode ser vazio")
    return value


def _sqlite_path(database_url: str) -> Path:
    url = make_url(database_url)
    if url.drivername != "sqlite":
        raise ValueError("A URL não é SQLite")
    if url.database in {None, ":memory:"}:
        raise ValueError("SQLite em memória não pode ser copiado")
    return Path(url.database).resolve()


def _backup_sqlite(database_url: str, output: Path) -> None:
    source_path = _sqlite_path(database_url)
    output.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(source_path)
    destination = sqlite3.connect(output)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()


def _restore_sqlite(database_url: str, backup: Path) -> None:
    target_path = _sqlite_path(database_url)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(backup)
    destination = sqlite3.connect(target_path)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()


def _run_postgres(command: list[str]) -> None:
    subprocess.run(command, check=True, env=os.environ.copy())


def backup(database_url: str, output: Path) -> None:
    """Gera um backup sem sobrescrever credenciais ou configurar defaults de produção."""
    if make_url(database_url).drivername == "sqlite":
        _backup_sqlite(database_url, output)
        return
    _run_postgres(["pg_dump", "--format=custom", "--file", str(output), database_url])


def restore(database_url: str, backup_path: Path, confirmed: bool) -> None:
    """Restaura um backup somente após confirmação explícita do operador."""
    if not confirmed:
        raise ValueError("restore exige --confirm porque substitui dados existentes")
    if not backup_path.is_file():
        raise FileNotFoundError(backup_path)
    if make_url(database_url).drivername == "sqlite":
        _restore_sqlite(database_url, backup_path)
        return
    _run_postgres(["pg_restore", "--clean", "--if-exists", "--exit-on-error", "--dbname", database_url, str(backup_path)])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["backup", "restore"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--confirm", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    database_url = _database_url()
    if args.action == "backup":
        if args.output is None:
            raise SystemExit("backup exige --output")
        backup(database_url, args.output)
        return
    if args.input is None:
        raise SystemExit("restore exige --input")
    restore(database_url, args.input, args.confirm)


if __name__ == "__main__":
    main()
