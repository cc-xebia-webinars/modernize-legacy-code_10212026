import sqlite3

from shipbill import settings

CONN = None


def get_conn():
    global CONN
    if CONN is None:
        CONN = sqlite3.connect(settings.DB_PATH)
        CONN.row_factory = sqlite3.Row
    return CONN


def query(sql):
    if settings.DEBUG:
        print("SQL: " + sql)
    cur = get_conn().cursor()
    cur.execute(sql)
    return cur.fetchall()


def execute(sql, params=()):
    if settings.DEBUG:
        print("SQL: " + sql)
    cur = get_conn().cursor()
    cur.execute(sql, params)
    get_conn().commit()
    return cur.lastrowid


def get_customer(cust_id):
    rows = query("SELECT * FROM customers WHERE id = %d" % cust_id)
    if len(rows) == 0:
        return None
    return rows[0]


def _period_like(period):
    # shipped is stored as MM/DD/YYYY HH:MM (from the old VB front end)
    yyyy, mm = period.split("-")
    return mm + "/%/" + yyyy + "%"


def get_active_customers(period):
    return query("SELECT DISTINCT c.* FROM customers c JOIN shipments s ON s.cust_id = c.id "
                 "WHERE c.active = 1 AND s.shipped LIKE '" + _period_like(period) + "' ORDER BY c.id")


def get_shipments(cust_id, period):
    return query("SELECT * FROM shipments WHERE cust_id = " + str(cust_id) +
                 " AND shipped LIKE '" + _period_like(period) + "' ORDER BY id")


def save_invoice(cust_id, period, inv_date, due_date, subtotal, fuel, discount, tax, total):
    return execute("INSERT INTO invoices (cust_id, period, inv_date, due_date, subtotal, fuel, "
                   "discount, tax, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (cust_id, period, inv_date, due_date, subtotal, fuel, discount, tax, total))


def save_line(invoice_id, shipment_id, description, amount):
    execute("INSERT INTO invoice_lines (invoice_id, shipment_id, description, amount) "
            "VALUES (?, ?, ?, ?)", (invoice_id, shipment_id, description, amount))


def get_invoice(invoice_id):
    rows = query("SELECT * FROM invoices WHERE id = %d" % invoice_id)
    if len(rows) == 0:
        return None
    return rows[0]


def get_lines(invoice_id):
    return query("SELECT * FROM invoice_lines WHERE invoice_id = %d ORDER BY id" % invoice_id)


def delete_period(period):
    # rerun safe: wipe the period first so ops can run it twice - JK 2017
    execute("DELETE FROM invoice_lines WHERE invoice_id IN "
            "(SELECT id FROM invoices WHERE period = ?)", (period,))
    execute("DELETE FROM invoices WHERE period = ?", (period,))
