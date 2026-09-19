# Demo Instructions for This Webinar

The general rules for demos, including folder naming, `uv` setup, the README structure, and the writing style, are in the `CLAUDE.md` file at the root of the repo. This file adds what's specific to this webinar.

## Tools

- The AI tool is GitHub Copilot in Visual Studio Code, used from the Chat view with the **Local** session target. Use the **Ask** role for exploring code, **Plan** for planning a change, and **Agent** for making one. Only Local sessions load prompt files, so every demo assumes Local.
- Each demo carries its own Copilot context in a `.github` folder: `copilot-instructions.md` for the whole workspace, `instructions/*.instructions.md` scoped with `applyTo`, and `prompts/*.prompt.md` for reusable workflows. Prompt files use the `description`, `agent`, and `argument-hint` front matter keys. Have students open each demo folder as its own VS Code workspace, so Copilot reads that demo's `.github` folder and nothing else.
- Python 3.14 for everything. Each demo pins it in its `pyproject.toml` (`requires-python = "==3.14.*"`) and `.python-version` file, and sets `package = false` so the legacy code runs in place.
- Tests use `pytest` and `pytest-cov` in a `dev` dependency group, pinned to exact versions.
- The legacy dependency is `arrow`, pinned to 0.13.2 in Demos 1 to 3, so that Demo 3 can upgrade it to 1.4.0. Version 0.13.2 prints SyntaxWarnings on Python 3.14, and ShipBill relies on its plural `replace()` (removed in 0.14.5) and its `timestamp` property (a method since 1.0); that's deliberate.

## The Legacy Codebase

Every demo works on ShipBill, a small courier billing system written in a 2012 style: a god function, a global connection, string-built SQL, float money, hard-coded customer rules, dead code, and an out-of-date `README.txt`. Keep that style in the `shipbill` package and in `run_billing.py`. The supporting code we wrote for the demos (`sample_data.py`, `codemap.py`, `approve.py`, `parallel_run.py`, the tests, and `demos/reference/`) is modern Python with comments that explain why.

Each demo folder holds its own copy of ShipBill at the state the previous demo leaves it in:

| Demo | Starts with |
|------|-------------|
| 1 | The legacy code and one test that's been skipped since 2017 |
| 2 | Demo 1's reviewed `docs/ARCHITECTURE.md` and `.github/copilot-instructions.md`, a test fixture, and a golden master test with nothing approved yet |
| 3 | A full characterization suite and the approved golden master files |
| 4 | Demo 3's refactor (`shipbill/pricing.py`) and the arrow 1.4.0 upgrade, plus the strangler fig router and the parallel run |

A change to ShipBill or its sample data has to be carried forward through every later demo. When a change alters billing output on purpose, regenerate the approved files in `tests/approved` for Demos 3 and 4, update the line numbers cited in each `docs/ARCHITECTURE.md`, and check the counts the READMEs quote, such as the 72 tests and the 15 shipments the first draft disagrees on.

Keep anything that answers a demo's exercise outside that demo's folder. Copilot's agent searches the whole workspace, so Demo 4's finished pricing engines live in `demos/reference/`, and each `copilot-instructions.md` tells Copilot that the demo's `README.md` is a walkthrough for people, not documentation of ShipBill.

The sample data comes from a fixed random seed, so every machine produces the same invoices. The golden master files are compared byte for byte, and the repo's `.gitattributes` stops git from changing their line endings.

## Outside Services

GitHub Copilot is the only service a demo may use beyond the presenter's machine. Everything else, including the database, runs locally and offline once `uv sync` has run.

## Coverage

Between them, the demos cover the agenda in the repo `README.md`:

- **Why brownfield is harder.** Demo 1 shows missing context (an outdated README, unexplained hard-coded rules), implicit constraints (the LedgerLink file format), and tech debt, and every later demo runs into at least one of them.
- **Understanding unfamiliar code.** Demo 1: mapping the architecture, tracing a dependency path, generating documentation with evidence, checking the AI's claims with `codemap.py`, and capturing what we learned as custom instructions.
- **A safety net first.** Demo 2: a golden master, characterization tests written with Copilot, and coverage used to find gaps rather than as a target.
- **Incremental modernization.** Demo 3: a targeted refactor and a dependency upgrade, each in small steps under green tests. Demo 4: the strangler fig.
- **Preserving behavior through a rewrite.** Demo 4: the new pricing engine, the parallel run that catches a one-cent rounding difference, and the decision to keep the legacy behavior for now.
- **Knowing the limits.** Demo 4: when the parallel run says to intervene, and why `shipbill/export.py` is left alone. The approval prompts and "don't change the tests" rules in every demo show where people stay in the loop.
