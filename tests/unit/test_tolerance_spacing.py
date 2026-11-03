"""Tests for the check in `tests/conftest.py` that refuses a tolerance below the float spacing.

The expected spacings are worked out from the IEEE 754 binary64 format rather
than taken from the module. A double has 52 fraction bits, so between 2**e and
2**(e + 1) the numbers are 2**(e - 52) apart. 100.0 lies between 2**6 and
2**7, so its neighbours are 2**-46, about 1.42e-14, away. 1.0 is a power of
two: the number above it is 2**-52 away and the number below it 2**-53.
"""

from __future__ import annotations

import math
from decimal import Decimal

import pytest

SPACING_AT_100 = 2.0**-46
SPACING_ABOVE_1 = 2.0**-52
SPACING_BELOW_1 = 2.0**-53


def test_a_tolerance_below_the_spacing_fails() -> None:
    with pytest.raises(
        pytest.fail.Exception, match=r"difference of 1e-15.*the 1\.42e-14 between 100\.0"
    ):
        assert 100.0 == pytest.approx(100.0, abs=1e-15)


def test_each_element_of_a_list_or_mapping_is_checked() -> None:
    with pytest.raises(pytest.fail.Exception, match="1.42e-14"):
        assert [1.0, 100.0] == pytest.approx([1.0, 100.0], abs=1e-15)
    with pytest.raises(pytest.fail.Exception, match="1.42e-14"):
        assert {"dial": 100.0} == pytest.approx({"dial": 100.0}, abs=1e-15)


def test_a_tolerance_equal_to_the_spacing_admits_the_neighbour() -> None:
    assert 100.0 + SPACING_AT_100 == pytest.approx(100.0, abs=SPACING_AT_100)
    assert -100.0 - SPACING_AT_100 == pytest.approx(-100.0, abs=SPACING_AT_100)
    with pytest.raises(pytest.fail.Exception, match="1.42e-14"):
        assert 100.0 == pytest.approx(100.0, abs=math.nextafter(SPACING_AT_100, 0.0))


def test_the_smaller_gap_decides_at_a_power_of_two() -> None:
    between_the_gaps = 1.5 * SPACING_BELOW_1
    assert 1.0 + SPACING_ABOVE_1 == pytest.approx(1.0, abs=SPACING_ABOVE_1)
    assert 1.0 - SPACING_BELOW_1 == pytest.approx(1.0, abs=between_the_gaps)
    # The message names the gap below, 2**-53, about 1.11e-16.
    with pytest.raises(pytest.fail.Exception, match="1.11e-16"):
        assert 1.0 == pytest.approx(1.0, abs=0.5 * SPACING_BELOW_1)


def test_a_zero_tolerance_is_an_exact_check_written_on_purpose() -> None:
    assert 100.0 == pytest.approx(100.0, rel=0, abs=0)
    assert math.isclose(100.0, 100.0, rel_tol=0.0, abs_tol=0.0)


def test_the_default_tolerance_passes_at_every_scale() -> None:
    for expected in (1e-300, 1e-6, 1.0, 1e6, 1e300):
        assert expected == pytest.approx(expected)


def test_the_tolerance_is_pytests_own_combination_of_rel_and_abs() -> None:
    # Given only `rel`, pytest still applies its default absolute tolerance,
    # 1e-12, so rel=1e-17 on 100.0 allows 1e-12, which is above the spacing.
    assert 100.0 == pytest.approx(100.0, rel=1e-17)
    # At 1e6 the spacing is 2**-33, about 1.16e-10, above both 1e-11 and 1e-12.
    with pytest.raises(pytest.fail.Exception, match="1.16e-10"):
        assert 1e6 == pytest.approx(1e6, rel=1e-17)


def test_isclose_called_from_a_test_is_checked() -> None:
    with pytest.raises(pytest.fail.Exception, match=r"math\.isclose.*1\.42e-14"):
        math.isclose(100.0, 100.0, rel_tol=1e-18)
    with pytest.raises(pytest.fail.Exception, match="1.42e-14"):
        math.isclose(1.0, 100.0, rel_tol=0.0, abs_tol=1e-15)


def test_isclose_called_from_outside_the_tests_is_left_alone() -> None:
    namespace: dict[str, object] = {"math": math}
    code = compile(
        "result = math.isclose(100.0, 100.0, rel_tol=1e-18)", "/elsewhere/module.py", "exec"
    )
    exec(code, namespace)
    assert namespace["result"] is True


def test_values_without_a_float_spacing_are_left_alone() -> None:
    assert Decimal("100") == pytest.approx(Decimal("100"), abs=Decimal("1e-30"))
    assert math.inf == pytest.approx(math.inf, abs=1e-300)


def test_an_invalid_tolerance_is_still_refused_by_pytest() -> None:
    with pytest.raises(ValueError, match="can't be negative"):
        assert 2.0 == pytest.approx(1.0, abs=-1.0)
    with pytest.raises(ValueError):
        math.isclose(1.0, 2.0, rel_tol=-1.0)
