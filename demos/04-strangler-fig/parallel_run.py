"""Price every shipment with both engines and report where they disagree.

This is the evidence a service needs before it moves to the new engine. It reads
every shipment in the sample database, prices each one with the legacy code and
with pricing_v2, and compares the lines to the cent. Nothing is billed or saved.

    uv run parallel_run.py
"""

import sys
from collections import Counter
from decimal import Decimal

import sample_data
from shipbill import db, pricing, settings

SHOW = 10  # mismatches to print in full; the summary counts all of them


def legacy_lines(shipment):
    return [(sid, desc, Decimal(str(amount))) for sid, desc, amount in pricing.price_shipment(shipment)]


def v2_lines(shipment, pricing_v2):
    return [(line.shipment_id, line.description, line.amount)
            for line in pricing_v2.price_shipment(shipment)]


def main() -> int:
    try:
        from shipbill import pricing_v2
    except ImportError:
        print("shipbill/pricing_v2.py doesn't exist yet. Write it first, then run this again.")
        return 2

    sample_data.ensure_database(settings.DB_PATH)
    shipments = db.query("SELECT * FROM shipments ORDER BY id")

    compared, mismatched, examples = Counter(), Counter(), []
    for s in shipments:
        compared[s["service"]] += 1
        old, new = legacy_lines(s), v2_lines(s, pricing_v2)
        if old != new:
            mismatched[s["service"]] += 1
            examples.append((s, old, new))

    print(f"{'service':<8} {'compared':>9} {'agree':>7} {'disagree':>9}")
    for service in sorted(compared):
        n, bad = compared[service], mismatched[service]
        print(f"{service:<8} {n:>9} {n - bad:>7} {bad:>9}")

    for s, old, new in examples[:SHOW]:
        print(f"\nshipment {s['id']}  {s['service']} {s['status']}  "
              f"{s['weight_kg']} kg  {s['length_cm']:g}x{s['width_cm']:g}x{s['height_cm']:g} cm  "
              f"to {s['dest_postcode']}")
        print(f"  legacy: {[(d, str(a)) for _, d, a in old]}")
        print(f"  v2:     {[(d, str(a)) for _, d, a in new]}")
    if len(examples) > SHOW:
        print(f"\n...and {len(examples) - SHOW} more")

    total = sum(compared.values())
    print(f"\n{total - len(examples)} of {total} shipments agree.")
    return 1 if examples else 0


if __name__ == "__main__":
    sys.exit(main())
