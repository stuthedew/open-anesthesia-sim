"""Tests for the compartment schematic's readings: each container's fill and its labels.

`docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
share bar assert" is the specification (`PL-2881`). The expected values come
from a closed form, not from the snapshot under test. With no alveolar
ventilation, nothing leaves the circuit for the patient. The circuit then
fills from the fresh gas alone, so its fraction is F_D(1 - exp(-t FGF / V))
and its amount is V times that fraction (`PL-KFTM`'s oracle). The chart's
axis top is 3 MAC of the running agent, and sevoflurane's MAC is read from its
data file, apart from the code under test.
"""

from math import exp

import pytest

from anesthesia_sim.app.compartment_schematic import container_readings
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import readouts
from anesthesia_sim.app.playback import DEFAULT_PLAYBACK_RATE
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, FreshGasFlow

STEP_S = 0.1
FRESH_GAS_FLOW_L_MIN = 8.0
SECONDS_PER_MINUTE = 60.0
SEVOFLURANE_MAC_PERCENT = load_agent_parameters("sevoflurane").mac_percent
# The concentration chart's axis is 3 MAC of the running agent for every agent
# (`docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
# share bar assert").
AXIS_TOP_PERCENT = 3 * SEVOFLURANE_MAC_PERCENT


def _run_with_no_ventilation(dial_percent: float, seconds: float) -> SimulationController:
    """Run sevoflurane with no alveolar ventilation, so only the circuit fills."""

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_fresh_gas_flow(FreshGasFlow(FRESH_GAS_FLOW_L_MIN))
    controller.set_delivered_concentration_percent(Percent(dial_percent))
    controller.start()

    for _ in range(round(seconds / STEP_S)):
        controller.advance(SimulationStep(STEP_S))

    return controller


def _circuit_percent(dial_percent: float, seconds: float, volume_l: float) -> float:
    """The closed-form circuit concentration, in percent, with no uptake by the patient."""

    return dial_percent * (
        1.0 - exp(-seconds * FRESH_GAS_FLOW_L_MIN / SECONDS_PER_MINUTE / volume_l)
    )


def test_the_containers_are_the_readout_panels_in_the_readout_row_s_order() -> None:
    readings = container_readings(SimulationController(agent_id="sevoflurane").snapshot())

    assert [reading.quantity for reading in readings] == list(COMPARTMENT_QUANTITIES)
    assert [reading.name for reading in readings] == [
        "Circuit",
        "Alveolar",
        "Mixed venous",
        "Vessel-rich group",
        "Muscle",
        "Fat",
    ]


def test_a_run_that_has_not_started_fills_no_container_and_holds_no_agent() -> None:
    for reading in container_readings(SimulationController(agent_id="sevoflurane").snapshot()):
        assert reading.fill == 0.0
        assert not reading.off_scale
        assert reading.tension == "0.00%"
        assert reading.amount == "0 mL vapour"


def test_the_circuit_fills_to_its_closed_form_tension_on_the_chart_s_scale() -> None:
    """At a 4% dial for 30 s, the circuit is about 2.0%, a third of the 6% axis."""

    seconds = 30.0
    snapshot = _run_with_no_ventilation(4.0, seconds).snapshot()
    volume_l = float(snapshot.circuit_volume_l)
    percent = _circuit_percent(4.0, seconds, volume_l)
    millilitres = volume_l * percent / 100.0 * 1000.0
    circuit = container_readings(snapshot)[0]

    assert 100.0 <= millilitres < 1000.0
    assert circuit.quantity is RecordedQuantity.CIRCUIT
    assert circuit.fill == pytest.approx(percent / AXIS_TOP_PERCENT, rel=1e-6)
    assert not circuit.off_scale
    assert circuit.tension == f"{percent:.2f}%"
    assert circuit.amount == f"{round(millilitres, -1):.0f} mL vapour"


def test_a_tension_above_the_chart_s_top_fills_the_container_and_keeps_its_value() -> None:
    """An 8% sevoflurane dial puts the circuit at 4 MAC, above the 3 MAC top."""

    seconds = 10 * SECONDS_PER_MINUTE
    snapshot = _run_with_no_ventilation(8.0, seconds).snapshot()
    percent = _circuit_percent(8.0, seconds, float(snapshot.circuit_volume_l))
    circuit, alveolar, *_ = container_readings(snapshot)

    assert percent > AXIS_TOP_PERCENT
    assert circuit.fill == 1.0
    assert circuit.off_scale
    assert circuit.tension == f"{percent:.2f}%"
    assert not alveolar.off_scale


def test_a_container_s_height_is_its_tension_and_not_its_amount() -> None:
    """At a 1 MAC sevoflurane dial, fat stands under 1% of its height at 60 min.

    It then holds about a fifth of the agent the run holds, more than the
    alveoli hold, while the alveolar container stands near a third of its
    height (`docs/MODEL.md` § "The compartment schematic: what its heights,
    amounts and share bar assert"). So a reader who took the heights for
    amounts would rank the two the wrong way round, and the labels must carry
    the amounts.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(SEVOFLURANE_MAC_PERCENT))
    controller.start()
    for _ in range(round(60 * SECONDS_PER_MINUTE / STEP_S)):
        controller.advance(SimulationStep(STEP_S))
    snapshot = controller.snapshot()
    by_quantity = {reading.quantity: reading for reading in container_readings(snapshot)}
    amounts = snapshot.compartment_agent_amounts

    assert by_quantity[RecordedQuantity.FAT].fill < 0.01
    assert amounts.of(RecordedQuantity.FAT) / snapshot.stored_agent_l > 0.15
    assert by_quantity[RecordedQuantity.ALVEOLAR].fill > by_quantity[RecordedQuantity.FAT].fill
    assert amounts.of(RecordedQuantity.FAT) > amounts.of(RecordedQuantity.ALVEOLAR)


def test_each_container_prints_the_tension_its_readout_prints() -> None:
    snapshot = _run_with_no_ventilation(8.0, 90.0).snapshot()
    readout_values = {
        readout.name: readout.value for readout in readouts(snapshot, DEFAULT_PLAYBACK_RATE)
    }

    for reading in container_readings(snapshot):
        assert reading.tension == readout_values[reading.name]
