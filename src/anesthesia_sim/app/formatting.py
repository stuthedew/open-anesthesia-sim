"""Render modeled values as the strings the interface displays.

This module is pure formatting, independent of the Qt toolkit and of the
scientific core. Every function here takes a number that the model produced and
returns the text that a reader sees. Nothing in this module builds a control,
reads simulation state, or performs a physiological calculation.

This is a module of its own for the following reason. `docs/MODEL.md`
§ "Displayed precision" derives how many digits of a concentration are worth
showing, starting from what the model's parameters can support. This module
applies the result of that derivation. `CLAUDE.md` treats presentation
correctness as part of the safety standard. It also requires a displayed value
to be traceable to the transformations that produced it. Rounding for display
is the last of those transformations. So it has to be readable, citable and
testable on its own, not reachable only by loading the whole dashboard.
`tests/unit/test_formatting.py` tests it.

This module deliberately does not restate that derivation's figures. They were
once restated at four places in this package, and all four went stale together
when the solver changed (`PL-X9KD`). The section is cited instead, so the next
re-derivation has only one place to update.

The displayed resolution is a property of the display alone. Everything
upstream carries full binary64 precision: the compartment states, every
integration step, and every state of the `DrawnWindow` that the chart is drawn
from. The rounding happens exactly once, here.

Two of the decimal counts in this module do more than set the display, and
their comments say so. `CONCENTRATION_DISPLAY_DECIMALS` and
`FLOW_DISPLAY_DECIMALS` set the slider steps, so they decide which settings can
reach the model. The concentration resolution also sets the smallest inspired
fraction from which an F_A/F_I ratio is formed. So a finer count is a change to
the model's inputs, not only to its text.

The precision of an agent amount depends on its unit as well as on the amount
(`PL-0S0V`). The same amount shown in litres of vapour and in millilitres of
liquid needs two derivations, one for each unit. So
`AGENT_AMOUNT_DISPLAY_PRECISION` holds one entry for each pair of amount and
unit, and formatting an amount in a unit with no entry is refused.

The module has two display units and one resolution. A compartment's partial
pressure is shown as a percent of one atmosphere and as a multiple of 1 MAC of
the agent in use. The MAC multiple is the unit that clinicians reason in, and
the only one that means the same thing when the agent changes. The MAC multiple
is the percent divided by a per-agent constant. So `MAC_DISPLAY_DECIMALS` is
*derived* from `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` rather than chosen
separately. One stated resolution governs both units. A re-derived percent
resolution therefore carries through to the MAC readout without a second
derivation. `docs/MODEL.md` § "MAC multiples as a display unit" states what that
division does and does not assert. A MAC multiple is a statement about a partial
pressure, never about a depth of anesthesia. The divisor is a tier-3 parameter,
and the interface displays its provenance.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app_metadata import APP_BUILD_VERSION, APP_VERSION_IS_KNOWN
from anesthesia_sim.core.concentration import (
    Fraction,
    MacMultiple,
    MacPercent,
    percent_from_fraction,
    require_mac_percent,
)
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S
from anesthesia_sim.core.units import SECONDS_PER_HOUR, SECONDS_PER_MINUTE

__all__ = [
    "AGENT_AMOUNT_DISPLAY_PRECISION",
    "CHART_AXIS_TOP_MAC",
    "CHART_GRID_INTERVAL_MAC",
    "CONCENTRATION_DISPLAY_DECIMALS",
    "CONCENTRATION_DISPLAY_RESOLUTION_PERCENT",
    "DECIMAL_BASE",
    "AgentAmount",
    "AgentAmountUnit",
    "AgentAmountPrecision",
    "FLOW_DISPLAY_DECIMALS",
    "MAC_AXIS_STEP_LADDER_MAC",
    "MAC_DISPLAY_DECIMALS",
    "MAC_DISPLAY_RESOLUTION_MAC",
    "MAC_UNIT_SUFFIX",
    "MAX_MAC_AXIS_INTERVALS",
    "WASH_IN_DISPLAY_DECIMALS",
    "agent_amount_display_precision",
    "chart_axis_top_percent",
    "chart_grid_interval_percent",
    "format_agent_residual",
    "format_agent_volume",
    "format_branch_discard_warning",
    "format_case_discard_warning",
    "format_chart_time_label",
    "format_delivered_label",
    "format_elapsed",
    "format_flow",
    "format_mac_awake_reference",
    "format_mac_multiple",
    "format_mac_reference",
    "format_percent",
    "format_playback_rate",
    "format_subtitle",
    "format_time_base",
    "format_wash_in_ratio",
    "mac_awake_band_percent",
    "mac_axis_ticks",
    "mac_multiple",
    "render_mac_multiple",
]

# Every displayed resolution is a power of this base. A value shown to `n`
# decimals has a resolution of `DECIMAL_BASE**-n`. A slider that steps at that
# resolution counts its position in those steps
# (`dashboard_frame.slider_position`).
DECIMAL_BASE: Final = 10.0

# Displayed resolution for every modeled concentration and relative partial
# pressure, and for the delivered-agent setting shown beside its slider.
#
# **A choice, inside a band the model imposes.** `docs/MODEL.md` § "Displayed
# precision" derives the band as one to two decimals. The upper end of the band
# is set by what the measured spread of the partition coefficients supports.
# The lower end is set by the fat and muscle compartments. At one decimal they
# show a flat `0.0%` for minutes to an hour, which erases the wash-in that the
# simulator exists to teach. Two decimals is the project owner's choice inside
# that band (PL-040, re-affirmed 2026-09-03 under `PL-88GQ`). One decimal is
# ruled out by a teaching judgment, not by a numerical limit.
#
# So moving this count to one decimal is the owner's decision. The move would
# need no re-derivation in `core/`, because no model-side bound is computed
# from this count. Moving it to three decimals would leave the band. That is a
# safety-critical change, because three decimals would assert a resolution that
# the parameters do not support. Revise the documented derivation along with it.
# The figures behind both ends of the band are in that section and are
# deliberately not restated here.
#
# **This count also sets two things outside the display** (`PL-0S0V`). It sets
# the delivered dial's slider step, through `ParameterControl.decimals`, so it
# decides which dial settings can reach the model. And `app/wash_in.py` derives
# `WASH_IN_DENOMINATOR_FLOOR_FRACTION` from the resolution below. That constant
# is the smallest inspired fraction from which an F_A/F_I ratio may be formed.
# One more decimal moves that floor down by a factor of ten.
CONCENTRATION_DISPLAY_DECIMALS: Final = 2
# Smallest percentage-point difference the concentration readouts resolve.
CONCENTRATION_DISPLAY_RESOLUTION_PERCENT: Final = DECIMAL_BASE**-CONCENTRATION_DISPLAY_DECIMALS

# Decimals shown on a flow readout and on the flow sliders' drag labels.
#
# **A choice, and revisable** (`PL-88GQ`). No model bound sets it. A flow is a
# setting that the reader dialled, not a modelled output being rounded. One
# decimal is used because flowmeters are read at that resolution, so the number
# on screen matches what the same setting looks like on a machine. Changing it
# re-derives nothing in `core/`.
#
# **It is not display-only.** `ParameterControl.decimals` in
# `app/dashboard_frame.py` reads it to set each flow slider's step, so it also
# sets which flows a reader can apply to the model (`PL-25KS`). A second decimal
# would make 0.05 L/min steps reachable inputs. `CONCENTRATION_DISPLAY_DECIMALS`
# sets the delivered dial's step the same way.
FLOW_DISPLAY_DECIMALS: Final = 1


class AgentAmount(Enum):
    """Which agent amount a displayed precision was derived for.

    A precision is derived for an amount *in a unit*, not for the amount
    alone (`PL-0S0V`). So this enum is the first half of the key of
    `AGENT_AMOUNT_DISPLAY_PRECISION`, and `AgentAmountUnit` is the second.
    The three totals are separate members because one unit can suit one
    total and not another. The stored total, converted to liquid, comes out
    5.8% too high. The delivered and exhausted agent convert exactly.

    Attributes:
        DELIVERED: The agent a run has delivered. The accounting panel and the
            agent cost View show it.
        EXHAUSTED: The agent a run has exhausted. The accounting panel shows it.
        STORED: The agent a run holds in the circuit and the body. The
            accounting panel shows it.
        COMPARTMENT: One compartment's amount, which the compartment schematic
            labels. `PL-2881` derives its precision. Until then, this amount has
            no entry in any unit, so formatting it is refused.
    """

    DELIVERED = "delivered total"
    EXHAUSTED = "exhausted total"
    STORED = "stored total"
    COMPARTMENT = "compartment's amount"


class AgentAmountUnit(Enum):
    """The unit that an agent amount is shown in, used as a key of the precision table.

    A member identifies a unit but does not say how the unit is written.
    `PL-2881` will decide how each unit is written beside a value, and those
    spellings will be `DisplayUnit` members. Every member names whether it
    measures vapour or liquid. About 183 mL of sevoflurane vapour come from
    1 mL of liquid, so a bare "mL" cannot say which is meant.

    Attributes:
        LITRES_OF_VAPOUR: Litres of pure agent vapour at the model's reference
            condition (`docs/MODEL.md` § "Agent amount").
        MILLILITRES_OF_LIQUID: Millilitres of the liquid agent that the vapour
            came from, converted with `AgentParameters.vapour_volume_per_liquid_volume`.
        MILLILITRES_OF_VAPOUR: Millilitres of pure agent vapour at the same
            reference condition.
    """

    LITRES_OF_VAPOUR = "litres of vapour"
    MILLILITRES_OF_LIQUID = "millilitres of liquid"
    MILLILITRES_OF_VAPOUR = "millilitres of vapour"


# Each entry below is the finest number of decimals that `docs/MODEL.md`
# § "Displayed precision" derives for one agent amount in one unit. That section
# holds the figures behind each count, and this comment does not restate them.
#
# - A run total in litres of vapour has one decimal, the finest that the
#   parameters support (`PL-TG60`). All three totals use it, so the accounting
#   panel shows them on one scale.
# - The delivered total in millilitres of liquid has one decimal (project owner,
#   2026-10-27, ratified, over whole millilitres). The delivered agent is the
#   vaporizer dial setting times the fresh gas flow times the time, so no
#   partition coefficient makes it uncertain. Once it is converted to liquid,
#   its only uncertainty comes from the measured density. One SD of the density
#   moves the liquid figure by 0.1 mL only above about 190 mL of liquid. The
#   litre display of this total is coarser than 0.1 mL of liquid. That is
#   allowed, because the bound is one-sided: it limits how fine a display may
#   be, not how coarse.
# - The exhausted total in millilitres of liquid has no decimals. One step of
#   the litre display, 0.1 L of vapour, is about half a millilitre of liquid
#   for every shipped agent. 1 mL is the finest power of ten that is no finer
#   than that step. So the litre and millilitre displays claim the same
#   resolution for the same amount.
#
# A pair of amount and unit with no entry has no derivation behind it. It is
# refused rather than shown at a default precision. The stored total has no
# liquid entry, because a store converted to liquid comes out 5.8% too high.
# That error is more than 1 mL once the store holds about 17 mL of liquid. A
# compartment's amount has no entry until `PL-2881` derives one. Money has no
# entry here, because the resolution of a cost depends on the price that the
# reader sets. `PL-1P15` derives that resolution.
_RUN_TOTAL_LITRE_DECIMALS: Final = 1
_FINEST_DERIVED_DECIMALS: Final[Mapping[tuple[AgentAmount, AgentAmountUnit], int]] = (
    MappingProxyType(
        {
            **{
                (total, AgentAmountUnit.LITRES_OF_VAPOUR): _RUN_TOTAL_LITRE_DECIMALS
                for total in (AgentAmount.DELIVERED, AgentAmount.EXHAUSTED, AgentAmount.STORED)
            },
            (AgentAmount.DELIVERED, AgentAmountUnit.MILLILITRES_OF_LIQUID): 1,
            (AgentAmount.EXHAUSTED, AgentAmountUnit.MILLILITRES_OF_LIQUID): 0,
        }
    )
)


def _finest_derived_decimals(amount: AgentAmount, unit: AgentAmountUnit) -> int:
    """Return the finest count derived for an amount in a unit, or refuse the pair."""

    try:
        return _FINEST_DERIVED_DECIMALS[(amount, unit)]
    except KeyError:
        raise ValueError(
            f"No displayed precision is derived for a {amount.value} in {unit.value}. "
            "Derive one in the section 'Displayed precision' of docs/MODEL.md and add it to "
            "app/formatting.py before showing this amount in this unit."
        ) from None


@dataclass(frozen=True)
class AgentAmountPrecision:
    """The decimal count an agent amount is shown at, checked against its derivation.

    The derived count is an upper bound only (`PL-0S0V`). Showing fewer
    decimals than the derivation admits loses detail but claims nothing false.
    Showing more claims a resolution that the model's parameters or its
    conversion factors do not support. So a finer count is refused when the
    precision is built, rather than clamped to the bound. The bound is read
    from the derivation for the amount and unit, never passed in by the
    caller. So if a reader is ever allowed to set a precision, building it
    through this type will still stop it from being finer than the derivation.

    Attributes:
        amount: Which agent amount is shown.
        unit: The unit it is shown in.
        decimals: The number of decimals shown.

    Raises:
        ValueError: If no precision is derived for the amount in the unit, if
            `decimals` is not a whole number of 0 or more, or if it is finer
            than the derived count.
    """

    amount: AgentAmount
    unit: AgentAmountUnit
    decimals: int

    def __post_init__(self) -> None:
        finest = _finest_derived_decimals(self.amount, self.unit)

        if (
            isinstance(self.decimals, bool)
            or not isinstance(self.decimals, int)
            or self.decimals < 0
        ):
            raise ValueError(
                f"A displayed precision must be a whole number of decimals of 0 or more, "
                f"not {self.decimals!r}."
            )

        if self.decimals > finest:
            raise ValueError(
                f"{self.decimals} decimals is finer than the {finest} that docs/MODEL.md "
                f"section 'Displayed precision' derives for a {self.amount.value} in "
                f"{self.unit.value}. A finer count would claim a resolution the model does "
                "not support, so it is refused."
            )

    @property
    def finest_decimals(self) -> int:
        """Return the finest count derived for this amount in this unit."""

        return _finest_derived_decimals(self.amount, self.unit)

    @property
    def resolution(self) -> float:
        """Return the smallest difference that this count of decimals resolves."""

        return DECIMAL_BASE**-self.decimals


# The precision each agent amount is shown at, in each unit it has a
# derivation for. Every one is shown at the finest count derived for it.
AGENT_AMOUNT_DISPLAY_PRECISION: Final[
    Mapping[tuple[AgentAmount, AgentAmountUnit], AgentAmountPrecision]
] = MappingProxyType(
    {
        (amount, unit): AgentAmountPrecision(amount, unit, finest)
        for (amount, unit), finest in _FINEST_DERIVED_DECIMALS.items()
    }
)


def agent_amount_display_precision(
    amount: AgentAmount, unit: AgentAmountUnit
) -> AgentAmountPrecision:
    """Return the displayed precision for an agent amount in a unit.

    Args:
        amount: Which agent amount is shown.
        unit: The unit it is shown in.

    Returns:
        The precision that `docs/MODEL.md` § "Displayed precision" derives
        for that amount in that unit.

    Raises:
        ValueError: If no precision has been derived for that amount in that
            unit. A unit offered with no derivation behind it fails here rather
            than being shown at a default precision.
    """

    _finest_derived_decimals(amount, unit)

    return AGENT_AMOUNT_DISPLAY_PRECISION[(amount, unit)]


# The precision of the accounting panel's three amounts, which share one count.
_RUN_TOTAL_LITRES: Final = agent_amount_display_precision(
    AgentAmount.DELIVERED, AgentAmountUnit.LITRES_OF_VAPOUR
)

# Decimals shown on a MAC multiple, and the resolution that follows from them.
# This value is *derived*, not chosen. A MAC multiple is a percent divided by
# the agent's own `mac_percent`, so the percent resolution above already fixes
# how finely the quotient is known. Stating a second, independent resolution
# would mean re-deriving two numbers whenever the first is re-derived
# (`docs/MODEL.md` § "Displayed precision" gives the reason). The rule fits in
# one line: use the finest power of ten that is nowhere finer than the percent
# resolution converted into MAC. That conversion depends on the agent. A step
# of 0.01 percentage points is 0.005 MAC for sevoflurane, 0.0083 for isoflurane
# and 0.0017 for desflurane. So the binding agent is the one with the largest
# quotient, isoflurane at 0.0083 MAC, and 0.01 is the finest power of ten at or
# above it. `test_the_mac_resolution_is_derived_from_the_percent_resolution` in
# `tests/unit/test_formatting.py` repeats that arithmetic for every shipped
# agent. So adding an agent or changing the percent resolution makes that test
# fail, rather than letting this value silently over-claim.
MAC_DISPLAY_DECIMALS: Final = 2
#: Smallest difference in MAC multiples the readouts resolve.
MAC_DISPLAY_RESOLUTION_MAC: Final = DECIMAL_BASE**-MAC_DISPLAY_DECIMALS

# The unit written after a MAC multiple. It is read from the unit's
# `DisplayUnit` member, which explains why the multiplication sign matters.
MAC_UNIT_SUFFIX: Final = f" {DisplayUnit.MAC_MULTIPLE.label}"

# The label written after a concentration in percent, read from its
# `DisplayUnit` member.
_PERCENT: Final = DisplayUnit.CONCENTRATION.label

# Candidate spacings for the chart's MAC axis, coarsest last. `mac_axis_ticks`
# takes the first spacing that keeps the axis within `MAX_MAC_AXIS_INTERVALS`
# intervals, so the spacing depends on the plotted range, not on the agent.
# Since PL-CC23 that range is `CHART_AXIS_TOP_MAC` for every agent. So the
# ladder selects 0.5 MAC for all of them by construction, not by coincidence.
# That lets a reader carry one mental scale from one agent to the next. It is
# still a ladder rather than a constant, because the range is the input: a
# chart drawn over a different span picks its own spacing.
MAC_AXIS_STEP_LADDER_MAC: Final = (0.25, 0.5, 1.0, 2.0, 5.0)
#: The most intervals the MAC axis may have before the next coarser spacing is used.
MAX_MAC_AXIS_INTERVALS: Final = 10

# Top of the compartment chart, as a multiple of the running agent's 1 MAC.
#
# The axis is denominated in MAC, so it is the *same ruler for every agent*,
# and that is its whole purpose. Until PL-CC23 the top was the agent's
# vaporizer dial maximum: 3.00 MAC of desflurane, 4.00 of sevoflurane and 4.17
# of isoflurane. So the same case plotted under two agents was drawn at two
# scales differing by 1.39x. A learner comparing desflurane's wash-in with
# sevoflurane's was comparing shapes that had been silently rescaled. No label
# prevents that misreading.
#
# Three is not a round number chosen for tidiness. It is exactly
# desflurane's dial maximum (18 % / 6 % = 3.00). So the shared ceiling is
# anchored to a real device limit rather than to a preference, and the agent
# whose vaporizer is most limited has no empty band at the top of its plot.
# A ceiling of three also puts 1 MAC at one third of the plot height,
# comfortably inside the plot rather than on its frame, which a 2 MAC ceiling
# could not do. And it keeps on the plot the 2-3x MAC range in which
# overpressure induction works.
#
# **Fixed, and fixed for the whole session rather than only within a run.**
# An axis that grew to fit an excursion would redraw a rising curve at a
# smaller height partway through a lesson. A reader would then attribute that
# change of shape to the model rather than to the axis. The section "Why the
# axis is fixed rather than fitted" in `docs/MODEL.md` settled the same
# question for the wash-in plot, and its reasoning applies here too. Because
# the axis is also fixed across the session, two consecutive runs can be
# compared as well.
#
# Sevoflurane and isoflurane can be dialled above this ceiling. For example,
# 8 % is 4.00 MAC and is a common inhalational-induction setting. So a trace
# can leave the top of the plot. The interface reports that, rather than
# letting the trace look like a plateau (see
# `dashboard_frame.OFF_SCALE_NOTICE_TEMPLATE`).
CHART_AXIS_TOP_MAC: Final = 3.0

# Spacing of the compartment chart's horizontal rules, in MAC. It is
# denominated in MAC for the same reason as the ceiling. Until PL-CC23 the
# interval was a fixed 2 *percent*. That drew a rule every 0.5 MAC for
# sevoflurane, every 1.67 MAC for isoflurane and every 0.33 MAC for desflurane.
# One plot had nine lines and another had three, and none of them sat at a
# value a reader looks for. At half a MAC the rules land on the same values
# that `mac_axis_ticks` labels, so the axis names every gridline on the plot.
CHART_GRID_INTERVAL_MAC: Final = 0.5

# Decimals shown on an F_A/F_I ratio, both on the chart's axis and in the
# reading beside it. This value is not derived from the concentration
# resolution above, and it is deliberately not presented as though it were.
# The ratio's own resolution depends on its denominator. So early in wash-in, a
# run knows the quotient far less finely than it does at equilibrium, and a
# single derived figure would over-claim at one end or waste a digit at the
# other. Instead, the value is set by what the ratio is compared against.
# Yasuda et al. report F_A/F_I at 30 minutes as 0.850, 0.733 and 0.90, with
# standard deviations of 0.018, 0.027 and 0.01
# (`docs/MODEL.md` § "Published wash-in and elimination validation test").
# A third decimal would be finer than the published spread that this trace
# exists to be read beside.
WASH_IN_DISPLAY_DECIMALS: Final = 2


def format_percent(partial_pressure_fraction: Fraction) -> str:
    """Convert a partial-pressure-equivalent fraction to display percent.

    The value is rendered at `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`, the
    resolution that `docs/MODEL.md` § "Displayed precision" derives.

    A value that is positive but rounds to zero is rendered as below the
    resolution, not as zero. That distinction matters. Muscle and fat stay
    below 0.01% for the first minutes of a run, and fat stays there for
    thirteen minutes at 1 MAC sevoflurane. Showing `0.00%` there would
    assert that a compartment is empty when the model says it is filling.
    `<0.01%` says only what is known, and leaves `0.00%` with its proper
    meaning, that nothing has arrived yet.

    A negative fraction is never given the below-resolution form, because
    that form would absorb it into a plausible-looking reading. No
    `Fraction` can hold a negative value, and since `PL-LLMN` that includes
    minus zero. So a negative value that reaches this function came as a
    bare `float` from a caller that `mypy` does not check.
    `percent_from_fraction` refuses it before anything is rendered. Since
    `PL-1DP1` it refuses the value because it was never built as a
    `Fraction`, whatever the value is. Before that, `PL-4R3W` refused it
    because it was out of range. Until `PL-4R3W`, a negative value was
    rendered with its sign, as the anomaly it is. Refusing it is the
    stronger form of the same rule.

    Args:
        partial_pressure_fraction: Dimensionless partial-pressure-equivalent
            fraction from zero through one.

    Returns:
        Concentration as percent at the displayed resolution, or the
        below-resolution form for a positive value that rounds to zero.

    Raises:
        TypeError: The value was not built as a `Fraction`. This includes a
            bare `float`, whatever its value. `percent_from_fraction` refuses
            such a value before anything is rendered, and its error names the
            constructor to use (`core/concentration.py`, `PL-1DP1`).
    """

    percent = percent_from_fraction(partial_pressure_fraction)
    rendered = f"{percent:.{CONCENTRATION_DISPLAY_DECIMALS}f}"

    if percent > 0.0 and float(rendered) == 0.0:
        resolution = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT

        return f"<{resolution:.{CONCENTRATION_DISPLAY_DECIMALS}f}{_PERCENT}"

    return f"{rendered}{_PERCENT}"


def mac_multiple(partial_pressure_fraction: Fraction, mac_percent: MacPercent) -> MacMultiple:
    """Convert a partial-pressure-equivalent fraction to multiples of 1 MAC.

    This function holds all the arithmetic of the second display unit, in one
    place. So the transformation that `docs/MODEL.md` § "MAC multiples as a
    display unit" specifies can be read and tested without a formatter or a
    control around it.

    The returned number claims less than it seems to, and that section of
    the specification states its meaning in full. In short, it is this
    compartment's partial pressure expressed as a multiple of the *alveolar*
    concentration that would be 1 MAC. On the alveolar compartment, that is
    the conventional reading. On the circuit, mixed venous, vessel-rich,
    muscle and fat compartments, it is a partial-pressure ratio and nothing
    more. MAC is defined for an alveolar concentration in a nominal
    40-year-old, and this model has no age, no second agent, and no
    depth-of-anesthesia endpoint.

    Args:
        partial_pressure_fraction: Dimensionless partial-pressure-equivalent
            fraction from zero through one.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere, from `SimulationSnapshot.agent_mac_percent`. It is
            passed in rather than looked up. The divisor is what makes the
            number agent-specific, so it travels with the value it divides.
            It is not read from a module-level default, which could outlive
            an agent change.

    Returns:
        The concentration as a multiple of the agent's 1 MAC.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`. A
            `MacPercent` is checked once, when it is built, to be above zero,
            so a divisor of zero cannot reach this function
            (`core/concentration.py`, `PL-F9TC`).
        TypeError: the fraction was not built as a `Fraction`.
            `percent_from_fraction` refuses it, as `format_percent` says.
    """

    require_mac_percent("mac_percent", mac_percent)

    return MacMultiple(percent_from_fraction(partial_pressure_fraction) / mac_percent)


def format_mac_multiple(partial_pressure_fraction: Fraction, mac_percent: MacPercent) -> str:
    """Render a partial-pressure-equivalent fraction as a MAC multiple.

    It follows the same three rules as `format_percent`, for the same
    reasons, at this unit's own derived resolution. It rounds rather than
    truncates. It marks a positive value that rounds to zero as below the
    resolution, instead of showing it as `0.00`. It refuses a value that was
    never built as a `Fraction`, an impossible negative among them, rather
    than absorbing it. `mac_multiple` makes that check before anything is
    rendered.

    The below-resolution form matters more here than in percent, not less.
    0.01 MAC is 0.02 percentage points of sevoflurane and 0.06 of
    desflurane. So a compartment's value reaches this unit's last digit
    later than it reaches the last digit of the percent readout beside it.
    A `0.00 ×MAC` on a fat compartment that the percent line already shows
    filling would make the two readouts contradict each other.

    Args:
        partial_pressure_fraction: Dimensionless partial-pressure-equivalent
            fraction from zero through one.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        The MAC multiple at the displayed resolution with its unit, or
        the below-resolution form for a positive value that rounds to
        zero.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`, or the
            fraction was not built as a `Fraction`. `mac_multiple` refuses
            each of them.
    """

    return render_mac_multiple(mac_multiple(partial_pressure_fraction, mac_percent))


def render_mac_multiple(multiple: MacMultiple) -> str:
    """Render a value that is already a MAC multiple, with its unit.

    This is the rendering half of `format_mac_multiple`. It is split out for
    values that arrive as a multiple rather than as a fraction and a divisor.
    The only such value is the height of a `bookmarks.MacTarget`. It is one
    function rather than two copies of the same three rules, because a
    target listed at `0.8 ×MAC` beside a readout showing `0.80 ×MAC` would
    look like two quantities where there is one, and the reader would have
    to work out whether the target had been met.

    Args:
        multiple: The value, as a multiple of the running agent's 1 MAC.

    Returns:
        The multiple at the displayed resolution with its unit, or the
        below-resolution form for a positive value that rounds to zero.
    """

    rendered = f"{multiple:.{MAC_DISPLAY_DECIMALS}f}"

    if multiple > 0.0 and float(rendered) == 0.0:
        resolution = MAC_DISPLAY_RESOLUTION_MAC

        return f"<{resolution:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX}"

    return f"{rendered}{MAC_UNIT_SUFFIX}"


def format_mac_reference(agent_display_name: str, mac_percent: MacPercent) -> str:
    """State the divisor every MAC multiple on screen was produced with.

    `CLAUDE.md` requires a clinically meaningful displayed value to be
    traceable to the exact transformation that produced it. A MAC multiple
    has exactly one free parameter, the MAC it divides by. Naming that MAC
    on the display, beside the axis it scales, makes the readouts traceable
    without opening a data file. A reader who disagrees with the divisor can
    see that they disagree, and can convert back.

    The value is deliberately shown to one decimal, which is the
    precision the three stored values actually carry. `docs/MODEL.md`
    § "Delivery-limit and MAC parameters" gives their provenance and the
    limitation that follows from it.

    Args:
        agent_display_name: Running agent's display name.
        mac_percent: That agent's 1 MAC as a percent of one atmosphere.

    Returns:
        A one-line statement of the agent's 1 MAC in percent.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`, which
            refuses a zero MAC when it is built (`core/concentration.py`,
            `PL-F9TC`). A zero MAC would print `1 MAC = 0.0%`.
    """

    require_mac_percent("mac_percent", mac_percent)

    return f"1 MAC {agent_display_name.lower()} = {mac_percent:.1f}{_PERCENT}"


def mac_awake_band_percent(
    *,
    fraction_of_mac: MacMultiple,
    standard_deviation_fraction_of_mac: MacMultiple,
    mac_percent: MacPercent,
) -> tuple[float, float]:
    """Place the MAC-awake band on the chart's percent axis, as (lower, upper).

    The stored value is a fraction of the agent's own MAC. The chart plots
    percent of one atmosphere. This function makes that one multiplication,
    in one place, so the band's height on a labelled axis can be tested
    without a chart around it. `docs/MODEL.md` § "MAC-awake as a chart
    reference" states what the band asserts and which trace it is read
    against.

    The band multiplies the *fraction* by the stored `mac_percent`, rather
    than storing an absolute percent. That keeps the band's height
    consistent with the axis it is drawn on, by construction. A published
    MAC-awake percent was measured in a population that has its own MAC. For
    desflurane, that MAC is not this project's. Chortkoff's 2.60% sits
    against a MAC of 7.25%. Importing that percent onto an axis scaled by a
    MAC of 6.0% would raise the band by 20%. Concentration falls during
    washout, so a trace crosses a band drawn too high sooner. That band would
    teach an earlier wake-up than the source supports.

    Every argument is keyword-only. The fraction and its standard deviation
    are two dimensionless numbers of the same magnitude. So a positional
    call is one transposition away from drawing a band ten times too wide,
    centered on the spread rather than the mean. Nothing in the type system
    would catch it.

    Args:
        fraction_of_mac: Population MAC-awake as a fraction of this
            agent's 1 MAC, from
            `SimulationSnapshot.agent_mac_awake.fraction_of_mac`.
        standard_deviation_fraction_of_mac: That population's standard
            deviation, in the same fraction-of-MAC unit. The band is one
            standard deviation either side of the mean, so it spans
            roughly the middle two thirds of the population rather than
            its full range.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere. It is passed in beside the fraction it scales, for
            the reason `mac_multiple` gives. The divisor is what makes the
            number agent-specific.

    Returns:
        The band's lower and upper edges, both as a percent of one
        atmosphere, lower first.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`. A
            `MacPercent` is checked once, when it is built, to be above zero,
            so a divisor of zero cannot reach this function
            (`core/concentration.py`, `PL-F9TC`).
        ValueError: If the band's lower edge would not be strictly
            positive. That band cannot be drawn. `CLAUDE.md` requires an
            obvious failure over a plausible-looking number. The
            loader's `_MacAwakePayload` already makes it unreachable from
            a shipped data file, so one arriving here means something
            upstream is wrong.
    """

    require_mac_percent("mac_percent", mac_percent)

    lower_fraction = fraction_of_mac - standard_deviation_fraction_of_mac

    if not lower_fraction > 0.0:
        raise ValueError(
            "the MAC-awake band's lower edge must be strictly positive, got "
            f"{fraction_of_mac!r} - {standard_deviation_fraction_of_mac!r}"
        )

    upper_fraction = fraction_of_mac + standard_deviation_fraction_of_mac

    return lower_fraction * mac_percent, upper_fraction * mac_percent


def format_mac_awake_reference(
    agent_display_name: str,
    *,
    fraction_of_mac: MacMultiple,
    standard_deviation_fraction_of_mac: MacMultiple,
    mac_percent: MacPercent,
) -> str:
    """State what the MAC-awake band was drawn from, in one line.

    This meets the same requirement that `format_mac_reference` meets for
    the MAC axis. A clinically meaningful mark on the display must be
    traceable to the exact values that produced it. The band has two free
    parameters rather than one: a published fraction and the divisor it is
    applied to. So both are named, together with the percent they land at.
    A reader who disagrees with either can see which one they disagree with.

    The fraction is shown at the resolution of the MAC readouts. The
    percents are shown at the resolution of the concentration readouts. So
    the line claims no more precision than the rest of the interface already
    does.

    Args:
        agent_display_name: Running agent's display name.
        fraction_of_mac: Population MAC-awake as a fraction of that
            agent's 1 MAC.
        standard_deviation_fraction_of_mac: That population's standard
            deviation, in the same unit.
        mac_percent: That agent's 1 MAC as a percent of one atmosphere.

    Returns:
        A one-line statement of the band's centre and its edges.

    Raises:
        TypeError, ValueError: For the inputs that `mac_awake_band_percent`
            refuses.
    """

    lower_percent, upper_percent = mac_awake_band_percent(
        fraction_of_mac=fraction_of_mac,
        standard_deviation_fraction_of_mac=standard_deviation_fraction_of_mac,
        mac_percent=mac_percent,
    )
    centre_percent = fraction_of_mac * mac_percent
    decimals = CONCENTRATION_DISPLAY_DECIMALS

    return (
        f"MAC-awake {agent_display_name.lower()} = "
        f"{fraction_of_mac:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX} "
        f"({centre_percent:.{decimals}f}{_PERCENT}), "
        f"band ±1 SD {lower_percent:.{decimals}f}–{upper_percent:.{decimals}f}{_PERCENT}"
    )


def chart_axis_top_percent(mac_percent: MacPercent) -> float:
    """Give the compartment chart's axis top, in percent, for one agent.

    The chart plots percent, so the axis top has to be passed to it in
    percent. But the top is *chosen* in MAC, at `CHART_AXIS_TOP_MAC`, which
    makes it the same ruler for every agent. The comment on that constant
    explains why it is three, why it is fixed, and what it replaced.

    Args:
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        Top of the chart's percent axis.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`, which
            refuses a zero MAC when it is built (`core/concentration.py`,
            `PL-F9TC`). A zero MAC would give an axis of zero height, and a
            chart drawn against one would place every trace somewhere
            meaningless rather than failing.
    """

    require_mac_percent("mac_percent", mac_percent)

    return CHART_AXIS_TOP_MAC * mac_percent


def chart_grid_interval_percent(mac_percent: MacPercent) -> float:
    """Give the compartment chart's horizontal rule spacing, in percent.

    This makes the same conversion as `chart_axis_top_percent`, for the
    same reason, from `CHART_GRID_INTERVAL_MAC`. The chart's grid interval
    is a percent, but the spacing it stands for is a MAC multiple. So every
    agent's chart has its rules at the same fractions of MAC.

    Args:
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        Spacing between the chart's horizontal rules, in percent.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`, as
            `chart_axis_top_percent` says.
    """

    require_mac_percent("mac_percent", mac_percent)

    return CHART_GRID_INTERVAL_MAC * mac_percent


def mac_axis_ticks(max_percent: float, mac_percent: MacPercent) -> tuple[tuple[float, str], ...]:
    """Place the chart's MAC axis labels against a percent-valued axis.

    The chart plots percent, and always has. A MAC axis reads the same
    traces against a second ruler. It is not a second set of points. So
    nothing here converts a plotted value, and the two axes cannot come to
    disagree about a trace. Each tick is returned as the percent position
    it sits at and the MAC number written beside it.

    Ticks land on round MAC values rather than on round percentages, which
    is the point of the axis. A reader looks for 1 MAC, not for whatever
    multiple 2% happens to be. The spacing is the finest step in
    `MAC_AXIS_STEP_LADDER_MAC` that keeps the axis within
    `MAX_MAC_AXIS_INTERVALS` intervals. So a wider plotted range gets
    coarser labels instead of crowded ones.

    Args:
        max_percent: Top of the chart's percent axis, which is what the
            MAC axis is placed against.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        Ticks from zero upward, each as (percent position, MAC label).
        Empty if the plotted range is not positive, which leaves the
        axis unlabelled rather than inventing a scale for it.

    Raises:
        TypeError: `mac_percent` was not built as a `MacPercent`, as
            `chart_axis_top_percent` says.
    """

    require_mac_percent("mac_percent", mac_percent)

    if not max_percent > 0.0:
        return ()

    span_mac = max_percent / mac_percent
    step_mac = next(
        (step for step in MAC_AXIS_STEP_LADDER_MAC if span_mac / step <= MAX_MAC_AXIS_INTERVALS),
        MAC_AXIS_STEP_LADDER_MAC[-1],
    )
    # Use one decimal for a half-MAC step, two for a quarter-MAC step and none
    # for whole-MAC steps. The count is derived from the spacing rather than
    # fixed, so a label never shows a digit that the spacing cannot change.
    decimals = max(0, len(f"{step_mac:.2f}".rstrip("0").partition(".")[2]))

    return tuple(
        (index * step_mac * mac_percent, f"{index * step_mac:.{decimals}f}")
        # `int()` truncates toward zero, so the last tick is the last one
        # at or below the top of the axis. The `+ 1` makes the range include
        # that tick. A tick above `max_percent` would be drawn outside the
        # plotted area.
        for index in range(int(span_mac / step_mac) + 1)
    )


def format_wash_in_ratio(wash_in_ratio: float) -> str:
    """Render an F_A/F_I ratio as the dimensionless number it is.

    The result has no unit suffix and no percent sign, because the quantity
    has neither. It is one fraction of an atmosphere divided by another.
    Writing it as a percentage would invite a reader to compare it with the
    concentration axis beside it. `app/wash_in.py` states what the quotient
    asserts and where it is defined at all. This function only writes it
    down.

    Args:
        wash_in_ratio: The dimensionless quotient F_A/F_I.

    Returns:
        The ratio at `WASH_IN_DISPLAY_DECIMALS`.
    """

    return f"{wash_in_ratio:.{WASH_IN_DISPLAY_DECIMALS}f}"


def format_flow(flow_l_min: float) -> str:
    """Render a flow setting in litres per minute, at the slider's own resolution.

    There is one definition for the three flow settings rather than one per
    display site. The readout beside a slider, the slider's own drag label
    and the control-input timeline are three renderings of one number. If two
    of them disagreed by half a litre a minute, that would be the same class
    of failure as a concentration shown at two resolutions. That is why
    `FLOW_DISPLAY_DECIMALS` exists, and why no other code should write
    `:.1f` beside it.
    """

    return f"{flow_l_min:.{FLOW_DISPLAY_DECIMALS}f} {DisplayUnit.FLOW.label}"


def format_elapsed(elapsed_s: float) -> str:
    """Render simulated time as the interface states it everywhere.

    It uses the compound, self-describing form, such as `45s`, `1m30s`,
    `1h23m45.6s` or `24h`. So the clock, every recorded control change
    stamped against it, and the chart's own axis state one quantity in one
    way.

    **This function used to render `5400.0 s` and the reasoning for it was
    wrong in a checkable way** (`PL-Q4M4`, `PL-CZFY`). It said the two forms
    could not be one function because "a compound duration form would round
    the stamp away". That is not true of the compound form that shipped.
    `_duration_components` returns the seconds as a float, and the label
    formats them with `:g`, so the tenth of a second that the simulation
    steps at survives, as in `1h23m45.6s`. Both forms met the stamp's
    requirement, so the only argument left for two forms was that one of
    them had been written first.

    Two forms left a reader converting between them. `PL-SSBP` gave the
    chart a time base that spans a case. Finding a control mark stamped
    `5400.0 s` on an axis reading `1h30m` then meant dividing by 3600 by
    hand, on a screen that showed both at once. `PL-Y5WR` declared a
    24-hour envelope, so the clock's top reading became `86400.0 s`. That
    is seven characters, down to tenths, for a quantity a reader thinks
    about in hours. `format_supported_run_length` below had already refused
    to reuse the old form for exactly that reason.

    **Raises an error rather than rendering a negative or non-finite
    time**, through `_duration_components`. The previous form would have
    printed `-1.0 s` without complaint. Simulated time cannot run
    backwards, so a negative value is a fault upstream, and `CLAUDE.md`
    prefers an obvious failure to a plausible-looking displayed number.

    `format_chart_time_label` uses the same form with one deliberate
    difference, which its docstring explains: the axis origin is a bare
    `0`.

    Args:
        elapsed_s: Simulated time since the run began, in seconds.

    Returns:
        The duration in compound form, `0s` at the run's start.

    Raises:
        ValueError: If `elapsed_s` is negative or not finite.
    """

    return _format_duration_compound(elapsed_s, zero="0s")


def format_supported_run_length() -> str:
    """State the supported run length the way a reader thinks about a case.

    The length is given in hours and computed from
    `core.supported_ranges.MAXIMUM_ELAPSED_SIMULATION_TIME_S` rather than
    from a number written here. So the interface cannot state a limit that
    the model does not enforce.

    This function still does not use `format_elapsed`, but no longer for
    the reason first recorded here. That reason was false precision:
    `format_elapsed` rendered "86400.0 s", so this function had to say
    "24 hours" instead. The reason stopped applying when `PL-CZFY` moved
    the clock onto the compound form, where the same instant reads "24h".
    The remaining reason is register. This string goes into a sentence that
    a reader reads ("runs are supported to 24 hours"), where the spelled-out
    unit belongs. `format_time_base` does the same when it spells out
    "15 minutes" for a selector entry whose axis tick reads "15m". The two
    forms now agree about the quantity and differ only in how they are read.
    """

    return f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} hours"


def format_playback_rate(multiplier: int) -> str:
    """Return the label for the playback rate that is set, as a multiple of real time.

    The string states the setting, not whether the clock is moving. A paused,
    reset or halted run still shows the rate it plays at, and the status word
    in the transport row says whether the run is running. `docs/MODEL.md`
    § "Interface boundary" defines the label this way (`PL-SQJ1`, `PL-X4X2`).

    The rate is a mode. This project's interface rules exist to prevent a mode
    that nobody can see. A clock advancing at 60x beside numbers that look like
    a live case is easy to misread at a glance. So this function renders a label
    at every rate, including real time, where it gives "1x real time" rather than
    nothing. With no label at 1x, the label's *presence* would become the signal.
    A reader who has not learned that convention would take a missing label to
    mean a missing mode, not the default one.

    One function serves both places where the rate appears: the control
    that sets it, and the line under the clock that reports it. So the two
    cannot state the same mode differently. `docs/MODEL.md` § "Interface
    boundary" requires the rate to be shown wherever simulated time is
    shown. The interface meets that requirement by rendering this string,
    never by writing its own.

    The label says "Real time" rather than "wall clock" because a reader
    compares the rate with the pace of a case they have stood through. The
    rate is a multiple of that pace. Simulated time itself is rendered by
    `format_elapsed`, in simulated seconds, and remains the only clock on
    the display. This string names the pace at which the clock advances
    while the run plays, and is never a second reading of the time.

    Args:
        multiplier: Simulated seconds advanced per second of real time, as
            `app/playback.py` defines it. It is a whole number by
            construction. `app/playback.py` rejects a rate that does not
            land on a whole number of simulation steps per tick, so such a
            rate is never displayed here.

    Returns:
        The rate as the interface states it, using the multiplication sign
        the MAC readouts already use.
    """

    return f"{multiplier}\u00d7 real time"


def _duration_components(duration_s: float) -> tuple[int, int, float]:
    """Split a duration into whole hours, whole minutes and the rest.

    Args:
        duration_s: A duration in seconds.

    Returns:
        `(hours, minutes, seconds)`, the last carrying any fraction.

    Raises:
        ValueError: If the duration is negative or not finite.
    """

    if not isfinite(duration_s) or duration_s < 0.0:
        raise ValueError(f"duration must be finite and non-negative, got {duration_s!r}")

    hours = int(duration_s // SECONDS_PER_HOUR)
    minutes = int((duration_s - hours * SECONDS_PER_HOUR) // SECONDS_PER_MINUTE)

    return hours, minutes, duration_s - hours * SECONDS_PER_HOUR - minutes * SECONDS_PER_MINUTE


def _format_duration_compound(duration_s: float, *, zero: str) -> str:
    """Render a duration as `1h23m45.6s`, dropping components that are zero.

    This is the one place where the compound form is built. So the clock,
    the recorded control-change stamps and the chart's axis ticks cannot
    drift into stating one quantity in two ways (`PL-Q4M4`). Every component
    carries its own unit. The axis under a time base can span anything from
    a minute to half a day. A bare number would then mean seconds on one
    scale and hours on another, while looking identical on both.

    Seconds are formatted with `:g`, which keeps a tenth where there is one
    and drops a trailing `.0` where there is not. So a stamp resolves the
    `0.1 s` step that the simulation advances by, and a tick on a whole
    number of seconds is not padded with a digit that says nothing.

    Args:
        duration_s: A duration in seconds.
        zero: What to return when the duration is exactly zero. The two
            callers want different text here, and this is the only way they
            differ. That is why it is a parameter rather than a branch at
            each call site.

    Returns:
        The duration in compound form.

    Raises:
        ValueError: If the duration is negative or not finite.
    """

    hours, minutes, seconds = _duration_components(duration_s)

    if hours == 0 and minutes == 0 and seconds == 0.0:
        return zero

    parts = []

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if seconds:
        parts.append(f"{seconds:g}s")

    return "".join(parts)


def format_chart_time_label(elapsed_s: float) -> str:
    """Render one tick on the chart's simulated-time axis.

    The label is compact and self-describing: `0`, `45s`, `3m`, `1m30s`,
    `2h`, `1h30m`. Every component carries its own unit, and that is the
    purpose of the form. The axis under a time base can span anything from
    a minute to half a day. A bare number would then mean seconds on one
    scale and hours on another, while looking identical on both. That is
    the worst failure available, because a reader who misses the caption
    has nothing in the label to correct them. The unit letters make the
    tick readable without the caption, and without knowing which time base
    is selected.

    The run's start is deliberately a bare `0`. A `0s` label invites
    reading the whole axis as seconds, and the origin needs no unit to be
    understood.

    The form is the same as `format_elapsed`'s, on purpose. A reader looking
    for a control mark stamped `1h30m` on this axis reads the stamp and the
    tick in one register, rather than converting between two (`PL-Q4M4`).
    Both show a tenth of a second only where one is present. That is right
    for the axis because the ladder in `app/chart_time_base.py` places every
    tick on a whole number of seconds, so a trailing `.0` on every label
    would be noise. It is right for `format_elapsed` because a stamp has to
    resolve the `0.1 s` step that the simulation advances by.

    Args:
        elapsed_s: Simulated time of the tick, in seconds since the run
            began.

    Returns:
        The label text.

    Raises:
        ValueError: If `elapsed_s` is negative or not finite. An axis label
            is a clinically meaningful displayed value. `CLAUDE.md`'s
            standard prefers a failure to a plausible-looking label produced
            from an impossible time.
    """

    return _format_duration_compound(elapsed_s, zero="0")


def format_time_base(span_s: float) -> str:
    """Name a chart time base's width, as prose.

    This text is what the selector's entries show, and what the axis caption
    says the chart is showing. It is spelled out, as in `15 minutes`,
    `1 hour` or `12 hours`, rather than in `format_chart_time_label`'s
    compact form. A reader chooses from this text and reads it back, so it
    is not a tick competing for width. The two forms agree about the
    quantity and differ only in register. For example, the caption naming
    `15 minutes` sits above an axis whose last tick reads `15m`.

    Args:
        span_s: The width of the visible window, in seconds.

    Returns:
        The width in words.

    Raises:
        ValueError: If `span_s` is negative or not finite.
    """

    hours, minutes, seconds = _duration_components(span_s)
    parts = []

    if hours:
        parts.append(f"{hours} {_plural('hour', hours)}")

    if minutes:
        parts.append(f"{minutes} {_plural('minute', minutes)}")

    # Every rung of `TIME_BASE_LADDER` is a whole number of minutes, so the
    # selector can never produce a seconds term. The term is still spelled out
    # rather than rounded away. Folding a remainder into the minutes above it
    # would name a width that the chart is not drawing.
    if seconds or not parts:
        parts.append(f"{seconds:g} {_plural('second', seconds)}")

    return " ".join(parts)


def _plural(noun: str, count: float) -> str:
    """Return the noun, pluralized for the count that precedes it."""

    return noun if count == 1 else f"{noun}s"


#: The ending of both discard warnings: what is lost, and that the loss is final.
_DISCARD_CONSEQUENCE: Final = (
    "will be discarded along with its chart history. This cannot be undone."
)


def format_case_discard_warning(
    agent_display_name: str, elapsed_s: float, control_change_count: int
) -> str:
    """State what starting a new case is about to throw away.

    The warning names the two recorded things that a reader can see on
    screen and that a new case destroys beyond recovery: the simulated time
    the run reached, and the control changes it recorded. Both are stated in
    the terms of the display they will disappear from. The time uses
    `format_elapsed`, as the clock does. The count is of the grouped
    adjustments that the "Control changes" panel lists, not of the raw
    `ControlChange` entries behind them. So a reader comparing the warning
    with the panel finds the same number.

    This function lives here rather than in the view for the same reason as
    every other display string in this module. What a reader is told is a
    question of presentation correctness, and this string can be read and
    tested without loading the Qt toolkit.

    Args:
        agent_display_name: The agent the current run is using.
        elapsed_s: Simulated time the current run has reached, in seconds.
        control_change_count: How many recorded control changes the run
            has, counted the way `control_timeline.group_adjustments` groups
            them and the panel beside the chart lists them.

    Returns:
        One sentence naming the run and what discarding it costs.
    """

    return (
        f"The current {agent_display_name.lower()} case — "
        f"{format_elapsed(elapsed_s)} of simulated time, "
        f"{_recorded_control_changes(control_change_count)} — {_DISCARD_CONSEQUENCE}"
    )


def format_branch_discard_warning(
    run_name: str, began_at_s: float, elapsed_s: float | None, control_change_count: int
) -> str:
    """State what a trunk's Reset is about to throw away from one branch that it ends.

    This is the branch's counterpart of `format_case_discard_warning`, in the
    same words, because discarding a branch costs the same two things and
    nothing restores either (`PL-W5WX`). A branch uses the case's clock, so
    its simulated time is stated as two instants that the clock shows, not as
    a duration: the instant at which it branched, and the instant it has run
    to. A reader can check both against the branch's own clock and the label
    of the branch control.

    The second instant is left out when it would say nothing: when the
    branch has not run past its fork, or when its time could not be read
    because its snapshot refuses a value. The warning then states only what
    is known, and never a number that nothing produced.

    Args:
        run_name: What the branch is called on screen (`run_label`).
        began_at_s: The case instant the branch began at, its fork.
        elapsed_s: The case instant the branch has run to, or None where it
            could not be read.
        control_change_count: How many recorded control changes the branch
            has, counted the way the "Control changes" panel lists them.

    Returns:
        One sentence naming the branch and what discarding it costs.

    Raises:
        ValueError: If either instant is negative or not finite, through
            `format_elapsed`.
    """

    span = f"branched at {format_elapsed(began_at_s)}"

    if elapsed_s is not None and elapsed_s > began_at_s:
        span += f" and run to {format_elapsed(elapsed_s)}"

    return (
        f"{run_name} — {span}, {_recorded_control_changes(control_change_count)} — "
        f"{_DISCARD_CONSEQUENCE}"
    )


def _recorded_control_changes(count: int) -> str:
    """Return how many recorded control changes are about to be lost, in the warnings' words."""

    return "1 recorded control change" if count == 1 else f"{count} recorded control changes"


def format_subtitle(agent_display_name: str) -> str:
    """Build the header subtitle naming the current app build and agent.

    The subtitle names the build rather than the version, because every
    build between two releases carries the same version string. That made a
    merged fix indistinguishable from the code it replaced when the project
    owner went to confirm it by eye (`PL-QC38`, `PL-YKF8`).
    `app_metadata.py`'s `APP_BUILD_VERSION` adds the commit for anything
    that is not a clean checkout of the released tag, and adds nothing for a
    release.

    **When the version could not be read at all, the line says so rather
    than naming a version.** `app_metadata.py` falls back to
    `UNKNOWN_VERSION` when installed-package metadata is missing, as in a
    frozen or bundled build or a corrupted install. That fallback policy is
    right, because failing visibly is better than crashing on launch. What
    was wrong was where the visible failure appeared. Substituted into the
    sentence below, the fallback produced "Version unknown". This subtitle
    is the interface's only link between a displayed number and the model
    that produced it. So a reader saw a provenance field that seemed to give
    a version when there was none (`PL-KCWD`). `CLAUDE.md` requires a
    displayed value to be traceable to the exact model and version behind
    it. A build that cannot offer that has to say so. An unidentified build
    is precisely the one whose numbers must not be quoted later as if they
    came from a known version.

    Args:
        agent_display_name: The running agent, as it is named to a reader.

    Returns:
        The header subtitle.
    """

    if not APP_VERSION_IS_KNOWN:
        return (
            "Version unavailable (this build is not traceable) — "
            f"{agent_display_name} patient model"
        )

    return f"Version {APP_BUILD_VERSION} — {agent_display_name} patient model"


def format_delivered_label(agent_display_name: str) -> str:
    """Build the delivered-concentration panel label naming the agent."""

    return f"Delivered {agent_display_name.lower()}"


def format_agent_volume(litres: float) -> str:
    """Render an agent amount from the accounting panel in litres of agent gas.

    The amount is rendered at the precision that
    `AGENT_AMOUNT_DISPLAY_PRECISION` holds for the run totals in litres of
    vapour. `docs/MODEL.md` § "Displayed precision" derives it (`PL-TG60`).
    This function follows the same three rules as `format_percent`, for the
    same reasons. First, it rounds rather than truncates. Second, it marks a
    positive value that rounds to zero as below the resolution, rather than
    showing it as `0.0 L`. In the first minute of a run the exhausted and
    stored amounts are real and small. There, `0.0 L` would assert that
    nothing has left the circuit when the model says it has. Third, it never
    hides an impossible negative amount behind a plausible reading. A
    `Fraction` refuses a negative for `format_percent`, but an amount has no
    checked type that does so. So this function leaves a negative amount
    visible, as the anomaly it is. Exactly zero is shown as zero, which is the
    amount before a run starts.

    Args:
        litres: The amount, in litres of equivalent pure agent gas.

    Returns:
        The amount at the displayed resolution with its unit, or the
        below-resolution form for a positive value that rounds to zero.
    """

    decimals = _RUN_TOTAL_LITRES.decimals
    rendered = f"{litres:.{decimals}f}"

    if litres > 0.0 and float(rendered) == 0.0:
        return f"<{_RUN_TOTAL_LITRES.resolution:.{decimals}f} L"

    return f"{rendered} L"


def format_agent_residual(litres: float) -> str:
    """Render a residual of the accounting panel as the power of ten it lies below.

    This function renders the unaccounted amount and the absolute error. Those
    two lines exist to show how far below the amounts' resolution the
    conservation check sits. At 1e-12 L, the fixed form of
    `format_agent_volume` would show `0.0 L` and say nothing (`PL-TG60`). Each
    line instead prints the smallest power of ten that its magnitude is
    strictly less than. So `5.601e-14` is shown as `<1e-13 L`, where the `<`
    means the same as it does on the amounts above.

    **The decade is the only meaningful digit in the value** (`PL-3PJZ`). A
    passing residual is the rounding error left over from summing four
    amounts. Its mantissa and its sign are set by the order in which the
    arithmetic ran, not by anything modelled, and a correct last-bit change
    to the propagator changes them. `docs/MODEL.md` § "Displayed precision"
    has the measurement. Any finer form would print a digit that is noise.
    So both lines use the same form. The signed values are still shown when
    they mean something: a failing check halts the run, and the failure
    notice prints them to six figures.

    Exactly zero is shown as `0 L`. A value that is not finite cannot come
    out of the accounting check. If one arrives, it is printed as itself
    rather than as a bound, so the anomaly is visible instead of absorbed
    into a plausible reading.

    Args:
        litres: The residual, in litres of equivalent pure agent gas.

    Returns:
        The bound with its unit, such as `<1e-13 L`, or `0 L` for exactly zero.
    """

    if not isfinite(litres):
        return f"{litres} L"

    if litres == 0.0:
        return "0 L"

    # `Decimal` stores the float's exact binary value, so `adjusted()` is the
    # exact floor of its base-10 logarithm. `math.log10` rounds instead. The
    # float written `1e-16` is exactly 9.99...e-17, yet `math.log10` returns
    # -16.0 for it, which would print the decade above the one the value is in.
    exponent = Decimal(abs(litres)).adjusted() + 1

    return f"<1e{exponent:+03d} L"
