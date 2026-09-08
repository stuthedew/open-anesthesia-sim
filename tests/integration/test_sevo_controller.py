from collections.abc import Iterable
from itertools import cycle
from math import isfinite

import pytest

from anesthesia_sim.app.controller import RecordedQuantity, RecordedSeries, SimulationController
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
)

#: The step this suite drives the controller at, matching the shipped
#: `app/simulation_view.SIMULATION_STEP_S`. Restated rather than imported:
#: that module needs Flet, and `tests/unit/test_simulation_view.py` is what
#: holds the interface to the core's supported step.
SIMULATION_STEP_S = 0.1


def _advance_for(
    controller: SimulationController, duration_s: float, simulation_step_s: float = 0.1
) -> None:
    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        controller.advance(simulation_step_s)


def test_snapshot_exposes_patient_and_agent_accounting_state() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.alveolar_ventilation_l_min == 4.0
    assert snapshot.cardiac_output_l_min == 5.0
    assert snapshot.alveolar_concentration_fraction == 0.0
    assert snapshot.mixed_venous_concentration_fraction == 0.0
    assert snapshot.vessel_rich_partial_pressure_fraction == 0.0
    assert snapshot.muscle_partial_pressure_fraction == 0.0
    assert snapshot.fat_partial_pressure_fraction == 0.0
    assert snapshot.agent_accounting_passes_validation is True


def test_running_controller_advances_patient_and_named_history() -> None:
    controller = SimulationController()
    controller.start()

    _advance_for(controller, duration_s=60.0)

    snapshot = controller.snapshot()
    drawn = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)

    assert snapshot.circuit_concentration_fraction > 0.0
    assert snapshot.alveolar_concentration_fraction > 0.0
    assert snapshot.vessel_rich_partial_pressure_fraction > 0.0
    assert snapshot.stored_agent_l > 0.0
    assert snapshot.delivered_agent_l > 0.0
    assert snapshot.agent_accounting_passes_validation is True

    # The trace's right-hand end is the instant the readouts show. Both
    # bounds of a drawn window are always columns, so this holds by
    # construction rather than by the two reads being ordered.
    assert drawn.times_s[-1] == pytest.approx(snapshot.elapsed_s)
    assert drawn.compartment_fractions(
        RecordedSeries(snapshot.agent_id, RecordedQuantity.ALVEOLAR)
    )[-1] == pytest.approx(snapshot.alveolar_concentration_fraction)


def test_ventilation_and_cardiac_output_changes_preserve_state() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30.0)
    before = controller.snapshot()

    controller.set_alveolar_ventilation(7.0)
    controller.set_cardiac_output(6.5)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.alveolar_concentration_fraction == pytest.approx(
        before.alveolar_concentration_fraction
    )
    assert after.alveolar_ventilation_l_min == 7.0
    assert after.cardiac_output_l_min == 6.5
    assert after.agent_accounting_passes_validation is True


def test_reset_preserves_all_user_settings() -> None:
    controller = SimulationController(
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_concentration_fraction=0.06,
        alveolar_ventilation_l_min=5.5,
        cardiac_output_l_min=6.0,
    )
    controller.start()
    _advance_for(controller, duration_s=30.0)

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.stored_agent_l == 0.0

    assert snapshot.circuit_volume_l == 5.0
    assert snapshot.fresh_gas_flow_l_min == 3.0
    assert snapshot.delivered_concentration_fraction == 0.06
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0
    assert snapshot.agent_accounting_passes_validation is True


def test_identical_runs_produce_identical_snapshots_and_history() -> None:
    """Two runs with identical settings, events, and steps must match.

    Required test from docs/MODEL.md: deterministic replay across the full
    patient system, not just the v0.0.2 circuit-only path.
    """

    def _run() -> SimulationController:
        controller = SimulationController()
        controller.start()
        _advance_for(controller, duration_s=20.0)
        controller.set_alveolar_ventilation(6.0)
        controller.set_cardiac_output(4.5)
        _advance_for(controller, duration_s=20.0)
        controller.set_delivered_concentration(0.05)
        _advance_for(controller, duration_s=20.0)
        return controller

    first = _run()
    second = _run()

    assert first.snapshot() == second.snapshot()


def _scripted_run(
    bursts: Iterable[int], simulation_step_s: float = SIMULATION_STEP_S
) -> SimulationController:
    """One scripted run, its steps grouped into ticks of the given sizes.

    The script changes a setting at fixed *step counts*, never at a burst
    boundary, so two runs given different burst patterns differ in nothing
    but how the steps were grouped and how often the interface read the run
    between them - which is the difference between a fast host and a slow
    one.
    """

    controller = SimulationController()
    controller.start()
    steps_taken = 0

    for burst in bursts:
        for _ in range(burst):
            controller.advance(simulation_step_s)
            steps_taken += 1

            if steps_taken == 100:
                controller.set_alveolar_ventilation(6.0)
            elif steps_taken == 250:
                controller.set_cardiac_output(4.5)
            elif steps_taken == 400:
                controller.set_delivered_concentration(0.05)

        # What a frame does between ticks: read the run, and never move it.
        controller.drawn_window(
            controller.snapshot().elapsed_s - 60.0, controller.snapshot().elapsed_s, 150
        )

    return controller


def _ragged_bursts(total_steps: int) -> list[int]:
    """Steps per tick for a host that wakes the loop irregularly."""

    bursts: list[int] = []
    remaining = total_steps

    for size in cycle((7, 1, 13, 2, 5)):
        if remaining <= size:
            bursts.append(remaining)
            break

        bursts.append(size)
        remaining -= size

    return bursts


def test_a_run_records_the_same_history_however_the_ticks_fell() -> None:
    """Identical inputs must reproduce element-wise, whatever the host did.

    Required test from docs/MODEL.md, and the half the test above does not
    reach: that one drives both runs identically, so it holds the model to
    the same trajectory twice and says nothing about the machine. Simulated
    time is the number of steps taken times the step, and the run loop takes
    a fixed number of steps per tick and never extra ones to make up lost
    wall-clock time, so a host that wakes the loop late or drops a frame
    runs *slower* than one that does not - it does not run *differently*.

    The same 600 steps and the same settings at the same step counts, taken
    one per tick and in ragged bursts. Compared sample by sample rather than
    endpoint against endpoint, because that is the comparison a forked run
    makes against the run it forked from: a divergence anywhere in the
    recorded history is one a chart drawn from it would show.
    """

    steps = 600

    one_step_per_tick = _scripted_run([1] * steps)
    ragged = _scripted_run(_ragged_bursts(steps))

    # The score *is* the run now, so identity is compared there: the
    # settings each stretch was computed under and the keyframe opening it,
    # element for element and bit for bit, which the canonical evaluation
    # rule guarantees is reproducible rather than merely close.
    assert one_step_per_tick.score_segments == ragged.score_segments
    assert one_step_per_tick.snapshot() == ragged.snapshot()


def test_the_recorded_history_is_identical_at_every_playback_rate() -> None:
    """`PL-SN2C`: playing a run faster must not change the run.

    The playback multiplier is how many steps a tick takes and nothing
    else - the step stays 0.1 s at every rate - so a case played at 300x is
    the same steps in the same order as one played at real time, grouped
    differently. That makes it exactly the burst pattern the test above
    generalises, driven here through the *shipped* rates rather than
    invented burst sizes, so a rate added to the ladder is covered by this
    test on the day it is added.

    Element for element, and against the snapshot too: two learners
    comparing the same case at different speeds have to be comparing the
    same arithmetic, and a divergence anywhere in the recorded history is
    one the chart drawn from it would show.
    """

    steps = 600
    real_time = _scripted_run([1] * steps)
    reference = real_time.score_segments

    for rate in SUPPORTED_PLAYBACK_RATES:
        steps_per_tick = rate.steps_per_tick(
            tick_interval_s=SIMULATION_STEP_S, simulation_step_s=SIMULATION_STEP_S
        )
        whole_ticks, remainder = divmod(steps, steps_per_tick)
        bursts = [steps_per_tick] * whole_ticks + ([remainder] if remainder else [])

        played = _scripted_run(bursts)

        assert sum(bursts) == steps
        assert played.score_segments == reference, f"playing at {rate.multiplier}x changed the run"
        assert played.snapshot() == real_time.snapshot()


def test_extreme_ui_slider_range_stays_valid_through_wash_in_and_washout() -> None:
    """The full UI-allowed parameter range must remain safe, not just defaults.

    Reference and invariant tests elsewhere in this suite mostly exercise
    values near the physiologic defaults (~4-8 L/min). This drives every
    setting to the maximum the model supports, which is also the maximum the
    sliders offer: a run at the corner of the settings envelope is a run a
    user can ask for.
    """

    controller = SimulationController()
    controller.start()
    max_delivered_concentration_percent = controller.snapshot().max_delivered_concentration_percent
    controller.set_fresh_gas_flow(MAXIMUM_FRESH_GAS_FLOW_L_MIN)
    controller.set_delivered_concentration(max_delivered_concentration_percent / 100.0)
    controller.set_alveolar_ventilation(MAXIMUM_ALVEOLAR_VENTILATION_L_MIN)
    controller.set_cardiac_output(MAXIMUM_CARDIAC_OUTPUT_L_MIN)

    _advance_for(controller, duration_s=300.0)

    wash_in_snapshot = controller.snapshot()

    assert wash_in_snapshot.agent_accounting_passes_validation is True
    for fraction in (
        wash_in_snapshot.circuit_concentration_fraction,
        wash_in_snapshot.alveolar_concentration_fraction,
        wash_in_snapshot.mixed_venous_concentration_fraction,
        wash_in_snapshot.vessel_rich_partial_pressure_fraction,
        wash_in_snapshot.muscle_partial_pressure_fraction,
        wash_in_snapshot.fat_partial_pressure_fraction,
    ):
        assert isfinite(fraction)
        assert 0.0 <= fraction <= 1.0

    controller.set_delivered_concentration(0.0)
    _advance_for(controller, duration_s=300.0)

    washout_snapshot = controller.snapshot()

    assert washout_snapshot.agent_accounting_passes_validation is True
    assert washout_snapshot.circuit_concentration_fraction < (
        wash_in_snapshot.circuit_concentration_fraction
    )
    for fraction in (
        washout_snapshot.circuit_concentration_fraction,
        washout_snapshot.alveolar_concentration_fraction,
        washout_snapshot.mixed_venous_concentration_fraction,
        washout_snapshot.vessel_rich_partial_pressure_fraction,
        washout_snapshot.muscle_partial_pressure_fraction,
        washout_snapshot.fat_partial_pressure_fraction,
    ):
        assert isfinite(fraction)
        assert 0.0 <= fraction <= 1.0
