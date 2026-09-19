"""Approve the golden master output you've just reviewed.

Moves every file in tests/received into tests/approved. Run it only after you've
read the received files and you're satisfied they show what the system does
today, because from then on the tests treat them as the truth.

    uv run approve.py
"""

import shutil
from pathlib import Path

TESTS = Path(__file__).resolve().parent / "tests"


def main() -> None:
    received = TESTS / "received"
    approved = TESTS / "approved"
    files = sorted(received.glob("*")) if received.exists() else []
    if not files:
        print("Nothing to approve. Run uv run pytest first.")
        return
    approved.mkdir(exist_ok=True)
    for f in files:
        shutil.move(f, approved / f.name)
        print(f"approved {f.name}")


if __name__ == "__main__":
    main()
