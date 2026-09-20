"""Verification of the closed-form run against the stepped run it replaces.

The run definition's claim is that a run needs no samples: the settings it was computed
under determine every state it passed through, so a value can be recovered
rather than recalled. What that has to be checked against is the stepped path
itself, because the two are meant to describe the same run - so the central
tests here drive `AgentUptakeSystem` step by step, build a run definition from exactly
the same setting changes at exactly the same instants, and compare.

The tolerances are measured rather than chosen, and they are stated as
absolute differences in a fraction of one atmosphere because that is the
quantity displayed. Measured 2026-09-07 over a 600 s sevoflurane run with two
setting changes, against a run whose largest fraction reaches 0.0316:

    canonical (`state_at`) against the stepped run    1.8e-14
    display   (`evaluate`) against the stepped run    3.7e-15

Both are eleven orders below the 1e-4 the two-decimal percent readout can
show, so neither path can move a displayed digit. The difference between the
two paths is composition order rather than method error, and `docs/MODEL.md`
§ "The canonical evaluation rule" states which of them a stored value may come
from. `tests/reference/test_canonical_evaluation.py` holds that guarantee; what
is tested here is that the display path is refused where the rule says it is.
"""

from bisect import bisect_right
from math import inf, nan

import pytest

from anesthesia_sim.core import run_definition
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.matrix_exponential import Matrix
from anesthesia_sim.core.run_definition import (
    DisplayState,
    Keyframe,
    RunDefinition,
    RunSegment,
    SampledWindow,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

SIMULATION_STEP_S = 0.1
COMPARTMENT_STATES = (
    INSPIRED_FRACTION,
    ALVEOLAR_FRACTION,
    VENOUS_FRACTION,
    FIRST_TISSUE_FRACTION,
    FIRST_TISSUE_FRACTION + 1,
    FIRST_TISSUE_FRACTION + 2,
)
"""The six compartment fractions, in the order `_compartments` reads them."""

WORST_CANONICAL_DIFFERENCE = 5e-14
WORST_DISPLAY_DIFFERENCE = 5e-14
"""Absolute agreement required with the stepped run, in a fraction of 1 atm.

Both measured at or below 1.8e-14; see the module docstring. Rounded up to one
figure so an ordinary floating-point wobble does not fail the suite, and left
far below the 1e-4 a readout can show so a real divergence still does.
"""


def _compartments(system: AgentUptakeSystem) -> tuple[float, ...]:
    """The six compartment fractions the run records, in state order."""

    return (
        system.circuit.inspired_partial_pressure_fraction,
        system.alveoli.partial_pressure_fraction,
        system.patient.mixed_venous_partial_pressure_fraction,
        *(tissue.partial_pressure_fraction for tissue in system.patient.tissues),
    )


def _stepped_run(
    steps: int = 6000, changes: dict[int, tuple[str, float]] | None = None
) -> tuple[AgentUptakeSystem, RunDefinition, dict[float, tuple[float, ...]]]:
    """Step a run and build the run definition of the same run, returning both and the samples.

    The changes are applied to the system and recorded on the run definition at the
    same instant and in the same order the app layer does it: the setter
    first, so the core has accepted the value, then the run definition, which reads the
    settings back out of the compartments rather than taking the argument.
    """

    if changes is None:
        changes = {
            300: ("set_delivered_partial_pressure_fraction", 0.04),
            1200: ("set_alveolar_ventilation", 6.0),
        }

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    stepped = {0.0: _compartments(system)}

    for step in range(1, steps + 1):
        system.advance(SIMULATION_STEP_S)
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        definition.advance_to(elapsed_s)

        if step in changes:
            setter, value = changes[step]
            getattr(system, setter)(value)
            definition.record_change(system.equation_settings())

        stepped[elapsed_s] = _compartments(system)

    return system, definition, stepped


def test_evaluate_matches_a_stepped_run() -> None:
    """A window's states are the ones the stepped run actually reached.

    The whole claim of the run definition in one test: a run that recorded nothing
    answers for every instant a run that recorded everything passed through,
    across two setting changes and to within a difference no display can show.
    """

    _, definition, stepped = _stepped_run()
    window = definition.evaluate(0.0, 600.0, 601)

    assert len(window.states) == 601

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        expected = stepped[round(elapsed_s, 6)]

        for compartment, want in zip(COMPARTMENT_STATES, expected, strict=True):
            assert abs(state.values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_state_at_matches_a_stepped_run() -> None:
    """The canonical path answers the same run, at instants of its own choosing."""

    _, definition, stepped = _stepped_run()

    for step in range(0, 6001, 37):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        state = definition.state_at(elapsed_s)

        for compartment, want in zip(COMPARTMENT_STATES, stepped[elapsed_s], strict=True):
            assert abs(state[compartment] - want) < WORST_CANONICAL_DIFFERENCE


def test_the_canonical_path_answers_bit_identically_twice() -> None:
    """Two canonical evaluations of one definition at one instant agree exactly.

    Not to a tolerance: the same sequence of operations on the same values.
    This is the property a keyframe, an export and a fork's starting state
    rest on, and `PL-P1Z3` is what states it in `docs/MODEL.md` and gates it
    against the display path.
    """

    _, definition, _ = _stepped_run(steps=900)

    for step in (0, 1, 299, 300, 301, 899, 900):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)

        assert definition.state_at(elapsed_s) == definition.state_at(elapsed_s)


def test_the_accumulated_agent_matches_the_run_s_own_accounting() -> None:
    """Delivered and exhausted agent come back as running totals, not per-segment ones.

    The two accumulator rows have no diagonal entry, so a propagator maps each
    to itself with coefficient one and a cumulative total carried through is
    the same arithmetic as one restarted every segment. This is what lets the
    closed form answer the mass balance at any instant without stepping to it.
    """

    system, definition, _ = _stepped_run()
    accounting = system.agent_simulation_validation
    final = definition.state_at(600.0)

    assert final[DELIVERED_AGENT_L] == pytest.approx(accounting.delivered_agent_l, rel=1e-9)
    assert final[EXHAUSTED_AGENT_L] == pytest.approx(accounting.exhausted_agent_l, rel=1e-9)
    assert final[DELIVERED_AGENT_L] > definition.state_at(300.0)[DELIVERED_AGENT_L] > 0.0


def test_a_window_reads_only_the_segments_it_covers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Frame cost follows the window, not the run's length.

    The claim `PL-T691` exists for, tested structurally rather than by the
    clock: a matrix exponential is what a window pays per segment it covers,
    so counting them says whether the run's other 1 498 segments were touched.
    A timing assertion would say the same thing and fail on a busy machine.
    """

    exponentials = 0
    exact = run_definition.matrix_exponential

    def counting_exponential(matrix: Matrix, interval_s: float) -> Matrix:
        nonlocal exponentials
        exponentials += 1

        return exact(matrix, interval_s)

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    total_s = 30 * 24 * 3600.0

    for change in range(1, 1501):
        definition.advance_to(change * total_s / 1501)
        system.set_delivered_partial_pressure_fraction(0.01 + 0.005 * (change % 4))
        definition.record_change(system.equation_settings())

    definition.advance_to(total_s)

    assert len(definition.segments) == 1501

    monkeypatch.setattr(run_definition, "matrix_exponential", counting_exponential)
    definition.evaluate(total_s - 3600.0, total_s, 600)

    # This run changes a setting every 1 728 s, so the last hour covers three
    # segments at most, and a segment costs two propagators - one for the
    # offset from its keyframe to its first column, one for the column
    # spacing. An implementation that walked the run instead of the window
    # would be building on the order of the 1 501 segments behind it.
    assert exponentials <= 6
    assert exponentials < len(definition.segments) / 100


def test_a_run_under_unchanged_settings_is_one_segment() -> None:
    """Recording the settings already in force describes no change, so none is kept."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(10.0)
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1


def test_two_changes_at_one_instant_are_one_segment() -> None:
    """Two controls moved between one step and the next open one stretch, not two.

    The run was computed under whatever stood when the step ran, so a
    zero-length segment would describe a stretch the model never integrated.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(10.0)
    system.set_delivered_partial_pressure_fraction(0.03)
    definition.record_change(system.equation_settings())
    system.set_cardiac_output(4.0)
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2
    assert definition.segments[-1].opening.instant_s == 10.0
    assert definition.segments[-1].settings.cardiac_output_l_s == pytest.approx(4.0 / 60.0)
    assert definition.segments[-1].settings.delivered_partial_pressure_fraction == pytest.approx(
        0.03
    )


def test_a_change_opens_a_segment_at_the_run_s_own_reach() -> None:
    """A recorded change opens its segment where the run had got to, and nowhere else."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(12.5)
    system.set_fresh_gas_flow(1.5)
    definition.record_change(system.equation_settings())

    assert [segment.opening.instant_s for segment in definition.segments] == [0.0, 12.5]
    assert definition.segments[-1].opening.state == definition.state_at(12.5)


def test_the_run_starts_where_the_system_does() -> None:
    """A definition opened from a system's state answers that state at zero."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    assert definition.reached_s == 0.0
    assert definition.state_at(0.0) == system.state_vector()


def test_advancing_to_the_time_already_reached_changes_nothing() -> None:
    """Two steps' worth of bookkeeping at one instant is not an error."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(5.0)
    definition.advance_to(5.0)

    assert definition.reached_s == 5.0


def test_a_one_column_window_is_the_instant_asked_for() -> None:
    """`columns` of one returns `start_s` alone, with no spacing to divide by."""

    _, definition, stepped = _stepped_run(steps=100)
    window = definition.evaluate(4.0, 10.0, 1)

    assert window.times_s == (4.0,)
    assert len(window.states) == 1

    for compartment, want in zip(COMPARTMENT_STATES, stepped[4.0], strict=True):
        assert abs(window.states[0].values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_a_window_of_no_width_repeats_one_instant() -> None:
    """Every column of a zero-width window is the same state, not a divide by zero."""

    _, definition, _ = _stepped_run(steps=100)
    window = definition.evaluate(6.0, 6.0, 5)

    assert window.times_s == (6.0,) * 5
    assert set(window.states) == {DisplayState(definition.state_at(6.0))}


def test_a_window_opening_on_a_keyframe_needs_no_propagation() -> None:
    """The state at a segment's own opening is that segment's keyframe, unaltered."""

    _, definition, _ = _stepped_run(steps=600)
    window = definition.evaluate(30.0, 60.0, 4)

    assert window.states[0].values == definition.segments[1].opening.state


def test_a_segment_too_short_to_hold_a_column_is_skipped() -> None:
    """A window whose columns straddle a whole segment still reads the right one.

    A walk that assumed one segment per column would hand the column after the
    gap the skipped segment's settings, and draw a stretch of the run under
    settings it was never computed under.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    for elapsed_s, flow in ((10.0, 1.5), (10.5, 3.0), (60.0, 5.0)):
        definition.advance_to(elapsed_s)
        system.set_fresh_gas_flow(flow)
        definition.record_change(system.equation_settings())

    definition.advance_to(120.0)
    window = definition.evaluate(0.0, 120.0, 5)

    assert len(definition.segments) == 4
    assert window.times_s == (0.0, 30.0, 60.0, 90.0, 120.0)

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        canonical = definition.state_at(elapsed_s)

        for compartment in COMPARTMENT_STATES:
            difference = abs(state.values[compartment] - canonical[compartment])

            assert difference < WORST_DISPLAY_DIFFERENCE


def test_a_run_definition_refuses_a_display_state_as_its_opening_state() -> None:
    """A fork opening from a drawing value is the failure the wrapper exists to stop.

    `RunDefinition.__init__` is the canonical sink a display value is likeliest to
    reach by accident, because a fork's opening state and a drawn column are
    the same nine numbers in the same order. The refusal is what makes them
    different things rather than the same thing described differently.
    """

    _, definition, _ = _stepped_run(steps=100)
    drawn = definition.evaluate(0.0, 10.0, 5).states[0]
    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match="came from the display path"):
        RunDefinition(system.equation_settings(), drawn, opened_at_s=0.0)  # type: ignore[arg-type]


def test_a_display_state_is_not_a_state_vector() -> None:
    """The structural half of the guarantee, which is what protects a sink that has no check.

    A tuple subclass would have satisfied every test above while flowing
    silently into an exporter or a save format that indexes a state and asks
    nothing. What stops that is the value not being a sequence at all.
    """

    _, definition, _ = _stepped_run(steps=100)
    drawn = definition.evaluate(0.0, 10.0, 5).states[0]

    assert not isinstance(drawn, tuple)
    assert isinstance(drawn.values, tuple)
    assert len(drawn.values) == STATE_SIZE


def test_a_run_definition_refuses_a_state_of_the_wrong_length() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match=f"the equations carry {STATE_SIZE}"):
        RunDefinition(system.equation_settings(), (0.0, 1.0), opened_at_s=0.0)


def test_a_run_definition_refuses_a_non_finite_state() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[ALVEOLAR_FRACTION] = nan

    with pytest.raises(SimulationConfigurationError, match="which is not finite"):
        RunDefinition(system.equation_settings(), tuple(state), opened_at_s=0.0)


def test_a_run_definition_refuses_a_state_whose_unit_is_not_one() -> None:
    """The forcing terms are read against this entry, so it is not a free value."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[UNIT_STATE] = 0.5

    with pytest.raises(SimulationConfigurationError, match="the constant one"):
        RunDefinition(system.equation_settings(), tuple(state), opened_at_s=0.0)


@pytest.mark.parametrize("opened_at_s", [nan, inf])
def test_a_run_definition_refuses_to_open_at_a_non_finite_instant(opened_at_s: float) -> None:
    """The opening is validated where the state vector is, and for the same reason.

    It is the instant every later answer is measured from: a definition opened
    at a non-finite one would propagate over a non-finite interval and hand
    back a state of `nan`, which no bounds check downstream can distinguish
    from a run that genuinely reached one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=opened_at_s)


def test_a_run_definition_refuses_to_open_before_induction() -> None:
    """The case's axis starts at induction, so no run on it opens before zero."""

    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match="at or after induction"):
        RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=-1.0)


def test_a_run_refuses_to_go_backwards() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(20.0)

    with pytest.raises(SimulationConfigurationError, match="cannot go back"):
        definition.advance_to(19.9)


def test_a_run_refuses_a_non_finite_reach() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        definition.advance_to(inf)


@pytest.mark.parametrize("instant_s", [nan, inf])
def test_a_run_definition_refuses_a_non_finite_instant(instant_s: float) -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        definition.state_at(instant_s)


def test_a_run_definition_has_no_state_before_the_run_began() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.state_at(-0.1)


def _opening_after_zero() -> RunDefinition:
    """A definition opening at 600 s, which is the shape a branch forked there carries.

    Built through the public constructor since `PL-ZMRT`: the run opens on the
    case's own axis at 600 s and records a change at 900 s, so the guards below
    are exercised against the arrangement `SimulationController` actually
    builds rather than against a synthesized one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_partial_pressure_fraction(0.02)
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=600.0)

    definition.advance_to(900.0)
    system.set_delivered_partial_pressure_fraction(0.005)
    definition.record_change(system.equation_settings())

    definition.advance_to(1200.0)

    return definition


def test_a_run_definition_reports_the_instant_it_opens_at() -> None:
    """The one place a definition's own opening is named, and it is not the reach.

    Read directly rather than through a caller, because since `PL-B8MK` the
    app layer has one of its own: a branch's *beginning* is its fork, which a
    bookmark fork puts after the keyframe its definition opens at, so
    `SimulationController.began_at_s` is what clips a drawn axis and this is
    what says where the definition may be evaluated from. The two were one
    number until a bookmark became forkable, and a test reaching this through
    the app layer could not tell them apart.
    """

    trunk_shaped = RunDefinition(
        AgentUptakeSystem.for_agent("sevoflurane").equation_settings(),
        AgentUptakeSystem.for_agent("sevoflurane").state_vector(),
        opened_at_s=0.0,
    )

    assert trunk_shaped.opened_at_s == 0.0

    branch_shaped = _opening_after_zero()

    # It is the first segment's own instant, and recording changes and
    # advancing the reach past them leaves it where it was.
    assert branch_shaped.opened_at_s == 600.0
    assert branch_shaped.segments[0].opening.instant_s == 600.0
    assert branch_shaped.reached_s == 1200.0


def test_a_run_definition_that_opens_after_zero_refuses_the_span_before_it() -> None:
    """The lower bound is the run's own opening, never the literal zero.

    What a bound fixed at zero admits is not a wrong refusal but a silent
    wrong answer. `_segment_index_at` answers `-1` for an instant before the
    first opening, Python reads that as the *last* segment, and `_propagator`
    returns `None` for the non-positive interval that follows - so the caller
    is handed that segment's keyframe as the state at an instant the run did
    not exist for. Measured on this definition before the guard:
    `state_at(0.0)`, `state_at(100.0)` and `state_at(599.9)` all returned the
    same 0.005664 alveolar fraction rather than refusing, and
    `evaluate_anchored(0.0, 500.0, 100.0)` drew a varying curve across a span
    the run had no state for.
    """

    definition = _opening_after_zero()

    for elapsed_s in (0.0, 100.0, 599.9):
        with pytest.raises(SimulationConfigurationError, match="before it began"):
            definition.state_at(elapsed_s)

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.evaluate_anchored(0.0, 500.0, 100.0)

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.evaluate(0.0, 500.0, 6)


def test_a_run_definition_answers_at_its_own_opening() -> None:
    """The bound admits the opening itself, which is where the run's first keyframe is."""

    definition = _opening_after_zero()

    assert definition.state_at(600.0) == definition.segments[0].opening.state


def test_a_run_definition_is_under_no_settings_before_it_opens() -> None:
    """The second of the two guards, which only a direct call can reach.

    `_require_within_run` refuses the instant on every public path, so this
    one can never fire through `state_at`, `evaluate` or `evaluate_anchored`
    while that bound is right. It is here because the two protect against the
    same silent answer by different means: the bound says the run has no state
    there, and this says the search found no segment. A future caller reaching
    the walk without the bound - `_canonical_state_at` is already one, by
    design - meets a refusal rather than the last segment's keyframe.
    """

    definition = _opening_after_zero()

    with pytest.raises(SimulationConfigurationError, match="under no settings"):
        definition._segment_index_at(599.9)


def test_a_run_definition_refuses_to_predict_past_the_run() -> None:
    """Answering past the run would return a prediction indistinguishable from it."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        definition.state_at(30.1)


def test_a_window_needs_at_least_one_column() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    with pytest.raises(SimulationConfigurationError, match="at least one column"):
        definition.evaluate(0.0, 0.0, 0)


def test_a_window_refuses_to_end_before_it_begins() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="ends before it begins"):
        definition.evaluate(20.0, 10.0, 5)


def test_a_window_refuses_to_reach_past_the_run() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        definition.evaluate(10.0, 30.1, 5)


def test_a_sampled_window_pairs_each_state_with_one_instant() -> None:
    """Times and states of different lengths would draw a trace off its own axis."""

    with pytest.raises(SimulationConfigurationError, match="belongs to one instant"):
        SampledWindow(times_s=(0.0, 1.0), states=(DisplayState((0.0,) * STATE_SIZE),))


def test_a_segment_carries_the_state_its_settings_start_from() -> None:
    """The pairing `RunSegment` exists for, read back off a recorded run."""

    _, definition, _ = _stepped_run(steps=600)
    segment = definition.segments[1]

    assert isinstance(segment, RunSegment)
    assert isinstance(segment.opening, Keyframe)
    assert segment.opening.instant_s == 30.0
    assert len(segment.opening.state) == STATE_SIZE
    assert segment.opening.state[UNIT_STATE] == 1.0


def test_a_change_undone_before_a_step_runs_leaves_no_segment() -> None:
    """A dial moved and moved back between two steps describes no change at all.

    The stretch it opened is dropped rather than left standing with the
    settings it started from, which would put a keyframe in the run definition for an
    instant the run passed through unremarkably. The interface's own control
    timeline drops the matching entry for the same reason.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(10.0)
    system.set_delivered_partial_pressure_fraction(0.03)
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2

    system.set_delivered_partial_pressure_fraction(0.02)
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].opening.instant_s == 0.0


def test_the_first_stretch_is_kept_even_when_a_change_returns_to_it() -> None:
    """There is no earlier stretch to fold the opening one back into.

    The run's first segment opens at zero and carries the settings the run
    began under, so a change recorded at zero replaces those settings rather
    than dropping a stretch that nothing precedes.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    system.set_delivered_partial_pressure_fraction(0.05)
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].settings.delivered_partial_pressure_fraction == pytest.approx(
        0.05
    )


def test_anchored_columns_land_on_multiples_of_the_spacing() -> None:
    """The grid is measured from the case's zero, not from the window's left edge.

    This is what makes a following window reuse its column times, and it is
    the property `evaluate` deliberately does not have.
    """

    _, definition, _ = _stepped_run()
    spacing_s = 7.0
    window = definition.evaluate_anchored(103.0, 297.0, spacing_s)
    interior = [time_s for time_s in window.times_s if time_s not in (103.0, 297.0)]
    events = {segment.opening.instant_s for segment in definition.segments}

    assert interior
    for time_s in interior:
        if time_s in events:
            continue
        assert time_s % spacing_s == pytest.approx(0.0, abs=1e-9)


def test_a_following_window_reuses_every_column_time_but_its_edge() -> None:
    """A frame moves one point rather than all of them.

    `PL-Q197` measured every drawn point moving on every frame as what
    saturated the client. Anchoring the evaluation times to the run is that
    fix applied to the closed-form path, so a window advancing by less than
    the spacing keeps every interior column it had.
    """

    _, definition, _ = _stepped_run()
    spacing_s = 4.0
    # Neither edge is a multiple of the spacing, which is the ordinary case:
    # the right edge is whatever instant the run has reached this frame.
    before = set(definition.evaluate_anchored(0.0, 401.0, spacing_s).times_s)
    after = set(definition.evaluate_anchored(0.0, 402.0, spacing_s).times_s)

    # Only the moving right-hand bound leaves, and only it arrives; every
    # interior column keeps the instant it had, so its drawn point does not
    # move and the client is not sent it.
    assert before - after == {401.0}
    assert after - before == {402.0}


def test_every_control_event_inside_the_window_is_a_column() -> None:
    """The drawn chart reproduces every control change.

    A grid alone steps over a dial change, and the trajectory's only sharp
    features are at events, so a window that misses one draws a straight
    line through the single instant a reader is looking for.
    """

    _, definition, _ = _stepped_run()
    # A spacing far wider than the gap between the two recorded changes, so
    # no grid column could land on either by luck.
    window = definition.evaluate_anchored(0.0, 600.0, 250.0)
    events = {
        segment.opening.instant_s
        for segment in definition.segments
        if 0.0 < segment.opening.instant_s < 600.0
    }

    assert events
    assert events <= set(window.times_s)


def test_an_event_column_is_its_own_keyframe_exactly() -> None:
    """An event column is read, not propagated: no interval, no error, no cost."""

    _, definition, _ = _stepped_run()
    window = definition.evaluate_anchored(0.0, 600.0, 250.0)
    by_time = dict(zip(window.times_s, window.states, strict=True))

    for segment in definition.segments:
        if 0.0 < segment.opening.instant_s < 600.0:
            assert by_time[segment.opening.instant_s].values == segment.opening.state


def test_anchored_matches_a_stepped_run() -> None:
    """Every anchored column is the state the stepped run actually reached."""

    _, definition, stepped = _stepped_run()
    window = definition.evaluate_anchored(0.0, 600.0, SIMULATION_STEP_S * 10)

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        expected = stepped[round(elapsed_s, 6)]

        for compartment, want in zip(COMPARTMENT_STATES, expected, strict=True):
            assert abs(state.values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_both_bounds_are_columns_so_the_trace_ends_where_the_readouts_do() -> None:
    """The right-hand end of a trace is the instant the readouts are showing."""

    _, definition, _ = _stepped_run()
    window = definition.evaluate_anchored(103.0, 297.5, 7.0)

    assert window.times_s[0] == 103.0
    assert window.times_s[-1] == 297.5


def test_an_anchored_window_of_no_width_is_one_column() -> None:
    """Both bounds are the same instant, so the window is that instant alone."""

    _, definition, _ = _stepped_run(steps=100)
    window = definition.evaluate_anchored(6.0, 6.0, 1.0)

    assert window.times_s == (6.0,)
    assert window.states[0] == DisplayState(definition.state_at(6.0))


@pytest.mark.parametrize("spacing_s", [0.0, -1.0, float("inf"), float("nan")])
def test_an_anchored_window_refuses_a_spacing_that_is_not_an_interval(spacing_s: float) -> None:
    """A column spacing is a positive, finite interval or it is not one."""

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(SimulationConfigurationError):
        definition.evaluate_anchored(0.0, 10.0, spacing_s)


def test_an_anchored_window_refuses_bounds_the_run_has_not_reached() -> None:
    """A window past the run's duration would be a prediction rather than the run."""

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(SimulationConfigurationError):
        definition.evaluate_anchored(0.0, definition.reached_s + 1.0, 1.0)

    with pytest.raises(SimulationConfigurationError):
        definition.evaluate_anchored(5.0, 1.0, 1.0)


"""Why a fork opens at a keyframe, measured rather than asserted (`PL-TFX5`).

`SimulationController.resumed_at` refuses an instant the run holds no keyframe
for, and `docs/MODEL.md` § "The canonical evaluation rule" says why: restarting
from the canonical state at such an instant replaces one propagation over an
interval with two over its halves. That section measures what the substitution
costs; this measures that it costs anything at all, which is the half a refusal
rests on. Without it nothing would catch the refusal being relaxed into an
approximation on the grounds that the difference is too small to matter.
"""

# One hour past a fork at 655.3 s on the two-change sevoflurane run below,
# pinned as a ceiling rather than as an equality: it is a floating-point
# composition difference, so a compiler, a platform or an unrelated change in
# `matrix_exponential` may move it, and what the claim needs is that it is real
# and this small. The order of magnitude agrees with the 5.3e-13 accumulator
# figure `docs/MODEL.md` records for the same substitution on a different run;
# that section is the authority for the size, and this is not a second claim
# about it.
FORK_OFF_KEYFRAME_DIVERGENCE_CEILING = 1e-12

FORK_S = 655.3
PROBES_S = (700.0, 800.0, 900.0, 1200.0, 1800.0, 3600.0)


def _two_change_run() -> RunDefinition:
    """A sevoflurane run to an hour, carrying two setting changes."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    definition.advance_to(300.0)
    system.set_delivered_partial_pressure_fraction(Fraction(0.02))
    definition.record_change(system.equation_settings())
    definition.advance_to(600.0)
    system.set_fresh_gas_flow(1.0)
    definition.record_change(system.equation_settings())
    definition.advance_to(3600.0)

    return definition


def _worst(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def test_opening_a_branch_off_a_keyframe_does_not_reproduce_the_run() -> None:
    """The refusal's reason, as a number.

    A branch opened from the canonical state at an instant the run holds no
    keyframe for reaches that state by one propagation and then continues by a
    second, where the run answers the same later instant with one propagation
    over the whole span. The two are the same exact solution rounded
    differently, which is precisely what `PL-Z3W6`'s element-wise requirement
    refuses - so this asserts the disagreement is non-zero as well as small,
    because a test that only bounded it would pass if forking became exact by
    accident and stop describing anything.

    Both runs are asked for the same instant in the same float, because the
    branch opens at the fork on the case's own axis (`PL-ZMRT`). What is left
    in the measurement is therefore one propagation against two and nothing
    else, where a branch re-based to its own zero would have carried a frame
    conversion into the same number.
    """

    parent = _two_change_run()
    branch = RunDefinition(
        parent.segments[-1].settings, parent.state_at(FORK_S), opened_at_s=FORK_S
    )
    branch.advance_to(3600.0)

    divergences = [_worst(branch.state_at(p), parent.state_at(p)) for p in PROBES_S]

    assert all(divergence > 0.0 for divergence in divergences)
    assert max(divergences) < FORK_OFF_KEYFRAME_DIVERGENCE_CEILING


def test_a_pixel_wide_chord_misses_an_extremum_by_under_the_readout_s_resolution() -> None:
    """`PL-GS3R`'s guarantee, at the one point the pixel argument does not reach.

    Between two drawn instants both exact and no more than a pixel of time
    apart, a *monotone* run and the segment ruled between them cross every
    level inside the same pixel. Where the run turns between two dial
    changes - the alveoli and the venous blood keep filling for a moment
    after the vaporizer is turned down - it can rise above both drawn values
    inside one interval, and the line falls short of it there. Measured
    2026-09-14 over the supported envelope, the worst case is this one: a
    desflurane overpressure induction at the fastest supported settings,
    turned down at 600 s, drawn at the twelve-hour base on a 1 000 px plot,
    where the mixed venous trace rises 0.0028 pp above the drawn line at
    t = 609 s. Held at half the readout's resolution, so a real regression
    fails and the closed form's floating-point wobble does not. The truth is
    taken over the 1 800 s after each change, which is where every measured
    departure sits; beyond it the same run is within 0.0024 pp even at the
    290 s chord the fixed budget used to draw.
    """

    system = AgentUptakeSystem.for_agent("desflurane")
    system.set_fresh_gas_flow(10.0)
    system.set_alveolar_ventilation(12.0)
    system.set_cardiac_output(10.0)
    system.set_delivered_partial_pressure_fraction(0.12)
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)
    definition.advance_to(600.0)
    system.set_delivered_partial_pressure_fraction(0.06)
    definition.record_change(system.equation_settings())
    definition.advance_to(43_200.0)

    pixel_s = 43_200.0 / 1000.0
    drawn = definition.evaluate_anchored(0.0, 43_200.0, pixel_s)
    last = len(drawn.states) - 1
    fractions = (
        INSPIRED_FRACTION,
        ALVEOLAR_FRACTION,
        VENOUS_FRACTION,
        FIRST_TISSUE_FRACTION,
        FIRST_TISSUE_FRACTION + 1,
        FIRST_TISSUE_FRACTION + 2,
    )
    worst = 0.0

    for opening_s in (0.0, 600.0):
        truth = definition.evaluate_anchored(opening_s, opening_s + 1800.0, 0.1)

        for instant_s, state in zip(truth.times_s, truth.states, strict=True):
            after = bisect_right(drawn.times_s, instant_s)
            left = drawn.states[max(after - 1, 0)].values
            right = drawn.states[min(after, last)].values

            for index in fractions:
                low, high = min(left[index], right[index]), max(left[index], right[index])
                worst = max(worst, state.values[index] - high, low - state.values[index])

    assert worst * 100.0 < 0.005
