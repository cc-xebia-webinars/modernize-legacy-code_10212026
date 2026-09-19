---
description: Draft architecture notes for unfamiliar legacy code, with evidence for every claim.
agent: agent
argument-hint: The package or folder to document, for example shipbill
---

Write `docs/ARCHITECTURE.md` for the code I name (default to the `shipbill` package and `run_billing.py`).

Work only from the Python source. Ignore the Markdown files in this folder, and treat `README.txt` as a claim to check rather than a fact, because it may be out of date. Don't change, fix, or refactor any code. You may run `uv run codemap.py` and `uv run run_billing.py 2026-09` to check what you find.

Use these sections:

1. **Purpose.** Two or three sentences on what the system does and who depends on its output.
2. **How a billing run works.** Numbered steps from `run_billing.py` to the export file, naming the file and function for each step.
3. **Module map.** A table with one row per module: what it's responsible for and what it depends on. Follow it with a Mermaid `graph` of the imports.
4. **Business rules.** A table of every rule that changes an amount or a date: the rule in plain words, where it lives as `file:line`, and the constant or condition that drives it. Keep the order the code applies them in, because the order is part of the rule.
5. **Implicit constraints.** Things outside the code that depend on its exact behavior, and what would break if it changed.
6. **Tech debt and risks.** Global state, string-built SQL, dead code, float money, outdated dependencies, and anything else that would make a change risky.
7. **Open questions.** Things the code can't tell us and a person has to answer. Phrase each one as a question for a named role, such as accounting or operations.

Cite `file:line` for every rule and constraint. When you're inferring something rather than reading it directly from the code, mark it **(inferred)**.
