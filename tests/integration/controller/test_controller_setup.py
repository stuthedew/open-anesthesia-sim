"""The simulation controller, driven against real runs.

These tests cover its defaults, its patient, and switching agent.

`controller_support.py` holds what several of these files share.
"""

import dataclasses
import inspect
from importlib import resources
from itertools import permutations

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import PARAMETER_CONTROLS
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.run_definition import RunSegment
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from tests.integration.controller.controller_support import _advance_for


def test_default_controller_starts_with_sevoflurane() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "sevoflurane"
    assert snapshot.agent_display_name == "Sevoflurane"
    assert snapshot.max_delivered_concentration_percent == 8.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.02)


def test_default_controller_starts_each_agent_at_its_own_one_mac() -> None:
    """A freshly constructed controller starts at 1 MAC, the standard
    clinical starting point, not a fixed raw percentage.
    """

    assert SimulationController(
        agent_id="sevoflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.02)
    assert SimulationController(
        agent_id="isoflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.012)
    assert SimulationController(
        agent_id="desflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.06)


def test_explicit_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): an explicitly requested fraction above a
    vaporizer's real maximum must fail, not be silently clamped.

    Clamping produced a run in which every displayed value came from a dial
    position the caller never asked for. On screen, that run looked exactly
    like a run at a position they had asked for.
    """

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        SimulationController(agent_id="isoflurane", delivered_concentration_percent=Percent(8.0))


def test_setting_a_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): the setter path is bounded by the same guard.

    Before the fix only the UI slider bounded this value, so any non-UI
    caller could simulate 50% isoflurane on a 5% vaporizer.
    """

    controller = SimulationController(agent_id="isoflurane")

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration_percent(Percent(50.0))

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.012)


def test_delivered_concentration_exactly_at_the_agent_max_is_accepted() -> None:
    """The boundary is inclusive: 5.0% is a real isoflurane dial position."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration_percent(Percent(5.0))

    assert controller.snapshot().delivered_concentration_percent == 5.0


def test_delivered_concentration_can_be_turned_off() -> None:
    """Zero is always deliverable: it is the vaporizer off, which is how
    washout begins.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration_percent(Percent(0.0))

    assert controller.snapshot().delivered_concentration_percent == 0.0


def test_patient_defaults_come_from_the_data_file() -> None:
    """Regression (PL-017): the cited data-file defaults must reach the app.

    The controller previously hardcoded 4.0 L/min ventilation and 5.0
    L/min cardiac output, matching `reference_adult.json` by coincidence,
    so any correction to the cited values would silently not take effect.
    """

    original = uptake_system.load_reference_adult_parameters
    edited = dataclasses.replace(
        load_reference_adult_parameters(),
        default_alveolar_ventilation_l_min=5.5,
        default_cardiac_output_l_min=6.5,
    )
    uptake_system.load_reference_adult_parameters = lambda: edited

    try:
        snapshot = SimulationController().snapshot()
    finally:
        uptake_system.load_reference_adult_parameters = original

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
        alveolar_ventilation_l_min=AlveolarVentilation(3.0), cardiac_output_l_min=CardiacOutput(7.0)
    ).snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(3.0)
    assert snapshot.cardiac_output_l_min == pytest.approx(7.0)


def test_every_run_simulates_the_shipped_reference_adult() -> None:
    """Every run simulates the reference adult, because no input changes its body (`PL-DXJR`).

    `docs/MODEL.md`'s hazard row for entering an identifiable patient's data
    lists the fixed reference adult as one of its two safeguards. This test
    enforces that safeguard. A learner can set four settings and the agent, but
    nothing that would describe a particular patient: no weight, age, sex,
    height or body composition. A stretch is a `RunSegment`, a span of a run
    during which no setting changes. Every stretch of every run keeps the
    compartment volumes and perfusion fractions of
    `data/patients/reference_adult.json`, whatever the learner sets.

    The first five assertions check each way a patient could get into a run
    today. They check that the package ships one patient file, that the uptake
    system is built from an agent alone, and that the controller and its four
    controls take no patient argument. Patient factors (`ROADMAP.md`
    planned-milestone item 30) must change at least one of these facts, so this
    test fails when they are added. The failure is intended, because the same
    work must rewrite the hazard row.

    An agent change and a Reset each start a new run definition, so the test
    collects each run's stretches before the next run definition replaces them.
    """

    shipped_patients = {
        entry.name
        for entry in resources.files("anesthesia_sim.data.patients").iterdir()
        if entry.name.endswith(".json")
    }
    assert shipped_patients == {"reference_adult.json"}
    assert set(inspect.signature(uptake_system.AgentUptakeSystem.for_agent).parameters) == {
        "agent_id"
    }
    learner_controls = {
        ControlInput.FRESH_GAS_FLOW,
        ControlInput.DELIVERED,
        ControlInput.ALVEOLAR_VENTILATION,
        ControlInput.CARDIAC_OUTPUT,
    }
    assert set(ControlInput) == learner_controls
    assert {control.control for control in PARAMETER_CONTROLS} == learner_controls
    assert set(inspect.signature(SimulationController).parameters) == {
        "agent_id",
        "circuit_volume_l",
        "fresh_gas_flow_l_min",
        "delivered_concentration_percent",
        "alveolar_ventilation_l_min",
        "cardiac_output_l_min",
    }

    stretches: list[RunSegment] = []
    controller = SimulationController(agent_id="isoflurane")
    controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    controller.set_fresh_gas_flow(FreshGasFlow(1.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    controller.set_cardiac_output(CardiacOutput(3.0))
    controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    stretches.extend(controller.run_segments)
    controller.set_agent("desflurane")
    controller.set_cardiac_output(CardiacOutput(8.0))
    controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    stretches.extend(controller.run_segments)
    controller.reset()
    controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    stretches.extend(controller.run_segments)

    reference = load_reference_adult_parameters()
    expected_tissues = {
        "vessel_rich": (reference.vessel_rich_volume_l, reference.vessel_rich_perfusion_fraction),
        "muscle": (reference.muscle_volume_l, reference.muscle_perfusion_fraction),
        "fat": (reference.fat_volume_l, reference.fat_perfusion_fraction),
    }
    cardiac_outputs = {stretch.settings.cardiac_output_l_min for stretch in stretches}
    assert {3.0, 8.0} <= cardiac_outputs
    for stretch in stretches:
        settings = stretch.settings
        assert settings.alveolar_volume_l == reference.alveolar_gas_volume_l
        assert settings.venous_volume_l == reference.venous_pool_volume_l
        held = {
            tissue.name: (tissue.volume_l, tissue.blood_flow_l_min / settings.cardiac_output_l_min)
            for tissue in settings.tissues
        }
        assert held.keys() == expected_tissues.keys()
        for name, (volume_l, fraction) in expected_tissues.items():
            assert held[name][0] == volume_l
            assert held[name][1] == pytest.approx(fraction, rel=1e-12)


def test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac() -> None:
    """Switching agents must not carry over the old agent's raw percentage:
    the same percent means a different clinical depth per agent (e.g. 2%
    is 1 MAC of sevoflurane but only about a third of a MAC of desflurane).
    """

    controller = SimulationController(
        agent_id="sevoflurane", delivered_concentration_percent=Percent(8.0)
    )

    controller.set_agent("isoflurane")
    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.012)


def test_controller_can_be_constructed_for_a_different_agent() -> None:
    controller = SimulationController(agent_id="isoflurane")

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "isoflurane"
    assert snapshot.agent_display_name == "Isoflurane"


def test_set_agent_starts_fresh_preserving_flow_settings_but_not_concentration() -> None:
    """The circuit volume, fresh gas flow, ventilation and cardiac output carry over.

    The delivered concentration does not. It resets to the new agent's own
    1 MAC instead (see
    test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=CompartmentVolume(5.0),
        fresh_gas_flow_l_min=FreshGasFlow(3.0),
        delivered_concentration_percent=Percent(3.0),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.0),
    )
    controller.start()
    _advance_for(controller, duration_s=30.0)

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
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.06)
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0


_ORDERED_AGENT_PAIRS = tuple(permutations(AGENT_DATA_FILENAMES, 2))
"""Every switch a learner can make: each agent to each other agent, both ways."""


def _run_with_non_default_settings(agent_id: str) -> SimulationController:
    """A paused run of `agent_id` whose four carried-over settings are not the defaults.

    The data files give a 6.0 L circuit, 4.0 L/min of fresh gas, 4.0 L/min of
    alveolar ventilation and 5.0 L/min of cardiac output. Each value here
    differs from its default and from the other three. So a switch that drops
    a setting, or puts one setting's value in another's place, builds a run
    that differs from a fresh run with these settings.
    """

    return SimulationController(
        agent_id=agent_id,
        circuit_volume_l=CompartmentVolume(4.5),
        fresh_gas_flow_l_min=FreshGasFlow(2.5),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.5),
    )


def _switched_after_a_run_of(previous_agent_id: str, new_agent_id: str) -> SimulationController:
    """A run of `previous_agent_id` that has taken up agent, then switched to `new_agent_id`.

    Before the switch the run has taken 90 s of uptake into every compartment,
    with the dial moved to 1.5 times the previous agent's MAC at 60 s. So the
    compartments contain agent, the dial is not at its default, and the
    timeline contains a change. A switch that kept any of these would show
    the difference.
    """

    run = _run_with_non_default_settings(previous_agent_id)
    run.start()
    _advance_for(run, duration_s=60.0)
    run.set_delivered_concentration_percent(
        Percent(1.5 * load_agent_parameters(previous_agent_id).mac_percent)
    )
    _advance_for(run, duration_s=30.0)
    assert run.snapshot().stored_agent_l > 0.0

    run.set_agent(new_agent_id)

    return run


@pytest.mark.parametrize(("previous_agent_id", "new_agent_id"), _ORDERED_AGENT_PAIRS)
def test_an_agent_switch_runs_exactly_as_a_fresh_run_of_that_agent(
    previous_agent_id: str, new_agent_id: str
) -> None:
    """A switched run computes with the new agent alone (`PL-QJXS`).

    The expected run is built directly with the new agent and the same four
    settings, so the expected values do not come from the run under test.
    Every field of the snapshot is compared: the agent and its references, the
    settings, the six partial-pressure fractions, the delivered and exhausted
    amounts and the accounting. The equation settings and the opening state are
    compared before either run takes a step.

    A switch from sevoflurane to desflurane that kept sevoflurane's
    compartments passed every other test. Its run, labelled desflurane, showed
    an alveolar fraction of 2.95% (0.49 ×MAC) at 5 minutes, where a fresh
    desflurane run shows 3.59% (0.60 ×MAC).

    The comparison is exact, not within a tolerance. Both runs take the same
    steps from the same state, and the simulator is deterministic.
    """

    switched = _switched_after_a_run_of(previous_agent_id, new_agent_id)
    fresh = _run_with_non_default_settings(new_agent_id)

    assert switched.run_segments == fresh.run_segments
    assert switched.snapshot() == fresh.snapshot()

    for run in (switched, fresh):
        run.start()
        _advance_for(run, duration_s=300.0)

    assert fresh.snapshot().alveolar_partial_pressure_fraction > 0.0
    assert switched.snapshot() == fresh.snapshot()


@pytest.mark.parametrize(("previous_agent_id", "new_agent_id"), _ORDERED_AGENT_PAIRS)
def test_a_switched_run_branches_as_a_fresh_run_of_that_agent_does(
    previous_agent_id: str, new_agent_id: str
) -> None:
    """A branch of a switched run is the same as a branch of a fresh run (`PL-QJXS`).

    A branch rebuilds its agent and patient from the data files. Before it
    opens, `_branch_from` refuses a branch whose rebuilt settings differ from
    the settings of the run it comes from. So a switch that kept the previous
    agent's patient is refused here, and the error names the coefficient that
    differs. A correct switch gives the same branch that a fresh run of the
    new agent gives.
    """

    branches = []

    for run in (
        _switched_after_a_run_of(previous_agent_id, new_agent_id),
        _run_with_non_default_settings(new_agent_id),
    ):
        run.start()
        _advance_for(run, duration_s=120.0)
        run.pause()
        branch = run.resumed_at(CaseInstant(0.0))
        branch.start()
        _advance_for(branch, duration_s=60.0)
        branches.append(branch)

    switched_branch, fresh_branch = branches

    assert switched_branch.snapshot() == fresh_branch.snapshot()


def test_set_agent_rejects_unknown_agent_id() -> None:
    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError, match="unknown agent_id"):
        controller.set_agent("halothane")
