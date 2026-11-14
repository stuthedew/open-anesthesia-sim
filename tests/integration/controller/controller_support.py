"""Shared constants and helpers for the controller's integration tests in this directory.

The tests were one file, `tests/integration/test_controller.py`, until `PL-1FPR` split them by the
behaviour each checks. This module holds what more than one of the new files uses.
"""

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.control_record import ControlChange
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.blood_flow import PerfusionFraction
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow


def _advance_for(controller: SimulationController, duration_s: float) -> None:
    """Advance a running controller to `duration_s` at the largest supported step.

    The helper reaches the simulated time by taking many supported steps, not
    by asking for one large step. `MAXIMUM_SIMULATION_STEP_S` is the declared
    control-resolution tolerance, and the controller refuses a longer step.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def _with_stale_tissue_flows(controller: SimulationController, cardiac_output_l_min: float) -> None:
    """Make the tissue flows sum to `cardiac_output_l_min`, bypassing the tissues' guard.

    Each tissue's perfusion fraction is multiplied by `cardiac_output_l_min`
    divided by the patient's cardiac output. The new fraction is written
    directly, bypassing the tissue's own guard. The patient's cardiac output
    does not change. The settings record that opens the run's definition then
    rejects the tissue flows, because they no longer sum to the cardiac output.
    It rejects them at the next step and at Reset (`PL-M4M0`), and no setting
    repairs them. No guarded write can produce this record now. Every flow is
    computed from the cardiac output (`PL-HQF5`), and a fraction is written
    only once (`PL-Z0HN`). Before those changes, a tissue's `set_blood_flow`
    could produce the record, and a change of cardiac output repaired it.
    `_with_the_tissue_fractions_put_back` stands in for that repair.
    """

    patient = controller._state.uptake_system.patient
    scale = cardiac_output_l_min / patient.cardiac_output_l_min

    for tissue in patient.tissues:
        object.__setattr__(
            tissue, "perfusion_fraction", PerfusionFraction(tissue.perfusion_fraction * scale)
        )


def _with_the_tissue_fractions_put_back(controller: SimulationController) -> None:
    """Write back the reference adult's perfusion fractions, bypassing the tissues' guard.

    The fractions are typed in by hand from `data/patients/reference_adult.json`.
    Once they are back, the settings record no longer rejects the tissue flows.
    """

    for tissue, fraction in zip(
        controller._state.uptake_system.patient.tissues, (0.76, 0.18, 0.06), strict=True
    ):
        object.__setattr__(tissue, "perfusion_fraction", PerfusionFraction(fraction))


def _advance_through_halts(controller: SimulationController, duration_s: float) -> None:
    """Advance `duration_s`, resuming wherever a marked crossing halts the run.

    A marked run halts on the step that crosses one of its marks (`PL-CTD7`),
    and the halt is an ordinary pause. A driver that did not resume would
    leave a marked run stopped at its first crossing while an unmarked run
    went on. The two runs would then differ because of where the marks were,
    not because of anything the model computed. Unmarked runs never halt, so
    for a caller with no marks this helper behaves exactly like `_advance_for`.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        if not controller.is_running:
            controller.start()

        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def _run_with_two_changes(controller: SimulationController) -> None:
    """Drive 120 s through the controller, moving two controls on the way."""

    controller.start()
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    _advance_through_halts(controller, duration_s=60.0)


# `PL-J2TD`: a fork resumes into a live run. The tests below check the seam
# between a canonical keyframe state and a running system: the state a branch
# opens at, what its clock reads, and what it refuses. They work end to end
# through the controller, because only the controller holds both of the
# records that a branch must keep in agreement.

COMPARTMENT_SNAPSHOT_FIELDS = (
    "inspired_partial_pressure_fraction",
    "alveolar_partial_pressure_fraction",
    "mixed_venous_partial_pressure_fraction",
    "vessel_rich_partial_pressure_fraction",
    "muscle_partial_pressure_fraction",
    "fat_partial_pressure_fraction",
)
"""The six compartment fractions a snapshot carries, named as the snapshot names them.

The names are written out rather than derived from `COMPARTMENT_QUANTITIES`.
That tuple is keyed by the quantity the *chart* draws, and one of its names
differs from the snapshot's. The circuit's drawn quantity is `circuit`, while
the snapshot field is `inspired_partial_pressure_fraction`. The state is named
for the clinical quantity, but the container is still the circuit.
"""

BRANCH_AGREEMENT = 1e-14
"""How far a branch's live state may differ from its parent's, in fractions of 1 atm.

The two reach the same instant by different routes. The parent steps the whole
way from induction. The branch is placed at a keyframe that the canonical path
computed, and steps only from there. `docs/MODEL.md` § "Closed-form agreement
test" governs that comparison. It also gives the reason for stating the bound
in fractions of one atmosphere rather than as a relative bound. A relative
bound would tighten without limit on the near-zero fat fraction of a 120 s
run, and it would say nothing about a displayed digit.

Measured on 2026-09-14 on the run below, the worst disagreement across all six
compartments is 2.7e-16, about one unit in the last place. The two cumulative
accumulators agree to 1.6e-15 L. The bound is set two orders of magnitude
above that, so an ordinary floating-point wobble does not fail the suite. It
is also ten orders of magnitude below the 1e-4 that a two-decimal percent
readout can show, so a real divergence still fails it.
"""


def _trunk_with_two_changes() -> SimulationController:
    """A 120 s sevoflurane run with two setting changes, so it has three keyframes."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.pause()

    return controller


def _advance_until_halted(controller: SimulationController, limit_s: float) -> None:
    """Step a running controller until a mark halts it, or raise if no mark does.

    A bookmark fork is taken at the halt. A test that silently ran past the
    halt would fork at whatever instant it happened to stop at, and it would
    assert nothing about the case it was meant to test.
    """

    for _ in range(round(limit_s / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

        if controller.snapshot().bookmark_halt is not None:
            return

    raise AssertionError(f"no mark halted this run within {limit_s} s of stepping")


def _trunk_halted_on_a_bookmark() -> SimulationController:
    """A run stopped where a mark lies between two of its keyframes.

    The run has one setting change, at 30 s, so it has keyframes at 0 s and
    30 s and nowhere else. The mark is at 45.3 s, which is neither of them.
    That is the ordinary case, not a contrived one. On the 120 s run that the
    other fork tests use, 3 of the 1 201 instants a halt could land on are
    keyframes.
    """

    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _advance_until_halted(controller, limit_s=60.0)

    return controller


# --- A mark the run has passed, returned to (PL-W4XQ) -------------------------
#
# This is the act the owner described a time bookmark for: paused at 3 h, mark
# 1 h and go back to it. Neither of the other fork methods reaches it.
# `resumed_at` opens only at a keyframe, and `resumed_here` only where the run
# is stopped. So `resumed_at_mark` is a third method, built from the halt
# fork's construction. The cases scale the owner's hours down to seconds.
# Nothing in the fork depends on the scale, and the suite pays for every step
# it takes.


def _trunk_paused_past_a_change(past_s: float = 180.0) -> SimulationController:
    """The item's case at a minute's scale: a setting change at 30 s, then on to `past_s`.

    The run has keyframes at 0 s and 30 s and nowhere else. So the trunk has
    no keyframe at an instant past 30 s that a learner marks, and no step
    crossed that instant while it was marked. Both earlier fork methods refuse
    that case.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_fresh_gas_flow(FreshGasFlow(1.0))
    _advance_for(controller, duration_s=past_s - 30.0)
    controller.pause()

    return controller


# --- Edits made at a paused instant (PL-ZR49) --------------------------------
#
# When a run is paused or stopped at an instant, the step that brought it there
# ran under one stretch of settings, called the reaching stretch. After the
# case's opening, nothing can change the reaching stretch any more. A setting
# changed while the run is paused there starts a new stretch, so the stretch in
# force from that instant on can differ from the reaching stretch. Every branch
# takes its provenance from the reaching stretch. It runs under the stretch in
# force, which is what the dial shows at that instant. The branch records each
# setting that differs between the two as a change at the fork. The halt record
# lists the marks that the step ending at that instant crossed, tested against
# the marks as they are now. These tests check each way of branching against
# the rule in `docs/INTERFACE.md` § "The canonical evaluation rule".


def _described(changes: tuple[ControlChange, ...]) -> list[tuple[object, ...]]:
    """Each change as its instant, control and two values, leaving out how it was grouped."""

    return [
        (change.elapsed_s, change.control, change.previous_value, change.new_value)
        for change in changes
    ]


def _states_agree_after_the_fork(
    run: SimulationController, expected: SimulationController, fork_s: float, steps: int
) -> None:
    """Assert that two runs hold bit-identical canonical states for `steps` steps past `fork_s`."""

    fork_steps = round(fork_s / MAXIMUM_SIMULATION_STEP_S)

    for steps_past_fork in range(steps + 1):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert run._run_definition.state_at(case_s) == expected._run_definition.state_at(case_s), (
            f"the runs differ at {case_s} s"
        )
