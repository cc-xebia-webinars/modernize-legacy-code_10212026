# Decision Log

Every change to how ShipBill behaves, and every deliberate choice to keep a legacy behavior, gets an entry here. Copilot can draft an entry, but a person accepts it. Keep the newest decision at the bottom.

Each entry has a number, a status (proposed, accepted, or replaced), the evidence that prompted it, the decision, and what would make us revisit it.

## D-001: Upgrade arrow from 0.13.2 to 1.4.0

- **Status:** Accepted
- **Evidence:** arrow 0.13.2 printed SyntaxWarnings on Python 3.14, and the code relied on `replace(days=...)`, which 0.13.2 deprecates and 0.14.5 removed, and on the `timestamp` property, which became a method in 1.0. With warnings treated as errors, 32 tests failed.
- **Decision:** Upgrade to arrow 1.4.0 and change `replace(...)` with plural units to `shift(...)` and `timestamp` to `timestamp()` in `shipbill/dates.py`. No other code changed, and every characterization test and golden master file still passes unchanged.
- **Revisit when:** a later arrow release changes date parsing, or we replace arrow with the standard library's `datetime`.
