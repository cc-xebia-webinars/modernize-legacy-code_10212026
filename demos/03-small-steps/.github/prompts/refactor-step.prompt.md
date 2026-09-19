---
description: Make one behavior-preserving refactoring step, then prove it with the tests.
agent: agent
argument-hint: The refactoring you want, for example "extract per-shipment pricing from calc_invoice"
---

Make exactly one refactoring step: the one I describe. A refactoring changes how the code is organized, never what it does.

1. Run `uv run pytest` first and confirm everything passes. If anything fails, stop and tell me, because we can't refactor without a working safety net.
2. Tell me in two or three sentences what you'll change and which files you'll touch.
3. Make the change. Keep the legacy logic, the float arithmetic, and the order of operations exactly as they are, even if they look wrong. Moving code is fine; rewriting it isn't part of this step.
4. Don't touch the tests, the files in `tests/approved`, or `shipbill/export.py`.
5. Run `uv run pytest` again. If anything fails, undo your change and explain what the failure told you, rather than adjusting the code until it passes.
6. If the change moved code that `docs/ARCHITECTURE.md` cites, update those citations, so the notes keep matching the code.
7. Summarize the change in one paragraph I could paste into a commit message.
