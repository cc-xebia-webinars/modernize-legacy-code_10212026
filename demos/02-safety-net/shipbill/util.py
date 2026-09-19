def round2(x):
    # python round() does bankers rounding, accounting wants half up - KT 2012
    return int(x * 100 + 0.5) / 100.0


def cents(x):
    return int(round(x * 100))


def money(x):
    return "%.2f" % x
