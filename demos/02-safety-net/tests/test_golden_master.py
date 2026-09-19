"""Golden master tests: run a whole billing month and compare it with approved output.

These tests don't know any of the billing rules. They record what the system
produces today, once a person has reviewed and approved it, and fail if a single
character changes. When one fails, compare the file in tests/received with the
one in tests/approved to see what moved.
"""

from pathlib import Path

import pytest

from shipbill import billing, db, util

HERE = Path(__file__).parent
APPROVED = HERE / "approved"
RECEIVED = HERE / "received"

PERIODS = ["2026-08", "2026-09"]


def invoice_snapshot(invoice_ids):
    """Every invoice and every line, as plain text that's easy to read in a diff."""
    out = []
    for inv_id in invoice_ids:
        inv = db.get_invoice(inv_id)
        out.append(f"INVOICE {inv_id} customer {inv['cust_id']} "
                   f"dated {inv['inv_date']} due {inv['due_date']}")
        for line in db.get_lines(inv_id):
            out.append(f"  {line['description']:<32} {util.money(line['amount']):>10}")
        out.append(f"  {'TOTAL':<32} {util.money(inv['total']):>10}")
    return "\n".join(out) + "\n"


def check_against_approved(name: str, received: bytes) -> None:
    """Fail unless received matches the approved file, leaving a copy to review."""
    approved = APPROVED / name
    if approved.exists() and approved.read_bytes() == received:
        (RECEIVED / name).unlink(missing_ok=True)
        return
    RECEIVED.mkdir(exist_ok=True)
    (RECEIVED / name).write_bytes(received)
    if not approved.exists():
        pytest.fail(f"No approved {name} yet. Review tests/received/{name}, "
                    "then run: uv run approve.py")
    pytest.fail(f"{name} changed. Compare tests/received/{name} with tests/approved/{name}.")


@pytest.mark.parametrize("period", PERIODS)
def test_invoices_match_approved(billing_db, period):
    ids, _ = billing.run_billing(period)
    # Bytes, not text, so a change in line endings or encoding counts as a change.
    check_against_approved(f"invoices_{period}.txt", invoice_snapshot(ids).encode("utf-8"))


@pytest.mark.parametrize("period", PERIODS)
def test_ledger_file_matches_approved(billing_db, period):
    _, path = billing.run_billing(period)
    check_against_approved(Path(path).name, Path(path).read_bytes())
