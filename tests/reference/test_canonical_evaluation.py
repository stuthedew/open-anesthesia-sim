"""Hold the canonical evaluation rule: the answer is the run definition's, not the caller's.

`docs/MODEL.md` § "The canonical evaluation rule" states that every stored,
exported, replayed or forked value is taken from the canonical path, that two
evaluations of one definition at one instant are bit-identical, and that the display
path may be drawn and nothing else. That is the guarantee "The reproducibility
guarantee" now rests on: the fixed 0.1 s step used to carry determinism by
leaving every caller no choice of width, and a propagator that accepts an
interval takes that away, because the same instant can now be reached by more
than one route.

**What is tested, and why each half is needed.**

- *The canonical answer is a function of the run definition alone.* One run is built and
  then read; an identical run is hammered with arbitrary `state_at` and
  `evaluate` calls as it is built. Every keyframe and every checkpoint must
  agree **element for element**, not within a tolerance. This is what a cache,
  a memoised propagator or a reused buffer would break, and each of those is a
  reasonable-looking optimisation somebody will propose.
- *A fork reproduces its parent exactly, wherever it was taken.* `ROADMAP.md`
  item 12 requires element-wise reproduction rather than agreement within a
  tolerance, and the canonical rule supplies it under one condition on where
  the child's definition opens: **at the parent's keyframe at or before the
  fork instant, on the case's own axis**. Parent and child then propagate from
  the identical keyframe and form each interval by the identical subtraction,
  so the reproduction follows from how a branch is built rather than from a
  caller having converted correctly. The two shapes the program can produce
  are held to it separately here (`PL-Z3W6`), over 207 instants each:

  - *A fork on a keyframe*, where the fork and the definition's opening are
    one instant. Every fork taken at a control event is this.
  - *A fork between two keyframes*, where the definition opens at the earlier
    one while the branch stands at the fork - a fork at a bookmark halt, whose
    instant is not in general a keyframe (`PL-B8MK`). Its definition therefore
    covers a stretch the branch never lived, between that keyframe and the
    fork, and the parent's answers over that stretch are asserted too. What
    clips it from a branch's *drawn* range is a presentation decision about
    whose trajectory it is; this is what says the numbers under it were never
    in question.

  **Both are measured against the route the program refuses**, because a
  reproduction obtained for nothing is no evidence that the condition is
  load-bearing. Opening a definition *at* an unkeyframed fork instant, from the
  canonical state there, replaces one propagation over an interval with two
  over its halves - a different rounding of the same exact solution - and stops
  reproducing: on this file's run forked at 1 234.5 s, 1 109 of the 1 269 state
  elements over the 141 probes at or past it differ, worst 7.8e-15 as a fraction
  and 1.9e-12 L on an accumulator, measured 2026-09-21. Both figures sit far below anything a
  readout resolves, which is why the condition is enforced in code rather than
  left to a reader to notice.

  **One frame is what makes the subtraction safe** (`PL-ZMRT`, 2026-09-14).
  While a child opened at a zero of its own, exactness depended on every caller
  reaching it by subtracting the fork instant rather than naming the child's
  own elapsed time, and the two differ because the subtraction does not always
  round-trip - with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
  9.999999974752427e-07 rather than 1e-6. Opening on the case's own axis makes
  that difference unrepresentable instead of merely forbidden, which is why
  this file gates it rather than leaving it to be discovered by item 12.
- *The display path is separated in code.* A `DisplayState` cannot open a
  definition. `docs/MODEL.md` states the rule; this is what makes the statement
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
from anesthesia_sim.core.run_definition import DisplayState, RunDefinition
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

CHANGES: tuple[tuple[float, str, float], ...] = (
    (30.0, "set_delivered_partial_pressure_fraction", 0.04),
    (120.0, "set_alveolar_ventilation", 6.0),
    (450.0, "set_fresh_gas_flow", 2.0),
    (900.0, "set_delivered_partial_pressure_fraction", 0.01),
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


FORK_BETWEEN_KEYFRAMES_S = 1234.5
"""A fork instant inside the run's last stretch that is not one of its keyframes.

Chosen for three properties. It lies in the stretch opening at 900 s and the
run records no change after that, so parent and child share every instant from
that keyframe to the end of the run rather than only as far as the parent's
next setting. It is not a keyframe, which is what a fork at a bookmark halt is:
on the 120 s run the integration tests use, 3 of the 1 201 instants a halt
could land on are keyframes. And it is a whole number of the 0.1 s steps a run
is advanced through, so it is an instant the program could really be halted and
forked at rather than one only this file can name.
"""

WORST_RESTART_FRACTION_DIVERGENCE = 1e-13
"""Bound on |parent - restarted| for a compartment fraction, in a fraction of 1 atm.

"Restarted" is the route the program refuses: a definition opened *at* an
unkeyframed fork instant rather than at the keyframe before it. Measured at or
below 7.8e-15 on the run below; set an order above that so an ordinary
floating-point wobble does not fail the suite, and nine orders below the 1e-4 a
readout resolves, which is the point that measurement makes.
"""

WORST_RESTART_ACCUMULATOR_DIVERGENCE = 2e-11
"""Bound on |parent - restarted| for a cumulative accumulator, in litres.

Measured at or below 1.9e-12 on the run below. Held separately from the
fraction bound for the reason `WORST_ACCUMULATOR_SEPARATION` gives: one bound
covering both would have to be the looser of the two, and would let the other
quantity drift orders past anything measured without failing.
"""


def _run_definition(length_s: float = RUN_LENGTH_S, probe: Random | None = None) -> RunDefinition:
    """The run every test here uses, optionally queried as it is built.

    The queries are the whole point when `probe` is given: they are what a
    caller does that must not reach the answer. They are made *between* the
    calls that build the run, so anything a query left behind would be carried
    into the keyframe the next change computes.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    for at_s, setter, value in CHANGES:
        definition.advance_to(at_s)

        if probe is not None:
            _query(definition, probe)

        getattr(system, setter)(value)
        definition.record_change(system.equation_settings())

    definition.advance_to(length_s)

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


def _probe_instants(count: int = 200) -> tuple[float, ...]:
    """The structural instants, plus a seeded spread across the run.

    Seeded rather than drawn fresh so that a failure names the same instants on
    the next run: a determinism test that cannot be re-run on the case that
    failed it is a test that reports and cannot be acted on.
    """

    spread = Random(20260907)

    return (*PROBES, *(spread.uniform(0.0, RUN_LENGTH_S) for _ in range(count)))


def _shared_instants(opening_s: float, count: int = 200) -> tuple[float, ...]:
    """The instants a fork inside the run's last stretch shares with its parent.

    The structural ones first - the stretch's own opening, one microsecond past
    it, a second and a half past it, the fork and either side of it, and the
    end of the run - then a seeded spread across the stretch. Seeded for the
    reason `_probe_instants` is seeded: a failure has to name the same instants
    on the next run, or it reports something that cannot be acted on.

    The probes *below* the fork are not decoration. A branch taken between two
    keyframes opens its definition at the earlier one, so its definition covers
    a stretch the branch itself never lived; `SimulationController.began_at_s`
    clips that stretch from what the branch may be drawn from, because drawing
    it would show the parent's trajectory under the branch's identity. The clip
    is a statement about whose trajectory it is and not about the arithmetic,
    and these probes are what says so.
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
    """The settings the run was under at `elapsed_s`."""

    return max(
        (segment for segment in definition.segments if segment.opening.instant_s <= elapsed_s),
        key=lambda segment: segment.opening.instant_s,
    ).settings


def test_querying_a_run_does_not_change_what_it_answers() -> None:
    """The rule in one assertion: the canonical answer belongs to the run definition.

    Element-wise across the whole state vector rather than the six displayed
    compartments, because a difference in an accumulator is a difference in the
    run - the mass-balance identity is read from those two entries - and
    because the guarantee is about the arithmetic and not about what a chart
    happens to plot.
    """

    quiet = _run_definition()
    hammered = _run_definition(probe=Random(4242))

    for elapsed_s in _probe_instants():
        assert quiet.state_at(elapsed_s) == hammered.state_at(elapsed_s)


def test_querying_a_run_does_not_change_the_keyframes_it_stores() -> None:
    """A keyframe is what every later state is composed from, so it fails widest.

    `state_at` agreeing is the visible half; this is the half that would let a
    difference outlive the query that caused it.
    """

    quiet = _run_definition()
    hammered = _run_definition(probe=Random(4242))

    assert [segment.opening for segment in quiet.segments] == [
        segment.opening for segment in hammered.segments
    ]


def test_two_evaluations_of_one_instant_are_bit_identical() -> None:
    """Not "agree to within": the same operations in the same order, twice."""

    definition = _run_definition()

    for elapsed_s in _probe_instants(count=50):
        assert definition.state_at(elapsed_s) == definition.state_at(elapsed_s)


def test_a_fork_opening_from_a_keyframe_reproduces_its_parent() -> None:
    """`ROADMAP.md` item 12, held element-wise rather than to a tolerance.

    The child opens from the parent's own stored keyframe under the parent's
    own settings, at the instant that keyframe stands at, and is advanced
    alone; every instant the two share must agree entry for entry. The
    cumulative accumulators come with it - a propagator maps each of them to
    itself with coefficient one - so the child continues the parent's totals
    rather than restarting them.

    **Both runs are asked for the same instant, in the same float.** The child
    opens on the case's own axis rather than at a zero of its own (`PL-ZMRT`),
    so there is no offset for this test to apply and none for a caller to get
    wrong. `opening.instant_s + 1e-6` is in the probe list because it is the
    instant that arrangement could not reach without a caller-side
    subtraction: with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
    9.999999974752427e-07 rather than 1e-6, so a child asked for its own
    `1e-6` propagated over a different interval from its parent and landed one
    unit in the last place away. Opening at the fork makes that difference
    unrepresentable rather than merely avoided, and this line is what says so.
    """

    parent = _run_definition()
    opening = parent.segments[-1].opening
    child = RunDefinition(
        parent.segments[-1].settings, opening.state, opened_at_s=opening.instant_s
    )
    child.advance_to(RUN_LENGTH_S)

    for elapsed_s in _shared_instants(opening.instant_s):
        assert child.state_at(elapsed_s) == parent.state_at(elapsed_s), (
            f"the branch and its parent differ at {elapsed_s} s"
        )


def test_a_fork_opening_between_two_keyframes_reproduces_its_parent() -> None:
    """The same guarantee where the fork instant is not a keyframe (`PL-Z3W6`).

    A bookmark may be dropped anywhere, so a fork taken at one is in general
    taken between two of the parent's keyframes rather than on one - on the
    120 s run the integration tests use, 3 of the 1 201 instants a halt could
    land on are keyframes. Recording a keyframe where the run halts would make
    the two coincide again, and is the route `PL-B8MK` measured and refused: it
    displaces the parent's own later answers, so marking a run would change it.

    What the branch does instead is open its definition at the parent's
    keyframe **at or before** the fork, under the parent's settings, and stand
    its clock at the fork. That is the general form of the condition the
    keyframe case satisfies as a special case, and this is where the two are
    held apart: a keyframe fork cannot tell them apart, because there the
    opening and the fork are one instant.

    Three claims, and the second is the one a later change would break
    silently. The child's definition reproduces the parent over every instant
    they share, including the stretch below the fork that the branch never
    lived. The state the child stands at when it is forked is the parent's own
    canonical state there, bit for bit, rather than a value rederived by the
    child or read back out of a seeded uptake system - an 11.7% round-trip
    error on alveolar fractions is what `app/controller.py` takes the canonical
    route to avoid. And the parent is left as it was, which is what says the
    fork read the run rather than edited it.
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
    child.advance_to(RUN_LENGTH_S)

    assert child.state_at(FORK_BETWEEN_KEYFRAMES_S) == parent.state_at(FORK_BETWEEN_KEYFRAMES_S), (
        "the branch does not stand at the state its parent holds at the fork"
    )

    for elapsed_s in _shared_instants(opening.instant_s):
        assert child.state_at(elapsed_s) == parent.state_at(elapsed_s), (
            f"the branch and its parent differ at {elapsed_s} s"
        )

    assert [candidate.opening for candidate in parent.segments] == before


def test_a_fork_opening_at_the_instant_it_was_taken_does_not_reproduce_its_parent() -> None:
    """Why the definition opens at the keyframe, measured here rather than quoted.

    Opening at the fork is the arrangement a reader expects, and it is the one
    thing the relaxation above gives up. If it reproduced the parent anyway,
    the condition would be costing a reader an explanation and buying nothing,
    and every test above would pass while guarding it.

    It does not reproduce. Restarting at an instant the parent holds no
    keyframe for replaces one propagation over an interval with two over its
    halves, which is the same exact solution composed in a different order, and
    the difference survives to every later instant. Measured 2026-09-21 over
    the 141 probes at or past the fork: 1 109 of the 1 269 state elements
    differ, worst 7.8e-15 as a fraction and 1.9e-12 L on an accumulator.

    Both halves are asserted, because each alone permits a failure the other
    catches. That the difference is *real* is what makes the condition worth
    enforcing; that it is *this small* is what makes enforcing it in code the
    only way to catch it, since it is nine orders below the 1e-4 a compartment
    readout resolves and six below the 1e-6 L the mass balance is shown to. A
    branch built this way would look exactly like one built correctly.

    It fails honestly if a future change makes the restart exact, which would
    mean the condition had stopped costing anything and this file had a
    sentence to delete rather than a bug to fix.
    """

    parent = _run_definition()
    segment = parent.segment_at(FORK_BETWEEN_KEYFRAMES_S)
    restarted = RunDefinition(
        segment.settings,
        parent.state_at(FORK_BETWEEN_KEYFRAMES_S),
        opened_at_s=FORK_BETWEEN_KEYFRAMES_S,
    )
    restarted.advance_to(RUN_LENGTH_S)

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
    """The separation is refused by the program, not asserted by the document.

    A fork's opening state and a drawn column are the same nine numbers in the
    same order, so nothing about their contents distinguishes them; what does
    is that one of them is not a state vector at all.
    """

    definition = _run_definition()
    drawn = definition.evaluate(0.0, RUN_LENGTH_S, 600).states[0]

    assert isinstance(drawn, DisplayState)
    assert not isinstance(drawn, tuple)

    with pytest.raises(SimulationConfigurationError, match="came from the display path"):
        RunDefinition(_settings_at(definition, 0.0), drawn, opened_at_s=0.0)  # type: ignore[arg-type]


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
    wrapper would be cost with no benefit. This is what would say so - and it
    fails honestly if a future change makes chaining exact, which is a result
    worth having rather than a broken test.
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
