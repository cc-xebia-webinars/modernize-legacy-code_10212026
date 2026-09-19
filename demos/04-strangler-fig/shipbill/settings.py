# ShipBill settings
#
# These used to live in shipbill.ini. Moved them here in 2015 because ops kept
# editing the ini on the server and breaking the month end run. - DM

DB_PATH = "data/shipbill.db"
OUT_DIR = "out"
DEBUG = False

TAX_RATE = 0.0825          # state sales tax
MIN_CHARGE = 25.00         # smallest monthly invoice we send (transport only)
KEY_ACCOUNT_DISCOUNT = 0.10
VOL_DIVISOR = 5000         # cm3 per kg, same as the big carriers use
RETURN_RATE = 0.5          # returns billed at half the normal price
WEEKEND_FEE = 12.00        # saturday pickups, express only
REMOTE_FEE = 7.50          # anything we can't zone

# (base price incl. first kg, price per extra kg) by service and zone
RATES = {
    "ECO": {1: (4.95, 0.65), 2: (5.45, 0.75), 3: (5.95, 0.85), 4: (6.95, 0.95), 5: (8.45, 1.15)},
    "STD": {1: (6.95, 0.85), 2: (7.65, 0.95), 3: (8.45, 1.05), 4: (9.95, 1.25), 5: (11.95, 1.45)},
    "EXP": {1: (12.95, 1.35), 2: (14.45, 1.55), 3: (16.25, 1.75), 4: (18.95, 1.95), 5: (22.45, 2.35)},
}

# zone by first digit of the zip, depot is in the 3xxxx area
ZONES = {"0": 4, "1": 3, "2": 2, "3": 1, "4": 1, "5": 2, "6": 3, "7": 4, "8": 5, "9": 5}

# fuel surcharge by month. ops emails the new number every month, ADD IT HERE
FUEL_TABLE = {
    "2026-01": 0.065,
    "2026-02": 0.066,
    "2026-03": 0.071,
    "2026-04": 0.074,
    "2026-05": 0.078,
    "2026-06": 0.080,
    "2026-07": 0.082,
    "2026-08": 0.084,
}
