# Fax invoices to customers who asked for it. Gateway was MegaFax, they shut
# down in 2018 I think? leaving this here until someone confirms - JK

import socket

from shipbill import db, util

FAX_GATEWAY = ("fax.megafax.example", 4559)


def send_fax(invoice_id):
    inv = db.get_invoice(invoice_id)
    body = "INVOICE %d TOTAL %s" % (invoice_id, util.money(inv["total"]))
    try:
        s = socket.create_connection(FAX_GATEWAY, timeout=5)
        s.sendall(body.encode("ascii"))
        s.close()
        return True
    except:
        return False
