"""Test the canonical evaluation rule: each result is the run definition's, not the caller's.

`docs/MODEL.md` § "The canonical evaluation rule" states three things. Every
stored, exported, replayed or forked value is taken from the canonical path.
Two evaluations of one definition at one instant are bit-identical. The display
path may be drawn, and used for nothing else. The section "The reproducibility
guarantee" now rests on that rule. The fixed 0.1 s step used to provide
determinism by leaving no caller a choice of step width. A propagator that
accepts an interval takes that away, because the same instant can now be
reached by more than one route.

**What is tested, and why each half is needed.**

- *The canonical result is a function of the run definition alone.* One run is
  built and then read. An identical run is hammered with arbitrary `state_at`,
  `evaluate` and `evaluate_anchored` calls while it is built. Every keyframe
  and every checkpoint must agree **element for element**, not within a
  tolerance. A cache, a memoised propagator or a reused buffer would break
  this, and each of those is a reasonable-looking optimisation that somebody
  will propose. The chart's `evaluate_anchored` does keep the propagators it
  uses, for the next frame to reuse (`PL-CNCF`), which is why the hammering
  includes it. Drawing a window must leave the definition, from which every
  canonical result is derived, as it found it. That no canonical result reads
  the kept propagators is a different claim. Agreement here cannot show it,
  since a kept propagator read under its own key is exact.
  `tests/unit/test_run_definition.py` checks that claim by swapping the store
  for one that fails on any read.
- *A fork reproduces its parent exactly, wherever it was taken.* `ROADMAP.md`
  item 12 requires element-wise reproduction rather than agreement within a
  tolerance. The canonical rule supplies it under one condition on where the
  child's definition opens: **at the parent's keyframe at or before the
  fork instant, on the case's own axis**. Parent and child then propagate from
  the identical keyframe and form each interval by the identical subtraction.
  The reproduction therefore follows from how a branch is built, not from a
  caller having converted correctly. This module tests the two shapes that the
  program can produce separately (`PL-Z3W6`), over 207 instants each:

  - *A fork on a keyframe*, where the fork and the definition's opening are
    one instant. Every fork taken at a control event is of this kind.
  - *A fork between two keyframes*, where the definition opens at the earlier
    keyframe while the branch stands at the fork. A fork at a bookmark halt is
    of this kind, because its instant is not in general a keyframe
    (`PL-B8MK`). Its definition therefore covers a stretch that the branch
    never lived, between that keyframe and the fork, and the test asserts the
    parent's results over that stretch too. Removing that stretch from a
    branch's *drawn* range is a presentation decision about whose trajectory
    it is. This test shows that the numbers under it were never in question.

  **Both are measured against the route the program refuses.** A reproduction
  that would also happen without the condition would be no evidence that the
  condition is needed. Opening a definition *at* an unkeyframed fork instant,
  from the canonical state there, replaces one propagation over an interval
  with two propagations over its halves. That is a different rounding of the
  same exact solution, and it stops reproducing the parent. On this file's run
  forked at 1 234.5 s, 1 109 of the 1 269 state elements over the 141 probes at
  or past the fork differ. The worst difference is 7.8e-15 as a fraction and
  1.9e-12 L on an accumulator, measured 2026-09-21. Both figures are far below
  anything a readout resolves, which is why the condition is enforced in code
  rather than left to a reader to notice.

  **One frame is what makes the subtraction safe** (`PL-ZMRT`, 2026-09-14).
  When a child opened at a zero time of its own, exactness depended on every
  caller reaching it by subtracting the fork instant, rather than by naming
  the child's own elapsed time. The two differ because the subtraction does
  not always round-trip. With a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
  9.999999974752427e-07 rather than 1e-6. Opening on the case's own axis makes
  that difference impossible to represent, instead of merely forbidden. That
  is why this file tests it, rather than leaving item 12 to discover it.
- *The display path is separated in code.* A `DisplayState` cannot open a
  definition. `docs/MODEL.md` states the rule, and this check makes the
  statement true of the program rather than of the reader.

**The separation between the two paths is measured, not assumed.** The table
gives the worst absolute difference between the canonical and the display
result at the same instant, over the 600-column window that the chart draws,
on the run below. It was measured on 2026-09-07:

    span      six fractions           two accumulators
    1800 s    1.0e-14 (of 0.0301)     3.1e-12 L (of 2.06 L)
    24 h      8.0e-13 (of 0.0300)     3.1e-09 L (of 30.26 L)

The wider span is the worse case because its columns are further apart, so each
chained propagation covers more time. A span of 24 h is the supported run
length under "Supported run length", so the second row is the worst that a
supported run can reach at this column count.

**The two quantities have separate bounds because their headroom differs by
four orders of magnitude.** A fraction is displayed as a percent with two
decimals, so "Displayed precision" resolves 1e-4, and the measurement is eight
orders below that. `app/simulation_view.py` displays the accumulators to six
decimals of a litre, which resolves 1e-6 L, and the measurement is less than
three orders below *that*. Three orders is ample, but it is not fourteen, which
is why the separation is enforced in code rather than left to a reader to
observe.
"""

from random import Random

import pytest

from anesthesia_sim.core.concentration import Percent
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
from anesthesia_sim.core.run_definition import DisplayState, RunDefinition
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

CHANGES: tuple[tuple[float, str, float], ...] = (
    (30.0, "set_delivered_concentration_percent", Percent(4.0)),
    (120.0, "set_alveolar_ventilation", AlveolarVentilation(6.0)),
    (450.0, "set_fresh_gas_flow", FreshGasFlow(2.0)),
    (900.0, "set_delivered_concentration_percent", Percent(1.0)),
)
"""When each control moves, and to what, in the run that every test here uses.

There are four changes rather than one. A stretch of constant settings is the
easy case. What an evaluation rule has to get right is the boundary between two
stretches, where one composition ends and the next begins.
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
"""The six state entries stored as a fraction of one atmosphere, unlike the two in litres."""

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

`_probe_instants` adds a seeded spread to these. A reader can audit the
explicit list. The cases that a spread would miss are exactly the ones where a
boundary bug lives.
"""

WORST_FRACTION_SEPARATION = 1e-11
"""Bound on |canonical - display| for a compartment fraction, in a fraction of 1 atm.

The separation was measured at or below 8.0e-13 over the widest supported
window, as the module docstring shows. The bound is set one order of magnitude
above that, so that ordinary floating-point wobble does not fail the suite. It
is also seven orders below the 1e-4 that a readout can resolve, so that a real
divergence still fails it.
"""

WORST_ACCUMULATOR_SEPARATION = 5e-8
"""Bound on |canonical - display| for a cumulative accumulator, in litres.

The separation was measured at or below 3.1e-09 over the widest supported
window, as the module docstring shows. This bound is stated separately from the
fraction bound because these two entries are a different quantity with a
different display. One bound covering both would have to be the looser of the
two. It would then let a fraction drift four orders past anything ever measured
without failing.
"""


FORK_BETWEEN_KEYFRAMES_S = 1234.5
"""A fork instant inside the run's last stretch that is not one of its keyframes.

It was chosen for three properties. First, it lies in the stretch that opens at
900 s, and the run records no change after that. Parent and child therefore
share every instant from that keyframe to the end of the run, not only the
instants up to the parent's next setting. Second, it is not a keyframe, and a
fork at a bookmark halt is usually not one either: on the 120 s run that the
integration tests use, 3 of the 1 201 instants a halt could land on are
keyframes. Third, it is a whole number of the 0.1 s steps that a run advances
through. So it is an instant at which the program could really be halted and
forked, not one that only this file can name.
"""

WORST_RESTART_FRACTION_DIVERGENCE = 1e-13
"""Bound on |parent - restarted| for a compartment fraction, in a fraction of 1 atm.

"Restarted" is the route that the program refuses: a definition opened *at* an
unkeyframed fork instant rather than at the keyframe before it. The divergence
was measured at or below 7.8e-15 on the run below. The bound is set one order
above that, so that ordinary floating-point wobble does not fail the suite. It
is nine orders below the 1e-4 that a readout resolves, which is the point that
the measurement makes.
"""

WORST_RESTART_ACCUMULATOR_DIVERGENCE = 2e-11
"""Bound on |parent - restarted| for a cumulative accumulator, in litres.

The divergence was measured at or below 1.9e-12 on the run below. This bound is
separate from the fraction bound for the reason that
`WORST_ACCUMULATOR_SEPARATION` gives. One bound covering both would have to be
the looser of the two, and would let the other quantity drift orders of
magnitude past anything measured without failing.
"""


def _run_definition(length_s: float = RUN_LENGTH_S, probe: Random | None = None) -> RunDefinition:
    """Build the run that every test here uses, optionally querying it while it is built.

    When `probe` is given, the queries are the whole point. They stand for what
    a caller does that must not affect the result. They are made *between* the
    calls that build the run, so anything a query left behind would be carried
    into the keyframe that the next change computes.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    for at_s, setter, value in CHANGES:
        definition.advance_to(CaseInstant(at_s))

        if probe is not None:
            _query(definition, probe)

        getattr(system, setter)(value)
        definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(length_s))

    if probe is not None:
        _query(definition, probe)

    return definition


def _query(definition: RunDefinition, probe: Random) -> None:
    """Ask the run definition for states it is under no obligation to remember."""

    reach_s = definition.reached_s

    for _ in range(20):
        definition.state_at(probe.uniform(0.0, reach_s))

    start_s = probe.uniform(0.0, reach_s)
    definition.evaluate(start_s, probe.uniform(start_s, reach_s), probe.randint(1, 97))

    start_s = probe.uniform(0.0, reach_s)
    definition.evaluate_anchored(start_s, probe.uniform(start_s, reach_s), probe.uniform(1.0, 60.0))


def _probe_instants(count: int = 200) -> tuple[float, ...]:
    """Return the structural instants, plus a seeded spread across the run.

    The spread is seeded rather than drawn fresh, so that a failure names the
    same instants on the next run. A determinism test that cannot be re-run on
    the case that failed it reports a problem that nobody can act on.
    """

    spread = Random(20260907)

    return (*PROBES, *(spread.uniform(0.0, RUN_LENGTH_S) for _ in range(count)))


def _shared_instants(opening_s: float, count: int = 200) -> tuple[float, ...]:
    """Return the instants that a fork inside the run's last stretch shares with its parent.

    The structural instants come first: the stretch's own opening, one
    microsecond past it, a second and a half past it, the fork and either side
    of it, and the end of the run. A seeded spread across the stretch follows.
    It is seeded for the same reason that `_probe_instants` is seeded: a
    failure has to name the same instants on the next run, or it reports
    something that nobody can act on.

    The probes *below* the fork are not decoration. A branch taken between two
    keyframes opens its definition at the earlier one, so its definition covers
    a stretch that the branch itself never lived.
    `SimulationController.began_at_s` removes that stretch from the range the
    branch may be drawn from, because drawing it would show the parent's
    trajectory under the branch's identity. The clip is a statement about whose
    trajectory it is, not about the arithmetic, and these probes show that.
    """

    spread = Random(20260921)

    return (
        opening_s,
        opening_s + 1e-6,
        opening_s + 1.5,
        FORK_BETWEEN_KEYFRAMES_S - 1e-6,
        FORK_BETWEEN_KEYFRAMES_S,
        FORK_BETWEEN_KEYFRAMES_S + 1e-6,
        RUN_LENGTH_S,
        *(spread.uniform(opening_s, RUN_LENGTH_S) for _ in range(count)),
    )


def _settings_at(definition: RunDefinition, elapsed_s: float) -> UptakeEquationSettings:
    """Return the settings that the run was under at `elapsed_s`."""

    return max(
        (segment for segment in definition.segments if segment.opening.instant_s <= elapsed_s),
        key=lambda segment: segment.opening.instant_s,
    ).settings


def test_querying_a_run_does_not_change_what_it_answers() -> None:
    """The rule in one assertion: the canonical result belongs to the run definition.

    The comparison is element-wise across the whole state vector, not only the
    six displayed compartments. One reason is that a difference in an
    accumulator is a difference in the run, because the mass-balance identity
    is read from those two entries. The other is that the guarantee is about
    the arithmetic, not about what a chart happens to plot.
    """

    quiet = _run_definition()
    hammered = _run_definition(probe=Random(4242))

    for elapsed_s in _probe_instants():
        assert quiet.state_at(elapsed_s) == hammered.state_at(elapsed_s)


def test_querying_a_run_does_not_change_the_keyframes_it_stores() -> None:
    """Every later state is composed from a keyframe, so a changed keyframe does the most damage.

    Agreement of `state_at` is the visible half. A changed keyframe is the half
    that would let a difference outlive the query that caused it.
    """

    quiet = _run_definition()
    hammered = _run_definition(probe=Random(4242))

    assert [segment.opening for segment in quiet.segments] == [
        segment.opening for segment in hammered.segments
    ]


def test_two_evaluations_of_one_instant_are_bit_identical() -> None:
    """Identical, not "agree to within": the same operations in the same order, twice."""

    definition = _run_definition()

    for elapsed_s in _probe_instants(count=50):
        assert definition.state_at(elapsed_s) == definition.state_at(elapsed_s)


def test_a_fork_opening_from_a_keyframe_reproduces_its_parent() -> None:
    """`ROADMAP.md` item 12, checked element by element rather than to a tolerance.

    The child opens from the parent's own stored keyframe, under the parent's
    own settings, at that keyframe's instant, and is then advanced alone. At
    every instant the two share, they must agree entry for entry. The
    cumulative accumulators carry over too, because a propagator maps each of
    them to itself with coefficient one. So the child continues the parent's
    totals rather than restarting them.

    **Both runs are asked for the same instant, in the same float.** The child
    opens on the case's own axis rather than at a zero time of its own
    (`PL-ZMRT`). So there is no offset for this test to apply, and none for a
    caller to get wrong. `opening.instant_s + 1e-6` is in the probe list
    because it is the instant that a child opened at its own zero could not
    reach without a subtraction by the caller. With a fork at 900 s,
    `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 rather than 1e-6. A
    child asked for its own `1e-6` therefore propagated over a different
    interval from its parent's, and landed one unit in the last place away.
    Opening at the fork makes that difference impossible to represent, not
    merely avoided, and that probe is what shows it.
    """

    parent = _run_definition()
    opening = parent.segments[-1].opening
    child = RunDefinition(
        parent.segments[-1].settings, opening.state, opened_at_s=opening.instant_s
    )
    child.advance_to(CaseInstant(RUN_LENGTH_S))

    for elapsed_s in _shared_instants(opening.instant_s):
        assert child.state_at(elapsed_s) == parent.state_at(elapsed_s), (
            f"the branch and its parent differ at {elapsed_s} s"
        )


def test_a_fork_opening_between_two_keyframes_reproduces_its_parent() -> None:
    """The same guarantee where the fork instant is not a keyframe (`PL-Z3W6`).

    A bookmark may be dropped anywhere, so a fork taken at one is in general
    taken between two of the parent's keyframes rather than on one. On the
    120 s run that the integration tests use, 3 of the 1 201 instants a halt
    could land on are keyframes. Recording a keyframe where the run halts would
    make the two coincide again. `PL-B8MK` measured that route and refused it,
    because it displaces the parent's own later results, so marking a run would
    change the run.

    Instead, the branch opens its definition at the parent's keyframe **at or
    before** the fork, under the parent's settings, and sets its clock at the
    fork. That is the general form of the condition, and the keyframe case
    satisfies it as a special case. This test is where the general condition
    and its special case can be told apart. A keyframe fork cannot tell them
    apart, because there the opening and the fork are one instant.

    The test makes three claims, and the second is the one that a later change
    would break silently. First, the child's definition reproduces the parent
    over every instant they share, including the stretch below the fork that
    the branch never lived. Second, the state the child stands at when it is
    forked is the parent's own canonical state there, bit for bit. It is not a
    value rederived by the child or read back out of a seeded uptake system.
    `app/controller.py` takes the canonical route to avoid an 11.7% round-trip
    error on alveolar fractions. Third, the parent is left as it was, which
    shows that the fork read the run rather than edited it.
    """

    parent = _run_definition()
    segment = parent.segment_at(FORK_BETWEEN_KEYFRAMES_S)
    opening = segment.opening

    assert FORK_BETWEEN_KEYFRAMES_S not in [
        candidate.opening.instant_s for candidate in parent.segments
    ], "the premise: the parent holds no keyframe at the fork, so the two conditions differ"
    assert opening.instant_s < FORK_BETWEEN_KEYFRAMES_S

    before = [candidate.opening for candidate in parent.segments]
    child = RunDefinition(segment.settings, opening.state, opened_at_s=opening.instant_s)
    child.advance_to(CaseInstant(RUN_LENGTH_S))

    assert child.state_at(FORK_BETWEEN_KEYFRAMES_S) == parent.state_at(FORK_BETWEEN_KEYFRAMES_S), (
        "the branch does not stand at the state its parent holds at the fork"
    )

    for elapsed_s in _shared_instants(opening.instant_s):
        assert child.state_at(elapsed_s) == parent.state_at(elapsed_s), (
            f"the branch and its parent differ at {elapsed_s} s"
        )

    assert [candidate.opening for candidate in parent.segments] == before


def test_a_fork_opening_at_the_instant_it_was_taken_does_not_reproduce_its_parent() -> None:
    """Show, by measurement rather than quotation, why the definition opens at the keyframe.

    Opening at the fork is the arrangement that a reader expects, and it is the
    one thing that the relaxation above gives up. If opening at the fork
    reproduced the parent anyway, the condition would cost a reader an
    explanation and gain nothing, and every test above would pass while
    guarding it.

    It does not reproduce the parent. Restarting at an instant for which the
    parent has no keyframe replaces one propagation over an interval with two
    propagations over its halves. That is the same exact solution composed in
    a different order, and the difference survives to every later instant.
    Measured on 2026-09-21 over the 141 probes at or past the fork, 1 109 of the
    1 269 state elements differ. The worst difference is 7.8e-15 as a fraction
    and 1.9e-12 L on an accumulator.

    Both halves are asserted, because each alone permits a failure that the
    other catches. That the difference is *real* is what makes the condition
    worth enforcing. That it is *this small* is what makes enforcement in code
    the only way to catch it. It is nine orders below the 1e-4 that a
    compartment readout resolves, and six below the 1e-6 L resolution at which
    the mass balance is shown. A branch built this way would look exactly like one
    built correctly.

    The test fails honestly if a future change makes the restart exact. That
    would mean the condition had stopped costing anything, and that this file
    had a sentence to delete rather than a bug to fix.
    """

    parent = _run_definition()
    segment = parent.segment_at(FORK_BETWEEN_KEYFRAMES_S)
    restarted = RunDefinition(
        segment.settings,
        parent.state_at(FORK_BETWEEN_KEYFRAMES_S),
        opened_at_s=CaseInstant(FORK_BETWEEN_KEYFRAMES_S),
    )
    restarted.advance_to(CaseInstant(RUN_LENGTH_S))

    differing = 0

    for elapsed_s in _shared_instants(segment.opening.instant_s):
        if elapsed_s < FORK_BETWEEN_KEYFRAMES_S:
            continue

        canonical = parent.state_at(elapsed_s)
        restart = restarted.state_at(elapsed_s)
        differing += sum(canonical[entry] != restart[entry] for entry in range(STATE_SIZE))

        for entry in FRACTION_STATES:
            assert abs(canonical[entry] - restart[entry]) < WORST_RESTART_FRACTION_DIVERGENCE, (
                f"entry {entry} diverged further than measured at {elapsed_s} s"
            )

        for entry in (DELIVERED_AGENT_L, EXHAUSTED_AGENT_L):
            assert abs(canonical[entry] - restart[entry]) < WORST_RESTART_ACCUMULATOR_DIVERGENCE, (
                f"entry {entry} diverged further than measured at {elapsed_s} s"
            )

        assert restart[UNIT_STATE] == 1.0

    assert differing > 0, (
        "a definition restarted at an unkeyframed instant reproduced its parent element "
        "for element, so opening a branch at the keyframe before the fork has stopped "
        "buying anything and the condition should be retired rather than explained"
    )


def test_a_display_value_cannot_open_a_run_definition() -> None:
    """The program refuses a display value as an opening state, so the rule is not only documented.

    A fork's opening state and a drawn column are the same nine numbers in the
    same order, so nothing in their contents tells them apart. What does tell
    them apart is that a drawn column is not a state vector at all.
    """

    definition = _run_definition()
    drawn = definition.evaluate(0.0, RUN_LENGTH_S, 600).states[0]

    assert isinstance(drawn, DisplayState)
    assert not isinstance(drawn, tuple)

    with pytest.raises(SimulationConfigurationError, match="came from the display path"):
        RunDefinition(_settings_at(definition, 0.0), drawn, opened_at_s=CaseInstant(0.0))  # type: ignore[arg-type]


def test_the_display_path_stays_within_its_measured_separation() -> None:
    """The display path stays within the published figures.

    `docs/MODEL.md` § "The canonical evaluation rule" tells a reader how far
    the drawn value may sit from the canonical one. Without this test, the
    figures would only be prose in two files. A change to the equations, to
    the propagator or to how a window is walked would move them silently, and
    the document would keep publishing the old ones.
    """

    assert {*FRACTION_STATES, DELIVERED_AGENT_L, EXHAUSTED_AGENT_L, UNIT_STATE} == set(
        range(STATE_SIZE)
    ), "a state entry outside these three groups would be measured by nothing below"

    definition = _run_definition(length_s=SUPPORTED_RUN_LENGTH_S)
    window = definition.evaluate(0.0, SUPPORTED_RUN_LENGTH_S, 600)

    for elapsed_s, drawn in zip(window.times_s, window.states, strict=True):
        canonical = definition.state_at(elapsed_s)

        for entry in FRACTION_STATES:
            assert abs(canonical[entry] - drawn.values[entry]) < WORST_FRACTION_SEPARATION

        for entry in (DELIVERED_AGENT_L, EXHAUSTED_AGENT_L):
            assert abs(canonical[entry] - drawn.values[entry]) < WORST_ACCUMULATOR_SEPARATION

        assert drawn.values[UNIT_STATE] == 1.0


def test_the_two_paths_are_not_the_same_arithmetic() -> None:
    """A separation worth enforcing has to be a real one.

    If the display path ever became bit-identical to the canonical one, this
    file's other tests would all still pass while guarding nothing, and the
    wrapper would be a cost with no benefit. This test is what would report
    that. It fails honestly if a future change makes chaining exact, and that
    failure is a result worth having rather than a broken test.
    """

    definition = _run_definition()
    window = definition.evaluate(0.0, RUN_LENGTH_S, 600)
    accumulators = (DELIVERED_AGENT_L, EXHAUSTED_AGENT_L)

    assert any(
        canonical[entry] != drawn.values[entry]
        for elapsed_s, drawn in zip(window.times_s, window.states, strict=True)
        for canonical in (definition.state_at(elapsed_s),)
        for entry in accumulators
    )
