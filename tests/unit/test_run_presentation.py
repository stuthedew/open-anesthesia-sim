"""Unit tests for `app/run_presentation.py`: the one value a run's panel is written from.

No test here builds a widget. Each builds a real `SimulationController`,
advances it at the shipped step size, and checks the `RunPresentation` that
`drawn_run` or `halted_run` returns. `RunView.show_presentation` writes that
value and decides nothing, so what a reader sees on a frame and on a halt is
decided here.

The tests of a halt check the compartment values as one value. A halt either
keeps all of them or withholds all of them. The tests that walk the fields
of `RunValues` use `dataclasses.fields`, so a field added later is checked
without an edit to this file (`PL-RF2S`).
"""

import json
from collections.abc import Iterator
from dataclasses import fields, is_dataclass, replace
from importlib.resources import files

import pytest

from anesthesia_sim.app.agent_cost import WITHHELD_DELIVERED
from anesthesia_sim.app.compartment_schematic import WITHHELD_SCHEMATIC
from anesthesia_sim.app.control_timeline import group_adjustments
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    SIMULATION_STEP_S,
    WITHHELD_ACCOUNTING,
    WITHHELD_CONCENTRATION_TEXT,
    WITHHELD_ELAPSED_TIME_TEXT,
    WITHHELD_MAC_MULTIPLE_TEXT,
)
from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.app.run_presentation import (
    DialsNotOffered,
    KeptValues,
    RunPanelState,
    RunPresentation,
    RunValues,
    ValuesStanding,
    drawn_run,
    drawn_values,
    halted_run,
    withheld_values,
)
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import AgentSimulationValidationError
from anesthesia_sim.core.parameters import parse_breathing_circuit_parameters
from anesthesia_sim.layout.run_identity import RunIdentities

_RUN_ID = RunIdentities().mint()
_AGENT_NAMES = ("sevoflurane", "desflurane", "isoflurane")
_CLOCK_INDEX = next(index for index, panel in enumerate(READOUT_PANELS) if panel.quantity is None)


def _state(**changes: object) -> RunPanelState:
    """What a lone run's panel holds before anything has happened to it."""

    state = RunPanelState(
        run_id=_RUN_ID,
        name=None,
        case=0,
        playback_rate=PlaybackRate(1),
        is_branch=False,
        comparing=False,
        branch_offered=False,
        rejected_setting_notice=None,
        refused_reset_notice=None,
        pending_agent_name=None,
    )

    return replace(state, **changes)  # type: ignore[arg-type]


def _run_at(elapsed_s: float, *, agent_id: str = "sevoflurane") -> SimulationController:
    """A real run of `agent_id`, delivering 2%, advanced to `elapsed_s` and paused."""

    controller = SimulationController()

    if agent_id != controller.snapshot().agent_id:
        controller.set_agent(agent_id)

    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()

    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)

    controller.pause()

    return controller


def _drawn(controller: SimulationController, state: RunPanelState) -> RunPresentation:
    snapshot = controller.snapshot()

    return drawn_run(snapshot, group_adjustments(snapshot.control_timeline), state)


def _halted(
    controller: SimulationController, state: RunPanelState, kept: KeptValues
) -> RunPresentation:
    record = controller.record()

    return halted_run(record, group_adjustments(record.control_timeline), state, kept)


def _strings(value: object) -> Iterator[str]:
    """Every string anywhere inside a value built from dataclasses, tuples and strings."""

    if isinstance(value, str):
        yield value
    elif isinstance(value, tuple):
        for item in value:
            yield from _strings(item)
    elif is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield from _strings(getattr(value, field.name))


# --- a drawn frame ------------------------------------------------------------------


def test_a_drawn_run_states_the_snapshot_it_was_given_on_every_part() -> None:
    """A frame's values, 1 MAC line, dials and record all come from the one snapshot.

    The expected texts are worked out from the run, not from the builders. The run
    delivers 2% sevoflurane and has run for 90 s, and 1 MAC of sevoflurane is 2.0%
    (`docs/MODEL.md` § "MAC multiples as a display unit").
    """

    controller = _run_at(90.0)

    shown = _drawn(controller, _state())

    assert shown.standing is ValuesStanding.DRAWN
    assert shown.run_id == _RUN_ID
    assert shown.record == controller.record()
    assert shown.values.readouts[_CLOCK_INDEX].value == "1m30s"
    assert shown.values.schematic.instant == "1m30s"
    assert shown.values.delivered.instant == "1m30s"
    assert shown.one_mac == "1 MAC sevoflurane = 2.0%"
    assert shown.statement.agent_id == "sevoflurane"
    assert shown.delivered_line is not None
    assert shown.delivered_line == "Delivered 2.00% (1.00 ×MAC)"
    assert not isinstance(shown.dials, DialsNotOffered)
    assert shown.new_case is None


def test_a_drawn_run_restates_an_open_new_case_question_from_its_snapshot() -> None:
    """The open question names the time the frame's own snapshot has run to (`PL-WM5P`)."""

    controller = _run_at(90.0)

    shown = _drawn(controller, _state(pending_agent_name="Desflurane"))

    assert shown.new_case is not None
    assert any("1m30s" in line for line in shown.new_case.body)


def test_a_compared_run_s_banner_names_the_run() -> None:
    """While a second run is drawn, a run's banner says which run it speaks for (`PL-TSZM`)."""

    controller = _run_at(30.0)

    lone = _drawn(controller, _state(rejected_setting_notice="Setting refused: too high."))
    compared = _drawn(
        controller, _state(name="Run 2", rejected_setting_notice="Setting refused: too high.")
    )

    assert lone.notice is not None
    assert lone.notice.startswith("Setting refused: too high.")
    assert "Run 2" not in lone.notice
    assert compared.notice is not None
    assert compared.notice != lone.notice
    assert "Run 2" in compared.notice
    assert compared.name == "Run 2"


# --- a halt -------------------------------------------------------------------------


def test_a_halt_keeps_every_value_of_the_last_frame_while_the_run_is_the_one_it_drew() -> None:
    """A halt with no start-over since the last frame shows that frame's values, all of them."""

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.fail("the frame could not be drawn")

    shown = _halted(controller, state, KeptValues(state.case, frame.values))

    assert shown.standing is ValuesStanding.KEPT
    assert shown.values == frame.values
    assert shown.statement.status != frame.statement.status


def test_a_halt_after_a_start_over_withholds_every_value_of_the_discarded_run() -> None:
    """After a Reset or an agent change that no frame has drawn, a halt keeps no value at all.

    This is the case behind `PL-6RJ0`, `PL-J5GC`, `PL-RNYV`, `PL-B396` and
    `PL-B8DL`. Each of them found one more value that a halt had left on
    screen from the run before. The loop walks the fields of `RunValues`, so
    a value added to the frame later is checked here without being named.
    """

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.set_agent("desflurane")
    controller.fail("the frame could not be drawn")
    started_over = replace(state, case=state.case + 1)

    shown = _halted(controller, started_over, KeptValues(state.case, frame.values))

    assert shown.standing is ValuesStanding.WITHHELD

    for field in fields(RunValues):
        withheld = getattr(shown.values, field.name)
        assert withheld != getattr(frame.values, field.name), field.name
        assert withheld == getattr(withheld_values(state.playback_rate), field.name), field.name

    assert shown.one_mac == "1 MAC desflurane = 6.0%"


def _naming_no_agent(text: str) -> str:
    """`text` with each shipped agent's name replaced by the word a withheld panel uses."""

    lowered = text.lower()

    for agent in _AGENT_NAMES:
        lowered = lowered.replace(agent, "agent")

    return lowered


def test_withheld_values_state_no_number_and_no_agent_of_any_run() -> None:
    """A withheld value holds no agent's name, and no number that belongs to a run.

    The expected property is worked out here, not read from the constants. A
    withheld value stands under the heading of the run that replaced the
    discarded one. So any number in it, and any agent it named, would be read
    as that run's. Some standing text holds a digit: the playback rate, which
    is a setting of the view (`PL-P58M`), and a unit's caption, which states
    the temperature the unit is defined at. Such text reads the same on two
    frames of different agents at different instants, once the agent's name
    is taken out. Every other digit on a frame belongs to its run.
    """

    rate = PlaybackRate(20)
    standing = {
        _naming_no_agent(text) for text in _strings(drawn_values(_run_at(90.0).snapshot(), rate))
    } & {
        _naming_no_agent(text)
        for text in _strings(drawn_values(_run_at(30.0, agent_id="desflurane").snapshot(), rate))
    }

    texts = list(_strings(withheld_values(rate)))

    assert texts
    assert [text for text in texts if any(agent in text.lower() for agent in _AGENT_NAMES)] == []
    assert [
        text
        for text in texts
        if any(character.isdigit() for character in text) and _naming_no_agent(text) not in standing
    ] == []


def test_withheld_values_are_the_withheld_form_of_each_surface() -> None:
    """Each surface is given its own whole withheld value, with no field kept from a frame."""

    withheld = withheld_values(PlaybackRate(1))

    assert withheld.schematic == WITHHELD_SCHEMATIC
    assert withheld.delivered == WITHHELD_DELIVERED
    assert withheld.accounting == WITHHELD_ACCOUNTING
    assert [readout.value for readout in withheld.readouts] == [
        WITHHELD_ELAPSED_TIME_TEXT if panel.quantity is None else WITHHELD_CONCENTRATION_TEXT
        for panel in READOUT_PANELS
    ]
    assert [
        readout.secondary
        for panel, readout in zip(READOUT_PANELS, withheld.readouts, strict=True)
        if panel.quantity is not None
    ] == [WITHHELD_MAC_MULTIPLE_TEXT] * 6
    assert [readout.name for readout in withheld.readouts] == [
        panel.name for panel in READOUT_PANELS
    ]


def test_every_value_a_frame_draws_differs_from_its_withheld_form() -> None:
    """A drawn value never equals its withheld form, so the two tests above can tell them apart."""

    drawn = drawn_values(_run_at(90.0).snapshot(), PlaybackRate(1))
    withheld = withheld_values(PlaybackRate(1))

    for field in fields(RunValues):
        assert getattr(drawn, field.name) != getattr(withheld, field.name), field.name


def test_a_halt_s_banner_says_the_run_started_over_only_when_it_did() -> None:
    """The banner and the values agree on whether the last frame belongs to this run."""

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.fail("the frame could not be drawn")
    kept = KeptValues(state.case, frame.values)

    same_run = _halted(controller, state, kept)
    started_over = _halted(controller, replace(state, case=state.case + 1), kept)

    assert same_run.notice is not None
    assert started_over.notice is not None
    assert same_run.notice != started_over.notice
    assert "started over" in started_over.notice
    assert "started over" not in same_run.notice


def test_a_halt_restates_the_playback_rate_the_reader_chose_on_the_halted_run() -> None:
    """A rate chosen after the last frame reaches the clock's playback line (`PL-P58M`)."""

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.fail("the frame could not be drawn")

    shown = _halted(
        controller,
        replace(state, playback_rate=PlaybackRate(60)),
        KeptValues(state.case, frame.values),
    )

    assert frame.values.readouts[_CLOCK_INDEX].secondary == "1× real time"
    assert shown.values.readouts[_CLOCK_INDEX].secondary == "60× real time"
    assert shown.values.readouts[_CLOCK_INDEX].value == "1m30s"
    assert [
        readout for index, readout in enumerate(shown.values.readouts) if index != _CLOCK_INDEX
    ] == [readout for index, readout in enumerate(frame.values.readouts) if index != _CLOCK_INDEX]


@pytest.mark.parametrize("started_over", [False, True])
def test_a_halt_after_a_rejected_accounting_step_shows_that_step_s_check(
    started_over: bool,
) -> None:
    """The accounting panel shows the rejected step, whether the other values are kept or not.

    40.0 L delivered, 20.0 L exhausted and 14.0 L stored leave 6.0 L
    unaccounted, which the panel prints as less than 1e+01 L.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=40.0, exhausted_agent_l=20.0)

    with pytest.raises(AgentSimulationValidationError) as raised:
        validator.require_valid_agent_accounting(currently_stored_agent_l=14.0)

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.fail("the accounting check failed")
    record = replace(controller.record(), rejected_accounting=raised.value.check)

    shown = halted_run(
        record,
        group_adjustments(record.control_timeline),
        replace(state, case=state.case + int(started_over)),
        KeptValues(state.case, frame.values),
    )

    assert shown.values.accounting.amounts.splitlines()[3] == "Unaccounted: <1e+01 L"
    assert shown.values.accounting != frame.values.accounting
    assert shown.values.accounting != WITHHELD_ACCOUNTING
    assert (shown.values.schematic == WITHHELD_SCHEMATIC) is started_over
    assert (shown.values.schematic == frame.values.schematic) is not started_over


def test_a_halt_builds_no_compartment_value() -> None:
    """A halt is stated for a run whose snapshot is refused (`PL-7DJK`)."""

    controller = _run_at(90.0)
    state = _state()
    frame = _drawn(controller, state)
    controller.fail("a compartment value was refused")

    def refuse() -> None:
        raise AssertionError("a halt must not read a snapshot")

    controller.snapshot = refuse  # type: ignore[method-assign, assignment]

    shown = _halted(controller, state, KeptValues(state.case, frame.values))

    assert shown.record == controller.record()
    assert shown.statement.transport.start_enabled is False


# --- dials that cannot be built -----------------------------------------------------


def test_dials_that_cannot_be_built_are_carried_and_everything_else_is_still_stated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A run whose machine can offer no fresh gas flow still states its status and banner.

    The machine declares a deliverable range from 4.02 to 4.04 L/min, which
    holds no step of the dial's 0.1 L/min resolution. `setting_readouts`
    refuses it. The refusal is returned in `dials`, so that the status word,
    the transport and the banner reach the screen before it is raised
    (`PL-25KS`, `PL-7DJK`, `PL-85LJ`).
    """

    payload = json.loads(
        files("anesthesia_sim.data.machines")
        .joinpath("reference_circle_system.json")
        .read_text(encoding="utf-8")
    )
    payload["default_fresh_gas_flow_l_min"] = 4.03
    payload["deliverable_fresh_gas_flow_range"] = {"minimum_l_min": 4.02, "maximum_l_min": 4.04}
    machine = parse_breathing_circuit_parameters(payload)
    monkeypatch.setattr(uptake_system, "load_reference_circle_system_parameters", lambda: machine)
    controller = SimulationController()
    controller.fail("no setting can be offered")
    state = _state()
    record = controller.record()
    opening = KeptValues(state.case, withheld_values(state.playback_rate))

    shown = halted_run(record, group_adjustments(record.control_timeline), state, opening)

    assert isinstance(shown.dials, DialsNotOffered)
    assert isinstance(shown.dials.error, ValueError)
    assert shown.delivered_line is None
    assert shown.notice is not None
    assert shown.statement.transport.start_enabled is False
    assert shown.one_mac == "1 MAC sevoflurane = 2.0%"
