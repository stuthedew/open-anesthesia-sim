"""Unit tests for the presentation logic in SimulationView.

These tests exercise formatting, unit conversion, and controller-wiring
without a live Flet client. Flet's individual controls (Text, Slider,
Event, chart series, ...) can be constructed and inspected as plain Python
objects; only a live Page/Session is needed to actually flush updates to a
browser. `_FakePage` stands in for the three Page behaviors SimulationView
touches outside of `start_simulation_timer()` (which this suite does not call
and does not claim to cover): the `padding` attribute, the `update()` call,
and the `add()` that `mount()` hands the assembled control tree to. Mounting
is covered only to the extent of what the assembled tree *says* - the label
tests below read strings out of it - not of what a live client would draw
from it.
"""

import asyncio
import contextlib
import dataclasses
import re
from typing import Any, cast

import flet as ft
import flet_charts as fch
import pytest

from anesthesia_sim.app.chart_series import CHART_COLUMN_BUDGET_PER_SERIES
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    TIME_BASE_LADDER,
    time_base_for_span,
)
from anesthesia_sim.app.control_timeline import group_adjustments
from anesthesia_sim.app.controller import (
    CONTROL_INPUT_UNITS,
    ControlChange,
    ControlInput,
    HistoryWindow,
    RecordedQuantity,
    RunHistory,
    SimulationController,
    SimulationHistorySample,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    CHART_GRID_INTERVAL_MAC,
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    chart_axis_top_percent,
    format_case_discard_warning,
    format_chart_time_label,
    format_elapsed,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_time_base,
    format_wash_in_ratio,
    mac_axis_ticks,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.simulation_view import (
    AGENT_RENDER_STYLES,
    AGENT_SELECTOR_WIDTH,
    AVAILABLE_AGENTS,
    KEEP_CURRENT_CASE_TEMPLATE,
    MAC_AWAKE_BAND_COLOR,
    MAC_AWAKE_BAND_EDGE_STROKE_WIDTH,
    MAC_AWAKE_BAND_FILL_OPACITY,
    MAX_CHART_CONTROL_MARKS,
    MAX_LISTED_ADJUSTMENTS,
    METRIC_GRID_COLUMNS,
    NEW_CASE_CARRYOVER_TEMPLATE,
    NEW_CASE_IS_NOT_A_VIEW_TEXT,
    NO_CONTROL_CHANGES_TEXT,
    NO_TRACES_SHOWN_TEXT,
    ONE_MAC_LINE_DASH_PATTERN,
    RENDER_INTERVAL_S,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    START_NEW_CASE_TEMPLATE,
    WASH_IN_AXIS_MAXIMUM,
    WASH_IN_TERMINUS_CEILING,
    SimulationView,
)
from anesthesia_sim.app.theme import ACCENT_TEXT, AGENT_COLOR_SCHEMES, INK, MUTED, WARNING
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO, read_wash_in, wash_in_ratio
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.exceptions import SimulationDomainLimitError, SimulationNumericalError
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    MacAwakeReference,
    load_agent_parameters,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem


class _FakePage:
    """Stand-in exposing only the Page surface SimulationView uses."""

    def __init__(self) -> None:
        self.padding: int | None = None
        self.update_calls = 0
        # What `mount()` handed over, kept so a test can read the assembled
        # tree back. A real Page renders these; this one only holds them.
        self.controls: list[object] = []
        # The dialog stack, in the order `show_dialog` was called. A real
        # Page also drops a dialog from this list when the *client* reports
        # its dismissal, which no test has a client to do; keeping every
        # dialog is what lets a test see that a second one was never opened.
        self.dialogs: list[ft.AlertDialog] = []

    def add(self, *controls: object) -> None:
        self.controls.extend(controls)

    def update(self) -> None:
        self.update_calls += 1

    def show_dialog(self, dialog: ft.AlertDialog) -> None:
        """Open a dialog, marking it open as the real Page does."""

        dialog.open = True
        self.dialogs.append(dialog)

    def pop_dialog(self) -> ft.AlertDialog | None:
        """Close the topmost open dialog, as the real Page does.

        Deliberately does not call `dialog.update()`, which the real one
        does and which needs a live client. What a test is reading here is
        the `open` flag, and that is set the same way.
        """

        for dialog in reversed(self.dialogs):
            if dialog.open:
                dialog.open = False
                return dialog

        return None


class _FakeController:
    """Stand-in with a caller-controlled snapshot and run history.

    Isolates view-formatting tests from the simulation engine so the
    accounting-failed branch can be exercised without needing to actually
    violate a physical invariant.

    The snapshot and the history are held apart because the real controller
    answers for them apart: `snapshot()` is the run's state at one instant,
    `history_window()` is the part of the run one frame draws. A test with
    nothing to say about the chart leaves `history` unset and gets a single
    sample at the snapshot's own simulated time.
    """

    def __init__(
        self,
        snapshot: SimulationSnapshot,
        history: tuple[SimulationHistorySample, ...] | None = None,
    ) -> None:
        self.snapshot_value = snapshot
        self.history_value = (
            history
            if history is not None
            else (
                _sample(
                    snapshot.elapsed_s, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=snapshot.agent_id
                ),
            )
        )
        self._run = RunHistory.of(self.history_value)
        self.is_running = snapshot.is_running
        self.requested_window_starts: list[float] = []

    def snapshot(self) -> SimulationSnapshot:
        return self.snapshot_value

    def advance_to(
        self, history: tuple[SimulationHistorySample, ...], **snapshot_fields: Any
    ) -> None:
        """Move the fake on to a longer run, snapshot and history together.

        Set as a pair for the reason `_fake_controller` builds them as one:
        the two halves of a frame must describe the same run, or a test
        watching the chart follow the readouts is watching two runs.
        """

        self.snapshot_value = _snapshot(history=history, **snapshot_fields)
        self.history_value = history
        self._run = RunHistory.of(history)

    def switch_agent(
        self,
        agent_id: str,
        history: tuple[SimulationHistorySample, ...] | None = None,
        **snapshot_fields: Any,
    ) -> None:
        """Move the fake to another agent, its run started over as the real one does.

        `SimulationController.set_agent` builds a new `RunHistory` under the
        new agent's identifier, so a fake that changed only the snapshot
        would hand the view a state the controller cannot produce: a run
        recorded under one substance, read under another's name.

        Args:
            agent_id: The agent now running, and so the substance its run
                is recorded under.
            history: The new run, already recorded under `agent_id`. A run
                of one blank sample by default, as `set_agent` leaves it.
            snapshot_fields: Everything else `_snapshot` takes.
        """

        if history is None:
            history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=agent_id),)

        self.advance_to(history, agent_id=agent_id, **snapshot_fields)

    def history_window(self, start_s: float) -> HistoryWindow:
        """Cut the window the real controller would, by the same search.

        Deliberately not a hand-rolled slice: a fake that located the
        window differently could let a view test pass against a boundary
        the real controller never produces.
        """

        self.requested_window_starts.append(start_s)

        return self._run.window_from(start_s)


#: The agent every fixture here runs unless it says otherwise.
#:
#: Named once because the snapshot and the recorded run have to agree on it:
#: the view reads the run under the agent its snapshot names.
_DEFAULT_AGENT = "sevoflurane"


def _sample(
    elapsed_s: float,
    circuit: float,
    alveolar: float,
    venous: float,
    vessel_rich: float,
    muscle: float,
    fat: float,
    substance_id: str = _DEFAULT_AGENT,
) -> SimulationHistorySample:
    """One recorded sample of one substance's six compartments.

    `substance_id` defaults to the agent `_snapshot` does, so the two
    halves of a fixture describe one run. A test naming another agent has
    to name it here too: the view reads the run under the agent its
    snapshot names, and a history recorded under a different one raises
    rather than drawing whichever substance the run happens to hold.
    """

    return SimulationHistorySample(
        elapsed_s=elapsed_s,
        substances={
            substance_id: {
                RecordedQuantity.CIRCUIT: circuit,
                RecordedQuantity.ALVEOLAR: alveolar,
                RecordedQuantity.MIXED_VENOUS: venous,
                RecordedQuantity.VESSEL_RICH: vessel_rich,
                RecordedQuantity.MUSCLE: muscle,
                RecordedQuantity.FAT: fat,
            }
        },
    )


def _recorded(
    sample: SimulationHistorySample, quantity: RecordedQuantity, substance_id: str = _DEFAULT_AGENT
) -> float:
    """One compartment's recorded value, addressed the way the chart addresses it."""

    return sample.substances[substance_id][quantity]


def _snapshot(
    is_running: bool = False,
    passes_validation: bool = True,
    history: tuple[SimulationHistorySample, ...] | None = None,
    agent_id: str = "sevoflurane",
    agent_display_name: str = "Sevoflurane",
    max_delivered_concentration_percent: float = 8.0,
    agent_mac_percent: float | None = None,
    agent_mac_awake: MacAwakeReference | None = None,
    control_timeline: tuple[ControlChange, ...] = (),
    failure_reason: str | None = None,
    supported_limit_reason: str | None = None,
) -> SimulationSnapshot:
    """Build a snapshot for the view, defaulting MAC from the named agent.

    `agent_mac_percent` and `agent_mac_awake` both resolve from the data
    file rather than from a literal so that a test naming an agent cannot
    accidentally pair that agent's concentrations with another agent's MAC,
    or its chart with another agent's MAC-awake band - which is the
    presentation failure the MAC readouts and the reference band have to be
    proof against, and would be a fixture that proved the opposite of what
    it looked like. Pass either explicitly only to test a value the data
    files do not hold.
    """

    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=agent_id),)

    if agent_mac_percent is None:
        agent_mac_percent = load_agent_parameters(agent_id).mac_percent

    if agent_mac_awake is None:
        agent_mac_awake = load_agent_parameters(agent_id).mac_awake

    latest = history[-1]
    # Read under the agent this snapshot names, so a fixture cannot pair one
    # agent's readouts with another agent's recorded run - which is the
    # pairing failure the readouts and the chart both have to be proof
    # against, and would be a fixture proving the opposite of what it looks
    # like.
    compartments = latest.substances[agent_id]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=latest.elapsed_s,
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=max_delivered_concentration_percent,
        agent_mac_percent=agent_mac_percent,
        agent_mac_awake=agent_mac_awake,
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=4.0,
        delivered_concentration_fraction=0.08,
        alveolar_ventilation_l_min=4.0,
        cardiac_output_l_min=5.0,
        circuit_concentration_fraction=compartments[RecordedQuantity.CIRCUIT],
        alveolar_concentration_fraction=compartments[RecordedQuantity.ALVEOLAR],
        mixed_venous_concentration_fraction=compartments[RecordedQuantity.MIXED_VENOUS],
        vessel_rich_partial_pressure_fraction=compartments[RecordedQuantity.VESSEL_RICH],
        muscle_partial_pressure_fraction=compartments[RecordedQuantity.MUSCLE],
        fat_partial_pressure_fraction=compartments[RecordedQuantity.FAT],
        delivered_agent_l=0.012345,
        exhausted_agent_l=0.002345,
        stored_agent_l=0.01,
        unaccounted_agent_l=1.5e-13,
        agent_accounting_absolute_error_l=1.5e-13,
        agent_accounting_passes_validation=passes_validation,
        control_timeline=control_timeline,
        supported_limit_reason=supported_limit_reason,
        failure_reason=failure_reason,
    )


def _fake_controller(
    history: tuple[SimulationHistorySample, ...] | None = None, **snapshot_fields: Any
) -> _FakeController:
    """A fake controller whose snapshot and history come from one run.

    Built together rather than passed separately because the real
    controller answers for the two out of the same recorded run. A fixture
    that let a test hand one run's samples to the chart beside another
    run's snapshot would prove nothing about the boundary they cross, and
    would look exactly like one that did.
    """

    return _FakeController(_snapshot(history=history, **snapshot_fields), history)


def _recording_controller(
    history: tuple[SimulationHistorySample, ...] | None = None, **snapshot_fields: Any
) -> _RecordingController:
    """`_fake_controller`, recording `fail()` instead of running."""

    return _RecordingController(_snapshot(history=history, **snapshot_fields), history)


def _build_view(
    history: tuple[SimulationHistorySample, ...] | None = None, **snapshot_fields: Any
) -> tuple[SimulationView, _FakePage]:
    page = _FakePage()
    view = SimulationView(page=page, controller=_fake_controller(history, **snapshot_fields))
    return view, page


def test_the_shipped_step_is_within_the_maximum_simulation_step() -> None:
    """The interface may not run the model outside its supported domain.

    `SIMULATION_STEP_S` is this module's cadence and
    `MAXIMUM_SIMULATION_STEP_S` is `core/`'s declared control-resolution
    tolerance; they are separate decisions that happen to coincide today, and
    this is what stops them from parting company unnoticed. Before PL-VP7N the
    only statement
    of the supported step lived here in the presentation layer and bound
    nothing, so any other caller of `core/` - a headless run, a notebook, a
    test - could step as coarsely as it liked and be given a number.

    The relation is `<=` rather than equality on purpose: a numerical method
    that supported a coarser step would not make a coarser step a good
    render cadence, so the interface must be free to run finer than the
    limit without this test having to be rewritten.
    """

    assert SIMULATION_STEP_S <= MAXIMUM_SIMULATION_STEP_S


def test_the_sliders_span_the_supported_input_ranges() -> None:
    """The interface offers exactly the domain the model declares.

    Equality in both directions, and each half fails for its own reason. A
    slider reaching past a supported maximum would hand the user a setting
    `core/` refuses, which is a control that raises when dragged to its own
    end. A slider stopping short would silently narrow the reachable domain,
    which is how the retired splitting-error bound came to be measured over
    less than the interface could produce (PL-042). The same hazard applies to
    the reference gates that replaced it: they are driven at the corner these
    constants declare, so a slider reaching past one would be a setting no gate
    has ever measured.

    Read off the constructed controls rather than the module constants, so a
    literal typed into a slider fails here rather than passing because the
    constant beside it is still correct.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=SimulationController())

    assert (
        view._fresh_gas_flow_slider.min,
        view._fresh_gas_flow_slider.max,
        view._alveolar_ventilation_slider.min,
        view._alveolar_ventilation_slider.max,
        view._cardiac_output_slider.min,
        view._cardiac_output_slider.max,
    ) == (
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )


def test_every_slider_endpoint_is_a_setting_the_core_accepts() -> None:
    """Dragging a slider to either end must never raise out of `core/`.

    The check above compares numbers; this one drives the real controller
    through the same callbacks the interface uses, so a slider whose end the
    model refuses fails as the user would meet it rather than as a mismatched
    constant. The delivered-concentration dial is included because its
    maximum is the agent's own vaporizer limit, which is instance state and
    so cannot be compared against a constant at all.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=SimulationController())

    sliders = (
        (view._fresh_gas_flow_slider, view._handle_fresh_gas_flow_change),
        (view._alveolar_ventilation_slider, view._handle_alveolar_ventilation_change),
        (view._cardiac_output_slider, view._handle_cardiac_output_change),
        (view._delivered_concentration_slider, view._handle_delivered_concentration_change),
    )

    for slider, handle_change in sliders:
        for endpoint in (slider.min, slider.max):
            slider.value = endpoint
            handle_change(ft.Event(name="change", control=slider))

            assert view._rejected_setting_notice is None, (
                f"the core refused {endpoint}, an endpoint of a slider the "
                f"interface offers: {view._rejected_setting_notice}"
            )


def _advance_to(controller: SimulationController, elapsed_s: float) -> None:
    """Step a started controller to `elapsed_s` at the shipped step size."""

    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)


def test_a_real_run_displays_a_filling_compartment_as_below_resolution() -> None:
    """End to end: real model, real step, real units, displayed string.

    Not a fabricated snapshot. This drives the shipped controller with the
    shipped step and reads what the dashboard would actually show, which is
    the path `CLAUDE.md` requires be tested end to end — inputs, model,
    units, formatting, displayed value.

    Fat is the compartment the PL-040 decision turns on. Two minutes into a
    1 MAC sevoflurane run it holds agent but less than 0.01% of it, so the
    display must say so rather than round it to an empty compartment; by an
    hour it has risen into the resolved range and reads as an ordinary
    value.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    _advance_to(controller, 120.0)
    view._refresh_view()

    assert controller.snapshot().fat_partial_pressure_fraction > 0.0
    assert view._fat_concentration_text.value == "<0.01%"

    # The alveolar reading over the same interval is an ordinary value at
    # the documented resolution, so the marker is specific to what is
    # genuinely below it rather than a formatting quirk.
    assert view._alveolar_concentration_text.value == "0.61%"

    _advance_to(controller, 1_200.0)
    view._refresh_view()

    assert view._fat_concentration_text.value == "0.01%"


def test_slider_drag_labels_match_the_readouts_beside_them() -> None:
    """One quantity must not be displayed at two resolutions at once.

    Flet rounds a slider's drag label to whole numbers unless `round` says
    otherwise, so an unset `round` would show "2%" on a dial the readout
    reports as "2.40%", and "4 L/min" on a flow the text beside it reports
    as "4.5 L/min". A reader has no way to tell which of the two is the
    setting actually in force.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=SimulationController())

    assert view._delivered_concentration_slider.round == CONCENTRATION_DISPLAY_DECIMALS
    assert view._delivered_concentration_slider.label == "{value}%"

    for slider in (
        view._fresh_gas_flow_slider,
        view._alveolar_ventilation_slider,
        view._cardiac_output_slider,
    ):
        assert slider.round == FLOW_DISPLAY_DECIMALS
        assert slider.label == "{value} L/min"

    # The flow readouts these labels must agree with.
    assert view._fresh_gas_flow_text.value == "4.0 L/min"
    assert view._alveolar_ventilation_text.value == "4.0 L/min"
    assert view._cardiac_output_text.value == "5.0 L/min"


def test_metric_placeholders_match_the_formatter_before_a_run() -> None:
    """The pre-run reading must not outlive a change to the resolution."""

    page = _FakePage()
    view = SimulationView(page=page, controller=SimulationController())

    empty = format_percent(0.0)
    for text in (
        view._circuit_concentration_text,
        view._alveolar_concentration_text,
        view._mixed_venous_concentration_text,
        view._vessel_rich_concentration_text,
        view._muscle_concentration_text,
        view._fat_concentration_text,
    ):
        assert text.value == empty


# The exact two strings the alveolar readout must carry, restated here rather
# than imported from `simulation_view.py`. An import would move both sides of
# the assertion together, which is precisely the edit these tests exist to
# catch: `docs/MODEL.md` requires "alveolar or end-tidal-equivalent
# concentration", and the hedge is the requirement rather than decoration.
_ALVEOLAR_METRIC_NAME = "Alveolar"
_ALVEOLAR_METRIC_QUALIFIER = "end-tidal-equivalent"

# Any spelling of the measurement's name that is not the hedged form. The
# lookahead is what distinguishes the two: "end-tidal-equivalent" is the
# required gloss, "end-tidal" on its own is the claim MODEL.md forbids.
_UNHEDGED_END_TIDAL = re.compile(r"end[\s-]?tidal(?!-equivalent)", re.IGNORECASE)


def _metric_labels_above(view: SimulationView, value_text: ft.Text) -> tuple[ft.Text, ft.Text]:
    """Return the name and qualifier controls the grid draws above `value_text`.

    Reads the assembled grid rather than a constant, so the pairing of a label
    with the reading underneath it is part of what gets asserted: the right
    number under the wrong label is the presentation-safety failure
    `CLAUDE.md` names, and it would survive any assertion made on the label
    strings alone.
    """

    for panel in view._build_concentration_metrics().controls:
        name_control, qualifier_control, panel_value_text, _mac_text = panel.content.controls
        if panel_value_text is value_text:
            return name_control, qualifier_control

    raise AssertionError("no metric panel in the grid displays that value control")


def _mounted_interface_strings(view: SimulationView, page: _FakePage) -> set[str]:
    """Return every string reachable in the mounted control tree.

    Flet controls are dataclasses, so the whole assembled interface can be
    walked generically: labels, headings, axis captions, legend entries,
    dropdown options and button text all come back without this helper
    needing to know where any of them live. That is the point — a claim about
    what the interface does *not* say has to be made against all of it, not
    against the handful of controls a test remembered to look at.

    Visited objects are held rather than only their ids, because CPython
    reuses the id of an object it has collected and a reused id would make
    the walk skip a live control.
    """

    view.mount()

    strings: set[str] = set()
    visited: dict[int, object] = {}

    def visit(node: object) -> None:
        if id(node) in visited:
            return
        visited[id(node)] = node

        if isinstance(node, str):
            strings.add(node)
        elif isinstance(node, (list, tuple, set)):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            for item in node.values():
                visit(item)
        elif dataclasses.is_dataclass(node) and not isinstance(node, type):
            for field in dataclasses.fields(node):
                # Flet keeps its bookkeeping (`_values`, `_dirty`, the parent
                # back-reference) in underscored fields; the public ones are
                # the interface.
                if not field.name.startswith("_"):
                    visit(getattr(node, field.name, None))

    visit(page.controls)
    return strings


def test_the_alveolar_readout_is_labelled_end_tidal_equivalent() -> None:
    """The hedge is a safety requirement, not a wording preference.

    `docs/MODEL.md` § "Minimum displayed outputs" requires "alveolar or
    end-tidal-equivalent concentration", and states the reason in terms: the
    phrase "must not imply that airway sampling dynamics, dead space, or
    capnography are modeled". None of them are — dead space, airway sampling
    delay, shunt and V/Q mismatch are all in "Known limitations" — so what
    this readout holds is the gas fraction of one perfectly-mixed alveolar
    compartment, and it is not end-tidal in any patient. End-tidal is the
    name of a measurement; presenting a modeled value under it is the
    modeled-versus-measured confusion `CLAUDE.md` forbids, on the one readout
    a clinician would most readily set beside a real agent monitor.

    Regression test: the interface shipped `"Alveolar / end-tidal"` from
    `74bec83` until PL-NV9W.
    """

    view, _ = _build_view()

    name, qualifier = _metric_labels_above(view, view._alveolar_concentration_text)

    assert name.value == _ALVEOLAR_METRIC_NAME
    assert qualifier.value == _ALVEOLAR_METRIC_QUALIFIER
    # The gloss is the weaker of the two claims and has to read as such: the
    # compartment is what the model computes, the measurement is what a
    # clinician would compare it against. Equal type would offer them as
    # alternative names for one quantity, which is the confusion the split
    # exists to remove.
    assert qualifier.size < name.size


def test_the_header_shows_the_application_name_from_app_metadata() -> None:
    """The page header must name the application, not a copy of its name.

    `app_metadata.APP_DISPLAY_NAME` is the single place the name is declared,
    and `app/main.py` also sets it as the window title. A literal in the view
    would leave those two disagreeing after a rename, in the largest text on
    the screen. This suite has caught the same class of bug once already, in
    the delivered-concentration label that was hardcoded to one agent.

    Asserted against the mounted tree rather than the import, so a header
    rebuilt from a literal fails here even while the import still resolves.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=_fake_controller())

    assert APP_DISPLAY_NAME in _mounted_interface_strings(view, page)


def test_every_readout_reserves_a_qualifier_line_and_an_equal_column() -> None:
    """The row is read across, so no panel may be shaped unlike its neighbours.

    `docs/MODEL.md` § "Displayed precision" says the six concentration
    readouts "sit in one row and are read comparatively" - the reason for
    showing them together is that a reader can see "the circuit lead the
    alveoli lead the tissues". Two things have to hold for that to work, and
    neither is visible in a diff:

    A panel with no clinical gloss still draws the gloss line, so that every
    label block is the same height and every reading sits on one baseline.
    Before PL-8M05 the labels were single strings of unequal length, and the
    ones that wrapped dropped their reading a line below the rest - a
    different set of them at every window width.

    And the widest step of the reflow ladder puts every readout side by side.
    Adding an eighth panel without widening that step would silently break the
    row into two, which is the one arrangement the comparative reading cannot
    survive.
    """

    view, _ = _build_view()

    panels = view._build_concentration_metrics().controls

    for panel in panels:
        name, qualifier, value, second_unit = panel.content.controls
        assert name.value, "a readout with no name"
        assert qualifier.value, "a readout that does not hold its gloss line open"
        assert qualifier.size < name.size
        # The MAC line is under the reading rather than above it, so it holds
        # the *bottom* of every block level for the same reason the gloss
        # holds the top: "Simulated time" has no second unit, and a panel that
        # simply omitted the line would sit shorter than the six beside it and
        # break the shared baseline in the other direction.
        assert second_unit.value, "a readout that does not hold its second-unit line open"
        assert second_unit.size < value.size
        assert panel.col == 1, "a readout given more of the row than its neighbours"

    assert max(METRIC_GRID_COLUMNS.values()) == len(panels)


def test_no_interface_string_drops_the_end_tidal_equivalent_hedge() -> None:
    """The whole interface, not only the metric panel, has to hold the hedge.

    A chart legend entry, an axis caption or a future readout would carry the
    same claim to the same reader, so the assertion is made against every
    string the mounted tree contains rather than against the one control the
    defect was found in.

    If a genuine reference to the measurement or to the clinical technique
    ever belongs in this interface — closed-loop end-tidal control is on the
    roadmap — narrow this test to the readout labels and traces rather than
    deleting it. What must not happen is a *modeled* value acquiring the
    unhedged name again.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=_fake_controller())

    strings = _mounted_interface_strings(view, page)

    assert [text for text in sorted(strings) if _UNHEDGED_END_TIDAL.search(text)] == []

    # Checked after the claim above, not before it: an empty result proves
    # nothing on its own, and a Flet release that changed how a control holds
    # its children would leave the walk finding nothing and the assertion
    # passing vacuously. Ordering them this way also keeps the failure
    # message pointed at the real cause in either case.
    assert _ALVEOLAR_METRIC_QUALIFIER in strings, (
        "the control-tree walk did not reach the concentration readouts, "
        "so the assertion above proved nothing"
    )


def test_refresh_view_formats_every_concentration_metric() -> None:
    view, _ = _build_view(
        history=(_sample(12.5, 0.02345, 0.01234, 0.00456, 0.00789, 0.00321, 0.00012),)
    )

    assert view._elapsed_time_text.value == "12.5 s"
    assert view._circuit_concentration_text.value == "2.34%"
    assert view._alveolar_concentration_text.value == "1.23%"
    assert view._mixed_venous_concentration_text.value == "0.46%"
    assert view._vessel_rich_concentration_text.value == "0.79%"
    assert view._muscle_concentration_text.value == "0.32%"
    assert view._fat_concentration_text.value == "0.01%"
    assert view._fresh_gas_flow_text.value == "4.0 L/min"
    assert view._delivered_concentration_text.value == "8.00%"
    assert view._alveolar_ventilation_text.value == "4.0 L/min"
    assert view._cardiac_output_text.value == "5.0 L/min"


@pytest.mark.parametrize(
    ("is_running", "expected_status", "expected_start_disabled", "expected_pause_disabled"),
    [(True, "Running", True, False), (False, "Paused", False, True)],
)
def test_refresh_view_reflects_running_state(
    is_running: bool,
    expected_status: str,
    expected_start_disabled: bool,
    expected_pause_disabled: bool,
) -> None:
    view, _ = _build_view(is_running=is_running)

    assert view._status_text.value == expected_status
    assert view._status_text.color == (ACCENT_TEXT if is_running else MUTED)
    assert view._start_button.disabled is expected_start_disabled
    assert view._pause_button.disabled is expected_pause_disabled


def test_refresh_view_populates_chart_series_from_history() -> None:
    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(0.1, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06),
        _sample(0.2, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12),
    )
    view, _ = _build_view(history=history)

    for series, quantity in (
        (view._circuit_series, RecordedQuantity.CIRCUIT),
        (view._alveolar_series, RecordedQuantity.ALVEOLAR),
        (view._mixed_venous_series, RecordedQuantity.MIXED_VENOUS),
        (view._vessel_rich_series, RecordedQuantity.VESSEL_RICH),
        (view._muscle_series, RecordedQuantity.MUSCLE),
        (view._fat_series, RecordedQuantity.FAT),
    ):
        assert len(series.points) == len(history)

        for point, sample in zip(series.points, history, strict=True):
            assert point.x == pytest.approx(sample.elapsed_s)
            assert point.y == pytest.approx(_recorded(sample, quantity) * 100.0)


def test_refresh_view_reports_valid_agent_accounting() -> None:
    view, _ = _build_view(passes_validation=True)

    assert view._agent_accounting_status_text.value == "Valid"
    assert view._agent_accounting_status_text.color == ACCENT_TEXT
    assert "still accounts for all delivered agent" in (view._agent_accounting_detail_text.value)
    assert view._agent_amounts_text.value == (
        "Delivered: 0.012345 L\n"
        "Exhausted: 0.002345 L\n"
        "Stored: 0.010000 L\n"
        "Unaccounted: 1.500e-13 L\n"
        "Absolute error: 1.500e-13 L"
    )


def test_refresh_view_reports_failed_agent_accounting() -> None:
    view, _ = _build_view(passes_validation=False)

    assert view._agent_accounting_status_text.value == "Validation failed"
    assert view._agent_accounting_status_text.color == WARNING
    assert "unaccounted agent" in view._agent_accounting_detail_text.value


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown() -> None:
    view, _ = _build_view(agent_id="isoflurane", agent_display_name="Isoflurane")
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert view._subtitle_text.value is not None
    assert "Isoflurane" in view._subtitle_text.value
    assert view._agent_dropdown.value == "isoflurane"
    assert view._agent_header_badge.bgcolor == scheme.fill
    assert view._subtitle_text.color == scheme.foreground
    assert view._agent_dropdown.fill_color == scheme.fill
    assert view._agent_dropdown.color == scheme.foreground


def test_agent_dropdown_options_pair_every_color_with_the_agent_name() -> None:
    """Color is a redundant cue, never the only way to identify an agent."""

    view, _ = _build_view()
    expected_names = dict(AVAILABLE_AGENTS)

    assert {option.key for option in view._agent_dropdown.options} == set(expected_names)
    for option in view._agent_dropdown.options:
        assert option.key is not None
        assert option.text == expected_names[option.key]
        assert option.style is not None
        assert option.style.bgcolor == AGENT_COLOR_SCHEMES[option.key].fill
        assert option.style.color == AGENT_COLOR_SCHEMES[option.key].foreground


@pytest.mark.parametrize(
    ("agent_id", "display_name"),
    [("sevoflurane", "Sevoflurane"), ("isoflurane", "Isoflurane"), ("desflurane", "Desflurane")],
)
def test_refresh_view_applies_current_agent_color_to_control_and_header(
    agent_id: str, display_name: str
) -> None:
    view, _ = _build_view(agent_id=agent_id, agent_display_name=display_name)
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert view._agent_dropdown.value == agent_id
    assert view._agent_dropdown.fill_color == scheme.fill
    assert view._agent_dropdown.bgcolor == scheme.fill
    assert view._agent_dropdown.color == scheme.foreground
    assert view._agent_dropdown.text_style is not None
    assert view._agent_dropdown.text_style.color == scheme.foreground
    assert view._agent_header_badge.bgcolor == scheme.fill
    assert view._subtitle_text.color == scheme.foreground
    assert display_name in view._subtitle_text.value


@pytest.mark.parametrize("agent_id", ["sevoflurane", "isoflurane", "desflurane"])
def test_agent_header_badge_is_bordered_against_the_panel(agent_id: str) -> None:
    """Sevoflurane's fill is 1.37:1 on the panel; the edge needs a border."""

    view, _ = _build_view(agent_id=agent_id, agent_display_name=agent_id.title())
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    border = view._agent_header_badge.border
    assert border is not None
    assert border.top is not None
    assert border.top.color == scheme.foreground


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_every_agent_has_render_objects_in_its_own_identification_color(agent_id: str) -> None:
    """An agent added to the color map but not here would raise on selection.

    `AGENT_RENDER_STYLES` is the Flet objects built once from those colors
    (PL-010). Both halves are asserted: that the map covers every agent, and
    that each entry carries that agent's own foreground rather than another
    agent's - ISO 5360 Table 2 footnote b makes a wrong pairing an
    identification error, not a styling one.
    """

    assert set(AGENT_RENDER_STYLES) == set(AGENT_COLOR_SCHEMES)

    scheme = AGENT_COLOR_SCHEMES[agent_id]
    style = AGENT_RENDER_STYLES[agent_id]

    assert style.badge_border.top is not None
    assert style.badge_border.top.color == scheme.foreground
    assert style.dropdown_text_style.color == scheme.foreground


def test_agent_color_render_objects_survive_a_frame_instead_of_being_rebuilt() -> None:
    """PL-010: the render tick assigns the prebuilt objects, unconditionally."""

    view, _ = _build_view(agent_id="isoflurane", agent_display_name="Isoflurane")
    style = AGENT_RENDER_STYLES["isoflurane"]

    assert view._agent_header_badge.border is style.badge_border
    assert view._agent_dropdown.text_style is style.dropdown_text_style

    view._refresh_view()

    assert view._agent_header_badge.border is style.badge_border
    assert view._agent_dropdown.text_style is style.dropdown_text_style


def test_switching_agent_repaints_the_header_badge_and_the_dropdown() -> None:
    """Sharing one prebuilt object per agent must not freeze the selection.

    The reason this is a separate test from the per-agent construction ones
    above: those build a view per agent, so a `_apply_agent_color_scheme`
    that had stopped updating anything would still pass them.
    """

    controller = _fake_controller(agent_id="sevoflurane", agent_display_name="Sevoflurane")
    view = SimulationView(page=_FakePage(), controller=controller)

    controller.switch_agent(
        "desflurane", agent_display_name="Desflurane", max_delivered_concentration_percent=18.0
    )
    view._refresh_view()

    scheme = AGENT_COLOR_SCHEMES["desflurane"]
    style = AGENT_RENDER_STYLES["desflurane"]

    assert view._agent_header_badge.bgcolor == scheme.fill
    assert view._agent_header_badge.border is style.badge_border
    assert view._subtitle_text.color == scheme.foreground
    assert view._subtitle_text.value is not None
    assert "Desflurane" in view._subtitle_text.value

    assert view._agent_dropdown.value == "desflurane"
    assert view._agent_dropdown.fill_color == scheme.fill
    assert view._agent_dropdown.bgcolor == scheme.fill
    assert view._agent_dropdown.color == scheme.foreground
    assert view._agent_dropdown.text_style is style.dropdown_text_style
    assert view._agent_dropdown.border_color == scheme.foreground
    assert view._agent_dropdown.focused_border_color == scheme.foreground


def test_the_slider_tracks_the_dial_maximum_and_the_chart_no_longer_does() -> None:
    """Two ceilings that used to be one, and had to stop being one.

    Real vaporizer caps differ per agent, so the delivered-concentration
    slider must track the dial: it is a control standing for a real
    device, and offering 8% of desflurane would be offering a setting the
    vaporizer does not have.

    The chart's ceiling is a different question and PL-CC23 separated
    them. An axis at the dial maximum is 3.00 MAC of desflurane and 4.17
    of isoflurane, so the same case drawn under two agents was drawn at
    two scales. Desflurane is the agent that makes this test worth
    reading: 3 MAC *is* 18%, so the number below is unchanged and the
    reason for it is not - which is exactly the coincidence that would
    let the old rule creep back unnoticed. Isoflurane is asserted beside
    it because there the two ceilings visibly part company.
    """

    view, _ = _build_view(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert view._delivered_concentration_slider.max == 18.0
    assert view._concentration_chart.max_y == pytest.approx(18.0)
    assert view._concentration_chart.max_y == pytest.approx(CHART_AXIS_TOP_MAC * 6.0)

    view, _ = _build_view(
        agent_id="isoflurane",
        agent_display_name="Isoflurane",
        max_delivered_concentration_percent=5.0,
    )

    assert view._delivered_concentration_slider.max == 5.0
    assert view._concentration_chart.max_y == pytest.approx(3.6), "1.2% MAC x 3, not the 5% dial"


def test_the_axis_top_is_the_same_mac_multiple_for_every_agent() -> None:
    """The property the whole item exists for: one ruler, three agents.

    Read as a *multiple of the running agent's 1 MAC*, the chart's ceiling
    must be identical whichever agent is selected - that is what makes a
    desflurane wash-in and a sevoflurane wash-in the same shape when they
    are the same case. Before PL-CC23 the three spans were 3.00, 4.00 and
    4.17 MAC, a 1.39x silent rescale between the extremes.

    Asserted against the shipped agent files rather than against inlined
    numbers, so a new agent joins this guarantee by existing. The
    gridlines are checked in the same pass because a ruler is its
    ceiling *and* its spacing: rules at whole percentages would land on
    0.33 MAC intervals for desflurane, and a reader looks for MAC.
    """

    spans_mac: set[float] = set()
    intervals_mac: set[float] = set()

    for agent_id in ("sevoflurane", "isoflurane", "desflurane"):
        mac_percent = load_agent_parameters(agent_id).mac_percent
        view, _ = _build_view(agent_id=agent_id, agent_display_name=agent_id.title())

        spans_mac.add(round(view._concentration_chart.max_y / mac_percent, 6))
        intervals_mac.add(
            round(view._concentration_chart.horizontal_grid_lines.interval / mac_percent, 6)
        )

        # Every agent's axis carries the identical ladder of MAC labels,
        # which is the reader-facing half of the same guarantee.
        assert [label.label.value for label in view._mac_axis.labels] == [
            "0.0",
            "0.5",
            "1.0",
            "1.5",
            "2.0",
            "2.5",
            "3.0",
        ]

    assert spans_mac == {CHART_AXIS_TOP_MAC}
    assert intervals_mac == {CHART_GRID_INTERVAL_MAC}


def test_refresh_view_disables_agent_dropdown_while_running() -> None:
    view, _ = _build_view(is_running=True)

    assert view._agent_dropdown.disabled is True


@pytest.mark.parametrize(
    ("agent_id", "display_name"),
    [("sevoflurane", "Sevoflurane"), ("isoflurane", "Isoflurane"), ("desflurane", "Desflurane")],
)
def test_the_agent_name_stays_legible_while_the_run_disables_the_selector(
    agent_id: str, display_name: str
) -> None:
    """Regression test: the running agent's name went grey on its own fill.

    `disabled` was the whole of what a run did to the selector, and
    Flet/Material paints a disabled label in the theme's disabled-content
    grey - overriding the `color=` and `text_style=` the agent scheme sets
    while leaving the saturated ISO 5360 fill behind it. The name was least
    readable exactly while the agent-specific readouts beside it were live,
    which `CLAUDE.md`'s presentation clause treats as a safety failure and
    not a styling one (PL-61WW).

    What this pins is the property rather than the mechanism: whatever
    carries agent identity during a run is drawn in the declared
    foreground/fill pair - the one `tools/contrast_check.py` measures - and
    is not in a widget state entitled to substitute a colour of its own.
    Every agent is checked because every fill in `AGENT_COLOR_SCHEMES` is
    saturated, so this was never one palette's problem.
    """

    view, _ = _build_view(agent_id=agent_id, agent_display_name=display_name, is_running=True)
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert view._running_agent_display.visible is True
    assert view._running_agent_display.disabled in (False, None)
    assert view._running_agent_display.bgcolor == scheme.fill
    assert view._running_agent_text.value == display_name
    assert view._running_agent_text.color == scheme.foreground
    assert view._running_agent_lock_text.color == scheme.foreground

    # The control that *is* recoloured when disabled carries no identity
    # while the run is going, because it is not on screen.
    assert view._agent_dropdown.visible is False


def test_exactly_one_of_the_selector_and_the_running_agent_display_is_shown() -> None:
    """Both at once would be two agent identities in one header row.

    They would agree today, since one snapshot writes both - but the
    failure mode this interface guards against everywhere is a stale label
    beside a live number, and two controls able to disagree is the shape
    that produces one.
    """

    for is_running in (False, True):
        view, _ = _build_view(is_running=is_running)

        assert view._agent_dropdown.visible is not view._running_agent_display.visible
        assert view._running_agent_display.visible is is_running


def test_the_running_agent_display_says_why_the_selector_is_gone() -> None:
    """A control that vanishes is a mode change, and modes are announced.

    The greyed dropdown read as "unavailable"; the chip that replaced it
    has to read as "this is what is running", with the reason it cannot be
    changed second. The caption says "running" rather than "this case"
    because the selector returns on Pause.
    """

    view, _ = _build_view(agent_id="desflurane", agent_display_name="Desflurane", is_running=True)

    assert view._running_agent_text.value == "Desflurane"
    assert view._running_agent_lock_text.value == RUNNING_AGENT_LOCK_TEXT
    assert view._running_agent_display.width == AGENT_SELECTOR_WIDTH
    assert view._agent_dropdown.width == AGENT_SELECTOR_WIDTH


def test_the_running_agent_display_is_already_correct_before_it_is_shown() -> None:
    """It is coloured and named on every tick, visible or not.

    A chip revealed in the previous agent's colour would be the wrong
    label over the right numbers for as long as one frame, and one frame is
    all a reader glancing up at Start needs.
    """

    view, _ = _build_view(agent_id="isoflurane", agent_display_name="Isoflurane")
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert view._running_agent_display.visible is False
    assert view._running_agent_display.bgcolor == scheme.fill
    assert view._running_agent_display.border == AGENT_RENDER_STYLES["isoflurane"].badge_border
    assert view._running_agent_text.value == "Isoflurane"
    assert view._running_agent_text.color == scheme.foreground


def test_refresh_view_updates_delivered_concentration_label_for_current_agent() -> None:
    """Regression test: this label was found hardcoded to "Delivered
    sevoflurane" during manual browser verification of agent switching,
    left stale even after selecting a different agent."""

    view, _ = _build_view(agent_id="desflurane", agent_display_name="Desflurane")

    assert view._delivered_concentration_label.value == "Delivered desflurane"


def test_start_pause_reset_handlers_drive_the_real_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)

    view._handle_start(ft.Event(name="click", control=view._start_button))

    assert controller.is_running is True
    assert view._status_text.value == "Running"
    assert view._start_button.disabled is True
    assert view._pause_button.disabled is False
    assert page.update_calls == 1

    _advance_to(controller, elapsed_s=1.0)
    view._handle_pause(ft.Event(name="click", control=view._pause_button))

    assert controller.is_running is False
    assert view._status_text.value == "Paused"
    assert page.update_calls == 2

    view._handle_reset(ft.Event(name="click", control=view._reset_button))

    assert controller.snapshot().elapsed_s == 0.0
    assert view._elapsed_time_text.value == "0.0 s"
    assert page.update_calls == 3


def test_agent_dropdown_handler_switches_the_real_controller() -> None:
    """The selector still reaches the controller, on a run with nothing to lose.

    A controller that has never been started holds no elapsed time and no
    recorded input, so this is the path `_handle_agent_change` takes without
    asking. The paths that do ask are below.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._agent_dropdown.value = "desflurane"

    view._handle_agent_change(ft.Event(name="select", control=view._agent_dropdown))

    assert controller.snapshot().agent_id == "desflurane"
    assert view._agent_dropdown.value == "desflurane"
    assert view._subtitle_text.value is not None
    assert "Desflurane" in view._subtitle_text.value
    assert page.dialogs == []


def _paused_run_with_history(elapsed_s: float = 60.0) -> SimulationController:
    """A real, paused run holding both elapsed time and a recorded input.

    Both halves deliberately: `SimulationSnapshot.has_recorded_run` reads
    the two together, and a fixture carrying only one would leave the other
    unexercised by every test built on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, elapsed_s=elapsed_s)
    controller.set_fresh_gas_flow(2.0)
    controller.pause()

    return controller


def _select_agent(
    controller: SimulationController, agent_id: str = "desflurane"
) -> tuple[SimulationView, _FakePage]:
    """Mount a view over a controller and pick an agent from the dropdown."""

    page = _FakePage()
    view = SimulationView(page=page, controller=controller)
    view._agent_dropdown.value = agent_id
    view._handle_agent_change(ft.Event(name="select", control=view._agent_dropdown))

    return view, page


def _click_dialog_action(view: SimulationView, label: str) -> None:
    """Press the open confirmation's button carrying `label`.

    Through the button's own `on_click` rather than by calling the handler,
    so that the wiring is part of what these tests hold: a dialog whose
    destructive button called the declining handler would pass every
    assertion made against the handlers alone.
    """

    dialog = view._new_case_dialog
    assert dialog is not None

    for action in dialog.actions:
        if getattr(action, "content", None) == label:
            handler = action.on_click
            assert handler is not None
            handler(ft.Event(name="click", control=action))
            return

    raise AssertionError(f"the confirmation has no action labelled {label!r}")


def test_a_recorded_run_is_not_discarded_before_the_reader_has_answered() -> None:
    """Selecting an agent must rebuild nothing until it has been confirmed.

    The defect PL-R3KB records: the dropdown called `set_agent` directly, so
    a paused run with forty minutes of history behind it was gone at the
    moment of the click, with no statement that it had happened.
    """

    controller = _paused_run_with_history()
    before = controller.snapshot()
    samples_before = controller.history_window(0.0).sample_count

    view, page = _select_agent(controller)

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert controller.history_window(0.0).sample_count == samples_before
    assert len(page.dialogs) == 1
    assert page.dialogs[0].open is True
    # The selector reads the agent that is actually running, not the one
    # being offered, for as long as the question is open.
    assert view._agent_dropdown.value == before.agent_id


def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched() -> None:
    """Declining costs nothing: the run, its history and the dropdown stand."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    samples_before = controller.history_window(0.0).sample_count

    view, page = _select_agent(controller)
    _click_dialog_action(view, KEEP_CURRENT_CASE_TEMPLATE.format(agent="sevoflurane"))

    after = controller.snapshot()
    assert after.agent_id == "sevoflurane"
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert controller.history_window(0.0).sample_count == samples_before
    assert view._agent_dropdown.value == "sevoflurane"
    assert view._subtitle_text.value is not None
    assert "Sevoflurane" in view._subtitle_text.value
    assert page.dialogs[0].open is False
    assert view._new_case_dialog is None


def test_a_confirmed_agent_change_starts_the_new_case() -> None:
    """Confirming does what the selector used to do on its own."""

    controller = _paused_run_with_history()
    view, page = _select_agent(controller)

    _click_dialog_action(view, START_NEW_CASE_TEMPLATE.format(agent="desflurane"))

    after = controller.snapshot()
    assert after.agent_id == "desflurane"
    assert after.elapsed_s == 0.0
    assert after.control_timeline == ()
    assert controller.history_window(0.0).sample_count == 1
    assert view._agent_dropdown.value == "desflurane"
    assert view._delivered_concentration_label.value == "Delivered desflurane"
    assert page.dialogs[0].open is False


def test_the_dismissal_that_follows_a_confirmed_switch_does_not_undo_it() -> None:
    """Flet reports a dismissal after the button that closed the dialog.

    That report reaches the declining branch, so without the guard in
    `_resolve_new_case` it would run over the case that had just started and
    put the selector back to the agent it had just replaced.
    """

    controller = _paused_run_with_history()
    view, _ = _select_agent(controller)
    _click_dialog_action(view, START_NEW_CASE_TEMPLATE.format(agent="desflurane"))

    view._handle_new_case_dismissed(ft.Event(name="dismiss", control=view._agent_dropdown))

    assert controller.snapshot().agent_id == "desflurane"
    assert view._agent_dropdown.value == "desflurane"


def test_dismissing_the_confirmation_keeps_the_current_case() -> None:
    """A dialog closed by anything but its buttons has chosen nothing."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    view, _ = _select_agent(controller)

    view._handle_new_case_dismissed(ft.Event(name="dismiss", control=view._agent_dropdown))

    assert controller.snapshot().agent_id == before.agent_id
    assert controller.snapshot().elapsed_s == before.elapsed_s
    assert view._agent_dropdown.value == before.agent_id


def test_reselecting_the_running_agent_discards_nothing_and_asks_nothing() -> None:
    """A dropdown opened and closed on the same option reports a selection.

    Which used to destroy the run outright - the same discard, from a gesture
    that changed nothing on screen at all.
    """

    controller = _paused_run_with_history()
    before = controller.snapshot()

    view, page = _select_agent(controller, agent_id="sevoflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert page.dialogs == []
    assert view._new_case_dialog is None


def test_the_confirmation_quotes_the_time_and_the_changes_the_panel_shows() -> None:
    """What is about to be lost is stated in the run's own displayed terms.

    The elapsed time through `format_elapsed`, so the warning and the clock
    cannot read at two resolutions, and the control changes counted as the
    panel beside the chart groups them, so a reader checking one against the
    other finds the same number rather than the raw entries behind it.
    """

    controller = _paused_run_with_history()
    snapshot = controller.snapshot()
    view, _ = _select_agent(controller)

    dialog = view._new_case_dialog
    assert dialog is not None
    content = cast(ft.Column, dialog.content)
    warning = cast(ft.Text, content.controls[1])

    assert warning.value == format_case_discard_warning(
        "Sevoflurane", snapshot.elapsed_s, len(group_adjustments(snapshot.control_timeline))
    )
    assert warning.value is not None
    assert format_elapsed(snapshot.elapsed_s) in warning.value


def test_the_confirmation_names_both_agents_and_what_survives_the_switch() -> None:
    """A reader deciding this needs the agent they are leaving and the one
    they would start, and needs to know that the discard stops at the run."""

    controller = _paused_run_with_history()
    view, _ = _select_agent(controller)

    dialog = view._new_case_dialog
    assert dialog is not None
    title = cast(ft.Text, dialog.title)
    content = cast(ft.Column, dialog.content)
    strings = [cast(ft.Text, control).value for control in content.controls]

    assert title.value == "Start a new desflurane case?"
    assert strings[0] == NEW_CASE_IS_NOT_A_VIEW_TEXT
    assert strings[1] is not None
    assert "sevoflurane" in strings[1]
    assert strings[2] == NEW_CASE_CARRYOVER_TEMPLATE.format(agent="desflurane")
    assert dialog.modal is True


def test_the_confirmations_trailing_action_is_the_one_that_keeps_the_case() -> None:
    """The press a reader makes without reading must not destroy the run.

    A dialog's trailing action is where a default press lands, so the
    declining button holds that position and carries the filled style. This
    pins the arrangement rather than leaving it to whoever next edits the
    action list.
    """

    controller = _paused_run_with_history()
    view, _ = _select_agent(controller)

    dialog = view._new_case_dialog
    assert dialog is not None
    discard, keep = dialog.actions

    assert discard.content == "Discard and start desflurane"
    assert isinstance(discard, ft.OutlinedButton)
    assert keep.content == "Keep the sevoflurane case"
    assert isinstance(keep, ft.FilledButton)


def test_fresh_gas_flow_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._fresh_gas_flow_slider.value = 7.0

    view._handle_fresh_gas_flow_change(ft.Event(name="change", control=view._fresh_gas_flow_slider))

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert view._fresh_gas_flow_text.value == "7.0 L/min"


def test_delivered_concentration_slider_converts_percent_to_fraction() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._delivered_concentration_slider.value = 6.5

    view._handle_delivered_concentration_change(
        ft.Event(name="change", control=view._delivered_concentration_slider)
    )

    assert controller.snapshot().delivered_concentration_fraction == pytest.approx(0.065)
    assert view._delivered_concentration_text.value == "6.50%"


def test_alveolar_ventilation_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._alveolar_ventilation_slider.value = 8.0

    view._handle_alveolar_ventilation_change(
        ft.Event(name="change", control=view._alveolar_ventilation_slider)
    )

    assert controller.snapshot().alveolar_ventilation_l_min == 8.0
    assert view._alveolar_ventilation_text.value == "8.0 L/min"


def test_cardiac_output_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._cardiac_output_slider.value = 6.5

    view._handle_cardiac_output_change(ft.Event(name="change", control=view._cardiac_output_slider))

    assert controller.snapshot().cardiac_output_l_min == 6.5
    assert view._cardiac_output_text.value == "6.5 L/min"


@pytest.mark.parametrize(
    "handler_name",
    [
        "_handle_fresh_gas_flow_change",
        "_handle_delivered_concentration_change",
        "_handle_alveolar_ventilation_change",
        "_handle_cardiac_output_change",
        "_handle_agent_change",
    ],
)
def test_change_handlers_ignore_a_none_value(handler_name: str) -> None:
    """Flet may report a control value of None mid-drag; handlers must be a no-op then."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    before = controller.snapshot()

    unset_slider = ft.Slider(min=0, max=10)
    handler = getattr(view, handler_name)
    handler(ft.Event(name="change", control=unset_slider))

    assert controller.snapshot() == before
    assert page.update_calls == 0


def _run_history(
    sample_count: int, substance_id: str = _DEFAULT_AGENT
) -> tuple[SimulationHistorySample, ...]:
    """A run of `sample_count` samples at the real 0.1 s simulation step."""

    return tuple(
        _sample(
            index * SIMULATION_STEP_S,
            0.08 * (1.0 - 0.5**index),
            0.07 * (1.0 - 0.5**index),
            0.06 * (1.0 - 0.5**index),
            0.05 * (1.0 - 0.5**index),
            0.04 * (1.0 - 0.5**index),
            0.03 * (1.0 - 0.5**index),
            substance_id=substance_id,
        )
        for index in range(sample_count)
    )


def _select_time_base(view: SimulationView, span_s: float) -> None:
    """Choose a chart time base through its own control, as a reader would."""

    view._time_base_dropdown.value = str(span_s)
    view._handle_time_base_change(ft.Event(name="select", control=view._time_base_dropdown))


def _all_series(view: SimulationView) -> tuple[fch.LineChartData, ...]:
    return (
        view._circuit_series,
        view._alveolar_series,
        view._mixed_venous_series,
        view._vessel_rich_series,
        view._muscle_series,
        view._fat_series,
    )


def _drawn_series(view: SimulationView) -> tuple[fch.LineChartData, ...]:
    """Every trace a frame redraws through `chart_series.redraw_points`.

    `_all_series` above is the concentration chart's six. The wash-in pool
    is the rest of what a frame writes points into - filled, or emptied by
    `park_series`, which is the same call with no coordinates - so a test
    making a statement about the render tick rather than about one chart
    has to include it.
    """

    return (*_all_series(view), *view._wash_in_segment_series)


def test_a_frame_never_materializes_the_window_as_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """`PL-D9WD`: nothing on the render path may walk the visible window.

    `HistoryWindow.samples` rebuilds one row per sample in the window, so a
    single use of it anywhere in a frame puts the per-frame cost back in
    proportion to the width shown - which is the whole defect the M4
    aggregate cache was built to remove, and the one a later change is most
    likely to reintroduce, because rows are the obvious shape to reach for.

    Asserted as never rather than as a bound: a frame has no legitimate use
    for a row, since every trace reads one quantity through
    `RunHistory.aggregates` and every readout comes from the snapshot.
    """

    materializations = 0
    build_rows = HistoryWindow.samples.fget
    assert build_rows is not None

    def counted(window: HistoryWindow) -> tuple[SimulationHistorySample, ...]:
        nonlocal materializations
        materializations += 1

        return build_rows(window)

    monkeypatch.setattr(HistoryWindow, "samples", property(counted))

    view, _ = _build_view(history=_run_history(18_000))
    materializations = 0

    view._refresh_view()

    assert materializations == 0


@pytest.mark.parametrize("sample_count", [3_000, 6_000, 18_000])
def test_chart_payload_is_bounded_however_long_the_run(sample_count: int) -> None:
    """The render payload must not grow with the length of the run.

    The budget is in columns and the points follow from it: M4 contributes
    at most its four tuples per column, and two on the monotone stretches a
    real run is mostly made of.
    """

    view, _ = _build_view(history=_run_history(sample_count))

    for series in _all_series(view):
        assert len(series.points) <= 4 * CHART_COLUMN_BUDGET_PER_SERIES


def test_chart_sends_only_samples_inside_the_visible_window() -> None:
    """Sending samples the axis clips is payload the client cannot show.

    On a selected time base the run has outgrown, which is the only way the
    axis clips anything: the default "Fit run" widens the window to the run
    rather than cutting it.
    """

    history = _run_history(12_000)
    view, _ = _build_view(history=history)
    _select_time_base(view, 900.0)

    window_start_s = view._concentration_chart.min_x
    assert window_start_s > 0.0

    for series in _all_series(view):
        assert all(point.x >= window_start_s for point in series.points)


def test_the_chart_asks_the_run_for_exactly_the_window_it_draws() -> None:
    """Asking for less than the axis shows would truncate a trace in silence.

    PL-0VM7 moved the cut from the view to the controller: the view sets
    its axis, then asks the run for the samples at or after that same left
    edge. A request for a later time would draw a run that appeared to
    begin after it did, with nothing on the chart to say so, so the request
    itself is asserted and not only what came back from it.

    The companion to `test_chart_sends_only_samples_inside_the_visible_window`
    above: that one holds that nothing outside the window is drawn, this
    one that nothing inside it is dropped.
    """

    history = _run_history(6_000)
    controller = _fake_controller(history=history)
    view = SimulationView(page=_FakePage(), controller=controller)

    (requested_start_s,) = controller.requested_window_starts
    assert requested_start_s == view._concentration_chart.min_x

    oldest_visible = next(sample for sample in history if sample.elapsed_s >= requested_start_s)

    for series in _all_series(view):
        assert series.points[0].x == pytest.approx(oldest_visible.elapsed_s)


def test_chart_right_edge_matches_the_numeric_readout() -> None:
    """A trace ending before the newest sample would contradict the metrics."""

    history = _run_history(6_000)
    latest = history[-1]
    view, _ = _build_view(history=history)

    for series, quantity in (
        (view._circuit_series, RecordedQuantity.CIRCUIT),
        (view._alveolar_series, RecordedQuantity.ALVEOLAR),
        (view._mixed_venous_series, RecordedQuantity.MIXED_VENOUS),
        (view._vessel_rich_series, RecordedQuantity.VESSEL_RICH),
        (view._muscle_series, RecordedQuantity.MUSCLE),
        (view._fat_series, RecordedQuantity.FAT),
    ):
        assert series.points[-1].x == pytest.approx(latest.elapsed_s)
        assert series.points[-1].y == pytest.approx(_recorded(latest, quantity) * 100.0)

    assert view._circuit_concentration_text.value == format_percent(
        _recorded(latest, RecordedQuantity.CIRCUIT)
    )


def test_chart_traces_stay_bound_to_their_own_compartment() -> None:
    """Each trace must plot its own quantity, decimation notwithstanding."""

    history = _run_history(6_000)
    view, _ = _build_view(history=history)

    # Distinct constant multiples in _run_history make a swapped pairing show
    # up as a trace whose values belong to another compartment.
    for series, quantity in (
        (view._circuit_series, RecordedQuantity.CIRCUIT),
        (view._alveolar_series, RecordedQuantity.ALVEOLAR),
        (view._mixed_venous_series, RecordedQuantity.MIXED_VENOUS),
        (view._vessel_rich_series, RecordedQuantity.VESSEL_RICH),
        (view._muscle_series, RecordedQuantity.MUSCLE),
        (view._fat_series, RecordedQuantity.FAT),
    ):
        by_time = {sample.elapsed_s: _recorded(sample, quantity) for sample in history}

        for point in series.points:
            assert point.y == pytest.approx(by_time[point.x] * 100.0)


def test_a_trace_above_the_fixed_axis_is_reported_rather_than_left_to_look_flat() -> None:
    """The failure mode PL-CC23's fixed ceiling introduces, and its guard.

    The old axis was the agent's dial maximum and so could not be
    exceeded. A ceiling at 3 MAC can be: sevoflurane's 8% dial is
    4.00 MAC and is a common inhalational-induction setting. A
    clipped trace draws as a horizontal line at the top of the plot, and
    a horizontal line reads as a plateau — so a reader would conclude the
    concentration stopped rising at 3 MAC when the model says it did not.
    That is a wrong clinical reading of a correct model, which is why the
    plot says so rather than relying on the reader noticing.
    """

    # 8% circuit is 4 MAC of sevoflurane, against a 6% (3 MAC) ceiling.
    # Alveolar at 5% stays inside it, which is what makes this a test of
    # *which* compartments are named rather than only that something was.
    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.05, 0.01, 0.01, 0.0, 0.0),
    )
    view, _ = _build_view(agent_id="sevoflurane", agent_display_name="Sevoflurane", history=history)

    assert view._off_scale_text.visible is True
    assert "Circuit" in view._off_scale_text.value
    assert "Alveolar" not in view._off_scale_text.value
    # The notice has to say where the unclipped number is, or it reports a
    # problem and leaves the reader without the value.
    assert "readouts above" in view._off_scale_text.value
    assert "3.00 \u00d7MAC" in view._off_scale_text.value


def test_the_off_scale_notice_stays_silent_for_a_run_inside_the_axis() -> None:
    """An advisory that fires on an ordinary run is one nobody reads.

    A 1 MAC maintenance case is the common case and sits at a third of
    the plot height, nowhere near the ceiling.
    """

    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )
    view, _ = _build_view(agent_id="sevoflurane", agent_display_name="Sevoflurane", history=history)

    assert view._off_scale_text.visible is False
    assert view._off_scale_text.value == ""


def test_a_trace_exactly_at_the_ceiling_is_not_reported_off_scale() -> None:
    """Isoflurane is where a naive comparison would report noise as a defect.

    Its ceiling is 3 x 1.2%, which in binary floating point is
    3.5999999999999996 rather than 3.6 — so a trace sitting exactly at
    3 MAC is arithmetically *above* the axis by 4e-16. Comparing against
    the displayed resolution rather than against zero is what stops the
    notice firing on a run that reaches the ceiling and no further, and a
    notice that fires on an in-range run is one a reader learns to ignore
    before the induction that needed it.
    """

    at_ceiling = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
        _sample(1.0, 0.036, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
    )
    view, _ = _build_view(
        agent_id="isoflurane", agent_display_name="Isoflurane", history=at_ceiling
    )

    assert view._off_scale_text.visible is False

    # ...and the tolerance is not so wide that it swallows a real excursion:
    # 3.62% clears the ceiling by more than the readouts can resolve.
    above_ceiling = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
        _sample(1.0, 0.0362, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
    )
    view, _ = _build_view(
        agent_id="isoflurane", agent_display_name="Isoflurane", history=above_ceiling
    )

    assert view._off_scale_text.visible is True


def test_a_hidden_trace_is_not_named_as_off_scale() -> None:
    """A hidden series keeps the points of the frame it was last drawn in.

    So a notice read from the series table without the visibility filter
    would name a compartment the reader has taken off the chart and
    cannot see — pointing at a trace that is not there.
    """

    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0),
    )
    view, _ = _build_view(agent_id="sevoflurane", agent_display_name="Sevoflurane", history=history)

    assert view._off_scale_text.visible is True

    _set_trace_shown(view, RecordedQuantity.CIRCUIT, False)
    view._refresh_view()

    assert view._off_scale_text.visible is False


def _set_trace_shown(view: SimulationView, quantity: RecordedQuantity, shown: bool) -> None:
    """Click one compartment's checkbox, the way a reader would.

    Through the control's own `on_change` rather than through the view's
    handler, so the wiring between a box and the trace it stands for is part
    of what every test below asserts. A closure bound to the wrong trace is
    exactly the kind of mistake that would leave every other assertion here
    passing.
    """

    trace = view._trace(quantity)
    trace.checkbox.value = shown
    handler = trace.checkbox.on_change
    assert handler is not None
    handler(ft.Event(name="change", control=trace.checkbox))


def test_chart_traces_stay_bound_to_their_own_compartment_when_some_are_hidden() -> None:
    """The pairing has to survive the filter, which is what could break it.

    Filtering is exactly the operation that could misalign the table: over
    two parallel sequences - the series in one, the quantities in another -
    a filter applied to one and not the other would draw one compartment's
    values on another compartment's line, and every drawn point would still
    be a real recorded sample. `_CompartmentTrace` carries the pair as one
    object so that cannot happen, and this is what holds it.
    """

    history = _run_history(6_000)
    view, _ = _build_view(history=history)

    for hidden in (RecordedQuantity.CIRCUIT, RecordedQuantity.MUSCLE):
        _set_trace_shown(view, hidden, False)

    for quantity in (
        RecordedQuantity.ALVEOLAR,
        RecordedQuantity.MIXED_VENOUS,
        RecordedQuantity.VESSEL_RICH,
        RecordedQuantity.FAT,
    ):
        series = view._trace(quantity).series
        by_time = {sample.elapsed_s: _recorded(sample, quantity) for sample in history}

        assert series.points

        for point in series.points:
            assert point.y == pytest.approx(by_time[point.x] * 100.0)

    # The pairing itself is unchanged: what a trace draws does not depend on
    # whether the reader is currently looking at it.
    assert len(view._plotted_series(_DEFAULT_AGENT)) == len(view._compartment_traces)
    assert len(view._visible_plotted_series(_DEFAULT_AGENT)) == 4


def test_a_hidden_trace_is_not_drawn_rather_than_drawn_empty() -> None:
    """Removed, not emptied: an empty series is one the client still holds.

    That is the render-cost half of this control - what reaches the client
    each frame is about two patch operations per drawn point whose chosen
    sample moved (`PL-Q197`), so cost is linear in the traces drawn - and it
    is also what stops a trace that is no longer redrawn from sitting on the
    chart showing the frame it was last drawn in.
    """

    view, _ = _build_view(history=_run_history(600))
    fat = view._trace(RecordedQuantity.FAT)

    assert fat.series in view._concentration_chart.data_series

    _set_trace_shown(view, RecordedQuantity.FAT, False)

    assert fat.series not in view._concentration_chart.data_series
    assert fat.plotted(_DEFAULT_AGENT) not in view._visible_plotted_series(_DEFAULT_AGENT)

    # Nothing else moved: the other five traces, both references and every
    # control mark are still on the chart.
    for trace in view._compartment_traces:
        if trace is not fat:
            assert trace.series in view._concentration_chart.data_series

    for furniture in (
        view._mac_awake_band_upper_edge,
        view._mac_awake_band_lower_edge,
        view._one_mac_line_series,
        *view._control_mark_series,
    ):
        assert furniture in view._concentration_chart.data_series


def test_the_drawing_order_survives_a_trace_being_hidden() -> None:
    """Rebuilding the series list must not reorder what is left of it.

    Marks are drawn before the references and the references before every
    trace, so no annotation can obscure the run it annotates. That ordering
    is a property of `_chart_data_series`, and hiding a trace is what makes
    it rebuild.
    """

    view, _ = _build_view(history=_run_history(600))
    _set_trace_shown(view, RecordedQuantity.CIRCUIT, False)

    order = view._concentration_chart.data_series
    drawn = [series for series, _ in view._visible_plotted_series(_DEFAULT_AGENT)]

    assert len(drawn) == 5

    references = (
        view._mac_awake_band_upper_edge,
        view._mac_awake_band_lower_edge,
        view._one_mac_line_series,
    )

    for mark in view._control_mark_series:
        assert order.index(mark) < min(order.index(each) for each in references)

    for reference in references:
        assert order.index(reference) < min(order.index(each) for each in drawn)


def test_a_hidden_trace_stops_being_redrawn_and_is_current_again_when_shown() -> None:
    """Hidden costs nothing per frame; shown again is never a stale curve.

    A trace left out of `redraw_visible_window` keeps the points of the
    frame it was last drawn in - that is what makes hiding one free, and it
    is why it must also come off the chart. What must never reach a reader
    is those points: `_handle_trace_visibility_change` redraws before it
    puts the trace back, so a trace returning to the plot is already
    current with the readouts beside it.
    """

    controller = _fake_controller(_run_history(200))
    view = SimulationView(page=_FakePage(), controller=controller)
    fat = view._trace(RecordedQuantity.FAT)

    _set_trace_shown(view, RecordedQuantity.FAT, False)
    frozen = [(point.x, point.y) for point in fat.series.points]

    later = _run_history(400)
    controller.advance_to(later)
    view._refresh_view()

    # The run moved on and this trace did not - and nothing on screen is
    # showing these points, because the series is off the chart.
    assert [(point.x, point.y) for point in fat.series.points] == frozen
    assert view._alveolar_series.points[-1].x == pytest.approx(later[-1].elapsed_s)

    _set_trace_shown(view, RecordedQuantity.FAT, True)

    assert fat.series in view._concentration_chart.data_series
    assert fat.series.points[-1].x == pytest.approx(later[-1].elapsed_s)
    assert fat.series.points[-1].y == pytest.approx(
        _recorded(later[-1], RecordedQuantity.FAT) * 100.0
    )


def test_the_legend_says_exactly_which_traces_are_drawn() -> None:
    """A legend naming a line the chart is not drawing misstates the run.

    The entry is the control, so there is no second list of six to fall out
    of step - and this holds the three channels an entry carries against the
    chart's own series list: the box, the swatch, and the label's weight.
    """

    view, _ = _build_view(history=_run_history(600))
    _set_trace_shown(view, RecordedQuantity.MUSCLE, False)
    _set_trace_shown(view, RecordedQuantity.MIXED_VENOUS, False)

    drawn = view._concentration_chart.data_series

    for trace in view._compartment_traces:
        on_chart = trace.series in drawn

        assert trace.visible is on_chart
        assert trace.checkbox.value is on_chart
        assert trace.swatch.bgcolor == (trace.color if on_chart else None)
        assert trace.checkbox.label_style is not None
        assert trace.checkbox.label_style.color == (INK if on_chart else MUTED)
        # A hidden compartment is still named, so the box that brings it
        # back is findable - and its concentration is in the readouts
        # whether or not its curve is on the plot.
        assert trace.checkbox.label is not None
        assert trace.label in trace.checkbox.label


def test_no_two_chart_traces_are_separated_by_colour_alone() -> None:
    """PL-GVXP. Circuit and vessel-rich were both solid, and are the same weight.

    Colour cannot carry this on its own and no palette makes it: holding each
    trace to 3:1 against the panel caps its luminance, and six traces under
    that cap cannot be more than about 1.48 apart pairwise, against SC
    1.4.11's 3:1. `tools/contrast_check.py` measures the palette; what is
    asserted here is the channel that does the separating, which is the dash
    pattern - and it separates nothing for a pair that shares one.

    Both halves are checked because they fail apart: two traces could carry
    distinct patterns while the legend called them the same thing, which
    leaves a reader matching a word to the wrong curve.
    """

    view, _ = _build_view()
    traces = view._compartment_traces

    assert len(traces) == 6
    patterns = [
        tuple(trace.series.dash_pattern) if trace.series.dash_pattern else None for trace in traces
    ]
    assert len(set(patterns)) == len(traces), f"a dash pattern is drawn twice: {patterns}"
    styles = [trace.line_style for trace in traces]
    assert len(set(styles)) == len(traces), f"a legend style word is claimed twice: {styles}"


def test_every_trace_legend_entry_names_the_pattern_it_is_drawn_with() -> None:
    """The words are the redundant channel, so a wrong word is the whole defect.

    The pattern a reader is told to look for has to be the one on the plot.
    Held as a mapping in both directions: one word may not name two patterns,
    and the solid trace - the only one with no dash pattern at all - has to be
    the one the legend calls solid.
    """

    view, _ = _build_view()
    by_style = {}

    for trace in view._compartment_traces:
        assert trace.checkbox.label is not None
        assert f"({trace.line_style})" in trace.checkbox.label
        pattern = tuple(trace.series.dash_pattern) if trace.series.dash_pattern else None
        assert by_style.setdefault(trace.line_style, pattern) == pattern

    assert by_style["solid"] is None
    assert [style for style, pattern in by_style.items() if pattern is None] == ["solid"]


def test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line() -> None:
    """The reference line must not read as a seventh compartment.

    `ONE_MAC_LINE_DASH_PATTERN`'s comment claims it is wider than every
    trace's dashes, and PL-GVXP added a pattern with a wider *gap* than any
    that comment was written against. Both halves are asserted, because a
    dash is found by its mark and its gap together.
    """

    view, _ = _build_view()
    mark, gap = ONE_MAC_LINE_DASH_PATTERN

    for trace in view._compartment_traces:
        pattern = trace.series.dash_pattern
        if pattern is None:
            continue
        assert max(pattern[::2]) < mark, f"{trace.label} has a mark as long as the 1 MAC line"
        assert max(pattern[1::2]) < gap, f"{trace.label} has a gap as wide as the 1 MAC line"


def test_the_chart_says_so_when_no_compartment_is_drawn() -> None:
    """A blank plot reads as a display that has failed, not as an empty view."""

    view, page = _build_view(history=_run_history(600))

    assert view._hidden_traces_text.visible is False
    # In the assembled panel whether or not it is currently shown, so the
    # line exists to be revealed rather than being built on demand.
    assert NO_TRACES_SHOWN_TEXT in _mounted_interface_strings(view, page)

    for trace in view._compartment_traces:
        _set_trace_shown(view, trace.quantity, False)

    assert view._visible_plotted_series(_DEFAULT_AGENT) == ()
    assert view._hidden_traces_text.visible is True

    _set_trace_shown(view, RecordedQuantity.ALVEOLAR, True)

    assert view._hidden_traces_text.visible is False


def test_hiding_a_trace_changes_only_what_is_drawn() -> None:
    """Every compartment's value stays on the display, and so does the run.

    `docs/MODEL.md`'s minimum displayed outputs require all six
    concentrations, and they are the readouts rather than the traces - so a
    reader looking at two curves is looking at a chosen view of six modelled
    compartments and not at a model with two. Hiding one also leaves the
    rest of the frame untouched, which is what makes this a choice about
    what is drawn rather than about what is computed.
    """

    history = _run_history(600)
    view, _ = _build_view(history=history)
    before = {
        trace.quantity: [(point.x, point.y) for point in trace.series.points]
        for trace in view._compartment_traces
    }

    _set_trace_shown(view, RecordedQuantity.FAT, False)

    for trace in view._compartment_traces:
        if trace.quantity is not RecordedQuantity.FAT:
            assert [(point.x, point.y) for point in trace.series.points] == before[trace.quantity]

    latest = history[-1]

    for text, quantity in (
        (view._circuit_concentration_text, RecordedQuantity.CIRCUIT),
        (view._muscle_concentration_text, RecordedQuantity.MUSCLE),
        (view._fat_concentration_text, RecordedQuantity.FAT),
    ):
        assert text.value == format_percent(_recorded(latest, quantity))


def test_every_compartment_has_exactly_one_trace() -> None:
    """The table is the whole pairing, so a missing entry is a lost compartment."""

    view, _ = _build_view()

    assert {trace.quantity for trace in view._compartment_traces} == {
        RecordedQuantity.CIRCUIT,
        RecordedQuantity.ALVEOLAR,
        RecordedQuantity.MIXED_VENOUS,
        RecordedQuantity.VESSEL_RICH,
        RecordedQuantity.MUSCLE,
        RecordedQuantity.FAT,
    }

    with pytest.raises(KeyError):
        view._trace(RecordedQuantity.WASH_IN_RATIO)


def test_chart_keeps_every_sample_of_a_short_run() -> None:
    """Decimation must not kick in before the budget is actually exceeded."""

    history = _run_history(50)
    view, _ = _build_view(history=history)

    for series in _all_series(view):
        assert len(series.points) == len(history)


def test_the_chart_defaults_to_fitting_the_whole_run() -> None:
    """ "Fit run" is the default, so a learner sees the complete curve first.

    `PL-012`'s requirement, and the reason it is a default rather than an
    option: the wash-in curve is the lesson, and it is unreachable if the
    reader has to discover a control before the run scrolls past it.
    """

    view, _ = _build_view(history=_run_history(12_000))

    assert view._time_base_dropdown.value == FIT_RUN_KEY
    assert view._concentration_chart.min_x == 0.0
    assert view._concentration_chart.max_x >= 1_199.9


def test_the_time_base_selector_offers_fit_run_and_the_settled_widths() -> None:
    """The options are the ladder, which is what lets a bad key be a defect.

    `_handle_time_base_change` raises on a width `TIME_BASE_LADDER` does not
    carry rather than falling back to a nearby one, and that is only safe
    while the control cannot offer one.
    """

    view, _ = _build_view()
    options = view._time_base_dropdown.options

    assert [option.key for option in options] == [
        FIT_RUN_KEY,
        *(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]
    assert [option.text for option in options] == [
        "Fit run",
        *(format_time_base(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]


def test_selecting_a_time_base_makes_the_window_exactly_that_wide() -> None:
    """The selected duration is the width of the visible window.

    Held exactly, at every width the selector offers, so seconds-per-pixel
    is a property of the choice rather than of how far the run has got.
    """

    view, _ = _build_view(history=_run_history(12_000))

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, time_base.span_s)

        assert view._concentration_chart.max_x - view._concentration_chart.min_x == pytest.approx(
            time_base.span_s
        )


def test_a_run_shorter_than_the_selected_time_base_shows_whole() -> None:
    """`PL-SSBP`'s "Done when", and the axis does not shrink to fit it either.

    A window that shrank to the samples recorded so far would rescale
    continuously, which changes every trace's apparent slope while no
    modelled rate moves - the encoding `PL-012` rejected. So the run is
    drawn whole *and* against the full width that was chosen.
    """

    view, _ = _build_view(history=_run_history(3_000))
    _select_time_base(view, 900.0)

    assert view._concentration_chart.min_x == 0.0
    assert view._concentration_chart.max_x == 900.0

    for series in _all_series(view):
        assert series.points[0].x == pytest.approx(0.0)


def test_the_gridline_interval_is_derived_from_the_time_base() -> None:
    """`PL-012`: derived, never fixed.

    The 60 s interval this replaced would rule a twelve-hour axis into 720
    lines and a solid block. Both plots are checked because they share one
    window, so a fixed interval left on either would rule the same span two
    different ways.
    """

    view, _ = _build_view(history=_run_history(12_000))

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, time_base.span_s)

        assert view._concentration_chart.vertical_grid_lines.interval == time_base.tick_interval_s
        assert view._wash_in_chart.vertical_grid_lines.interval == time_base.tick_interval_s


def test_the_time_axis_is_labelled_in_units_rather_than_in_bare_seconds() -> None:
    """A bare number would mean seconds on one time base and hours on another.

    The two look identical, so a reader who misses the caption has nothing
    in the label to correct them. `format_chart_time_label` puts the unit on
    every tick, and this is what holds the axis to it.
    """

    view, _ = _build_view(history=_run_history(12_000))
    _select_time_base(view, 3_600.0)

    labels = view._time_axis.labels

    assert labels, "the time axis is drawing no labels"
    assert [label.label.value for label in labels] == [
        format_chart_time_label(label.value) for label in labels
    ]
    # Every tick stands at a multiple of the interval the chart is ruled at,
    # so a label never falls between two gridlines.
    assert all(
        label.value % view._concentration_chart.vertical_grid_lines.interval == 0
        for label in labels
    )


def test_the_window_s_own_ends_are_labelled_only_when_they_are_ticks() -> None:
    """The origin is worth a label; an arbitrary edge would read as a gridline.

    Under "Fit run" the window is pinned to zero and to a whole number of
    intervals, so both ends are ruled and both are labelled - and the `0` is
    the only label that says where the run starts. Once a chosen width is
    following the run its ends fall wherever the newest sample puts them,
    and a label at `1h58m2s` beside one reading `2h` would be read as a tick
    the chart is not ruled at.
    """

    controller = _fake_controller(history=_run_history(12_000))
    view = SimulationView(page=_FakePage(), controller=controller)

    assert view._concentration_chart.min_x == 0.0
    assert view._time_axis.show_min
    assert view._time_axis.show_max
    assert view._wash_in_time_axis.show_min
    assert view._wash_in_time_axis.show_max

    _select_time_base(view, 900.0)

    assert view._concentration_chart.min_x > 0.0
    assert not view._time_axis.show_min
    assert not view._time_axis.show_max
    assert not view._wash_in_time_axis.show_min
    assert not view._wash_in_time_axis.show_max


def test_both_plots_are_labelled_from_the_same_ticks() -> None:
    """One window, so one set of times - drawn twice because a control has one chart.

    The wash-in plot's caption says "the same window as above", and a
    reader comparing the two curves is reading one against the other. Axes
    that disagreed about where a time falls would break that silently.
    """

    view, _ = _build_view(history=_run_history(12_000))
    _select_time_base(view, 1_800.0)

    assert [label.value for label in view._wash_in_time_axis.labels] == [
        label.value for label in view._time_axis.labels
    ]
    # Distinct controls, not the same objects on two charts: a Flet control
    # belongs to one chart, so sharing them would drop one axis's labels.
    assert all(
        wash_in is not concentration
        for wash_in, concentration in zip(
            view._wash_in_time_axis.labels, view._time_axis.labels, strict=True
        )
    )


def test_the_axis_caption_states_the_span_the_chart_is_showing() -> None:
    """`PL-012` required the caption to name the span actually drawn.

    The width is a mode: the same plot showing fifteen minutes and twelve
    hours is two very different claims about what a flat trace means, and a
    reader who does not know which cannot tell a compartment at equilibrium
    from one that has not started moving.
    """

    view, _ = _build_view(history=_run_history(12_000))
    _select_time_base(view, 7_200.0)

    assert "2 hours shown" in view._time_axis_caption.value
    assert "simulated seconds" not in view._time_axis_caption.value


def test_the_caption_says_when_the_span_was_chosen_by_the_run_rather_than_the_reader() -> None:
    """Under "Fit run" the width is derived, and nothing else on screen says so.

    The selector reads "Fit run", which names the rule; the caption is the
    only place the plot says what the rule came out as.
    """

    view, _ = _build_view(history=_run_history(12_000))

    assert "whole run so far" in view._time_axis_caption.value
    assert (
        f"{format_time_base(view._drawn_time_base.span_s)} shown" in view._time_axis_caption.value
    )

    _select_time_base(view, 43_200.0)

    assert "whole run so far" not in view._time_axis_caption.value


def test_the_wash_in_plot_spans_the_same_window_as_the_chart_above_it() -> None:
    """Its caption claims exactly this, and the two are read against each other."""

    view, _ = _build_view(history=_run_history(12_000))

    for span_s in (None, 900.0, 43_200.0):
        if span_s is not None:
            _select_time_base(view, span_s)

        assert view._wash_in_chart.min_x == view._concentration_chart.min_x
        assert view._wash_in_chart.max_x == view._concentration_chart.max_x


def test_choosing_a_time_base_changes_nothing_the_run_recorded() -> None:
    """It is a view control: it decides what is drawn, never what is modelled.

    The same guarantee the compartment checkboxes carry, and the reason
    `CLAUDE.md`'s determinism requirement is untouched by this control. A
    case watched at fifteen minutes and the same case watched at twelve
    hours are the same run, sample for sample.
    """

    controller = SimulationController()
    view = SimulationView(page=_FakePage(), controller=controller)
    controller.start()

    for _ in range(200):
        controller.advance(SIMULATION_STEP_S)

    def recorded() -> tuple[SimulationHistorySample, ...]:
        return controller.history_window(0.0).samples

    before = recorded()

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, time_base.span_s)

    assert recorded() == before


def test_the_time_base_is_never_disabled() -> None:
    """Widening the window on a run already going is the usual reason to reach for it.

    Unlike the agent dropdown, which is disabled while running because
    choosing an agent discards the case, this reaches no model state and so
    has nothing to protect.
    """

    view, _ = _build_view(is_running=True)

    assert view._agent_dropdown.disabled
    assert not view._time_base_dropdown.disabled


def test_reset_leaves_the_selected_time_base_alone() -> None:
    """A reader setting, like every other: Reset clears the run, not the view.

    A width silently snapping back to "Fit run" would be a mode change
    nobody asked for, in the middle of the comparison the reader reset the
    run to make.
    """

    controller = SimulationController()
    view = SimulationView(page=_FakePage(), controller=controller)
    _select_time_base(view, 1_800.0)

    view._handle_reset(ft.Event(name="click", control=view._reset_button))

    assert view._time_base == time_base_for_span(1_800.0)
    assert view._time_base_dropdown.value == "1800.0"


def test_the_axis_labels_are_rebuilt_only_when_the_ticks_move() -> None:
    """The same guard the MAC axis carries, and for the same cost.

    Ticks stand at absolute multiples of the interval, so a following window
    crosses one every `tick_interval_s` of simulated time rather than every
    frame. Rebuilding them unguarded would allocate a control per tick per
    frame and send the client an add-and-remove of both axes each time -
    the per-frame churn `tests/integration/test_chart_patching.py` measures.
    """

    controller = _fake_controller(history=_run_history(12_000))
    view = SimulationView(page=_FakePage(), controller=controller)
    _select_time_base(view, 900.0)

    held = list(view._time_axis.labels)

    # Ten further steps: one second of simulated time, far inside the three
    # minutes between ticks at this width.
    controller.advance_to(_run_history(12_010))
    view._refresh_view()

    assert view._time_axis.labels is held or list(view._time_axis.labels) == held
    assert all(new is old for new, old in zip(view._time_axis.labels, held, strict=True)), (
        "the axis was relabelled on a frame that crossed no tick"
    )


def test_crossing_a_tick_relabels_the_axis() -> None:
    """The other half of the guard: a stale label is a wrong displayed time."""

    controller = _fake_controller(history=_run_history(12_000))
    view = SimulationView(page=_FakePage(), controller=controller)
    _select_time_base(view, 900.0)

    before = [label.value for label in view._time_axis.labels]

    # Past the next tick: at a 15 minute width the axis is ruled every three
    # minutes, so 200 s of further run moves the window across one.
    controller.advance_to(_run_history(14_000))
    view._refresh_view()

    assert [label.value for label in view._time_axis.labels] != before


def test_fitting_widens_the_axis_in_steps_rather_than_continuously() -> None:
    """`PL-012`: rescale in discrete labelled steps, not with every sample.

    A continuously growing axis is the same misleading encoding as a
    continuously shrinking one - the trace's slope changes while nothing
    the model computes does.
    """

    controller = _fake_controller(history=_run_history(400))
    view = SimulationView(page=_FakePage(), controller=controller)
    widths = []

    for sample_count in range(400, 1_400, 100):
        controller.advance_to(_run_history(sample_count))
        view._refresh_view()
        widths.append(view._concentration_chart.max_x)

    assert set(widths) <= {time_base.span_s for time_base in TIME_BASE_LADDER}
    assert widths == sorted(widths), "a fitted axis narrowed as the run grew"


def test_chart_points_are_recorded_samples_not_interpolations() -> None:
    history = _run_history(6_000)
    recorded_times = {sample.elapsed_s for sample in history}
    view, _ = _build_view(history=history)

    for series in _all_series(view):
        assert all(point.x in recorded_times for point in series.points)
        assert [point.x for point in series.points] == sorted(point.x for point in series.points)


def test_chart_points_are_moved_rather_than_rebuilt_each_frame() -> None:
    """PL-010's saving: a frame moves the points the chart already holds.

    Identity is compared against retained references rather than `id()`,
    which a freed point's replacement could reuse. That a *live client* is
    told about the move - the part this saving is only safe because of - is
    `tests/integration/test_chart_patching.py`'s to prove.
    """

    controller = _fake_controller(history=_run_history(12_000))
    view = SimulationView(page=_FakePage(), controller=controller)
    # A selected time base, so the window slides rather than widening: under
    # "Fit run" a run this length is drawn whole and the older points do not
    # move at all, which would leave the assertion below passing vacuously.
    _select_time_base(view, 900.0)

    held = [list(series.points) for series in _all_series(view)]
    drawn_before = [[(point.x, point.y) for point in points] for points in held]

    # 50 further steps: the window slides, so every drawn time changes.
    controller.advance_to(_run_history(12_050))
    view._refresh_view()

    for series, points_held, before in zip(_all_series(view), held, drawn_before, strict=True):
        assert len(series.points) == len(points_held)
        assert all(new is old for new, old in zip(series.points, points_held, strict=True))
        assert [(point.x, point.y) for point in series.points] != before


def test_refresh_allocates_no_chart_points_when_drawn_count_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`PL-LKCN`: a frame that draws the same number of points builds none.

    This is the property `PL-010` bought, stated as something the ordinary
    suite holds a later change to. `PL-010`'s own evidence was a wall-clock
    figure - 16.6 ms to 2.6 ms at the saturated window - measured with a
    harness written in a scratch directory and thrown away with the session,
    so nothing in the repository could re-measure it. What regressed, and
    what would regress again, is allocation rather than milliseconds; and
    allocation is deterministic, so it cannot flake on a shared runner the
    way a wall-clock ceiling would.

    Stated as a conditional, because the unconditional form is false. The
    drawn count is not fixed frame to frame even at a saturated window: M4
    contributes up to four points per column and two on the monotone
    stretches a real run is mostly made of, so a sliding window crosses
    column boundaries where the total moves by a point or two per trace. A
    frame that grows a trace *must* build the difference. What must never
    happen is building points for a trace whose drawn count is exactly what
    it already was - that is the per-sample rebuild returning by another
    door.

    The history advances every frame, which is not incidental. Flet's
    `Prop.__set__` early-returns when the new value equals the old one, so a
    replay of one fixed snapshot exercises a cheaper write than the running
    app ever performs; `PL-010`'s per-part harness was caught by exactly
    that. A fixed snapshot would also pin the drawn count and leave every
    frame below vacuously unchanged. Both are guarded at the end.

    Companion to `test_chart_points_are_moved_rather_than_rebuilt_each_frame`
    above, which asserts the surviving points are the same objects. That one
    would miss a frame that built points and then discarded them; this one
    counts construction itself, and over every trace the tick redraws rather
    than the concentration chart's six.
    """

    built = 0
    build_point = fch.LineChartDataPoint

    def counted(*args: Any, **kwargs: Any) -> fch.LineChartDataPoint:
        nonlocal built
        built += 1

        return build_point(*args, **kwargs)

    # Patched on the module `chart_series` reads the name from, rather than
    # on one call site, so a construction anywhere on the render path counts.
    monkeypatch.setattr(fch, "LineChartDataPoint", counted)

    controller = _fake_controller(history=_run_history(12_000))
    view = SimulationView(page=_FakePage(), controller=controller)
    # A selected time base, so the window slides at its saturated width
    # rather than widening: under "Fit run" a run this length is drawn whole,
    # the older points never move, and the ceiling this defends is never
    # reached. Building the view fills the traces from one point each, which
    # is a change of drawn count and legitimately allocates - `built` is
    # zeroed per frame below, after all of that.
    _select_time_base(view, 900.0)
    # One render tick's worth of new samples, so the window slides at the
    # rate the running app slides it.
    steps_per_render_tick = round(RENDER_INTERVAL_S / SIMULATION_STEP_S)

    def drawn_counts() -> tuple[int, ...]:
        return tuple(len(series.points) for series in _drawn_series(view))

    def drawn_coordinates() -> list[list[tuple[float, float]]]:
        return [[(point.x, point.y) for point in series.points] for series in _drawn_series(view)]

    frames = 60
    frames_at_unchanged_count = 0
    frames_that_moved = 0
    previous_counts = drawn_counts()
    previous_coordinates = drawn_coordinates()

    for step in range(1, frames + 1):
        controller.advance_to(_run_history(12_000 + step * steps_per_render_tick))
        built = 0
        view._refresh_view()
        counts = drawn_counts()
        coordinates = drawn_coordinates()

        if counts == previous_counts:
            frames_at_unchanged_count += 1
            assert built == 0, (
                f"frame {step} built {built} chart points while drawing the same "
                f"{sum(counts)} across the tick as the frame before it"
            )

        if coordinates != previous_coordinates:
            frames_that_moved += 1

        previous_counts = counts
        previous_coordinates = coordinates

    # Not vacuous: the run has to have produced frames of the kind the
    # assertion applies to, and each has to have been a real redraw rather
    # than a snapshot replayed against itself.
    assert frames_at_unchanged_count > 0, "no frame drew an unchanged count, so nothing was tested"
    assert frames_that_moved == frames, "a frame redrew its own coordinates, so the history stalled"


def _run_briefly(coroutine_function, ticks: int, interval_s: float) -> None:
    """Run a never-ending view loop for roughly `ticks` of its own interval.

    The loops run forever by design, so each is started as a task, given a
    bounded amount of real time to tick, and then cancelled.
    """

    async def drive() -> None:
        task = asyncio.create_task(coroutine_function())
        await asyncio.sleep(interval_s * ticks + interval_s / 2.0)
        task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await task

    asyncio.run(drive())


def test_simulation_loop_advances_without_rendering() -> None:
    """Stepping must not be gated on drawing."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()
    page.update_calls = 0

    _run_briefly(view._run_simulation_timer, ticks=3, interval_s=SIMULATION_STEP_S)

    # How many ticks land in a fixed slice of real time is up to the host, so
    # the claim under test is that stepping happened and drawing did not.
    assert controller.snapshot().elapsed_s > 0.0
    assert page.update_calls == 0


def test_render_loop_draws_without_advancing() -> None:
    """Drawing must not move simulation time."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()
    page.update_calls = 0

    _run_briefly(view._run_render_timer, ticks=2, interval_s=RENDER_INTERVAL_S)

    assert controller.snapshot().elapsed_s == 0.0
    assert page.update_calls >= 1


def test_neither_loop_does_anything_while_paused() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    page.update_calls = 0

    _run_briefly(view._run_simulation_timer, ticks=2, interval_s=SIMULATION_STEP_S)
    _run_briefly(view._run_render_timer, ticks=1, interval_s=RENDER_INTERVAL_S)

    assert controller.snapshot().elapsed_s == 0.0
    assert page.update_calls == 0


def test_simulation_time_does_not_depend_on_render_cadence() -> None:
    """Identical step counts must give identical results, however drawing goes.

    Simulation time is a function of steps taken, never of wall-clock time or
    of how long a frame took, so a slow or skipped redraw cannot perturb the
    trajectory.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    _run_briefly(view._run_simulation_timer, ticks=5, interval_s=SIMULATION_STEP_S)
    stepped_by_the_loop = controller.snapshot()

    reference = SimulationController()
    reference.start()
    steps_taken = len(controller.history_window(0.0).samples) - 1
    assert steps_taken > 0

    for _ in range(steps_taken):
        reference.advance(SIMULATION_STEP_S)

    # Exact rather than approximate: the same steps under the same settings
    # are the same arithmetic, and simulated time is the step count times
    # the step (`PL-VM40`). An approximate match here would pass over
    # precisely the drift this asserts the absence of.
    assert stepped_by_the_loop.elapsed_s == reference.snapshot().elapsed_s
    assert (
        stepped_by_the_loop.alveolar_concentration_fraction
        == reference.snapshot().alveolar_concentration_fraction
    )


def _drive_exact_ticks(view: SimulationView, ticks: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the simulation loop for exactly `ticks` wakeups, with no real time.

    The loop's own `asyncio.sleep` is replaced by a tick that returns at
    once for the first `ticks` wakeups and then parks, so the number of
    steps taken is exact rather than a race between the driver's cancel and
    one more tick. That is what lets a caller assert a step *count*; the
    tests that let real time elapse deliberately claim less, because how
    many ticks land in a slice of real time is up to the host.
    """

    real_sleep = asyncio.sleep
    wakeups = 0

    async def tick(interval_s: float) -> None:
        nonlocal wakeups
        wakeups += 1
        await real_sleep(0.0 if wakeups <= ticks else 3600.0)

    async def drive() -> None:
        task = asyncio.create_task(view._run_simulation_timer())

        for _ in range(ticks * 100):
            if wakeups > ticks:
                break

            await real_sleep(0)

        task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await task

    monkeypatch.setattr(asyncio, "sleep", tick)
    asyncio.run(drive())

    assert wakeups == ticks + 1, "the loop did not wake the expected number of times"


def test_the_run_loop_takes_one_step_per_tick_at_real_time_and_never_catches_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A late tick must cost the run real time, never change its trajectory.

    How many steps a tick takes is the reader's playback setting rather than
    a function of how long the tick took, so a host that wakes it late
    leaves the run behind the wall clock and it stays behind. The
    alternative - stepping until simulated time catches up with elapsed real
    time - would make the number of steps a run takes a property of the
    machine, which is what docs/MODEL.md's reproducibility guarantee
    forbids. At the default rate that setting is one step, which is what
    this asserts; the rate test below asserts the same property across the
    whole ladder.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    ticks = 7
    _drive_exact_ticks(view, ticks, monkeypatch)

    assert controller.snapshot().elapsed_s == ticks * SIMULATION_STEP_S
    assert len(controller.history_window(0.0).samples) == ticks + 1


def test_a_tick_is_one_simulation_step_of_real_time() -> None:
    """The equality every displayed playback rate is derived through.

    A tick advances `steps_per_tick` steps, and calling that "N times real
    time" is true only because one tick is one step long. The two constants
    are separate decisions - one about the model's numerics, one about this
    host's event loop - so re-tuning the wakeup without the step would
    silently falsify every rate on screen rather than failing anywhere.
    """

    assert SIMULATION_TICK_INTERVAL_S == SIMULATION_STEP_S


def test_a_frame_is_two_control_grid_steps_at_every_rate() -> None:
    """The premise of the argument `PL-NBWP` was settled on.

    A tick advances its whole burst uninterrupted, so a setting changed
    while the run plays first acts at a tick boundary; a frame is drawn
    every render interval. Because the render interval is twice the tick,
    a reader sees the run at half the resolution they can act on it at, at
    every rate the ladder offers - and that ordering is the reason
    `docs/MODEL.md` § "Supported simulation step" gives for leaving the
    grid where it is rather than servicing control events inside the burst.

    Held here rather than derived in the module, because a display cadence
    and an event-loop cadence are separate decisions that happen to be in
    this ratio today. Re-tuning the render interval for the display is
    allowed; doing it while `docs/MODEL.md` still argues from the old ratio
    is what this fails on.
    """

    assert RENDER_INTERVAL_S == 2.0 * SIMULATION_TICK_INTERVAL_S


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_run_loop_takes_the_playback_rates_steps_per_tick(
    rate: PlaybackRate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The multiplier is steps per tick, and the step never moves.

    `PL-SN2C`'s safety argument, asserted at every rate the interface
    offers. A multiplier that resized the step would make the same case read
    differently depending on how fast it was watched - the same number
    meaning something different according to a *view* control - so what is
    checked here is both halves at once: how many times `advance` was
    called, and that every one of those calls was handed
    `SIMULATION_STEP_S`.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._playback_rate = rate
    controller.start()

    steps_requested: list[float] = []
    advance = controller.advance

    def recording_advance(simulation_step_s: float) -> None:
        steps_requested.append(simulation_step_s)
        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", recording_advance)

    ticks = 3
    _drive_exact_ticks(view, ticks, monkeypatch)

    steps_per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    expected_steps = ticks * steps_per_tick

    assert steps_per_tick == rate.multiplier
    assert len(steps_requested) == expected_steps
    assert set(steps_requested) == {SIMULATION_STEP_S}
    assert controller.snapshot().elapsed_s == expected_steps * SIMULATION_STEP_S
    assert len(controller.history_window(0.0).samples) == expected_steps + 1


def _panel_under(view: SimulationView, value_text: ft.Text) -> ft.Text:
    """Return the fourth line of the metric panel drawing `value_text`.

    The slot the six compartment panels give to a MAC multiple. Read out of
    the assembled grid rather than off the view, so what is asserted is what
    a reader would see under that particular reading.
    """

    for panel in view._build_concentration_metrics().controls:
        _name, _qualifier, panel_value_text, secondary_text = panel.content.controls
        if panel_value_text is value_text:
            return secondary_text

    raise AssertionError("no metric panel in the grid displays that value control")


def _select_playback_rate(view: SimulationView, multiplier: int) -> None:
    """Drive the dropdown as a user selection would."""

    view._playback_rate_dropdown.value = str(multiplier)
    view._handle_playback_rate_change(
        cast(Any, ft.Event(name="select", control=view._playback_rate_dropdown, data=None))
    )


def test_the_playback_rate_is_drawn_under_the_clock_it_governs() -> None:
    """A rate is a mode, and the clock is where it would be misread.

    A clock advancing at 60x beside numbers that look like a live case is
    misreadable at a glance, so `PL-SN2C` requires the multiplier beside the
    elapsed-time readout - not merely somewhere on the page, and not only
    when it is not 1x. Asserted against the assembled grid so that the
    pairing of the rate with *that* reading is what is held, which an
    assertion on the string alone would not be.
    """

    view, _page = _build_view()

    assert _panel_under(view, view._elapsed_time_text).value == format_playback_rate(
        DEFAULT_PLAYBACK_RATE.multiplier
    )


def test_the_mounted_interface_states_the_playback_rate() -> None:
    """Assembled, not merely constructed: the rate has to reach the page.

    `_panel_under` above reads the metric grid, which a view builds whether
    or not `mount()` puts it on the page. This walks what `mount()` actually
    handed over, so a rate that lives only on a control nothing draws fails
    here.
    """

    view, page = _build_view()

    assert format_playback_rate(DEFAULT_PLAYBACK_RATE.multiplier) in (
        _mounted_interface_strings(view, page)
    )


def test_the_default_playback_rate_is_real_time() -> None:
    """A reader who never touches the control is never in a mode they did not choose."""

    view, _page = _build_view()

    assert view._playback_rate == DEFAULT_PLAYBACK_RATE
    assert view._playback_rate.multiplier == 1


def test_every_supported_playback_rate_is_offered_by_the_control() -> None:
    """The control and the list must not diverge.

    `playback_rate_for` raises rather than defaulting when a multiplier it
    does not know reaches the loop, so an option the list has lost would be
    an exception in a dropdown handler rather than a wrong rate - but an
    option the list has *gained* and the control has not would simply be
    unreachable, which nothing else would show.
    """

    view, _page = _build_view()
    options = view._playback_rate_dropdown.options

    assert [option.key for option in options] == [
        str(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES
    ]
    assert [option.text for option in options] == [
        format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES
    ]


def test_the_control_and_the_clock_state_the_rate_identically() -> None:
    """One mode, named once. Two spellings of it would be two modes to a reader."""

    view, _page = _build_view()

    _select_playback_rate(view, 60)
    offered = {option.key: option.text for option in view._playback_rate_dropdown.options}

    assert view._playback_rate_text.value == offered["60"]


def test_selecting_a_rate_changes_the_loop_and_the_readout_together() -> None:
    """The displayed rate is the rate the loop is about to run at.

    The correct number under the wrong label is still a presentation
    failure, and a rate is exactly a label over a behavior: what the panel
    says and what the next tick does have to move in one act.
    """

    view, _page = _build_view()

    _select_playback_rate(view, 60)

    assert view._playback_rate.multiplier == 60
    assert view._playback_rate_text.value == format_playback_rate(60)

    _select_playback_rate(view, 1)

    assert view._playback_rate.multiplier == 1
    assert view._playback_rate_text.value == format_playback_rate(1)


def test_the_playback_control_is_never_disabled() -> None:
    """Unlike the agent dropdown, which is, and for a reason that is not this one.

    Choosing an agent discards the case, so it is locked while a run holds
    state. A playback rate reaches no model state at all, and the usual
    reason to reach for it is to slow a *running* case down and watch
    something - so locking it would remove the control at the only moment it
    is wanted.
    """

    view, _page = _build_view(is_running=True)
    view._refresh_and_render()

    assert view._agent_dropdown.disabled is True
    assert view._playback_rate_dropdown.disabled in (False, None)


def test_reset_leaves_the_playback_rate_alone() -> None:
    """Reset clears dynamic state and preserves user settings; this is one.

    A rate snapping back to real time on Reset would be a mode change nobody
    made, announced only by a line the reader has no reason to re-read.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)

    _select_playback_rate(view, 20)
    view._handle_reset(cast(Any, ft.Event(name="click", control=view._reset_button, data=None)))

    assert view._playback_rate == playback_rate_for(20)
    assert view._playback_rate_text.value == format_playback_rate(20)


def test_a_failed_step_abandons_the_rest_of_its_tick(monkeypatch: pytest.MonkeyPatch) -> None:
    """A burst is not a licence to step past a step the core could not take.

    docs/MODEL.md forbids the interface continuing a run past a step the
    core could not complete, and a fast playback is where that could
    silently stop holding: the steps after the failure are already queued
    inside one tick. The run must stop on the last completed step, exactly
    as it does at real time.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._playback_rate = playback_rate_for(60)
    controller.start()

    calls = 0
    advance = controller.advance

    def failing_advance(simulation_step_s: float) -> None:
        nonlocal calls
        calls += 1

        if calls == 5:
            raise _real_step_failure()

        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", failing_advance)

    _drive_exact_ticks(view, 2, monkeypatch)

    # Five calls: four that stepped and the one that raised. Nothing after
    # it, in this tick or the next - halting clears `is_running`.
    assert calls == 5
    assert controller.snapshot().elapsed_s == 4 * SIMULATION_STEP_S
    assert controller.is_running is False


# --- PL-018: a core failure must never leave a stale "Running" display ----


def _real_step_failure() -> SimulationNumericalError:
    """Capture the exception the core actually raises on a broken step.

    Reusing the real exception rather than inventing one keeps these tests
    tied to what `core/` does: if the core stopped raising a
    `SimulationNumericalError` here, this helper fails rather than letting
    the interface tests pass against a fiction.

    The step taken is a supported one. Since PL-VP7N a step longer than
    `MAXIMUM_SIMULATION_STEP_S` is refused as a *configuration* error, which
    is a different thing entirely and is not what these tests are about: the
    interface has to halt a run whose numbers went bad mid-step, not one
    whose argument was rejected before it began.

    The failure is injected rather than provoked, and since PL-GS5X it has to
    be. The exact step is the solution of a pure transfer system, so its
    propagator is entrywise nonnegative and cannot carry a compartment out of
    range - no parameter set reaches the guard through the model any more.
    What is stood in for is what the guard remains cover for: a compartment
    handed a value the equations could not have produced.
    `tests/unit/test_uptake_system_failure.py` carries the same construction
    and the full reasoning.
    """

    system = AgentUptakeSystem.for_agent("isoflurane")
    original = system.patient.fat

    class _FatThatRefusesTheStep(TissueGroup):
        def set_partial_pressure_fraction(self, partial_pressure_fraction: float) -> None:
            super().set_partial_pressure_fraction(-1.0)

    system.patient.fat = _FatThatRefusesTheStep(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=(original.blood_gas_partition_coefficient),
        tissue_gas_partition_coefficient=(original.tissue_gas_partition_coefficient),
        blood_flow_l_min=original.blood_flow_l_min,
    )

    try:
        system.advance(MAXIMUM_SIMULATION_STEP_S)
    except SimulationNumericalError as error:
        return error

    raise AssertionError("expected the coupled step to be refused by the fat compartment")


class _StepFailingController(SimulationController):
    """A real controller whose next `advance()` raises, once."""

    def __init__(self, error: Exception) -> None:
        super().__init__()
        self._pending_error: Exception | None = error

    def advance(self, simulation_step_s: float) -> None:
        if self._pending_error is not None:
            error, self._pending_error = self._pending_error, None
            raise error

        super().advance(simulation_step_s)


def test_refresh_view_reports_a_failed_run_as_stopped_not_paused() -> None:
    view, _ = _build_view(
        failure_reason="SimulationNumericalError: the step could not be completed"
    )

    assert view._status_text.value == "Stopped — simulation error"
    assert view._status_text.color == WARNING
    assert view._notice_text.visible is True
    assert view._notice_text.value is not None
    assert "the step could not be completed" in view._notice_text.value
    # PL-026: the numbers beside the banner are the last completed step,
    # because the core rolls a failed step back. The reader has to be told
    # that much - a banner that only says something went wrong leaves them
    # to guess whether the values are a solution of the model or debris.
    assert "last completed step" in view._notice_text.value
    assert "rolled back" in view._notice_text.value


def test_refresh_view_does_not_offer_to_resume_a_failed_run() -> None:
    view, _ = _build_view(failure_reason="SimulationNumericalError: boom")

    assert view._start_button.disabled is True
    assert view._pause_button.disabled is True


def test_refresh_view_shows_no_notice_for_an_ordinary_run() -> None:
    for is_running in (True, False):
        view, _ = _build_view(is_running=is_running)

        assert view._notice_text.visible is False
        assert view._status_text.value in {"Running", "Paused"}


def test_a_failed_step_stops_the_run_instead_of_killing_the_loop() -> None:
    """The reproduced P1-1 failure, end to end through the real loop.

    Before this was guarded, the raise escaped `_run_simulation_timer` and
    killed the asyncio task while the interface still read "Running" over
    the last state it had drawn.
    """

    page = _FakePage()
    controller = _StepFailingController(_real_step_failure())
    view = SimulationView(page=page, controller=controller)
    controller.start()

    _run_briefly(view._run_simulation_timer, ticks=3, interval_s=SIMULATION_STEP_S)

    assert controller.is_running is False
    assert controller.has_failed is True
    assert view._status_text.value == "Stopped — simulation error"
    assert view._notice_text.visible is True
    assert view._notice_text.value is not None
    assert "SimulationNumericalError" in view._notice_text.value
    # The failure was drawn, not just recorded.
    assert page.update_calls >= 1


def test_the_simulation_loop_survives_a_failure_so_reset_can_restart_it() -> None:
    """The loop is started once, at mount, so it must not return on error.

    A loop that exited would leave Reset with nothing to restart: the
    interface would look recoverable and never advance again.
    """

    page = _FakePage()
    controller = _StepFailingController(_real_step_failure())
    view = SimulationView(page=page, controller=controller)
    controller.start()

    async def drive() -> None:
        task = asyncio.create_task(view._run_simulation_timer())

        await asyncio.sleep(SIMULATION_STEP_S * 3)
        assert controller.has_failed is True

        view._handle_reset(ft.Event(name="click", control=view._reset_button))
        view._handle_start(ft.Event(name="click", control=view._start_button))
        await asyncio.sleep(SIMULATION_STEP_S * 3)

        task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await task

    asyncio.run(drive())

    assert controller.has_failed is False
    assert controller.snapshot().elapsed_s > 0.0
    assert view._status_text.value == "Running"
    assert view._notice_text.visible is False


def test_a_failed_render_stops_the_run_rather_than_freezing_the_display() -> None:
    """A dead render loop over a live simulation is the mirror failure.

    The numbers would silently stop being current while the simulation
    kept advancing behind them, which is the same stale-state trap from
    the other direction.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    real_refresh_and_render = view._refresh_and_render
    failures_left = [1]

    def failing_refresh_and_render() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("chart series could not be updated")

        real_refresh_and_render()

    view._refresh_and_render = failing_refresh_and_render  # type: ignore[method-assign]

    _run_briefly(view._run_render_timer, ticks=2, interval_s=RENDER_INTERVAL_S)

    assert controller.is_running is False
    assert controller.has_failed is True
    # A plain programming error is treated exactly like a modelling one:
    # both kill the loop, and both leave the display claiming to be live.
    assert view._status_text.value == "Stopped — simulation error"
    assert view._notice_text.value is not None
    assert "RuntimeError" in view._notice_text.value


def test_a_refused_setting_is_reported_without_stopping_the_run() -> None:
    """Isoflurane's vaporizer stops at 5%, so 50% must be refused."""

    page = _FakePage()
    controller = SimulationController(agent_id="isoflurane")
    view = SimulationView(page=page, controller=controller)
    controller.start()
    delivered_before = controller.snapshot().delivered_concentration_fraction

    view._delivered_concentration_slider.value = 50.0
    view._handle_delivered_concentration_change(
        ft.Event(name="change", control=view._delivered_concentration_slider)
    )

    assert controller.is_running is True
    assert controller.has_failed is False
    assert view._status_text.value == "Running"
    assert view._notice_text.visible is True
    assert view._notice_text.value is not None
    assert "Setting refused" in view._notice_text.value
    assert "vaporizer maximum" in view._notice_text.value

    # The control must not keep showing a dial position the simulation is
    # not running at: that is the correct number under the wrong label.
    assert controller.snapshot().delivered_concentration_fraction == delivered_before
    assert view._delivered_concentration_slider.value == pytest.approx(delivered_before * 100.0)


def test_a_refusal_notice_clears_once_a_setting_is_accepted() -> None:
    page = _FakePage()
    controller = SimulationController(agent_id="isoflurane")
    view = SimulationView(page=page, controller=controller)

    view._delivered_concentration_slider.value = 50.0
    view._handle_delivered_concentration_change(
        ft.Event(name="change", control=view._delivered_concentration_slider)
    )
    assert view._notice_text.visible is True

    view._delivered_concentration_slider.value = 2.0
    view._handle_delivered_concentration_change(
        ft.Event(name="change", control=view._delivered_concentration_slider)
    )

    assert view._notice_text.visible is False
    assert controller.snapshot().delivered_concentration_fraction == pytest.approx(0.02)


@pytest.mark.parametrize(
    ("handler_name", "slider_name", "refused_value"),
    [
        ("_handle_fresh_gas_flow_change", "_fresh_gas_flow_slider", -1.0),
        ("_handle_alveolar_ventilation_change", "_alveolar_ventilation_slider", -1.0),
        ("_handle_cardiac_output_change", "_cardiac_output_slider", -1.0),
    ],
)
def test_every_slider_handler_refuses_without_escaping_into_flet(
    handler_name: str, slider_name: str, refused_value: float
) -> None:
    """No setting callback may let a core raise reach Flet's dispatcher.

    The sliders' own bounds keep these values unreachable in the running
    app, which is exactly why the guard needs its own cover: a later
    change to a bound would otherwise make an unguarded callback reachable
    with nothing to catch it.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    slider = getattr(view, slider_name)
    slider.value = refused_value
    getattr(view, handler_name)(ft.Event(name="change", control=slider))

    assert controller.is_running is True
    assert controller.has_failed is False
    assert view._notice_text.visible is True
    assert view._notice_text.value is not None
    assert "Setting refused" in view._notice_text.value
    assert slider.value >= 0.0


class _RecordingController(_FakeController):
    """A controller recording how it was stopped, instead of running.

    `_halt_run` is the path that turns a raised exception into a stopped run
    and a visible banner. What matters is that it stops the run and records
    the reason *on the right channel*, so both are recorded here and kept
    apart: routing a domain limit into `fail` would still stop the run, and
    would put "simulation error" over a model that behaved correctly.
    """

    def __init__(
        self,
        snapshot: SimulationSnapshot,
        history: tuple[SimulationHistorySample, ...] | None = None,
    ) -> None:
        super().__init__(snapshot, history)
        self.failures: list[str] = []
        self.supported_limits: list[str] = []

    def fail(self, reason: str) -> None:
        self.failures.append(reason)
        self.is_running = False

    def halt_at_supported_limit(self, reason: str) -> None:
        self.supported_limits.append(reason)
        self.is_running = False


def test_halt_run_stops_the_session_and_records_the_exception_type() -> None:
    """The reason carries the type as well as the message.

    A bare message loses the difference between a modelling failure and a
    `TypeError` from a refactor, and the two want different responses from
    whoever reads the banner.
    """
    controller = _recording_controller()
    view = SimulationView(page=_FakePage(), controller=controller)

    view._halt_run(ValueError("mass balance violated"))

    assert controller.failures == ["ValueError: mass balance violated"]
    assert controller.is_running is False


def test_halt_run_survives_a_render_failure_and_leaves_the_run_stopped() -> None:
    """A display that cannot be updated must not prevent the run from stopping.

    `_halt_run` swallows a rendering exception on purpose: the run is already
    stopped, and a frozen display over a stopped simulation is at worst
    uninformative, where one over a *running* simulation is actively
    misleading. This asserts that documented behaviour - that the failure is
    recorded, the run is stopped, and nothing propagates to the caller - so
    that the suppression is covered by a test rather than only by a comment.
    """
    controller = _recording_controller()
    view = SimulationView(page=_FakePage(), controller=controller)

    def _explode() -> None:
        raise RuntimeError("the page is gone")

    view._refresh_and_render = _explode  # type: ignore[method-assign]

    view._halt_run(ValueError("mass balance violated"))

    assert controller.failures == ["ValueError: mass balance violated"]
    assert controller.is_running is False


def test_a_built_in_agent_without_an_identification_colour_fails_at_import() -> None:
    """Adding an agent without its ISO 5360 colour must stop the app starting.

    The guard runs at module scope, so covering it means re-executing the
    module body with the colour table short one entry. The module is reloaded
    again afterwards so that the genuine table is what every later test and
    every later import sees.
    """
    import importlib

    from anesthesia_sim.app import simulation_view as module
    from anesthesia_sim.app import theme

    original = dict(theme.AGENT_COLOR_SCHEMES)
    theme.AGENT_COLOR_SCHEMES.pop(next(iter(original)))
    try:
        with pytest.raises(
            RuntimeError,
            match="^AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents$",
        ):
            importlib.reload(module)
    finally:
        theme.AGENT_COLOR_SCHEMES.clear()
        theme.AGENT_COLOR_SCHEMES.update(original)
        importlib.reload(module)


def test_the_model_keeps_precision_the_display_throws_away() -> None:
    """The 0.01% resolution is a property of the display alone.

    `docs/MODEL.md` § "Displayed precision" argues at length for two decimal
    places, and a reader could reasonably take that for a statement about the
    model. It is not: every compartment state, every integration step, and
    every history sample carries full binary64 throughout, and the rounding
    happens once, in the formatter. The gap is nine orders of magnitude: the
    solver's own residual is around 1e-12 percentage points against a last
    displayed digit of 0.01.

    Two runs whose only difference is four orders of magnitude below the
    display resolution must therefore reach different states. If anything in
    the pipeline quantized to what the display shows — a tidied `round()` in
    `core/`, a rounded snapshot field — the two would be identical here and
    this fails, which is the regression the assertion exists to catch.
    """

    below_resolution = 1e-8  # a fraction, i.e. 1e-6 percentage points

    def run_at(delivered_concentration_fraction: float) -> tuple[float, str]:
        controller = SimulationController()
        controller.set_delivered_concentration(delivered_concentration_fraction)
        controller.start()
        _advance_to(controller, 120.0)
        snapshot = controller.snapshot()

        return snapshot.alveolar_concentration_fraction, format_percent(
            snapshot.alveolar_concentration_fraction
        )

    baseline_fraction, baseline_displayed = run_at(0.02)
    perturbed_fraction, perturbed_displayed = run_at(0.02 + below_resolution)

    assert baseline_fraction != perturbed_fraction, (
        "a change four orders of magnitude below the display resolution left "
        "the alveolar state bit-identical; something in the model or the "
        "snapshot is rounding to what the display shows"
    )
    assert 0.0 < abs(perturbed_fraction - baseline_fraction) < 1e-6
    assert baseline_displayed == perturbed_displayed, (
        "the two runs should be indistinguishable on the display and distinct "
        "in the model; if they differ on the display this test is no longer "
        "measuring what it claims"
    )


def test_every_compartment_is_readable_in_mac_multiples() -> None:
    """PL-DHV7's own acceptance criterion, read off the assembled grid.

    The whole point of the second unit is that it is on *every* graphed
    compartment rather than on the alveolar readout alone: a MAC multiple
    on the vessel-rich, muscle and fat traces is what makes a wash-in
    comparable across agents, and it is the unit the reference simulator
    plots in. Asserted against the panels rather than the controls, so a
    MAC line built but never placed in the row fails here.
    """

    view, _ = _build_view(history=(_sample(60.0, 0.02, 0.016, 0.008, 0.006, 0.001, 5e-5),))

    mac_lines = [
        panel.content.controls[3].value for panel in view._build_concentration_metrics().controls
    ]

    # "Simulated time" holds the line open without a value; the six
    # compartments each carry one.
    assert sum(1 for line in mac_lines if line and "MAC" in line) == 6
    assert view._circuit_mac_text.value == "1.00 ×MAC"
    assert view._alveolar_mac_text.value == "0.80 ×MAC"
    assert view._mixed_venous_mac_text.value == "0.40 ×MAC"
    assert view._vessel_rich_mac_text.value == "0.30 ×MAC"
    assert view._muscle_mac_text.value == "0.05 ×MAC"
    assert view._fat_mac_text.value == "<0.01 ×MAC"


def test_each_mac_readout_uses_its_own_agent_divisor() -> None:
    """The failure this readout has to be proof against, stated as a test.

    A MAC multiple is a concentration divided by the running agent's own
    1 MAC, and the same concentration is a different multiple under each
    agent: 6% is 3 MAC of sevoflurane and 1 MAC of desflurane. A divisor
    left over from the previously selected agent would therefore produce
    a plausible number under the correct label, which is the presentation
    failure `CLAUDE.md` treats as a safety failure rather than a cosmetic
    one.

    Switching the snapshot rather than building two views is deliberate,
    for the reason the header-repaint test gives: a `_refresh_view` that
    had stopped re-reading the divisor would still pass a per-agent
    construction test.
    """

    controller = _fake_controller(history=(_sample(60.0, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06),))
    view = SimulationView(page=_FakePage(), controller=controller)

    assert view._alveolar_mac_text.value == "3.00 ×MAC"

    controller.switch_agent(
        "desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
        history=(_sample(60.0, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, substance_id="desflurane"),),
    )
    view._refresh_view()

    assert view._alveolar_mac_text.value == "1.00 ×MAC"
    assert view._fat_mac_text.value == "1.00 ×MAC"


def test_the_display_names_the_mac_the_readouts_were_divided_by() -> None:
    """The divisor is the one free parameter, so the display carries it.

    `CLAUDE.md` requires a clinically meaningful value to be traceable to
    the exact transformation that produced it, and PL-DHV7's "done when"
    names this explicitly: the agent's `mac_percent` has to be traceable
    from the display. It also has to follow an agent change, or it becomes
    a confident statement about the wrong agent.
    """

    controller = _fake_controller()
    view = SimulationView(page=_FakePage(), controller=controller)

    assert view._mac_reference_text.value == format_mac_reference("Sevoflurane", 2.0)

    controller.switch_agent(
        "desflurane", agent_display_name="Desflurane", max_delivered_concentration_percent=18.0
    )
    view._refresh_view()

    assert view._mac_reference_text.value == format_mac_reference("Desflurane", 6.0)


def test_the_interface_says_what_a_mac_multiple_on_a_compartment_is_not() -> None:
    """The convention has to be stated where the numbers are read.

    A MAC multiple on a tissue compartment means "this partial pressure
    equals N times the alveolar concentration that would be 1 MAC", not
    "the patient is at N MAC of anesthetic depth" — the two read the same
    on a label and are not the same claim, which is the hard half of
    PL-DHV7. MAC is also defined for a nominal 40-year-old without
    adjustment for age or a second agent, neither of which this model has.

    Asserted against the whole mounted tree rather than one control, for
    the reason the end-tidal hedge is: the claim is about what the
    interface says, not about where it says it.
    """

    page = _FakePage()
    view = SimulationView(page=page, controller=_fake_controller())
    view.mount()

    disclosure = " ".join(sorted(_mounted_interface_strings(view, page)))

    assert "not a depth of anesthesia" in disclosure
    assert "40-year-old" in disclosure
    assert "1 MAC sevoflurane = 2.0%" in disclosure


def test_the_chart_carries_a_mac_axis_beside_its_percent_axis() -> None:
    """Two rulers, one set of traces, and no unit mode between them.

    The plotted points stay in percent, so the MAC axis is a relabelling
    of the same coordinate rather than a second series — which is what
    makes it impossible for the two axes to disagree about where a trace
    is. A unit toggle would instead make the axis unit a hidden mode, and
    a chart read under the wrong assumed unit is a misreading no
    disclaimer catches.
    """

    view, _ = _build_view()

    assert view._concentration_chart.right_axis is view._mac_axis
    assert view._concentration_chart.left_axis is not None

    ticks = mac_axis_ticks(chart_axis_top_percent(2.0), 2.0)

    # `value` is the position in the chart's own percent coordinate and
    # `label` the MAC number written there. Asserting both together is what
    # makes this a test of the *pairing*: a MAC number placed at the wrong
    # percent would be a correctly labelled axis reading the wrong scale.
    assert [label.value for label in view._mac_axis.labels] == pytest.approx(
        [percent for percent, _ in ticks]
    )
    assert [label.label.value for label in view._mac_axis.labels] == [text for _, text in ticks]
    assert [label.label.value for label in view._mac_axis.labels][:3] == ["0.0", "0.5", "1.0"]
    assert view._mac_axis.labels[2].value == pytest.approx(2.0), "1 MAC sevoflurane is not at 2%"


def test_the_mac_axis_is_rebuilt_only_when_the_agent_or_the_range_moves() -> None:
    """A per-frame axis rebuild is the churn PL-010 removed, by another door.

    The labels depend on the agent and the plotted range and on nothing
    that moves during a run, where the render loop runs several times a
    second. Rebuilding them per frame would allocate a control per tick
    per frame and send the client an add-and-remove of the whole axis each
    time. `tests/integration/test_chart_patching.py` measures the
    consequence against a real Flet session; this pins the guard itself.
    """

    controller = _fake_controller()
    view = SimulationView(page=_FakePage(), controller=controller)

    before = view._mac_axis.labels
    view._refresh_view()

    assert view._mac_axis.labels is before, "the axis was rebuilt for an unchanged frame"

    controller.switch_agent(
        "desflurane", agent_display_name="Desflurane", max_delivered_concentration_percent=18.0
    )
    view._refresh_view()

    assert view._mac_axis.labels is not before
    assert [label.label.value for label in view._mac_axis.labels][-1] == "3.0"
    assert view._mac_axis.labels[-1].value == pytest.approx(18.0)


def test_the_dial_is_readable_in_the_unit_its_compartments_are() -> None:
    """The one control a reader sets, in the units of the traces it fills.

    Without it the delivered concentration would be the only value on the
    page that could not be compared with the compartments it drives — and
    "open the vaporizer to 1 MAC" is the single most common thing a reader
    of this simulator will want to do.
    """

    view, _ = _build_view()

    assert view._delivered_concentration_text.value == format_percent(0.08)
    assert view._delivered_concentration_mac_text.value == format_mac_multiple(0.08, 2.0)
    assert view._delivered_concentration_mac_text.value == "4.00 ×MAC"


def test_the_end_to_end_mac_path_reaches_the_panel_from_a_real_run() -> None:
    """Patient inputs, model selection, calculation, units, formatting, display.

    `CLAUDE.md` asks for the whole path to be tested where it matters, and
    a MAC readout adds a transformation to it that the percent readout
    does not have. A real controller, a real step and the real formatter,
    read off the control the user actually looks at.
    """

    controller = SimulationController(agent_id="desflurane")
    view = SimulationView(page=_FakePage(), controller=controller)

    controller.start()

    for _ in range(600):
        controller.advance(SIMULATION_STEP_S)

    view._refresh_view()

    snapshot = controller.snapshot()

    assert snapshot.agent_mac_percent == 6.0
    assert view._alveolar_mac_text.value == format_mac_multiple(
        snapshot.alveolar_concentration_fraction, 6.0
    )
    # The dial starts at the agent's own 1 MAC, so after a minute of wash-in
    # the alveolar compartment is somewhere below it and above nothing.
    alveolar_mac = snapshot.alveolar_concentration_fraction * 100.0 / 6.0
    assert 0.0 < alveolar_mac < 1.0
    assert view._delivered_concentration_mac_text.value == "1.00 ×MAC"


def test_the_clinical_references_are_drawn_at_the_running_agents_own_values() -> None:
    """Both references are placed by the running agent's own two constants.

    The band is `mac_awake.fraction_of_mac` times `mac_percent`, and the line
    is `mac_percent`. Placing either from another agent's value would be a
    correct number at the wrong height on a labelled axis, which
    `CLAUDE.md` counts as a presentation failure rather than a cosmetic one.
    Checked across every shipped agent so the pairing cannot hold for the
    default and not the others.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view, _ = _build_view(agent_id=agent_id)

        deviation = agent.mac_awake.standard_deviation_fraction_of_mac * agent.mac_percent
        centre = agent.mac_awake.fraction_of_mac * agent.mac_percent

        upper = view._mac_awake_band_upper_edge
        lower = view._mac_awake_band_lower_edge
        assert all(point.y == pytest.approx(centre + deviation) for point in upper.points)
        assert all(point.y == pytest.approx(centre - deviation) for point in lower.points)
        assert upper.below_line_cutoff_y == pytest.approx(centre - deviation)

        for point in view._one_mac_line_series.points:
            assert point.y == pytest.approx(agent.mac_percent)


def test_the_mac_awake_band_reads_as_an_interval_not_a_line() -> None:
    """Two strokes on the published boundaries, and no inflation between them.

    `PL-90Y6`: one standard deviation either side of the mean is 3.3% of the
    plot height for sevoflurane and 4.2% for desflurane on the fixed
    `CHART_AXIS_TOP_MAC` axis, and no axis range the overpressure constraint
    allows makes that fill read as a band on its own. A stroked upper edge
    over an unstroked fill is the geometry of a line with a shadow under it,
    whatever the fill's extent, so the mark was drawn as a line - which
    erases the distinction `docs/MODEL.md` chose the mark type to carry: a
    band for a measured population value with real spread, a line for the
    definitional 1 MAC anchor.

    Two things are asserted together because either alone permits the wrong
    fix. The band has two stroked edges, so it reads as an interval; and both
    strokes sit on the published boundaries, so the drawn extent is the data
    extent. A minimum drawn height would satisfy the first and violate the
    second, asserting a wider population spread than the literature supports
    - an interpretability defect traded for a correctness one.

    Checked across every shipped agent, because the spread is the agent's own
    and sevoflurane's is the narrowest of the three.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view, _ = _build_view(agent_id=agent_id)

        centre = agent.mac_awake.fraction_of_mac * agent.mac_percent
        deviation = agent.mac_awake.standard_deviation_fraction_of_mac * agent.mac_percent

        upper = view._mac_awake_band_upper_edge
        lower = view._mac_awake_band_lower_edge

        # Two edges, both stroked, both undashed: a pair of solid rules is
        # what separates this mark from the dashed 1 MAC line beside it.
        assert upper is not lower
        for edge in (upper, lower):
            assert edge.stroke_width == MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
            assert edge.stroke_width > 0.0
            assert edge.color == MAC_AWAKE_BAND_COLOR
            assert edge.dash_pattern is None

        # The drawn extent is the data extent: nothing is padded outward to
        # make the band easier to see.
        assert all(point.y == pytest.approx(centre + deviation) for point in upper.points)
        assert all(point.y == pytest.approx(centre - deviation) for point in lower.points)
        assert upper.below_line_cutoff_y == pytest.approx(centre - deviation)

        # The fill spans exactly the two strokes rather than extending past
        # either of them, so no part of the mark claims more than +/-1 SD.
        drawn_extent = upper.points[0].y - lower.points[0].y
        assert drawn_extent == pytest.approx(2.0 * deviation)

        # And the 1 MAC anchor stays a single line, so the two references
        # remain distinguishable in kind rather than by colour alone.
        assert view._one_mac_line_series is not upper
        assert view._one_mac_line_series is not lower


def test_the_band_legend_swatch_is_ruled_on_both_edges_like_the_chart_mark() -> None:
    """A legend teaching one mark for a chart drawing another misreads it.

    The swatch is how a reader learns which mark means what, so a swatch
    ruled on its upper edge only would carry the same line-not-band reading
    `PL-90Y6` removed from the chart, and would carry it into every glance at
    the plot afterwards.
    """

    swatch = cast(
        ft.Container,
        SimulationView._build_band_legend_item(
            "MAC-awake (population, ±1 SD)", MAC_AWAKE_BAND_COLOR
        ).controls[0],
    )

    border = swatch.border
    assert border is not None
    assert border.top is not None
    assert border.bottom is not None
    for side in (border.top, border.bottom):
        assert side.width == MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
        assert side.color == MAC_AWAKE_BAND_COLOR

    assert swatch.bgcolor == ft.Colors.with_opacity(
        MAC_AWAKE_BAND_FILL_OPACITY, MAC_AWAKE_BAND_COLOR
    )


def test_the_clinical_references_follow_the_agent_when_it_changes() -> None:
    """A reference left at the previous agent's height would misread the run.

    The chart is agent-switchable and the MAC axis already rebuilds on a
    change; the references have to move with it. Sevoflurane and desflurane
    differ by a factor of three in MAC, so a reference that failed to move
    would sit at a third or triple its correct height rather than being
    subtly wrong.
    """

    controller = _fake_controller(agent_id="sevoflurane")
    view = SimulationView(page=_FakePage(), controller=controller)

    sevoflurane = load_agent_parameters("sevoflurane")
    assert view._one_mac_line_series.points[0].y == pytest.approx(sevoflurane.mac_percent)

    desflurane = load_agent_parameters("desflurane")
    controller.switch_agent("desflurane", agent_display_name="Desflurane")
    view._refresh_view()

    assert view._one_mac_line_series.points[0].y == pytest.approx(desflurane.mac_percent)

    centre = desflurane.mac_awake.fraction_of_mac * desflurane.mac_percent
    deviation = desflurane.mac_awake.standard_deviation_fraction_of_mac * desflurane.mac_percent
    assert view._mac_awake_band_upper_edge.points[0].y == pytest.approx(centre + deviation)
    assert view._mac_awake_band_lower_edge.points[0].y == pytest.approx(centre - deviation)
    assert view._mac_awake_band_upper_edge.below_line_cutoff_y == pytest.approx(centre - deviation)


def test_the_clinical_references_span_the_visible_window() -> None:
    """A reference ruled across part of the chart would read as ending.

    Both marks are constants that hold for the whole run, so each has to span
    the plotted range exactly - a line stopping short would invite reading it
    as a quantity that changed.
    """

    view, _ = _build_view(history=_run_history(6_000))
    chart = view._concentration_chart

    for series in (
        view._mac_awake_band_upper_edge,
        view._mac_awake_band_lower_edge,
        view._one_mac_line_series,
    ):
        assert [point.x for point in series.points] == [chart.min_x, chart.max_x]


def test_the_clinical_references_are_not_compartment_traces() -> None:
    """A reference must not enter the trace-to-compartment table, or the palette.

    `_plotted_series` binds each trace to the one quantity it draws and is
    what `test_chart_traces_stay_bound_to_their_own_compartment` audits. A
    reference reads no sample, so it belongs to neither. It is also drawn
    *before* every trace, so an annotation can never obscure the run it
    annotates.
    """

    view, _ = _build_view()

    plotted = [series for series, _ in view._plotted_series(_DEFAULT_AGENT)]
    references = (
        view._mac_awake_band_upper_edge,
        view._mac_awake_band_lower_edge,
        view._one_mac_line_series,
    )
    for reference in references:
        assert reference not in plotted

    order = view._concentration_chart.data_series
    for reference in references:
        assert order.index(reference) < min(order.index(each) for each in plotted)


def test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from() -> None:
    """Two free parameters, both on the display.

    `format_mac_reference` names the MAC axis's one divisor for the same
    reason. The band is a published fraction applied to that divisor, so a
    reader has two things they might disagree with and both are stated.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view, page = _build_view(agent_id=agent_id, agent_display_name=agent.display_name)
        strings = _mounted_interface_strings(view, page)

        expected = format_mac_awake_reference(
            agent.display_name,
            fraction_of_mac=agent.mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=(agent.mac_awake.standard_deviation_fraction_of_mac),
            mac_percent=agent.mac_percent,
        )

        assert expected in strings
        assert format_mac_reference(agent.display_name, agent.mac_percent) in strings


def test_the_interface_says_which_trace_the_band_is_read_against() -> None:
    """The one instruction without which a correct band teaches the wrong thing.

    This model has no effect-site compartment and defines the arterial
    fraction as the alveolar one, so the alveolar trace is the fastest curve
    on the chart. Measured on a 3-hour 1 MAC sevoflurane washout it crosses
    the band's centre 2.3 times sooner than the vessel-rich trace does, so a
    band read against it teaches an early wake-up - the direction with
    clinical consequence. `docs/MODEL.md` § "MAC-awake as a chart reference"
    is the specification this sentence is the display-side half of.
    """

    view, page = _build_view()
    prose = " ".join(_mounted_interface_strings(view, page))

    assert "vessel-rich trace" in prose
    # The endpoint, distinguished from MAC's own.
    assert "respond to command" in prose
    assert "immobility to incision" in prose
    # And the extent, so the band is not read as a threshold.
    assert "±1 SD" in prose or "1 SD" in prose


def test_the_interface_never_predicts_a_time_to_wake_up() -> None:
    """The claim the band exists *instead of*, checked against the whole tree.

    A readout of the form "time to wake-up: 14 min" reads as a per-patient
    prediction this model does not support, and no surrounding disclaimer
    undoes that - the number would be acted on and the disclaimer would not.
    The band is the strongest claim the evidence carries, so this asserts the
    stronger one is absent from everywhere in the assembled interface rather
    than from the controls a test remembered to check.
    """

    view, page = _build_view(history=_run_history(6_000))
    strings = _mounted_interface_strings(view, page)
    prose = " ".join(strings).lower()

    # The hazard itself: any string that mentions waking *and* carries a
    # duration is a time prediction however it is worded, and this catches a
    # phrasing nobody thought to enumerate.
    duration = re.compile(
        r"\d+(?:\.\d+)?\s*(?:s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hour|hours)\b"
    )

    for value in strings:
        lowered = value.lower()
        if any(word in lowered for word in ("wake", "awaken", "arousal", "emergence")):
            assert duration.search(lowered) is None, value

    # And the named forms, each of which must appear only under a negation if
    # it appears at all - the band's own disclaimer says "not a time to
    # wake-up", which is the sentence that makes the claim absent rather than
    # a claim being made.
    for forbidden in (
        "time to wake",
        "time to awaken",
        "wake-up time",
        "wakeup time",
        "emergence time",
        "time to emergence",
        "predicted wake",
        "will wake",
    ):
        for match in re.finditer(re.escape(forbidden), prose):
            preceding = prose[max(0, match.start() - 12) : match.start()]
            assert "not " in preceding, (forbidden, preceding)

    # The band's own line says what it is not, in terms.
    assert "not a time to wake-up" in prose
    assert "not a prediction for any individual patient" in prose


def _control_change(
    elapsed_s: float,
    control: ControlInput,
    previous_value: float,
    new_value: float,
    adjustment: int,
) -> ControlChange:
    return ControlChange(
        elapsed_s=elapsed_s,
        sample_index=round(elapsed_s * 10),
        adjustment=adjustment,
        control=control,
        previous_value=previous_value,
        new_value=new_value,
        unit=CONTROL_INPUT_UNITS[control],
    )


def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time() -> None:
    view, _ = _build_view(
        history=_run_history(600),
        control_timeline=(
            _control_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        ),
    )

    mark = view._control_mark_series[0]
    assert [point.x for point in mark.points] == [12.0, 12.0]


def test_a_control_mark_spans_the_running_agents_plotted_range() -> None:
    """A mark short of the top would leave a trace above it unannotated.

    The range follows the agent's dial maximum, so this also pins the mark
    to the same snapshot the axis was built from.
    """

    view, _ = _build_view(
        agent_id="desflurane",
        history=_run_history(600, substance_id="desflurane"),
        control_timeline=(
            _control_change(12.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=1),
        ),
    )

    mark = view._control_mark_series[0]
    assert [point.y for point in mark.points] == [0.0, view._concentration_chart.max_y]


def test_unused_control_marks_are_parked_outside_the_plotted_window() -> None:
    """The pool is fixed, so a mark with nothing to mark must draw nothing."""

    view, _ = _build_view(
        history=_run_history(600),
        control_timeline=(
            _control_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        ),
    )

    chart = view._concentration_chart
    for mark in view._control_mark_series[1:]:
        assert all(point.x < chart.min_x for point in mark.points)


def test_a_control_mark_left_by_a_previous_frame_is_parked_when_it_ends() -> None:
    """A reset clears the timeline, and the marks have to follow it.

    A mark surviving the run that recorded it would annotate a fresh run
    with an adjustment nobody made.
    """

    controller = _fake_controller(
        history=_run_history(600),
        control_timeline=(
            _control_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        ),
    )
    view = SimulationView(page=_FakePage(), controller=cast(SimulationController, controller))

    controller.advance_to(_run_history(600))
    view._refresh_view()

    chart = view._concentration_chart
    assert all(point.x < chart.min_x for point in view._control_mark_series[0].points)


def test_control_marks_are_not_compartment_traces() -> None:
    """A mark reads no sample, so it belongs to neither the table nor the palette.

    It is also drawn before every trace and before both references: a
    vertical rule crosses the whole plot, so of the three kinds of series
    it is the one that could hide all six compartments at once.
    """

    view, _ = _build_view()

    plotted = [series for series, _ in view._plotted_series(_DEFAULT_AGENT)]
    order = view._concentration_chart.data_series

    for mark in view._control_mark_series:
        assert mark not in plotted
        assert order.index(mark) < min(order.index(each) for each in plotted)
        assert order.index(mark) < order.index(view._mac_awake_band_upper_edge)
        assert order.index(mark) < order.index(view._mac_awake_band_lower_edge)


def test_the_list_states_what_was_changed_and_to_what() -> None:
    view, _ = _build_view(
        history=_run_history(600),
        control_timeline=(
            _control_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        ),
    )

    assert view._control_timeline_text.value == ("12.0 s · Fresh gas flow 4.0 L/min -> 2.0 L/min")


def test_the_list_reads_most_recent_first() -> None:
    """A fixed panel has to show the change the reader has just made."""

    view, _ = _build_view(
        history=_run_history(600),
        control_timeline=(
            _control_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
            _control_change(20.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
        ),
    )

    lines = view._control_timeline_text.value.splitlines()
    assert lines[0].startswith("20.0 s")
    assert lines[1].startswith("10.0 s")


def test_a_run_with_no_changes_says_so_rather_than_showing_an_empty_panel() -> None:
    view, _ = _build_view()

    assert view._control_timeline_text.value == NO_CONTROL_CHANGES_TEXT
    assert not view._control_timeline_overflow_text.visible


def test_changes_the_panel_cannot_list_are_counted_rather_than_dropped() -> None:
    """A list that quietly stops asserts that nothing earlier happened."""

    timeline = tuple(
        _control_change(
            float(index), ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.1, adjustment=index + 1
        )
        for index in range(MAX_LISTED_ADJUSTMENTS + 3)
    )
    view, _ = _build_view(history=_run_history(600), control_timeline=timeline)

    assert len(view._control_timeline_text.value.splitlines()) == MAX_LISTED_ADJUSTMENTS
    assert view._control_timeline_overflow_text.visible
    assert "3 earlier change(s) not listed" in view._control_timeline_overflow_text.value


def test_changes_the_chart_cannot_mark_are_counted_rather_than_dropped() -> None:
    """Same rule for the plot: a chart that stops annotating is a claim."""

    timeline = tuple(
        _control_change(
            float(index), ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    view, _ = _build_view(history=_run_history(600), control_timeline=timeline)

    assert view._undrawn_control_marks == 2
    assert "2 not marked on the chart" in view._control_timeline_overflow_text.value


def test_the_most_recent_changes_are_the_ones_marked() -> None:
    """The reader is comparing the change they just made against the curve."""

    timeline = tuple(
        _control_change(
            float(index), ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    view, _ = _build_view(history=_run_history(600), control_timeline=timeline)

    marked = {mark.points[0].x for mark in view._control_mark_series}
    assert max(marked) == float(MAX_CHART_CONTROL_MARKS + 1)
    assert 0.0 not in marked


def test_a_drag_of_one_slider_is_marked_and_listed_once() -> None:
    """One act by the person, however many settings the model was stepped under."""

    view, _ = _build_view(
        history=_run_history(600),
        control_timeline=(
            _control_change(10.0, ControlInput.DELIVERED, 0.02, 0.03, adjustment=1),
            _control_change(10.1, ControlInput.DELIVERED, 0.03, 0.035, adjustment=1),
            _control_change(10.2, ControlInput.DELIVERED, 0.035, 0.04, adjustment=1),
        ),
    )

    assert len(view._control_timeline_text.value.splitlines()) == 1
    assert view._control_mark_series[0].points[0].x == 10.0
    chart = view._concentration_chart
    assert all(point.x < chart.min_x for point in view._control_mark_series[1].points)


def test_the_sliders_declare_an_adjustment_boundary_when_a_drag_begins() -> None:
    """Without it two turns of one dial are one adjustment on the record.

    The interface is the only party that knows where a gesture ended, so
    the wiring is what makes the controller's grouping correct rather than
    merely available.
    """

    view, _ = _build_view()

    for slider in (
        view._fresh_gas_flow_slider,
        view._delivered_concentration_slider,
        view._alveolar_ventilation_slider,
        view._cardiac_output_slider,
    ):
        assert slider.on_change_start == view._handle_adjustment_start


def test_a_declared_boundary_reaches_the_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)

    controller.start()
    controller.set_fresh_gas_flow(3.0)
    controller.advance(SIMULATION_STEP_S)
    view._handle_adjustment_start(cast(ft.Event[ft.Slider], None))
    controller.set_fresh_gas_flow(2.0)

    assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}


def test_the_interface_says_a_control_mark_is_an_input_not_a_measurement() -> None:
    """The one misreading a vertical rule on a patient chart invites.

    Every other mark on this plot is either a modelled quantity or a
    published constant; this one is a record of what the user did, and a
    reader who takes it for an event in the patient has read the run
    backwards.
    """

    view, page = _build_view()

    disclosure = " ".join(sorted(_mounted_interface_strings(view, page)))

    assert "not anything measured from the patient" in disclosure
    assert "Settings only — not a measurement." in disclosure


def _wash_in_points(view: SimulationView) -> list[tuple[float, float]]:
    """Every point the wash-in trace is drawing, in x order across segments."""

    return [
        (point.x, point.y) for series in view._wash_in_segment_series for point in series.points
    ]


def _drawn_wash_in_segments(view: SimulationView) -> list[list[tuple[float, float]]]:
    """The wash-in trace as the separate stretches the chart draws it in."""

    return [
        [(point.x, point.y) for point in series.points]
        for series in view._wash_in_segment_series
        if series.points
    ]


def test_the_wash_in_trace_draws_the_ratio_and_not_a_percent() -> None:
    """The one trace on this chart is in nobody else's unit.

    Every other trace is converted from a fraction to percent on its way
    to the chart, and the wash-in axis runs 0 to 1. A ratio multiplied by
    100 on a 0-to-1 axis would leave the whole curve off the top of a
    plot whose axis said it was a fraction, which is the wrong-unit
    failure `CLAUDE.md` treats as a safety failure rather than a
    cosmetic one.
    """

    history = _run_history(40)
    view, _ = _build_view(history=history)

    latest = history[-1]
    expected = wash_in_ratio(
        _recorded(latest, RecordedQuantity.ALVEOLAR), _recorded(latest, RecordedQuantity.CIRCUIT)
    )

    assert expected is not None
    assert _wash_in_points(view)[-1] == (latest.elapsed_s, pytest.approx(expected))
    assert view._wash_in_chart.max_y == WASH_IN_AXIS_MAXIMUM


def test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit() -> None:
    """0/0 is not a point, and an empty circuit is where every run starts."""

    view, _ = _build_view(history=_run_history(1))

    assert _wash_in_points(view) == []
    assert "Not defined" in cast(str, view._wash_in_state_text.value)
    assert "no agent has reached the circuit" in cast(str, view._wash_in_state_text.value)


def test_the_wash_in_trace_stops_when_alveolar_exceeds_inspired() -> None:
    """Elimination is not wash-in, and the plot says so rather than drawing it."""

    history = (*_run_history(20), _sample(2.0, 0.010, 0.030, 0.02, 0.02, 0.01, 0.01))
    view, _ = _build_view(history=history)

    drawn_times = [x for x, _ in _wash_in_points(view)]

    # A ratio of 3.0 is far past the terminus ceiling, so it is not drawn at
    # all - not clamped onto the ceiling, and not interpolated onto it.
    assert 2.0 not in drawn_times
    assert max(y for _, y in _wash_in_points(view)) <= WASH_IN_TERMINUS_CEILING
    assert "alveolar exceeds inspired" in cast(str, view._wash_in_state_text.value)
    assert "elimination" in cast(str, view._wash_in_state_text.value)


def test_the_wash_in_trace_ends_on_the_equilibrium_line_it_crossed() -> None:
    """A curve that halts a step short of the line it stopped at reads as clipped.

    The last sample at or below equilibrium is up to one simulation step
    below it, so a trace ending there stops in clear space with nothing to
    show why. Drawing the crossing sample puts the ending on the line. It
    is one point outside the plotted domain and it is bounded: what admits
    it is `WASH_IN_TERMINUS_CEILING`, not a promise about the model.
    """

    crossing = _sample(2.0, 0.0800, 0.0801, 0.02, 0.02, 0.01, 0.01)
    view, _ = _build_view(history=(*_run_history(20), crossing))

    last_x, last_y = _wash_in_points(view)[-1]

    assert last_x == 2.0
    assert WASH_IN_EQUILIBRIUM_RATIO < last_y <= WASH_IN_TERMINUS_CEILING
    assert view._wash_in_chart.max_y > last_y, "the ending must not sit on the frame"


def test_a_stopped_wash_in_trace_ends_in_a_terminus_marker() -> None:
    """A line that merely stops cannot be told from one the frame cut off."""

    crossing = _sample(2.0, 0.0800, 0.0801, 0.02, 0.02, 0.01, 0.01)
    view, _ = _build_view(history=(*_run_history(20), crossing))

    drawn = [series for series in view._wash_in_segment_series if series.points]

    assert len(drawn) == 1
    assert drawn[0].points[-1].point is not None
    assert all(point.point is None for point in drawn[0].points[:-1])


def test_a_growing_wash_in_trace_carries_no_terminus_marker() -> None:
    """The live right-hand end of a run is not an ending.

    Marking it would put a dot on a point that moves every frame, and
    would say the curve had stopped when it is still being drawn.
    """

    view, _ = _build_view(history=_run_history(20))

    drawn = [series for series in view._wash_in_segment_series if series.points]

    assert len(drawn) == 1
    assert all(point.point is None for point in drawn[0].points)


def test_the_equilibrium_line_spans_the_window_at_one() -> None:
    """The reference the trace ends on, ruled where the ratio reaches one."""

    view, _ = _build_view(history=_run_history(6_000))
    line = view._equilibrium_line_series

    assert [point.y for point in line.points] == [
        WASH_IN_EQUILIBRIUM_RATIO,
        WASH_IN_EQUILIBRIUM_RATIO,
    ]
    assert [point.x for point in line.points] == [
        view._wash_in_chart.min_x,
        view._wash_in_chart.max_x,
    ]


def test_the_wash_in_trace_breaks_rather_than_drawing_across_a_gap() -> None:
    """A polyline through the drawn samples would invent the stretch it skipped.

    A vaporizer closed and later reopened leaves a run of samples where
    the ratio is outside its domain. Joining the wash-in either side of
    it with one line segment would draw values the run never produced -
    the synthesized trace the decimation is careful never to create,
    arriving through the gap instead.
    """

    washout = tuple(
        _sample(2.0 + index * SIMULATION_STEP_S, 0.010, 0.030, 0.02, 0.02, 0.01, 0.01)
        for index in range(10)
    )
    resumed = tuple(
        _sample(3.0 + index * SIMULATION_STEP_S, 0.080, 0.070, 0.02, 0.02, 0.01, 0.01)
        for index in range(10)
    )
    view, _ = _build_view(history=(*_run_history(20), *washout, *resumed))

    segments = _drawn_wash_in_segments(view)

    assert len(segments) == 2
    # No drawn segment spans the washout: each is wholly on one side of it.
    for segment in segments:
        times = [x for x, _ in segment]
        assert max(times) < 2.0 or min(times) >= 3.0


def test_the_wash_in_plot_shows_the_same_window_as_the_compartment_chart() -> None:
    """Two plots stacked on one time base must not be showing two spans."""

    view, _ = _build_view(history=_run_history(6_000))

    assert view._wash_in_chart.min_x == view._concentration_chart.min_x
    assert view._wash_in_chart.max_x == view._concentration_chart.max_x


def test_a_control_change_is_marked_on_the_wash_in_plot_too() -> None:
    """The caveat this trace carries is only visible if the marks are on it.

    F_A/F_I is the textbook curve while inspired concentration is held
    constant. A dial change is what breaks that, so a mark on the
    compartment chart alone leaves the plot that is actually being
    misread unannotated.
    """

    change = ControlChange(
        elapsed_s=1.0,
        sample_index=10,
        adjustment=1,
        control=ControlInput.DELIVERED,
        previous_value=0.02,
        new_value=0.04,
        unit=CONTROL_INPUT_UNITS[ControlInput.DELIVERED],
    )
    view, _ = _build_view(history=_run_history(40), control_timeline=(change,))

    marked = [
        series.points[0].x
        for series in view._wash_in_control_mark_series
        if series.points[0].x >= 0.0
    ]

    assert marked == [1.0]
    # And it spans this chart's own range, not the percent chart's.
    top = max(point.y for point in view._wash_in_control_mark_series[0].points)
    assert top == WASH_IN_AXIS_MAXIMUM


def test_the_wash_in_reading_is_the_value_the_trace_ends_at() -> None:
    """The sentence beside the plot and the plot cannot disagree."""

    history = _run_history(40)
    view, _ = _build_view(history=history)

    drawn_ratio = _wash_in_points(view)[-1][1]

    assert format_wash_in_ratio(drawn_ratio) in cast(str, view._wash_in_state_text.value)


def test_the_wash_in_plot_says_what_its_denominator_is() -> None:
    """Named at the point of display, because the graph invites the wrong one.

    A reader who has seen this curve in a textbook will assume the
    denominator is whatever was set on the vaporizer. It is not - it is
    the modelled circuit fraction, which approaches the dial over the
    circuit's own time constant - and the difference is the whole reason
    the trace rises the way it does early in a run.
    """

    view, page = _build_view()
    strings = " ".join(_mounted_interface_strings(view, page))

    assert "not the vaporizer dial" in strings
    assert "no dead space" in strings
    assert "held constant" in strings
    assert "Equilibrium, F_A = F_I" in strings


def test_a_real_run_draws_the_ratio_of_its_own_recorded_compartments() -> None:
    """End to end: real core, real step, real history, the drawn point.

    The trace is a derived clinical value, so what matters is not that
    the formula is right in isolation but that the number on the chart
    was produced from this run's own alveolar and circuit fractions.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.start()
    _advance_to(controller, 60.0)

    view = SimulationView(page=_FakePage(), controller=controller)
    snapshot = controller.snapshot()
    reading = read_wash_in(
        snapshot.alveolar_concentration_fraction, snapshot.circuit_concentration_fraction
    )

    assert reading.plotted_ratio is not None
    assert _wash_in_points(view)[-1] == (
        pytest.approx(snapshot.elapsed_s),
        pytest.approx(reading.plotted_ratio),
    )


# --- Stopping at the supported run length (PL-Y5WR) --------------------------


def test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed() -> None:
    """The whole point of the separate field: a correct stop reads as one.

    A run that reaches 24 hours has done everything right - the core refused
    the next step before taking it, nothing was miscalculated, nothing was
    rolled back. Presenting that as "simulation error" would spend the one
    signal this interface has for a real fault on a model that is working,
    and teach a reader to discount it when it matters.
    """

    view, _ = _build_view(
        is_running=False, supported_limit_reason="this run has reached 86400 s of simulated time"
    )

    assert view._status_text.value == "Stopped — supported run length reached"
    assert view._status_text.color != WARNING
    assert view._notice_text.visible is True
    assert view._notice_text.value is not None
    assert "supported run length of 24 hours" in view._notice_text.value


def test_the_supported_run_length_notice_does_not_describe_a_failure() -> None:
    """No step failed and none was rolled back, so neither may be claimed.

    The failure banner's wording is right for a failure and false here. A
    notice describing an event that did not happen is the presentation half
    of the safety-critical standard - the correct number under the wrong
    label - and it points the reader at the model's own limits rather than
    at an imagined defect.
    """

    view, _ = _build_view(
        is_running=False, supported_limit_reason="this run has reached 86400 s of simulated time"
    )

    notice = view._notice_text.value

    assert notice is not None
    assert "rolled back" not in notice
    assert "error" not in notice.lower()
    assert "failed" not in notice.lower()
    # It says *why* the limit is where it is: a boundary with no reason reads
    # as an arbitrary restriction rather than as the edge of the model.
    assert "metabolism" in notice
    assert "last completed step" in notice


def test_refresh_view_does_not_offer_to_resume_a_run_at_the_supported_limit() -> None:
    """The controller would refuse this Start, so the button must not offer it."""

    view, _ = _build_view(
        is_running=False, supported_limit_reason="this run has reached 86400 s of simulated time"
    )

    assert view._start_button.disabled is True


def test_a_failure_outranks_the_supported_run_length_in_the_notice() -> None:
    """Where both are somehow recorded, the more serious statement wins."""

    view, _ = _build_view(
        is_running=False,
        failure_reason="SimulationNumericalError: boom",
        supported_limit_reason="this run has reached 86400 s of simulated time",
    )

    assert view._status_text.value == "Stopped — simulation error"
    assert view._notice_text.value is not None
    assert "boom" in view._notice_text.value


def test_halt_run_routes_the_supported_run_length_away_from_failure() -> None:
    """`_halt_run` stops the run for every exception and mislabels none.

    The routing is the whole of the change, and a regression in it would not
    break the halt - the run still stops - it would only put "simulation
    error" over a model that stopped exactly where `docs/MODEL.md` says it
    must. Nothing but a test notices that.
    """

    controller = _recording_controller()
    view = SimulationView(page=_FakePage(), controller=controller)
    error = SimulationDomainLimitError("this run has reached 86400 s of simulated time")

    view._halt_run(error)

    assert controller.supported_limits == ["this run has reached 86400 s of simulated time"]
    assert controller.failures == []
    assert controller.is_running is False


def test_halt_run_still_treats_an_unrecognised_exception_as_a_failure() -> None:
    """The narrow case is the named one, so anything else falls through safely."""

    controller = _recording_controller()
    view = SimulationView(page=_FakePage(), controller=controller)

    view._halt_run(ValueError("mass balance violated"))

    assert controller.failures == ["ValueError: mass balance violated"]
    assert controller.supported_limits == []
