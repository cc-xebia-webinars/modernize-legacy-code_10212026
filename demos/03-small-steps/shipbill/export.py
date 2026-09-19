# LedgerLink export
#
# Accounting imports this file every month. The format is fixed by LedgerLink:
# 80 character records, CRLF line endings, amounts in cents, zero padded.
# Header, one detail record per invoice, trailer with a count and hash total.
# If the import fails, nobody gets paid. Talk to accounting before changing it.

import os

from shipbill import dates, db, settings, util


def write_ledger_file(period, invoice_ids):
    if not os.path.exists(settings.OUT_DIR):
        os.makedirs(settings.OUT_DIR)
    path = os.path.join(settings.OUT_DIR, "LEDGER_%s.TXT" % period.replace("-", ""))
    f = open(path, "w", newline="")  # we write the CRLF ourselves
    end = dates.period_end(period)
    f.write(("H" + "SHIPBILL" + period.replace("-", "") + "%010d" % dates.batch_stamp(end)).ljust(80) + "\r\n")
    count = 0
    hash_total = 0
    for inv_id in invoice_ids:
        inv = db.get_invoice(inv_id)
        cust = db.get_customer(inv["cust_id"])
        name = cust["name"].upper()[:20].ljust(20)
        inv_date = dates.fmt_ymd(dates.parse_shipped(inv["inv_date"]))
        due = dates.fmt_ymd(dates.parse_shipped(inv["due_date"]))
        total = util.cents(inv["total"])
        tax = util.cents(inv["tax"])
        flag = " "
        if cust["tax_exempt"]:
            flag = "X"
        rec = "D%08d%06d%s%s%s%010d%010d%s" % (inv_id, inv["cust_id"], name, inv_date, due, total, tax, flag)
        f.write(rec.ljust(80) + "\r\n")
        count = count + 1
        hash_total = hash_total + total
    f.write(("T%06d%012d" % (count, hash_total)).ljust(80) + "\r\n")
    f.close()
    return path
