---
description: The LedgerLink export is a contract with accounting's import, and it's frozen.
applyTo: "shipbill/export.py"
---

# The LedgerLink Export Is Frozen

`shipbill/export.py` writes the file that accounting imports into LedgerLink every month. Its layout, padding, line endings, and rounding are a contract with that import, and if the import rejects the file, invoices don't go out.

- Don't modernize, refactor, reformat, or "clean up" this file, even when the change looks harmless. Old-style string formatting, `open` without `with`, and `os.path` are fine here.
- If someone asks you to change it, explain the risk first and ask whether the LedgerLink format itself has changed. Only go ahead if they say it has, or if they confirm they want the change anyway.
- If you do change it, run `uv run pytest tests/test_golden_master.py` before you say you're done. The approved ledger files must still match byte for byte.
