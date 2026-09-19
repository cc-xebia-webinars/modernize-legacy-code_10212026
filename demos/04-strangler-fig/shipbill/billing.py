from shipbill import dates, db, export, pricing_router, settings, util


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
        for line in pricing_router.price_shipment(s):
            lines.append(line)
            subtotal = subtotal + line[2]

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
