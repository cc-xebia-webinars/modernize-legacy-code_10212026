"""The new pricing engine, first draft: exact Decimal arithmetic from end to end.

This is a typical first attempt, and it reads well: typed, data-driven, and free
of floats. It's kept here because the parallel run finds that it doesn't bill the
same cents as the legacy code. Compare it with pricing_v2.py, next to this file.

To try it, run this from the demos/04-strangler-fig folder:

    cp ../reference/pricing_v2_first_draft.py shipbill/pricing_v2.py
    uv run parallel_run.py
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from shipbill import dates

CENT = Decimal("0.01")
VOLUMETRIC_DIVISOR = Decimal(5000)
RETURN_FACTOR = Decimal("0.5")
REMOTE_FEE = Decimal("7.50")
WEEKEND_FEE = Decimal("12.00")
FALLBACK_SERVICE = "STD"
REMOTE_ZONE = 5

# (base price including the first kilo, price per extra kilo) by service and zone.
RATE_CARD: dict[str, dict[int, tuple[Decimal, Decimal]]] = {
    "ECO": {1: (Decimal("4.95"), Decimal("0.65")), 2: (Decimal("5.45"), Decimal("0.75")),
            3: (Decimal("5.95"), Decimal("0.85")), 4: (Decimal("6.95"), Decimal("0.95")),
            5: (Decimal("8.45"), Decimal("1.15"))},
    "STD": {1: (Decimal("6.95"), Decimal("0.85")), 2: (Decimal("7.65"), Decimal("0.95")),
            3: (Decimal("8.45"), Decimal("1.05")), 4: (Decimal("9.95"), Decimal("1.25")),
            5: (Decimal("11.95"), Decimal("1.45"))},
    "EXP": {1: (Decimal("12.95"), Decimal("1.35")), 2: (Decimal("14.45"), Decimal("1.55")),
            3: (Decimal("16.25"), Decimal("1.75")), 4: (Decimal("18.95"), Decimal("1.95")),
            5: (Decimal("22.45"), Decimal("2.35"))},
}

ZONE_BY_FIRST_DIGIT = {"0": 4, "1": 3, "2": 2, "3": 1, "4": 1,
                       "5": 2, "6": 3, "7": 4, "8": 5, "9": 5}


@dataclass(frozen=True)
class PricedLine:
    """One line on an invoice, as the router expects it."""

    shipment_id: int
    description: str
    amount: Decimal


def zone_for(postcode: str) -> int | None:
    """Zone from the first digit of a zip, restoring a lost leading zero. None if unzoned."""
    code = str(postcode).strip()
    if not code.isdigit():
        return None
    return ZONE_BY_FIRST_DIGIT.get(code.zfill(5)[0])


def chargeable_weight(kg: float, length: float, width: float, height: float) -> Decimal:
    """The heavier of actual and volumetric weight, rounded up to the next half kilo."""
    volumetric = Decimal(str(length)) * Decimal(str(width)) * Decimal(str(height)) / VOLUMETRIC_DIVISOR
    weight = max(Decimal(str(kg)), volumetric)
    return Decimal(math.ceil(weight * 2)) / 2


def base_charge(service: str, zone: int, weight: Decimal) -> Decimal:
    """Base price for the first kilo plus the per-kilo rate for the rest."""
    base, per_kg = RATE_CARD.get(service, RATE_CARD[FALLBACK_SERVICE])[zone]
    return base if weight <= 1 else base + per_kg * (weight - 1)


def price_shipment(shipment: Mapping[str, Any]) -> list[PricedLine]:
    """Invoice lines for one shipment, in the same order as the legacy code."""
    if shipment["status"] == "CANCELLED":
        return []
    sid = shipment["id"]
    zone = zone_for(shipment["dest_postcode"])
    remote = zone is None
    zone = REMOTE_ZONE if zone is None else zone
    weight = chargeable_weight(shipment["weight_kg"], shipment["length_cm"],
                               shipment["width_cm"], shipment["height_cm"])
    amount = base_charge(shipment["service"], zone, weight)

    if shipment["status"] == "RETURNED":
        lines = [PricedLine(sid, f"RETURN {sid}", (amount * RETURN_FACTOR).quantize(CENT, ROUND_HALF_UP))]
    else:
        desc = f"SHIP {sid} {shipment['service']} Z{zone} {weight:.1f}KG"
        lines = [PricedLine(sid, desc, amount.quantize(CENT, ROUND_HALF_UP))]

    if remote:
        lines.append(PricedLine(sid, "REMOTE AREA", REMOTE_FEE))
    if (shipment["service"] == "EXP" and shipment["status"] != "RETURNED"
            and dates.is_saturday(dates.parse_shipped(shipment["shipped"]))):
        lines.append(PricedLine(sid, "WEEKEND PICKUP", WEEKEND_FEE))
    return lines
