import math

from shipbill import settings


def zone_for(postcode):
    pc = str(postcode).strip()
    if pc.isdigit():
        # the 2014 CSV import stored zips as numbers and lost the leading zero
        pc = pc.zfill(5)
    else:
        return None
    return settings.ZONES.get(pc[:1])


def chargeable_weight(weight, length, width, height):
    vol = (length * width * height) / settings.VOL_DIVISOR
    wt = weight
    if vol > wt:
        wt = vol
    # always round UP to the next half kilo
    return math.ceil(wt * 2) / 2.0


def base_charge(service, zone, cw):
    base, per_kg = settings.RATES[service][zone]
    if cw <= 1:
        return base
    return base + per_kg * (cw - 1)
