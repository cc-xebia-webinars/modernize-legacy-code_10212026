# Demo 4: Strangle, Rewrite, and Know When to Stop

ShipBill's pricing rules now live in their own module, which makes them possible to replace. In this demo you'll grow a new pricing engine next to the old one with Copilot, using the strangler fig pattern: a router decides which engine prices each service, and a parallel run compares the two on every shipment before any service moves. Along the way you'll hit a one-cent disagreement that the agent can't settle for you, and a module that's better left alone.

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
| `shipbill/pricing.py` | The legacy per-shipment pricing, extracted in Demo 3 |
| `shipbill/pricing_router.py` | The strangler fig's seam: sends each service to the old or new engine |
| `parallel_run.py` | Prices every shipment with both engines and reports where they disagree |
| `tests/` | The 72 characterization tests and the approved golden master |
| `docs/decisions.md` | The decision log, starting with the arrow upgrade from Demo 3 |
| `.github/prompts/strangle-pricing.prompt.md` | A prompt file for writing the new engine |
| `.github/instructions/ledger-export.instructions.md` | Marks `shipbill/export.py` as frozen |

## Presentation Trail

### Part 1: The seam

#### Step 1: Read the router

Open `shipbill/pricing_router.py`. `ROUTED_TO_V2` is an empty set, so every shipment still goes to the legacy `pricing.price_shipment`. Adding a service code to the set sends that service to the new engine instead, and removing it sends it back. The docstring sets the contract the new engine has to keep: a list of `PricedLine` objects with a `Decimal` amount, which the router converts back to the floats the rest of ShipBill expects.

This is the strangler fig pattern. The new code grows around the old, one slice at a time, until the old code has nothing left to do, so there's never a big switchover.

#### Step 2: See how little the legacy code changed

Open `shipbill/billing.py` and find the loop in `calc_invoice`. It calls `pricing_router.price_shipment` where it used to call `pricing.price_shipment`. That call and its import are the only changes to the legacy code that this whole rewrite needs.

#### Step 3: Read the parallel run

Open `parallel_run.py`. It reads every shipment in the sample database, prices each one with both engines, and compares the lines to the cent, grouped by service. It never bills or saves anything, so it's safe to run as often as you like. Try it now:

```
uv run parallel_run.py
```

It tells you `shipbill/pricing_v2.py` doesn't exist yet.

### Part 2: Grow the new engine

#### Step 4: Ask Copilot for the new engine

Open `.github/prompts/strangle-pricing.prompt.md`. It gives Copilot the contract, our standard for new code (`Decimal` money, type hints, a rate card instead of magic numbers), and three limits: don't change the legacy code or the tests, don't route any service, and explain any disagreement before changing anything.

Pick the **Agent** role and send:

```text
/strangle-pricing
```

Copilot writes `shipbill/pricing_v2.py` and runs the parallel run. Allow the command when it asks.

#### Step 5: Review the new code

Open `shipbill/pricing_v2.py`. Compared with `shipbill/pricing.py`, it should read more like a specification: a rate card table, named constants, small typed functions, and no dependence on the legacy pricing code. Code that reads like its own specification is the real payoff of a rewrite.

#### Step 6: Read the parallel run's verdict

If Copilot didn't show you the summary, run it yourself:

```
uv run parallel_run.py
```

Most first attempts disagree with the legacy code on a handful of shipments, each by exactly one cent. Our first draft disagreed on 15 of 272. If your run comes back clean, look at how your version rounds. Then try our first draft, which lives in the [reference folder](../reference/README.md) outside this workspace, to see the disagreement. Save your own version first:

```
cp shipbill/pricing_v2.py pricing_v2_mine.py
```

Copy in the first draft:

```
cp ../reference/pricing_v2_first_draft.py shipbill/pricing_v2.py
```

Then run the comparison again:

```
uv run parallel_run.py
```

### Part 3: Intervene

#### Step 7: Find out why

Pick a shipment from the output and ask, in the **Ask** role, replacing the shipment number and amounts with the ones you see:

```text
parallel_run.py says shipment 50131 is 19.92 in the legacy code and 19.93 in pricing_v2. Using shipbill/pricing.py, shipbill/util.py, and shipbill/pricing_v2.py, explain exactly where the two calculations part ways.
```

The cause is float arithmetic: the legacy code computes 11.95 + 1.45 × 5.5 in floats, gets 19.924999…, and rounds it down. Exact `Decimal` arithmetic gets 19.925 and rounds it up. The new engine is arguably more correct, and it would still change what customers are billed.

#### Step 8: Decide, and record the decision

This isn't a decision for the agent, or for the developer alone. Accepting the new cents changes invoices, so it needs accounting's sign-off. Keeping the old cents means deliberately copying a quirk. We'll keep them for now, following the rule in `.github/copilot-instructions.md`: change the structure or change the behavior, never both in one step. With the **Agent** role, send:

```text
Add decision D-002 to docs/decisions.md: for now, pricing_v2 bills the same cents as the legacy code, including the float rounding, until accounting signs off on exact rounding. Use the parallel run results as the evidence. Then change pricing_v2 so one clearly named function reproduces the legacy float arithmetic and rounding, and run parallel_run.py again.
```

#### Step 9: Confirm the engines agree

```
uv run parallel_run.py
```

All 272 shipments agree. If yours still disagrees, compare it with [our final version](../reference/pricing_v2.py), which keeps the legacy cents in a single function, `legacy_compatible_amount`. When accounting signs off, that function is the one thing that changes.

### Part 4: Move one service

#### Step 10: Route ECO to the new engine

Open `shipbill/pricing_router.py` and change the empty set to `ROUTED_TO_V2 = {"ECO"}`. Notice that this is a person's change, not Copilot's. Then run the tests:

```
uv run pytest
```

All 72 tests pass, and now they're exercising the new engine for every economy shipment, including the golden master that compares the LedgerLink file byte for byte. Run the billing month too:

```
uv run run_billing.py 2026-09
```

The total is still 3348.55. The next service moves the same way, and once all four are routed, `shipbill/pricing.py` can be deleted.

### Part 5: Know when to stop

#### Step 11: Ask to modernize the export

Open `shipbill/export.py`. It's old-fashioned, with `%` formatting, `os.path`, and a file opened without `with`. With the **Agent** role, send:

```text
Modernize shipbill/export.py with pathlib, f-strings, and a with block.
```

Copilot should push back, because two layers of instructions tell it to. The "Hands off" section of `.github/copilot-instructions.md`, which Copilot reads in every chat, says to leave the file alone. Open `.github/instructions/ledger-export.instructions.md` too: its `applyTo` line attaches it whenever Copilot edits `export.py`, and it says to explain the risk and ask before changing anything. If Copilot goes ahead anyway, run `uv run pytest tests/test_golden_master.py` to check whether a single byte moved.

The code works, it rarely changes, a mistake fails the month-end import, and nothing about it slows anyone down, which makes it a module to leave alone. If the LedgerLink format ever changes, the golden master makes it safe to touch.

## What You Saw

- The strangler fig replaces legacy code one slice at a time behind a seam, with a one-line way back.
- A parallel run on real data is the evidence a slice needs before it moves, and it catches differences that tests written from the old code's rules can miss.
- When the evidence shows a behavior change, a person decides, and the decision gets written down.
- Some legacy code should be left alone, and scoped instructions tell the agent so.
