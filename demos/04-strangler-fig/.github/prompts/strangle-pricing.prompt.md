---
description: Write the new pricing engine behind the strangler fig router, without switching anything over.
agent: agent
---

Write `shipbill/pricing_v2.py`, a new implementation of the per-shipment pricing in `shipbill/pricing.py`.

**The contract.** Follow the docstring in `shipbill/pricing_router.py`. Provide `price_shipment(shipment) -> list[PricedLine]`, where `PricedLine` is a frozen dataclass with `shipment_id: int`, `description: str`, and `amount: Decimal`. The `shipment` argument is a `sqlite3.Row` from the `shipments` table. Return the lines in the same order, with the same descriptions, as the legacy function.

**The standard for new code.** Use `Decimal` for money, type hints on every function, a named constant or a rate-card table instead of magic numbers, and small functions with docstrings. Don't import `shipbill.settings`, `shipbill.rates`, or `shipbill.util`, because the new engine shouldn't depend on the code it's replacing. Importing `shipbill.dates` is fine.

**Limits.**

- Don't change `shipbill/pricing.py`, `shipbill/pricing_router.py`, `shipbill/billing.py`, or any test.
- Don't add anything to `ROUTED_TO_V2`. A person decides when a service moves.
- When you're done, run `uv run parallel_run.py` and show me its summary table. If any shipments disagree, explain the cause before you change anything.
