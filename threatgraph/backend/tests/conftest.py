"""
Every test in this suite stubs the single seam where the app talks to
CognoDB - `app.db.run_query` - instead of standing up a real database.
That keeps the suite fast and hermetic while still exercising the real
repository, service, and route code above that seam.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


class RunQueryStub:
    """Replaces app.db.run_query. Queue up canned responses with .add(); each
    call to the stub pops the next one, so a test whose code issues N
    queries in sequence just calls .add() N times in the same order.
    """

    def __init__(self):
        self._responses: list[list[dict]] = []
        self.calls: list[tuple[str, dict]] = []

    def add(self, response: list[dict]) -> "RunQueryStub":
        self._responses.append(response)
        return self

    def __call__(self, query: str, parameters: dict | None = None) -> list[dict]:
        self.calls.append((query, parameters or {}))
        if not self._responses:
            raise AssertionError("RunQueryStub called more times than responses were queued")
        return self._responses.pop(0)


@pytest.fixture
def db_stub(monkeypatch):
    stub = RunQueryStub()
    monkeypatch.setattr("app.db.run_query", stub)
    return stub
