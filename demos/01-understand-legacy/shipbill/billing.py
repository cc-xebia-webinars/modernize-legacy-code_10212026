from shipbill import dates, db, export, rates, settings, util


def fuel_rate(period):
    if period in settings.FUEL_TABLE:
        return settings.FUEL_TABLE[period]
    # ops is late with the number sometimes, use the last one we have
    last = 0.0
    for k in sorted(settings.FUEL_TABLE.keys()):
        if k < period:
            last = settings.FUEL_TABLE[k]
    return last


def calc_invoice(cust_id, period):
    cust = db.get_customer(cust_id)
    if cust is None:
        print("WARNING: no customer %s" % cust_id)
        return None
    ships = db.get_shipments(cust_id, period)
    lines = []
    subtotal = 0.0
    for s in ships:
        if s["status"] == "CANCELLED":
            continue
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
        amt = util.round2(amt)
        lines.append((s["id"], desc, amt))
        subtotal = subtotal + amt
        if remote:
            lines.append((s["id"], "REMOTE AREA", settings.REMOTE_FEE))
            subtotal = subtotal + settings.REMOTE_FEE
        if s["service"] == "EXP" and s["status"] != "RETURNED":
            if dates.is_saturday(dates.parse_shipped(s["shipped"])):
                lines.append((s["id"], "WEEKEND PICKUP", settings.WEEKEND_FEE))
                subtotal = subtotal + settings.WEEKEND_FEE

    if len(lines) == 0:
        return None  # nothing to bill this month

    subtotal = util.round2(subtotal)

    # discounts
    disc = 0.0
    if cust_id == 1047:
        # contract renegotiated 2014, DM says do not touch
        disc = util.round2(subtotal * 0.15)
    elif cust["account_type"] == "KEY":
        disc = util.round2(subtotal * settings.KEY_ACCOUNT_DISCOUNT)
    if disc > 0:
        lines.append((None, "DISCOUNT", -disc))
    net = util.round2(subtotal - disc)

    # fuel goes on the transport after discount
    fuel = util.round2(net * fuel_rate(period))
    if fuel > 0:
        lines.append((None, "FUEL SURCHARGE", fuel))

    if net < settings.MIN_CHARGE:
        top = util.round2(settings.MIN_CHARGE - net)
        lines.append((None, "MINIMUM CHARGE", top))
        net = net + top

    tax = 0.0
    if not cust["tax_exempt"]:
        # fuel is not taxable in this state, see memo from accounting 2013
        tax = util.round2(net * settings.TAX_RATE)
        lines.append((None, "SALES TAX", tax))

    total = util.round2(net + fuel + tax)

    inv_date = dates.period_end(period)
    due = dates.due_date(inv_date)
    inv_id = db.save_invoice(cust_id, period, dates.fmt_legacy(inv_date), dates.fmt_legacy(due),
                             subtotal, fuel, disc, tax, total)
    for l in lines:
        db.save_line(inv_id, l[0], l[1], l[2])
    if settings.DEBUG:
        print("invoice %d for %d total %s" % (inv_id, cust_id, util.money(total)))
    return inv_id


def run_billing(period):
    db.delete_period(period)
    ids = []
    for c in db.get_active_customers(period):
        inv = calc_invoice(c["id"], period)
        if inv:
            ids.append(inv)
    path = export.write_ledger_file(period, ids)
    return ids, path


def recalc_all(periods=[]):
    # used for the 2019 rate correction, keep in case they ask again
    for p in periods:
        run_billing(p)
