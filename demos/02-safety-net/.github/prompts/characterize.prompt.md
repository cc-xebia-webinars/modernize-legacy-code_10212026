---
description: Write characterization tests that pin what legacy code does today, quirks included.
agent: agent
argument-hint: The module to characterize, for example shipbill/rates.py
---

Write characterization tests for the module I name (default to the file that's open in the editor). A characterization test records what the code does now. It isn't a statement of what the code should do.

1. Read the module and list every behavior that affects an amount, a date, or whether something gets billed. Include the odd ones, such as fallbacks, hard-coded values, and rounding. Keep this first pass to the 10 to 15 behaviors that matter most to what customers are billed, and tell me which ones you left for later.
2. For each behavior, decide on an input that shows it and work out the expected value by running the real code, for example with `uv run python -c "..."`. Don't calculate expected values in your head, and don't "correct" a value that looks wrong.
3. Write the tests in `tests/test_<module>.py`. If that file already exists, add to it and leave the tests already in it alone. Name each test after the behavior it pins, and put a one-line comment on any test that pins a value that looks like a bug, so a reader knows it's deliberate.
4. Use the `billing_db` fixture from `tests/conftest.py` for anything that touches the database. Call pure functions directly.
5. Don't change any code under `shipbill/`. If you think you've found a bug, tell me and add it to the open questions in `docs/ARCHITECTURE.md`.
6. Run `uv run pytest --cov --cov-report=term-missing` and report which lines of the module are still uncovered and why.
