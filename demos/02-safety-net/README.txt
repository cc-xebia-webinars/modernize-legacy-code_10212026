SHIPBILL 2.1
============

Month end billing for the courier business.

To run billing:

    python run_billing.py --month=09 --year=2013

Needs Python 2.7 and arrow (pip install arrow).

The database is on \\FILESRV01\shipbill\shipbill.mdb

Rates are in rates.xls on the shared drive, update settings.py from it when
they change. Fuel surcharge comes from ops every month.

The export file goes to accounting for LedgerLink. Don't change the format.

Questions: Dave M. x4417
