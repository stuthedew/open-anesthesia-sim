"""The simulation controller, driven against real runs.

These tests cover branches taken from a case, and the case that holds them.

`controller_support.py` holds what several of these files share.
"""

import dataclasses

import pytest

from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.run_series import COMPARTMENT_STATE_INDEX
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.concentration import MacPercent, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.mac import mac_for_patient
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from tests.integration.controller.controller_support import (
    COMPARTMENT_SNAPSHOT_FIELDS,
    _advance_for,
    _run_with_two_changes,
    _trunk_with_two_changes,
    _with_stale_tissue_flows,
)


def test_a_fork_opens_at_a_keyframe_on_the_case_s_own_axis() -> None:
    """The item's own deliverable, in one test.

    A branch opens at a canonical keyframe state of another run. Its clock
    starts at the instant it was forked from, and its definition's instants
    are on the same axis. That is because a branch is one patient's case
    under a second management, and uptake is a function of time since
    induction. The test asserts the clock and the definition together,
    because their agreement is what `PL-ZMRT` delivered. While the definition
    opened at a zero of its own, a branch carried two time frames, and every
    reader had to know which one it was using.

    The definition opens on the trunk's stretch before the keyframe, which is
    the stretch that the step reaching the keyframe ran under. It records the
    trunk's change at the keyframe as a keyframe of its own (`PL-ZR49`).
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s

    branch = trunk.resumed_at(fork_s)

    # The branch uses the case's clock: it starts at the fork instant, not at zero.
    assert branch.snapshot().elapsed_s == fork_s

    # The definition uses the case's axis too. It opens on the stretch before
    # the fork, and its own keyframe at the fork stands where the trunk's does.
    assert branch.run_segments[0] == trunk.run_segments[-2]
    assert branch.run_segments[-1].opened_at_s == fork_s
    assert branch.run_segments[-1].settings == trunk.run_segments[-1].settings

    # And the state at the fork is the parent's keyframe, element for element.
    for entry in COMPARTMENT_STATE_INDEX.values():
        assert (
            branch._state.stored_states.state_at(branch.run_segments[-1].opened_at_s)[entry]
            == (trunk._state.stored_states.state_at(trunk.run_segments[-1].opened_at_s)[entry])
        )

    # It is a live run: it advances by the path every run takes.
    branch.start()
    _advance_for(branch, duration_s=10)

    assert branch.snapshot().elapsed_s == fork_s + 10.0

    # The opening does not move, and the reach follows the clock exactly. Since
    # `PL-ZMRT`, the reach and the clock are one quantity, not two related by
    # an offset. So asserting that they are equal asserts that no frame
    # conversion is left.
    assert branch.run_segments[0] == trunk.run_segments[-2]
    assert branch._run_definition.reached_s == branch.snapshot().elapsed_s


def test_a_branch_continues_the_case_s_step_count_so_the_envelope_is_the_case_s() -> None:
    """The 24 h supported run length belongs to the patient, not to each branch.

    `require_supported_run_length` reads a step count, so a branch that
    restarted the count would get a fresh 24 h envelope. A fork taken late
    could then be advanced well past the span that `docs/INTERFACE.md` § "Supported
    run length" declares, with every guard passing. The model is not claimed to
    represent a patient for a run that long. As `core/supported_ranges.py`
    argues, the model omits metabolism and its fat flow is uncertain, so how
    far the slow part of the trace can stray from a patient grows as a run
    goes on. When the branch
    continues the parent's count, the whole case has one envelope, and no
    second guard is needed.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s

    branch = trunk.resumed_at(fork_s)

    # The trunk's second change is at 60 s, and a step is one second. So the
    # case had completed 60 steps at the fork.
    assert fork_s == 60
    assert branch._state.step_count == 60
    assert branch.snapshot().elapsed_s == fork_s


def test_a_branch_reproduces_its_parent_at_every_instant_they_share() -> None:
    """`ROADMAP.md` item 12, element-wise rather than within a tolerance.

    The parent and the branch are both advanced past the fork in the same way.
    At every second from the fork on, the state each run stored must agree
    entry for entry. The branch holds its parent's stored states up to the
    fork and steps on from the state stored there with the same terms of its
    totals (`PL-FST0`), so nothing is left for rounding to change.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)

    trunk.start()
    _advance_for(trunk, duration_s=20)
    trunk.pause()

    branch.start()
    _advance_for(branch, duration_s=20)
    branch.pause()

    for steps_past_fork in range(0, 21):
        case_s = CaseInstant(fork_s + steps_past_fork * SIMULATION_STEP_S)

        assert branch._state.stored_states.state_at(case_s) == (
            trunk._state.stored_states.state_at(case_s)
        ), f"the branch and its parent differ at {case_s} s"


def test_a_branch_steps_to_where_its_parent_stepped() -> None:
    """The readouts agree too, in every digit.

    The parent stepped from induction to 120 s. The branch was placed at the
    state its parent stored for 60 s, with the stored terms of its totals, and
    stepped from there. At the same case instant, the two
    must describe one patient. Any comparison of two managements rests on that
    claim, because everything before the fork has to be the same history, not
    a reproduction of it.
    """

    trunk = _trunk_with_two_changes()
    at_end = trunk.snapshot()
    fork_s = trunk.run_segments[-1].opened_at_s

    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=at_end.elapsed_s - fork_s)

    resumed = branch.snapshot()

    assert resumed.elapsed_s == at_end.elapsed_s, "the two must be compared at one case instant"

    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(at_end, field) == getattr(resumed, field), (
            f"{field} diverged across the fork"
        )

    assert at_end.delivered_agent_l == resumed.delivered_agent_l
    assert at_end.exhausted_agent_l == resumed.exhausted_agent_l


def test_a_branch_s_drawn_window_is_on_the_case_s_axis() -> None:
    """The chart uses one time axis, whichever run fills it.

    `drawn_window` takes the axis the caller has set and returns the instants
    it drew. On a branch, as on a trunk, both are in the case's time. Since
    `PL-ZMRT`, there is no second time frame for either to be in. A window
    measured from the fork would draw a correct trace at the wrong place on a
    labelled axis. `CLAUDE.md`'s safety-critical standard counts that as a
    presentation failure, not as a lesser kind of error.

    The test deliberately passes a left edge earlier than the branch's fork.
    That exercises the clamp in `drawn_window`, which clips to the run's own
    opening rather than to zero. Clipping to zero would ask the definition for
    an instant before the branch existed. The definition refuses such an
    instant, so an ordinary frame on a branch would raise an error out of the
    render loop.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10)

    window = branch.drawn_window(0.0, fork_s + 10.0, 150)

    assert window.times_s[0] == fork_s, "a branch draws nothing before the fork"
    assert window.times_s[-1] == fork_s + 10.0
    assert all(time_s >= fork_s for time_s in window.times_s)


def test_a_trunk_s_drawn_window_spans_the_axis_it_was_asked_for() -> None:
    """A trunk opens at the case's zero, so the whole axis is inside its run."""

    trunk = _trunk_with_two_changes()
    snapshot = trunk.snapshot()

    window = trunk.drawn_window(0.0, snapshot.elapsed_s, 150)

    assert trunk.run_segments[0].opened_at_s == 0.0
    assert window.times_s[0] == 0.0
    assert window.times_s[-1] == snapshot.elapsed_s


def test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from() -> None:
    """One shared time frame aligns the chart's columns, so `PL-2R2C` needed no fix.

    `RunDefinition.evaluate_anchored` lays its grid on absolute multiples of
    the spacing, measured in the definition's own frame. This is deliberate. A
    grid anchored to the window instead makes every drawn point a new instant
    on every frame, and `PL-Q197` measured that as the cause of the saturated
    client. While a branch's definition opened at a zero of its own, its
    columns fell at `fork + m x spacing`, against the trunk's `m x spacing`.
    On this 13-column 120 s axis, with the fork deliberately off the grid at
    55 s, 2 of the branch's 8 columns landed where the trunk also drew. A
    user then could not read "at this instant the trunk was here and the
    branch was there" from matched points. Any difference trace or shared
    tooltip built on that assumption would be wrong, not merely coarse.

    One time frame makes the columns coincide, with nothing added to the
    display path. Both definitions are on the case's axis, so both grids use
    the same multiples. The fork instant itself is a column on the trunk
    because it is a setting change. It is the branch's first column because
    it is where the branch opens.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=55)
    trunk.set_delivered_concentration_percent(Percent(4.0))
    _advance_for(trunk, duration_s=65)
    trunk.pause()

    fork_s = trunk.run_segments[-1].opened_at_s
    stop_s = trunk.snapshot().elapsed_s
    branch = trunk.resumed_at(fork_s)

    branch.start()
    _advance_for(branch, duration_s=stop_s - fork_s)
    branch.pause()

    trunk_columns = trunk.drawn_window(0.0, stop_s, 13).times_s
    branch_columns = branch.drawn_window(0.0, stop_s, 13).times_s

    # The fork is deliberately not a multiple of the 10 s spacing. If it were,
    # the two grids would coincide whatever frame the branch was in, and the
    # test would pass without showing anything.
    assert fork_s % ((stop_s - 0.0) / 12) != 0.0

    assert set(branch_columns) <= set(trunk_columns), (
        "the branch is drawn at instants the trunk never draws, so the two "
        "traces cannot be read against each other"
    )
    assert len(branch_columns) > 2

    # The axis extends to the left of the fork. The branch's window is clipped
    # at its opening rather than refused, and it starts exactly there.
    assert branch_columns[0] == fork_s
    assert branch_columns[-1] == trunk_columns[-1]


def test_a_control_moved_before_a_branch_steps_replaces_the_stretch_at_its_fork() -> None:
    """The user's actual first act on a branch, which is to change something.

    When the run has not advanced past the open segment's own opening,
    `RunDefinition.record_change` replaces that segment's settings in place.
    It does not record a zero-length stretch that nothing was ever computed
    under. The check it makes is whether the instant the run has reached
    equals the open keyframe's instant. On a branch taken at a keyframe, both
    of those are the fork instant, because the branch records the trunk's
    change there as a keyframe of its own (`PL-ZR49`). So the behaviour is
    worth asserting rather than assuming from the code. A version that
    recorded the keyframe anywhere else would open a zero-length segment
    here, and the run would still look right.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)

    assert len(branch.run_segments) == 2

    branch.set_delivered_concentration_percent(Percent(1.0))

    assert len(branch.run_segments) == 2
    assert branch.run_segments[-1].opened_at_s == fork_s
    assert branch._state.stored_states.state_at(
        branch.run_segments[-1].opened_at_s
    ) == trunk._state.stored_states.state_at(trunk.run_segments[-1].opened_at_s)

    # And the new settings are the ones the run is then computed under.
    branch.start()
    _advance_for(branch, duration_s=10)
    branch.pause()

    assert branch.run_segments[-1].settings.delivered_concentration_percent == 1.0
    assert len(branch.run_segments) == 2


def test_a_branch_carries_the_case_s_delivered_and_exhausted_totals() -> None:
    """The litres a branch reports are the patient's, not the branch's own.

    A branch that restarted them at zero would show a mass-balance readout
    that is correct for the branch and wrong for the patient. It would do so
    at the moment a user is most likely to compare two managements by how
    much agent each used.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)

    # The expected totals come from a second run of the same case, stopped at
    # the fork. `_run_with_two_changes` makes its second change at 60 s.
    stopped_at_fork = SimulationController()
    stopped_at_fork.start()
    _advance_for(stopped_at_fork, duration_s=30)
    stopped_at_fork.set_delivered_concentration_percent(Percent(4.0))
    _advance_for(stopped_at_fork, duration_s=30)
    expected = stopped_at_fork.snapshot()

    at_fork = branch.snapshot()

    assert fork_s == expected.elapsed_s == 60
    assert at_fork.delivered_agent_l > 0.0
    assert at_fork.agent_accounting_passes_validation
    assert at_fork.delivered_agent_l == expected.delivered_agent_l
    assert at_fork.exhausted_agent_l == expected.exhausted_agent_l


def test_a_branch_opens_with_only_the_change_it_runs_under_in_its_timeline() -> None:
    """A branch records the acts its own user makes, not its parent's.

    The history before the fork belongs to the trunk and is not reproduced
    here. What a branch carries forward is the *state* that history produced.
    A branch taken at a keyframe opens with only the trunk's change at that
    keyframe, because the branch runs under it (`PL-ZR49`). A branch taken
    where the trunk stands, between keyframes, opens with none.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    at_the_keyframe = trunk.resumed_at(fork_s).snapshot()

    def described(changes: tuple[ControlChange, ...]) -> list[tuple[object, ...]]:
        return [
            (change.elapsed_s, change.control, change.previous_value, change.new_value)
            for change in changes
        ]

    at_fork = [change for change in trunk.snapshot().control_timeline if change.elapsed_s == fork_s]

    assert len(trunk.snapshot().control_timeline) > len(at_fork) == 1
    assert described(at_the_keyframe.control_timeline) == described(tuple(at_fork))
    assert at_the_keyframe.opened_with == at_the_keyframe.control_timeline

    trunk.start()
    _advance_for(trunk, duration_s=10)
    trunk.pause()

    assert trunk.resumed_here().snapshot().control_timeline == ()


def test_a_branch_inherits_its_parent_s_settings_at_the_fork() -> None:
    """The settings are read from the run definition, then checked against the rebuilt branch.

    The check is the point. A branch that assembled a system matrix its parent
    never used would diverge from its first step. The divergence would stay
    inside the tolerance that keeps the two records in agreement, and nothing
    would report it.
    """

    trunk = _trunk_with_two_changes()

    for segment in trunk.run_segments:
        branch = trunk.resumed_at(segment.opened_at_s)

        assert branch._state.uptake_system.equation_settings() == segment.settings


def test_a_settings_mismatch_names_the_setting_that_differs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression (`PL-NC62`): the refusal states what differs, never a cause.

    A branch re-reads the agent's data file when it is rebuilt. So a file
    edited between the trunk and the branch fails the settings check, even
    though the control timeline is not at fault. Whatever had differed, the
    refusal used to say that the timeline did not reproduce its own segments.
    That sent its reader to the one part that was working.
    """

    trunk = _trunk_with_two_changes()
    before = trunk.snapshot()
    on_file = load_agent_parameters(before.agent_id)
    edited = dataclasses.replace(
        on_file,
        blood_gas_partition_coefficient=PartitionCoefficient(
            on_file.blood_gas_partition_coefficient + 0.05
        ),
    )
    monkeypatch.setattr(uptake_system, "load_agent_parameters", lambda agent_id: edited)

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    assert (
        f"blood_gas_partition_coefficient is {on_file.blood_gas_partition_coefficient!r} "
        f"in this run and {edited.blood_gas_partition_coefficient!r} on the branch"
    ) in _developer_note(refusal.value)
    assert "timeline" not in str(refusal.value) + _developer_note(refusal.value)
    assert trunk.snapshot() == before


def test_a_patient_mismatch_names_the_tissue_group_it_is_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Three tissue groups share each field name, so the message names the group too."""

    trunk = _trunk_with_two_changes()
    on_file = load_reference_adult_parameters()
    edited = dataclasses.replace(
        on_file, muscle_volume_l=CompartmentVolume(on_file.muscle_volume_l + 1.0)
    )
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: edited)

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    assert (
        f"muscle volume_l is {on_file.muscle_volume_l!r} in this run and "
        f"{edited.muscle_volume_l!r} on the branch"
    ) in _developer_note(refusal.value)


def test_a_branch_rebuilt_under_another_mac_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """`PL-NC62`'s second gap: an agent reference that no equation reads is checked too.

    Every MAC multiple on screen is a concentration divided by the MAC, and a
    branch re-reads the MAC from the agent's file. A branch rebuilt under a
    different MAC would show one concentration as a different multiple from
    its parent's, while every equation setting agreed. So the settings check
    alone let it through.
    """

    trunk = _trunk_with_two_changes()
    on_file = load_agent_parameters(trunk.snapshot().agent_id)
    edited = dataclasses.replace(
        on_file, mac_at_age_40_percent=MacPercent(on_file.mac_at_age_40_percent + 0.1)
    )
    monkeypatch.setattr(
        "anesthesia_sim.app.controller.load_agent_parameters", lambda agent_id: edited
    )

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    patient = load_reference_adult_parameters()

    assert (
        f"agent_mac is {mac_for_patient(on_file, patient)!r} in this run and "
        f"{mac_for_patient(edited, patient)!r} on the branch"
    ) in _developer_note(refusal.value)


def test_a_vaporizer_maximum_edited_before_a_branch_is_named_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A vaporizer maximum edited between a trunk and its branch is named once, as one difference.

    The equation settings carry the circuit's vaporizer maximum (`PL-BBMG`).
    The controller used to keep a second copy, read from the same file, and
    compared that copy as a displayed reference. So the one edit appeared twice
    in the message that refused the branch, and sent its reader looking for a
    second edit (`PL-1MGB`).
    """

    trunk = _trunk_with_two_changes()
    on_file = load_agent_parameters(trunk.snapshot().agent_id)
    edited = dataclasses.replace(
        on_file,
        max_delivered_concentration_percent=Percent(
            on_file.max_delivered_concentration_percent + 1.0
        ),
    )
    monkeypatch.setattr(uptake_system, "load_agent_parameters", lambda agent_id: edited)
    monkeypatch.setattr(
        "anesthesia_sim.app.controller.load_agent_parameters", lambda agent_id: edited
    )

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    named = (
        f"max_delivered_concentration_percent is "
        f"{on_file.max_delivered_concentration_percent!r} in this run and "
        f"{edited.max_delivered_concentration_percent!r} on the branch"
    )

    assert _developer_note(refusal.value).count(named) == 1


def test_a_branch_can_open_at_any_keyframe_the_run_holds() -> None:
    """Every recorded setting change is a branch point, and so is the run's start.

    The branch's last keyframe is the trunk's keyframe, at the same instant,
    state and settings. The branch's first stretch is the trunk's stretch
    before that keyframe, or the trunk's opening stretch for a branch at the
    start (`PL-ZR49`).
    """

    trunk = _trunk_with_two_changes()

    for index, segment in enumerate(trunk.run_segments):
        branch = trunk.resumed_at(segment.opened_at_s)

        assert branch.run_segments[-1] == segment
        assert branch.run_segments[0] == trunk.run_segments[max(index - 1, 0)]


def test_a_branch_between_two_setting_changes_runs_under_the_settings_in_force_there() -> None:
    """A branch at 65 s runs under both of the trunk's changes, with nothing in its timeline.

    The trunk changed the delivered concentration at 30 s and the alveolar
    ventilation at 60 s. Second 65 holds no change, so the branch's timeline
    opens empty (`PL-ZR49`), and its settings are the ones the trunk left
    second 65 under. `test_controller_stored_states.py` checks the states a
    branch at any second holds and stores (`PL-FST0`).
    """

    trunk = _trunk_with_two_changes()

    branch = trunk.resumed_at(CaseInstant(65))
    snapshot = branch.snapshot()

    assert branch.began_at_s == snapshot.elapsed_s == 65
    assert snapshot.control_timeline == ()
    assert snapshot.delivered_concentration_percent == 4.0
    assert snapshot.alveolar_ventilation_l_min == 6.0
    assert branch.opened_from is not None
    assert branch.opened_from.segment.opened_at_s == 60
    assert branch.opened_from == trunk.resumed_at(CaseInstant(65)).opened_from


def test_an_instant_the_run_never_reached_is_refused() -> None:
    """A branch of a run that has not happened would be a prediction drawn as a run."""

    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError, match="no state at 12m to branch") as refusal:
        trunk.resumed_at(CaseInstant(trunk.snapshot().elapsed_s + 600))

    assert "this run has reached 2m" in str(refusal.value)


def test_a_non_finite_fork_instant_cannot_be_built() -> None:
    """This refusal is separate from the keyframe refusal, which would give the wrong reason.

    Since `PL-CN5S`, a non-finite instant is refused when the instant is
    built, so no run is ever asked to branch at one. An instant is a whole
    number of seconds, and every `float` is refused as the wrong type
    (`PL-SZ6G`). So the refusal is a `TypeError`, and it does not depend on
    the value.
    """

    with pytest.raises(TypeError, match="has type float, not int"):
        CaseInstant(float("inf"))  # type: ignore[arg-type]


@pytest.mark.parametrize("instant_s", [0, 0.0, float("inf")])
def test_a_fork_instant_not_built_as_a_case_instant_is_refused(instant_s: float) -> None:
    """The instant is refused whatever its value, before the keyframes are searched (`PL-CN5S`).

    A bare `0` or `0.0` is refused even though the trunk has a keyframe there,
    because nothing has checked it. The refusal says so. It does not say that
    the run has no keyframe there, which would be the wrong reason. `fork_at`
    forwards to this method, so it refuses the same way.
    """

    trunk = _trunk_with_two_changes()

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        trunk.resumed_at(instant_s)  # type: ignore[arg-type]


def test_a_failed_frame_refuses_every_fork_until_the_trunk_starts_over() -> None:
    """A trunk whose frame failed offers no fork point and refuses every fork (`PL-T2Q2`).

    The failed-frame record belongs to the run, as a failure does. So a reset
    clears it, and the fresh run offers its opening again. A failure alone
    does not cause a refusal: a trunk whose own step failed keeps its
    keyframes.
    """

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)
    keyframes = case.fork_points_s
    assert len(keyframes) == 3

    trunk.fail("SimulationNumericalError: a step failed", kind=FailureKind.NUMERICAL)

    assert case.fork_points_s == keyframes
    assert trunk.fork_refusal is None

    trunk.record_failed_frame("RuntimeError: this frame could not be assembled")

    assert case.fork_points_s == ()
    assert case.mark_fork_points == ()
    assert trunk.fork_refusal is not None
    assert "this frame could not be assembled" in trunk.fork_refusal

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
        case.fork_at(keyframes[0])

    trunk.reset()

    assert trunk.fork_refusal is None
    assert case.fork_points_s == (CaseInstant(0),)


def test_a_branch_of_a_branch_is_refused_rather_than_silently_flattened() -> None:
    """`PL-TFX5`'s shape: one trunk with N branches, and sub-forks deliberately excluded.

    Sub-forks multiply without bound and give little that re-branching from
    the trunk does not. That is the whole reason. The rule once also rested on
    a branch's keyframes belonging to its own definition. An instant passed to
    this method on a branch then meant something different from the same
    number passed to the trunk. `PL-ZMRT` retired that, because every run's
    instants are now the case's. `SimulationController.resumed_at` states only
    the reason that remains. A later reader removes a guard whose argument has
    stopped being true.
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at(branch.snapshot().elapsed_s)


def test_forking_leaves_the_trunk_untouched() -> None:
    """The trunk survives the fork, which is what separates branching from truncating."""

    trunk = _trunk_with_two_changes()
    before = trunk.snapshot()
    segments_before = trunk.run_segments

    trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    assert trunk.snapshot() == before
    assert trunk.run_segments == segments_before


def test_a_branch_starts_paused() -> None:
    """Opening a branch is not starting it: the user decides when it runs."""

    trunk = _trunk_with_two_changes()
    trunk.start()
    branch = trunk.resumed_at(trunk.run_segments[-1].opened_at_s)

    assert branch.is_running is False


def test_resetting_a_branch_returns_it_to_its_fork_rather_than_to_zero() -> None:
    """A branch begins at the fork, and the case's induction is not a state it has.

    Clearing to an empty system would put the patient at no agent, at a case
    time when the model says they are loaded with agent. That is a plausible
    state that never happened.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)
    at_fork = branch.snapshot()

    branch.start()
    _advance_for(branch, duration_s=10)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    branch.reset()

    after = branch.snapshot()

    # The timeline holds only what the branch reopened with at the fork: the
    # trunk's change there, and the fresh gas flow the reset kept (`PL-ZR49`).
    # The branch first opened with the trunk's change alone, and the reset
    # keeps that record, so the kept flow is a change since the opening.
    assert after.elapsed_s == fork_s
    assert after.opened_with == at_fork.control_timeline
    assert [change.elapsed_s for change in after.control_timeline] == [fork_s, fork_s]
    assert [change.control for change in after.changes_since_opening] == [
        ControlInput.FRESH_GAS_FLOW
    ]
    assert after.changes_since_opening[0].new_value == 1.0
    assert branch._state.stored_states.state_at(
        branch.run_segments[-1].opened_at_s
    ) == trunk._state.stored_states.state_at(trunk.run_segments[-1].opened_at_s)

    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(at_fork, field)


def test_a_branch_reset_the_core_refuses_leaves_the_branch_exactly_as_it_was() -> None:
    """A branch's reset reads the same record first, so a refused reset leaves the branch as it was.

    `_open_at` takes the branch back to its fork and records the settings in
    force at the fork. Before `PL-M4M0`, it read those settings itself, after
    the state had already been moved back to the fork. So a refusal left the
    branch at the fork under its old definition, with nothing recorded.
    `reset()` now reads the record before anything moves and passes it in.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opened_at_s
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    before = branch.snapshot()
    segments = branch.run_segments
    _with_stale_tissue_flows(branch, 6.0)

    with pytest.raises(
        SimulationConfigurationError, match="the venous balance returns what the tissues receive"
    ):
        branch.reset()

    after = branch.snapshot()

    assert after.is_running is True
    assert branch.has_failed is False
    assert after.elapsed_s == before.elapsed_s > fork_s
    assert after.control_timeline == before.control_timeline
    # The trunk's change the branch opened with, and the user's change at 70 s.
    assert len(after.control_timeline) == 2
    assert branch.run_segments == segments
    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(before, field)


def test_a_branch_is_the_agent_and_patient_its_parent_was() -> None:
    """`PL-TFX5`: a branch that could change either would be a second case."""

    trunk = SimulationController(agent_id="desflurane", cardiac_output_l_min=CardiacOutput(3.8))
    _run_with_two_changes(trunk)
    trunk.pause()

    branch = trunk.resumed_at(trunk.run_segments[-1].opened_at_s)
    at_fork = branch.snapshot()

    assert at_fork.agent_id == "desflurane"
    assert at_fork.cardiac_output_l_min == trunk.snapshot().cardiac_output_l_min
    assert at_fork.circuit_volume_l == trunk.snapshot().circuit_volume_l


"""`PL-TFX5`: a case is one trunk and the branches taken from it, kept flat.

`SimulationController.resumed_at` cannot enforce this clause on its own. It
makes one branch and returns it detached. So two calls produce two
controllers that each know the instant they opened at, and neither knows the
other exists. `BranchedCase` makes them one case, and it builds the flat shape
into the structure. The trunk is the only run it will fork, so a sub-fork is
not an operation it ever has to refuse.
"""


def test_a_case_forks_at_every_instant_the_trunk_offers() -> None:
    """`PL-TFX5`'s first clause: any recorded control event is a branch point.

    `fork_points_s` is the run's keyframes: its opening and every setting
    change that the model was actually stepped under. So the test asserts that
    the list agrees with the timeline, as well as that each point forks. A
    list of fork points that quietly left one out would still pass a test that
    only walked the list.
    """

    case = BranchedCase(_trunk_with_two_changes())
    timeline = case.trunk.snapshot().control_timeline

    assert case.fork_points_s == (0.0, *(change.elapsed_s for change in timeline))

    for elapsed_s in case.fork_points_s:
        branch = case.fork_at(elapsed_s)

        assert branch.run_segments[-1].opened_at_s == elapsed_s
        assert branch.snapshot().elapsed_s == elapsed_s

    assert len(case.branches) == len(case.fork_points_s)
    assert case.runs == (case.trunk, *case.branches)


def test_a_case_holds_two_branches_taken_at_one_decision_point() -> None:
    """The comparison the milestone is named for, so a fork point can be used more than once.

    Coasting against holding, from the same instant: two branches at one fork
    point are the normal case, not a duplicate to reject. Once taken, they
    must be managed separately.
    """

    case = BranchedCase(_trunk_with_two_changes())
    fork_s = case.fork_points_s[-1]

    coasting = case.fork_at(fork_s)
    holding = case.fork_at(fork_s)

    assert case.branches == (coasting, holding)
    assert coasting is not holding

    coasting.set_fresh_gas_flow(FreshGasFlow(0.5))
    holding.set_fresh_gas_flow(FreshGasFlow(6.0))

    assert coasting.snapshot().fresh_gas_flow_l_min == 0.5
    assert holding.snapshot().fresh_gas_flow_l_min == 6.0


def test_forking_a_case_repeatedly_leaves_the_trunk_where_it_was() -> None:
    """`PL-TFX5`'s third clause, against the whole of `fork_points_s`.

    The trunk's survival is what separates a comparison from an undo. The test
    checks it after every branch has been advanced and re-dialled, because a
    branch that shared a compartment with its parent would show nothing until
    something moved.
    """

    case = BranchedCase(_trunk_with_two_changes())
    before = case.trunk.snapshot()
    segments_before = case.trunk.run_segments

    for elapsed_s in case.fork_points_s:
        branch = case.fork_at(elapsed_s)
        branch.set_cardiac_output(CardiacOutput(2.5))
        branch.start()
        _advance_for(branch, duration_s=30)
        branch.pause()

    assert case.trunk.snapshot() == before
    assert case.trunk.run_segments == segments_before
    assert case.trunk.run_segments[0].opened_at_s == 0.0
    assert case.trunk.opened_from is None


def test_a_case_cannot_be_rooted_in_a_branch() -> None:
    """`PL-TFX5`'s fourth clause, as an interface that cannot express a sub-fork.

    `resumed_at` refuses a branch of a branch and keeps doing so. That is the
    guard for a caller that holds two controllers. This test covers the other
    half. A case built on a branch would offer `fork_at` over a second
    generation, so the case is refused when it is built, not at the fork.
    """

    trunk = _trunk_with_two_changes()
    branch = BranchedCase(trunk).fork_at(trunk.run_segments[-1].opened_at_s)

    with pytest.raises(SimulationConfigurationError, match="branches of branches are excluded"):
        BranchedCase(branch)


def test_a_case_keeps_a_branch_taken_between_two_setting_changes() -> None:
    """A case branches at any second its trunk has reached, and keeps the branch (`PL-FST0`)."""

    case = BranchedCase(_trunk_with_two_changes())
    between_s = (case.fork_points_s[-2] + case.fork_points_s[-1]) // 2

    assert between_s not in case.fork_points_s

    branch = case.fork_at(CaseInstant(between_s))

    assert case.branches == (branch,)
    assert branch.began_at_s == between_s


def test_a_case_refuses_a_fork_at_a_second_its_trunk_has_not_reached() -> None:
    """The refusal passes through the case unchanged rather than being softened by it."""

    case = BranchedCase(_trunk_with_two_changes())

    with pytest.raises(SimulationConfigurationError, match="no state at 2m1s to branch"):
        case.fork_at(CaseInstant(121))

    assert case.branches == ()


def test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork() -> None:
    """A branch carries its trunk's agent and patient as they were at the fork.

    This checks the last clause of `PL-TFX5` against a patient value that moves
    during the run. Cardiac output is the one patient quantity that a control
    can change. So it is the only one that tells "the branch carries its
    parent's patient" apart from "the branch rebuilds the same reference
    patient from the same data file". A run that never changes it checks the
    second claim while appearing to check the first, because a branch built
    from the value in force now would pass too. So this test changes it
    mid-run and forks *before* the change. The branch must carry the value
    the case was computed under at the fork, which is no longer the trunk's
    current value.
    """

    trunk = SimulationController(agent_id="isoflurane", cardiac_output_l_min=CardiacOutput(4.2))
    trunk.start()
    _advance_for(trunk, duration_s=30)
    trunk.set_cardiac_output(CardiacOutput(6.5))
    _advance_for(trunk, duration_s=30)
    trunk.pause()

    case = BranchedCase(trunk)
    before_s, after_s = case.fork_points_s

    assert trunk.snapshot().cardiac_output_l_min == 6.5

    at_earlier_fork = case.fork_at(before_s).snapshot()
    at_later_fork = case.fork_at(after_s).snapshot()

    assert at_earlier_fork.cardiac_output_l_min == 4.2
    assert at_later_fork.cardiac_output_l_min == 6.5

    for at_fork in (at_earlier_fork, at_later_fork):
        assert at_fork.agent_id == "isoflurane"
        assert at_fork.circuit_volume_l == trunk.snapshot().circuit_volume_l


def test_a_branch_cannot_change_its_agent_out_from_under_the_case() -> None:
    """`PL-TFX5`: a branch that could re-choose its agent is a second case.

    `set_agent` begins a new run, and `_build_state` clears `opened_from` along
    with everything else. Without this refusal, a branch would silently become
    a trunk. `reset()` would stop returning it to its fork, `resumed_at` would
    accept it, and the case it was taken from would go on listing it. The
    trunk is unaffected: changing the case's agent still starts an explicit
    new case, as it always did.
    """

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)
    branch = case.fork_at(case.fork_points_s[-1])

    with pytest.raises(SimulationConfigurationError, match="carries the agent of the case"):
        branch.set_agent("desflurane")

    assert branch.snapshot().agent_id == trunk.snapshot().agent_id
    assert branch.opened_from is not None

    trunk.set_agent("desflurane")

    assert trunk.snapshot().agent_id == "desflurane"


def test_every_recorded_control_event_is_an_instant_the_run_can_be_forked_at() -> None:
    """`PL-TFX5`'s first clause, against the case that used to break it.

    The clause "A run can be forked at any recorded control event" ties two
    records together. They collapse redundant changes by different rules, so
    the clause is true only while those rules agree.
    `RunDefinition.record_change` compares the whole settings against the
    previous stretch, and its result does not depend on order. The control
    timeline compares one entry, and it used to compare only the newest one.

    What separated the two records was two dials nudged and both put back in
    **interleaved** order: F up, C up, F back, C back. Each move's predecessor
    was the other control, so no collapse happened. Four entries remained at
    an instant at which the run never changed, while the definition correctly
    had no keyframe there. The nested order collapsed to nothing. So the
    defect depended on order, and a test that moved two controls once each
    could not see it. A user meets it while paused, when `advance()` does
    nothing and every control they touch carries the same instant.

    The test asserts the property rather than the repair. Every time stamp the
    reader is shown is an instant at which the run has a keyframe, and
    `resumed_at` accepts each one.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=30)

    opening = trunk.snapshot()
    trunk.pause()

    trunk.set_fresh_gas_flow(FreshGasFlow(opening.fresh_gas_flow_l_min + 1.0))
    trunk.set_cardiac_output(CardiacOutput(opening.cardiac_output_l_min + 1.0))
    trunk.set_fresh_gas_flow(opening.fresh_gas_flow_l_min)
    trunk.set_cardiac_output(opening.cardiac_output_l_min)

    timeline = trunk.snapshot().control_timeline
    openings = [segment.opened_at_s for segment in trunk.run_segments]

    # Nothing the model saw has changed, so neither record shows a change.
    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings == [0.0]

    # Now the general property, on a run that does change. Every time stamp a
    # reader is shown is a fork point, which is what the clause promises.
    trunk.start()
    _advance_for(trunk, duration_s=30)
    trunk.set_alveolar_ventilation(AlveolarVentilation(6.0))
    _advance_for(trunk, duration_s=30)
    trunk.pause()

    case = BranchedCase(trunk)

    for change in trunk.snapshot().control_timeline:
        assert change.elapsed_s in case.fork_points_s
        assert case.fork_at(change.elapsed_s).run_segments[-1].opened_at_s == (change.elapsed_s)


def test_a_branch_opened_with_no_entries_numbers_adjustments_as_a_new_trunk_does() -> None:
    """A branch that opens with no entries numbers its first adjustment as a new trunk does.

    An adjustment number groups the timeline entries that one act produced. A
    branch numbers the parent's changes at its fork first, and the user's
    adjustments after them, so that no later entry can share an opened
    entry's number. A branch taken where its trunk is paused between two
    changes opens with no entries. Its user's adjustments are then the
    first on the branch, so they are numbered from 1, as on a new trunk.

    The expected numbers come from a new trunk given the same two
    adjustments (rule 2 of `.claude/rules/test-oracles.md`).
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=30)
    trunk.pause()
    branch = trunk.resumed_here()

    fresh = SimulationController()

    for run in (branch, fresh):
        run.set_fresh_gas_flow(FreshGasFlow(1.0))
        run.set_cardiac_output(CardiacOutput(4.0))

    assert branch.snapshot().opened_with == ()
    assert [change.adjustment for change in branch.snapshot().control_timeline] == [
        change.adjustment for change in fresh.snapshot().control_timeline
    ]


def _developer_note(refusal: BaseException) -> str:
    """Return the notes that a refused branch carries for a developer (`PL-72X2`)."""

    return "\n".join(getattr(refusal, "__notes__", ()))
