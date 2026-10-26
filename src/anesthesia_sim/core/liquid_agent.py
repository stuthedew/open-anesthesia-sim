"""Convert an amount of agent vapour into the volume of liquid agent it came from.

The model holds every amount of agent as a volume of pure agent vapour, stated
at one reference condition: 20 °C and one standard atmosphere, dry
(`docs/MODEL.md` § "Agent amount"). A vaporizer is filled with liquid, and an
agent is bought by the bottle of liquid. So a figure that a reader acts on,
such as what the delivered agent cost, needs the vapour converted into
liquid.

One millilitre of liquid agent weighs rho grams, where rho is the liquid's
density in g/mL. Dividing by the molar mass M, in g/mol, gives the moles in
that millilitre. Each mole of vapour, treated as an ideal gas, fills the molar
volume V_m = R T / p at the reference condition. So one millilitre of liquid
gives

    vapour per liquid = (rho / M) x V_m

millilitres of vapour, with V_m in millilitres per mole. For sevoflurane that
is about 183 mL of vapour from each millilitre of liquid.

Each agent's data file stores rho and M with their sources, and stores rho
with the temperature at which it was measured (`PL-KZ99`). The literature
also publishes the ratio itself, one number per agent. Those published ratios
are not stored. A published ratio states its temperature only where its
source does, and Biro 2014's abstract does not.
`tests/reference/test_published_vapour_to_liquid.py` compares the derived
ratios with the published ones instead.

The ideal gas is part of the model's definition of its unit, not a claim
about real vapour. The unit is the volume that the agent would fill as an
ideal gas at the reference condition, as `docs/MODEL.md` § "Agent amount"
defines it.

**The conversion is exact for fresh gas and about 5.8 % high for a store.**
The delivered and exhausted agent and the circuit's amount are gas at room
temperature, so they really are at the 20 °C condition, and this conversion
is exact for them. The alveolar, venous and tissue stores are at body
temperature and carry the 20 °C condition only as a label. They hold 5.8 %
fewer moles than the label implies, so the liquid volume converted from a
store is 5.8 % too high (`docs/MODEL.md` § "Known limitations", "One
reference condition, where the model physically has two"). A cost is a
delivered amount, so it is exact. A readout that converts a store must say
so (`PL-B396`).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Final

from anesthesia_sim.core.checked_number import require_a_number, shown
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.units import LITRES_PER_CUBIC_METRE, MILLILITRES_PER_LITRE
from anesthesia_sim.core.validation import require_nonnegative_finite, require_positive_finite

# The SI defines the Boltzmann and Avogadro constants as exact, so the molar gas
# constant R, their product, is exact too. The standard atmosphere is defined as
# exactly 101 325 Pa, which is 760 mmHg. Mohr PJ, Newell DB, Taylor BN, Tiesinga
# E. CODATA recommended values of the fundamental physical constants: 2022. Rev
# Mod Phys. 2025;97(2):025002. doi:10.1103/RevModPhys.97.025002. Table XXXII
# gives k, N_A and R, and Table XXXIII gives the standard atmosphere. Read at
# full text from arXiv:2409.03787v1 on 2026-10-26.

BOLTZMANN_CONSTANT_J_K: Final = 1.380_649e-23
"""k, in joules per kelvin. Exact by the definition of the SI."""

AVOGADRO_CONSTANT_PER_MOL: Final = 6.022_140_76e23
"""N_A, in entities per mole. Exact by the definition of the SI."""

MOLAR_GAS_CONSTANT_J_MOL_K: Final = AVOGADRO_CONSTANT_PER_MOL * BOLTZMANN_CONSTANT_J_K
"""R = N_A k, in joules per mole per kelvin: 8.314 462 618... and exact."""

STANDARD_ATMOSPHERE_PA: Final = 101_325.0
"""One standard atmosphere in pascals. Exact by definition."""

CELSIUS_ZERO_K: Final = 273.15
"""0 °C in kelvin. The SI defines a Celsius temperature as the kelvin temperature minus this."""

REFERENCE_TEMPERATURE_CELSIUS: Final = 20.0
"""The temperature at which every amount of agent is stated (`docs/MODEL.md` § "Agent amount")."""

REFERENCE_MOLAR_VOLUME_L_MOL: Final = (
    MOLAR_GAS_CONSTANT_J_MOL_K
    * (REFERENCE_TEMPERATURE_CELSIUS + CELSIUS_ZERO_K)
    / STANDARD_ATMOSPHERE_PA
    * LITRES_PER_CUBIC_METRE
)
"""V_m = R T / p at 20 °C and one standard atmosphere, in litres per mole: about 24.055."""


@dataclass(frozen=True, slots=True)
class LiquidDensity:
    """One liquid agent's density, its spread, and the temperature at which it was measured.

    A liquid's density falls as it warms, so a density means nothing without
    its temperature, and this record carries it. The temperature must be the
    model's reference temperature, 20 °C. The density is converted into
    vapour stated at that temperature, so the liquid has to be stated there
    too. A density measured at another temperature is refused rather than
    corrected, because no correction for temperature is stored.

    `standard_deviation_g_ml` is the spread that the measurement reports. No
    calculation uses it. It is kept so that the uncertainty a reader of the
    data file sees is the source's own.

    Raises:
        TypeError: `measured_at_celsius` is not an `int` or a `float`, or is a
            `bool`, as `require_a_number` says. The guards on the other two
            fields raise the same.
        SimulationConfigurationError: `g_ml` is not positive and finite,
            `standard_deviation_g_ml` is negative or not finite, or
            `measured_at_celsius` is not the reference temperature.
    """

    g_ml: float
    standard_deviation_g_ml: float
    measured_at_celsius: float

    def __post_init__(self) -> None:
        require_positive_finite("liquid density g_ml", self.g_ml)
        require_nonnegative_finite(
            "liquid density standard_deviation_g_ml", self.standard_deviation_g_ml
        )

        require_a_number("liquid density measured_at_celsius", self.measured_at_celsius)

        if self.measured_at_celsius != REFERENCE_TEMPERATURE_CELSIUS:
            raise SimulationConfigurationError(
                f"a liquid density measured at {shown(self.measured_at_celsius)} °C cannot be "
                f"used: the model states every amount of agent at "
                f"{REFERENCE_TEMPERATURE_CELSIUS:g} °C, and no correction for temperature is "
                'stored (docs/MODEL.md, "Agent amount")'
            )


def vapour_volume_per_liquid_volume(
    liquid_density: LiquidDensity, molar_mass_g_mol: float
) -> float:
    """Return the millilitres of vapour that one millilitre of liquid agent gives.

    The vapour is stated at the model's reference condition, 20 °C and one
    standard atmosphere. The equation is the module docstring's.

    Raises:
        SimulationConfigurationError: `molar_mass_g_mol` is not positive and
            finite. Also raised when the two inputs are each positive and
            finite but their ratio overflows to infinity or underflows to
            zero. The message names both inputs.
    """

    require_positive_finite("molar_mass_g_mol", molar_mass_g_mol)

    moles_per_ml_of_liquid = liquid_density.g_ml / molar_mass_g_mol
    vapour_per_liquid = (
        moles_per_ml_of_liquid * REFERENCE_MOLAR_VOLUME_L_MOL * MILLILITRES_PER_LITRE
    )

    if not isfinite(vapour_per_liquid) or vapour_per_liquid <= 0.0:
        raise SimulationConfigurationError(
            f"a liquid density of {shown(liquid_density.g_ml)} g/mL and a molar mass of "
            f"{shown(molar_mass_g_mol)} g/mol give a vapour-to-liquid ratio of "
            f"{shown(vapour_per_liquid)}, which is not a positive finite number"
        )

    return vapour_per_liquid


def liquid_volume_ml(vapour_volume_l: float, vapour_per_liquid: float) -> float:
    """Return the millilitres of liquid agent that gave `vapour_volume_l` litres of vapour.

    `vapour_per_liquid` is the agent's `vapour_volume_per_liquid_volume`, in
    millilitres of vapour per millilitre of liquid. The vapour is an amount of
    agent as the model states it, at 20 °C and one standard atmosphere. The
    result is exact for a delivered, exhausted or circuit amount, and 5.8 %
    too high for an alveolar, venous or tissue amount, as the module
    docstring says.

    Raises:
        SimulationConfigurationError: `vapour_volume_l` is negative or not
            finite, or `vapour_per_liquid` is not positive and finite.
    """

    require_nonnegative_finite("vapour_volume_l", vapour_volume_l)
    require_positive_finite("vapour_per_liquid", vapour_per_liquid)

    return vapour_volume_l * MILLILITRES_PER_LITRE / vapour_per_liquid
