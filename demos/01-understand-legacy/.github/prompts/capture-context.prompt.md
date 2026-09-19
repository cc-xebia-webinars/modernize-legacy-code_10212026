---
description: Turn reviewed architecture notes into custom instructions that every Copilot session reads.
agent: agent
---

Read `docs/ARCHITECTURE.md` and draft `.github/copilot-instructions.md` for this repository. Copilot reads that file at the start of every chat, so it should hold only what an assistant needs before it changes this code. Keep it under 60 lines.

Include these sections:

1. **What this system is.** One short paragraph. End it by saying that `README.md` in this folder is the walkthrough for the people running the demo, not documentation of ShipBill, so Copilot shouldn't use it as a source.
2. **How to run it.** The exact `uv` commands for a billing run and, once they exist, the tests.
3. **Rules that must not change without sign-off.** The business rules and implicit constraints from the architecture notes, one line each, with the `file` they live in.
4. **How we change legacy code.** Preserve behavior unless a person asks for a change. Make one small change at a time and run the tests after each. Don't fix bugs you find along the way; add them to the open questions instead. Never edit an expected value in a characterization test to make a change pass; stop and report the difference.
5. **Hands off.** `shipbill/export.py` writes the LedgerLink file that accounting imports. Don't change it unless a person says the LedgerLink format has changed.

Don't copy the open questions into the instructions. They stay in `docs/ARCHITECTURE.md` until someone answers them.
