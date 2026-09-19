"""Shared fixtures for the ShipBill tests.

ShipBill reads its database path from a module-level setting and keeps one global
connection in db.CONN. Neither was designed for testing, so this fixture is the
seam: it points the settings at a fresh database and clears the cached connection,
without changing a line of the legacy code.
"""

import pytest

import sample_data
from shipbill import db, settings


@pytest.fixture
def billing_db(tmp_path, monkeypatch):
    """A freshly seeded database and output folder that only this test can see."""
    # In memory, because the legacy code commits after every insert, and on disk
    # that makes a single billing run take seconds instead of milliseconds.
    monkeypatch.setattr(settings, "DB_PATH", ":memory:")
    monkeypatch.setattr(settings, "OUT_DIR", str(tmp_path / "out"))
    monkeypatch.setattr(db, "CONN", None)
    conn = db.get_conn()
    sample_data.populate(conn)
    yield conn
    conn.close()
