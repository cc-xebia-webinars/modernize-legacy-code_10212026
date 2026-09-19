"""The strangler fig's seam: send each shipment to the legacy pricing or the new engine.

billing.calc_invoice asks this module to price a shipment and never knows which
engine answered. A service moves to the new engine by adding it to ROUTED_TO_V2,
one service at a time, and only once parallel_run.py shows the two engines agree
on every shipment of that service. Moving it back is the same one-line change.

The new engine lives in shipbill/pricing_v2.py and keeps this contract:

    price_shipment(shipment) -> list[PricedLine]

where PricedLine has shipment_id (int), description (str), and amount (Decimal).
The rest of ShipBill still works in floats, so amounts are converted here, at the
boundary, and nowhere else.
"""

from shipbill import pricing

# Services priced by pricing_v2. Empty means the legacy code prices everything.
ROUTED_TO_V2 = set()


def price_shipment(shipment):
    """Price one shipment with whichever engine owns its service."""
    if shipment["service"] not in ROUTED_TO_V2:
        return pricing.price_shipment(shipment)
    # Imported here so ShipBill keeps running before pricing_v2 exists.
    from shipbill import pricing_v2

    return [(line.shipment_id, line.description, float(line.amount))
            for line in pricing_v2.price_shipment(shipment)]
