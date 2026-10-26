"""Tests for `core/liquid_agent.py`: the liquid density record and the conversion to liquid."""

from __future__ import annotations

import math
import re

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.liquid_agent import (
    REFERENCE_MOLAR_VOLUME_L_MOL,
    LiquidDensity,
    liquid_volume_ml,
    vapour_volume_per_liquid_volume,
)

# Mohr PJ, Newell DB, Taylor BN, Tiesinga E. CODATA recommended values of the
# fundamental physical constants: 2022. Rev Mod Phys. 2025;97(2):025002,
# Table XXXIII: "molar volume of ideal gas RT/p, T = 273.15 K, p = 101.325 kPa,
# Vm 22.413 969 54... x 10^-3 m^3 mol^-1, exact". Read from arXiv:2409.03787v1
# on 2026-10-26. The code derives its molar volume from R, T and p instead, so
# this tabulated value is independent of it.
CODATA_MOLAR_VOLUME_AT_0_CELSIUS_L_MOL = 22.413_969_54


def _molar_volume_at_20_celsius_l_mol() -> float:
    """Scale CODATA's 0 °C molar volume to 20 °C, in proportion to T at fixed pressure."""

    return CODATA_MOLAR_VOLUME_AT_0_CELSIUS_L_MOL * 293.15 / 273.15


def _density(g_ml: float = 1.5) -> LiquidDensity:
    return LiquidDensity(g_ml=g_ml, standard_deviation_g_ml=0.001, measured_at_celsius=20.0)


def test_the_reference_molar_volume_is_codatas_at_0_celsius_scaled_to_20_celsius() -> None:
    """A wrong gas constant, pressure or Celsius offset in the code fails this test.

    `docs/MODEL.md` § "Agent amount" states the molar volume as 24.055 L/mol,
    so the scaled CODATA figure is checked against that too.
    """

    expected = _molar_volume_at_20_celsius_l_mol()

    assert REFERENCE_MOLAR_VOLUME_L_MOL == pytest.approx(expected, rel=1e-9)
    assert expected == pytest.approx(24.055, abs=0.0005)


def test_one_millilitre_of_liquid_gives_its_moles_times_the_molar_volume() -> None:
    """At 1.5 g/mL and 200 g/mol, 1 mL of liquid is 0.0075 mol, about 180.4 mL of vapour."""

    expected_ml = 1.5 / 200.0 * _molar_volume_at_20_celsius_l_mol() * 1000.0

    # CODATA prints the molar volume to ten significant figures, so the
    # comparison can be no closer than about one part in 1e9.
    assert vapour_volume_per_liquid_volume(_density(1.5), 200.0) == pytest.approx(
        expected_ml, rel=1e-9
    )
    assert expected_ml == pytest.approx(180.41, abs=0.01)


@pytest.mark.parametrize(
    ("vapour_volume_l", "vapour_per_liquid", "expected_ml"),
    [
        # 2 % at 2 L/min for 60 min delivers 2.4 L of vapour. At 182.8 mL of
        # vapour per mL of liquid, that is 2400 / 182.8 mL of liquid.
        (2.4, 182.8, 2400.0 / 182.8),
        (0.0, 182.8, 0.0),
        (1.0, 200.0, 5.0),
    ],
)
def test_liquid_volume_divides_the_vapour_by_the_ratio(
    vapour_volume_l: float, vapour_per_liquid: float, expected_ml: float
) -> None:
    assert liquid_volume_ml(vapour_volume_l, vapour_per_liquid) == pytest.approx(
        expected_ml, rel=1e-12
    )


@pytest.mark.parametrize("vapour_volume_l", [-0.1, math.nan, math.inf])
def test_liquid_volume_refuses_a_vapour_volume_that_is_negative_or_not_finite(
    vapour_volume_l: float,
) -> None:
    with pytest.raises(SimulationConfigurationError, match="^vapour_volume_l must be"):
        liquid_volume_ml(vapour_volume_l, 182.8)


@pytest.mark.parametrize("vapour_per_liquid", [0.0, -182.8, math.nan, math.inf])
def test_liquid_volume_refuses_a_ratio_that_is_not_positive_and_finite(
    vapour_per_liquid: float,
) -> None:
    with pytest.raises(SimulationConfigurationError, match="^vapour_per_liquid must be"):
        liquid_volume_ml(1.0, vapour_per_liquid)


def test_liquid_volume_refuses_a_bool_as_a_programming_error() -> None:
    with pytest.raises(TypeError, match="vapour_volume_l"):
        liquid_volume_ml(True, 182.8)


@pytest.mark.parametrize("molar_mass_g_mol", [0.0, -200.0, math.nan, math.inf])
def test_the_ratio_refuses_a_molar_mass_that_is_not_positive_and_finite(
    molar_mass_g_mol: float,
) -> None:
    with pytest.raises(SimulationConfigurationError, match="^molar_mass_g_mol must be"):
        vapour_volume_per_liquid_volume(_density(), molar_mass_g_mol)


@pytest.mark.parametrize("g_ml", [0.0, -1.5, math.nan, math.inf])
def test_a_liquid_density_refuses_a_density_that_is_not_positive_and_finite(g_ml: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="^liquid density g_ml must be"):
        LiquidDensity(g_ml=g_ml, standard_deviation_g_ml=0.001, measured_at_celsius=20.0)


@pytest.mark.parametrize("standard_deviation_g_ml", [-0.001, math.nan, math.inf])
def test_a_liquid_density_refuses_a_spread_that_is_negative_or_not_finite(
    standard_deviation_g_ml: float,
) -> None:
    with pytest.raises(
        SimulationConfigurationError, match="^liquid density standard_deviation_g_ml must be"
    ):
        LiquidDensity(
            g_ml=1.5, standard_deviation_g_ml=standard_deviation_g_ml, measured_at_celsius=20.0
        )


def test_a_liquid_density_accepts_a_spread_of_zero() -> None:
    assert (
        LiquidDensity(g_ml=1.5, standard_deviation_g_ml=0.0, measured_at_celsius=20.0).g_ml == 1.5
    )


@pytest.mark.parametrize("measured_at_celsius", [0.0, 19.9, 25.0, 37.0])
def test_a_liquid_density_measured_at_another_temperature_is_refused(
    measured_at_celsius: float,
) -> None:
    """A density at 25 °C is about 0.8 % lower than at 20 °C, and nothing here corrects it.

    Laster, Fang and Eger measured a fall of 0.0025 g/mL per °C. Using a 25 °C
    density as though it were the 20 °C one would put that error, unseen,
    into every liquid volume and every cost derived from it.
    """

    # The message spells out "degrees C" because tools/glyph_check.py has not
    # confirmed that the interface draws the degree sign.
    expected = (
        f"a liquid density measured at {measured_at_celsius!r} degrees C cannot be used: the "
        "model states every amount of agent at 20 degrees C, and no correction for "
        'temperature is stored (docs/MODEL.md, "Agent amount")'
    )

    with pytest.raises(SimulationConfigurationError, match=f"^{re.escape(expected)}$"):
        LiquidDensity(
            g_ml=1.5, standard_deviation_g_ml=0.001, measured_at_celsius=measured_at_celsius
        )


@pytest.mark.parametrize("measured_at_celsius", [None, True, "20"])
def test_a_liquid_density_refuses_a_temperature_that_is_not_a_number(
    measured_at_celsius: object,
) -> None:
    """A missing or mistyped temperature is refused as a programming error.

    It is not treated as a measurement, whether at 20 °C or at another
    temperature. Before this test, `None` was refused as "a liquid density
    measured at None °C". That message reports a real measurement at the wrong
    temperature. `PL-KZ99`'s second blind review pass found this.
    """

    expected = (
        f"liquid density measured_at_celsius of {measured_at_celsius!r} has type "
        f"{type(measured_at_celsius).__name__}, not int or float"
    )

    with pytest.raises(TypeError, match=f"^{re.escape(expected)}"):
        LiquidDensity(
            g_ml=1.5,
            standard_deviation_g_ml=0.001,
            measured_at_celsius=measured_at_celsius,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("g_ml", "molar_mass_g_mol", "shown_inputs", "shown_ratio"),
    [
        # 1.5 / 1e-306 overflows to inf once multiplied by the molar volume.
        (1.5, 1e-306, "1.5 g/mL and a molar mass of 1e-306", "inf"),
        # 1e-300 / 1e300 underflows to zero.
        (1e-300, 1e300, "1e-300 g/mL and a molar mass of 1e+300", "0.0"),
    ],
)
def test_the_ratio_refuses_inputs_whose_ratio_is_not_a_positive_finite_number(
    g_ml: float, molar_mass_g_mol: float, shown_inputs: str, shown_ratio: str
) -> None:
    """Each input is positive and finite, and the ratio they make is not.

    Before this test, the ratio came back as `inf` or `0.0` with no error. The
    refusal then came later, from `liquid_volume_ml`, naming its own argument
    rather than the density and molar mass that caused it (found by
    `PL-KZ99`'s first blind review pass).
    """

    density = LiquidDensity(g_ml=g_ml, standard_deviation_g_ml=0.0, measured_at_celsius=20.0)

    expected = (
        f"a liquid density of {shown_inputs} g/mol give a vapour-to-liquid ratio of "
        f"{shown_ratio}, which is not a positive finite number"
    )

    with pytest.raises(SimulationConfigurationError, match=f"^{re.escape(expected)}$"):
        vapour_volume_per_liquid_volume(density, molar_mass_g_mol)


def test_the_ratio_accepts_a_ratio_below_one() -> None:
    """A ratio of vapour volume to liquid volume below 1 is accepted.

    Only a ratio that is not a positive finite number is rejected. With a liquid density of
    0.001 g/mL and a molar mass of 200 g/mol, 1 mL of liquid becomes about 0.12 mL of vapour.
    No agent has such a density, but nothing physical forbids the ratio.
    """

    density = LiquidDensity(g_ml=0.001, standard_deviation_g_ml=0.0, measured_at_celsius=20.0)

    assert vapour_volume_per_liquid_volume(density, 200.0) == pytest.approx(
        0.001 / 200.0 * _molar_volume_at_20_celsius_l_mol() * 1000.0, rel=1e-9
    )


@pytest.mark.parametrize(
    ("vapour_volume_l", "vapour_per_liquid", "shown_inputs"),
    [(1e306, 182.8, "1e+306 L of vapour at 182.8"), (1.0, 1e-306, "1.0 L of vapour at 1e-306")],
)
def test_liquid_volume_refuses_a_result_that_overflows(
    vapour_volume_l: float, vapour_per_liquid: float, shown_inputs: str
) -> None:
    """Each input passes its own check, and the liquid volume they make is infinite.

    Before this test, `liquid_volume_ml` returned `inf` without an error
    (found by `PL-KZ99`'s adversarial review).
    """

    expected = (
        f"{shown_inputs} mL of vapour per mL of liquid gives a liquid volume that is not finite"
    )

    with pytest.raises(SimulationConfigurationError, match=f"^{re.escape(expected)}$"):
        liquid_volume_ml(vapour_volume_l, vapour_per_liquid)
