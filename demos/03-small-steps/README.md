# Demo 3: Modernize in Small Steps

With a safety net in place, ShipBill can finally change. In this demo you'll make two changes with Copilot, each one small enough to review and each one proved by the tests before moving on. The first is a targeted refactor that pulls per-shipment pricing out of the 80-line `calc_invoice`. The second is a dependency upgrade, from a 2019 release of `arrow` to 1.4.0.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/copilot/setup)

Open this folder as its own VS Code window, then open a terminal in it and install the dependencies:

```
uv sync
```

Use the **Local** session target in the Chat view.

## What's in This Folder

| File | Purpose |
|------|---------|
| `shipbill/`, `run_billing.py` | The legacy code, still unchanged |
| `tests/` | The full characterization suite: 72 tests, including the golden master |
| `tests/approved/` | The approved golden master files from Demo 2 |
| `.github/copilot-instructions.md` | The custom instructions from Demo 1 |
| `.github/prompts/refactor-step.prompt.md` | A prompt file for one behavior-preserving refactoring step |
| `.github/prompts/upgrade-dependency.prompt.md` | A prompt file for finishing a dependency upgrade |

## Presentation Trail

### Part 1: Check the net

#### Step 1: Run the suite

```
uv run pytest
```

All 72 tests pass. Scroll up to the warnings summary. It holds a `DeprecationWarning` from `arrow` that says `replace()` with plural properties is deprecated and to use `shift()` instead, and the first time you run the tests it also holds SyntaxWarnings from `arrow`'s parser. A warnings summary is a to-do list that most teams scroll past. We'll come back to it in Part 3.

#### Step 2: See what the suite covers

```
uv run pytest --cov --cov-report=term-missing
```

92% overall, and 100% of `rates.py`, `dates.py`, and `export.py`. What's missing is dead code and debug printing, which is fine. Open `tests/test_billing.py` and skim the names, such as `test_fuel_does_not_count_toward_the_minimum`. Each one is a rule we can't break by accident.

### Part 2: A targeted refactor

#### Step 3: Find the seam inside calc_invoice

Open `shipbill/billing.py`. The `for s in ships:` loop inside `calc_invoice` prices one shipment at a time: zone, chargeable weight, base charge, the return and weekend rules, and rounding. Everything after the loop works on the whole invoice. That boundary is where the function wants to split, and pulling the loop body out into its own function makes the pricing rules testable on their own and, in Demo 4, replaceable.

#### Step 4: Plan the change first

Pick the **Plan** role and send:

```text
Plan how to extract the per-shipment pricing in the loop inside calc_invoice (shipbill/billing.py) into a function price_shipment(shipment) in a new module, shipbill/pricing.py. It should return the same (shipment id, description, amount) lines in the same order. calc_invoice keeps its signature and its behavior. Don't change anything yet.
```

Read the plan before you approve anything. Good signs: it keeps the float arithmetic as it is, it adds each line to `subtotal` in the same order as before, and it keeps the `KeyError` fallback for old service codes. A plan that offers to switch to `Decimal` or tidy up the rules along the way is mixing a refactor with a behavior change. Push back on it.

#### Step 5: Make the change in one step

Open `.github/prompts/refactor-step.prompt.md`. It tells Copilot to run the tests before and after, change nothing but the structure, leave the tests alone, and undo the change if anything fails rather than adjusting the code until it passes.

Switch to the **Agent** role and send:

```text
/refactor-step Extract the per-shipment pricing from calc_invoice into price_shipment in shipbill/pricing.py, following the plan above.
```

Allow the `uv run pytest` commands when Copilot asks. When it's done, review the edits in the chat before you keep them: a new `shipbill/pricing.py`, and a loop in `calc_invoice` that's now three or four lines long.

#### Step 6: Check it yourself

```
uv run pytest
```

Then run the billing month:

```
uv run run_billing.py 2026-09
```

All 72 tests pass, and the total is still 3348.55. Because the golden master compares the LedgerLink file byte for byte, a passing suite means the refactor didn't move a single cent.

### Part 3: A dependency upgrade

#### Step 7: Turn the warnings into failures

```
uv run pytest -W error::DeprecationWarning
```

32 tests fail, because every path through a due date or a period end uses the deprecated plural form of `arrow`'s `replace()`. That's the list of places an upgrade will hit.

#### Step 8: Upgrade arrow

```
uv add arrow==1.4.0
```

`uv add` updates both `pyproject.toml` and `uv.lock`, so the upgrade is one reviewable change. Run the tests:

```
uv run pytest
```

The same 32 tests fail, now with `ValueError: Unknown attribute: 'months'`. The plural form of `replace()` that 0.13.2 warned about was removed in arrow 0.14.5, so every release since then rejects it.

#### Step 9: Let Copilot finish the upgrade

Open `.github/prompts/upgrade-dependency.prompt.md`. It asks Copilot to group the failures by cause, name the arrow release behind each one, make the smallest fix, and finish with deprecation warnings turned into errors. With the **Agent** role, send:

```text
/upgrade-dependency arrow 0.13.2 to 1.4.0
```

There are two causes, and the second one hides behind the first. Once `replace(months=...)` and `replace(days=...)` become `shift(...)` in `shipbill/dates.py`, eight tests still fail, because `timestamp` became a method in arrow 1.0 and `int(d.timestamp)` no longer works. Copilot may spot both from the changelog, or only find the second when it reruns the tests. Either way, a good run changes five lines in `dates.py`, updates the arrow entry in `docs/ARCHITECTURE.md`, and touches nothing else.

#### Step 10: Prove nothing moved

```
uv run pytest -W error::DeprecationWarning
```

All 72 tests pass, with no warnings at all. The approved LedgerLink files still match byte for byte, including the batch stamp built from `timestamp()`, so accounting's import won't notice that anything happened.

Demo 4 starts from this point, with both changes already made: [`shipbill/pricing.py`](../04-strangler-fig/shipbill/pricing.py) and the upgraded [`shipbill/dates.py`](../04-strangler-fig/shipbill/dates.py).

## What You Saw

- A refactor changes structure, never behavior, and the tests are how you know which one you did.
- Plan first, then make one step at a time with the tests run before and after.
- A dependency's deprecation warnings are an upgrade plan you already have.
- Failing tests, grouped by cause, give Copilot exactly the context it needs to finish an upgrade.
