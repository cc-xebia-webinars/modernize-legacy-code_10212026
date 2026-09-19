import arrow

LEGACY_FMT = "MM/DD/YYYY"


def parse_shipped(s):
    # shipped has a time on the end, we only need the day
    return arrow.get(s, LEGACY_FMT)


def period_start(period):
    return arrow.get(period + "-01", "YYYY-MM-DD")


def period_end(period):
    return period_start(period).shift(months=+1).shift(days=-1)


def due_date(inv_date):
    # net 30, but never due on a weekend
    due = inv_date.shift(days=+30)
    if due.weekday() == 5:
        due = due.shift(days=+2)
    elif due.weekday() == 6:
        due = due.shift(days=+1)
    return due


def is_saturday(d):
    return d.weekday() == 5


def batch_stamp(d):
    # LedgerLink wants the batch as epoch seconds
    return int(d.timestamp())


def fmt_legacy(d):
    return d.format("MM/DD/YYYY")


def fmt_ymd(d):
    return d.format("YYYYMMDD")
