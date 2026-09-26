"""Contract tests for request-scoped database sessions."""

import pytest


def test_get_db_rolls_back_and_closes_failed_request(monkeypatch):
    from app import database

    class FakeSession:
        def __init__(self):
            self.rolled_back = False
            self.closed = False

        def rollback(self):
            self.rolled_back = True

        def close(self):
            self.closed = True

    session = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: session)
    dependency = database.get_db()
    assert next(dependency) is session

    with pytest.raises(RuntimeError):
        dependency.throw(RuntimeError("commit failed"))

    assert session.rolled_back is True
    assert session.closed is True
