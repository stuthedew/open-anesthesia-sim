import dataclasses

import pytest

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core import respiratory_system
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationExecutionError,
)
from anesthesia_sim.core.parameters import load_reference_adult_parameters


def test_default_controller_starts_with_sevoflurane() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "sevoflurane"
    assert snapshot.agent_display_name == "Sevoflurane"
    assert snapshot.max_delivered_concentration_percent == 8.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.02)


def test_default_controller_starts_each_agent_at_its_own_one_mac() -> None:
    """A freshly constructed controller starts at 1 MAC, the standard
    clinical starting point, not a fixed raw percentage.
    """

    assert SimulationController(
        agent_id="sevoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.02)
    assert SimulationController(
        agent_id="isoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.012)
    assert SimulationController(
        agent_id="desflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.06)


def test_explicit_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): an explicitly requested fraction above a
    vaporizer's real maximum must fail, not be silently clamped.

    Clamping produced a run whose every displayed value came from a dial
    position the caller never asked for, which is indistinguishable on
    screen from one they did.
    """

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        SimulationController(
            agent_id="isoflurane",
            delivered_concentration_fraction=0.08,
        )


def test_setting_a_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): the setter path is bounded by the same guard.

    Before the fix only the UI slider bounded this value, so any non-UI
    caller could simulate 50% isoflurane on a 5% vaporizer.
    """

    controller = SimulationController(agent_id="isoflurane")

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration(0.50)

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.012)


def test_delivered_concentration_exactly_at_the_agent_max_is_accepted() -> None:
    """The boundary is inclusive: 5.0% is a real isoflurane dial position."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration(0.05)

    assert controller.snapshot().delivered_concentration_fraction == pytest.approx(0.05)


def test_delivered_concentration_can_be_turned_off() -> None:
    """Zero is always deliverable: it is the vaporizer off, which is how
    washout begins.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration(0.0)

    assert controller.snapshot().delivered_concentration_fraction == 0.0


def test_patient_defaults_come_from_the_data_file() -> None:
    """Regression (PL-017): the cited data-file defaults must reach the app.

    The controller previously hardcoded 4.0 L/min ventilation and 5.0
    L/min cardiac output, matching `reference_adult.json` by coincidence,
    so any correction to the cited values would silently not take effect.
    """

    original = respiratory_system.load_reference_adult_parameters
    edited = dataclasses.replace(
        load_reference_adult_parameters(),
        default_alveolar_ventilation_l_min=5.5,
        default_cardiac_output_l_min=6.5,
    )
    respiratory_system.load_reference_adult_parameters = lambda: edited

    try:
        snapshot = SimulationController().snapshot()
    finally:
        respiratory_system.load_reference_adult_parameters = original

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(5.5)
    assert snapshot.cardiac_output_l_min == pytest.approx(6.5)


def test_patient_defaults_are_the_shipped_cited_values() -> None:
    """The app runs exactly what `reference_adult.json` declares."""

    patient_parameters = load_reference_adult_parameters()
    snapshot = SimulationController().snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(
        patient_parameters.default_alveolar_ventilation_l_min
    )
    assert snapshot.cardiac_output_l_min == pytest.approx(
        patient_parameters.default_cardiac_output_l_min
    )


def test_explicit_patient_settings_still_override_the_data_file() -> None:
    """The constructor arguments remain explicit overrides."""

    snapshot = SimulationController(
        alveolar_ventilation_l_min=3.0,
        cardiac_output_l_min=7.0,
    ).snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(3.0)
    assert snapshot.cardiac_output_l_min == pytest.approx(7.0)


def test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac() -> None:
    """Switching agents must not carry over the old agent's raw percentage:
    the same percent means a different clinical depth per agent (e.g. 2%
    is 1 MAC of sevoflurane but only about a third of a MAC of desflurane).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        delivered_concentration_fraction=0.08,
    )

    controller.set_agent("isoflurane")
    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.012)


def test_controller_can_be_constructed_for_a_different_agent() -> None:
    controller = SimulationController(agent_id="isoflurane")

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "isoflurane"
    assert snapshot.agent_display_name == "Isoflurane"


def test_set_agent_starts_fresh_preserving_flow_settings_but_not_concentration() -> None:
    """Circuit, flow, ventilation, and cardiac output carry over; the
    delivered concentration resets to the new agent's own 1 MAC instead
    (see test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_concentration_fraction=0.03,
        alveolar_ventilation_l_min=5.5,
        cardiac_output_l_min=6.0,
    )
    controller.start()
    controller.advance(30.0)

    assert controller.snapshot().stored_agent_l > 0.0

    controller.set_agent("desflurane")
    snapshot = controller.snapshot()

    assert snapshot.agent_id == "desflurane"
    assert snapshot.agent_display_name == "Desflurane"
    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.stored_agent_l == 0.0
    assert snapshot.agent_accounting_passes_validation is True

    assert snapshot.circuit_volume_l == 5.0
    assert snapshot.fresh_gas_flow_l_min == 3.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.06)
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0


def test_set_agent_rejects_unknown_agent_id() -> None:
    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError, match="unknown agent_id"):
        controller.set_agent("halothane")


def test_pause_blocks_advancement() -> None:
    controller = SimulationController()

    controller.advance(0.1)

    assert controller.snapshot().elapsed_s == 0.0


def test_start_advance_pause_sequence_is_deterministic() -> None:
    first = SimulationController()
    second = SimulationController()

    for controller in (first, second):
        controller.start()
        controller.advance(0.1)
        controller.advance(0.1)
        controller.pause()

    assert first.snapshot() == second.snapshot()


def test_reset_pauses_and_clears_concentration_history() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.circuit_concentration_fraction == 0.0
    assert snapshot.alveolar_concentration_fraction == 0.0
    assert snapshot.stored_agent_l == 0.0
    assert len(snapshot.concentration_history) == 1
    assert snapshot.concentration_history[0].elapsed_s == 0.0


def test_parameter_changes_do_not_reset_dynamic_state() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(10.0)
    before = controller.snapshot()

    controller.set_circuit_volume(5.0)
    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_concentration(0.06)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.circuit_volume_l == 5.0
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_concentration_fraction == 0.06


def test_a_failed_session_is_not_the_same_state_as_a_pause() -> None:
    """`is_running` alone cannot carry the difference, so the reason does.

    A pause and a failure both stop the run, but only one of them leaves
    state a reader can trust. The snapshot has to say which it is.
    """

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    paused = SimulationController()
    paused.start()
    paused.advance(0.1)
    paused.pause()

    controller.fail("SimulationNumericalError: the step could not be completed")

    assert controller.snapshot().is_running is False
    assert controller.has_failed is True
    assert controller.snapshot().failure_reason == (
        "SimulationNumericalError: the step could not be completed"
    )

    assert paused.snapshot().is_running is False
    assert paused.has_failed is False
    assert paused.snapshot().failure_reason is None


def test_a_failed_session_cannot_be_resumed() -> None:
    """Resuming would extend a run from a step that never completed."""

    controller = SimulationController()
    controller.start()
    controller.fail("SimulationNumericalError: boom")

    with pytest.raises(SimulationExecutionError, match="cannot resume a failed simulation"):
        controller.start()

    assert controller.snapshot().is_running is False


def test_a_failed_session_does_not_advance() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
    controller.fail("SimulationNumericalError: boom")
    elapsed_at_failure = controller.snapshot().elapsed_s

    controller.advance(0.1)

    assert controller.snapshot().elapsed_s == elapsed_at_failure


def test_the_first_failure_reason_is_the_one_kept() -> None:
    """A later raise reacting to the same broken state must not mask it."""

    controller = SimulationController()
    controller.start()
    controller.fail("SimulationNumericalError: the step could not be completed")
    controller.fail("AttributeError: NoneType has no attribute 'value'")

    assert controller.snapshot().failure_reason == (
        "SimulationNumericalError: the step could not be completed"
    )


def test_reset_clears_a_failure_and_restores_a_startable_session() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
    controller.fail("SimulationNumericalError: boom")

    controller.reset()

    assert controller.has_failed is False
    assert controller.snapshot().failure_reason is None
    assert controller.snapshot().elapsed_s == 0.0

    controller.start()
    controller.advance(0.1)

    assert controller.snapshot().is_running is True
    assert controller.snapshot().elapsed_s == pytest.approx(0.1)


def test_switching_agent_clears_a_failure() -> None:
    """Switching agents begins a new run, so nothing survives the old one."""

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
    controller.fail("SimulationNumericalError: boom")

    controller.set_agent("desflurane")

    assert controller.has_failed is False
    assert controller.snapshot().failure_reason is None
    assert controller.snapshot().agent_id == "desflurane"

    controller.start()

    assert controller.snapshot().is_running is True


def test_a_refused_setting_does_not_fail_the_session() -> None:
    """A rejected value changes nothing, so the run stays trustworthy."""

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    controller.advance(0.1)
    before = controller.snapshot()

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration(0.50)

    after = controller.snapshot()

    assert after.failure_reason is None
    assert after.is_running is True
    assert after.delivered_concentration_fraction == before.delivered_concentration_fraction
