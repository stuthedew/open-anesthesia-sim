"""Render modeled values as the strings the interface displays.

Pure formatting, independent of Flet and of the scientific core: every
function here takes a number the model produced and returns the text a
reader sees. Nothing in this module builds a control, reads simulation
state, or performs a physiological calculation.

Why it is its own module. `docs/MODEL.md` § "Displayed precision" is a
derivation - from the shipped operator split's measured error, to how many
digits of a concentration are worth showing - and this is where that
derivation terminates. `CLAUDE.md` treats presentation correctness as part
of the safety standard and requires a displayed value to be traceable to
the transformations that produced it, so the last transformation in that
chain has to be readable, citable and testable on its own rather than
reachable only by loading the whole dashboard. `tests/unit/test_formatting.py`
is what pins it.

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

from typing import Final

from anesthesia_sim.app_metadata import APP_VERSION

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
    "format_delivered_label",
    "format_elapsed",
    "format_flow",
    "format_mac_awake_reference",
    "format_mac_multiple",
    "format_mac_reference",
    "format_percent",
    "format_subtitle",
    "format_wash_in_ratio",
    "mac_awake_band_percent",
    "mac_axis_ticks",
    "mac_multiple",
]

# Displayed resolution for every modeled concentration and relative partial
# pressure, and for the delivered-agent setting shown beside its slider. Two
# decimals of a percent — 0.01 percentage points — is a recorded decision
# (PL-040), justified in `docs/MODEL.md` § "Displayed precision" against the
# measured error of the shipped operator split. The short version: the
# split disagrees with the independent solution by up to 5e-3 percentage
# points at the default flows and 1.2e-2 at the extreme corner of the
# settings envelope, so the second decimal is the uncertain digit — as the
# last displayed digit should be — and the third and beyond were noise.
# Changing this is a safety-critical change to how a clinical value reads,
# not a formatting preference: revise the documented basis with it.
CONCENTRATION_DISPLAY_DECIMALS: Final = 2
# Smallest percentage-point difference the concentration readouts resolve.
CONCENTRATION_DISPLAY_RESOLUTION_PERCENT: Final = 10.0**-CONCENTRATION_DISPLAY_DECIMALS

# Decimals shown on the flow sliders' drag labels, matching the ".1f L/min"
# readouts beside them. Flet's default is 0, which would make a slider's own
# label disagree with the text next to it mid-drag.
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
# spacing is a function of the plotted range rather than of the agent: all
# three shipped agents land on 0.5 MAC at the current dial-maximum axis, which
# is what lets a reader carry one mental scale from one agent to the next.
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
# 4.00 MAC and is the standard inhalational-induction setting - so a trace
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

    Renders at `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`, the
    resolution `docs/MODEL.md` § "Displayed precision" justifies against
    the measured error of the shipped operator split.

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
    """

    return f"{elapsed_s:.1f} s"


def format_subtitle(agent_display_name: str) -> str:
    """Build the header subtitle naming the current app version and agent."""

    return f"Version {APP_VERSION} — {agent_display_name} patient model"


def format_delivered_label(agent_display_name: str) -> str:
    """Build the delivered-concentration panel label naming the agent."""

    return f"Delivered {agent_display_name.lower()}"
