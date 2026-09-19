"""Characterization tests for shipbill/util.py: rounding and money formatting."""

import pytest

from shipbill import rates, util


@pytest.mark.parametrize(("amount", "expected"), [
    (0.125, 0.13),
    (2.675, 2.68),
    (10.485, 10.49),
    (34.2, 34.2),
])
def test_round2_rounds_half_up(amount, expected):
    assert util.round2(amount) == expected


def test_round2_rounds_down_a_literal_that_floats_store_below_the_half_cent():
    # 1.005 is stored as 1.00499999..., so this pins a quirk, not a rule.
    assert util.round2(1.005) == 1.0


def test_round2_rounds_down_a_half_cent_produced_by_float_math():
    # 6.95 + 0.95 * 8.5 is 15.024999... in floats,
    # so customers were billed 15.02, not 15.03.
    assert util.round2(rates.base_charge("ECO", 4, 9.5)) == 15.02


@pytest.mark.parametrize(("amount", "expected"), [(19.92, 1992), (0.29, 29), (0.0, 0)])
def test_cents_converts_dollars_to_whole_cents(amount, expected):
    assert util.cents(amount) == expected


def test_money_always_shows_two_decimals():
    assert util.money(7.5) == "7.50"
