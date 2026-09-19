"""Characterization tests for shipbill/dates.py: periods, due dates, and stamps."""

import datetime as dt

import pytest

from shipbill import dates


@pytest.mark.parametrize(("period", "last_day"), [
    ("2026-09", dt.date(2026, 9, 30)),
    ("2026-02", dt.date(2026, 2, 28)),
    ("2026-12", dt.date(2026, 12, 31)),
])
def test_period_end_is_the_last_day_of_the_month(period, last_day):
    assert dates.period_end(period).date() == last_day


def test_invoices_are_due_thirty_days_after_the_period_ends():
    assert dates.due_date(dates.period_end("2026-09")).date() == dt.date(2026, 10, 30)


def test_a_due_date_on_saturday_moves_to_monday():
    # April 30 plus 30 days is Saturday, May 30.
    assert dates.due_date(dates.period_end("2026-04")).date() == dt.date(2026, 6, 1)


def test_a_due_date_on_sunday_moves_to_monday():
    # July 31 plus 30 days is Sunday, August 30.
    assert dates.due_date(dates.period_end("2026-07")).date() == dt.date(2026, 8, 31)


def test_shipped_dates_ignore_the_time_of_day():
    assert dates.parse_shipped("09/12/2026 09:05").date() == dt.date(2026, 9, 12)


@pytest.mark.parametrize(("shipped", "saturday"), [
    ("09/12/2026 09:05", True),
    ("09/13/2026 09:05", False),
])
def test_is_saturday(shipped, saturday):
    assert dates.is_saturday(dates.parse_shipped(shipped)) is saturday


def test_batch_stamp_is_epoch_seconds_at_midnight_utc():
    assert dates.batch_stamp(dates.period_end("2026-09")) == 1790726400


def test_dates_format_the_way_the_database_and_ledgerlink_expect():
    end = dates.period_end("2026-09")
    assert dates.fmt_legacy(end) == "09/30/2026"
    assert dates.fmt_ymd(end) == "20260930"
