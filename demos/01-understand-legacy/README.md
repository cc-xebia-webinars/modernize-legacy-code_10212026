# Demo 1: Read Before You Change

ShipBill is the monthly billing system for a regional courier. It was written around 2012, the people who built it have moved on, and the only documentation is a text file that's years out of date. In this demo you'll use GitHub Copilot to map the system, trace how one invoice total is calculated, and write down what you learn, checking the AI's claims against the code as you go. Nothing in this demo changes the code.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later. It installs Python 3.14 for you if you don't have it.
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/copilot/setup).

Open this folder as its own VS Code window, then open a terminal in it and install the dependencies:

```
uv sync
```

In the Chat view, use the **Local** session target. Each step says which role to pick: **Ask** for questions, **Agent** when Copilot should write files or run commands. The [demos overview](../README.md#make-sure-youre-in-a-local-session) explains how to check that you're in a Local session.

## What's in This Folder

| File | Purpose |
|------|---------|
| `shipbill/` | The legacy billing code |
| `run_billing.py` | The month-end entry point |
| `README.txt` | The only documentation the system came with |
| `tests/test_billing.py` | The only test, skipped since 2017 |
| `sample_data.py` | Builds a sample database that stands in for production |
| `codemap.py` | Maps the code mechanically, so you can check what Copilot tells you |
| `.github/prompts/` | Two prompt files that turn what you learn into documentation and custom instructions |

## Presentation Trail

### Part 1: Meet the system

#### Step 1: Run a billing month

Run September's billing and print one customer's invoice:

```
uv run run_billing.py 2026-09 1047
```

The first run builds the sample database in `data/` and prints a wall of `SyntaxWarning` messages from the `arrow` library. Those come from a 2019 release that predates Python 3.14, and they only appear the first time Python compiles it. Keep that in mind; it's the first sign of tech debt, and Demo 3 deals with it.

The summary line reads `ShipBill: 9 invoices for 2026-09, total billed 3348.55`, and customer 1047's invoice ends with a discount, a fuel surcharge, and sales tax. Open `out/LEDGER_202609.TXT` to see the file accounting imports: fixed-width records with amounts in cents.

#### Step 2: Read the documentation that exists

Open `README.txt`. It says to run `python run_billing.py --month=09 --year=2013`, that the system needs Python 2.7, and that the database is an Access file on a server. None of that is true anymore. In a brownfield codebase, documentation is a claim to check, not a fact, and the same goes for comments.

#### Step 3: Glance at the core

Open `shipbill/billing.py` and scroll through `calc_invoice`. It's about 80 lines that price shipments, apply discounts, fuel and tax, and save to the database, all in one function, with a hard-coded customer number in the middle. Don't try to understand it yet. This is the code Copilot will help us read.

### Part 2: Map it with Copilot

#### Step 4: Ask for the architecture

Pick the **Ask** role and send:

```text
#codebase Using only the Python files in this folder, describe ShipBill's architecture as a table with one row per module: what it's responsible for and what it depends on. Ignore the Markdown files, and treat README.txt as possibly out of date.
```

Telling Copilot to work from the code matters. The Markdown files in this folder are the demo's instructions, and `README.txt` is wrong, so either one would lead the answer astray.

Read the answer critically. A good one names `billing.py` as the center, `db.py` as the shared connection, `rates.py` and `dates.py` as helpers, and `export.py` as the LedgerLink writer. Note whether it mentions `notify.py`, and what it says about it.

#### Step 5: Trace one dependency path

Still in **Ask**, send:

```text
#codebase Trace how the total on customer 1047's September 2026 invoice is calculated, from run_billing.py to the line in the LedgerLink file. Answer as a numbered list of the functions in the order they run, each with its file and line number, and note every constant or condition that changes the amount.
```

Look for the details that matter for any change you'd make later: the hard-coded 15% for customer 1047, fuel charged after the discount, a minimum charge that ignores fuel, sales tax that skips fuel, and the `round2` helper doing the rounding. Check one line number Copilot gives you by opening the file. If it's off, you've learned something about how far to trust the rest.

#### Step 6: Ask what the code can't tell you

```text
#codebase Which rules in ShipBill look deliberate but are never explained? Answer as a short table: the rule, where it is, who in the business you'd ask, and the question you'd ask them.
```

This is the missing context that makes brownfield work hard. Copilot can find the customer 1047 discount, the fuel month that's missing from the table, and the inactive customer whose shipments are never billed, but only a person can tell you whether they're rules or mistakes.

### Part 3: Check the map

#### Step 7: Map the code mechanically

Open `codemap.py`. It parses every file with Python's `ast` module, without running any of them, and reports the import graph, the third-party libraries, functions that nothing calls, module state changed with `global`, and SQL glued together from strings. Run it:

```
uv run codemap.py
```

Compare its output with Copilot's answers:

- **Dead code.** `notify.send_fax` and `billing.recalc_all` are never called. Did Copilot say so, or did it describe faxing as a feature?
- **Global state.** `db.CONN` is one connection shared by everything, which will matter when we write tests in Demo 2.
- **String-built SQL.** Six lines in `db.py` and one in `run_billing.py`.

The point isn't that the script is smarter than Copilot. It's that a claim you can check mechanically should be checked mechanically.

#### Step 8: Check a claim against the code and the output

Copilot probably told you September's fuel rate is 8.4%. Open `shipbill/settings.py` and look at `FUEL_TABLE`: there's no entry for `2026-09`. Now open `fuel_rate` at the top of `shipbill/billing.py`. A missing month quietly reuses the latest earlier one. Customer 1047's invoice from Step 1 confirms it: the shipment lines add up to 688.02, the discount takes off 103.20, and 8.4% of the remaining 584.82 is the 49.12 fuel surcharge you saw.

### Part 4: Write down what you learned

#### Step 9: Generate the architecture notes

Open `.github/prompts/document-legacy.prompt.md`. It's a reusable prompt that asks for seven sections, from purpose to open questions, and it insists on a `file:line` citation for every rule and an **(inferred)** label on anything Copilot didn't read directly.

Pick the **Agent** role, type `/document-legacy` in the chat input, and send it. Copilot reads the code, may ask to run `codemap.py` or a billing run (allow it), and writes `docs/ARCHITECTURE.md`.

#### Step 10: Review the notes

Open `docs/ARCHITECTURE.md`, and pick three rules from the business rules table. For each one, follow the citation and confirm the line says what the table claims. Fix anything that's wrong, either by editing the file or by telling Copilot what to change.

AI-generated documentation is a draft until a person has checked it. Demo 2 starts from a reviewed copy of this file, so you can compare yours with [ours](../02-safety-net/docs/ARCHITECTURE.md).

#### Step 11: Capture the context for every future session

Open `.github/prompts/capture-context.prompt.md`. It turns the architecture notes into `.github/copilot-instructions.md`, the file Copilot reads at the start of every chat in this workspace. With the **Agent** role, type `/capture-context` and send it.

Read the result. It should hold the rules that must not change, how we change legacy code (small steps, preserve behavior, never edit a test to make it pass), and a warning to leave `shipbill/export.py` alone. From now on, every session starts with what this one learned. Compare it with the [reviewed copy](../02-safety-net/.github/copilot-instructions.md) that Demo 2 starts from.

## What You Saw

- Old documentation and comments are claims to check against the code and the running system.
- Copilot can map architecture and trace a calculation quickly, as long as you scope it to the code and ask for evidence.
- Mechanical checks, such as an `ast`-based map, a quick run, or opening the cited line, catch the claims that are wrong.
- What you learn belongs in files: reviewed architecture notes for people, and custom instructions for every future Copilot session.
