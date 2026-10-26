"""Tests for `core/liquid_agent.py`: the liquid density record and the conversion to liquid."""

from __future__ import annotations

import math

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

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^a liquid density measured at {measured_at_celsius!r} °C cannot be used: the "
            r"model states every amount of agent at 20 °C"
        ),
    ):
        LiquidDensity(
            g_ml=1.5, standard_deviation_g_ml=0.001, measured_at_celsius=measured_at_celsius
        )
