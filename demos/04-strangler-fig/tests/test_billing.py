"""Characterization tests for shipbill/billing.py: how an invoice is built.

Most tests add a fresh customer with a shipment or two, so each one shows a single
rule. The expected values came from running the legacy code, and a few of them pin
behavior that may well be a bug. Those say so, and they're listed as open
questions in docs/ARCHITECTURE.md. Don't "fix" them here.
"""

import pytest

from shipbill import billing, db
from tests.conftest import lines_of

PERIOD = "2026-09"


def invoice_for(cust_id):
    inv_id = billing.calc_invoice(cust_id, PERIOD)
    return inv_id, db.get_invoice(inv_id)


# ------------------------------------------------------------------ shipment lines

def test_a_small_invoice_has_every_line_in_order(customer, shipment):
    cust = customer()
    shipment(cust)
    inv_id, inv = invoice_for(cust)
    assert lines_of(inv_id) == [
        ("SHIP 90001 STD Z1 1.0KG", 6.95),
        ("FUEL SURCHARGE", 0.58),
        ("MINIMUM CHARGE", 18.05),
        ("SALES TAX", 2.06),
    ]
    assert inv["total"] == 27.64


def test_cancelled_shipments_are_not_billed(customer, shipment):
    cust = customer()
    shipment(cust, status="CANCELLED")
    assert billing.calc_invoice(cust, PERIOD) is None


def test_returns_are_billed_at_half_price(customer, shipment):
    cust = customer()
    shipment(cust, status="RETURNED")
    inv_id, _ = invoice_for(cust)
    assert lines_of(inv_id)[0] == ("RETURN 90001", 3.48)


def test_saturday_express_pickups_add_a_weekend_fee(customer, shipment):
    cust = customer()
    shipment(cust, service="EXP", shipped="09/12/2026 09:05")
    inv_id, _ = invoice_for(cust)
    assert lines_of(inv_id)[:2] == [("SHIP 90001 EXP Z1 1.0KG", 12.95), ("WEEKEND PICKUP", 12.0)]


@pytest.mark.parametrize(("service", "status"), [("STD", "DELIVERED"), ("EXP", "RETURNED")])
def test_no_weekend_fee_unless_a_delivered_express(customer, shipment, service, status):
    cust = customer()
    shipment(cust, service=service, status=status, shipped="09/12/2026 09:05")
    inv_id, _ = invoice_for(cust)
    assert "WEEKEND PICKUP" not in [desc for desc, _ in lines_of(inv_id)]


def test_postcodes_without_a_zone_are_priced_as_zone_5_plus_a_remote_fee(customer, shipment):
    cust = customer()
    shipment(cust, dest="K1A 0B1")
    inv_id, _ = invoice_for(cust)
    assert lines_of(inv_id)[:2] == [("SHIP 90001 STD Z5 1.0KG", 11.95), ("REMOTE AREA", 7.5)]


def test_unknown_service_codes_are_priced_as_std(customer, shipment):
    cust = customer()
    shipment(cust, service="OVN")
    inv_id, _ = invoice_for(cust)
    assert lines_of(inv_id)[0] == ("SHIP 90001 OVN Z1 1.0KG", 6.95)


def test_half_cents_from_float_math_round_down(customer, shipment):
    # Exact arithmetic gives 15.025, which would round to 15.03. Customers paid 15.02.
    cust = customer()
    shipment(cust, service="ECO", dest="70303", kg=9.5)
    inv_id, _ = invoice_for(cust)
    assert lines_of(inv_id)[0] == ("SHIP 90001 ECO Z4 9.5KG", 15.02)


# ------------------------------------------------------------ discounts and fuel

def test_key_accounts_get_ten_percent_off_transport(customer, shipment):
    cust = customer(account_type="KEY")
    for _ in range(3):
        shipment(cust, service="EXP")
    _, inv = invoice_for(cust)
    assert (inv["subtotal"], inv["discount"]) == (38.85, 3.89)


def test_customer_1047_gets_fifteen_percent_off(billing_db):
    # Hard-coded for one customer since 2014. Open question for accounting.
    _, inv = invoice_for(1047)
    assert (inv["subtotal"], inv["discount"]) == (688.02, 103.2)


def test_fuel_is_charged_on_transport_after_the_discount(customer, shipment):
    cust = customer(account_type="KEY")
    for _ in range(3):
        shipment(cust, service="EXP")
    inv_id, inv = invoice_for(cust)
    # (38.85 - 3.89) at August's 8.4%
    assert inv["fuel"] == 2.94
    assert ("FUEL SURCHARGE", 2.94) in lines_of(inv_id)


@pytest.mark.parametrize(("period", "rate"), [
    ("2026-08", 0.084),
    ("2026-01", 0.065),
    ("2026-09", 0.084),
    ("2027-03", 0.084),
    ("2025-12", 0.0),
])
def test_a_missing_fuel_month_uses_the_latest_earlier_rate(period, rate):
    assert billing.fuel_rate(period) == rate


# ------------------------------------------------------- minimum charge and tax

def test_invoices_under_25_dollars_are_topped_up(customer, shipment):
    cust = customer()
    for _ in range(5):
        shipment(cust, service="ECO")
    inv_id, _ = invoice_for(cust)
    assert ("MINIMUM CHARGE", 0.25) in lines_of(inv_id)


def test_fuel_does_not_count_toward_the_minimum(customer, shipment):
    # 24.95 of transport plus 2.10 of fuel is over 25.00, but it's still topped up.
    cust = customer()
    shipment(cust, service="EXP", shipped="09/12/2026 09:05")
    inv_id, _ = invoice_for(cust)
    assert ("MINIMUM CHARGE", 0.05) in lines_of(inv_id)


def test_no_minimum_charge_at_25_dollars_or_more(customer, shipment):
    cust = customer()
    for _ in range(2):
        shipment(cust, service="EXP")
    inv_id, _ = invoice_for(cust)
    assert "MINIMUM CHARGE" not in [desc for desc, _ in lines_of(inv_id)]


def test_sales_tax_is_charged_on_transport_but_not_fuel(customer, shipment):
    cust = customer()
    for _ in range(2):
        shipment(cust, service="EXP")
    _, inv = invoice_for(cust)
    # 25.90 x 8.25% = 2.14. With the 2.18 of fuel included it would be 2.32.
    assert (inv["fuel"], inv["tax"], inv["total"]) == (2.18, 2.14, 30.22)


def test_tax_exempt_customers_pay_no_sales_tax(customer, shipment):
    cust = customer(tax_exempt=1)
    for _ in range(2):
        shipment(cust, service="EXP")
    inv_id, inv = invoice_for(cust)
    assert (inv["tax"], inv["total"]) == (0.0, 28.08)
    assert "SALES TAX" not in [desc for desc, _ in lines_of(inv_id)]


# ------------------------------------------------------------- the billing run

def test_invoices_are_dated_at_period_end_and_due_30_days_later(customer, shipment):
    cust = customer()
    shipment(cust)
    _, inv = invoice_for(cust)
    assert (inv["inv_date"], inv["due_date"]) == ("09/30/2026", "10/30/2026")


def test_unknown_customers_get_no_invoice(billing_db):
    assert billing.calc_invoice(424242, PERIOD) is None


def test_the_september_run_bills_nine_customers(billing_db):
    ids, _ = billing.run_billing(PERIOD)
    billed = [db.get_invoice(i)["cust_id"] for i in ids]
    assert billed == [1001, 1012, 1023, 1047, 1058, 1063, 1071, 1090, 1102]


def test_inactive_customers_are_not_billed_even_when_they_shipped(billing_db):
    # 1084 is inactive but shipped in September. Open question for operations.
    ids, _ = billing.run_billing(PERIOD)
    assert 1084 not in [db.get_invoice(i)["cust_id"] for i in ids]


def test_running_a_period_twice_replaces_the_first_run(billing_db):
    billing.run_billing(PERIOD)
    billing.run_billing(PERIOD)
    count = db.query("SELECT COUNT(*) AS n FROM invoices WHERE period = '2026-09'")[0]["n"]
    assert count == 9
