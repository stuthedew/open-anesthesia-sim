"""Verification of the closed-form run against the stepped run it replaces.

The score's claim is that a run needs no samples: the settings it was computed
under determine every state it passed through, so a value can be recovered
rather than recalled. What that has to be checked against is the stepped path
itself, because the two are meant to describe the same run - so the central
tests here drive `AgentUptakeSystem` step by step, build a score from exactly
the same setting changes at exactly the same instants, and compare.

The tolerances are measured rather than chosen, and they are stated as
absolute differences in a fraction of one atmosphere because that is the
quantity displayed. Measured 2026-09-07 over a 600 s sevoflurane run with two
setting changes, against a run whose largest fraction reaches 0.0316:

    canonical (`state_at`) against the stepped run    1.8e-14
    display   (`evaluate`) against the stepped run    3.7e-15

Both are eleven orders below the 1e-4 the two-decimal percent readout can
show, so neither path can move a displayed digit. The difference between the
two paths is composition order rather than method error; `PL-P1Z3` states that
separation as a guarantee and gates it.
"""

from math import inf, nan

import pytest

from anesthesia_sim.core import run_score
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
from anesthesia_sim.core.run_score import Keyframe, RunScore, SampledWindow, ScoreSegment
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
        system.circuit.circuit_concentration_fraction,
        system.alveoli.concentration_fraction,
        system.patient.mixed_venous_fraction,
        *(tissue.partial_pressure_fraction for tissue in system.patient.tissues),
    )


def _stepped_run(
    steps: int = 6000, changes: dict[int, tuple[str, float]] | None = None
) -> tuple[AgentUptakeSystem, RunScore, dict[float, tuple[float, ...]]]:
    """Step a run and build the score of the same run, returning both and the samples.

    The changes are applied to the system and recorded on the score at the
    same instant and in the same order the app layer does it: the setter
    first, so the core has accepted the value, then the score, which reads the
    settings back out of the compartments rather than taking the argument.
    """

    if changes is None:
        changes = {
            300: ("set_delivered_concentration", 0.04),
            1200: ("set_alveolar_ventilation", 6.0),
        }

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    stepped = {0.0: _compartments(system)}

    for step in range(1, steps + 1):
        system.advance(SIMULATION_STEP_S)
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        score.advance_to(elapsed_s)

        if step in changes:
            setter, value = changes[step]
            getattr(system, setter)(value)
            score.record_change(system.equation_settings())

        stepped[elapsed_s] = _compartments(system)

    return system, score, stepped


def test_evaluate_matches_a_stepped_run() -> None:
    """A window's states are the ones the stepped run actually reached.

    The whole claim of the score in one test: a run that recorded nothing
    answers for every instant a run that recorded everything passed through,
    across two setting changes and to within a difference no display can show.
    """

    _, score, stepped = _stepped_run()
    window = score.evaluate(0.0, 600.0, 601)

    assert len(window.states) == 601

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        expected = stepped[round(elapsed_s, 6)]

        for compartment, want in zip(COMPARTMENT_STATES, expected, strict=True):
            assert abs(state[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_state_at_matches_a_stepped_run() -> None:
    """The canonical path answers the same run, at instants of its own choosing."""

    _, score, stepped = _stepped_run()

    for step in range(0, 6001, 37):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        state = score.state_at(elapsed_s)

        for compartment, want in zip(COMPARTMENT_STATES, stepped[elapsed_s], strict=True):
            assert abs(state[compartment] - want) < WORST_CANONICAL_DIFFERENCE


def test_the_canonical_path_answers_bit_identically_twice() -> None:
    """Two canonical evaluations of one score at one instant agree exactly.

    Not to a tolerance: the same sequence of operations on the same values.
    This is the property a keyframe, an export and a fork's starting state
    rest on, and `PL-P1Z3` is what states it in `docs/MODEL.md` and gates it
    against the display path.
    """

    _, score, _ = _stepped_run(steps=900)

    for step in (0, 1, 299, 300, 301, 899, 900):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)

        assert score.state_at(elapsed_s) == score.state_at(elapsed_s)


def test_the_accumulated_agent_matches_the_run_s_own_accounting() -> None:
    """Delivered and exhausted agent come back as running totals, not per-segment ones.

    The two accumulator rows have no diagonal entry, so a propagator maps each
    to itself with coefficient one and a cumulative total carried through is
    the same arithmetic as one restarted every segment. This is what lets the
    closed form answer the mass balance at any instant without stepping to it.
    """

    system, score, _ = _stepped_run()
    accounting = system.agent_simulation_validation
    final = score.state_at(600.0)

    assert final[DELIVERED_AGENT_L] == pytest.approx(accounting.delivered_agent_l, rel=1e-9)
    assert final[EXHAUSTED_AGENT_L] == pytest.approx(accounting.exhausted_agent_l, rel=1e-9)
    assert final[DELIVERED_AGENT_L] > score.state_at(300.0)[DELIVERED_AGENT_L] > 0.0


def test_a_window_reads_only_the_segments_it_covers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Frame cost follows the window, not the run's length.

    The claim `PL-T691` exists for, tested structurally rather than by the
    clock: a matrix exponential is what a window pays per segment it covers,
    so counting them says whether the run's other 1 498 segments were touched.
    A timing assertion would say the same thing and fail on a busy machine.
    """

    exponentials = 0
    exact = run_score.matrix_exponential

    def counting_exponential(matrix: Matrix, interval_s: float) -> Matrix:
        nonlocal exponentials
        exponentials += 1

        return exact(matrix, interval_s)

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    total_s = 30 * 24 * 3600.0

    for change in range(1, 1501):
        score.advance_to(change * total_s / 1501)
        system.set_delivered_concentration(0.01 + 0.005 * (change % 4))
        score.record_change(system.equation_settings())

    score.advance_to(total_s)

    assert len(score.segments) == 1501

    monkeypatch.setattr(run_score, "matrix_exponential", counting_exponential)
    score.evaluate(total_s - 3600.0, total_s, 600)

    # This run changes a setting every 1 728 s, so the last hour covers three
    # segments at most, and a segment costs two propagators - one for the
    # offset from its keyframe to its first column, one for the column
    # spacing. An implementation that walked the run instead of the window
    # would be building on the order of the 1 501 segments behind it.
    assert exponentials <= 6
    assert exponentials < len(score.segments) / 100


def test_a_run_under_unchanged_settings_is_one_segment() -> None:
    """Recording the settings already in force describes no change, so none is kept."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(10.0)
    score.record_change(system.equation_settings())

    assert len(score.segments) == 1


def test_two_changes_at_one_instant_are_one_segment() -> None:
    """Two controls moved between one step and the next open one stretch, not two.

    The run was computed under whatever stood when the step ran, so a
    zero-length segment would describe a stretch the model never integrated.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(10.0)
    system.set_delivered_concentration(0.03)
    score.record_change(system.equation_settings())
    system.set_cardiac_output(4.0)
    score.record_change(system.equation_settings())

    assert len(score.segments) == 2
    assert score.segments[-1].opening.elapsed_s == 10.0
    assert score.segments[-1].settings.cardiac_output_l_s == pytest.approx(4.0 / 60.0)
    assert score.segments[-1].settings.delivered_concentration_fraction == pytest.approx(0.03)


def test_a_change_opens_a_segment_at_the_run_s_own_reach() -> None:
    """A recorded change opens its segment where the run had got to, and nowhere else."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(12.5)
    system.set_fresh_gas_flow(1.5)
    score.record_change(system.equation_settings())

    assert [segment.opening.elapsed_s for segment in score.segments] == [0.0, 12.5]
    assert score.segments[-1].opening.state == score.state_at(12.5)


def test_the_run_starts_where_the_system_does() -> None:
    """A score opened from a system's state answers that state at zero."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    assert score.duration_s == 0.0
    assert score.state_at(0.0) == system.state_vector()


def test_advancing_to_the_time_already_reached_changes_nothing() -> None:
    """Two steps' worth of bookkeeping at one instant is not an error."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(5.0)
    score.advance_to(5.0)

    assert score.duration_s == 5.0


def test_a_one_column_window_is_the_instant_asked_for() -> None:
    """`columns` of one returns `start_s` alone, with no spacing to divide by."""

    _, score, stepped = _stepped_run(steps=100)
    window = score.evaluate(4.0, 10.0, 1)

    assert window.times_s == (4.0,)
    assert len(window.states) == 1

    for compartment, want in zip(COMPARTMENT_STATES, stepped[4.0], strict=True):
        assert abs(window.states[0][compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_a_window_of_no_width_repeats_one_instant() -> None:
    """Every column of a zero-width window is the same state, not a divide by zero."""

    _, score, _ = _stepped_run(steps=100)
    window = score.evaluate(6.0, 6.0, 5)

    assert window.times_s == (6.0,) * 5
    assert set(window.states) == {score.state_at(6.0)}


def test_a_window_opening_on_a_keyframe_needs_no_propagation() -> None:
    """The state at a segment's own opening is that segment's keyframe, unaltered."""

    _, score, _ = _stepped_run(steps=600)
    window = score.evaluate(30.0, 60.0, 4)

    assert window.states[0] == score.segments[1].opening.state


def test_a_segment_too_short_to_hold_a_column_is_skipped() -> None:
    """A window whose columns straddle a whole segment still reads the right one.

    A walk that assumed one segment per column would hand the column after the
    gap the skipped segment's settings, and draw a stretch of the run under
    settings it was never computed under.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    for elapsed_s, flow in ((10.0, 1.5), (10.5, 3.0), (60.0, 5.0)):
        score.advance_to(elapsed_s)
        system.set_fresh_gas_flow(flow)
        score.record_change(system.equation_settings())

    score.advance_to(120.0)
    window = score.evaluate(0.0, 120.0, 5)

    assert len(score.segments) == 4
    assert window.times_s == (0.0, 30.0, 60.0, 90.0, 120.0)

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        canonical = score.state_at(elapsed_s)

        for compartment in COMPARTMENT_STATES:
            assert abs(state[compartment] - canonical[compartment]) < WORST_DISPLAY_DIFFERENCE


def test_a_score_refuses_a_state_of_the_wrong_length() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match=f"the equations carry {STATE_SIZE}"):
        RunScore(system.equation_settings(), (0.0, 1.0))


def test_a_score_refuses_a_non_finite_state() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[ALVEOLAR_FRACTION] = nan

    with pytest.raises(SimulationConfigurationError, match="which is not finite"):
        RunScore(system.equation_settings(), tuple(state))


def test_a_score_refuses_a_state_whose_unit_is_not_one() -> None:
    """The forcing terms are read against this entry, so it is not a free value."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[UNIT_STATE] = 0.5

    with pytest.raises(SimulationConfigurationError, match="the constant one"):
        RunScore(system.equation_settings(), tuple(state))


def test_a_run_refuses_to_go_backwards() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(20.0)

    with pytest.raises(SimulationConfigurationError, match="cannot go back"):
        score.advance_to(19.9)


def test_a_run_refuses_a_non_finite_reach() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    with pytest.raises(SimulationConfigurationError, match="not finite"):
        score.advance_to(inf)


@pytest.mark.parametrize("elapsed_s", [nan, inf])
def test_a_score_refuses_a_non_finite_instant(elapsed_s: float) -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        score.state_at(elapsed_s)


def test_a_score_has_no_state_before_the_run_began() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        score.state_at(-0.1)


def test_a_score_refuses_to_predict_past_the_run() -> None:
    """Answering past the run would return a prediction indistinguishable from it."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        score.state_at(30.1)


def test_a_window_needs_at_least_one_column() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())

    with pytest.raises(SimulationConfigurationError, match="at least one column"):
        score.evaluate(0.0, 0.0, 0)


def test_a_window_refuses_to_end_before_it_begins() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="ends before it begins"):
        score.evaluate(20.0, 10.0, 5)


def test_a_window_refuses_to_reach_past_the_run() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(30.0)

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        score.evaluate(10.0, 30.1, 5)


def test_a_sampled_window_pairs_each_state_with_one_instant() -> None:
    """Times and states of different lengths would draw a trace off its own axis."""

    with pytest.raises(SimulationConfigurationError, match="belongs to one instant"):
        SampledWindow(times_s=(0.0, 1.0), states=((0.0,) * STATE_SIZE,))


def test_a_segment_carries_the_state_its_settings_start_from() -> None:
    """The pairing `ScoreSegment` exists for, read back off a recorded run."""

    _, score, _ = _stepped_run(steps=600)
    segment = score.segments[1]

    assert isinstance(segment, ScoreSegment)
    assert isinstance(segment.opening, Keyframe)
    assert segment.opening.elapsed_s == 30.0
    assert len(segment.opening.state) == STATE_SIZE
    assert segment.opening.state[UNIT_STATE] == 1.0


def test_a_change_undone_before_a_step_runs_leaves_no_segment() -> None:
    """A dial moved and moved back between two steps describes no change at all.

    The stretch it opened is dropped rather than left standing with the
    settings it started from, which would put a keyframe in the score for an
    instant the run passed through unremarkably. The interface's own control
    timeline drops the matching entry for the same reason.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    score.advance_to(10.0)
    system.set_delivered_concentration(0.03)
    score.record_change(system.equation_settings())

    assert len(score.segments) == 2

    system.set_delivered_concentration(0.02)
    score.record_change(system.equation_settings())

    assert len(score.segments) == 1
    assert score.segments[0].opening.elapsed_s == 0.0


def test_the_first_stretch_is_kept_even_when_a_change_returns_to_it() -> None:
    """There is no earlier stretch to fold the opening one back into.

    The run's first segment opens at zero and carries the settings the run
    began under, so a change recorded at zero replaces those settings rather
    than dropping a stretch that nothing precedes.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    score = RunScore(system.equation_settings(), system.state_vector())
    system.set_delivered_concentration(0.05)
    score.record_change(system.equation_settings())

    assert len(score.segments) == 1
    assert score.segments[0].settings.delivered_concentration_fraction == pytest.approx(0.05)
