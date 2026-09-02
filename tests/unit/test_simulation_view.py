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

import flet as ft
import flet_charts as fch
import pytest

from anesthesia_sim.app.controller import (
    SimulationController,
    SimulationHistorySample,
    SimulationSnapshot,
)
from anesthesia_sim.app.simulation_view import (
    AVAILABLE_AGENTS,
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    FLOW_DISPLAY_DECIMALS,
    MAX_CHART_POINTS_PER_SERIES,
    METRIC_GRID_COLUMNS,
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SimulationView,
)
from anesthesia_sim.app.theme import ACCENT_TEXT, AGENT_COLOR_SCHEMES, MUTED, WARNING
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import SimulationNumericalError
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem


class _FakePage:
    """Stand-in exposing only the Page surface SimulationView uses."""

    def __init__(self) -> None:
        self.padding: int | None = None
        self.update_calls = 0
        # What `mount()` handed over, kept so a test can read the assembled
        # tree back. A real Page renders these; this one only holds them.
        self.controls: list[object] = []

    def add(self, *controls: object) -> None:
        self.controls.extend(controls)

    def update(self) -> None:
        self.update_calls += 1


class _FakeController:
    """Stand-in with a caller-controlled snapshot.

    Isolates view-formatting tests from the simulation engine so the
    accounting-failed branch can be exercised without needing to actually
    violate a physical invariant.
    """

    def __init__(self, snapshot: SimulationSnapshot) -> None:
        self.snapshot_value = snapshot
        self.is_running = snapshot.is_running

    def snapshot(self) -> SimulationSnapshot:
        return self.snapshot_value


def _sample(
    elapsed_s: float,
    circuit: float,
    alveolar: float,
    venous: float,
    vessel_rich: float,
    muscle: float,
    fat: float,
) -> SimulationHistorySample:
    return SimulationHistorySample(
        elapsed_s=elapsed_s,
        circuit_concentration_fraction=circuit,
        alveolar_concentration_fraction=alveolar,
        mixed_venous_concentration_fraction=venous,
        vessel_rich_partial_pressure_fraction=vessel_rich,
        muscle_partial_pressure_fraction=muscle,
        fat_partial_pressure_fraction=fat,
    )


def _snapshot(
    is_running: bool = False,
    passes_validation: bool = True,
    history: tuple[SimulationHistorySample, ...] | None = None,
    agent_id: str = "sevoflurane",
    agent_display_name: str = "Sevoflurane",
    max_delivered_concentration_percent: float = 8.0,
    failure_reason: str | None = None,
) -> SimulationSnapshot:
    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)

    latest = history[-1]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=latest.elapsed_s,
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=max_delivered_concentration_percent,
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=4.0,
        delivered_concentration_fraction=0.08,
        alveolar_ventilation_l_min=4.0,
        cardiac_output_l_min=5.0,
        circuit_concentration_fraction=latest.circuit_concentration_fraction,
        alveolar_concentration_fraction=latest.alveolar_concentration_fraction,
        mixed_venous_concentration_fraction=latest.mixed_venous_concentration_fraction,
        vessel_rich_partial_pressure_fraction=latest.vessel_rich_partial_pressure_fraction,
        muscle_partial_pressure_fraction=latest.muscle_partial_pressure_fraction,
        fat_partial_pressure_fraction=latest.fat_partial_pressure_fraction,
        delivered_agent_l=0.012345,
        exhausted_agent_l=0.002345,
        stored_agent_l=0.01,
        unaccounted_agent_l=1.5e-13,
        agent_accounting_absolute_error_l=1.5e-13,
        agent_accounting_passes_validation=passes_validation,
        concentration_history=history,
        failure_reason=failure_reason,
    )


def _build_view(snapshot: SimulationSnapshot) -> tuple[SimulationView, _FakePage]:
    page = _FakePage()
    view = SimulationView(page=page, controller=_FakeController(snapshot))
    return view, page


def test_the_shipped_step_is_within_the_maximum_simulation_step() -> None:
    """The interface may not run the model outside its supported domain.

    `SIMULATION_STEP_S` is this module's cadence and
    `MAXIMUM_SIMULATION_STEP_S` is `core/`'s applicability domain; they are
    separate decisions that happen to coincide today, and this is what stops
    them from parting company unnoticed. Before PL-VP7N the only statement
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
    which is how the splitting-error bound came to be measured over less than
    the interface could produce (PL-042) - and how, before PL-0MLQ, the
    floors could have moved and taken the bound's own worst case, a
    trajectory holding cardiac output at zero, out of the measured domain.

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


def test_format_percent_uses_the_documented_display_resolution() -> None:
    """Pin the PL-040 decision: 0.01 percentage points, uniformly.

    The resolution is justified in `docs/MODEL.md` § "Displayed precision"
    against the measured splitting error, so a change here is a change to a
    safety-critical claim about what the model can support — not a
    formatting preference. This test exists to make that change deliberate.
    """

    assert CONCENTRATION_DISPLAY_DECIMALS == 2
    assert CONCENTRATION_DISPLAY_RESOLUTION_PERCENT == pytest.approx(0.01)

    assert SimulationView._format_percent(0.0) == "0.00%"
    assert SimulationView._format_percent(1.0) == "100.00%"
    assert SimulationView._format_percent(0.0803456) == "8.03%"
    assert SimulationView._format_percent(0.02) == "2.00%"


def test_format_percent_rounds_rather_than_truncates() -> None:
    """The last displayed digit is the nearest one, not a truncation.

    Truncation would bias every reading downward by up to a full count of
    the uncertain digit, on top of the solver error the resolution is
    already chosen to sit above. Exact ties are not asserted: a decimal
    tie is not generally representable as a double, and the model's own
    error is many orders of magnitude larger than that distinction.
    """

    assert SimulationView._format_percent(0.021_39) == "2.14%"
    assert SimulationView._format_percent(0.021_31) == "2.13%"


def test_format_percent_marks_a_value_below_the_resolution() -> None:
    """A filling compartment must not read as an empty one.

    Muscle and fat sit under 0.01% for the opening minutes of every run.
    Rounding them to `0.00%` would assert the model holds zero there when
    it does not, so a positive value that rounds to zero is shown as below
    the resolution instead.
    """

    assert SimulationView._format_percent(1e-8) == "<0.01%"
    assert SimulationView._format_percent(4.0e-5) == "<0.01%"

    # Exactly zero is the one value that may read as zero: nothing has
    # reached the compartment, which is a fact the model does hold.
    assert SimulationView._format_percent(0.0) == "0.00%"

    # Either side of the rounding threshold, at half the resolution.
    assert SimulationView._format_percent(4.9e-5) == "<0.01%"
    assert SimulationView._format_percent(5.1e-5) == "0.01%"


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

    empty = SimulationView._format_percent(0.0)
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
        name_control, qualifier_control, panel_value_text = panel.content.controls
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

    view, _ = _build_view(_snapshot())

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
    view = SimulationView(page=page, controller=_FakeController(_snapshot()))

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

    view, _ = _build_view(_snapshot())

    panels = view._build_concentration_metrics().controls

    for panel in panels:
        name, qualifier, _value = panel.content.controls
        assert name.value, "a readout with no name"
        assert qualifier.value, "a readout that does not hold its gloss line open"
        assert qualifier.size < name.size
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
    view = SimulationView(page=page, controller=_FakeController(_snapshot()))

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


def test_format_percent_leaves_an_impossible_negative_visible() -> None:
    """A negative fraction cannot occur, and must not be disguised if it does.

    The compartment guards reject a negative amount, so reaching here means
    something upstream is wrong. The below-resolution form would render that
    as an ordinary small positive reading; `CLAUDE.md` requires the obvious
    failure instead.
    """

    assert SimulationView._format_percent(-1e-8) == "-0.00%"
    assert SimulationView._format_percent(-0.02) == "-2.00%"


def test_refresh_view_formats_every_concentration_metric() -> None:
    snapshot = _snapshot(
        history=(_sample(12.5, 0.02345, 0.01234, 0.00456, 0.00789, 0.00321, 0.00012),)
    )
    view, _ = _build_view(snapshot)

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
    view, _ = _build_view(_snapshot(is_running=is_running))

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
    view, _ = _build_view(_snapshot(history=history))

    for series, attribute in (
        (view._circuit_series, "circuit_concentration_fraction"),
        (view._alveolar_series, "alveolar_concentration_fraction"),
        (view._mixed_venous_series, "mixed_venous_concentration_fraction"),
        (view._vessel_rich_series, "vessel_rich_partial_pressure_fraction"),
        (view._muscle_series, "muscle_partial_pressure_fraction"),
        (view._fat_series, "fat_partial_pressure_fraction"),
    ):
        assert len(series.points) == len(history)

        for point, sample in zip(series.points, history, strict=True):
            assert point.x == pytest.approx(sample.elapsed_s)
            assert point.y == pytest.approx(getattr(sample, attribute) * 100.0)


def test_refresh_view_reports_valid_agent_accounting() -> None:
    view, _ = _build_view(_snapshot(passes_validation=True))

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
    view, _ = _build_view(_snapshot(passes_validation=False))

    assert view._agent_accounting_status_text.value == "Validation failed"
    assert view._agent_accounting_status_text.color == WARNING
    assert "unaccounted agent" in view._agent_accounting_detail_text.value


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown() -> None:
    view, _ = _build_view(_snapshot(agent_id="isoflurane", agent_display_name="Isoflurane"))
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

    view, _ = _build_view(_snapshot())
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
    view, _ = _build_view(_snapshot(agent_id=agent_id, agent_display_name=display_name))
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

    view, _ = _build_view(_snapshot(agent_id=agent_id, agent_display_name=agent_id.title()))
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    border = view._agent_header_badge.border
    assert border is not None
    assert border.top is not None
    assert border.top.color == scheme.foreground


def test_refresh_view_scales_slider_and_chart_to_agent_max() -> None:
    """Real vaporizer caps differ per agent (e.g. desflurane 18% vs isoflurane 5%);
    the delivered-concentration slider and the chart's y-axis must track it."""

    view, _ = _build_view(
        _snapshot(
            agent_id="desflurane",
            agent_display_name="Desflurane",
            max_delivered_concentration_percent=18.0,
        )
    )

    assert view._delivered_concentration_slider.max == 18.0
    assert view._concentration_chart.max_y == 18.0


def test_refresh_view_disables_agent_dropdown_while_running() -> None:
    view, _ = _build_view(_snapshot(is_running=True))

    assert view._agent_dropdown.disabled is True


def test_refresh_view_updates_delivered_concentration_label_for_current_agent() -> None:
    """Regression test: this label was found hardcoded to "Delivered
    sevoflurane" during manual browser verification of agent switching,
    left stale even after selecting a different agent."""

    view, _ = _build_view(_snapshot(agent_id="desflurane", agent_display_name="Desflurane"))

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
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._agent_dropdown.value = "desflurane"

    view._handle_agent_change(ft.Event(name="select", control=view._agent_dropdown))

    assert controller.snapshot().agent_id == "desflurane"
    assert view._agent_dropdown.value == "desflurane"
    assert view._subtitle_text.value is not None
    assert "Desflurane" in view._subtitle_text.value


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


def _run_history(sample_count: int) -> tuple[SimulationHistorySample, ...]:
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
        )
        for index in range(sample_count)
    )


def _all_series(view: SimulationView) -> tuple[fch.LineChartData, ...]:
    return (
        view._circuit_series,
        view._alveolar_series,
        view._mixed_venous_series,
        view._vessel_rich_series,
        view._muscle_series,
        view._fat_series,
    )


@pytest.mark.parametrize("sample_count", [3_000, 6_000, 18_000])
def test_chart_payload_is_bounded_however_long_the_run(sample_count: int) -> None:
    """The render payload must not grow with the length of the run."""

    view, _ = _build_view(_snapshot(history=_run_history(sample_count)))

    for series in _all_series(view):
        assert len(series.points) <= MAX_CHART_POINTS_PER_SERIES


def test_chart_sends_only_samples_inside_the_visible_window() -> None:
    """Sending samples the axis clips is payload the client cannot show."""

    history = _run_history(6_000)
    view, _ = _build_view(_snapshot(history=history))

    window_start_s = view._concentration_chart.min_x
    assert window_start_s > 0.0

    for series in _all_series(view):
        assert all(point.x >= window_start_s for point in series.points)


def test_chart_right_edge_matches_the_numeric_readout() -> None:
    """A trace ending before the newest sample would contradict the metrics."""

    history = _run_history(6_000)
    latest = history[-1]
    view, _ = _build_view(_snapshot(history=history))

    for series, value in (
        (view._circuit_series, latest.circuit_concentration_fraction),
        (view._alveolar_series, latest.alveolar_concentration_fraction),
        (view._mixed_venous_series, latest.mixed_venous_concentration_fraction),
        (view._vessel_rich_series, latest.vessel_rich_partial_pressure_fraction),
        (view._muscle_series, latest.muscle_partial_pressure_fraction),
        (view._fat_series, latest.fat_partial_pressure_fraction),
    ):
        assert series.points[-1].x == pytest.approx(latest.elapsed_s)
        assert series.points[-1].y == pytest.approx(value * 100.0)

    assert view._circuit_concentration_text.value == SimulationView._format_percent(
        latest.circuit_concentration_fraction
    )


def test_chart_traces_stay_bound_to_their_own_compartment() -> None:
    """Each trace must plot its own quantity, decimation notwithstanding."""

    history = _run_history(6_000)
    view, _ = _build_view(_snapshot(history=history))

    # Distinct constant multiples in _run_history make a swapped pairing show
    # up as a trace whose values belong to another compartment.
    for series, attribute in (
        (view._circuit_series, "circuit_concentration_fraction"),
        (view._alveolar_series, "alveolar_concentration_fraction"),
        (view._mixed_venous_series, "mixed_venous_concentration_fraction"),
        (view._vessel_rich_series, "vessel_rich_partial_pressure_fraction"),
        (view._muscle_series, "muscle_partial_pressure_fraction"),
        (view._fat_series, "fat_partial_pressure_fraction"),
    ):
        by_time = {sample.elapsed_s: getattr(sample, attribute) for sample in history}

        for point in series.points:
            assert point.y == pytest.approx(by_time[point.x] * 100.0)


def test_chart_keeps_every_sample_of_a_short_run() -> None:
    """Decimation must not kick in before the budget is actually exceeded."""

    history = _run_history(50)
    view, _ = _build_view(_snapshot(history=history))

    for series in _all_series(view):
        assert len(series.points) == len(history)


def test_chart_points_are_recorded_samples_not_interpolations() -> None:
    history = _run_history(6_000)
    recorded_times = {sample.elapsed_s for sample in history}
    view, _ = _build_view(_snapshot(history=history))

    for series in _all_series(view):
        assert all(point.x in recorded_times for point in series.points)
        assert [point.x for point in series.points] == sorted(point.x for point in series.points)


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
    steps_taken = len(stepped_by_the_loop.concentration_history) - 1
    assert steps_taken > 0

    for _ in range(steps_taken):
        reference.advance(SIMULATION_STEP_S)

    assert stepped_by_the_loop.elapsed_s == pytest.approx(reference.snapshot().elapsed_s)
    assert stepped_by_the_loop.alveolar_concentration_fraction == pytest.approx(
        reference.snapshot().alveolar_concentration_fraction
    )


# --- PL-018: a core failure must never leave a stale "Running" display ----


def _real_step_failure() -> SimulationNumericalError:
    """Capture the exception the core actually raises on a broken step.

    Reusing the real exception rather than inventing one keeps these tests
    tied to what `core/` does: if the core stopped raising a
    `SimulationNumericalError` here, this helper fails rather than letting
    the interface tests pass against a fiction.

    The step taken is a supported one. Since PL-VP7N a step outside the
    operator split's applicability domain is refused as a *configuration*
    error, which is a different thing entirely and is not what these tests
    are about: the interface has to halt a run whose numbers went bad
    mid-step, not one whose argument was rejected before it began. So the
    breakdown is reached the way a future parameter set could reach it -
    a compartment whose capacity one supported step overdraws - rather
    than by asking for a step nothing would grant.
    `tests/unit/test_uptake_system_failure.py` carries the same
    construction and the reasoning behind its numbers.
    """

    agent = load_agent_parameters("isoflurane")
    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem(
        circuit=BreathingCircuit(
            delivered_concentration_fraction=(agent.mac_percent / 100.0),
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=0.005,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )
    system.set_cardiac_output(10.0)

    try:
        system.advance(MAXIMUM_SIMULATION_STEP_S)
    except SimulationNumericalError as error:
        return error

    raise AssertionError("expected the coupled step to break down on these compartments")


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
        _snapshot(failure_reason="SimulationNumericalError: the step could not be completed")
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
    view, _ = _build_view(_snapshot(failure_reason="SimulationNumericalError: boom"))

    assert view._start_button.disabled is True
    assert view._pause_button.disabled is True


def test_refresh_view_shows_no_notice_for_an_ordinary_run() -> None:
    for snapshot in (_snapshot(is_running=True), _snapshot(is_running=False)):
        view, _ = _build_view(snapshot)

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
    """A controller that records `fail()` instead of running a simulation.

    `_halt_run` is the path that turns a raised exception into a stopped run
    and a visible banner. What matters is that it stops the run and records
    the reason, so that is what is recorded here.
    """

    def __init__(self, snapshot: SimulationSnapshot) -> None:
        super().__init__(snapshot)
        self.failures: list[str] = []

    def fail(self, reason: str) -> None:
        self.failures.append(reason)
        self.is_running = False


def test_halt_run_stops_the_session_and_records_the_exception_type() -> None:
    """The reason carries the type as well as the message.

    A bare message loses the difference between a modelling failure and a
    `TypeError` from a refactor, and the two want different responses from
    whoever reads the banner.
    """
    controller = _RecordingController(_snapshot())
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
    controller = _RecordingController(_snapshot())
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
    happens once, in the formatter. What limits the model is the splitting
    error, which is smaller than the last displayed digit in ordinary use.

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

        return snapshot.alveolar_concentration_fraction, SimulationView._format_percent(
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
