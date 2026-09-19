# Reference Versions of the New Pricing Engine

These are two finished versions of `shipbill/pricing_v2.py` from [Demo 4](../04-strangler-fig/README.md), for comparing with the one Copilot writes for you. They live here, outside the demo folder, so Copilot can't find them while it's working on the demo.

| File | What it shows |
|------|---------------|
| `pricing_v2_first_draft.py` | A typical first attempt: typed, data-driven, and exact `Decimal` arithmetic throughout. The parallel run finds it disagrees with the legacy code on 15 of 272 shipments, each by one cent. |
| `pricing_v2.py` | The final version. It keeps the legacy cents in one function, `legacy_compatible_amount`, until accounting agrees to exact rounding, and the parallel run shows all 272 shipments agree. |

To try either one, run these from the `demos/04-strangler-fig` folder. Copy the first draft:

```
cp ../reference/pricing_v2_first_draft.py shipbill/pricing_v2.py
```

Or copy the final version:

```
cp ../reference/pricing_v2.py shipbill/pricing_v2.py
```

Then run the comparison:

```
uv run parallel_run.py
```
