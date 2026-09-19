# Demo 2: Build the Safety Net

Before anyone changes ShipBill, we need a way to know that a change didn't break it. In this demo you'll build that safety net in two layers. First, a golden master that runs a whole billing month and compares the output with a reviewed copy, byte for byte. Then focused characterization tests, written with Copilot, that pin each rule by name, quirks included. Coverage tells us where the gaps are along the way.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/copilot/setup)

Open this folder as its own VS Code window, then open a terminal in it and install the dependencies, which now include `pytest` and `pytest-cov`:

```
uv sync
```

Use the **Local** session target in the Chat view.

## What's in This Folder

| File | Purpose |
|------|---------|
| `shipbill/`, `run_billing.py` | The legacy code, unchanged from Demo 1 |
| `docs/ARCHITECTURE.md` | The reviewed architecture notes from Demo 1 |
| `.github/copilot-instructions.md` | The reviewed custom instructions from Demo 1 |
| `tests/conftest.py` | A fixture that gives each test its own fresh database |
| `tests/test_golden_master.py` | Runs August and September billing and compares the output with approved files |
| `tests/test_billing.py` | The legacy test, still skipped |
| `approve.py` | Moves reviewed output from `tests/received` to `tests/approved` |
| `.github/prompts/characterize.prompt.md` | A prompt file for writing characterization tests |
| `.github/instructions/tests.instructions.md` | Test conventions that Copilot applies to files in `tests/` |

## Presentation Trail

### Part 1: A golden master

#### Step 1: See how much the existing test protects

Run the one test the system came with, with coverage:

```
uv run pytest tests/test_billing.py --cov
```

One test, skipped, and coverage still reports 18%. That's because importing a module runs its `import` and `def` lines, and coverage counts them. Coverage measures what ran, not what was checked, so treat it as a map of the gaps rather than a score.

#### Step 2: Read the seam in the test fixture

Open `tests/conftest.py`. ShipBill reads its database path from `settings.DB_PATH` and caches one connection in `db.CONN`, and neither was built with tests in mind. The `billing_db` fixture works around both without touching the legacy code: it points the setting at an in-memory database, clears the cached connection, and loads the sample data. A spot like this, where you can change behavior from outside the code, is called a seam, and finding one is often the first job in legacy code.

#### Step 3: Read the golden master test

Open `tests/test_golden_master.py`. Each test runs a whole billing month and checks two things: a readable snapshot of every invoice line, and the LedgerLink file itself, compared as bytes so even a changed line ending counts. `check_against_approved` compares what it got with the file in `tests/approved`. If they differ, or there's no approved file yet, it saves what it got in `tests/received` and fails. Nothing has been approved yet.

#### Step 4: Run it and review the output

```
uv run pytest
```

All four golden master tests fail with a message that there's no approved file yet. Open `tests/received/invoices_2026-09.txt` and `tests/received/LEDGER_202609.TXT`. This is what ShipBill does today, and it matches the billing run from Demo 1. You're not deciding whether it's right. You're confirming it's what the system really produces, because from now on it's the definition of "unchanged." The warnings summary at the bottom of the test output is `arrow` again, and Demo 3 deals with it.

#### Step 5: Approve it

```
uv run approve.py
```

Then run the tests again:

```
uv run pytest
```

All four pass. If any change to ShipBill moves a single character of output, they'll fail.

#### Step 6: Check coverage now

```
uv run pytest --cov --cov-report=term-missing
```

Four tests, and coverage jumps to 88%. That's the strength of a golden master: it's quick to build and covers a lot. The same breadth is its weakness, because a failure tells you something changed but not which rule broke, and the test can't tell you that a branch it happened to run was ever checked. The `Missing` column shows what it never reached, such as the due-date code for weekends.

### Part 2: Focused tests with Copilot

#### Step 7: Read the prompt file and the test conventions

Open `.github/prompts/characterize.prompt.md`. It tells Copilot that a characterization test records what the code does, not what it should do, and that every expected value must come from running the real code rather than from Copilot's own arithmetic. It also says not to change anything under `shipbill/`.

Open `.github/instructions/tests.instructions.md`. The `applyTo` line means Copilot follows these conventions whenever it works on a file in `tests/`. Note the rule against `pytest.approx` for money, because a one-cent difference is exactly what these tests are for.

#### Step 8: Characterize the rates module

Open `shipbill/rates.py`, pick the **Agent** role, and send:

```text
/characterize shipbill/rates.py
```

Watch Copilot run small `uv run python -c` commands to get real values before it writes `tests/test_rates.py`. Allow the terminal commands when it asks. When it's done, read the tests: they should cover the four-digit zips, the non-numeric postcodes, the half-kilo rounding, and volumetric weight, each in a test named after the rule.

#### Step 9: Characterize the billing rules

```text
/characterize shipbill/billing.py
```

This one needs the database, so Copilot should use the `billing_db` fixture. `tests/test_billing.py` already holds the skipped legacy test, so Copilot should add its tests to that file and leave the old one alone. Check three things in what it writes: the customer 1047 discount is pinned with a comment that it's deliberate, the minimum charge is tested with fuel excluded, and nothing in `shipbill/` was changed. If Copilot reports something that looks like a bug, such as the inactive customer who's never billed, it should add it to the open questions in `docs/ARCHITECTURE.md` rather than fixing it.

#### Step 10: Close a gap that coverage found

Run coverage again:

```
uv run pytest --cov --cov-report=term-missing
```

If `shipbill/dates.py` still shows missing lines, they're the weekend branches of `due_date`, which the sample months never reach. Ask Copilot, still in **Agent**:

```text
Add characterization tests for dates.due_date where the due date falls on a Saturday and on a Sunday. Find periods that cause each case by running the code.
```

What's left uncovered afterward is mostly `notify.py`, which Demo 1 showed is dead code, and debug printing. Coverage helped you find the gaps worth closing, and it's fine to leave the rest.

### Part 3: Prove the net catches something

#### Step 11: Break a rule on purpose

Open `shipbill/settings.py` and change `RETURN_RATE = 0.5` to `RETURN_RATE = 0.6`. Then run the tests:

```
uv run pytest
```

The golden master tests fail, which tells you something changed. If Copilot wrote a test for returns in Step 9, it fails too, and its name tells you what changed. That's why you want both layers. Change `RETURN_RATE` back to `0.5` and run `uv run pytest` once more to see everything pass.

Demo 3 starts from our version of the full suite, 72 tests in all, so you can compare it with what Copilot wrote for you in [Demo 3's tests folder](../03-small-steps/tests/).

## What You Saw

- A golden master is the fastest way to pin a whole system's behavior, and a person reviews it once before it becomes the truth.
- Characterization tests pin today's behavior by name, including the quirks, and their expected values come from running the code.
- Prompt files and scoped instructions keep Copilot from "fixing" the code or loosening a test.
- Coverage is a map of what ran, not a measure of what's protected. Use it to find gaps, not as a goal.
