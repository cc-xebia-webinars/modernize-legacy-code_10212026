---
description: Conventions for the ShipBill characterization tests.
applyTo: "tests/**/*.py"
---

# Test Conventions

- These are characterization tests. They pin what the code does today, so an expected value comes from running the code, never from what the code "should" return.
- Name each test after the behavior it pins, for example `test_returns_are_billed_at_half_price`.
- Use `pytest.mark.parametrize` for the same rule at several inputs, especially just below, at, and just above a threshold.
- Compare money with `==` against the exact float the legacy code returns, such as `19.92`. Don't use `pytest.approx`, because a one-cent difference is exactly what these tests exist to catch.
- Use the `billing_db` fixture for anything that reads or writes the database. Don't open your own connection or touch `data/shipbill.db`.
- The files in `tests/approved` are the golden master. Only a person updates them, by reviewing `tests/received` and running `uv run approve.py`.
