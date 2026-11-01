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

from anesthesia_sim.app.compartment_schematic import (
    NO_AGENT_SHARE_LINE,
    WITHHELD_SCHEMATIC,
    container_readings,
    schematic_shown,
    share_line,
    share_segments,
)
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
    """At a 1 MAC sevoflurane dial, fat's container is less than 1% full at 60 min.

    Fat then holds about a fifth of all the agent in the run, which is more than
    the alveoli hold. Yet the alveolar container is filled to nearly a third of
    its height (`docs/MODEL.md` § "The compartment schematic: what its heights,
    amounts and share bar assert"). So a reader who took the heights for amounts
    would rank fat and the alveoli the wrong way round. That is why the labels
    must give the amounts.
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


def _run(agent_id: str, seconds: float) -> SimulationController:
    """Run an agent at its 1 MAC dial with the default ventilation and flow."""

    controller = SimulationController(agent_id=agent_id)
    controller.set_delivered_concentration_percent(
        Percent(load_agent_parameters(agent_id).mac_percent)
    )
    controller.start()

    for _ in range(round(seconds / STEP_S)):
        controller.advance(SimulationStep(STEP_S))

    return controller


@pytest.mark.parametrize("agent_id", ["sevoflurane", "desflurane", "isoflurane"])
def test_the_share_bar_shares_add_up_to_the_whole(agent_id: str) -> None:
    """At every instant tested, the six shares fill the bar, and each is its amount over the total.

    The six amounts are summed here, apart from the snapshot's own total. So
    the test also checks that the bar divides by all the agent the run holds,
    circuit included (`docs/MODEL.md` § "The compartment schematic: what its
    heights, amounts and share bar assert").
    """

    controller = _run(agent_id, 0.0)
    elapsed_s = 0.0

    for until_s in (1.0, 60.0, 20 * SECONDS_PER_MINUTE, 60 * SECONDS_PER_MINUTE):
        for _ in range(round((until_s - elapsed_s) / STEP_S)):
            controller.advance(SimulationStep(STEP_S))
        elapsed_s = until_s
        snapshot = controller.snapshot()
        segments = share_segments(snapshot)
        assert segments is not None
        amounts = snapshot.compartment_agent_amounts
        total = sum(amounts.of(quantity) for quantity in COMPARTMENT_QUANTITIES)

        assert [segment.quantity for segment in segments] == list(COMPARTMENT_QUANTITIES)
        assert sum(segment.share for segment in segments) == pytest.approx(1.0, rel=1e-12)
        for segment in segments:
            assert segment.share == pytest.approx(amounts.of(segment.quantity) / total, rel=1e-12)


def test_with_no_ventilation_the_circuit_holds_the_whole_share() -> None:
    """With no alveolar ventilation, no agent leaves the circuit, so its share is the whole.

    This is the closed form of the module's oracle. Every other compartment
    holds nothing, so its share is exactly zero and is shown as `0%`.
    """

    segments = share_segments(_run_with_no_ventilation(8.0, 90.0).snapshot())
    assert segments is not None

    assert [(segment.share, segment.text) for segment in segments] == [(1.0, "100%")] + [
        (0.0, "0%")
    ] * 5


def test_a_run_that_holds_no_agent_draws_an_empty_bar_and_prints_no_share() -> None:
    """Before any agent is delivered, no share exists, so none is printed, not six zeros."""

    snapshot = SimulationController(agent_id="sevoflurane").snapshot()
    shown = schematic_shown(snapshot)

    assert snapshot.stored_agent_l == 0.0
    assert share_segments(snapshot) is None
    assert shown.shares is None
    assert shown.share_line == NO_AGENT_SHARE_LINE
    assert "%" not in NO_AGENT_SHARE_LINE


def test_the_share_lines_keep_their_count_when_the_first_agent_arrives() -> None:
    """The schematic keeps its size at Start: the empty bar's lines are as many as the shares'.

    The blind review of `PL-S79P` found that the empty bar's one line grew to
    three when the first agent arrived, which moved everything below it.
    """

    segments = share_segments(_run("sevoflurane", 1.0).snapshot())

    assert len(NO_AGENT_SHARE_LINE.splitlines()) == len(share_line(segments).splitlines())


def test_the_share_lines_name_every_segment_with_its_share_in_text() -> None:
    """The segments are named in text, never by colour alone, in the containers' order."""

    segments = share_segments(_run("sevoflurane", 60 * SECONDS_PER_MINUTE).snapshot())
    assert segments is not None
    text = share_line(segments)
    names = ["Circuit", "Alveolar", "Mixed venous", "Vessel-rich group", "Muscle", "Fat"]
    positions = [
        text.index(f"{name} {segment.text}") for name, segment in zip(names, segments, strict=True)
    ]

    assert text.splitlines()[0] == "Share of the agent the run holds:"
    assert positions == sorted(positions)


def test_fat_s_share_grows_through_the_first_hour_while_its_container_stays_nearly_empty() -> None:
    """The bar shows what the heights cannot: fat's share grows while its tension stays near zero.

    `docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
    share bar assert" gives fat about a fifth of the stored agent at one hour
    of a 1 MAC sevoflurane dial (`PL-H5DV`).
    """

    controller = _run("sevoflurane", 10 * SECONDS_PER_MINUTE)
    early = share_segments(controller.snapshot())
    for _ in range(round(50 * SECONDS_PER_MINUTE / STEP_S)):
        controller.advance(SimulationStep(STEP_S))
    snapshot = controller.snapshot()
    late = share_segments(snapshot)
    assert early is not None
    assert late is not None
    fat_reading = container_readings(snapshot)[-1]

    assert late[-1].quantity is RecordedQuantity.FAT
    assert late[-1].share > early[-1].share
    assert 0.15 < late[-1].share < 0.25
    assert fat_reading.fill < 0.01


def test_withheld_values_draw_an_empty_bar_with_no_lines() -> None:
    assert WITHHELD_SCHEMATIC.shares is None
    assert WITHHELD_SCHEMATIC.share_line is None
