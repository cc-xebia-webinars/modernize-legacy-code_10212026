"""Build the sample ShipBill database for the demos.

ShipBill is a stand-in for a system that would already have years of production
data. This module plays the part of that data, so it's written in today's style
rather than the legacy one. The data is generated from a fixed seed, which keeps
every run, every machine, and every approved test file identical.

    uv run sample_data.py           # build the database if it's missing
    uv run sample_data.py --reset   # throw it away and build it again
"""

import argparse
import random
import sqlite3
from pathlib import Path

DEFAULT_PATH = Path("data") / "shipbill.db"

SCHEMA = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    postcode TEXT,
    account_type TEXT NOT NULL,
    tax_exempt INTEGER NOT NULL,
    active INTEGER NOT NULL,
    created TEXT
);
CREATE TABLE shipments (
    id INTEGER PRIMARY KEY,
    cust_id INTEGER NOT NULL,
    shipped TEXT NOT NULL,
    dest_postcode TEXT,
    weight_kg REAL,
    length_cm REAL,
    width_cm REAL,
    height_cm REAL,
    service TEXT,
    status TEXT
);
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cust_id INTEGER, period TEXT, inv_date TEXT, due_date TEXT,
    subtotal REAL, fuel REAL, discount REAL, tax REAL, total REAL
);
CREATE TABLE invoice_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER, shipment_id INTEGER, description TEXT, amount REAL
);
"""

# (id, name, postcode, account type, tax exempt, active, created, shipments a month)
CUSTOMERS = [
    (1001, "Alder Street Books", "30310", "STD", 0, 1, "03/14/2011", 14),
    (1012, "Bluewater Outfitters", "28202", "KEY", 0, 1, "07/02/2012", 30),
    (1023, "Cedar Hollow Pottery", "37203", "STD", 0, 1, "11/19/2013", 0),
    (1047, "Granite Peak Supply Co", "35203", "KEY", 0, 1, "01/08/2014", 26),
    (1058, "Harborview Community Clinic", "32801", "STD", 1, 1, "05/27/2015", 8),
    (1063, "Juniper Lane Florist", "30501", "STD", 0, 1, "09/09/2016", 10),
    (1071, "Kestrel Bike Works", "29401", "KEY", 0, 1, "02/23/2018", 18),
    (1084, "Lakeside Print Shop", "40202", "STD", 0, 0, "06/11/2019", 6),
    (1090, "Maple and Main Hardware", "31401", "STD", 0, 1, "10/30/2020", 12),
    (1102, "Orchard Valley Farms", "33101", "STD", 1, 1, "04/04/2022", 6),
    (1115, "Pinecrest Pet Supply", "30060", "STD", 0, 1, "08/15/2024", 0),
]

# Mostly ordinary zips, plus the kinds of values a long-lived table collects:
# zips that lost their leading zero in an old import, and Canadian postal codes
# from a short-lived cross-border trial.
DESTINATIONS = [
    "30303", "30309", "35203", "37203", "28202", "29401", "32801", "33101",
    "40202", "46204", "60601", "75201", "80202", "85004", "94103", "98101",
    "10001", "19103", "02134", "07030", "2134", "7030",
]

# Hand-picked shipments that make sure every rule in the billing code is exercised
# in September, rather than leaving it to the random generator.
# (customer, shipped, destination, kg, length, width, height, service, status)
FIXED_SHIPMENTS = [
    (1023, "09/03/2026 10:15", "37203", 1.2, 20, 15, 10, "ECO", "DELIVERED"),
    (1023, "09/17/2026 14:40", "30303", 0.8, 25, 20, 8, "STD", "DELIVERED"),
    (1063, "09/12/2026 09:05", "28202", 2.4, 30, 25, 20, "EXP", "DELIVERED"),
    (1071, "09/19/2026 11:30", "60601", 4.0, 40, 30, 30, "EXP", "DELIVERED"),
    (1071, "09/26/2026 08:20", "46204", 1.0, 20, 20, 20, "EXP", "RETURNED"),
    (1001, "09/08/2026 13:10", "K1A 0B1", 3.1, 35, 25, 15, "STD", "DELIVERED"),
    (1012, "09/22/2026 16:45", "V6B 1A1", 6.5, 50, 40, 30, "ECO", "DELIVERED"),
    (1090, "09/15/2026 12:00", "2134", 2.0, 30, 20, 15, "STD", "DELIVERED"),
    (1090, "09/24/2026 15:30", "19103", 5.5, 45, 35, 25, "OVN", "DELIVERED"),
    (1047, "09/10/2026 10:00", "94103", 18.0, 60, 40, 40, "STD", "DELIVERED"),
    (1084, "09/16/2026 09:45", "40202", 2.2, 25, 20, 15, "STD", "DELIVERED"),
    (1115, "09/09/2026 11:11", "30060", 1.5, 20, 15, 10, "ECO", "CANCELLED"),
]

SERVICES = ["ECO"] * 35 + ["STD"] * 45 + ["EXP"] * 17 + ["OVN"] * 3
STATUSES = ["DELIVERED"] * 87 + ["RETURNED"] * 8 + ["CANCELLED"] * 5
PERIODS = [(2026, 8, 31), (2026, 9, 30)]


def _random_shipments(rng: random.Random) -> list[tuple]:
    rows = []
    for year, month, days in PERIODS:
        for cust_id, *_, volume in CUSTOMERS:
            for _ in range(volume):
                shipped = (f"{month:02d}/{rng.randint(1, days):02d}/{year} "
                           f"{rng.randint(7, 18):02d}:{rng.randint(0, 59):02d}")
                rows.append((
                    cust_id, shipped, rng.choice(DESTINATIONS),
                    round(rng.uniform(0.2, 25.0), 2),
                    rng.randint(10, 80), rng.randint(10, 60), rng.randint(5, 50),
                    rng.choice(SERVICES), rng.choice(STATUSES),
                ))
    return rows


def populate(conn: sqlite3.Connection) -> None:
    """Create the tables and load the sample data into an open, empty database."""
    # A fixed seed means the September invoices come out the same on every machine.
    rng = random.Random(2026)
    shipments = _random_shipments(rng) + FIXED_SHIPMENTS
    shipments.sort(key=lambda r: (r[1][6:10], r[1][0:2], r[1][3:5], r[1][11:], r[0]))
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)",
                     [c[:7] for c in CUSTOMERS])
    conn.executemany(
        "INSERT INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(50001 + i, *row) for i, row in enumerate(shipments)],
    )
    conn.commit()


def build_database(path: str | Path = DEFAULT_PATH) -> Path:
    """Create a fresh database at path, replacing any file that's already there."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    try:
        populate(conn)
    finally:
        conn.close()
    return path


def ensure_database(path: str | Path = DEFAULT_PATH) -> Path:
    """Build the database only if it doesn't exist, so billing runs keep their history."""
    path = Path(path)
    if not path.exists():
        build_database(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the sample ShipBill database.")
    parser.add_argument("--reset", action="store_true", help="rebuild it from scratch")
    args = parser.parse_args()
    path = build_database() if args.reset else ensure_database()
    with sqlite3.connect(path) as conn:
        customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        shipments = conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
    conn.close()
    print(f"{path}: {customers} customers, {shipments} shipments")


if __name__ == "__main__":
    main()
