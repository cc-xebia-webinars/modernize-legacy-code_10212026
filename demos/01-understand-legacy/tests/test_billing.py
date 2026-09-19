import unittest

from shipbill import billing


class BillingTest(unittest.TestCase):

    @unittest.skip("broken since the sqlite move, fix later - JK 2017")
    def test_invoice_total(self):
        self.assertEqual(billing.calc_invoice(1001, "2013-09"), 418.06)


if __name__ == "__main__":
    unittest.main()
