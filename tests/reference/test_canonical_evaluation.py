"""Hold the canonical evaluation rule: the answer is the score's, not the caller's.

`docs/MODEL.md` § "The canonical evaluation rule" states that every stored,
exported, replayed or forked value is taken from the canonical path, that two
evaluations of one score at one instant are bit-identical, and that the display
path may be drawn and nothing else. That is the guarantee "The reproducibility
guarantee" now rests on: the fixed 0.1 s step used to carry determinism by
leaving every caller no choice of width, and a propagator that accepts an
interval takes that away, because the same instant can now be reached by more
than one route.

**What is tested, and why each half is needed.**

- *The canonical answer is a function of the score alone.* One run is built and
  then read; an identical run is hammered with arbitrary `state_at` and
  `evaluate` calls as it is built. Every keyframe and every checkpoint must
  agree **element for element**, not within a tolerance. This is what a cache,
  a memoised propagator or a reused buffer would break, and each of those is a
  reasonable-looking optimisation somebody will propose.
- *A fork opening from a keyframe reproduces its parent exactly.* `ROADMAP.md`
  item 12 requires element-wise reproduction rather than agreement within a
  tolerance, and the canonical rule supplies it under two conditions, both
  measured on this file's run on 2026-09-07 rather than assumed. The fork must
  open **at a keyframe**: a score restarted from `state_at` at a segment
  opening reproduces its parent bit for bit, and one restarted at an instant
  the parent has no keyframe for does not, differing by up to 5.3e-13 in a
  cumulative accumulator - the restart is one propagation over an interval
  against two over its halves, which is a different rounding of the same exact
  solution. And the child's clock must be re-based **by subtracting the fork
  instant**, because that subtraction does not always round-trip: with a fork
  at 900 s, `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 rather than
  1e-6, so a child asked for its own `1e-6` propagates over a different
  interval from the parent and lands one unit in the last place away. Both
  conditions constrain how a fork may be built, which is why this file gates
  them rather than leaving them to be discovered by item 12.
- *The display path is separated in code.* A `DisplayState` cannot open a
  score. `docs/MODEL.md` states the rule; this is what makes the statement
  true of the program rather than of the reader.

**The separation between the two paths is measured, not assumed.** Worst
absolute difference between the canonical and the display answer at the same
instant, over the 600-column window the chart draws, on the run below, measured
2026-09-07:

    span      six fractions           two accumulators
    1800 s    1.0e-14 (of 0.0301)     3.1e-12 L (of 2.06 L)
    24 h      8.0e-13 (of 0.0300)     3.1e-09 L (of 30.26 L)

The wider span is the worse case because its columns are further apart, so each
chained propagation covers more ground; 24 h is the supported run length under
"Supported run length", so the second row is the worst a supported run can
reach at this column count.

**The two quantities are held to separate bounds because their headroom
differs by four orders.** A fraction is displayed as a two-decimal percent, so
"Displayed precision" resolves 1e-4 and the measurement sits eight orders
below it. The accumulators are displayed by `app/simulation_view.py` as six
decimals of a litre, resolving 1e-6 L, and the measurement sits under three
orders below *that*. Three orders is ample and it is not fourteen, which is
the reason the separation is enforced in code rather than left to a reader to
observe.
"""

from random import Random

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    TISSUE_GROUP_COUNT,
    UNIT_STATE,
    VENOUS_FRACTION,
    UptakeEquationSettings,
)
from anesthesia_sim.core.run_score import DisplayState, RunScore
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

CHANGES: tuple[tuple[float, str, float], ...] = (
    (30.0, "set_delivered_concentration", 0.04),
    (120.0, "set_alveolar_ventilation", 6.0),
    (450.0, "set_fresh_gas_flow", 2.0),
    (900.0, "set_delivered_concentration", 0.01),
)
"""When each control moves, and to what, in the run every test here uses.

Four changes rather than one: a stretch of constant settings is the easy case,
and what an evaluation rule has to get right is the boundary between two of
them, where one composition ends and the next begins.
"""

RUN_LENGTH_S = 1800.0

SUPPORTED_RUN_LENGTH_S = 24 * 3600.0
"""The longest run the model supports, from `docs/MODEL.md` § "Supported run length"."""

FRACTION_STATES: tuple[int, ...] = (
    INSPIRED_FRACTION,
    ALVEOLAR_FRACTION,
    VENOUS_FRACTION,
    *(FIRST_TISSUE_FRACTION + group for group in range(TISSUE_GROUP_COUNT)),
)
"""The six entries held as a fraction of one atmosphere, as against the two in litres."""

PROBES: tuple[float, ...] = (
    0.0,
    1e-9,
    29.999999999,
    30.0,
    30.000000001,
    119.5,
    120.0,
    450.0,
    899.9,
    900.0,
    1234.5678,
    RUN_LENGTH_S,
)
"""Instants chosen for their structure: each boundary, and either side of one.

A seeded spread is added to these in `_probe_instants`. The explicit list is
what a reader can audit - the cases that would be missed by a spread are
exactly the ones a boundary bug lives at.
"""

WORST_FRACTION_SEPARATION = 1e-11
"""Bound on |canonical - display| for a compartment fraction, in a fraction of 1 atm.

Measured at or below 8.0e-13 over the widest supported window; see the module
docstring. Set an order above that so an ordinary floating-point wobble does
not fail the suite, and seven orders below the 1e-4 a readout can resolve so a
real divergence still does.
"""

WORST_ACCUMULATOR_SEPARATION = 5e-8
"""Bound on |canonical - display| for a cumulative accumulator, in litres.

Measured at or below 3.1e-09 over the widest supported window; see the module
docstring. Stated separately from the fraction bound because these two entries
are a different quantity with a different display: one bound covering both
would have to be the looser of the two, and would then let a fraction drift
four orders past anything ever measured without failing.
"""


def _score(length_s: float = RUN_LENGTH_S, probe: Random | None = None) -> RunScore:
    """The run every test here uses, optionally queried as it is built.

    The queries are the whole point when `probe` is given: they are what a
    caller does that must not reach the answer. They are made *between* the
    calls that build the run, so anything a query left behind would be carried
    into the keyframe the next change computes.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    for at_s, setter, value in CHANGES:
        score.advance_to(at_s)

        if probe is not None:
            _query(score, probe)

        getattr(system, setter)(value)
        score.record_change(system.equation_settings())

    score.advance_to(length_s)

    if probe is not None:
        _query(score, probe)

    return score


def _query(score: RunScore, probe: Random) -> None:
    """Ask the score for states it is under no obligation to remember."""

    reach_s = score.duration_s

    for _ in range(20):
        score.state_at(probe.uniform(0.0, reach_s))

    start_s = probe.uniform(0.0, reach_s)
    score.evaluate(start_s, probe.uniform(start_s, reach_s), probe.randint(1, 97))


def _probe_instants(count: int = 200) -> tuple[float, ...]:
    """The structural instants, plus a seeded spread across the run.

    Seeded rather than drawn fresh so that a failure names the same instants on
    the next run: a determinism test that cannot be re-run on the case that
    failed it is a test that reports and cannot be acted on.
    """

    spread = Random(20260907)

    return (*PROBES, *(spread.uniform(0.0, RUN_LENGTH_S) for _ in range(count)))


def _settings_at(score: RunScore, elapsed_s: float) -> UptakeEquationSettings:
    """The settings the run was under at `elapsed_s`."""

    return max(
        (segment for segment in score.segments if segment.opening.elapsed_s <= elapsed_s),
        key=lambda segment: segment.opening.elapsed_s,
    ).settings


def test_querying_a_run_does_not_change_what_it_answers() -> None:
    """The rule in one assertion: the canonical answer belongs to the score.

    Element-wise across the whole state vector rather than the six displayed
    compartments, because a difference in an accumulator is a difference in the
    run - the mass-balance identity is read from those two entries - and
    because the guarantee is about the arithmetic and not about what a chart
    happens to plot.
    """

    quiet = _score()
    hammered = _score(probe=Random(4242))

    for elapsed_s in _probe_instants():
        assert quiet.state_at(elapsed_s) == hammered.state_at(elapsed_s)


def test_querying_a_run_does_not_change_the_keyframes_it_stores() -> None:
    """A keyframe is what every later state is composed from, so it fails widest.

    `state_at` agreeing is the visible half; this is the half that would let a
    difference outlive the query that caused it.
    """

    quiet = _score()
    hammered = _score(probe=Random(4242))

    assert [segment.opening for segment in quiet.segments] == [
        segment.opening for segment in hammered.segments
    ]


def test_two_evaluations_of_one_instant_are_bit_identical() -> None:
    """Not "agree to within": the same operations in the same order, twice."""

    score = _score()

    for elapsed_s in _probe_instants(count=50):
        assert score.state_at(elapsed_s) == score.state_at(elapsed_s)


def test_a_fork_opening_from_a_keyframe_reproduces_its_parent() -> None:
    """`ROADMAP.md` item 12, held element-wise rather than to a tolerance.

    The child opens from the parent's own stored keyframe under the parent's
    own settings and is advanced alone; every instant the two share must agree
    entry for entry. The cumulative accumulators come with it - a propagator
    maps each of them to itself with coefficient one - so the child continues
    the parent's totals rather than restarting them.
    """

    parent = _score()
    opening = parent.segments[-1].opening
    child = RunScore(parent.segments[-1].settings, opening.state)
    child.advance_to(RUN_LENGTH_S - opening.elapsed_s)

    for elapsed_s in (opening.elapsed_s, 901.5, 1234.5678, RUN_LENGTH_S):
        assert child.state_at(elapsed_s - opening.elapsed_s) == parent.state_at(elapsed_s)


def test_a_display_value_cannot_open_a_score() -> None:
    """The separation is refused by the program, not asserted by the document.

    A fork's opening state and a drawn column are the same nine numbers in the
    same order, so nothing about their contents distinguishes them; what does
    is that one of them is not a state vector at all.
    """

    score = _score()
    drawn = score.evaluate(0.0, RUN_LENGTH_S, 600).states[0]

    assert isinstance(drawn, DisplayState)
    assert not isinstance(drawn, tuple)

    with pytest.raises(SimulationConfigurationError, match="came from the display path"):
        RunScore(_settings_at(score, 0.0), drawn)  # type: ignore[arg-type]


def test_the_display_path_stays_within_its_measured_separation() -> None:
    """The published figures, held to.

    `docs/MODEL.md` § "The canonical evaluation rule" tells a reader how far
    the drawn value may sit from the canonical one. Without this the figures
    would be prose in two files: a change to the equations, to the propagator
    or to how a window is walked would move them silently, and the document
    would keep publishing the old ones.
    """

    assert {*FRACTION_STATES, DELIVERED_AGENT_L, EXHAUSTED_AGENT_L, UNIT_STATE} == set(
        range(STATE_SIZE)
    ), "a state entry outside these three groups would be measured by nothing below"

    score = _score(length_s=SUPPORTED_RUN_LENGTH_S)
    window = score.evaluate(0.0, SUPPORTED_RUN_LENGTH_S, 600)

    for elapsed_s, drawn in zip(window.times_s, window.states, strict=True):
        canonical = score.state_at(elapsed_s)

        for entry in FRACTION_STATES:
            assert abs(canonical[entry] - drawn.values[entry]) < WORST_FRACTION_SEPARATION

        for entry in (DELIVERED_AGENT_L, EXHAUSTED_AGENT_L):
            assert abs(canonical[entry] - drawn.values[entry]) < WORST_ACCUMULATOR_SEPARATION

        assert drawn.values[UNIT_STATE] == 1.0


def test_the_two_paths_are_not_the_same_arithmetic() -> None:
    """A separation worth enforcing has to be a real one.

    If the display path ever became bit-identical to the canonical one, this
    file's other tests would all still pass while guarding nothing, and the
    wrapper would be cost with no benefit. This is what would say so - and it
    fails honestly if a future change makes chaining exact, which is a result
    worth having rather than a broken test.
    """

    score = _score()
    window = score.evaluate(0.0, RUN_LENGTH_S, 600)
    accumulators = (DELIVERED_AGENT_L, EXHAUSTED_AGENT_L)

    assert any(
        canonical[entry] != drawn.values[entry]
        for elapsed_s, drawn in zip(window.times_s, window.states, strict=True)
        for canonical in (score.state_at(elapsed_s),)
        for entry in accumulators
    )
