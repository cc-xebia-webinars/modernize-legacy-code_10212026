"""Characterization tests for shipbill/rates.py: zones, weights, and base charges."""

import pytest

from shipbill import rates


@pytest.mark.parametrize(("postcode", "zone"), [
    ("30303", 1),
    ("90210", 5),
    (" 30303 ", 1),
])
def test_zone_comes_from_the_first_digit_of_the_zip(postcode, zone):
    assert rates.zone_for(postcode) == zone


@pytest.mark.parametrize("postcode", ["2134", "02134", "7030"])
def test_four_digit_zips_get_their_leading_zero_back(postcode):
    assert rates.zone_for(postcode) == 4


@pytest.mark.parametrize("postcode", ["K1A 0B1", "V6B 1A1"])
def test_postcodes_that_are_not_all_digits_have_no_zone(postcode):
    assert rates.zone_for(postcode) is None


@pytest.mark.parametrize(("parcel", "expected"), [
    ((1.0, 10, 10, 10), 1.0),
    ((1.01, 10, 10, 10), 1.5),
    ((1.5, 10, 10, 10), 1.5),
    ((3.1, 35, 25, 15), 3.5),
])
def test_chargeable_weight_rounds_up_to_the_next_half_kilo(parcel, expected):
    assert rates.chargeable_weight(*parcel) == expected


@pytest.mark.parametrize(("parcel", "expected"), [
    ((0.2, 50, 40, 30), 12.0),
    ((18.0, 60, 40, 40), 19.5),
    ((2.0, 30, 20, 10), 2.0),
])
def test_chargeable_weight_uses_volume_when_it_is_heavier(parcel, expected):
    assert rates.chargeable_weight(*parcel) == expected


@pytest.mark.parametrize("weight", [0.5, 1.0])
def test_base_price_covers_the_first_kilo(weight):
    assert rates.base_charge("STD", 1, weight) == 6.95


@pytest.mark.parametrize(("service", "zone", "weight", "expected"), [
    ("STD", 1, 2.5, 8.225),
    ("EXP", 5, 6.0, 34.2),
])
def test_each_extra_kilo_costs_the_per_kg_rate(service, zone, weight, expected):
    assert rates.base_charge(service, zone, weight) == expected


def test_unknown_services_raise_key_error():
    # billing.calc_invoice catches this and falls back to STD.
    with pytest.raises(KeyError):
        rates.base_charge("OVN", 1, 1.0)
