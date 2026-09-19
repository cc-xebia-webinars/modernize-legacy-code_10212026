"""Shared fixtures for the ShipBill tests.

ShipBill reads its database path from a module-level setting and keeps one global
connection in db.CONN. Neither was designed for testing, so these fixtures are the
seam: they point the settings at a fresh database and clear the cached connection,
without changing a line of the legacy code.
"""

import itertools

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


@pytest.fixture
def customer(billing_db):
    """Add a customer with no history, so a test controls every shipment it bills."""
    ids = itertools.count(9001)

    def add(account_type="STD", tax_exempt=0, active=1, cust_id=None):
        cust_id = cust_id or next(ids)
        billing_db.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (cust_id, "Test Customer", "30303", account_type, tax_exempt,
                            active, "01/01/2020"))
        return cust_id

    return add


@pytest.fixture
def shipment(billing_db):
    """Add one shipment. The defaults are a 1 kg STD parcel to zone 1 in September."""
    ids = itertools.count(90001)

    def add(cust_id, *, shipped="09/15/2026 10:00", dest="30303", kg=1.0, dims=(10, 10, 10),
            service="STD", status="DELIVERED"):
        ship_id = next(ids)
        billing_db.execute("INSERT INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (ship_id, cust_id, shipped, dest, kg, *dims, service, status))
        return ship_id

    return add


def lines_of(invoice_id):
    """An invoice's lines as (description, amount) pairs, in the order they were added."""
    return [(row["description"], row["amount"]) for row in db.get_lines(invoice_id)]
