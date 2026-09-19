---
description: Fix the code after a dependency upgrade, guided by the failing tests and the library's changelog.
agent: agent
argument-hint: The package and versions, for example "arrow 0.13.2 to 1.4.0"
---

I've just upgraded the dependency I name with `uv add`. Help me finish the upgrade.

1. Run `uv run pytest` and group the failures by cause. Several failures often share one root cause.
2. For each cause, find the call in our code and the change in the library that broke it. Name the release that made the change, and tell me if you're not sure, rather than guessing.
3. Fix our code with the smallest change that restores the old behavior, one cause at a time, and rerun `uv run pytest` after each fix, because one failure can hide another. Don't change what the code does, and don't touch the tests or the files in `tests/approved`.
4. Run `uv run pytest -W error::DeprecationWarning` to make sure nothing still depends on a deprecated call.
5. Update the dependency's entry in `docs/ARCHITECTURE.md` so the notes don't describe the old version.
6. List every line you changed, with the reason for each one.
