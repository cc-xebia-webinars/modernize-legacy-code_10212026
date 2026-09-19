# Month end billing run
#
#   uv run run_billing.py 2026-09
#   uv run run_billing.py 2026-09 1047      (also print one customer's invoice)

import sys

import sample_data  # demo only: stands in for the production database
from shipbill import billing, db, settings, util


def show_invoice(cust_id, period):
    rows = db.query("SELECT * FROM invoices WHERE cust_id = %d AND period = '%s'" % (cust_id, period))
    if len(rows) == 0:
        print("no invoice for %d in %s" % (cust_id, period))
        return
    inv = rows[0]
    print("")
    print("Invoice %d  customer %d  period %s  due %s" % (inv["id"], cust_id, period, inv["due_date"]))
    for l in db.get_lines(inv["id"]):
        print("  %-32s %10s" % (l["description"], util.money(l["amount"])))
    print("  %-32s %10s" % ("TOTAL", util.money(inv["total"])))


def main():
    if len(sys.argv) < 2:
        print("usage: run_billing.py YYYY-MM [customer]")
        sys.exit(1)
    period = sys.argv[1]
    sample_data.ensure_database(settings.DB_PATH)
    ids, path = billing.run_billing(period)
    total = 0.0
    for i in ids:
        total = total + db.get_invoice(i)["total"]
    print("ShipBill: %d invoices for %s, total billed %s" % (len(ids), period, util.money(total)))
    print("LedgerLink file: %s" % path)
    if len(sys.argv) > 2:
        show_invoice(int(sys.argv[2]), period)


if __name__ == "__main__":
    main()
