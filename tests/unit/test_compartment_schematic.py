"""Tests for the compartment schematic's readings: each container's fill and its labels.

`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert" is the specification (`PL-2881`). The expected values come
from a closed form, not from the snapshot under test. With no alveolar
ventilation, nothing leaves the circuit for the patient. The circuit then
fills from the fresh gas alone, so its fraction is F_D(1 - exp(-t FGF / V))
and its amount is V times that fraction (`PL-KFTM`'s oracle). The chart's
axis top is 3 MAC of the running agent, and sevoflurane's MAC is read from its
data file, apart from the code under test.
"""

import math
import re
from dataclasses import replace
from math import exp

import pytest

from anesthesia_sim.app.compartment_schematic import (
    NO_AGENT_SHARE_CAPTION,
    NO_SHARE_TEXT,
    SHARE_CAPTION,
    WITHHELD_SCHEMATIC,
    container_readings,
    instant_line,
    scale_caption,
    scale_marks,
    schematic_shown,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import readouts
from anesthesia_sim.app.playback import DEFAULT_PLAYBACK_RATE
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, FreshGasFlow

FRESH_GAS_FLOW_L_MIN = 8.0
SECONDS_PER_MINUTE = 60
SEVOFLURANE_MAC_PERCENT = load_agent_parameters("sevoflurane").mac_at_age_40_percent
# The concentration chart's axis is 3 MAC of the running agent for every agent
# (`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
# share bar assert").
AXIS_TOP_PERCENT = 3 * SEVOFLURANE_MAC_PERCENT


def _run_with_no_ventilation(dial_percent: float, seconds: int) -> SimulationController:
    """Run sevoflurane with no alveolar ventilation, so only the circuit fills."""

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_fresh_gas_flow(FreshGasFlow(FRESH_GAS_FLOW_L_MIN))
    controller.set_delivered_concentration_percent(Percent(dial_percent))
    controller.start()

    for _ in range(seconds // SIMULATION_STEP_S):
        controller.advance()

    return controller


def _circuit_percent(dial_percent: float, seconds: int, volume_l: float) -> float:
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

    seconds = 30
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
    its height (`docs/INTERFACE.md` § "The compartment schematic: what its heights,
    amounts and share bar assert"). So a reader who took the heights for amounts
    would rank fat and the alveoli the wrong way round. That is why the labels
    must give the amounts.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(SEVOFLURANE_MAC_PERCENT))
    controller.start()
    for _ in range(60 * SECONDS_PER_MINUTE // SIMULATION_STEP_S):
        controller.advance()
    snapshot = controller.snapshot()
    by_quantity = {reading.quantity: reading for reading in container_readings(snapshot)}
    amounts = snapshot.compartment_agent_amounts

    assert by_quantity[RecordedQuantity.FAT].fill < 0.01
    assert amounts.of(RecordedQuantity.FAT) / snapshot.stored_agent_l > 0.15
    assert by_quantity[RecordedQuantity.ALVEOLAR].fill > by_quantity[RecordedQuantity.FAT].fill
    assert amounts.of(RecordedQuantity.FAT) > amounts.of(RecordedQuantity.ALVEOLAR)


def test_each_container_prints_the_tension_its_readout_prints() -> None:
    snapshot = _run_with_no_ventilation(8.0, 90).snapshot()
    readout_values = {
        readout.name: readout.value for readout in readouts(snapshot, DEFAULT_PLAYBACK_RATE)
    }

    for reading in container_readings(snapshot):
        assert reading.tension == readout_values[reading.name]


def _run(agent_id: str, seconds: int) -> SimulationController:
    """Run an agent at its 1 MAC dial with the default ventilation and flow."""

    controller = SimulationController(agent_id=agent_id)
    controller.set_delivered_concentration_percent(
        Percent(load_agent_parameters(agent_id).mac_at_age_40_percent)
    )
    controller.start()

    for _ in range(seconds // SIMULATION_STEP_S):
        controller.advance()

    return controller


@pytest.mark.parametrize("agent_id", ["sevoflurane", "desflurane", "isoflurane"])
def test_the_six_shares_add_up_to_the_whole(agent_id: str) -> None:
    """At every instant tested, the six shares make up the whole, each its amount over the total.

    The test sums the six amounts itself, independently of the snapshot's own
    total. So the test also checks that each share divides by all the agent
    the run holds, circuit included (`docs/INTERFACE.md` § "The compartment
    schematic: what its heights, amounts and share bar assert").
    """

    controller = _run(agent_id, 0)
    elapsed_s = 0

    for until_s in (1, 60, 20 * SECONDS_PER_MINUTE, 60 * SECONDS_PER_MINUTE):
        for _ in range((until_s - elapsed_s) // SIMULATION_STEP_S):
            controller.advance()
        elapsed_s = until_s
        snapshot = controller.snapshot()
        readings = container_readings(snapshot)
        amounts = snapshot.compartment_agent_amounts
        total = sum(amounts.of(quantity) for quantity in COMPARTMENT_QUANTITIES)
        shares = [reading.share for reading in readings]

        assert [reading.quantity for reading in readings] == list(COMPARTMENT_QUANTITIES)
        assert None not in shares
        # Both limits are numerical. Each share rounds once in its division and
        # the sum rounds five more times, so the error is a few times 1.1e-16.
        # 1e-12 is far above that, and far below the 0.5% a printed share hides.
        assert sum(share for share in shares if share is not None) == pytest.approx(1.0, rel=1e-12)
        for reading in readings:
            assert reading.share == pytest.approx(amounts.of(reading.quantity) / total, rel=1e-12)


def test_with_no_ventilation_the_circuit_holds_the_whole_share() -> None:
    """With no alveolar ventilation, no agent leaves the circuit, which then holds the whole share.

    This is the closed form that the module's docstring describes. Every other compartment
    holds nothing, so its share is exactly zero and its label prints `0%`.
    """

    readings = container_readings(_run_with_no_ventilation(8.0, 90).snapshot())

    assert [(reading.share, reading.share_text) for reading in readings] == [
        (1.0, "100% of agent")
    ] + [(0.0, "0% of agent")] * 5


def test_a_run_that_holds_no_agent_prints_no_share_and_says_why() -> None:
    """Before any agent is delivered, no share exists, so none is printed, not six zeros."""

    snapshot = SimulationController(agent_id="sevoflurane").snapshot()
    shown = schematic_shown(snapshot)

    assert snapshot.stored_agent_l == 0.0
    assert [reading.share for reading in shown.readings] == [None] * 6
    assert [reading.share_text for reading in shown.readings] == [NO_SHARE_TEXT] * 6
    assert shown.share_caption == NO_AGENT_SHARE_CAPTION
    assert "%" not in NO_SHARE_TEXT
    assert "%" not in NO_AGENT_SHARE_CAPTION
    assert "the six containers hold no agent" in NO_AGENT_SHARE_CAPTION


def test_the_share_caption_keeps_its_height_when_the_first_agent_arrives() -> None:
    """The caption is one line before the first agent and after it, so nothing below it moves.

    The blind review of `PL-S79P` found that the old bar's one line grew to
    three when the first agent arrived, which moved everything below it.
    """

    before = schematic_shown(SimulationController(agent_id="sevoflurane").snapshot())
    after = schematic_shown(_run("sevoflurane", 1).snapshot())

    assert before.share_caption is not None
    assert after.share_caption is not None
    assert len(before.share_caption.splitlines()) == len(after.share_caption.splitlines()) == 1


def test_the_share_caption_says_the_shares_are_of_the_agent_held_at_this_instant() -> None:
    """`PL-8PL4`, `PL-KQ0S`: the caption says the whole is the agent in the six containers now.

    The project owner read the old bar's heading, "Share of the agent the run
    holds", as agent counted over the whole run. So the caption must name the
    instant. The share is computed over the six containers drawn, and the model
    leaves out stores that a patient's body holds agent in (`docs/MODEL.md`
    § "What the model does not represent"). So the caption names the six
    containers, and must not claim the whole body. The count in the caption is
    checked against the number of containers the schematic shows.
    """

    shown = schematic_shown(_run("sevoflurane", 60 * SECONDS_PER_MINUTE).snapshot())

    assert shown.share_caption == SHARE_CAPTION
    assert len(shown.readings) == 6
    assert "in the six containers at this instant" in SHARE_CAPTION
    assert "body" not in SHARE_CAPTION


def test_each_label_prints_its_own_compartment_s_share_in_whole_percent() -> None:
    """Each container's label prints the share of its own compartment, never a neighbour's.

    The expected text is worked out here from the six amounts, rounded to the
    nearest whole percent, with `<1%` for a share that rounds to 0 but is above
    it (`docs/INTERFACE.md` § "Displayed precision"). The test reads the run at
    ten minutes, when no two of the six shares print the same, so a share
    printed under the wrong container would show. It checks that they differ,
    so a change to the model cannot leave two equal texts that a swap would not
    change.
    """

    snapshot = _run("sevoflurane", 10 * SECONDS_PER_MINUTE).snapshot()
    readings = container_readings(snapshot)
    amounts = snapshot.compartment_agent_amounts
    total = sum(amounts.of(quantity) for quantity in COMPARTMENT_QUANTITIES)
    expected_texts = []

    for reading in readings:
        percent = 100.0 * amounts.of(reading.quantity) / total
        whole = round(percent)
        expected = "<1%" if whole == 0 and percent > 0.0 else f"{whole}%"
        expected_texts.append(f"{expected} of agent")

    assert len(set(expected_texts)) == len(expected_texts), expected_texts
    assert [reading.share_text for reading in readings] == expected_texts


def test_fat_s_share_grows_through_the_first_hour_while_its_container_stays_nearly_empty() -> None:
    """Fat's share grows while fat's tension stays near zero.

    The containers' heights are tensions, so the heights cannot show this
    growth. `docs/INTERFACE.md` § "The compartment schematic: what its heights,
    amounts and share bar assert" gives fat about a fifth of the stored agent
    after one hour with the sevoflurane dial at 1 MAC (`PL-H5DV`).
    """

    controller = _run("sevoflurane", 10 * SECONDS_PER_MINUTE)
    early = container_readings(controller.snapshot())[-1]
    for _ in range(50 * SECONDS_PER_MINUTE // SIMULATION_STEP_S):
        controller.advance()
    late = container_readings(controller.snapshot())[-1]
    assert early.share is not None
    assert late.share is not None

    assert late.quantity is RecordedQuantity.FAT
    assert late.share > early.share
    assert 0.15 < late.share < 0.25
    assert late.fill < 0.01


@pytest.mark.parametrize("agent_id", ["sevoflurane", "desflurane", "isoflurane"])
def test_each_container_is_marked_every_half_mac_of_the_standard_scale(agent_id: str) -> None:
    """`PL-8W1B`: the marks stand at every 0.5 MAC below the 3 MAC top, for every agent.

    At its standard top the chart labels its MAC axis every 0.5 MAC from 0 to
    3 MAC (`docs/INTERFACE.md` § "The compartment schematic: what its heights,
    amounts and share bar assert"). So a container is marked at five sixths
    of its height and below, in sixths. The caption names the top in percent
    and in MAC, and the spacing in MAC. The top's percent is three times the
    agent's MAC, read from its data file apart from the code under test.
    """

    controller = SimulationController(agent_id=agent_id)
    snapshot = controller.snapshot()
    top = 3 * load_agent_parameters(agent_id).mac_at_age_40_percent

    assert scale_marks(snapshot) == pytest.approx([sixth / 6 for sixth in range(1, 6)])
    assert f"0 to {top:g}% of 1 atm (3 ×MAC)" in scale_caption(snapshot)
    assert "Marks stand every 0.5 ×MAC." in scale_caption(snapshot)


def test_withheld_values_draw_no_marks() -> None:
    assert WITHHELD_SCHEMATIC.marks == ()


def test_withheld_values_draw_empty_share_bars_with_no_share_and_no_caption() -> None:
    assert [reading.share for reading in WITHHELD_SCHEMATIC.readings] == [None] * 6
    assert [reading.share_text for reading in WITHHELD_SCHEMATIC.readings] == [NO_SHARE_TEXT] * 6
    assert WITHHELD_SCHEMATIC.share_caption is None


#: The containers' names, as the readout panels name them.
_CONTAINER_NAMES = ["Circuit", "Alveolar", "Mixed venous", "Vessel-rich group", "Muscle", "Fat"]


def test_the_schematic_shows_every_part_from_one_snapshot() -> None:
    """At an 8% sevoflurane dial with no ventilation for 10 min, every part of the schematic shows.

    Each part is checked against a value worked out here. The circuit is
    above the 3 MAC top, so it is drawn full and named in words as above the
    scale, and no other container is named. The marks stand at each sixth of
    the height below the top, and the caption names that top. No agent leaves
    the circuit, so the circuit's label gives it the whole share. A
    schematic that left out a part would hide that a container is off the
    scale, or show a run that holds agent as if it held none.
    """

    seconds = 10 * SECONDS_PER_MINUTE
    snapshot = _run_with_no_ventilation(8.0, seconds).snapshot()
    shown = schematic_shown(snapshot)
    circuit = shown.readings[0]

    assert _circuit_percent(8.0, seconds, float(snapshot.circuit_volume_l)) > AXIS_TOP_PERCENT
    assert (circuit.quantity, circuit.fill, circuit.off_scale) == (
        RecordedQuantity.CIRCUIT,
        1.0,
        True,
    )
    assert shown.off_scale_line is not None
    assert [name for name in _CONTAINER_NAMES if name in shown.off_scale_line] == ["Circuit"]
    assert shown.marks == pytest.approx([sixth / 6 for sixth in range(1, 6)])
    assert shown.scale_caption is not None
    assert f"0 to {AXIS_TOP_PERCENT:g}% of 1 atm (3 ×MAC)" in shown.scale_caption
    assert [(reading.share, reading.share_text) for reading in shown.readings] == [
        (1.0, "100% of agent")
    ] + [(0.0, "0% of agent")] * 5
    assert shown.share_caption == SHARE_CAPTION


@pytest.mark.parametrize("total_l", [-1.0, math.inf, math.nan])
def test_a_stored_total_that_is_negative_or_not_finite_is_refused_by_name(total_l: float) -> None:
    """The shares are refused, with the total named, rather than drawn from such a total.

    A run that has not started holds no agent in any compartment. Divided by
    an infinite or a negative total, its six amounts would give six shares of
    0%. That bar looks like a real one, so the total is refused before any
    share is formed.
    """

    snapshot = replace(
        SimulationController(agent_id="sevoflurane").snapshot(), stored_agent_l=total_l
    )
    message = f"the run's stored agent must be finite and not negative, not {total_l!r} L"

    with pytest.raises(ValueError, match=re.escape(message)):
        container_readings(snapshot)


def test_the_line_over_a_schematic_names_the_run_only_while_runs_are_compared() -> None:
    """A lone run's line gives the instant alone, and a compared run's line also names the run.

    The order in which compared schematics are stacked cannot say which run a
    tension belongs to, so the name in this line is what says it.
    """

    assert instant_line("10m", None) == "At 10m of simulated time"
    assert instant_line("10m", "Run 2") == "Run 2, at 10m of simulated time"
