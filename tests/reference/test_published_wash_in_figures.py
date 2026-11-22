"""Figures that `docs/VERIFICATION.md` prints beside the published wash-in comparison.

`docs/VERIFICATION.md` § "Published wash-in and elimination validation test"
explains its comparisons with figures that no comparison asserts: how much
agent the rebreathing circuit returns during an elimination, how fast the
vessel-rich group equilibrates, how close the stored coefficients lie to
Yasuda's brain:blood measurements, several properties of the published
five-exponential washout fits, and where the model's 24-hour washout departs
from them. Each test here computes one group of them, from the model or from
the stored published coefficients.

Each test reads its figures from the section as printed, with a narrow
pattern for the sentence that states them, as
`tests/reference/test_supported_input_range_figures.py` does, and compares
them at the number of decimal places the text prints. So a change to the
model that moves a figure fails here, and so does an edit to the text that
changes a figure without changing what it was computed from.

The model runs are the ones `tests/reference/test_published_wash_in_and_elimination.py`
drives. The published fits, the 24-hour washout curves and the model's
apparent muscle and fat terms are the ones
`tests/reference/test_late_washout_against_published_fits.py` records and
checks.
"""

from collections.abc import Callable, Sequence
from decimal import ROUND_HALF_UP, Decimal
from functools import cache

from test_late_washout_against_published_fits import (
    PUBLISHED_FITS,
    RECORDED_APPARENT_TERMS,
    PublishedWashoutFit,
    WashoutCurve,
    washout_curve,  # noqa: F401  # a fixture, which the tests below take by name
)
from test_parameter_source_figures import YASUDA_BRAIN_BLOOD
from test_published_wash_in_and_elimination import AGENT_IDS, FRESH_GAS_FLOW_L_MIN, _eliminate
from test_supported_input_range_figures import DOCS, _one, _section

from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters

#: Minutes in an hour, for the hours the late-washout paragraphs give.
MINUTES_PER_HOUR = 60

#: The index of each term of a five-exponential fit, fastest first.
MUSCLE_TERM = 2
FOURTH_TERM = 3
FAT_TERM = 4

#: The agents in the order the section lists their figures.
SECTION_ORDER = ("sevoflurane", "isoflurane", "desflurane")


@cache
def _section_text() -> str:
    return _section(
        DOCS / "VERIFICATION.md", "### Published wash-in and elimination validation test"
    )


def _printed(pattern: str) -> tuple[str, ...]:
    """The figures of the one sentence in the section that `pattern` matches."""

    return _one(pattern, _section_text())


def _as_printed(value: float, printed: str) -> str:
    """`value` rounded half away from zero to as many decimal places as `printed` has.

    A format string rounds half to even, so it would print 52.5 as 52 where
    the section prints 53.
    """

    places = len(printed.split(".")[1]) if "." in printed else 0

    return str(Decimal(repr(value)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def _assert_span(values: Sequence[float], low: str, high: str) -> None:
    """The lowest and highest of `values` are `low` and `high` as printed."""

    assert (_as_printed(min(values), low), _as_printed(max(values), high)) == (low, high), values


def _vessel_rich_tissue_blood(agent_id: str) -> float:
    """The stored vessel-rich tissue:gas coefficient over the stored blood:gas one."""

    agent = load_agent_parameters(agent_id)

    return (
        agent.vessel_rich_tissue_gas_partition_coefficient / agent.blood_gas_partition_coefficient
    )


def test_the_rebreathing_circuit_returns_about_three_tenths_of_the_alveolar_fraction() -> None:
    """F_I settles near V_A/(V_A + V_F) of F_A, and the runs give F_I/F_A of 0.30 to 0.32.

    The section explains the five-minute elimination's departure from the
    published cohorts by the circuit: during an elimination the inspired gas
    is circuit gas, so F_I settles near that share of F_A. It is 0.29 at the
    reference adult's 4 L/min and the comparison's 10 L/min of fresh gas.
    """

    share, low, high = _printed(
        r"That is (0\.\d+) at the highest supported flow, and the simulated value at five "
        r"minutes is (0\.\d+) to (0\.\d+)"
    )
    ventilation_l_min = load_reference_adult_parameters().default_alveolar_ventilation_l_min
    readings = [_eliminate(agent_id) for agent_id in AGENT_IDS]

    assert (
        _as_printed(ventilation_l_min / (ventilation_l_min + FRESH_GAS_FLOW_L_MIN), share) == share
    )
    _assert_span([r.inspired_fraction / r.alveolar_fraction for r in readings], low, high)


def test_the_alveolar_fraction_at_discontinuation_at_the_1_percent_dial_is_as_printed() -> None:
    """F_A0, in percent of an atmosphere, is the figure printed for each agent.

    The section gives these to say when the shipped alveolar trace falls below
    the readouts' resolution during the 24-hour washout.
    """

    printed = _printed(r"\$`F_\{A0\}`\$ is (0\.\d+), (0\.\d+) and (0\.\d+)% of an atmosphere")

    for agent_id, figure in zip(SECTION_ORDER, printed, strict=True):
        percent = 100 * _eliminate(agent_id).alveolar_fraction_at_discontinuation

        assert _as_printed(percent, figure) == figure, agent_id


def test_the_vessel_rich_group_s_time_constant_is_2_0_to_2_7_minutes() -> None:
    """The group's isolated time constant spans the minutes printed across the three agents.

    It is the group's volume times its tissue:gas coefficient, over its blood
    flow times the blood:gas coefficient (`docs/MODEL.md` § "Tissue groups").
    The section uses it to say that the group has equilibrated by the end of
    a 30-minute administration.
    """

    low, high = _printed(r"time constant is (\d\.\d) to (\d\.\d) minutes across the three agents")
    patient = load_reference_adult_parameters()
    blood_flow_l_min = patient.vessel_rich_perfusion_fraction * patient.default_cardiac_output_l_min
    minutes = [
        patient.vessel_rich_volume_l * _vessel_rich_tissue_blood(agent_id) / blood_flow_l_min
        for agent_id in AGENT_IDS
    ]

    _assert_span(minutes, low, high)


def test_the_stored_vessel_rich_coefficients_lie_within_3_percent_of_yasudas_brain_values() -> None:
    """Each stored tissue:blood ratio is the figure printed, and within the percentage printed."""

    percent, *ratios = _printed(
        r"within (\d+)%: (\d\.\d+) against \d\.\d+, (\d\.\d+) against \d\.\d+, and "
        r"(\d\.\d+) against"
    )

    for agent_id, figure in zip(SECTION_ORDER, ratios, strict=True):
        ratio = _vessel_rich_tissue_blood(agent_id)

        assert _as_printed(ratio, figure) == figure, agent_id
        assert abs(ratio / YASUDA_BRAIN_BLOOD[agent_id] - 1) < int(percent) / 100, agent_id


def test_normalising_the_fitted_amplitudes_would_move_the_curves_by_the_percentages_printed() -> (
    None
):
    """Scaling each fit to sum to 1 would raise it, and lower a ratio to it, by the spans shown."""

    raise_low, raise_high, lower_low, lower_high = _printed(
        r"raise every fitted value by (\d+) to (\d+)%, and lower every ratio below by "
        r"(\d+) to (\d+)%"
    )
    sums = [fit.value_at_discontinuation for fit in PUBLISHED_FITS]

    _assert_span([100 * (1 / total - 1) for total in sums], raise_low, raise_high)
    _assert_span([100 * (1 - total) for total in sums], lower_low, lower_high)


def test_the_fourth_term_is_4_to_5_percent_of_the_fitted_curve_at_five_minutes() -> None:
    """At five minutes, the fourth compartment's term is the share printed of each fitted ratio."""

    low, high = _printed(r"that term is (\d+) to (\d+)% of what remains")

    _assert_span(
        [100 * fit.term_at(FOURTH_TERM, 5) / fit.ratio_at(5) for fit in PUBLISHED_FITS], low, high
    )


def test_the_published_amplitude_spreads_are_the_shares_of_their_means_printed() -> None:
    """The fat amplitudes' SDs, and the fourth term's, are the shares of their means printed."""

    def shares(index: int) -> list[float]:
        return [
            100 * fit.amplitude_sds_percent[index] / fit.amplitudes_percent[index]
            for fit in PUBLISHED_FITS
        ]

    _assert_span(shares(FAT_TERM), *_printed(r"SDs that are (\d+) to (\d+)% of their means"))
    _assert_span(shares(FOURTH_TERM), *_printed(r"Those SDs are (\d+) to (\d+)% of the means"))


def test_the_model_s_apparent_terms_against_the_fitted_ones_give_the_ratios_printed() -> None:
    """The model's muscle and fat terms are as many times as slow and as large as printed.

    Each ratio is the model's apparent term, as
    `test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones`
    checks it, over the published mean term of each cohort.
    """

    muscle_slow = _printed(r"muscle term is (\d\.\d+) to (\d\.\d+) times as slow")
    muscle_large = _printed(r"and (\d\.\d+) to (\d\.\d+) times as large\. Its fat term")
    fat_slow = _printed(r"Its fat term is (\d\.\d+) to (\d\.\d+) times as slow")
    fat_large = _printed(
        r"times as slow and (\d\.\d+) to (\d\.\d+) times as large\. The fitted fat"
    )

    def ratios(model_value: Callable, index: int, published: str) -> list[float]:
        return [
            model_value(RECORDED_APPARENT_TERMS[fit.agent_id]) / getattr(fit, published)[index]
            for fit in PUBLISHED_FITS
        ]

    _assert_span(
        ratios(lambda t: t.muscle_time_constant_min, MUSCLE_TERM, "time_constants_min"),
        *muscle_slow,
    )
    _assert_span(
        ratios(lambda t: t.muscle_amplitude_percent, MUSCLE_TERM, "amplitudes_percent"),
        *muscle_large,
    )
    _assert_span(
        ratios(lambda t: t.fat_time_constant_min, FAT_TERM, "time_constants_min"), *fat_slow
    )
    _assert_span(
        ratios(lambda t: t.fat_amplitude_percent, FAT_TERM, "amplitudes_percent"), *fat_large
    )


def _model_over_fit(curve: WashoutCurve, fit: PublishedWashoutFit) -> list[float]:
    """The model's F_A/F_A0 over the fitted curve's, at each whole minute of the run."""

    return [
        curve.ratio_at(minutes) / fit.ratio_at(minutes)
        for minutes in range(len(curve.ratios_by_minute))
    ]


def _lowest_minute(ratios: Sequence[float], first: int, last: int) -> int:
    """The minute from `first` to `last`, inclusive, at which `ratios` is lowest."""

    return min(range(first, last + 1), key=lambda minutes: ratios[minutes])


def test_the_open_circuit_tail_s_lowest_points_are_as_printed(
    washout_curve: Callable[..., WashoutCurve],  # noqa: F811  # the fixture imported above
) -> None:
    """After the first hour, the open circuit falls to its lowest at the ratios and hours printed.

    Sevoflurane is lower only in the first half hour, at the ratio and minute
    printed. The second study's isoflurane rises above the curve, between the
    hours that the crossing table gives, by no more than the percentage
    printed.
    """

    low, high, desflurane_hour, other_hour = _printed(
        r"in every cohort \((0\.\d+) to (0\.\d+)\), near hour (\d+) for desflurane and near "
        r"hour (\d+) for the others"
    )
    early_ratio, early_minute = _printed(r"first half hour, at (0\.\d+) near minute (\d+)")
    (excess,) = _printed(r"between \d+\.\d+ and \d+\.\d+ h, by (\d+)% at most")
    lowest = []

    for fit in PUBLISHED_FITS:
        ratios = _model_over_fit(washout_curve(fit.agent_id, "open circuit"), fit)
        minute = _lowest_minute(ratios, MINUTES_PER_HOUR, len(ratios) - 1)
        lowest.append(ratios[minute])
        hour = desflurane_hour if fit.agent_id == "desflurane" else other_hour

        assert round(minute / MINUTES_PER_HOUR) == int(hour), fit.label

        if fit.agent_id == "sevoflurane":
            early = _lowest_minute(ratios, 1, MINUTES_PER_HOUR // 2)

            assert ratios[early] < ratios[minute]
            assert _as_printed(ratios[early], early_ratio) == early_ratio
            assert abs(early - int(early_minute)) <= 1

        if fit.agent_id == "isoflurane" and fit.cohort_size == 8:
            # Its one stretch above the curve lies between the second and the fifth hour.
            highest = max(ratios[2 * MINUTES_PER_HOUR : 5 * MINUTES_PER_HOUR])

            assert 1 < highest < 1 + int(excess) / 100

    _assert_span(lowest, low, high)


def test_the_shipped_tail_s_first_dip_is_15_to_44_percent_below_the_fitted_curve(
    washout_curve: Callable[..., WashoutCurve],  # noqa: F811  # the fixture imported above
) -> None:
    """The shipped tail is furthest below the curve in the first hour within the minutes printed.

    At that point it is below the curve by the span of percentages printed.
    """

    first, last, low, high = _printed(r"around (\d+) to (\d+) minutes, it is (\d+) to (\d+)% below")
    widest = []

    for fit in PUBLISHED_FITS:
        ratios = _model_over_fit(washout_curve(fit.agent_id, "shipped"), fit)
        minute = _lowest_minute(ratios, 1, MINUTES_PER_HOUR)
        widest.append(100 * (1 - ratios[minute]))

        assert int(first) <= minute <= int(last), fit.label

    _assert_span(widest, low, high)


def test_the_shipped_trace_falls_below_the_readout_resolution_at_the_hours_printed(
    washout_curve: Callable[..., WashoutCurve],  # noqa: F811  # the fixture imported above
) -> None:
    """At the 1% dial, the alveolar trace falls below the readouts' resolution at the hours printed.

    A higher desflurane dial keeps the trace above that resolution until the
    hour printed for it. The model is linear in the delivered fraction, so the
    trace at a higher dial is the trace at 1% times the dial.
    """

    hours = _printed(r"Displayed precision\"\) at (\d\.\d), (\d\.\d) and (\d\.\d) hours")
    dial, dial_hours = _printed(
        r"A (\d+)% desflurane dial keeps it there until about (\d\.\d) hours"
    )

    def hours_below(curve: WashoutCurve, dial_percent: float) -> float:
        start = 100 * curve.alveolar_fraction_at_discontinuation * dial_percent
        minutes = next(
            minutes
            for minutes, ratio in enumerate(curve.ratios_by_minute)
            if start * ratio < CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
        )
        return minutes / MINUTES_PER_HOUR

    for agent_id, figure in zip(SECTION_ORDER, hours, strict=True):
        found = hours_below(washout_curve(agent_id, "shipped"), 1)

        assert _as_printed(found, figure) == figure, agent_id

    found = hours_below(washout_curve("desflurane", "shipped"), int(dial))

    assert _as_printed(found, dial_hours) == dial_hours
