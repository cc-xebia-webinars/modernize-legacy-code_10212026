"""The new pricing engine: the legacy rules, written to be read, tested, and changed.

It keeps the router's contract (see shipbill/pricing_router.py) and bills the same
cents as the legacy code on every shipment in the parallel run. The one place it
deliberately copies a legacy quirk is legacy_compatible_amount, which repeats the
old float arithmetic so that no customer's invoice moves by a cent. Decision D-002,
recorded in docs/decisions.md during the demo, explains why.

Compare it with pricing_v2_first_draft.py, next to this file, which uses exact Decimal
arithmetic throughout and disagrees with the legacy code on 15 shipments.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from shipbill import dates

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


def legacy_compatible_amount(service: str, zone: int, weight: Decimal,
                             factor: Decimal = Decimal(1)) -> Decimal:
    """Price a shipment exactly the way the legacy code did, in floats, to the cent.

    Exact arithmetic says an ECO parcel to zone 4 at 9.5 kg costs 15.025, which rounds
    to 15.03. The legacy float math gets 15.024999... and bills 15.02, and that's what
    customers have paid for years. Until accounting agrees to the change (D-002),
    the new engine repeats the float steps in the same order and rounds them the
    same way, half up on the float.
    """
    base, per_kg = RATE_CARD.get(service, RATE_CARD[FALLBACK_SERVICE])[zone]
    amount = float(base) if weight <= 1 else float(base) + float(per_kg) * (float(weight) - 1)
    if factor != 1:
        amount = amount * float(factor)
    return Decimal(int(amount * 100 + 0.5)) / 100


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

    if shipment["status"] == "RETURNED":
        amount = legacy_compatible_amount(shipment["service"], zone, weight, RETURN_FACTOR)
        lines = [PricedLine(sid, f"RETURN {sid}", amount)]
    else:
        amount = legacy_compatible_amount(shipment["service"], zone, weight)
        desc = f"SHIP {sid} {shipment['service']} Z{zone} {weight:.1f}KG"
        lines = [PricedLine(sid, desc, amount)]

    if remote:
        lines.append(PricedLine(sid, "REMOTE AREA", REMOTE_FEE))
    if (shipment["service"] == "EXP" and shipment["status"] != "RETURNED"
            and dates.is_saturday(dates.parse_shipped(shipment["shipped"]))):
        lines.append(PricedLine(sid, "WEEKEND PICKUP", WEEKEND_FEE))
    return lines
