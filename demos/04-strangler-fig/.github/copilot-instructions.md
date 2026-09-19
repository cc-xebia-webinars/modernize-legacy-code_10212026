# Working in the ShipBill Codebase

ShipBill is a legacy billing system for a regional courier, written around 2012 and now running on Python 3.14. Each month it prices shipments, stores invoices in SQLite, and writes a fixed-width file that accounting imports into LedgerLink. `docs/ARCHITECTURE.md` describes how it works and lists the questions nobody has answered yet. `README.md` in this folder is the walkthrough for the people running the demo, not documentation of ShipBill, so don't use it as a source.

## How to run it

- Billing run: `uv run run_billing.py 2026-09`. Add a customer number, such as `1047`, to print that customer's invoice.
- Tests: `uv run pytest`.
- Rebuild the sample database: `uv run sample_data.py --reset`.
- Compare the legacy and new pricing engines: `uv run parallel_run.py`.
- Add dependencies with `uv add`, never `pip install`.

## Rules that must not change without sign-off

- Customer 1047 gets 15% off and other key accounts get 10% (`shipbill/billing.py`).
- Fuel is charged on transport after the discount, and a missing month reuses the latest earlier rate (`shipbill/billing.py`).
- Invoices under $25.00 of transport get a minimum charge line. Fuel doesn't count toward it (`shipbill/billing.py`).
- Sales tax never applies to fuel, and tax-exempt customers pay none (`shipbill/billing.py`).
- Amounts are rounded half up to the cent with `util.round2`, and new code must produce the same cents (`shipbill/util.py`).
- Four-digit zips get their leading zero back, and non-numeric postcodes are remote (`shipbill/rates.py`, `shipbill/pricing.py`).
- Unknown service codes are priced as `STD`, returns are half price, and Saturday express pickups add a weekend fee (`shipbill/pricing.py`).
- Invoices are due 30 days after the period ends, moved off weekends (`shipbill/dates.py`).
- Inactive customers aren't billed (`shipbill/db.py`).

## How we change legacy code

- Preserve behavior unless a person asks for a change. A refactor that changes any amount, date, or byte of the export isn't a refactor.
- Make one small change at a time, and run `uv run pytest` after each one.
- Don't fix bugs you find along the way. Add them to the open questions in `docs/ARCHITECTURE.md` and tell me about them.
- Never change an expected value in a characterization test to make a change pass. Stop and show me the difference instead.
- New code gets type hints and docstrings. Comments explain why, not what.

## The pricing rewrite

We're replacing `shipbill/pricing.py` with `shipbill/pricing_v2.py` using the strangler fig pattern. `shipbill/pricing_router.py` decides which engine prices each service.

- Only a person adds a service to `ROUTED_TO_V2`, and only after `uv run parallel_run.py` shows every shipment of that service agrees.
- Change the structure or change the behavior, never both in one step. If the new engine should bill differently, that's a separate, signed-off change with its own entry in `docs/decisions.md`.

## Hands off

`shipbill/export.py` writes the LedgerLink file that accounting imports. Don't change it unless a person says the LedgerLink format has changed.
