"""Render modeled values as the strings the interface displays.

Pure formatting, independent of Flet and of the scientific core: every
function here takes a number the model produced and returns the text a
reader sees. Nothing in this module builds a control, reads simulation
state, or performs a physiological calculation.

Why it is its own module. `docs/MODEL.md` § "Displayed precision" is a
derivation - from what the model's parameters can support, to how many digits
of a concentration are worth showing - and this is where that derivation
terminates. `CLAUDE.md` treats presentation correctness as part of the safety
standard and requires a displayed value to be traceable to the transformations
that produced it, so the last transformation in that chain has to be readable,
citable and testable on its own rather than reachable only by loading the whole
dashboard. `tests/unit/test_formatting.py` is what pins it.

Nothing here restates that derivation's figures, deliberately. They were
restated at four sites in this package and every one of them went stale
together when the solver changed (`PL-X9KD`); the section is cited instead, so
the next re-derivation reaches one place.

The displayed resolution is a property of the display alone. Everything
upstream carries full binary64 - the compartment states, every integration
step, every `SimulationHistorySample` - and the rounding happens exactly
once, here.

Two display units, one resolution. A compartment is shown as a percent of
one atmosphere and as a multiple of the running agent's 1 MAC, which is the
unit clinicians reason in and the only one that means the same thing when
the agent changes. The second is the first divided by a per-agent constant,
so `MAC_DISPLAY_DECIMALS` is *derived* from
`CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` rather than chosen beside it -
one stated resolution governs both, and re-deriving the percent resolution
propagates to the MAC readout without a second derivation. What that
division does and does not assert is `docs/MODEL.md` § "MAC multiples as a
display unit"; it is a statement about a partial pressure, never about a
depth of anesthesia, and the divisor is a tier-3 parameter whose provenance
the interface displays.
"""

from math import isfinite
from typing import Final

from anesthesia_sim.app_metadata import APP_BUILD_VERSION
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S

__all__ = [
    "CHART_AXIS_TOP_MAC",
    "CHART_GRID_INTERVAL_MAC",
    "CONCENTRATION_DISPLAY_DECIMALS",
    "CONCENTRATION_DISPLAY_RESOLUTION_PERCENT",
    "FLOW_DISPLAY_DECIMALS",
    "MAC_AXIS_STEP_LADDER_MAC",
    "MAC_DISPLAY_DECIMALS",
    "MAC_DISPLAY_RESOLUTION_MAC",
    "MAC_UNIT_SUFFIX",
    "MAX_MAC_AXIS_INTERVALS",
    "WASH_IN_DISPLAY_DECIMALS",
    "chart_axis_top_percent",
    "chart_grid_interval_percent",
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
]

# Displayed resolution for every modeled concentration and relative partial
# pressure, and for the delivered-agent setting shown beside its slider.
#
# **A choice, inside a band the model imposes.** `docs/MODEL.md` § "Displayed
# precision" derives the band as one to two decimals: bounded above by what the
# partition coefficients' measured spread supports, and below by the fat and
# muscle compartments reading a flat `0.0%` for minutes to an hour at one
# decimal, which erases the wash-in the simulator exists to teach. Two is the
# project owner's pick inside that band (PL-040, re-affirmed 2026-09-03 under
# `PL-88GQ`), and the reason one is not taken is a teaching judgment rather
# than a numerical limit.
#
# So moving this to one decimal is the owner's to make and re-derives nothing
# in `core/`: no model-side bound is computed from it. Moving it to three would
# leave the band and is a safety-critical change, because it would assert a
# resolution the parameters do not support - revise the documented derivation
# with it. The figures behind both halves live in that section and are
# deliberately not restated here.
CONCENTRATION_DISPLAY_DECIMALS: Final = 2
# Smallest percentage-point difference the concentration readouts resolve.
CONCENTRATION_DISPLAY_RESOLUTION_PERCENT: Final = 10.0**-CONCENTRATION_DISPLAY_DECIMALS

# Decimals shown on the flow sliders' drag labels, matching the ".1f L/min"
# readouts beside them. Flet's default is 0, which would make a slider's own
# label disagree with the text next to it mid-drag.
#
# **A choice, and revisable** (`PL-88GQ`). No model bound sets it: a flow is a
# setting the reader dialled rather than a modelled output being rounded, and
# the sliders carry no `divisions`, so a value reaches `core/` unquantized and a
# second decimal would display something real rather than noise. One decimal is
# taken because it is the resolution flowmeters are read at, so the number on
# screen matches what the same setting looks like on a machine. Changing it
# re-derives nothing.
FLOW_DISPLAY_DECIMALS: Final = 1

# Decimals shown on a MAC multiple, and the resolution that follows. This is
# *derived*, not chosen: a MAC multiple is a percent divided by the agent's
# own `mac_percent`, so the percent resolution above already fixes how finely
# the quotient is known, and stating a second independent resolution would
# mean re-deriving two numbers whenever the first is re-derived (the reason is
# in `docs/MODEL.md` § "Displayed precision"). The rule is one line: the
# finest power of ten that is nowhere finer than the percent resolution
# converted into MAC. That conversion is agent-specific — 0.01 percentage
# points is 0.005 MAC for sevoflurane, 0.0083 for isoflurane and 0.0017 for
# desflurane — so the binding agent is the one with the largest quotient,
# isoflurane at 0.0083 MAC, and 0.01 is the finest power of ten at or above
# it. `test_the_mac_resolution_is_derived_from_the_percent_resolution` in
# `tests/unit/test_formatting.py` re-runs that arithmetic against every
# shipped agent, so adding an agent or changing the percent resolution fails
# there rather than silently over-claiming here.
MAC_DISPLAY_DECIMALS: Final = 2
#: Smallest difference in MAC multiples the readouts resolve.
MAC_DISPLAY_RESOLUTION_MAC: Final = 10.0**-MAC_DISPLAY_DECIMALS

# The unit written after a MAC multiple. The multiplication sign is doing
# safety work rather than typographic work: "0.80 MAC" is read as a depth of
# anesthesia, and "0.80 ×MAC" as what the number actually is — a partial
# pressure expressed as a multiple of the concentration that would be 1 MAC.
# `docs/MODEL.md` § "MAC multiples as a display unit" states the convention
# the interface is holding a reader to here.
MAC_UNIT_SUFFIX: Final = " \u00d7MAC"

# Candidate spacings for the chart's MAC axis, coarsest last. `mac_axis_ticks`
# takes the first that keeps the axis within `MAX_MAC_AXIS_INTERVALS`, so the
# spacing is a function of the plotted range rather than of the agent. Since
# PL-CC23 that range is `CHART_AXIS_TOP_MAC` for every agent, so the ladder
# selects 0.5 MAC for all of them by construction rather than by coincidence -
# which is what lets a reader carry one mental scale from one agent to the
# next. It remains a ladder rather than a constant because the range is the
# input: a chart drawn over a different span picks its own spacing.
MAC_AXIS_STEP_LADDER_MAC: Final = (0.25, 0.5, 1.0, 2.0, 5.0)
#: Most gaps the MAC axis may be divided into before the next coarser spacing.
MAX_MAC_AXIS_INTERVALS: Final = 10

# Top of the compartment chart, as a multiple of the running agent's 1 MAC.
#
# The axis is denominated in MAC and is therefore the *same ruler for every
# agent*, which is the whole point of it: until PL-CC23 the top was the
# agent's vaporizer dial maximum, which is 3.00 MAC of desflurane, 4.00 of
# sevoflurane and 4.17 of isoflurane, so the same case plotted under two
# agents was drawn at two scales differing by 1.39x. A learner comparing
# desflurane's wash-in to sevoflurane's was comparing shapes that had been
# silently rescaled, which is a misreading no label prevents.
#
# Three is not a round number chosen for tidiness. It is exactly
# desflurane's dial maximum (18 % / 6 % = 3.00), so the shared ceiling is
# anchored to a real device limit rather than to a preference, and the agent
# whose vaporizer is most limited gets no dead band at the top of its plot.
# It also puts 1 MAC at one third of the plot height - comfortably inside it
# rather than on the frame, which a 2 MAC ceiling could not do - and leaves
# the 2-3x MAC range that overpressure induction works in on the plot.
#
# **Fixed, and fixed for the whole session rather than only within a run.**
# An axis that grew to fit an excursion would redraw a rising curve at a
# smaller height partway through a lesson, and a reader would attribute that
# shape change to the model rather than to the axis. `docs/MODEL.md`'s "Why
# the axis is fixed rather than fitted" settled the same question for the
# wash-in plot; the reasoning transfers, and being fixed across the session
# as well means two consecutive runs are comparable too.
#
# Sevoflurane and isoflurane can be dialled above this ceiling - 8 % is
# 4.00 MAC and is a common inhalational-induction setting - so a trace
# can leave the top of the plot. That is reported rather than left to look
# like a plateau; see `simulation_view.OFF_SCALE_NOTICE_TEMPLATE`.
CHART_AXIS_TOP_MAC: Final = 3.0

# Spacing of the compartment chart's horizontal rules, in MAC. Denominated in
# MAC for the same reason the ceiling is: until PL-CC23 the interval was a
# fixed 2 *percent*, which rules sevoflurane every 0.5 MAC, isoflurane every
# 1.67 MAC and desflurane every 0.33 MAC - nine lines on one plot and three
# on another, none of them at a value a reader is looking for. At half a MAC
# the rules land on the same values `mac_axis_ticks` labels, so every gridline
# on the plot is one the axis names.
CHART_GRID_INTERVAL_MAC: Final = 0.5

# Decimals shown on an F_A/F_I ratio, on the chart's axis and in the reading
# beside it. Not derived from the concentration resolution above, and
# deliberately not presented as though it were: the ratio's own resolution
# depends on its denominator, so a run early in wash-in knows the quotient far
# less finely than one at equilibrium, and a single derived figure would
# over-claim at one end or waste a digit at the other. It is instead set by
# what the quantity is compared against - Yasuda et al. report F_A/F_I at
# 30 minutes as 0.850, 0.733 and 0.90 with standard deviations of 0.018, 0.027
# and 0.01 (`docs/MODEL.md` § "Published wash-in validation test"), so a third
# decimal would be finer than the published spread this trace exists to be read
# beside.
WASH_IN_DISPLAY_DECIMALS: Final = 2


def format_percent(concentration_fraction: float) -> str:
    """Convert a concentration fraction to display percent.

    Renders at `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`, the resolution
    `docs/MODEL.md` § "Displayed precision" derives.

    A value that is positive but rounds to zero is rendered as below the
    resolution rather than as zero. The distinction is the point: muscle
    and fat sit under 0.01% for the first minutes of a run — fat for
    thirteen of them at 1 MAC sevoflurane — and `0.00%` there would
    assert a compartment is empty when the model says it is filling.
    `<0.01%` says only what is known, and leaves `0.00%` meaning what it
    should, that nothing has arrived yet.

    A negative fraction is deliberately not given the below-resolution
    form. The compartment guards make one impossible, so if one ever
    reaches here it must stay visible as the anomaly it is rather than
    be absorbed into a plausible-looking reading.

    Args:
        concentration_fraction: Dimensionless concentration
            fraction from zero through one.

    Returns:
        Concentration as percent at the displayed resolution, or the
        below-resolution form for a positive value that rounds to zero.
    """

    percent = concentration_fraction * 100.0
    rendered = f"{percent:.{CONCENTRATION_DISPLAY_DECIMALS}f}"

    if percent > 0.0 and float(rendered) == 0.0:
        resolution = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT

        return f"<{resolution:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"

    return f"{rendered}%"


def mac_multiple(concentration_fraction: float, mac_percent: float) -> float:
    """Convert a concentration fraction to multiples of the agent's 1 MAC.

    The whole arithmetic of the second display unit, in one place, so the
    transformation `docs/MODEL.md` § "MAC multiples as a display unit"
    specifies can be read and tested without a formatter or a control
    around it.

    What the returned number asserts is narrower than it looks, and the
    specification section named above is where that is stated in full.
    In short: it is this compartment's partial pressure expressed as a
    multiple of the *alveolar* concentration that would be 1 MAC. On the
    alveolar compartment that is the conventional reading. On the
    circuit, mixed venous, vessel-rich, muscle and fat compartments it is
    a partial-pressure ratio and nothing more — MAC is defined for an
    alveolar concentration in a nominal 40-year-old, and this model has
    no age, no second agent, and no depth-of-anesthesia endpoint.

    Args:
        concentration_fraction: Dimensionless concentration fraction
            from zero through one.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere, from `SimulationSnapshot.agent_mac_percent`.
            Passed in rather than looked up: the divisor is what makes
            the number agent-specific, so it travels with the value it
            divides instead of being reachable from a module-level
            default that could outlive an agent change.

    Returns:
        The concentration as a multiple of the agent's 1 MAC.

    Raises:
        ValueError: If `mac_percent` is not strictly positive. A
            non-positive divisor cannot produce a meaningful multiple,
            and `CLAUDE.md` requires an obvious failure over a
            plausible-looking number — the loader's `PositivePercent`
            already makes one unreachable from a shipped data file, so
            one arriving here means something upstream is wrong.
    """

    if not mac_percent > 0.0:
        raise ValueError(f"mac_percent must be strictly positive, got {mac_percent!r}")

    return concentration_fraction * 100.0 / mac_percent


def format_mac_multiple(concentration_fraction: float, mac_percent: float) -> str:
    """Render a concentration fraction as a MAC multiple with its unit.

    The same three rules `format_percent` follows, for the same reasons,
    at this unit's own derived resolution: round rather than truncate,
    mark a positive value that rounds to zero as below the resolution
    instead of showing it as `0.00`, and leave an impossible negative
    visible as the anomaly it is.

    The below-resolution form matters more here than in percent, not
    less. 0.01 MAC is 0.02 percentage points of sevoflurane and 0.06 of
    desflurane, so a compartment clears this unit's last digit later than
    it clears the percent readout beside it — and a `0.00 ×MAC` on a fat
    compartment that the percent line already shows filling would be the
    two readouts contradicting each other.

    Args:
        concentration_fraction: Dimensionless concentration fraction
            from zero through one.
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        The MAC multiple at the displayed resolution with its unit, or
        the below-resolution form for a positive value that rounds to
        zero.

    Raises:
        ValueError: If `mac_percent` is not strictly positive.
    """

    multiple = mac_multiple(concentration_fraction, mac_percent)
    rendered = f"{multiple:.{MAC_DISPLAY_DECIMALS}f}"

    if multiple > 0.0 and float(rendered) == 0.0:
        resolution = MAC_DISPLAY_RESOLUTION_MAC

        return f"<{resolution:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX}"

    return f"{rendered}{MAC_UNIT_SUFFIX}"


def format_mac_reference(agent_display_name: str, mac_percent: float) -> str:
    """State the divisor every MAC multiple on screen was produced with.

    `CLAUDE.md` requires a clinically meaningful displayed value to be
    traceable to the exact transformation that produced it, and a MAC
    multiple has exactly one free parameter. Naming it on the display,
    beside the axis it scales, is what makes the readouts traceable
    without opening a data file: a reader who disagrees with the divisor
    can see that they disagree, and can convert back.

    The value is deliberately shown to one decimal, which is the
    precision the three stored values actually carry. `docs/MODEL.md`
    § "Delivery-limit and MAC parameters" holds their provenance and the
    limitation that follows from it.

    Args:
        agent_display_name: Running agent's display name.
        mac_percent: That agent's 1 MAC as a percent of one atmosphere.

    Returns:
        A one-line statement of the agent's 1 MAC in percent.
    """

    return f"1 MAC {agent_display_name.lower()} = {mac_percent:.1f}%"


def mac_awake_band_percent(
    *, fraction_of_mac: float, standard_deviation_fraction_of_mac: float, mac_percent: float
) -> tuple[float, float]:
    """Place the MAC-awake band on the chart's percent axis, as (lower, upper).

    The stored value is a fraction of the agent's own MAC; the chart plots
    percent of one atmosphere. This is that one multiplication, in the one
    place, so the band's height on a labelled axis is testable without a
    chart around it. `docs/MODEL.md` § "MAC-awake as a chart reference"
    states what the band asserts and which trace it is read against.

    Multiplying the *fraction* by the stored `mac_percent` — rather than
    storing an absolute percent — is what keeps the band's height and the
    axis it is drawn on consistent by construction. The population a
    published MAC-awake percent was measured in has its own MAC, and
    desflurane's is not this project's: Chortkoff's 2.60% sits against a MAC
    of 7.25%, so importing that percent onto an axis scaled by a MAC of 6.0%
    would raise the band by 20% and teach a later wake-up than the source
    supports.

    Every argument is keyword-only. The fraction and its standard deviation
    are two dimensionless numbers of the same magnitude, so a positional
    call is one transposition away from drawing a band ten times too wide
    centered on the spread rather than the mean, with nothing in the type
    system to catch it.

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
            atmosphere. Passed in beside the fraction it scales, for the
            reason `mac_multiple` gives: the divisor is what makes the
            number agent-specific.

    Returns:
        The band's lower and upper edges, both as a percent of one
        atmosphere, lower first.

    Raises:
        ValueError: If `mac_percent` is not strictly positive, or if the
            band's lower edge would not be. Neither is drawable, and
            `CLAUDE.md` requires an obvious failure over a
            plausible-looking number. The loader's `_MacAwakePayload`
            already makes both unreachable from a shipped data file, so
            one arriving here means something upstream is wrong.
    """

    if not mac_percent > 0.0:
        raise ValueError(f"mac_percent must be strictly positive, got {mac_percent!r}")

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
    fraction_of_mac: float,
    standard_deviation_fraction_of_mac: float,
    mac_percent: float,
) -> str:
    """State what the MAC-awake band was drawn from, in one line.

    The same requirement `format_mac_reference` answers for the MAC axis:
    a clinically meaningful mark on the display is traceable to the exact
    values that produced it. The band has two free parameters rather than
    one — a published fraction and the divisor it is applied to — so both
    are named, together with the percent they land at, and a reader who
    disagrees with either can see which one they disagree with.

    The fraction is shown at the MAC readouts' own resolution and the
    percents at the concentration readouts', so the line carries no digit
    the rest of the interface does not already stand behind.

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
        ValueError: For the inputs `mac_awake_band_percent` refuses.
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
        f"({centre_percent:.{decimals}f}%), "
        f"band ±1 SD {lower_percent:.{decimals}f}–{upper_percent:.{decimals}f}%"
    )


def chart_axis_top_percent(mac_percent: float) -> float:
    """Give the compartment chart's axis top, in percent, for one agent.

    The chart plots percent, so the ceiling has to be handed over in
    percent — but it is *chosen* in MAC, at `CHART_AXIS_TOP_MAC`, which
    is what makes it the same ruler for every agent. That constant
    carries why three, why fixed, and what it replaced.

    Args:
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        Top of the chart's percent axis.

    Raises:
        ValueError: If `mac_percent` is not strictly positive. A
            non-positive divisor would give an axis of zero or negative
            height, and a chart drawn against one would place every
            trace somewhere meaningless rather than failing.
    """

    if not mac_percent > 0.0:
        raise ValueError(f"mac_percent must be strictly positive, got {mac_percent!r}")

    return CHART_AXIS_TOP_MAC * mac_percent


def chart_grid_interval_percent(mac_percent: float) -> float:
    """Give the compartment chart's horizontal rule spacing, in percent.

    The same conversion `chart_axis_top_percent` makes, for the same
    reason and against `CHART_GRID_INTERVAL_MAC`: the chart's grid
    interval is a percent, and the spacing that percent stands for is a
    MAC multiple, so every agent is ruled at the same fractions of MAC.

    Args:
        mac_percent: The running agent's 1 MAC as a percent of one
            atmosphere.

    Returns:
        Spacing between the chart's horizontal rules, in percent.

    Raises:
        ValueError: If `mac_percent` is not strictly positive.
    """

    if not mac_percent > 0.0:
        raise ValueError(f"mac_percent must be strictly positive, got {mac_percent!r}")

    return CHART_GRID_INTERVAL_MAC * mac_percent


def mac_axis_ticks(max_percent: float, mac_percent: float) -> tuple[tuple[float, str], ...]:
    """Place the chart's MAC axis labels against a percent-valued axis.

    The chart plots percent and always has: a MAC axis is the same
    traces read against a second ruler, not a second set of points, so
    nothing here converts a plotted value and the two axes cannot come
    to disagree about a trace. Each tick is returned as the percent
    position it sits at and the MAC number written beside it.

    Ticks land on round MAC values rather than on round percentages,
    which is the point of the axis — a reader looks for 1 MAC, not for
    whatever multiple 2% happens to be. The spacing comes from
    `MAC_AXIS_STEP_LADDER_MAC`, taking the finest that keeps the axis
    within `MAX_MAC_AXIS_INTERVALS`, so a wider plotted range coarsens
    the labels instead of crowding them.

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
        ValueError: If `mac_percent` is not strictly positive.
    """

    if not mac_percent > 0.0:
        raise ValueError(f"mac_percent must be strictly positive, got {mac_percent!r}")

    if not max_percent > 0.0:
        return ()

    span_mac = max_percent / mac_percent
    step_mac = next(
        (step for step in MAC_AXIS_STEP_LADDER_MAC if span_mac / step <= MAX_MAC_AXIS_INTERVALS),
        MAC_AXIS_STEP_LADDER_MAC[-1],
    )
    # One decimal for a half-MAC step, two for a quarter-MAC one, none for
    # the whole-MAC steps: derived from the spacing rather than fixed, so a
    # label never shows a digit the spacing cannot move.
    decimals = max(0, len(f"{step_mac:.2f}".rstrip("0").partition(".")[2]))

    return tuple(
        (index * step_mac * mac_percent, f"{index * step_mac:.{decimals}f}")
        # `int()` truncates toward zero, so the last tick is the last one
        # at or below the top of the axis; `+ 1` makes the range inclusive
        # of it. A tick above `max_percent` would be drawn outside the
        # plotted area.
        for index in range(int(span_mac / step_mac) + 1)
    )


def format_wash_in_ratio(wash_in_ratio: float) -> str:
    """Render an F_A/F_I ratio as the dimensionless number it is.

    No unit suffix and no percent sign, because the quantity has neither:
    it is one fraction of an atmosphere divided by another, and writing it
    as a percentage would invite reading it against the concentration axis
    beside it. `app/wash_in.py` states what the quotient asserts and where
    it is defined at all; this only writes it down.

    Args:
        wash_in_ratio: The dimensionless quotient F_A/F_I.

    Returns:
        The ratio at `WASH_IN_DISPLAY_DECIMALS`.
    """

    return f"{wash_in_ratio:.{WASH_IN_DISPLAY_DECIMALS}f}"


def format_flow(flow_l_min: float) -> str:
    """Render a flow setting in litres per minute, at the slider's own resolution.

    One definition for the three flow settings rather than one per display
    site. The readout beside a slider, the slider's own drag label and the
    control-input timeline are three renderings of one number, and two of
    them disagreeing by half a litre a minute is the same class of failure
    as a concentration shown at two resolutions - which is why
    `FLOW_DISPLAY_DECIMALS` exists and why nothing should be spelling
    `:.1f` out beside it.
    """

    return f"{flow_l_min:.{FLOW_DISPLAY_DECIMALS}f} L/min"


def format_elapsed(elapsed_s: float) -> str:
    """Render simulated time as the interface states it everywhere.

    Seconds, one decimal, matching the simulation step the run advances by.
    The clock, and every recorded control change stamped against it, come
    through here: a timeline reading in one time format beside a clock
    reading in another would leave the reader converting between two
    displayed times of the same quantity.

    Seconds do not read well across a whole case, which is what v0.4.0's
    case-length time base is for. That is a change to how this project
    states simulated time rather than to one panel, so it belongs here, at
    the one place that decides it, and not in whichever display happens to
    be built first.

    The time base landed as `format_chart_time_label` below, and this
    function deliberately did *not* become it. The two render the same
    quantity for different readings and cannot be one function: a stamp
    beside a recorded control change has to resolve the simulation step it
    was taken at, which is a tenth of a second, while an axis tick on a
    twelve-hour span has to be legible at seven characters. A compound
    duration form would round the stamp away; a one-decimal second count
    would label that axis `43200.0 s`. See `format_chart_time_label` for
    which is used where.
    """

    return f"{elapsed_s:.1f} s"


def format_supported_run_length() -> str:
    """State the supported run length the way a reader thinks about a case.

    Hours, from `core.supported_ranges.MAXIMUM_ELAPSED_SIMULATION_TIME_S`
    rather than from a number written here, so the interface cannot state a
    limit the model does not enforce. `format_elapsed` above is deliberately
    not reused: it renders an instant to a tenth of a second, which is right
    for a clock beside a control change and reads as false precision on a
    boundary declared in hours - "86400.0 s" also asks a reader to divide
    before they can tell whether it is a plausible case length.
    """

    return f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} hours"


def format_playback_rate(multiplier: int) -> str:
    """State how fast simulated time is being played against real time.

    The rate is a mode, and a mode nobody can see is the failure this
    project's interface rules exist to prevent: a clock advancing at 60x
    beside numbers that look like a live case is misreadable at a glance.
    So this renders at every rate including real time - "1x real time"
    rather than nothing - because an absent label at 1x would make the
    label's *presence* the signal, and a reader who has not learned that
    convention reads a missing label as a missing mode rather than as the
    default one.

    One function for both places the rate appears - the control that sets
    it and the line under the clock that reports it - so the two cannot
    state the same mode differently. `docs/MODEL.md` § "Interface boundary"
    requires the rate wherever simulated time is shown, and the interface
    satisfies that by rendering this string, never by spelling one out.

    "Real time" rather than "wall clock": the comparison a reader makes is
    against the pace of a case they have stood through, and the multiple is
    of that pace. Simulated time itself is `format_elapsed`, in simulated
    seconds, and stays the only clock on the display - this names the pace
    the clock is advancing at and is never a second reading of the time.

    Args:
        multiplier: Simulated seconds advanced per second of real time, as
            `app/playback.py` defines it. A whole number by construction:
            a rate that did not land on a whole number of simulation steps
            per tick is refused there rather than displayed here.

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

    hours = int(duration_s // 3600.0)
    minutes = int((duration_s - hours * 3600.0) // 60.0)

    return hours, minutes, duration_s - hours * 3600.0 - minutes * 60.0


def format_chart_time_label(elapsed_s: float) -> str:
    """Render one tick on the chart's simulated-time axis.

    Compact and self-describing: `0`, `45s`, `3m`, `1m30s`, `2h`, `1h30m`.
    Every component carries its own unit, which is the point. The axis under
    a time base spans anything from a minute to half a day, so a bare number
    would mean seconds on one scale and hours on another while looking
    identical on both — the worst available failure, since a reader who
    misses the caption has nothing in the label to correct them. The unit
    letters make the tick readable without the caption and without knowing
    which time base is selected.

    Bare `0` for the run's start, deliberately. `0s` invites reading the
    whole axis as seconds, and the origin needs no unit to be understood.

    Not `format_elapsed`, which stamps a recorded time to the tenth of a
    second the simulation steps at. This rounds to whole seconds for whole
    values and shows a tenth only where one is present, because the ladder
    in `app/chart_time_base.py` places every tick on a whole number of
    seconds and a trailing `.0` on every label is noise.

    Args:
        elapsed_s: Simulated time of the tick, in seconds since the run
            began.

    Returns:
        The label text.

    Raises:
        ValueError: If `elapsed_s` is negative or not finite. An axis label
            is a clinically meaningful displayed value; a plausible-looking
            one produced from an impossible time is what `CLAUDE.md`'s
            standard prefers a failure to.
    """

    hours, minutes, seconds = _duration_components(elapsed_s)

    if hours == 0 and minutes == 0 and seconds == 0.0:
        return "0"

    parts = []

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if seconds:
        parts.append(f"{seconds:g}s")

    return "".join(parts)


def format_time_base(span_s: float) -> str:
    """Name a chart time base's width, as prose.

    What the selector's entries read and what the axis caption states the
    chart is showing. Spelled out — `15 minutes`, `1 hour`, `12 hours` —
    rather than in `format_chart_time_label`'s compact form, because this is
    a sentence a reader chooses from and reads back, not a tick competing
    for width. The two are consistent about the quantity and differ only in
    register; the caption naming `15 minutes` sits above an axis whose last
    tick reads `15m`.

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
    # seconds term is unreachable from the selector. It is spelled out rather
    # than rounded away because the alternative — folding a remainder into
    # the minutes above it — would name a width the chart is not drawing.
    if seconds or not parts:
        parts.append(f"{seconds:g} {_plural('second', seconds)}")

    return " ".join(parts)


def _plural(noun: str, count: float) -> str:
    """The noun, pluralized for the count that precedes it."""

    return noun if count == 1 else f"{noun}s"


def format_case_discard_warning(
    agent_display_name: str, elapsed_s: float, control_change_count: int
) -> str:
    """State what starting a new case is about to throw away.

    Names the two recorded things a reader can see on screen and that a new
    case destroys with nothing able to restore them: the simulated time the
    run reached, and the control changes it recorded. Both are quoted in the
    terms of the display they will disappear from — `format_elapsed` for the
    clock, and the grouped adjustments the "Control changes" panel lists
    rather than the raw `ControlChange` entries behind them, so a reader
    comparing the warning against the panel finds the same number.

    Here rather than in the view for the reason every other display string
    in this module is: what a reader is told is a presentation-correctness
    question, and this one can be read and tested without loading Flet.

    Args:
        agent_display_name: The agent the current run is using.
        elapsed_s: Simulated time the current run has reached, in seconds.
        control_change_count: How many recorded control changes the run
            holds, counted as `control_timeline.group_adjustments` groups
            them and as the panel beside the chart lists them.

    Returns:
        One sentence naming the run and what discarding it costs.
    """

    changes = (
        "1 recorded control change"
        if control_change_count == 1
        else f"{control_change_count} recorded control changes"
    )

    return (
        f"The current {agent_display_name.lower()} case — "
        f"{format_elapsed(elapsed_s)} of simulated time, {changes} — will be "
        "discarded along with its chart history. This cannot be undone."
    )


def format_subtitle(agent_display_name: str) -> str:
    """Build the header subtitle naming the current app build and agent.

    The build rather than the version, because between two releases every
    build carries the same version string - which is what made a merged fix
    indistinguishable from the code it replaced when the project owner went
    to confirm it by eye (`PL-QC38`, `PL-YKF8`). `app_metadata.py`'s
    `APP_BUILD_VERSION` adds the commit on anything that is not a clean
    checkout of the released tag, and adds nothing on a release.

    Args:
        agent_display_name: The running agent, as it is named to a reader.

    Returns:
        The header subtitle.
    """

    return f"Version {APP_BUILD_VERSION} — {agent_display_name} patient model"


def format_delivered_label(agent_display_name: str) -> str:
    """Build the delivered-concentration panel label naming the agent."""

    return f"Delivered {agent_display_name.lower()}"
