"""The control-input timeline, applied again to a fresh run, reproduces the run it records.

`docs/MODEL.md` § "The control-input timeline" rests the chart marks and the
change list on one claim: "Given the recorded settings at the recorded times,
a fresh run must reproduce the run that the timeline describes." A setting
that reached the model by a path that does not record it would change the
curves with no mark on the chart, and every test of the timeline's separate
properties would still pass (`PL-FCYQ`).

The test drives a `SimulationController` through a case that changes all four
controls, and records the full state vector after every step. It then builds
the fresh run from the core alone, as `.claude/rules/test-oracles.md` rule 2
asks: an `AgentUptakeSystem` for the same agent, with no object taken from the
controller. Each recorded change is applied at its recorded instant through the
core's own setter, and the two runs' states are compared element for element
at every step. The arithmetic is the same on both sides, so the comparison is
exact.
"""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

_AGENT_ID = "sevoflurane"
_STEP = SimulationStep(MAXIMUM_SIMULATION_STEP_S)

#: How each control is applied to the core, from the value the timeline holds.
_CORE_SETTERS: dict[ControlInput, Callable[[AgentUptakeSystem, float], None]] = {
    ControlInput.FRESH_GAS_FLOW: lambda system, value: system.set_fresh_gas_flow(
        FreshGasFlow(value)
    ),
    ControlInput.DELIVERED: lambda system, value: system.set_delivered_concentration_percent(
        Percent(value)
    ),
    ControlInput.ALVEOLAR_VENTILATION: lambda system, value: system.set_alveolar_ventilation(
        AlveolarVentilation(value)
    ),
    ControlInput.CARDIAC_OUTPUT: lambda system, value: system.set_cardiac_output(
        CardiacOutput(value)
    ),
}


def _state(controller: SimulationController) -> tuple[float, ...]:
    return controller._state.uptake_system.state_vector()


def _advance(controller: SimulationController, steps: int, states: list[tuple[float, ...]]) -> None:
    """Take `steps` steps, and record the state after each one."""

    for _ in range(steps):
        controller.advance(_STEP)
        states.append(_state(controller))


def _a_case_that_changes_every_control() -> tuple[
    tuple[ControlChange, ...], list[tuple[float, ...]], int
]:
    """Run a case through the controller, and return its timeline and its state after each step.

    The case holds each kind of input that the timeline treats differently:

    - a setting made before Start, at 0 s;
    - a drag of the fresh gas flow over five steps, one setting per step, as a
      held key gives;
    - a dial moved twice inside one step, which the model sees as one change;
    - a dial moved and moved back inside one step, which the model never sees;
    - a setting the core refuses, which never takes effect;
    - a change to each of the other two controls.

    Returns:
        The control timeline, the state after each step, and the number of steps.
    """

    controller = SimulationController(_AGENT_ID)
    states: list[tuple[float, ...]] = []

    controller.set_delivered_concentration_percent(Percent(6.0))
    controller.start()
    _advance(controller, 300, states)

    controller.begin_control_adjustment()

    for fresh_gas_flow_l_min in (5.0, 4.0, 3.0, 2.0, 1.0):
        controller.set_fresh_gas_flow(FreshGasFlow(fresh_gas_flow_l_min))
        _advance(controller, 1, states)

    _advance(controller, 300, states)
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.set_cardiac_output(CardiacOutput(2.5))
    controller.set_cardiac_output(CardiacOutput(5.0))
    _advance(controller, 300, states)

    # The sevoflurane vaporizer's maximum is 8%, so the core refuses 9%.
    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration_percent(Percent(9.0))

    controller.set_alveolar_ventilation(AlveolarVentilation(8.0))
    _advance(controller, 300, states)
    controller.set_cardiac_output(CardiacOutput(3.0))
    _advance(controller, 300, states)

    return controller.record().control_timeline, states, len(states)


def _replayed(timeline: tuple[ControlChange, ...], steps: int) -> list[tuple[float, ...]]:
    """Build a fresh run from the core, apply each change at its instant, and step it.

    The instant before each step is the steps taken times the step, which is
    how a run's clock is defined (`SimulationState.elapsed_s`).
    """

    system = AgentUptakeSystem.for_agent(_AGENT_ID)
    pending = list(timeline)
    states: list[tuple[float, ...]] = []

    for steps_taken in range(steps):
        while pending and pending[0].elapsed_s == steps_taken * MAXIMUM_SIMULATION_STEP_S:
            change = pending.pop(0)
            _CORE_SETTERS[change.control](system, change.new_value)

        system.advance(_STEP)
        states.append(system.state_vector())

    assert pending == [], "every recorded change falls inside the run"

    return states


def test_the_recorded_timeline_reproduces_the_run_step_for_step() -> None:
    """Applying the timeline to a fresh run gives the same state after every step."""

    timeline, states, steps = _a_case_that_changes_every_control()

    assert {change.control for change in timeline} == set(ControlInput)
    assert _replayed(timeline, steps) == states


def test_the_replay_detects_a_setting_that_the_timeline_left_out() -> None:
    """The comparison above fails when one recorded change is missing.

    This shows that the case's changes act on the states, so a setting applied
    without a record would make the two runs differ.
    """

    timeline, states, steps = _a_case_that_changes_every_control()

    for left_out in range(len(timeline)):
        partial = timeline[:left_out] + timeline[left_out + 1 :]

        assert _replayed(partial, steps) != states, timeline[left_out]
