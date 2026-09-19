"""Price a single shipment.

Extracted from billing.calc_invoice so the per-shipment rules can be read and
tested without a database or a whole billing run. The logic, the float math, and
the order of the lines are unchanged from the original loop.
"""

from shipbill import dates, rates, settings, util


def price_shipment(s):
    """Return the invoice lines for one shipment as (shipment id, description, amount).

    Cancelled shipments get no lines. A remote-area fee and a Saturday express
    fee, when they apply, follow the shipment's own line in that order.
    """
    if s["status"] == "CANCELLED":
        return []
    lines = []
    z = rates.zone_for(s["dest_postcode"])
    remote = False
    if z is None:
        z = 5
        remote = True
    cw = rates.chargeable_weight(s["weight_kg"], s["length_cm"], s["width_cm"], s["height_cm"])
    try:
        amt = rates.base_charge(s["service"], z, cw)
    except KeyError:
        # old service codes from before 2016 (OVN etc), bill them as STD
        amt = rates.base_charge("STD", z, cw)
    if s["status"] == "RETURNED":
        amt = amt * settings.RETURN_RATE
        desc = "RETURN %d" % s["id"]
    else:
        desc = "SHIP %d %s Z%d %.1fKG" % (s["id"], s["service"], z, cw)
    lines.append((s["id"], desc, util.round2(amt)))
    if remote:
        lines.append((s["id"], "REMOTE AREA", settings.REMOTE_FEE))
    if s["service"] == "EXP" and s["status"] != "RETURNED":
        if dates.is_saturday(dates.parse_shipped(s["shipped"])):
            lines.append((s["id"], "WEEKEND PICKUP", settings.WEEKEND_FEE))
    return lines
