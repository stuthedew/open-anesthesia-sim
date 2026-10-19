"""The dashboard, driven headless against real runs.

`app/run_view.py` and `app/simulation_view.py` are the toolkit half of the
dashboard: every string and every per-tick claim is settled in
`app/dashboard_frame.py` without a toolkit, and `tests/unit/test_dashboard_frame.py`
holds it there. These tests hold the other half - that the widgets say what
the frame said, that a control a reader moves reaches the run it belongs to
and no other, that the two timer slots keep stepping and drawing apart, that
a refusal is a notice and a raise is a halt - against real
`SimulationController`s, under the `offscreen` platform `tests/conftest.py`
selects.

Ported by claim from the Flet suite this file replaces (`PL-25KS`), keeping
each surviving test's name where a closed item's verify line greps for it.
What is not carried is Flet's own mechanism: wire-protocol patch counts,
per-point tooltip objects, control identity across frames. The one count
that survives is `SimulationView.presented_frames`, which is what the
coalescing rule (`PL-R2YM`) is about.

The dashboard is shown at one fixed size before its first presentation,
because a frame is assembled from the plot's laid-out width and a widget
with no size has no pixels for the hover to measure against.
"""

import importlib
import re
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import replace
from typing import NoReturn

import pytest
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QBrush, QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSlider,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QLabel,
    QLayout,
    QLineEdit,
    QScrollArea,
    QSplitter,
    QStyle,
    QStyleOptionComboBox,
    QWidget,
)

from anesthesia_sim.app import control_timeline as control_timeline_module
from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app import theme
from anesthesia_sim.app.bookmarks import MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    HOVER_INSTANT_RESOLUTION_S,
    format_trace_hover,
)
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    time_base_for_span,
)
from anesthesia_sim.app.control_record import ControlChange
from anesthesia_sim.app.control_timeline import ControlAdjustment, group_adjustments
from anesthesia_sim.app.controller import BranchedCase, MarkForkPoint, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    BRANCH_AGENT_LOCK_TEXT,
    BRANCH_RUN_INDEX,
    COMPARING_AGENT_LOCK_TEXT,
    CONTROL_TIMELINE_HEADING,
    FORK_NOTHING_SELECTED_TEXT,
    HALT_FORK_LABEL_TEMPLATE,
    HERE_FORK_LABEL_TEMPLATE,
    INTERPRETATION_DISCLAIMER_TEXT,
    KEEP_CURRENT_CASE_TEMPLATE,
    MARK_STANDING_COMPARED_TEXT,
    MARK_STANDING_TEXT,
    MARK_STILL_RUNNING_TEXT,
    MAX_DISPLAYED_RUNS,
    NEW_CASE_CARRYOVER_TEMPLATE,
    NEW_CASE_IS_NOT_A_VIEW_TEXT,
    NO_CONTROL_CHANGES_TEXT,
    NO_MAC_TARGETS_TEXT,
    NO_TIME_BOOKMARKS_TEXT,
    NO_TRACES_SHOWN_TEXT,
    READOUT_PANELS,
    REFUSED_RESET_WAY_OUT_TEXT,
    REMOVE_NOTHING_SELECTED_TEXT,
    RESET_EXIT_TEXT,
    RESET_LABEL,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    START_NEW_CASE_TEMPLATE,
    STATUS_FAILED_TEXT,
    STATUS_PAUSED_TEXT,
    STATUS_SUPPORTED_LIMIT_TEXT,
    TRUNK_RUN_INDEX,
    ComparedRuns,
    ForkPoint,
    MarkListing,
    comparing_fork_lock_text,
    fork_offer,
    halt_notice,
    notice,
    run_label,
    slider_position,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_case_discard_warning,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_subtitle,
    format_time_base,
    format_wash_in_ratio,
    mac_multiple,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_chart import TimeBaseSelector, TraceLegend
from anesthesia_sim.app.qt_widgets import BookmarkDialog, MarkListingLabel, ParameterSlider
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import (
    ACCENT_TEXT,
    AGENT_COLOR_SCHEMES,
    AGENT_SELECTOR_WIDTH,
    INK,
    MARK_ROW_BULLET,
    MUTED,
    PANEL,
    WARNING,
)
from anesthesia_sim.app.unconditional_set import (
    INHALED_AGENT,
    UnconditionalValue,
    unconditional_set,
)
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART, PARAMETER_CONTROLS
from anesthesia_sim.app.views import AccountingView, ConcentrationView, WashInView
from anesthesia_sim.app.wash_in import read_wash_in
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core import supported_ranges as supported_ranges_module
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, MacMultiple, Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.units import SECONDS_PER_HOUR, SECONDS_PER_MINUTE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import AreaId, Split

# The identities a dashboard gives the first runs it places, in order, which
# render as "Run 1", "Run 2" and "Run 3". A run is named from its identity
# rather than from where it is drawn (`PL-7Z84`).
TEST_SESSION = SessionToken("0" * 32)
RUN_IDS = tuple(RunId(TEST_SESSION, number) for number in (1, 2, 3))
FIRST_RUN, SECOND_RUN = RUN_IDS[:2]
COMPARED = ComparedRuns(run_label(FIRST_RUN), run_label(SECOND_RUN))


# The size every dashboard here is shown at: wide enough for the seven
# readouts to stand side by side and for a chart column with pixels to
# measure hover distances in.
_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000

#: The two required glosses, restated rather than imported so an edit to the
#: application cannot move both sides of the assertion at once.
_ALVEOLAR_METRIC_QUALIFIER = "end-tidal-equivalent"
#: Any spelling of end-tidal not followed by the hedge, anywhere on screen.
_UNHEDGED_END_TIDAL = re.compile(r"end[\s-]?tidal(?!-equivalent)", re.IGNORECASE)

#: The index of each readout panel in the row, from the table the widgets are
#: built from, so a test names a compartment rather than a column number.
_READOUT_INDEX = {panel.quantity: index for index, panel in enumerate(READOUT_PANELS)}
_CLOCK_INDEX = _READOUT_INDEX[None]


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


#: The dashboards `_shown_view` built and has not yet deleted. A view left to
#: the garbage collector is deleted whenever a collection happens to run -
#: inside a later test's `show()`, or at interpreter shutdown after Qt's own
#: statics have gone - and either is a fatal error rather than a failure. So
#: a view is held here and deleted deliberately: before the next dashboard is
#: shown, and the last one in `_torn_down_views`, each time with the event
#: loop still able to deliver the deferred deletion. One at a time rather
#: than all at the end, because draining a hundred deferred deletions in one
#: call took twenty seconds where one takes twenty milliseconds.
_SHOWN_VIEWS: list[SimulationView] = []


def _delete_shown_views(application: QApplication) -> None:
    for view in _SHOWN_VIEWS:
        view.stop_timers()
        view.close()
        view.deleteLater()

    _SHOWN_VIEWS.clear()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


@pytest.fixture(scope="module", autouse=True)
def _torn_down_views(application: QApplication) -> Iterator[None]:
    yield

    _delete_shown_views(application)


# ------------------------------------------------------------------ helpers


def _concentration(view: SimulationView) -> ConcentrationView:
    """The concentration chart View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, ConcentrationView))


def _accounting(view: SimulationView) -> AccountingView:
    """The agent accounting View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, AccountingView))


def _wash_in(view: SimulationView) -> WashInView:
    """The F_A/F_I View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, WashInView))


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


def _advance_to(controller: SimulationController, elapsed_s: float) -> None:
    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)


def _shown_view(
    application: QApplication,
    *controllers: SimulationController,
    width_px: int = _WINDOW_WIDTH_PX,
    case: BranchedCase | None = None,
) -> SimulationView:
    """A dashboard over these runs, shown at the fixed size and presented once.

    The order is the one `main.py` follows: show, let the layout settle, then
    present, because the first frame reads the plot's laid-out width.
    """

    _delete_shown_views(application)
    view = SimulationView(controllers, case=case)
    _SHOWN_VIEWS.append(view)
    view.resize(width_px, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _settle(application: QApplication) -> None:
    """Deliver the deferred deletions and events an action has posted."""

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _widest_chord_px(view: SimulationView) -> int:
    """The widest gap, in plot pixels, between two consecutive drawn alveolar instants."""

    chart = _concentration(view).chart
    times, percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    xs = [
        chart.plot_pixel(time_s, percent)[0]
        for time_s, percent in zip(times, percents, strict=True)
    ]

    return max(right - left for left, right in zip(xs, xs[1:], strict=False))


def _page_of(view: SimulationView) -> QWidget:
    """The scrolling page the dashboard lays itself out on."""

    scroll = view.findChild(QScrollArea)
    assert scroll is not None, "the dashboard has no scroll area"
    page = scroll.widget()
    assert page is not None, "the scroll area holds no page"

    return page


def _record_panels(run: RunView) -> tuple[QWidget, QWidget]:
    """The accounting and control-change panels a run placed on the page, in that order.

    The accounting panel is in the sidebar beside the charts and the
    control-change panel in the unconditional region (`PL-NWTM`). Reached
    through the heading placed in each rather than through the build methods,
    so what the tests below measure is what the page holds whatever those
    methods hand back. A second call to the method that built both used to
    build panels with no parent and move the run's live labels into them
    (`PL-N67T`).
    """

    accounting = run._accounting_panels[0]._accounting_heading_text.parentWidget()
    timeline = run._control_timeline_heading_text.parentWidget()
    assert accounting is not None and timeline is not None, "a sidebar heading is in no panel"

    return accounting, timeline


def _setting_sections(view: SimulationView) -> list[QWidget]:
    """Each run's setting controls, in the column between the unconditional region and the Areas."""

    column = view._settings_column
    sections = [column.itemAt(index).widget() for index in range(column.count())]
    assert all(section is not None for section in sections), "the column holds a bare layout"

    return [section for section in sections if section is not None]


def _steps(run: RunView, ticks: int) -> None:
    for _ in range(ticks):
        run.step_tick()


def _read_the_alveolar_quotient_as(monkeypatch: pytest.MonkeyPatch, quotient: float) -> None:
    """Make every alveolar compartment answer `quotient` for its partial-pressure fraction.

    The one route left to a quotient outside 0 to 1: no supported setting
    reaches one (`core/concentration.py`), and since `PL-544D` an amount
    written past the capacity is refused at the write, so the quotient every
    alveolar compartment answers is replaced, for the snapshot and the stepper
    alike, rather than reached through the stored amount.
    """

    monkeypatch.setattr(
        AlveolarCompartment, "partial_pressure_fraction", property(lambda compartment: quotient)
    )


def _readout_value(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].value_label.text()


def _readout_secondary(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].secondary_label.text()


def _drag(control: ParameterSlider, value: float, decimals: int) -> None:
    """Move a slider the way a reader's drag reaches it: through the QSlider itself.

    Through the control the run actually holds and the signal it actually
    wired, so the tests assert the wiring as well as the effect: a handler
    bound to the wrong run is exactly the mistake a comparison of two runs
    has to be proof against.
    """

    control.slider.setValue(slider_position(value, decimals))


def _set_fresh_gas_flow(run: RunView, flow_l_min: float) -> None:
    _drag(run._setting_controls[0]._fresh_gas_flow_slider, flow_l_min, FLOW_DISPLAY_DECIMALS)


def _set_delivered_percent(run: RunView, percent: float) -> None:
    _drag(
        run._setting_controls[0]._delivered_concentration_slider,
        percent,
        CONCENTRATION_DISPLAY_DECIMALS,
    )


def _select_playback_rate(run: RunView, multiplier: int) -> None:
    combo = run._playback_rate_dropdown
    index = combo.findData(multiplier)
    assert index >= 0, f"the playback control does not offer {multiplier}x"
    combo.setCurrentIndex(index)


def _select_time_base(view: SimulationView, key: str) -> None:
    combo = _concentration(view).time_base_selector
    index = combo.findData(key)
    assert index >= 0, f"the time-base control does not offer {key!r}"
    combo.setCurrentIndex(index)


def _set_trace_shown(
    application: QApplication, view: SimulationView, quantity: RecordedQuantity, shown: bool
) -> None:
    """Check or uncheck one compartment in the legend, as a reader clicking would.

    Through the box, which is the route a click takes: the legend asks, and
    the dashboard's answer is what both the boxes and the chart then show
    (`PL-VN6M`). Once the two-compartment cap is holding, that answer keeps
    what was just asked for and drops the longest-standing selection.
    """

    _concentration(view).legend.set_compartment_shown(quantity, shown)
    application.processEvents()


def _paused_run_with_history(elapsed_s: float = 60.0) -> SimulationController:
    """A real, paused run holding both elapsed time and a recorded input.

    Both halves deliberately: `SimulationSnapshot.has_recorded_run` reads
    the two together, and a fixture carrying only one would leave the other
    unexercised by every test built on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, elapsed_s)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    controller.pause()

    return controller


def _branched_case(elapsed_s: float = 60.0) -> BranchedCase:
    """A case whose trunk is paused with a recorded run and two instants to fork at.

    `_paused_run_with_history` records one setting change, so the trunk holds
    a keyframe at induction and another at `elapsed_s` - which is what
    `BranchedCase.fork_points_s` offers and the only two instants
    `resumed_at` will open a branch at.
    """

    return BranchedCase(_paused_run_with_history(elapsed_s))


def _case_view(
    application: QApplication, case: BranchedCase, width_px: int = _WINDOW_WIDTH_PX
) -> SimulationView:
    """A dashboard opened over a case's trunk, the way `main()` opens one."""

    return _shown_view(application, case.trunk, width_px=width_px, case=case)


def _offered_fork_instants(view: SimulationView) -> tuple[float, ...]:
    """The instants the permanent selector holds, in the order it holds them."""

    selector = view._fork_panel.point_selector

    return tuple(float(selector.itemData(index)) for index in range(selector.count()))


def _take_fork(view: SimulationView, instant_s: float) -> None:
    """Choose an offered instant in the branch control and press its button.

    `findData` answers the first entry at that instant, which is a recorded
    control event wherever a mark stands at the same instant too, because
    `fork_offer` lists the control event first.
    """

    panel = view._fork_panel
    index = panel.point_selector.findData(instant_s)
    assert index >= 0, f"the branch control does not offer {instant_s} s"
    panel.point_selector.setCurrentIndex(index)
    panel.take_button.click()


def _select_fork_entry(view: SimulationView, label: str) -> None:
    """Choose the branch control's entry that reads `label`, as a reader picks it by its words."""

    selector = view._fork_panel.point_selector
    index = selector.findText(label)
    assert index >= 0, (
        f"the branch control offers no {label!r}; it offers "
        f"{[selector.itemText(row) for row in range(selector.count())]}"
    )
    selector.setCurrentIndex(index)


# The mark the halt tests stop the trunk on: later than the keyframe
# `_branched_case` records at 60 s, so the instant a branch opens at is not one
# of the trunk's keyframes and cannot be confused with one.
_HALT_MARK_S = 80.0

# A budget rather than "step until it stops": a test that fails by hanging
# reports nothing. 80 s from the trunk's 60 s is 200 steps, so this is ample.
_TRUNK_STEP_BUDGET = 1000


def _halted_trunk_case(application: QApplication) -> tuple[BranchedCase, SimulationView]:
    """A case whose trunk ran onto a mark the learner set and is standing on it.

    The sequence `docs/ARCHITECTURE.md` § "How a learner takes one" describes,
    in the order a learner does it: the trunk has a recorded run and a keyframe
    at 60 s, the learner marks a later instant, and the run is stepped until
    the mark halts it. The frame is drawn afterwards, so the panel under test
    is the one a learner would be looking at.
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_HALT_MARK_S), "the decision point"))
    case.trunk.start()

    for _ in range(_TRUNK_STEP_BUDGET):
        if case.trunk.snapshot().bookmark_halt is not None:
            break

        case.trunk.advance(SIMULATION_STEP_S)
    else:
        raise AssertionError(
            f"the trunk ran {_TRUNK_STEP_BUDGET} steps without halting on the mark at "
            f"{_HALT_MARK_S} s; it stands at {case.trunk.snapshot().elapsed_s} s"
        )

    view.present(False)

    return case, view


# The rewind tests' trunk records one setting change at 30 s and is paused at
# 120 s, so a mark between the two lies behind its clock at an instant it holds
# no keyframe for: the case `PL-W4XQ` asked for, which only the mark door can
# branch at.
_REWIND_CHANGE_S = 30.0
_REWIND_PAUSE_S = 120.0

# The mark set behind that clock, inside a step: 75.05 s is first reached by the
# step ending at 751 x 0.1 s, so the instant a branch taken there opens at is
# not the instant typed. Written as the product the clock forms rather than
# read from the controller, so the two are compared rather than copied.
_BEHIND_MARK_S = 75.05
_BEHIND_MARK_FORK_S = 751 * 0.1

# What the selector says for that mark, restated rather than built from
# `MARK_FORK_LABEL_TEMPLATE`, so an edit to the template cannot move both sides
# of an assertion at once.
_BEHIND_MARK_LABEL = f"{format_elapsed(_BEHIND_MARK_FORK_S)}, on your mark"


def _rewind_case(application: QApplication) -> tuple[BranchedCase, SimulationView, TimeBookmark]:
    """A case whose trunk is paused past a setting change, marked behind its clock.

    The owner's sequence at a minute's scale: paused at 3 h, a learner marks
    1 h to go back and try something else there. The mark is set after the
    clock has passed it, so no step crossed it and the trunk never halted on
    it; the frame is drawn afterwards, so the panel is the one a learner
    would be looking at.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, _REWIND_CHANGE_S)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance_to(trunk, _REWIND_PAUSE_S)
    trunk.pause()
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    mark = TimeBookmark(CaseInstant(_BEHIND_MARK_S), "what if")
    case.trunk.add_time_bookmark(mark)
    view.present(False)

    return case, view, mark


def _select_agent(run: RunView, agent_id: str) -> None:
    """Pick an agent from the selector, through the combo's own signal."""

    combo = run._agent_dropdown
    index = combo.findData(agent_id)
    assert index >= 0, f"the selector does not offer {agent_id!r}"

    if index == combo.currentIndex():
        # A combo reports no change on the same item, and a reader opening
        # and closing it on the running agent still reaches the handler.
        run._handle_agent_change(index)
    else:
        combo.setCurrentIndex(index)


def _colour_name(value: object) -> str:
    """One spelling for a colour however the widget layer stores it."""

    if isinstance(value, QBrush):
        value = value.color()

    if isinstance(value, QColor):
        return value.name().lower()

    return QColor(str(value)).name().lower()


def _identity_controls(run: RunView) -> tuple[QWidget, ...]:
    """The six controls `_apply_agent_color_scheme` writes, and nothing else."""

    return (
        run._agent_header_badge,
        run._subtitle_text,
        run._running_agent_display,
        run._running_agent_text,
        run._running_agent_lock_text,
        run._agent_dropdown,
    )


def _interface_strings(view: SimulationView) -> set[str]:
    """Every string the dashboard holds, hidden ones included: for what is never said."""

    return set(view.interface_strings())


def _visible_strings(view: SimulationView) -> set[str]:
    """The strings a reader can see now: for what the reader is told (`PL-904Y`)."""

    return set(view.visible_strings())


def _strings_of(widget: QWidget, skip: Sequence[QWidget]) -> set[str]:
    """Every string a widget subtree shows, skipping `skip` by identity."""

    strings: set[str] = set()
    widgets = [widget, *widget.findChildren(QWidget)]

    for child in widgets:
        if any(child is skipped for skipped in skip):
            continue

        if isinstance(child, QLabel | QAbstractButton):
            strings.add(child.text())
        elif isinstance(child, QComboBox):
            strings.update(child.itemText(index) for index in range(child.count()))

    return strings


def _strings_between(
    after: QWidget | None, before: QWidget, *, skip: Sequence[QWidget] = ()
) -> set[str]:
    """The strings laid out between two widgets of one column, in layout order.

    Walks the layout of the widget that holds `before`, recursing into
    nested layouts and into any widget that contains a boundary, so the
    result is what a reader passes between the two on screen.
    """

    column = before.parentWidget()
    assert column is not None, "the plot has no parent to walk"
    layout = column.layout()
    assert layout is not None, "the plot's parent has no layout to walk"
    strings: set[str] = set()
    collecting = after is None

    def contains(widget: QWidget, boundary: QWidget) -> bool:
        return widget is boundary or widget.isAncestorOf(boundary)

    def walk(items: QLayout) -> bool:
        nonlocal collecting

        for index in range(items.count()):
            item = items.itemAt(index)
            if item is None:
                continue
            nested = item.layout()
            widget = item.widget()

            if nested is not None:
                if walk(nested):
                    return True
                continue

            if widget is None:
                continue

            if widget is before:
                return True

            if after is not None and widget is after:
                collecting = True
                continue

            if contains(widget, before) or (after is not None and contains(widget, after)):
                inner = widget.layout()
                assert inner is not None
                if walk(inner):
                    return True
                continue

            if collecting:
                strings.update(_strings_of(widget, skip))

        return False

    assert walk(layout), "the walk never reached the plot it was to stop at"

    return strings


def _real_step_failure() -> SimulationNumericalError:
    """Capture the exception the core actually raises on a broken step.

    Reusing the real exception rather than inventing one keeps these tests
    tied to what `core/` does: if the core stopped raising a
    `SimulationNumericalError` here, this helper fails rather than letting
    the interface tests pass against a fiction. The failure is injected,
    because the exact propagator cannot carry a compartment out of range on
    its own (`PL-GS5X`); what is stood in for is what the guard remains
    cover for.
    """

    system = AgentUptakeSystem.for_agent("isoflurane")
    original = system.patient.fat

    class _FatThatRefusesTheStep(TissueGroup):
        def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
            super().set_partial_pressure_fraction(Fraction(-1.0))

    system.patient.fat = _FatThatRefusesTheStep(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=original.blood_gas_partition_coefficient,
        tissue_gas_partition_coefficient=original.tissue_gas_partition_coefficient,
    )

    try:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
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


def _with_stale_tissue_flows(controller: SimulationController, cardiac_output_l_min: float) -> None:
    """Make the tissue flows sum to `cardiac_output_l_min`, past the tissues' guard.

    Each tissue's perfusion fraction is scaled by `cardiac_output_l_min` over
    the patient's output, and written past the tissue's own guard. The patient
    keeps its output. The settings record that a run's definition opens on
    then refuses the tissue flows, because they no longer sum to the output.
    It refuses them at the next step and at Reset (`PL-M4M0`), and no setting
    repairs them. No guarded write can make this record now. Every flow is
    formed from the output (`PL-HQF5`), and a fraction is written once
    (`PL-Z0HN`). Until then, a tissue's `set_blood_flow` made it, and a
    cardiac output change repaired it. `_with_the_tissue_fractions_put_back`
    stands in for that repair.
    """

    patient = controller._state.uptake_system.patient
    scale = cardiac_output_l_min / patient.cardiac_output_l_min

    for tissue in patient.tissues:
        object.__setattr__(tissue, "perfusion_fraction", tissue.perfusion_fraction * scale)


def _with_the_tissue_fractions_put_back(controller: SimulationController) -> None:
    """Write back the reference adult's perfusion fractions, past the tissues' guard.

    The fractions are typed from `data/patients/reference_adult.json`. With
    them back, the settings record no longer refuses the tissue flows.
    """

    for tissue, fraction in zip(
        controller._state.uptake_system.patient.tissues, (0.76, 0.18, 0.06), strict=True
    ):
        object.__setattr__(tissue, "perfusion_fraction", fraction)


# ------------------------------------------------------- the constructor


def test_a_dashboard_refuses_to_be_built_with_no_run() -> None:
    """A dashboard with no run has no agent, no ruler and nothing to draw."""

    with pytest.raises(
        ValueError, match=re.escape("a dashboard displays at least one run; none was given")
    ):
        SimulationView(())


def test_a_dashboard_refuses_more_runs_than_may_be_displayed() -> None:
    """`ROADMAP.md` bounds the comparison at two, and the cap is why.

    At three runs the encoding that tells one from another has nothing left:
    colour and line style carry the compartment and line width is a two-level
    channel. A third curve would be drawn with nothing identifying it.
    """

    assert MAX_DISPLAYED_RUNS == 2

    with pytest.raises(
        ValueError,
        match=re.escape(f"3 runs given; at most {MAX_DISPLAYED_RUNS} may be displayed at once"),
    ):
        SimulationView(tuple(SimulationController() for _ in range(MAX_DISPLAYED_RUNS + 1)))


def test_a_dashboard_refuses_two_runs_on_different_agents() -> None:
    """One ×MAC ruler and one set of references cannot describe two agents.

    Two agents on one chart would leave one run's traces read against the
    other's divisor - a correct number under the wrong label, which
    `CLAUDE.md`'s standard treats as a failure of the value.
    """

    with pytest.raises(
        ValueError,
        match=re.escape(
            "every displayed run must be on the same agent, because they share one MAC axis "
            "and one set of clinical references; given desflurane, sevoflurane"
        ),
    ):
        SimulationView((SimulationController(), SimulationController(agent_id="desflurane")))


# --------------------------------------------------------- the transport


def test_every_transport_button_declares_its_own_foreground(application: QApplication) -> None:
    """None of the three is left to take its label colour from the host palette.

    `PL-DHBX`: a button that declares no foreground is drawn in Qt's palette
    `ButtonText` role, which follows the host appearance rather than this
    interface, and went near-white under macOS Dark while every surface around
    it stayed this light theme's. Both states are asserted because the defect
    arrived twice - declaring `:enabled` alone left the *unavailable* button
    still absent on the project owner's screen.

    `transport_button_stylesheet` carries the colours; this holds `RunView` to
    applying them, which is the half a test of the helper alone would not catch.
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    transport = (run._start_button, run._pause_button, run._reset_button)

    for button in transport:
        sheet = button.styleSheet()

        assert f"QPushButton:enabled {{ color: {INK}; }}" in sheet
        assert f"QPushButton:disabled {{ color: {MUTED}; }}" in sheet
        assert f"background-color: {PANEL}" in sheet


def test_start_pause_reset_handlers_drive_the_real_controller(application: QApplication) -> None:
    """Each button reaches the run through its own click, and draws its own frame."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    presented = view.presented_frames

    run._start_button.click()

    assert controller.is_running is True
    assert run._status_text.text() == "Running"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is True
    assert view.presented_frames == presented + 1

    _steps(run, 10)
    run._pause_button.click()

    assert controller.is_running is False
    assert run._status_text.text() == "Paused"
    assert view.presented_frames == presented + 2

    run._reset_button.click()

    assert controller.snapshot().elapsed_s == 0.0
    assert run._elapsed_time_text.text() == "0s"
    assert view.presented_frames == presented + 3


def test_the_status_word_is_drawn_in_its_own_emphasis(application: QApplication) -> None:
    """Running in accent, paused in muted: the word and its colour move together."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert MUTED in run._status_text.styleSheet()

    run._start_button.click()

    assert ACCENT_TEXT in run._status_text.styleSheet()
    assert MUTED not in run._status_text.styleSheet()


# ------------------------------------------------------------ the sliders


def test_the_integer_sliders_span_the_supported_input_ranges(application: QApplication) -> None:
    """Read off the constructed controls, not off module constants."""

    run = _shown_view(application, SimulationController()).runs[0]

    for control, minimum, maximum in (
        (
            run._setting_controls[0]._fresh_gas_flow_slider,
            MINIMUM_FRESH_GAS_FLOW_L_MIN,
            MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        ),
        (
            run._setting_controls[0]._alveolar_ventilation_slider,
            MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        ),
        (
            run._setting_controls[0]._cardiac_output_slider,
            MINIMUM_CARDIAC_OUTPUT_L_MIN,
            MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
    ):
        assert control.slider.minimum() == slider_position(minimum, FLOW_DISPLAY_DECIMALS)
        assert control.slider.maximum() == slider_position(maximum, FLOW_DISPLAY_DECIMALS)


def test_every_slider_endpoint_reaches_the_core_and_is_accepted(application: QApplication) -> None:
    """The interface must not offer a position the model refuses."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    for control in (
        run._setting_controls[0]._fresh_gas_flow_slider,
        run._setting_controls[0]._alveolar_ventilation_slider,
        run._setting_controls[0]._cardiac_output_slider,
        run._setting_controls[0]._delivered_concentration_slider,
    ):
        for endpoint in (control.slider.minimum(), control.slider.maximum()):
            control.slider.setValue(endpoint)

            assert run._rejected_setting_notice is None, (
                f"the core refused {endpoint}, an endpoint of a slider the interface offers: "
                f"{run._rejected_setting_notice}"
            )


def test_fresh_gas_flow_slider_forwards_value_to_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _set_fresh_gas_flow(run, 7.0)

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert run._setting_controls[0]._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"


def test_the_delivered_dial_reaches_the_core_as_the_percent_dialled(
    application: QApplication,
) -> None:
    """The dial is in percent and so is what the core holds (`PL-NJPB`).

    The model reads that as a fraction of one atmosphere, which is the
    magnitude the second assertion holds.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _set_delivered_percent(run, 6.5)

    assert controller.snapshot().delivered_concentration_percent == 6.5
    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.065)
    assert run._setting_controls[0]._delivered_concentration_slider.value_label.text() == "6.50%"


def test_alveolar_ventilation_slider_forwards_value_to_controller(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(run._setting_controls[0]._alveolar_ventilation_slider, 8.0, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().alveolar_ventilation_l_min == 8.0
    assert run._setting_controls[0]._alveolar_ventilation_slider.value_label.text() == "8.0 L/min"


def test_cardiac_output_slider_forwards_value_to_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(run._setting_controls[0]._cardiac_output_slider, 6.5, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().cardiac_output_l_min == 6.5
    assert run._setting_controls[0]._cardiac_output_slider.value_label.text() == "6.5 L/min"


def test_the_sliders_declare_an_adjustment_boundary_when_a_drag_begins(
    application: QApplication,
) -> None:
    """Without it two turns of one dial are one adjustment on the record.

    Each slider's press is wired to the boundary, so a second act on the
    same control after a press is a second adjustment. Observed through the
    controller rather than by inspecting the connection, which PySide6 does
    not expose.
    """

    for slider_name in (
        "_fresh_gas_flow_slider",
        "_delivered_concentration_slider",
        "_alveolar_ventilation_slider",
        "_cardiac_output_slider",
    ):
        controller = SimulationController()
        run = _shown_view(application, controller).runs[0]
        controller.start()
        controller.set_fresh_gas_flow(FreshGasFlow(3.0))
        controller.advance(SIMULATION_STEP_S)

        control: ParameterSlider = getattr(run._setting_controls[0], slider_name)
        control.slider.sliderPressed.emit()
        controller.set_fresh_gas_flow(FreshGasFlow(2.0))

        assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}, (
            f"{slider_name}'s press did not declare an adjustment boundary"
        )


def test_a_declared_boundary_reaches_the_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    controller.start()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.advance(SIMULATION_STEP_S)
    run._handle_adjustment_start()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}


def test_a_drag_of_one_slider_is_marked_and_listed_once(application: QApplication) -> None:
    """One act by the person, however many settings the model was stepped under."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _advance(controller, 10.0)

    run._setting_controls[0]._delivered_concentration_slider.slider.sliderPressed.emit()

    for percent in (3.0, 3.5, 4.0):
        _set_delivered_percent(run, percent)
        controller.advance(SIMULATION_STEP_S)

    view.present(False)

    assert len(run._control_timeline_text.text().splitlines()) == 1
    assert _concentration(view).chart.control_mark_times(0) == (pytest.approx(10.0),)
    assert _wash_in(view).chart.control_mark_times(0) == (pytest.approx(10.0),)


# ---------------------------------------------- refusals, and the halt


@pytest.mark.parametrize(
    ("dialled_percent", "refusal"),
    [
        (50.0, "vaporizer maximum"),
        (150.0, "delivered_concentration_percent of 150.0 is outside 0 to 100"),
    ],
    ids=["above the vaporizer maximum", "outside any percent"],
)
def test_a_refused_setting_is_reported_without_stopping_the_run(
    application: QApplication, dialled_percent: float, refusal: str
) -> None:
    """Isoflurane's vaporizer stops at 5%, so 50% must be refused, and 150% is no percent.

    Called on the handler rather than dragged, because the slider's own
    ceiling keeps both unreachable on the control - which is exactly why the
    handler needs its own cover. They are refused in different places: 50% by
    the circuit, against the vaporizer maximum, and 150% by `Percent` as the
    handler builds it. So the handler builds it inside the setting it applies,
    and names it: built before, its refusal would escape the handler, and no
    banner would say the setting was refused (`PL-4R3W`).
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()
    delivered_before = controller.snapshot().delivered_concentration_percent

    run._handle_delivered_concentration_change(dialled_percent)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Setting refused" in notice
    assert refusal in notice

    # The control must not keep showing a dial position the simulation is
    # not running at: that is the correct number under the wrong label.
    assert controller.snapshot().delivered_concentration_percent == delivered_before
    assert run._setting_controls[0]._delivered_concentration_slider.value() == pytest.approx(
        delivered_before
    )


def test_a_refusal_notice_clears_once_a_setting_is_accepted(application: QApplication) -> None:
    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]

    run._handle_delivered_concentration_change(50.0)
    assert run._notice_text.isHidden() is False

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert controller.snapshot().delivered_concentration_percent == 2.0


@pytest.mark.parametrize(
    ("handler_name", "slider_name"),
    [
        ("_handle_fresh_gas_flow_change", "_fresh_gas_flow_slider"),
        ("_handle_alveolar_ventilation_change", "_alveolar_ventilation_slider"),
        ("_handle_cardiac_output_change", "_cardiac_output_slider"),
    ],
)
def test_every_slider_handler_refuses_without_escaping_into_the_toolkit(
    application: QApplication, handler_name: str, slider_name: str
) -> None:
    """No setting slot may let a core raise reach Qt's dispatcher.

    The sliders' own bounds keep a negative flow unreachable in the running
    app, which is exactly why the guard needs its own cover: an exception
    escaping a slot is lost under PySide6 rather than shown.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    getattr(run, handler_name)(-1.0)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Setting refused" in notice
    control: ParameterSlider = getattr(run._setting_controls[0], slider_name)
    assert control.value() >= 0.0


def test_a_refused_setting_reaches_the_notice_through_apply_setting(
    application: QApplication,
) -> None:
    """A `SimulationConfigurationError` is a refusal: the run is untouched."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def refuse() -> None:
        raise SimulationConfigurationError("a value the core refused")

    run._apply_setting(refuse)

    assert controller.has_failed is False
    assert controller.is_running is True
    assert run._rejected_setting_notice == "Setting refused — a value the core refused"


def test_an_execution_error_in_a_setting_halts_the_run_through_apply_setting(
    application: QApplication,
) -> None:
    """`PL-V6M0`: an execution error is not a refusal and must not read as one."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def explode() -> None:
        raise SimulationExecutionError("the run cannot continue safely")

    run._apply_setting(explode)

    assert controller.snapshot().failure_reason == (
        "SimulationExecutionError: the run cannot continue safely"
    )
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_a_domain_limit_in_a_setting_reaches_the_supported_limit_channel_through_apply_setting(
    application: QApplication,
) -> None:
    """A domain limit stops the run as a limit, never as a failure (`PL-Y5WR`)."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def limit() -> None:
        raise SimulationDomainLimitError("this run has reached 86400 s of simulated time")

    run._apply_setting(limit)

    assert controller.snapshot().supported_limit_reason == (
        "this run has reached 86400 s of simulated time"
    )
    assert controller.has_failed is False
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_a_type_error_in_a_setting_halts_the_run_through_apply_setting(
    application: QApplication,
) -> None:
    """`PL-YK2V`: a raise from outside the project hierarchy still halts the run."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def explode() -> None:
        raise TypeError("a future refactor changed a signature")

    run._apply_setting(explode)

    assert controller.snapshot().failure_reason == (
        "TypeError: a future refactor changed a signature"
    )
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_halt_run_stops_the_session_and_records_the_exception_type(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    run._halt_run(ValueError("mass balance violated"))

    assert controller.snapshot().failure_reason == "ValueError: mass balance violated"
    assert controller.is_running is False


def test_halt_run_survives_a_render_failure_and_leaves_the_run_stopped(
    application: QApplication,
) -> None:
    """A halt that cannot draw its frame is still a halt."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    def explode() -> None:
        raise RuntimeError("the page is gone")

    view._refresh_view = explode  # type: ignore[method-assign]

    run._halt_run(ValueError("mass balance violated"))

    assert controller.snapshot().failure_reason == "ValueError: mass balance violated"
    assert controller.is_running is False


# -------------------------------------------------------------- the loops


def test_simulation_loop_advances_without_rendering(application: QApplication) -> None:
    """Stepping must not be gated on drawing."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    _steps(view.runs[0], 3)

    assert controller.snapshot().elapsed_s > 0.0
    assert view.presented_frames == presented


def test_render_loop_draws_without_advancing(application: QApplication) -> None:
    """Drawing must not move simulation time."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    view.render_tick()
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames >= presented + 1


def test_neither_loop_does_anything_while_paused(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    _steps(view.runs[0], 2)
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames == presented


def test_a_dragged_slider_leaves_its_frame_to_the_render_tick(application: QApplication) -> None:
    """`PL-R2YM`: a drag updates its own readout at once and defers the frame.

    What must still be immediate is the view beside the dial, which has to
    agree with the snapshot the moment the setting is applied (`PL-018`).
    What waits is the presentation - chart assembly, draw and captions.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames

    _set_fresh_gas_flow(run, 7.0)

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert run._setting_controls[0]._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"
    assert view.presented_frames == presented
    assert view._render_pending is True


def test_a_refused_slider_change_draws_its_own_frame(application: QApplication) -> None:
    """The one state the coalescing rule may not defer.

    A refused setting is the only case where the dial on screen and the
    simulation disagree; waiting even a tick there leaves a control stating
    a setting the run is not using.
    """

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    presented = view.presented_frames

    run._handle_delivered_concentration_change(50.0)

    assert run._notice_text.isHidden() is False
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_frame_that_clears_a_refusal_is_drawn_too(application: QApplication) -> None:
    """The same fault backwards: a notice left up after it stopped being true."""

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]

    run._handle_delivered_concentration_change(50.0)
    presented = view.presented_frames

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert view.presented_frames == presented + 1


def test_a_discrete_action_still_draws_its_own_frame(application: QApplication) -> None:
    """Only a control that reports continuously coalesces."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    view.runs[0]._start_button.click()

    assert controller.is_running
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_render_tick_draws_a_pending_change_while_the_run_is_stopped(
    application: QApplication,
) -> None:
    """The bound has to hold on the pause-change-resume route as well.

    Paused there is no run to draw, but there is still a dial moving, so the
    tick fires for a change that is owed a frame - and stops once it has.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)

    _set_fresh_gas_flow(view.runs[0], 7.0)
    assert view._render_pending is True
    presented = view.presented_frames

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert view._render_pending is False

    view.render_tick()

    assert view.presented_frames == presented + 1, (
        "the tick kept drawing a paused run with nothing owed"
    )


def test_simulation_time_does_not_depend_on_render_cadence(application: QApplication) -> None:
    """Identical step counts must give identical results, however drawing goes.

    `PL-VM40`: simulation time is a function of steps taken, never of the
    wall clock or of how many frames were drawn between them.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    for _ in range(5):
        view.runs[0].step_tick()
        view.render_tick()

    steps_taken = round(controller.snapshot().elapsed_s / SIMULATION_STEP_S)
    reference = SimulationController()
    reference.start()
    _advance(reference, steps_taken * SIMULATION_STEP_S)

    assert controller.snapshot().elapsed_s == reference.snapshot().elapsed_s
    assert (
        controller.snapshot().alveolar_partial_pressure_fraction
        == reference.snapshot().alveolar_partial_pressure_fraction
    )


def test_the_run_loop_takes_one_step_per_tick_at_real_time_and_never_catches_up(
    application: QApplication,
) -> None:
    """A late tick must cost the run real time, never change its trajectory.

    How many steps a tick takes is the reader's playback setting rather
    than a function of how long the tick took, so a host that wakes it late
    leaves the run behind the wall clock and it stays behind.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    ticks = 7
    _steps(view.runs[0], ticks)

    assert controller.snapshot().elapsed_s == ticks * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == ticks


@pytest.mark.parametrize(
    "rate",
    SUPPORTED_PLAYBACK_RATES,
    ids=[f"{rate.multiplier}x" for rate in SUPPORTED_PLAYBACK_RATES],
)
def test_the_run_loop_takes_the_playback_rates_steps_per_tick(
    application: QApplication, rate: PlaybackRate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The multiplier is steps per tick, and the step never moves (`PL-SN2C`)."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = rate
    controller.start()

    steps_requested: list[float] = []
    advance = controller.advance

    def recording_advance(simulation_step_s: float) -> None:
        steps_requested.append(simulation_step_s)
        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", recording_advance)

    ticks = 3
    _steps(view.runs[0], ticks)

    steps_per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    expected_steps = ticks * steps_per_tick

    assert steps_per_tick == rate.multiplier
    assert len(steps_requested) == expected_steps
    assert set(steps_requested) == {SIMULATION_STEP_S}
    assert controller.snapshot().elapsed_s == expected_steps * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == expected_steps


def test_a_failed_step_abandons_the_rest_of_its_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A burst is not a licence to step past a step the core could not take.

    The run must stop on the last completed step, exactly as it does at real
    time, and nothing after the raise runs in this tick or the next.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = playback_rate_for(60)
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

    _steps(view.runs[0], 2)

    assert calls == 5
    assert controller.snapshot().elapsed_s == 4 * SIMULATION_STEP_S
    assert controller.is_running is False


def test_a_failed_step_stops_the_run_instead_of_killing_the_loop(application: QApplication) -> None:
    """`PL-018`: a core failure must never leave a stale "Running" display."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames

    _steps(run, 3)

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    assert WARNING in run._status_text.styleSheet()
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "SimulationNumericalError" in notice
    # The failure was drawn, not just recorded.
    assert view.presented_frames >= presented + 1


def test_the_simulation_loop_survives_a_failure_so_reset_can_restart_it(
    application: QApplication,
) -> None:
    """The tick slot must keep working after a halt, or Reset restarts nothing."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    _steps(run, 3)
    assert controller.has_failed is True

    run._reset_button.click()
    run._start_button.click()
    _steps(run, 3)

    assert controller.has_failed is False
    assert controller.snapshot().elapsed_s > 0.0
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is True


def test_a_failed_render_stops_the_run_rather_than_freezing_the_display(
    application: QApplication,
) -> None:
    """A dead render loop over a live simulation is the mirror failure."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("chart series could not be updated")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    view.render_tick()
    view.render_tick()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert "RuntimeError" in notice


def test_a_frame_that_cannot_be_drawn_on_a_discrete_action_halts_every_run(
    application: QApplication,
) -> None:
    """A discrete action presents through a signal, and a slot's raise is printed and dropped.

    So the immediate presentation guards itself as the render tick does:
    without that, a frame that could not be drawn for a playback change
    would leave every run advancing behind a display that had stopped.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("the frame could not be built")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    _select_playback_rate(view.runs[0], SUPPORTED_PLAYBACK_RATES[-1].multiplier)

    assert failures_left == [0], "the playback change did not present at once"

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        assert controller.snapshot().failure_reason == "RuntimeError: the frame could not be built"

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError" in notice


def test_a_halt_whose_frame_cannot_be_drawn_is_still_shown_on_every_run(
    application: QApplication,
) -> None:
    """The frame is the shared render path, and a halt for its raise cannot wait for it.

    Every controller is failed; what a reader has to see is the status word
    and the banner saying so, which need no frame. With one run's refresh
    raising on every attempt, the halt's own presentation raises too and is
    swallowed - and before `present_halt`, both status words went on
    reading the state before the raise with no banner under either.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    def failing_refresh(snapshot: object, frame: object, run_index: int) -> None:
        raise RuntimeError("this run's widgets could not be written")

    view.runs[0].refresh = failing_refresh  # type: ignore[method-assign]

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError: this run's widgets could not be written" in notice
        assert run._pause_button.isEnabled() is False
        assert run._start_button.isEnabled() is False


# ------------------------------------------ a run that stops itself (PL-T995)
#
# Driven through the dashboard's own timers and the Start button, because a
# test that steps the controller and presents by hand draws the very frame
# this path never asked for.

#: How long a real-timer test waits for what it is waiting on before failing
#: rather than hanging: ample beside the half second of play each one needs.
_REAL_TIMER_BUDGET_S = 10.0

#: Half a second of 1x play past the 60 s `_branched_case` pauses at, so the
#: step timer reaches it in five ticks.
_TIMED_STOP_S = 60.5


def _render_ticks(view: SimulationView) -> list[None]:
    """A list the dashboard's render timer appends to each time it fires, after `render_tick`."""

    fired: list[None] = []
    view._render_timer.timeout.connect(lambda: fired.append(None))

    return fired


def _run_the_timers_until(condition: Callable[[], bool], what: str) -> None:
    """Let the dashboard's own timers fire until `condition` holds, or fail naming `what`."""

    deadline = time.monotonic() + _REAL_TIMER_BUDGET_S

    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError(
                f"{_REAL_TIMER_BUDGET_S:g} s of the real timers passed without {what}"
            )

        QTest.qWait(10)


def _play_until_it_stops(view: SimulationView, trunk: SimulationController) -> None:
    """Press Start, let the timers play until the trunk stops itself, then one render tick more."""

    ticks = _render_ticks(view)
    view.start_simulation_timer()

    try:
        view.runs[0]._start_button.click()
        _run_the_timers_until(lambda: not trunk.is_running, "the trunk stopping itself")
        ticks.clear()
        _run_the_timers_until(lambda: bool(ticks), "a render tick after the trunk stopped")
    finally:
        view.stop_timers()


def test_a_run_that_halts_on_a_mark_under_its_own_timers_is_redrawn(
    application: QApplication,
) -> None:
    """A halt inside `step_tick` asks for no frame, and the next render tick draws one anyway.

    The halt changes the run's record, which the tick compares against what
    the run's view last wrote (`PL-X7D5`). Before that the tick drew only
    while a run ran or a frame was owed, so the screen read "Running" with
    Pause offered, the clock a step short and no offer to branch where the
    run stood, until the learner pressed something (`PL-T995`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_TIMED_STOP_S), "the decision point"))

    _play_until_it_stops(view, case.trunk)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None, "the trunk stopped, but not on its mark"
    run = view.runs[0]
    stood_at = format_elapsed(halt.instant_s)

    assert run._status_text.text() == STATUS_PAUSED_TEXT
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() == stood_at
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is True
    assert view._fork_panel.here_button.isHidden() is False
    assert view._fork_panel.here_button.text() == HALT_FORK_LABEL_TEMPLATE.format(instant=stood_at)


def test_a_run_that_arrives_at_the_supported_run_length_under_its_own_timers_is_redrawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other stop `step_tick` makes without a raise, drawn the same way.

    `SimulationController.advance` halts a run on the step that lands it on
    the supported run length and raises nothing, so `RunView._halt_run`, the
    one branch of `step_tick` that asked for a frame, is never reached
    (`PL-T995`). The span is shortened to end half a second past the trunk's
    pause, because the timers would take a day to reach the real one and
    stepping a run to a step short of it takes about 27 s. `maximum_step_count`
    is the one count the controller and the core both read the span from, so
    the two agree on the shortened one; where a run stops on the real span is
    `test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step`'s.
    """

    case = _branched_case()
    view = _case_view(application, case)
    last_step = round(_TIMED_STOP_S / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )

    _play_until_it_stops(view, case.trunk)

    assert case.trunk.has_reached_supported_limit is True
    run = view.runs[0]

    assert run._status_text.text() == STATUS_SUPPORTED_LIMIT_TEXT
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() == format_elapsed(_TIMED_STOP_S)
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False
    assert run._notice_text.notice() is not None


def test_a_frame_that_keeps_failing_is_attempted_once_not_every_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The halt stores the record it states, so the comparison does not re-halt the run every tick.

    A frame that raises halts every run, and the halt is then what the screen
    states. Were a run's record stored only where a frame draws, the failed
    run would differ from its view's record on every tick after, and the
    tick would assemble, fail and halt again five times a second for as long
    as the dashboard stood (`PL-X7D5`). The two attempts are the tick's and
    the one retry `SimulationView._halt_every_run` makes.
    """

    case = _branched_case()
    view = _case_view(application, case)
    attempts: list[None] = []

    def failing_assembly(*args: object, **kwargs: object) -> NoReturn:
        attempts.append(None)
        raise RuntimeError("this frame could not be assembled")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", failing_assembly)
    ticks = _render_ticks(view)
    view.start_simulation_timer()

    try:
        case.trunk.start()
        _run_the_timers_until(lambda: case.trunk.has_failed, "the failing frame halting the run")
        attempted = len(attempts)
        ticks.clear()
        _run_the_timers_until(lambda: len(ticks) >= 5, "five render ticks after the halt")
    finally:
        view.stop_timers()

    assert attempted == 2
    assert len(attempts) == attempted, "the failed frame was attempted again on a later tick"
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT


def test_a_halt_is_shown_when_the_snapshot_itself_is_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt stated from a fresh snapshot is not stated at all when the snapshot is what refused.

    `snapshot()` builds every compartment's fraction, so an alveolar quotient
    above 1 - reached by replacing what the compartment answers, since no
    supported setting takes one (`core/concentration.py`) and a write past the
    capacity is refused since `PL-544D` - refuses the snapshot and, through
    it, the frame. Before `PL-7DJK`,
    `present_halt` read a fresh snapshot for the status word, the transport
    and the banner, so the same refusal escaped the render tick with the
    controller failed and the screen reading "Running", Pause offered and no
    banner. The three are now written from `SimulationController.record()`,
    which no compartment value is built for, and the banner says no frame of
    the stopped run could be drawn rather than that a step was rolled back.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    view.render_tick()

    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    view.render_tick()

    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)

    with pytest.raises(SimulationConfigurationError, match="alveolar partial_pressure_fraction"):
        controller.snapshot()

    run = view.runs[0]

    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert "No frame of the stopped run could be drawn" in notice
    assert "rolled back" not in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False


def test_an_agent_change_on_a_halted_run_restates_the_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A pick on a run halted by its own snapshot is answered by that halt, not a raise Qt prints.

    `_handle_agent_change` reads the snapshot to decide between nothing, a
    new case and a question, inside a slot; on a run whose snapshot refuses
    (`PL-7DJK`) the read raised there, so the toolkit printed the traceback
    and the pick was accepted with nothing on screen answering it: no
    dialog, and the selector naming an agent the run is not of (`PL-V2HC`).
    The read now halts the run on the raise - the halt it is already in,
    whose first reason the controller keeps - and restates it, and the
    selector is put back to the running agent, which the controller names
    since the snapshot cannot. Reset stays the way out the banner names.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    view.render_tick()
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    view.render_tick()
    run = view.runs[0]
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    assert run._status_text.text() == "Stopped — simulation error"
    capfd.readouterr()

    _select_agent(run, "desflurane")

    assert "Traceback" not in capfd.readouterr().err
    assert run._new_case_dialog is None
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert controller.agent_id == "sevoflurane"
    status = controller.status()
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert run._start_button.isEnabled() is False
    assert run._reset_button.isEnabled() is True


def test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """The labels a dragged slider owes at once come from the snapshot; its refusal is the halt.

    `_apply_setting` rewrites this run's own labels after a coalesced change
    from a snapshot read once the setting has been applied, outside the gate
    the setting went through, so on a paused run whose snapshot refuses
    (`PL-7DJK`) the drag was accepted and the read raised out of the slot:
    the dial moved, the status word read "Paused" over a run no frame could
    draw, and the toolkit printed what nothing on screen said (`PL-V2HC`).
    The read now halts the run and states the halt from the controller's
    status - the first statement of it here, since a paused run draws no
    frame to refuse.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert run._status_text.text() == "Paused"
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert "Traceback" not in capfd.readouterr().err
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False


def test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """The value printed beside a dial dragged into a halt is the value the dial and the run hold.

    `_apply_setting` applies the setting, then the snapshot read that would
    rewrite the labels halts the run instead and no frame draws, so the
    value label - written only through `set_setting` - kept the value before
    the drag beside a dial standing at the new one: "2.0 L/min" beside a
    dial at 4.0 with the circuit holding 4.0, until Reset (`PL-85LJ`, found
    at `PL-V2HC`'s review). The halt now writes every dial from
    `SimulationController.record()`, which builds no compartment value,
    so the label, the dial and the run agree.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    dial = run._setting_controls[0]._fresh_gas_flow_slider
    assert dial.value_label.text() == "2.0 L/min"
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    assert controller.settings().fresh_gas_flow_l_min == 4.0
    assert dial.value() == 4.0
    assert dial.value_label.text() == "4.0 L/min"


def test_a_halt_is_stated_before_its_dials_are_written(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The status word, the transport and the banner are on screen before a dial is written.

    `present_halt` writes the dials through `dashboard_frame.setting_readouts`,
    which raises for a control that can offer no setting - a fresh gas flow
    range narrower than the dial's 0.1 L/min step, which no shipped machine
    declares and the circuit refuses at build. Written before the banner,
    that raise left the halt half stated, the status word and the transport
    written and no banner, and escaped the slot (found at `PL-85LJ`'s
    review). The dials come last, so the three statements of the halt are
    on screen before the raise, which still escapes rather than hiding.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )
    controller.fail("RuntimeError: step exploded")

    with pytest.raises(ValueError, match="can offer no setting"):
        run.present_halt()

    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Simulation stopped" in notice
    assert "step exploded" in notice


def _failing_assembly(*args: object, **kwargs: object) -> NoReturn:
    """Stands in for `assemble_chart_frame` where every frame is to fail."""

    raise RuntimeError("this frame could not be assembled")


def test_a_halt_after_an_agent_change_names_one_agent(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run halted on the first frame after an agent change names that agent everywhere.

    A run that has recorded nothing switches agent at once on a pick, so the
    frame that follows is the first to show the new agent. With it failing,
    `present_halt` is the only writer, and it wrote the dials and nothing of
    the agent's identity: "Delivered desflurane" under a subtitle, a chip
    and a heading still naming sevoflurane, in sevoflurane's colours
    (`PL-1YDD`). It now writes every identity widget from the controller's
    record.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    scheme = AGENT_COLOR_SCHEMES["desflurane"]

    _select_agent(run, "desflurane")

    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert (
        run._setting_controls[0]._delivered_concentration_slider.name_label.text()
        == "Delivered desflurane"
    )
    assert run._subtitle_text.text() == format_subtitle("Desflurane")
    assert run._running_agent_text.text() == "Desflurane"
    assert run._compartment_substance_text.text() == "Modelled concentrations: Desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control


def test_a_drag_that_halts_the_run_lists_the_record_the_run_holds(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control-change panel of a run halted by a drag lists the changes the run holds.

    `_paused_run_with_history` leaves the fresh gas flow change it records
    open, so dragging the dial back to where it started takes that change off
    the record. On a run whose snapshot refuses, the drag halts the run and
    no frame draws, and the panel went on listing the change the run no
    longer held (`PL-DTJQ`). The halt now writes the panel from the
    controller's record, with no undrawn marks, since no frame drew.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]
    assert run._control_timeline_text.text() != NO_CONTROL_CHANGES_TEXT
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    _set_fresh_gas_flow(run, 4.0)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert controller.record().control_timeline == ()
    assert run._control_timeline_text.text() == NO_CONTROL_CHANGES_TEXT
    assert run._control_timeline_overflow_text.isHidden() is True


#: The widget attributes of a `RunView` that may read differently on a run
#: drawn by a frame and on the same run halted with every frame failing, each
#: against the reason it may. Every other widget attribute - one added later
#: included - is held by the test below to read alike on both, which is what
#: makes `RunView._write_statement` the one writer of a run's state rather
#: than a list somebody has to keep: a widget left out of it reads the last
#: frame's run on a halt, and fails there (`PL-X7D5`).
#:
#: Held live in both directions, as `FOREGROUND_NOT_DECLARED` is: an entry
#: naming no widget attribute fails, and so does one whose widget reads alike
#: on the two runs, since nothing then needs the exemption. The accounting
#: panel's status and detail lines are frame widgets and are not listed for
#: that reason: both runs below read "Valid", so the comparison holds them
#: like any other widget.
FRAME_WIDGETS: dict[str, str] = {
    "_readout_row": (
        "the readouts and the clock they were read with, from the compartment "
        "values of the snapshot a frame drew from. The clock stays with its "
        "readouts, so no row pairs one instant's clock with another's values."
    ),
    "_accounting_panels[0]._agent_amounts_text": (
        "the accounting panel's amounts, which are the snapshot's mass balance "
        "and so compartment values."
    ),
    "_off_scale_lines[0]": (
        "which drawn traces are above the plot, read from the points the frame "
        "drew (`dashboard_frame.off_scale_notice`)."
    ),
    "_wash_in_state_lines[0]": (
        "what the wash-in plot shows, from the snapshot's alveolar and inspired "
        "fractions and the frame's undrawn stretches."
    ),
    "_notice_text": (
        "the banner. `_write_statement` writes it on both paths, worded for "
        "whether a frame drew: `halt_notice` says no frame of the stopped run "
        "has, and `notice` says the values shown are the last completed step. "
        "The test below holds each to its own wording."
    ),
}


def _widget_attributes(run: RunView) -> dict[str, QWidget]:
    """Every widget a `RunView` holds as an attribute, by name, and each of a tuple of them.

    Each live copy of a run surface is included with every widget it holds,
    named by its place in the run's list of copies (`PL-9LNF`).
    """

    widgets: dict[str, QWidget] = {}

    for name, value in vars(run).items():
        if isinstance(value, QWidget):
            widgets[name] = value
        elif isinstance(value, tuple) and value and all(isinstance(v, QWidget) for v in value):
            widgets.update({f"{name}[{index}]": item for index, item in enumerate(value)})
        elif isinstance(value, list) and all(isinstance(v, QWidget) for v in value):
            for index, copy in enumerate(value):
                widgets[f"{name}[{index}]"] = copy
                widgets.update(
                    {
                        f"{name}[{index}].{inner}": item
                        for inner, item in vars(copy).items()
                        if isinstance(item, QWidget)
                    }
                )

    return widgets


def _widget_state(widget: QWidget) -> tuple[object, ...]:
    """What a reader can see of one widget, its children apart."""

    state: list[object] = [
        type(widget).__name__,
        widget.isHidden(),
        widget.isEnabled(),
        widget.styleSheet(),
    ]

    if isinstance(widget, QLabel | QAbstractButton):
        state.append(widget.text())

    if isinstance(widget, QComboBox):
        state.extend((widget.currentIndex(), widget.currentText()))

    if isinstance(widget, QAbstractSlider):
        state.extend((widget.minimum(), widget.maximum(), widget.value()))

    return tuple(state)


def _stated(widget: QWidget, attributes: set[int]) -> tuple[tuple[object, ...], ...]:
    """One widget attribute as a reader sees it, with every widget under it no attribute names.

    A combo box's popup is left out: it is the toolkit's, and it shows
    what the combo's own entries say.
    """

    states = [_widget_state(widget)]

    if isinstance(widget, QComboBox):
        return tuple(states)

    for child in widget.children():
        if isinstance(child, QWidget) and id(child) not in attributes:
            states.extend(_stated(child, attributes))

    return tuple(states)


def test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt states the run on every widget a frame would, by default rather than by a list.

    The run is drawn, then changed in every way a run-state widget states,
    with every frame failing, so the halt is the only writer of what the
    screen says: a new agent, which is a new case with no control changes,
    its delivered dial renamed and the run failed by the frame. That screen
    is compared, widget attribute by widget attribute, with the same run once
    a frame draws it - one state, written once by `present_halt` and once by
    `refresh`. Before `_write_statement`, the halt wrote four widgets and a
    dial row, and the agent identity and the control-change panel went on
    stating the run the last frame drew (`PL-1YDD`, `PL-DTJQ`, `PL-X7D5`).

    Every widget attribute is compared unless `FRAME_WIDGETS` names it, so a
    widget added to `RunView` later is held here without being listed.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert run._off_scale_lines[0].isHidden() is False, "no trace is above the axis to go stale"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    attributes = _widget_attributes(run)
    named = {id(widget) for widget in attributes.values()}
    halted = {name: _stated(widget, named) for name, widget in attributes.items()}
    halted_banner = run._notice_text.notice()

    monkeypatch.undo()
    view.present(False)

    drawn = {name: _stated(widget, named) for name, widget in attributes.items()}
    differing = {name for name in attributes if halted[name] != drawn[name]}

    assert sorted(set(FRAME_WIDGETS) - set(attributes)) == [], (
        "FRAME_WIDGETS names a widget RunView no longer holds - remove the entry"
    )
    assert sorted(differing - set(FRAME_WIDGETS)) == [], (
        "these widgets read differently on a halted run and on the same run drawn: write "
        "them in RunView._write_statement, or name them in FRAME_WIDGETS with the reason "
        "only a frame can state them"
    )
    assert sorted(set(FRAME_WIDGETS) - differing) == [], (
        "these widgets read alike on a halted run and a drawn one now, so their exemption "
        "is stale - remove the entry"
    )
    assert halted_banner == halt_notice(controller.record())
    assert run._notice_text.notice() == notice(controller.snapshot(), None)


def test_a_confirmation_answered_after_the_snapshot_refuses_restates_the_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A confirmation answered once the snapshot refuses is answered by the halt, not a refusal.

    The question is asked from a snapshot read when the selector was used;
    by the time the reader answers, the run's snapshot may refuse.
    `set_agent` carries the settings over from the snapshot, so without the
    gate its raise reached `_apply_setting` as a refused setting, recorded in
    `_rejected_setting_notice` over a run halted for the same reason
    (`PL-V2HC`, found at review). `_start_new_case` now reads the snapshot
    through `_snapshot_for_a_control` first: the halt is stated, nothing is
    recorded as refused, the dialog is gone and the run keeps its agent.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    dialog.discard_button.click()

    assert "Traceback" not in capfd.readouterr().err
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert controller.agent_id == "sevoflurane"
    assert run._rejected_setting_notice is None
    assert run._new_case_dialog is None
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")


def test_a_reset_the_core_refuses_halts_the_run_visibly(application: QApplication) -> None:
    """A Reset the core refuses stops the run through the failed-step path, and clears nothing.

    `SimulationController.reset()` refuses a settings record that the run's
    definition cannot open on. Tissue flows that no longer sum to the cardiac
    output make such a record, and tissue fractions written past their guard
    leave them that way (`_with_stale_tissue_flows`). Before `PL-M4M0` the refusal escaped the
    Reset slot after `pause()` and the state had been cleared, so the run
    stood half reset - compartments and clock at zero, the old definition and
    timeline kept, no failure recorded, `case_restarted` never emitted - with
    the screen reading "Running" and Pause offered. The core now refuses
    before it clears anything, and the view halts the run on the refusal:
    recorded as the failure, said by the status word, the transport and the
    banner, whose way out says no setting can repair the refusal rather than
    naming the Reset just refused (`PL-01GY`). Nothing moved, so the frame
    that follows draws the run where it stood.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()
    segments = controller.run_segments
    presented = view.presented_frames
    _with_stale_tissue_flows(controller, 6.0)

    run._reset_button.click()

    reason = (
        "SimulationConfigurationError: the tissue groups are perfused at 6.0 L/min in total "
        "but cardiac output is 5.0 L/min; the venous balance returns what the tissues "
        "receive, so the two must agree"
    )
    status = controller.status()
    after = controller.snapshot()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert status.failure_reason == reason
    assert restarts == []
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert controller.run_segments == segments
    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is False
    assert view.presented_frames == presented + 1
    assert run._elapsed_time_text.text() != "0s"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice == (
        f"Simulation stopped — {reason}. The values shown are the last completed step. "
        f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}"
    )
    assert RESET_EXIT_TEXT not in notice


def test_a_second_refused_reset_states_the_refusal_once(application: QApplication) -> None:
    """Pressing the refused Reset again leaves the banner as it was: one reason, not two.

    The first press records the refusal as the failure, so on the second the
    run has a recorded reason - but it is this same refusal, and the exit
    that carries the refusal itself is for a run that failed for something
    else. Stated twice, the one refusal read as two faults (`PL-M4M0`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    run._reset_button.click()
    first = run._notice_text.notice()
    assert first is not None

    run._reset_button.click()

    notice = run._notice_text.notice()
    assert notice == first
    assert notice.count("perfused at") == 1
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")


def test_a_reset_refused_on_a_failed_run_keeps_the_failure_and_states_the_refusal(
    application: QApplication,
) -> None:
    """The first failure stays the banner's reason, so the exit carries the refusal itself.

    `SimulationController.fail` keeps the first reason it was given, which is
    right - the failure that stopped the run is what the values on screen are
    the last completed step of - so the refusal is stated where it can be:
    in the way out, which says Reset was refused and why (`PL-M4M0`).
    """

    controller = _StepFailingController(_real_step_failure())
    controller.set_cardiac_output(CardiacOutput(6.0))
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    failure = controller.status().failure_reason
    assert failure is not None and failure.startswith("SimulationNumericalError: ")
    _with_stale_tissue_flows(controller, 5.0)

    run._reset_button.click()

    assert controller.status().failure_reason == failure
    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {failure}.")
    assert notice.endswith(
        "Reset was refused — SimulationConfigurationError: the tissue groups are perfused at "
        "5.0 L/min in total but cardiac output is 6.0 L/min; the venous balance returns what "
        f"the tissues receive, so the two must agree. {REFUSED_RESET_WAY_OUT_TEXT}"
    )


def test_a_refused_reset_takes_once_the_cardiac_output_is_set_again(
    application: QApplication,
) -> None:
    """Once the record accepts a setting again, the exit is lifted and Reset clears the run.

    The accepted setting also takes the refused-Reset exit off the banner at
    once, so the reader is sent to a Reset that will take rather than to a
    setting already changed; a setting the stale record refuses leaves the
    exit standing (`PL-M4M0`). Until `PL-HQF5`, the cardiac output change
    itself repaired the stale flows. No setting repairs a fraction written
    past its guard, so the fractions are put back first.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    run._reset_button.click()
    assert controller.has_failed is True

    run._handle_fresh_gas_flow_change(3.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(REFUSED_RESET_WAY_OUT_TEXT)

    _with_the_tissue_fractions_put_back(controller)
    run._handle_cardiac_output_change(6.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith("Simulation stopped — SimulationConfigurationError: the tissue groups")
    assert notice.endswith(RESET_EXIT_TEXT)

    run._reset_button.click()

    assert restarts == [None]
    assert controller.has_failed is False
    assert controller.is_running is False
    assert controller.snapshot().elapsed_s == 0.0
    assert run._status_text.text() == "Paused"
    assert run._start_button.isEnabled() is True
    assert run._notice_text.isHidden() is True


def test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart(
    application: QApplication,
) -> None:
    """No dial repairs the record a Reset was refused on, so the banner names none.

    Every tissue flow is formed from the cardiac output (`PL-HQF5`), so a new
    output scales them all by one factor and the sum still disagrees with it.
    Until `PL-01GY` the banner said to change the setting the refusal names,
    which is the cardiac output. This test moves that dial on the refused run
    and shows the record still refused: the exit still stands, and the next
    Reset is refused again. The expected sentence is written here as a
    literal rather than read from the constant.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    way_out = (
        "Reset was refused for this reason. No setting can repair this, because only a "
        "fault in the simulator causes it. Close and reopen the application to start a "
        "new run."
    )

    run._reset_button.click()

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(way_out)
    assert "Change the setting" not in notice

    run._handle_cardiac_output_change(6.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(way_out)

    run._reset_button.click()

    assert restarts == []
    assert controller.has_failed is True
    assert controller.snapshot().elapsed_s > 0.0
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(way_out)


def test_a_run_halted_on_tissue_flows_set_past_its_patient_shows_the_output_its_last_step_ran_at(
    application: QApplication,
) -> None:
    """The cardiac output on screen is the one at which the values beside it were computed.

    Before `PL-KFNP`, a cardiac output could be assigned to the patient
    directly, bypassing `set_cardiac_output`. The run then halted at the next
    step, or at the Reset that `PL-M4M0` refuses. The readout and the dial
    showed the assigned output beside compartment values and a chart computed
    at the old flows (`PL-J39J`). The patient now refuses that assignment.
    Since `PL-HQF5` stale flows can be reached only by writing the tissue
    fractions past their guard (`_with_stale_tissue_flows`), and that changes
    no cardiac output.
    The patient keeps the output at which its last completed step ran. The
    settings record at the stale flows is refused before any step runs at
    them. So the readout, the dial, the values beside them and the run's
    definition, from which the chart is drawn, all show that output. The
    banner's sentence names the two figures that disagree.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()
    ran_under = controller._state.uptake_system.equation_settings()

    with pytest.raises(SimulationConfigurationError, match="set_cardiac_output"):
        controller._state.uptake_system.patient.cardiac_output_l_min = CardiacOutput(6.0)

    _with_stale_tissue_flows(controller, 6.0)

    _steps(run, 1)

    after = controller.snapshot()
    notice = run._notice_text.notice()

    assert controller.has_failed is True
    assert ran_under.cardiac_output_l_min == 5.0
    assert controller.run_segments[-1].settings == ran_under
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert after.alveolar_partial_pressure_fraction == before.alveolar_partial_pressure_fraction
    assert (
        after.mixed_venous_partial_pressure_fraction
        == before.mixed_venous_partial_pressure_fraction
    )
    assert run._setting_controls[0]._cardiac_output_slider.value_label.text() == "5.0 L/min"
    assert run._setting_controls[0]._cardiac_output_slider.value() == 5.0
    assert notice is not None
    assert "perfused at 6.0 L/min in total but cardiac output is 5.0 L/min" in notice
    assert "The values shown are the last completed step." in notice

    run._reset_button.click()

    assert controller.run_segments[-1].settings == ran_under
    assert run._setting_controls[0]._cardiac_output_slider.value_label.text() == "5.0 L/min"
    assert run._setting_controls[0]._cardiac_output_slider.value() == 5.0


def test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step(
    application: QApplication,
) -> None:
    """A setting the run never recorded halts the run before chart and readouts part (`PL-XRN8`).

    The readouts come from the steps and the chart from the run definition.
    A cardiac output written onto the core past `SimulationController` would
    step at 6.0 L/min while the chart was drawn at 5.0, so the run halts on
    the step before, and the banner says why.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()

    controller._state.uptake_system.set_cardiac_output(CardiacOutput(6.0))

    _steps(run, 1)

    after = controller.snapshot()
    notice = run._notice_text.notice()

    assert controller.has_failed is True
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert after.alveolar_partial_pressure_fraction == before.alveolar_partial_pressure_fraction
    assert controller.run_segments[-1].settings.cardiac_output_l_min == 5.0
    assert notice is not None
    assert "without SimulationController recording it" in notice


def test_a_refused_branch_reset_halts_the_branch_and_names_the_same_way_out(
    application: QApplication,
) -> None:
    """The same halt on a branch's own run, naming the same way out.

    `_open_at` records the settings in force at the fork, and `reset()` reads
    them before the branch is stood back there (`PL-M4M0`). The comparison
    stands, with the trunk untouched. The way out is the one every run has,
    closing and reopening the application, because a branch cannot start a
    case of its own (`PL-TFX5`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]
    branch._start_button.click()
    _steps(branch, 4)
    before = branch.snapshot()
    _with_stale_tissue_flows(branch.controller, 6.0)

    branch._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert branch.controller.has_failed is True
    assert branch.snapshot().elapsed_s == before.elapsed_s > 60.0
    assert branch._status_text.text() == "Stopped — simulation error"
    notice = branch._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")
    assert view.runs[TRUNK_RUN_INDEX].controller.has_failed is False


def test_a_refused_trunk_reset_while_comparing_names_the_one_door_open(
    application: QApplication,
) -> None:
    """Beside a branch the selector is locked, so the banner names a way out open on every run.

    A comparison replaces the trunk's agent selector with the
    `COMPARING_AGENT_LOCK_TEXT` chip, and the branch's Reset leaves the
    comparison standing, so a banner naming a new case named a control the
    screen had hidden, with the trunk's Reset - the one just refused - the
    only control left enabled (`PL-M4M0`). The exit names closing and
    reopening the application instead (`PL-01GY`). Once the record builds
    again, the trunk's Reset takes and ends the comparison as the fork panel
    says it does.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    trunk = view.runs[TRUNK_RUN_INDEX]
    _with_stale_tissue_flows(trunk.controller, 6.0)

    trunk._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert trunk.controller.has_failed is True
    assert trunk._agent_dropdown.isHidden() is True
    assert trunk._running_agent_lock_text.text() == COMPARING_AGENT_LOCK_TEXT
    notice = trunk._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")

    _with_the_tissue_fractions_put_back(trunk.controller)
    trunk._handle_cardiac_output_change(6.0)
    trunk._reset_button.click()
    _settle(application)

    assert trunk.controller.has_failed is False
    assert trunk.snapshot().elapsed_s == 0.0
    assert len(view.runs) == 1


def _refusing_a_drawn_column(
    controller: SimulationController, quantity: RecordedQuantity, value: float
) -> None:
    """Make the controller's next drawn window carry `value` in `quantity`'s last column.

    The one route to a drawn fraction outside 0 to 1, since no supported
    setting computes one (`core/concentration.py`): a drawn window is the
    closed form's evaluation, so the value is written into the window the
    controller answers with rather than into any compartment.
    """

    real_drawn_window = controller.drawn_window

    def drawn_window(start_s: float, stop_s: float, columns: int) -> DrawnWindow:
        window = real_drawn_window(start_s, stop_s, columns)
        states = list(window.states)
        values = list(states[-1].values)
        values[COMPARTMENT_STATE_INDEX[quantity]] = value
        states[-1] = replace(states[-1], values=tuple(values))

        return DrawnWindow(window.substance_id, window.times_s, tuple(states))

    controller.drawn_window = drawn_window  # type: ignore[method-assign]


def test_a_frame_that_refuses_a_drawn_value_moves_no_trace(application: QApplication) -> None:
    """Every drawn value is built before any is drawn, so a refusal leaves the chart as it was.

    With each value built as the toolkit converted it, trace by trace, a
    column refused in the muscle trace left the circuit, alveolar, mixed
    venous and vessel-rich traces redrawn from the failed frame and muscle
    and fat standing on the frame before it - six traces at two instants
    under a banner blaming a step that never failed (`PL-7DJK`). Now
    `assemble_chart_frame` refuses before a frame exists, the run halts,
    the halt names the compartment, and no trace moves. The value is the one
    that reproduced it.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)
    view.render_tick()
    chart = _concentration(view).chart
    before = {quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES}

    _refusing_a_drawn_column(controller, RecordedQuantity.MUSCLE, 1.0000000000001568)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)

    view.render_tick()

    status = controller.status()
    run = view.runs[0]

    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(
        "SimulationConfigurationError: muscle partial_pressure_fraction of 1.0000000000001568 "
        "is outside 0 to 1"
    )
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert "muscle partial_pressure_fraction of 1.0000000000001568" in notice
    assert "No frame of the stopped run could be drawn" in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False
    assert {
        quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES
    } == before


def test_two_runs_that_come_to_be_on_different_agents_halt_visibly(
    application: QApplication,
) -> None:
    """The same failure through a real refusal rather than a patched one.

    `assemble_chart_frame` refuses two runs on two agents on every attempt,
    so the halt it causes can never be drawn as a frame; each run still says
    it stopped, and why, from its own snapshot.
    """

    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    second.set_agent("desflurane")
    first.start()

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        reason = controller.snapshot().failure_reason
        assert reason is not None
        assert reason.startswith("ValueError")

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "ValueError" in notice


def test_a_resize_while_paused_redraws_the_frame_for_the_new_width(
    application: QApplication,
) -> None:
    """`PL-GS3R`: no chord wider than a pixel, at the width the plot has now.

    A frame is assembled for the width it is drawn on, so the one on screen
    is right for that width only. Paused, with nothing owed, nothing would
    redraw after a resize, and the columns drawn for the narrow plot would
    stand on the wide one at twice the chord.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller, width_px=800)
    presented = view.presented_frames

    view.resize(1600, _WINDOW_HEIGHT_PX)
    application.processEvents()

    assert _widest_chord_px(view) > 1, "the resize did not widen the plot under the old frame"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _widest_chord_px(view) <= 1

    view.render_tick()

    assert view.presented_frames == presented + 1, "the tick kept drawing with nothing owed"


# ---------------------------------------------------------- the playback


def test_the_default_playback_rate_is_real_time(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    assert run._playback_rate == DEFAULT_PLAYBACK_RATE
    assert run._playback_rate.multiplier == 1


def test_every_supported_playback_rate_is_offered_by_the_control(application: QApplication) -> None:
    combo = _shown_view(application, SimulationController()).runs[0]._playback_rate_dropdown

    assert [combo.itemData(index) for index in range(combo.count())] == [
        rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES
    ]


def test_the_control_and_the_clock_state_the_rate_identically(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]
    combo = run._playback_rate_dropdown
    offered = {combo.itemData(index): combo.itemText(index) for index in range(combo.count())}

    _select_playback_rate(run, 60)

    assert run._playback_rate_text.text() == offered[60]


def test_selecting_a_rate_changes_the_loop_and_the_readout_together(
    application: QApplication,
) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    _select_playback_rate(run, 60)

    assert run._playback_rate.multiplier == 60
    assert run._playback_rate_text.text() == format_playback_rate(60)

    _select_playback_rate(run, 1)

    assert run._playback_rate.multiplier == 1
    assert run._playback_rate_text.text() == format_playback_rate(1)


def test_the_mounted_interface_states_the_playback_rate(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    assert format_playback_rate(1) in _visible_strings(view)


def test_the_playback_control_is_never_disabled(application: QApplication) -> None:
    """A view control stays live while the run's own controls lock."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view.runs[0]._playback_rate_dropdown.isEnabled() is True


def test_reset_leaves_the_playback_rate_alone(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    _select_playback_rate(run, 20)
    run._reset_button.click()

    assert run._playback_rate == playback_rate_for(20)
    assert run._playback_rate_text.text() == format_playback_rate(20)


# ---------------------------------------------------- the agent selector


def test_agent_dropdown_options_pair_every_color_with_the_agent_name(
    application: QApplication,
) -> None:
    """Colour is a redundant cue: every option pairs the name with its ISO 5360 pair."""

    combo = _shown_view(application, SimulationController()).runs[0]._agent_dropdown
    keys = [combo.itemData(index) for index in range(combo.count())]

    assert keys == list(AGENT_DATA_FILENAMES)
    assert set(keys) == set(AGENT_COLOR_SCHEMES)

    for index, agent_id in enumerate(keys):
        scheme = AGENT_COLOR_SCHEMES[agent_id]

        assert combo.itemText(index) == load_agent_parameters(agent_id).display_name
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.BackgroundRole)) == (
            _colour_name(scheme.fill)
        )
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.ForegroundRole)) == (
            _colour_name(scheme.foreground)
        )


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown(
    application: QApplication,
) -> None:
    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert "Isoflurane" in run._subtitle_text.text()
    assert run._agent_dropdown.currentData() == "isoflurane"
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_refresh_view_applies_current_agent_color_to_control_and_header(
    application: QApplication, agent_id: str
) -> None:
    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert run._agent_dropdown.currentData() == agent_id
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert load_agent_parameters(agent_id).display_name in run._subtitle_text.text()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_agent_header_badge_is_bordered_against_the_panel(
    application: QApplication, agent_id: str
) -> None:
    """Sevoflurane's fill is 1.37:1 on the panel, so the badge carries a border."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert re.search(
        rf"border:\s*1px solid {re.escape(scheme.foreground)}", run._agent_header_badge.styleSheet()
    ), run._agent_header_badge.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_every_agent_has_render_objects_in_its_own_identification_color(
    application: QApplication, agent_id: str
) -> None:
    """The six identity controls carry the running agent's pair, and only its pair."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control

        for other_id, other in AGENT_COLOR_SCHEMES.items():
            if other_id != agent_id and other.fill != scheme.fill:
                assert other.fill not in control.styleSheet(), (control, other_id)


def test_switching_agent_repaints_the_header_badge_and_the_dropdown(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    scheme = AGENT_COLOR_SCHEMES["desflurane"]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control


def test_refresh_view_disables_agent_dropdown_while_running(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view.runs[0]._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_the_agent_name_stays_legible_while_the_run_disables_the_selector(
    application: QApplication, agent_id: str
) -> None:
    """`PL-61WW`: a disabled selector repaints the identity colour in a theme grey.

    So while the run locks the selector, the agent is named by a chip that
    is neither disabled nor greyed, in the agent's own pair, where the
    selector stood.
    """

    controller = SimulationController(agent_id=agent_id)
    view = _shown_view(application, controller)
    run = view.runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]
    controller.start()
    view.present(False)

    assert run._running_agent_display.isHidden() is False
    assert run._running_agent_display.isEnabled() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == load_agent_parameters(agent_id).display_name
    assert scheme.foreground in run._running_agent_text.styleSheet()
    assert scheme.foreground in run._running_agent_lock_text.styleSheet()
    assert run._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("running", [False, True])
def test_exactly_one_of_the_selector_and_the_running_agent_display_is_shown(
    application: QApplication, running: bool
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    if running:
        controller.start()
        view.present(False)

    assert run._agent_dropdown.isHidden() is not run._running_agent_display.isHidden()
    assert run._running_agent_display.isHidden() is not running


def test_the_running_agent_display_says_why_the_selector_is_gone(application: QApplication) -> None:
    controller = SimulationController(agent_id="desflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    view.present(False)

    assert run._running_agent_text.text() == "Desflurane"
    assert run._running_agent_lock_text.text() == RUNNING_AGENT_LOCK_TEXT
    assert run._running_agent_display.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._running_agent_display.maximumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.maximumWidth() == AGENT_SELECTOR_WIDTH


def test_the_running_agent_display_is_already_correct_before_it_is_shown(
    application: QApplication,
) -> None:
    """The chip is written every tick, so the frame that shows it has nothing to fix."""

    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert run._running_agent_display.isHidden() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == "Isoflurane"
    assert scheme.foreground in run._running_agent_text.styleSheet()


def test_building_a_run_view_opens_no_window_of_its_own(application: QApplication) -> None:
    """A widget shown before a layout adopts it is a top-level window.

    The selector and the chip have their visibility written as the view is
    built, before any layout places them, so each is built with the view as
    its parent; a parentless one shown there opened a window of its own
    beside the dashboard (`PL-25KS`).
    """

    host = QWidget()
    windows_before = len(application.topLevelWindows())

    run = RunView(SimulationController(), host, run_id=FIRST_RUN)
    application.processEvents()

    assert len(application.topLevelWindows()) == windows_before
    assert run.parent() is host

    host.deleteLater()
    _settle(application)


def test_the_delivered_label_on_screen_names_the_current_agent(application: QApplication) -> None:
    """Regression for a label hardcoded to "Delivered sevoflurane"."""

    run = _shown_view(application, SimulationController(agent_id="desflurane")).runs[0]

    assert (
        run._setting_controls[0]._delivered_concentration_slider.name_label.text()
        == "Delivered desflurane"
    )


def test_a_built_in_agent_without_an_identification_colour_fails_at_import() -> None:
    """Adding an agent without its ISO 5360 colour must stop the app starting.

    The guard runs at module scope, so covering it means re-executing the
    module body with the colour table short one entry, and reloading again
    afterwards so the genuine table is what every later test sees.
    """

    original = dict(theme.AGENT_COLOR_SCHEMES)
    theme.AGENT_COLOR_SCHEMES.pop(next(iter(original)))
    try:
        with pytest.raises(
            RuntimeError,
            match="^AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents$",
        ):
            importlib.reload(run_view_module)
    finally:
        theme.AGENT_COLOR_SCHEMES.clear()
        theme.AGENT_COLOR_SCHEMES.update(original)
        importlib.reload(run_view_module)


# ---------------------------------------------------- the new-case flow


def test_agent_dropdown_handler_switches_the_real_controller(application: QApplication) -> None:
    """A never-started run has nothing to lose, so the switch is immediate."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()
    assert run._new_case_dialog is None


def test_a_recorded_run_is_not_discarded_before_the_reader_has_answered(
    application: QApplication,
) -> None:
    """`PL-R3KB`: selecting an agent rebuilds nothing until it is confirmed."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._new_case_dialog is not None
    assert run._new_case_dialog.isVisible() is True
    # The selector reads the agent that is actually running, not the one
    # being offered, for as long as the question is open.
    assert run._agent_dropdown.currentData() == before.agent_id


def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched(
    application: QApplication,
) -> None:
    """Declining costs nothing: the run, its history and the selector stand."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.keep_button.text() == KEEP_CURRENT_CASE_TEMPLATE.format(agent="sevoflurane")
    dialog.keep_button.click()

    after = controller.snapshot()
    assert after.agent_id == "sevoflurane"
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert "Sevoflurane" in run._subtitle_text.text()
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_a_confirmed_agent_change_starts_the_new_case(application: QApplication) -> None:
    """Confirming does what the selector used to do on its own."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.discard_button.text() == START_NEW_CASE_TEMPLATE.format(agent="desflurane")
    dialog.discard_button.click()

    after = controller.snapshot()
    assert after.agent_id == "desflurane"
    assert after.elapsed_s == 0.0
    assert after.control_timeline == ()
    assert run._agent_dropdown.currentData() == "desflurane"
    assert (
        run._setting_controls[0]._delivered_concentration_slider.name_label.text()
        == "Delivered desflurane"
    )
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_an_agent_chosen_in_the_selector_runs_as_a_fresh_run_of_that_agent(
    application: QApplication,
) -> None:
    """A switch made through the selector computes with the new agent alone (`PL-QJXS`).

    `tests/integration/test_controller.py` compares `set_agent` with a fresh
    run of the new agent for every pair of agents. This test takes the path a
    reader takes: the selector, the new-case dialog and a presented frame. So
    a view that changed agent by some route other than `set_agent`, or wrote
    a control's old value into the new run, fails here.

    The expected run is built directly with desflurane and the same four
    settings, each different from its default. The comparison is exact,
    because both runs take the same steps from the same state.
    """

    settings = {
        "circuit_volume_l": 4.5,
        "fresh_gas_flow_l_min": FreshGasFlow(2.5),
        "alveolar_ventilation_l_min": AlveolarVentilation(5.5),
        "cardiac_output_l_min": CardiacOutput(6.5),
    }
    controller = SimulationController(agent_id="sevoflurane", **settings)
    controller.start()
    _advance_to(controller, 90.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()
    view.present(False)

    fresh = SimulationController(agent_id="desflurane", **settings)

    for each in (controller, fresh):
        each.start()
        _advance_to(each, 300.0)

    assert fresh.snapshot().alveolar_partial_pressure_fraction > 0.0
    assert controller.snapshot() == fresh.snapshot()


def test_the_dismissal_that_follows_a_confirmed_switch_does_not_undo_it(
    application: QApplication,
) -> None:
    """A dialog reports its close after the button that closed it.

    That report reaches the declining branch, so without the guard in
    `_resolve_new_case` it would run over the case that had just started.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.accept()

    run._resolve_new_case(False)

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"


def test_dismissing_the_confirmation_keeps_the_current_case(application: QApplication) -> None:
    """A dialog closed by anything but its buttons has chosen nothing."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.reject()

    assert controller.snapshot().agent_id == before.agent_id
    assert controller.snapshot().elapsed_s == before.elapsed_s
    assert run._agent_dropdown.currentData() == before.agent_id
    assert run._new_case_dialog is None


@pytest.mark.parametrize("answer", ["keep", "discard"])
def test_an_answered_confirmation_is_gone_from_the_view_and_its_strings(
    application: QApplication, answer: str
) -> None:
    """A question that has been answered is not part of the interface.

    Deleted once its `finished` has been read, or every confirmation ever
    asked stays a child of the run: its title on `interface_strings` and its
    widgets in every walk of the tree (`PL-25KS`).
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    title = dialog.windowTitle()
    assert title in view.interface_strings()

    (dialog.keep_button if answer == "keep" else dialog.discard_button).click()
    _settle(application)

    assert run.findChildren(QDialog) == []
    assert title not in view.interface_strings()
    assert controller.snapshot().agent_id == ("sevoflurane" if answer == "keep" else "desflurane")


def test_a_selection_while_a_confirmation_is_open_does_not_retarget_its_answer(
    application: QApplication,
) -> None:
    """The open dialog names one agent, and its answer starts that agent and no other.

    A second selection while the question stands is reverted and not
    answered; before the guard it opened a second dialog and moved the
    pending agent, so the first dialog's discard started the second agent.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    first = run._new_case_dialog
    assert first is not None

    _select_agent(run, "isoflurane")

    assert run._new_case_dialog is first
    assert run.findChildren(QDialog) == [first]
    assert run._agent_dropdown.currentData() == "sevoflurane"

    first.discard_button.click()

    assert controller.snapshot().agent_id == "desflurane"


def test_reselecting_the_running_agent_discards_nothing_and_asks_nothing(
    application: QApplication,
) -> None:
    """A selector opened and closed on the same option reports a selection."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "sevoflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert run._new_case_dialog is None


def test_the_dialog_quotes_the_time_and_the_changes_the_panel_shows(
    application: QApplication,
) -> None:
    """What is about to be lost is stated in the run's own displayed terms."""

    controller = _paused_run_with_history(elapsed_s=125.0)
    snapshot = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    warning = dialog.body_labels[1].text()

    assert warning == format_case_discard_warning(
        "Sevoflurane", snapshot.elapsed_s, len(group_adjustments(snapshot.control_timeline))
    )
    assert format_elapsed(snapshot.elapsed_s) in warning


def test_the_dialog_names_both_agents_and_what_survives_the_switch(
    application: QApplication,
) -> None:
    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    body = [label.text() for label in dialog.body_labels]

    assert dialog.title_label.text() == "Start a new desflurane case?"
    assert body[0] == NEW_CASE_IS_NOT_A_VIEW_TEXT
    assert "sevoflurane" in body[1]
    assert body[2] == NEW_CASE_CARRYOVER_TEMPLATE.format(agent="desflurane")
    assert dialog.isModal() is True


def test_the_open_confirmations_buttons_carry_both_outcomes_and_default_to_keeping(
    application: QApplication,
) -> None:
    """The press a reader makes without reading keeps their case."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None

    assert dialog.discard_button.text() == "Discard and start desflurane"
    assert dialog.keep_button.text() == "Keep the sevoflurane case"
    assert dialog.keep_button.isDefault() is True
    assert dialog.discard_button.isDefault() is False


# ------------------------------------------------------- the readouts


def test_the_readouts_say_they_are_model_outputs_beside_the_values(
    application: QApplication,
) -> None:
    """`PL-2K1R`: the interpretation line sits on the readout section's heading row.

    Once, beside the values it qualifies, rather than at the foot of the
    page where a repeated disclaimer stops being read.
    """

    run = _shown_view(application, SimulationController()).runs[0]

    assert run._interpretation_text.text() == INTERPRETATION_DISCLAIMER_TEXT
    heading_row = run._interpretation_text.parentWidget()
    assert heading_row is not None
    assert run._compartment_substance_text.parentWidget() is heading_row
    assert run._readout_row.parentWidget() in (heading_row, heading_row.parentWidget()), (
        "the interpretation line is not in the section that holds the readout row"
    )


def test_the_hover_readout_states_the_agent_compartment_and_both_units(
    application: QApplication,
) -> None:
    """`PL-YVHK`: a hover over a drawn point names what it is, in both units.

    Through the dashboard rather than the bare chart, so the shipped
    composition is what answers, and against the frame it drew, so the
    readout is the state the run was evaluated at rather than a position
    between two. A drawn instant is a grid column's rather than a step's,
    so the time the readout states is the instant at the hover's own
    resolution, not the column's raw time.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    chart = _concentration(view).chart
    frame = chart.frame
    assert frame is not None
    run = frame.runs[0]
    index = len(run.times_s) // 2
    time_s = run.times_s[index]
    fraction = run.fractions[RecordedQuantity.ALVEOLAR][index]

    readout = chart.readout_at(time_s, run.percents(RecordedQuantity.ALVEOLAR)[index])

    assert readout is not None
    assert readout == format_trace_hover(run, RecordedQuantity.ALVEOLAR, index, len(frame.runs))
    context, what, value = readout.splitlines()
    instant_s = round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S
    assert "sevoflurane" in context
    assert format_elapsed(instant_s) in context
    assert "Alveolar" in what
    assert _ALVEOLAR_METRIC_QUALIFIER in what
    assert format_percent(fraction) in value
    assert format_mac_multiple(fraction, controller.snapshot().agent_mac_percent) in value


def test_hiding_a_trace_changes_only_what_is_drawn(application: QApplication) -> None:
    """Unchecking a compartment takes its curve off and touches nothing else."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 120.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    chart = _concentration(view).chart
    snapshot = controller.snapshot()
    before = {
        quantity: chart.drawn_points(0, quantity)
        for quantity in COMPARTMENT_QUANTITIES
        if quantity is not RecordedQuantity.FAT
    }

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())

    for quantity, (times, percents) in before.items():
        redrawn_times, redrawn_percents = chart.drawn_points(0, quantity)

        assert redrawn_times == pytest.approx(times)
        assert redrawn_percents == pytest.approx(percents)

    assert _readout_value(run, RecordedQuantity.CIRCUIT) == format_percent(
        snapshot.inspired_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.MUSCLE) == format_percent(
        snapshot.muscle_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.FAT) == format_percent(
        snapshot.fat_partial_pressure_fraction
    )


def test_the_hidden_traces_advisory_is_present_always_and_shown_only_when_nothing_is_drawn(
    application: QApplication,
) -> None:
    """A plot missing all six is a blank panel, and a blank panel reads as a failure."""

    view = _shown_view(application, SimulationController())

    assert _concentration(view).hidden_traces_text.isHidden() is True
    assert NO_TRACES_SHOWN_TEXT in _interface_strings(view)

    for quantity in COMPARTMENT_QUANTITIES:
        _set_trace_shown(application, view, quantity, False)

    assert _concentration(view).hidden_traces_text.isHidden() is False
    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.visible == ()

    _set_trace_shown(application, view, RecordedQuantity.ALVEOLAR, True)

    assert _concentration(view).hidden_traces_text.isHidden() is True


def test_the_compartment_selection_outlives_the_legend_that_renders_it(
    application: QApplication,
) -> None:
    """The dashboard owns the selection, so the legend can go without taking it (`PL-VN6M`).

    The legend sits in the concentration chart's View. A reader closes the
    legend by choosing another View for its Area (`.claude/rules/ui-areas.md`,
    test 2). When the legend's boxes held the selection, the dashboard read
    the selection back from them. So a deleted legend left no selection from
    which to assemble the next frame. Here the chart's View is replaced, which
    deletes the legend. The dashboard still draws the reader's choice on the
    F_A/F_I plot's frame. It also still takes a branch and a Reset. Each of
    those fits the selection to the new run count, with no legend left to
    show the selection to. A chart View brought back, and a legend connected
    afterwards, follow the selection as the first ones did.
    """

    view = _case_view(application, _branched_case())
    legend = _concentration(view).legend

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)
    _set_trace_shown(application, view, RecordedQuantity.MUSCLE, False)

    chosen = view.compartment_selection

    assert chosen.shown == legend.shown
    assert RecordedQuantity.FAT not in chosen.shown

    deleted: list[bool] = []
    legend.destroyed.connect(lambda: deleted.append(True))
    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)

    assert deleted, "the legend was not deleted, so nothing here outlived it"

    presented = view.presented_frames
    view.present(False)

    # `present` turns a raise into a halt rather than letting it out, so the
    # count is what tells a frame drawn from one refused.
    assert view.presented_frames == presented + 1, "no frame could be drawn without the legend"
    assert view.compartment_selection == chosen

    frame = _wash_in(view).chart.frame

    assert frame is not None
    assert frame.visible == chosen.shown

    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert view.runs[1]._run_name_text.isHidden() is False, "the fork stopped part way"
    assert view.compartment_selection == chosen.with_run_count(2)

    compared = _wash_in(view).chart.frame

    assert compared is not None
    assert compared.visible == view.compartment_selection.shown

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.compartment_selection == chosen.with_run_count(2).with_run_count(1)

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _concentration(view).legend.shown == view.compartment_selection.shown
    assert _concentration(view).chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())

    renderer = TraceLegend()
    renderer.show_selection(view.compartment_selection)
    view.compartment_selection_changed.connect(renderer.show_selection)
    renderer.compartment_requested.connect(view._handle_compartment_request)

    assert renderer.shown == view.compartment_selection.shown

    renderer.set_compartment_shown(RecordedQuantity.FAT, True)
    application.processEvents()

    assert RecordedQuantity.FAT in view.compartment_selection.shown
    assert renderer.shown == view.compartment_selection.shown

    drawn = _concentration(view).chart.frame

    assert drawn is not None
    assert drawn.visible == renderer.shown


def test_a_legend_click_draws_one_frame_over_the_cap_too(application: QApplication) -> None:
    """A click is a discrete action, so it draws once and at once (`PL-R2YM`).

    Held on one run, and on two, where the click is over the cap and the
    selection rather than the legend decides which compartment makes room.
    """

    view = _case_view(application, _branched_case())
    presented = view.presented_frames

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert view.presented_frames == presented + 1

    _take_fork(view, 60.0)
    before = view.compartment_selection
    presented = view.presented_frames

    assert len(before.shown) == COMPARED_COMPARTMENT_CAP

    _set_trace_shown(application, view, RecordedQuantity.FAT, True)

    assert view.presented_frames == presented + 1
    assert view.compartment_selection == before.with_compartment(RecordedQuantity.FAT, True)

    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.visible == view.compartment_selection.shown
    assert RecordedQuantity.FAT in frame.visible


def test_a_legend_click_whose_frame_fails_keeps_the_legend_on_the_frame_drawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The legend names the curves on the plot even when the frame a click asked for fails.

    A click set the selection, handed it to the legend and then asked for a
    frame, so where that frame failed to assemble the boxes showed the new
    selection over a plot still drawing the old one: fat unchecked beside a
    fat trace (`PL-G3K7`). The legend is now handed the selection a frame was
    assembled from once both plots have drawn it, and a box nobody answers
    goes back to the selection the legend last showed.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    drawn = _concentration(view).chart.frame
    assert drawn is not None
    assert RecordedQuantity.FAT in drawn.visible
    presented = view.presented_frames
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert controller.has_failed is True
    assert view.presented_frames == presented
    assert _concentration(view).chart.frame is drawn
    assert _concentration(view).legend.shown == drawn.visible


def test_a_trace_above_the_axis_is_reported_on_the_run_that_drew_it(
    application: QApplication,
) -> None:
    """The off-scale notice is a per-run advisory, written from the drawn frame.

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling: after ten
    minutes the circuit is above the axis and the alveolar trace is inside
    it, so the notice names one and not the other.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._off_scale_lines[0].isHidden() is False
    assert "Circuit" in run._off_scale_lines[0].text()
    assert "Alveolar" not in run._off_scale_lines[0].text()
    assert "readouts above" in run._off_scale_lines[0].text()

    _set_trace_shown(application, view, RecordedQuantity.CIRCUIT, False)

    assert run._off_scale_lines[0].isHidden() is True


def test_the_control_timeline_is_not_regrouped_when_it_has_not_grown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-1PSX`: a frame in which nobody touched a control pays nothing for the record."""

    controller = SimulationController()
    controller.start()

    for index in range(4):
        controller.begin_control_adjustment()
        controller.set_fresh_gas_flow(FreshGasFlow(4.0 - (index + 1) * 0.1))
        _advance(controller, 1.0)

    view = _shown_view(application, controller)

    regroups = 0
    real = control_timeline_module.group_adjustments

    def counted(recorded: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
        nonlocal regroups
        regroups += 1
        return real(recorded)

    monkeypatch.setattr(control_timeline_module, "group_adjustments", counted)

    view.present(False)
    view.present(False)
    view.present(False)

    assert regroups == 0
    # The panel is still written from the grouping, so this is a cache
    # serving the right answer rather than a frame that stopped drawing.
    assert view.runs[0]._control_timeline_text.text().splitlines()[0].startswith("3s")


# ------------------------------------------------ the charts, integrated


def test_the_chart_defaults_to_fitting_the_whole_run(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 1200.0)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame

    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY
    assert view._time_base is None
    assert frame is not None
    assert frame.fitted is True
    assert frame.start_s == 0.0
    assert frame.stop_s >= 1200.0


def test_the_time_base_selector_offers_fit_run_and_the_settled_widths(
    application: QApplication,
) -> None:
    combo = _concentration(_shown_view(application, SimulationController())).time_base_selector

    assert [combo.itemData(index) for index in range(combo.count())] == [
        FIT_RUN_KEY,
        *(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        "Fit run",
        *(format_time_base(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]


def test_selecting_a_time_base_makes_the_window_exactly_that_wide(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, str(time_base.span_s))
        frame = _concentration(view).chart.frame

        assert frame is not None
        assert frame.fitted is False
        assert frame.stop_s - frame.start_s == pytest.approx(time_base.span_s)
        assert view._time_base == time_base_for_span(time_base.span_s)


def test_a_run_shorter_than_the_selected_time_base_shows_whole(application: QApplication) -> None:
    """`PL-SSBP`: a chosen width wider than the run draws the run from zero."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    _select_time_base(view, "900.0")
    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.start_s == 0.0
    assert frame.stop_s == 900.0
    assert _concentration(view).chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][0] == (
        pytest.approx(0.0)
    )


def test_both_plots_are_labelled_from_the_same_ticks(application: QApplication) -> None:
    """One frame, both charts: the ticks cannot disagree because there is one list."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 1800.0)
    view = _shown_view(application, controller)

    assert _wash_in(view).chart.frame is _concentration(view).chart.frame
    assert _wash_in(view).chart.axis_ticks("bottom") == _concentration(view).chart.axis_ticks(
        "bottom"
    )


def test_the_wash_in_plot_spans_the_same_window_as_the_chart_above_it(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    for key in (FIT_RUN_KEY, "900.0", "43200.0"):
        _select_time_base(view, key)

        assert _wash_in(view).chart.frame is _concentration(view).chart.frame


def test_the_time_axis_caption_on_screen_states_the_span_and_the_mode(
    application: QApplication,
) -> None:
    """The width is a mode (`PL-012`), so the caption says which and how wide."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 7200.0)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame
    assert frame is not None

    assert "whole run so far" in _concentration(view).time_axis_caption.text()
    assert (
        f"{format_time_base(frame.time_base.span_s)} shown"
        in _concentration(view).time_axis_caption.text()
    )
    assert "simulated seconds" not in _concentration(view).time_axis_caption.text()

    _select_time_base(view, "7200.0")

    assert _concentration(view).time_axis_caption.text() == "2 hours shown"


def test_choosing_a_time_base_changes_nothing_the_run_recorded(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 20.0)
    view = _shown_view(application, controller)
    recorded = (controller.snapshot().elapsed_s, controller.run_segments)

    for key in (*(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES), FIT_RUN_KEY):
        _select_time_base(view, key)

        assert (controller.snapshot().elapsed_s, controller.run_segments) == recorded


def test_the_time_base_is_never_disabled(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert _concentration(view).time_base_selector.isEnabled() is True


def test_the_chosen_time_base_survives_its_selector_being_closed(application: QApplication) -> None:
    """The dashboard, not the control, owns the width that both plots are drawn at (`PL-9LNF`).

    Before this change, the dropdown held the state, and the handler read the
    width back out of it. The control sits in the concentration chart's View,
    so a reader closes it by choosing another View for its Area. The next
    frame must stay at the width the reader chose, and a chart View brought
    back must show that width.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    _select_time_base(view, "1800.0")

    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)
    view.present(False)

    frame = _wash_in(view).chart.frame
    assert frame is not None
    assert frame.fitted is False
    assert frame.time_base == time_base_for_span(1800.0)

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _concentration(view).chart.frame is _wash_in(view).chart.frame
    assert format_time_base(1800.0) in _concentration(view).time_axis_caption.text()


def test_a_second_time_base_selector_shows_the_width_a_first_one_chose(
    application: QApplication,
) -> None:
    """Two controls on one dashboard show one width, because each shows what it is handed.

    The second selector stands for a second chart View in another Area. It
    is told the dashboard's width once a frame has drawn it, and a pick on
    either is a request the dashboard answers for both.
    """

    view = _shown_view(application, SimulationController())
    second = TimeBaseSelector()
    view.time_base_changed.connect(second.show_time_base)
    second.time_base_requested.connect(view._handle_time_base_request)

    _select_time_base(view, "1800.0")

    assert second.currentData() == "1800.0"

    second.setCurrentIndex(second.findData(FIT_RUN_KEY))

    assert view._time_base is None
    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY
    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.fitted is True


def test_reset_leaves_the_selected_time_base_alone(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    _select_time_base(view, "1800.0")
    view.runs[0]._reset_button.click()

    assert view._time_base == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"


def test_the_mac_axis_and_references_follow_the_agent(application: QApplication) -> None:
    """The divisor line, the 1 MAC line and the right axis are the running agent's."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart = _concentration(view).chart

    assert _concentration(view).mac_reference_text.text() == format_mac_reference(
        "Sevoflurane", 2.0
    )
    assert chart.one_mac_line() == 2.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(6.0)

    _select_agent(view.runs[0], "desflurane")
    # Read from desflurane's own file, not from the switched run's snapshot,
    # which would agree with a band the switch failed to rebuild (`PL-JPS2`).
    mac_awake = load_agent_parameters("desflurane").mac_awake

    assert _concentration(view).mac_reference_text.text() == format_mac_reference("Desflurane", 6.0)
    assert _concentration(view).mac_awake_reference_text.text() == format_mac_awake_reference(
        "Desflurane",
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=6.0,
    )
    assert chart.one_mac_line() == 6.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(18.0)


@pytest.mark.parametrize(
    ("previous_agent_id", "agent_id"),
    [
        (previous, chosen)
        for previous in AGENT_DATA_FILENAMES
        for chosen in AGENT_DATA_FILENAMES
        if previous != chosen
    ],
)
def test_the_mac_awake_band_after_a_switch_is_the_new_agents_own(
    application: QApplication, previous_agent_id: str, agent_id: str
) -> None:
    """After a switch, the band and its line of text use the chosen agent's own values.

    A switch keeps the controller. So a band the switch failed to rebuild
    would still hold the previous agent's fraction and spread, and the
    snapshot would agree with the chart. The expected values therefore come
    from the chosen agent's data file, and the test works out the band's
    edges itself (`PL-JPS2`). After a switch from sevoflurane, such a fault
    would draw desflurane's band at 1.74-2.34% instead of 1.78-2.54%.
    """

    view = _shown_view(application, SimulationController(agent_id=previous_agent_id))
    _select_agent(view.runs[0], agent_id)
    own = load_agent_parameters(agent_id)
    fraction = own.mac_awake.fraction_of_mac
    spread = own.mac_awake.standard_deviation_fraction_of_mac

    assert view.runs[0].controller.agent_id == agent_id
    assert _concentration(view).chart.mac_awake_band() == pytest.approx(
        ((fraction - spread) * own.mac_percent, (fraction + spread) * own.mac_percent)
    )
    assert _concentration(view).mac_awake_reference_text.text() == format_mac_awake_reference(
        own.display_name,
        fraction_of_mac=fraction,
        standard_deviation_fraction_of_mac=spread,
        mac_percent=own.mac_percent,
    )


def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time(
    application: QApplication,
) -> None:
    """`PL-DR1Z`: the mark stands at the change's instant on both plots."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)

    assert _concentration(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert _wash_in(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert view.runs[0]._control_timeline_text.text().startswith(format_elapsed(600.0))


def test_a_real_run_draws_the_ratio_of_its_own_recorded_compartments(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 60.0)
    view = _shown_view(application, controller)
    snapshot = controller.snapshot()
    reading = read_wash_in(
        snapshot.alveolar_partial_pressure_fraction, snapshot.inspired_partial_pressure_fraction
    )
    assert reading.plotted_ratio is not None

    stretches = _wash_in(view).chart.drawn_stretches(0)
    assert stretches
    last_time, last_ratio = stretches[-1][-1]

    assert last_time == pytest.approx(snapshot.elapsed_s)
    assert last_ratio == pytest.approx(reading.plotted_ratio)
    assert format_wash_in_ratio(last_ratio) in view.runs[0]._wash_in_state_lines[0].text()


# ------------------------------------------- the whole interface, walked


def test_the_page_leaves_the_application_name_to_the_window_title(
    application: QApplication,
) -> None:
    """The page no longer restates the name the window's title bar carries (`PL-J8K2` Q2).

    `PL-HK75` put the name on screen from `app_metadata`; the title bar is
    where it now is, and `test_bootstrap` holds the window title to it. The
    in-page title row cost 44 px the chart cannot spare on a laptop
    (`PL-84QX`).
    """

    view = _shown_view(application, SimulationController())

    assert APP_DISPLAY_NAME not in _interface_strings(view)


def test_no_interface_string_drops_the_end_tidal_equivalent_hedge(
    application: QApplication,
) -> None:
    """`PL-NV9W`: nothing on screen says "end-tidal" without "-equivalent"."""

    strings = _interface_strings(_shown_view(application, SimulationController()))

    for value in strings:
        assert _UNHEDGED_END_TIDAL.search(value) is None, value

    assert _ALVEOLAR_METRIC_QUALIFIER in strings, (
        "the interface walk did not reach the concentration readouts, so the assertion "
        "above proved nothing"
    )


def test_the_interface_states_the_mac_divisor_and_writes_the_unit_as_a_ratio(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    strings = _visible_strings(view)

    assert "1 MAC sevoflurane = 2.0%" in " ".join(sorted(strings))
    # The readouts write the unit as a ratio, never as a bare "MAC".
    assert any(value.endswith(" ×MAC") for value in strings)


def test_the_screen_states_the_band_fraction_and_the_divisor_for_every_agent(
    application: QApplication,
) -> None:
    """`PL-F52R`: both free parameters are named on screen, for every agent."""

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view = _shown_view(application, SimulationController(agent_id=agent_id))
        strings = _visible_strings(view)

        assert (
            format_mac_awake_reference(
                agent.display_name,
                fraction_of_mac=agent.mac_awake.fraction_of_mac,
                standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
                mac_percent=agent.mac_percent,
            )
            in strings
        )
        assert format_mac_reference(agent.display_name, agent.mac_percent) in strings


def test_the_interface_says_which_trace_the_band_is_read_against(application: QApplication) -> None:
    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "vessel-rich trace" in prose
    assert "±1 SD" in prose
    assert "population" in prose


def test_nothing_between_the_chart_heading_and_the_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-6580`: the panel above the compartment plot is legend and labels, not prose.

    The two state advisories are exempt and skipped by identity: they are
    empty here and speak only when they apply, which is the distinction
    being drawn - a message at the moment of need is not a standing
    paragraph.
    """

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None,
        _concentration(view).chart,
        skip=(_concentration(view).hidden_traces_text, view.runs[0]._off_scale_lines[0]),
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "1 MAC sevoflurane = 2.0%" in joined
    assert "read against vessel-rich trace" in joined
    assert "1 MAC, reference adult (alveolar)" in joined
    assert "Compartments:" in joined
    assert "Clinical references:" in joined
    assert "Run record:" in joined
    assert "Time base" in joined


def test_nothing_between_the_wash_in_heading_and_its_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-F9TQ`: the same rule as the panel above, applied to the panel below."""

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None, _wash_in(view).chart, skip=(view.runs[0]._wash_in_state_lines[0],)
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "not the vaporizer dial" in joined
    assert "Modelled, not measured" in joined
    assert "dimensionless ratio" not in joined


def test_the_wash_in_plot_says_what_its_denominator_is(application: QApplication) -> None:
    """`PL-F9TQ`: F_I is the modelled circuit, and the plot says so where it is read."""

    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "not the vaporizer dial" in prose
    assert "denominator moving" in prose
    assert "Equilibrium, F_A = F_I" in prose


def test_the_screen_says_a_control_mark_is_an_input_not_a_measurement(
    application: QApplication,
) -> None:
    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "Settings only — not a measurement." in prose
    assert "Control change" in prose
    assert "Run record:" in prose


def test_the_interface_never_predicts_a_time_to_wake_up(application: QApplication) -> None:
    """`PL-F52R`: the claim the band exists *instead of*, checked against the whole tree.

    A readout of the form "time to wake-up: 14 min" reads as a per-patient
    prediction this model does not support, and no surrounding disclaimer
    undoes that.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    strings = _interface_strings(_shown_view(application, controller))
    prose = " ".join(strings).lower()

    duration = re.compile(
        r"\d+(?:\.\d+)?\s*(?:s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hour|hours)\b"
    )

    for value in strings:
        lowered = value.lower()
        if any(word in lowered for word in ("wake", "awaken", "arousal", "emergence")):
            assert duration.search(lowered) is None, value

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

    assert "population" in prose
    assert "±1 sd" in prose


# ------------------------------------------- what declares its own foreground


#: Every control kind on the built dashboard that paints its own content and
#: declares no foreground, against the reason it is allowed not to. Read by
#: `tools/contrast_check.py`, which counts the entries into its report line:
#: that tool measures declared pairs, so a control declaring nothing is absent
#: from its numerator *and* its denominator and reads there as covered. What
#: nothing measures has to be stated somewhere, and this is where.
#:
#: A name here is a claim about a kind, not an excuse for one: the test below
#: fails on an entry naming a kind the dashboard no longer builds, and on one
#: that has since been given a foreground, so an entry cannot outlive the
#: reason beside it.
FOREGROUND_NOT_DECLARED: dict[str, str] = {
    "PlotWidget": (
        "the concentration chart and the wash-in plot. Their axis ticks and "
        "labels are text, and pyqtgraph draws them from a pen rather than from "
        "the palette: `qt_chart._plot` sets setTextPen(mkPen(MUTED)) on every "
        "axis and passes color=MUTED to each setLabel. So the colour is "
        "declared and contrast_check measures it as MUTED on PANEL; it is "
        "only unreachable through the palette this test reads."
    ),
    "QScrollArea": (
        "the page's scroll area. It paints the viewport surface, which "
        "`SimulationView` declares as BACKGROUND in a stylesheet, and no text: "
        "every string inside it belongs to a widget of its own."
    ),
    "QScrollBar": (
        "Qt's own chrome, on the page and inside each selector's popup. It "
        "draws no text, and its groove and handle come from the platform "
        "style rather than from the foreground role. Whether this interface "
        "should declare a colour scheme so the chrome follows it is PL-KRZW, "
        "which is the project owner's decision and open."
    ),
    "QSlider": (
        "the four setting sliders. Each draws no text - the value beside it is "
        "a label of its own - and `slider_stylesheet` declares the groove, "
        "the filled track and the handle, none of which is painted from the "
        "foreground role."
    ),
    "_AreaHandle": (
        "the border between two Areas, the chart column and the sidebar. It draws "
        "no text: nothing at rest, and under the pointer a PRIMARY line that "
        "`tools/contrast_check.py` measures against BACKGROUND (PL-RQT1)."
    ),
    "_LineSwatch": (
        "the legend's line samples. Each paints with the pen of the trace it "
        "stands for and never reads its foreground role; contrast_check holds "
        "every trace colour to TRACE_FLOOR against PANEL, in all four vision "
        "models."
    ),
    "_BandSwatch": (
        "the MAC-awake band's legend mark, painted with the band's own edge "
        "pen and fill for the reason the line swatches are."
    ),
}

#: A six-digit sRGB hex literal, the form every colour in `app/theme.py`
#: takes and the form `QColor.name` returns.
_HEX_COLOUR = re.compile(r"#[0-9A-Fa-f]{6}")

#: A foreground colour nothing in this interface declares, installed on the
#: application palette before the dashboard is built. A control that declares
#: none of its own resolves to it, which makes "undeclared" a value to read
#: rather than an absence to infer - and stops a host whose own default
#: happened to match a theme colour from making the walk vacuous.
_ALIEN_FOREGROUND = "#FF00FF"

#: The palette roles a control on this dashboard draws its content in. All of
#: them move together, because `QWidget.foregroundRole` differs by control -
#: WindowText for a label, ButtonText for a button, Text for a list - and a
#: role left at the platform's value would read as declared.
_ALIEN_ROLES = (
    QPalette.ColorRole.WindowText,
    QPalette.ColorRole.Text,
    QPalette.ColorRole.ButtonText,
    QPalette.ColorRole.BrightText,
    QPalette.ColorRole.ToolTipText,
    QPalette.ColorRole.PlaceholderText,
    QPalette.ColorRole.HighlightedText,
    QPalette.ColorRole.Link,
    QPalette.ColorRole.LinkVisited,
)

#: The Qt classes that paint a string of their own. Held to declaring a
#: foreground whatever they are painting today: a label built empty and filled
#: on the first frame draws text just as one built with its string does, and a
#: check that read `text()` would pass it while it was empty.
_TEXT_CONTROLS = (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
)

#: The frame shapes Qt rules from the foreground role. A `NoFrame` frame draws
#: no line at all and a `StyledPanel` is drawn by the style from its bevel
#: roles, so neither says anything about a foreground - which is what keeps
#: every panel and column container out of the walk without naming one.
_PLAIN_LINE_SHAPES = (
    QFrame.Shape.Box,
    QFrame.Shape.Panel,
    QFrame.Shape.WinPanel,
    QFrame.Shape.HLine,
    QFrame.Shape.VLine,
)


def _declared_colours() -> frozenset[str]:
    """Every colour `app/theme.py` declares, including both agent pairs.

    Read off the module rather than listed here: `contrast_check`'s
    `check_colors_live_in_the_theme` is what holds every colour to being
    declared there, so the module is the complete set by construction.
    """

    colours = {
        value.upper()
        for value in vars(theme).values()
        if isinstance(value, str) and _HEX_COLOUR.fullmatch(value)
    }

    for scheme in theme.AGENT_COLOR_SCHEMES.values():
        colours.update({scheme.fill.upper(), scheme.foreground.upper()})

    return frozenset(colours)


def _paints_its_own_content(widget: QWidget) -> bool:
    """Whether `widget` draws anything of its own in its foreground role.

    Three questions in order, because the first two would answer the third
    wrongly. A text control is in whatever it inherits from - `QLabel` is a
    `QFrame`, and asking the frame question first would drop every label on
    the dashboard. A frame that is not a plain line is a container or is drawn
    by the style, so it is out unless its class paints below `QFrame`; that is
    what keeps `MetricPanel`, `QSplitter` and the panels out of the walk while
    keeping `PlotWidget`, which is a `QGraphicsView` and paints its own scene.
    Everything else is in exactly when its class overrides `paintEvent`, which
    is the decidable form of "draws something nobody else declares".
    """

    if isinstance(widget, _TEXT_CONTROLS):
        return True

    if isinstance(widget, QFrame):
        plain_line = (
            widget.frameShape() in _PLAIN_LINE_SHAPES
            and widget.frameShadow() is QFrame.Shadow.Plain
        )

        return plain_line or type(widget).paintEvent is not QFrame.paintEvent

    return type(widget).paintEvent is not QWidget.paintEvent


def _content_painters(view: SimulationView) -> list[QWidget]:
    """Every widget of the built dashboard that paints its own content.

    A selector's popup is reached through `view()` rather than by the child
    walk: it is a window of its own, so `findChildren` never returns it, and
    it is where `PL-0NVN`'s rows were drawn from the host palette.
    """

    widgets: list[QWidget] = [view, *view.findChildren(QWidget)]

    for widget in list(widgets):
        if isinstance(widget, QComboBox):
            widgets.append(widget.view())

    return [widget for widget in widgets if _paints_its_own_content(widget)]


def _resolved_foreground(widget: QWidget) -> str:
    widget.ensurePolished()

    return widget.palette().color(widget.foregroundRole()).name().upper()


@pytest.fixture
def alien_foreground(application: QApplication) -> Iterator[QApplication]:
    """The application with every foreground role set to `_ALIEN_FOREGROUND`.

    On the application rather than on a widget, for the reason
    `tests/integration/test_dark_appearance.py` sets a host appearance there:
    a palette assigned to the widget under test would overwrite the
    declaration being tested instead of exercising it. The dashboard is built
    inside the fixture's scope so that every stylesheet resolves against this
    palette, and the views are deleted before it is restored, since the
    modules in this tree share one `QApplication`.
    """

    original = QPalette(application.palette())
    alien = QPalette(original)

    for role in _ALIEN_ROLES:
        alien.setColor(QPalette.ColorGroup.All, role, QColor(_ALIEN_FOREGROUND))

    application.setPalette(alien)

    yield application

    _delete_shown_views(application)
    application.setPalette(original)


def test_every_control_that_paints_its_own_content_declares_a_foreground(
    alien_foreground: QApplication,
) -> None:
    """`PL-4L49`: what declares nothing is drawn by the host, and says nothing.

    `tools/contrast_check.py` measures the pairs somebody wrote down. A
    control that writes none contributes to neither side of its count, so its
    report line reads the same whether the interface is covered or has three
    invisible controls on it - which is the state `PL-DHBX` was found in, by
    the project owner, on his own screen. The question it cannot answer is
    this one, and it needs a built tree rather than an `ast` walk: which
    widget a stylesheet actually reached is settled by Qt, not by the source.

    So every foreground role is set to a colour this interface never uses, the
    dashboard is built under it, and each content-painting widget is asked
    what it resolves to. A declared control answers with its own colour,
    because Qt folds a stylesheet's `color` into the widget's palette when it
    polishes it - and inherits it down from an ancestor's stylesheet exactly
    as it would on screen, which is why no rule here has to parse CSS or
    decide which selector reached what.
    """

    view = _shown_view(alien_foreground, SimulationController())
    declared = _declared_colours()
    painters = _content_painters(view)

    undeclared = sorted(
        {
            f"{type(widget).__name__} draws in {_resolved_foreground(widget)}"
            for widget in painters
            if type(widget).__name__ not in FOREGROUND_NOT_DECLARED
            and _resolved_foreground(widget) not in declared
        }
    )

    assert undeclared == [], (
        "these controls take their foreground from the host palette; declare each "
        "colour in app/theme.py with a requirement in tools/contrast_check.py, or "
        "name the kind in FOREGROUND_NOT_DECLARED with the reason it draws no text: "
        f"{undeclared}"
    )

    status = view.runs[0]._status_text
    status.setStyleSheet("")

    assert _resolved_foreground(status) == _ALIEN_FOREGROUND, (
        "a control stripped of its own declaration still read as a theme colour, so "
        "the walk above proved nothing"
    )


def test_no_control_kind_is_exempted_from_declaring_a_foreground_without_cause(
    alien_foreground: QApplication,
) -> None:
    """Every entry in `FOREGROUND_NOT_DECLARED` still names a live exemption.

    The half that keeps the list from becoming a comment nobody checks, which
    is what `tools/contrast_check.py` does with `KNOWN_SHORTFALLS`: an entry
    for a kind the dashboard stopped building, or for one that has since been
    given a foreground, fails here rather than sitting on as an exemption
    nothing needs. Both directions matter to the count the report line prints
    - it is the size of this mapping, and an entry that has stopped being true
    overstates what nothing measures just as a missing one understates it.
    """

    view = _shown_view(alien_foreground, SimulationController())
    painters = _content_painters(view)
    built = {type(widget).__name__ for widget in painters}

    absent = sorted(set(FOREGROUND_NOT_DECLARED) - built)

    assert absent == [], (
        "these kinds are exempted and the dashboard no longer builds them - remove "
        f"the entry: {absent}"
    )

    declared = _declared_colours()
    now_declaring = sorted(
        {
            type(widget).__name__
            for widget in painters
            if type(widget).__name__ in FOREGROUND_NOT_DECLARED
            and _resolved_foreground(widget) in declared
        }
    )

    assert now_declaring == [], (
        "these kinds declare a foreground now, so their exemption is stale - remove "
        f"the entry: {now_declaring}"
    )


# ---------------------------------------------------------------- the page


def test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar(
    application: QApplication,
) -> None:
    """Nothing holds the page wider than the window: the sidebar and every slider are on screen.

    The readout row reports a one-column minimum and the legend rows wrap,
    so the page's minimum is well inside the window and the scroll area
    never widens it; the chart column alone asks for less than a thousand
    pixels.

    The record panels measured are the ones the page holds, which the test
    below proves. They used to come from a second build of the panels,
    whose panels had no parent: `mapTo(page, ...)` assumes the page is
    an ancestor and checks nothing, so the last two assertions compared
    coordinates that never reached the page and could not fail (`PL-JS0X`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    scroll = view.findChild(QScrollArea)
    assert scroll is not None
    page = _page_of(view)

    assert page.minimumSizeHint().width() <= scroll.viewport().width()
    assert page.width() == scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert _concentration(view).minimumSizeHint().width() < 1000

    for slider in view.runs[0]._setting_controls[0].sliders:
        right_edge = slider.mapTo(page, slider.rect().bottomRight()).x()

        assert right_edge <= page.width(), "a setting control is laid beyond the page"

    for panel in _record_panels(view.runs[0]):
        assert page.isAncestorOf(panel), "a record panel measured is not on the page"
        assert panel.mapTo(page, panel.rect().bottomRight()).x() <= page.width()


def test_the_sidebar_panels_measured_are_the_ones_the_page_holds(application: QApplication) -> None:
    """Each panel the width test measures is the page's only panel of its kind, and is shown.

    Matched against the page's own children by the object name the panel's
    stylesheet is scoped by, so a rebuilt panel fails here, and so does a
    widget the heading might come to sit in between it and the panel. The
    second build of the panels that this replaced also moved the run's
    live labels out of the column the assertions before it had measured
    (`PL-JS0X`, `PL-N67T`).
    """

    view = _shown_view(application, SimulationController())
    page = _page_of(view)
    accounting, timeline = _record_panels(view.runs[0])

    for panel, name in ((accounting, "accountingPanel"), (timeline, "controlTimelinePanel")):
        assert page.findChildren(QWidget, name) == [panel], f"{name} is not the page's own"
        assert panel.isVisible(), f"{name} is not shown"


def test_a_second_build_of_the_record_panels_leaves_the_run_labels_on_screen(
    application: QApplication,
) -> None:
    """Asking a run again for its accounting or control-change panel leaves the placed one drawn.

    The method that built both used to build two new panels on every call and
    lay the run's own labels into them, and a layout takes a widget from
    wherever it sits: a second call moved the accounting status, its amounts
    and the control changes into panels with no parent, and the sidebar a
    learner was reading went empty of them (`PL-N67T`). Each label is held to
    being on screen and in its shared column before the call as well as after
    it, so the test cannot pass on a column that never showed them. The
    overflow line is hidden while nothing overflows, so it is held to its
    column alone. Since `PL-NWTM` the accounting panel is in the sidebar and
    the control-change panel in the unconditional region's record column.
    Since `PL-9LNF` the accounting panel may sit in an Area, so a second call
    builds a second copy for another Area and leaves the first where it is.
    The control-change panel stays in the region, so it is handed back.
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    sidebar = _accounting(view)
    records = view._record_column.parentWidget()
    placed = _record_panels(run)
    shown = (
        (run._accounting_panels[0]._accounting_heading_text, sidebar),
        (run._accounting_panels[0]._agent_accounting_status_text, sidebar),
        (run._accounting_panels[0]._agent_accounting_detail_text, sidebar),
        (run._accounting_panels[0]._agent_amounts_text, sidebar),
        (run._control_timeline_heading_text, records),
        (run._control_timeline_text, records),
    )

    assert sidebar is not None and records is not None

    for label, column in shown:
        assert label.isVisible(), "a run label is off screen before the second call"
        assert column is not None and column.isAncestorOf(label), (
            "a run label is outside its column to begin with"
        )

    again = (run.build_accounting_panel(), run.build_control_record())
    _settle(application)

    for label, column in shown:
        assert label.isVisible(), "a second call took a run label off screen"
        assert column is not None and column.isAncestorOf(label), (
            "a second call moved a run label out of its column"
        )

    assert records.isAncestorOf(run._control_timeline_overflow_text)
    assert again[0] is not placed[0], "a second call handed back the placed accounting panel"
    assert again[1] is placed[1], "a second call built a new control-change panel"


def test_a_second_build_call_leaves_each_run_widget_on_screen(application: QApplication) -> None:
    """Asking a run again for its transport row or readouts hands back the placed one.

    Each of the three used to lay the run's live widgets into a new container
    on every call, so a second call took the Start button, the substance
    heading and the fresh gas flow slider off screen, and dropping its result
    deleted them (`PL-KZR1`). Held the way the sidebar's test above holds its
    panels (`PL-N67T`): every widget is on the page before the call as well as
    after it, and each shown one stays shown, so the test cannot pass on a
    row that never showed them. Each case names a widget that has to be
    shown to begin with; the lone run's name and the agent chip are hidden
    in this state, so they are held to the page alone. The setting controls
    are not among the cases, because since `PL-9LNF` a second call builds a
    second copy for another Area (`tests/integration/test_run_surfaces.py`).
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    page = _page_of(view)
    transport = (
        run._run_name_text,
        run._agent_dropdown,
        run._running_agent_display,
        run._start_button,
        run._pause_button,
        run._reset_button,
        run._playback_rate_dropdown,
        run._status_text,
    )
    readouts = (run._compartment_substance_text, run._interpretation_text, run._readout_row)
    cases = (
        ("transport row", run.build_transport_row, run._start_button, transport),
        ("readout section", run.build_readout_section, run._compartment_substance_text, readouts),
    )

    for name, build, witness, widgets in cases:
        placed = widgets[-1].parentWidget()
        shown = tuple(widget for widget in widgets if widget.isVisible())

        assert witness in shown, f"the {name} is off screen before the second call"
        assert all(page.isAncestorOf(widget) for widget in widgets), f"the {name} is off the page"

        again = build()
        _settle(application)

        assert all(widget.isVisible() for widget in shown), f"a second call hid the {name}"
        assert all(page.isAncestorOf(widget) for widget in widgets), f"the {name} left the page"
        assert again is placed, f"a second call built a new {name}"


def test_spare_height_goes_to_the_plots_and_not_to_the_readouts(application: QApplication) -> None:
    """The region and the setting section stand at their own height; the chart row takes the rest.

    At the fixed test size the page is taller than the window and there is
    no spare; a window taller than the page's own hint has some, and every
    pixel of it lengthens the chart row while the region holding the
    readouts and the setting row above the charts do not move. The readout
    section is measured inside the region, where it has been since
    `PL-NWTM`.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    (settings,) = _setting_sections(view)
    chart_row = view.layout_container
    readout_section = view.unconditional_region
    page = _page_of(view)

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert abs(settings.height() - settings.sizeHint().height()) <= 2
    assert chart_row.height() >= chart_row.sizeHint().height() - 2

    settled_chart_row_height = chart_row.height()
    spare = 400
    view.resize(_WINDOW_WIDTH_PX, page.sizeHint().height() + spare)
    application.processEvents()

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert abs(settings.height() - settings.sizeHint().height()) <= 2
    assert chart_row.height() >= settled_chart_row_height + spare - 2
    assert chart_row.height() > chart_row.sizeHint().height()

    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    application.processEvents()


# ------------------------------------------------------------- two runs


def test_two_run_views_drive_two_controllers(application: QApplication) -> None:
    """`PL-B9PY`: two runs, two controllers, and neither states the other's numbers.

    A regression here would look like one branch's readouts standing over
    the other branch's numbers, which is the wrong-patient-context failure
    `CLAUDE.md`'s safety-critical standard names.
    """

    lean = SimulationController()
    generous = SimulationController()
    view = _shown_view(application, lean, generous)
    lean_run, generous_run = view.runs

    _set_fresh_gas_flow(lean_run, 1.0)
    _set_fresh_gas_flow(generous_run, 6.0)

    lean.start()
    generous.start()
    _advance_to(lean, 120.0)
    _advance_to(generous, 60.0)
    view.present(False)

    assert lean.snapshot().fresh_gas_flow_l_min == pytest.approx(1.0)
    assert generous.snapshot().fresh_gas_flow_l_min == pytest.approx(6.0)

    lean_flow = lean_run._setting_controls[0]._fresh_gas_flow_slider
    generous_flow = generous_run._setting_controls[0]._fresh_gas_flow_slider
    assert lean_flow.value_label.text() == format_flow(1.0)
    assert generous_flow.value_label.text() == format_flow(6.0)
    assert lean_run._elapsed_time_text.text() == format_elapsed(120.0)
    assert generous_run._elapsed_time_text.text() == format_elapsed(60.0)

    chart = _concentration(view).chart
    lean_times, lean_percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    generous_times, generous_percents = chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert lean_percents and generous_percents
    assert lean_times[-1] == pytest.approx(120.0)
    assert generous_times[-1] == pytest.approx(60.0)
    assert lean_percents[-1] != pytest.approx(generous_percents[-1])


def test_each_run_draws_only_its_own_recorded_values(application: QApplication) -> None:
    """The pairing hazard, doubled: a line must carry its run and its compartment.

    The model is linear in partial pressure, so a run at twice the dial
    reaches exactly twice every compartment at every instant: a line
    carrying the wrong run's values is visible in the drawn points rather
    than inferred.
    """

    single = SimulationController()
    double = SimulationController()
    double.set_delivered_concentration_percent(Percent(4.0))
    single.start()
    double.start()
    _advance(single, 60.0)
    _advance(double, 60.0)
    view = _shown_view(application, single, double)
    chart = _concentration(view).chart

    frame = chart.frame
    assert frame is not None
    # Every compartment the cap leaves drawn, which is what "each run draws
    # its own values" has to hold for; the cap itself is `PL-8PSW`'s own test.
    assert frame.visible

    for quantity in frame.visible:
        single_times, single_percents = chart.drawn_points(0, quantity)
        double_times, double_percents = chart.drawn_points(1, quantity)

        assert single_percents, f"{quantity} drew nothing on the first run"
        assert single_times == pytest.approx(double_times)
        assert double_percents == pytest.approx(tuple(2.0 * p for p in single_percents), rel=1e-9)


def test_one_compartment_selection_applies_to_every_run(application: QApplication) -> None:
    """`PL-HLD5`: unchecking a compartment takes it off the chart for both runs at once."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    view = _shown_view(application, first, second)
    chart = _concentration(view).chart
    # One of the two the cap leaves drawn, so what is being tested is the
    # selection reaching both runs rather than the cap removing a trace.
    quantity = RecordedQuantity.ALVEOLAR

    _set_trace_shown(application, view, quantity, False)

    assert chart.drawn_points(0, quantity) == ((), ())
    assert chart.drawn_points(1, quantity) == ((), ())

    _set_trace_shown(application, view, quantity, True)

    assert chart.drawn_points(0, quantity)[0]
    assert chart.drawn_points(1, quantity)[0]


def test_two_runs_cap_the_chart_at_two_compartments_and_say_so(application: QApplication) -> None:
    """`PL-8PSW`: the cap holds the selection, the boxes agree with it, and it is stated.

    The cap is what frees the line width for the run, so it is the half of
    the encoding that must hold whatever a reader does - including checking
    a third compartment, which takes the longest-standing one off rather
    than being silently ignored.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    single = _shown_view(application, first)

    assert _concentration(single).legend.shown == COMPARTMENT_QUANTITIES
    assert _concentration(single).capped_traces_text.isHidden() is True

    view = _shown_view(application, first, second)
    chart = _concentration(view).chart
    frame = chart.frame

    assert frame is not None
    # Reduced from six on the way in, to the top of the compartment table.
    assert _concentration(view).legend.shown == (
        RecordedQuantity.CIRCUIT,
        RecordedQuantity.ALVEOLAR,
    )
    assert frame.visible == (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    assert _concentration(view).capped_traces_text.isHidden() is False
    assert str(COMPARED_COMPARTMENT_CAP) in _concentration(view).capped_traces_text.text()

    _set_trace_shown(application, view, RecordedQuantity.FAT, True)

    # The third check is honoured and the oldest selection makes room for it,
    # so the boxes never name more curves than the plot draws.
    assert len(_concentration(view).legend.shown) == COMPARED_COMPARTMENT_CAP
    assert RecordedQuantity.FAT in _concentration(view).legend.shown
    assert _concentration(view).chart.frame is not None
    assert _concentration(view).chart.frame.visible == _concentration(view).legend.shown

    for quantity in COMPARTMENT_QUANTITIES:
        drawn = bool(chart.drawn_points(0, quantity)[0])

        assert drawn is (quantity in _concentration(view).legend.shown)


def test_the_window_fits_the_longer_of_two_runs(application: QApplication) -> None:
    """One window, wide enough for both, or one run is compared half-drawn."""

    short = SimulationController()
    long = SimulationController()
    short.start()
    long.start()
    _advance_to(short, 60.0)
    _advance_to(long, 600.0)
    view = _shown_view(application, short, long)
    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.stop_s >= 600.0
    assert _wash_in(view).chart.frame is frame
    assert _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)[0][-1] == (
        pytest.approx(600.0)
    )


def test_halting_one_run_leaves_the_other_advancing(application: QApplication) -> None:
    """A raise out of one run's step says nothing about the other run."""

    halted = SimulationController()
    untouched = SimulationController()
    halted.start()
    untouched.start()
    view = _shown_view(application, halted, untouched)

    view.runs[0]._halt_run(ValueError("mass balance violated"))

    assert halted.snapshot().failure_reason == "ValueError: mass balance violated"
    assert halted.is_running is False
    assert untouched.has_failed is False
    assert untouched.has_reached_supported_limit is False
    assert untouched.is_running is True

    _steps(view.runs[1], 1)

    assert untouched.snapshot().elapsed_s == SIMULATION_STEP_S


def test_a_frame_that_cannot_be_drawn_halts_every_run(application: QApplication) -> None:
    """The render loop draws all of them, so a raise out of it is nobody's."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    view._halt_every_run(ValueError("the frame could not be built"))

    assert first.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert second.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert first.is_running is False
    assert second.is_running is False


def test_the_interface_walk_reaches_the_axis_titles_and_the_accessible_names(
    application: QApplication,
) -> None:
    """The whole-interface walk covers what the Flet walk covered: axis titles too.

    The hedge and the wake-time walks guarantee only what the walk reaches,
    and the plots' axis titles and the legend boxes' accessible names are
    standing text a reader or a screen reader meets; both are on the walk
    (`PL-25KS`).
    """

    from anesthesia_sim.app.chart_frame import COMPARTMENT_TRACES
    from anesthesia_sim.app.dashboard_frame import TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE

    view = _shown_view(application, SimulationController())
    strings = set(view.interface_strings())

    assert {"% of 1 atm", "simulated time", "×MAC", "F_A/F_I"} <= strings
    assert {
        TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label)
        for style in COMPARTMENT_TRACES
    } <= strings


def test_the_dashboard_carries_the_educational_disclaimer(application: QApplication) -> None:
    """`PL-GMM7`: the educational disclaimer is on the dashboard, verbatim.

    `test_the_educational_disclaimer_says_what_the_tool_is_not` pins the
    words; this holds that the dashboard places them where a reader meets
    them, at the foot of the page, so the string the project's regulatory
    posture rests on cannot silently leave the screen.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT

    view = _shown_view(application, SimulationController())

    assert USE_DISCLAIMER_TEXT in view.visible_strings()


def test_a_value_hidden_from_the_reader_is_not_counted_as_shown(application: QApplication) -> None:
    """A View the reader cannot see is not counted as shown, and a replaced one is gone.

    A plot paints its axis titles itself, so they reach the walk through
    `View.painted_strings` rather than through a label (`PL-TH35`). Each title
    is visible only while the View that paints it is. The walk once counted
    the axis titles as on screen whatever happened to the plot (`PL-904Y`).
    Choosing another View for the chart's Area deletes the chart's View and
    keeps only its saved state, so its strings are no longer held at all, and
    a test that nothing says something still reaches every View that exists.
    The disclaimer is outside the Areas, so it stays visible. The expected
    strings are the concentration plot's axis title and a caption, written
    out here rather than read from the View.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT
    from anesthesia_sim.app.view_registry import WASH_IN

    view = _shown_view(application, SimulationController())
    in_the_chart = {"% of 1 atm", "Clinical references:"}

    assert in_the_chart <= _visible_strings(view)

    chart = _concentration(view)
    chart.hide()

    assert in_the_chart.isdisjoint(_visible_strings(view))
    assert in_the_chart <= _interface_strings(view)

    chart.show()
    view.layout_container.choose_view(AreaId(1), WASH_IN)
    _settle(application)

    assert in_the_chart.isdisjoint(_interface_strings(view))
    assert USE_DISCLAIMER_TEXT in _visible_strings(view)

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    _settle(application)

    assert in_the_chart <= _visible_strings(view)


def test_a_hidden_advisory_and_a_closed_combo_entry_are_held_but_not_shown(
    application: QApplication,
) -> None:
    """Present in the tree and visible to the reader are two answers (`PL-904Y`).

    The no-traces advisory waits hidden until every trace is off, and a
    combo shows its current entry only. Both are held, so a test that a
    string is never said still reaches them, and neither is told to the
    reader.
    """

    view = _shown_view(application, SimulationController())
    held = _interface_strings(view)
    visible = _visible_strings(view)

    assert NO_TRACES_SHOWN_TEXT in held
    assert NO_TRACES_SHOWN_TEXT not in visible
    assert format_playback_rate(1) in visible
    assert format_playback_rate(60) in held
    assert format_playback_rate(60) not in visible


# --------------------------------------------------------------- bookmarks
#
# The editing path end to end: a form filled in, a mark reaching both runs,
# and the listing a reader sees. `tests/unit/test_bookmarks.py` holds what a
# mark refuses and `tests/unit/test_dashboard_frame.py` what a row says; what
# is here is that the dialog is wired to every run rather than to one
# (`PL-LPLD`).


def _opened_bookmark_dialog(view: SimulationView) -> BookmarkDialog:
    """The editor, opened the way the button opens it."""

    view._bookmarks_panel.edit_button.click()
    dialog = view._bookmark_dialog

    assert dialog is not None

    return dialog


def test_a_dashboard_opens_with_both_collections_listed_as_empty(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    assert view._bookmarks_panel.times.text() == NO_TIME_BOOKMARKS_TEXT
    assert view._bookmarks_panel.targets.text() == NO_MAC_TARGETS_TEXT


def test_an_instant_entered_in_the_dialog_is_listed_beside_the_chart(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    assert "intubation" in view._bookmarks_panel.times.text()
    assert dialog.time_list.count() == 1


def test_the_entered_instant_is_restated_in_the_form_the_clock_uses(
    application: QApplication,
) -> None:
    # The spin box states one unit and the clock states three, so the dialog
    # carries the conversion rather than leaving it to the reader.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)

    assert dialog.instant_preview.text() == format_elapsed(600.0)


def test_a_target_entered_in_the_dialog_names_its_compartment_and_height(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

    listed = view._bookmarks_panel.targets.text()

    assert listed == "Vessel-rich 0.80 ×MAC"


def test_the_compartment_picker_offers_the_six_drawn_compartments_and_no_ratio(
    application: QApplication,
) -> None:
    # `WASH_IN_RATIO` is a quotient rather than a concentration, so a multiple
    # of MAC of it is not a quantity the model holds.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    offered = [
        dialog.compartment_combo.itemData(row) for row in range(dialog.compartment_combo.count())
    ]

    assert offered == [quantity.value for quantity in COMPARTMENT_QUANTITIES]
    assert RecordedQuantity.WASH_IN_RATIO.value not in offered


def test_the_height_control_stops_at_what_the_running_agent_can_reach(
    application: QApplication,
) -> None:
    # No compartment exceeds the delivered concentration and the vaporizer
    # bounds that, so a target above it is one no run of this agent could
    # cross. Refused in the control rather than reported afterwards.
    controller = SimulationController()
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    snapshot = controller.snapshot()
    reachable = mac_multiple(
        fraction_from_percent(snapshot.max_delivered_concentration_percent),
        snapshot.agent_mac_percent,
    )

    assert dialog.height_spin.maximum() == pytest.approx(reachable)

    dialog.height_spin.setValue(reachable * 2.0)

    assert dialog.height_spin.value() == pytest.approx(reachable)


def test_a_mark_added_from_the_dashboard_reaches_every_displayed_run(
    application: QApplication,
) -> None:
    # The marks are the case's. Two runs compared at two different heights,
    # because a learner typed one of them twice, is what writing to every run
    # makes unreachable.
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert len(first.snapshot().bookmarks.time_bookmarks) == 1


def test_every_displayed_run_carries_the_same_marks_after_an_add_and_a_removal(
    application: QApplication,
) -> None:
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    dialog = _opened_bookmark_dialog(view)

    for instant_s in (120.0, 600.0):
        dialog.instant_spin.setValue(instant_s)
        dialog.add_time_button.click()

    dialog.time_list.setCurrentRow(0)
    dialog.remove_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert [mark.instant_s for mark in first.snapshot().bookmarks.time_bookmarks] == [600.0]


def test_removing_with_nothing_selected_says_so_and_removes_nothing(
    application: QApplication,
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.time_list.setCurrentRow(-1)
    dialog.remove_time_button.click()

    assert dialog.notice.notice() == REMOVE_NOTHING_SELECTED_TEXT
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_marking_one_instant_twice_is_refused_and_says_why(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.add_time_button.click()

    notice = dialog.notice.notice()

    assert notice is not None
    assert "marked once" in notice
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_a_mark_edited_after_a_fork_reaches_the_branch_too(application: QApplication) -> None:
    """The invariant the marks panel now rests on, in the one shape `main` produces.

    `bookmark_panel` reads the reference run's mark *set* and every run's
    standings against it, so a branch whose set had drifted from the trunk's
    no longer draws the trunk's answer quietly - `BookmarkStandings` refuses
    the lookup, `present` catches it and the whole dashboard halts. That is
    the right direction under `CLAUDE.md`'s safety-critical standard, and it
    makes the invariant load-bearing in a way it was not.

    The three tests that hold it build two loose trunks, which is a
    configuration `main()` cannot produce: it opens one trunk and a
    `BranchedCase`. This walks the real one - fork, then add and remove from
    the dashboard - because `_branch_from` copies the set at the fork and
    `_apply_to_every_run` is what has to keep the two in step afterwards.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    trunk, branch = (run.controller for run in view.runs)

    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1

    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks

    dialog.time_list.setCurrentRow(0)
    dialog.remove_time_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks
    assert branch.snapshot().bookmarks.time_bookmarks == ()

    # And the panel still draws, which is what the refusal above would stop.
    view.present(False)

    assert view._bookmarks_panel.targets.text().startswith("Vessel-rich")


def test_a_refusal_leaves_every_run_carrying_the_same_marks(application: QApplication) -> None:
    # The refusal fires on the second run rather than the first only if the
    # two have drifted; this asserts they have not, which is the invariant
    # the write-to-every-run path exists for.
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks


def test_a_name_field_is_cleared_after_a_mark_is_added_and_the_value_is_not(
    application: QApplication,
) -> None:
    # Adding a second mark near the first is the common case, so the instant
    # stays; a reused name would name two marks alike, so the name goes.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    assert dialog.time_label_edit.text() == ""
    assert dialog.instant_spin.value() == 600.0


def test_the_dialog_and_the_panel_list_one_set_of_rows(application: QApplication) -> None:
    # Both read `dashboard_frame.bookmark_panel`, so a reader moving between
    # them is reading one listing in two places.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    listed = [dialog.time_list.item(row).text() for row in range(dialog.time_list.count())]

    assert view._bookmarks_panel.times.text() == "\n".join(listed)


def test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it(application: QApplication) -> None:
    # `PL-FPY2`: the two rows `PL-LHBY`'s review measured wrapping at 350 px.
    # Joined into one label, the first row's continuation began at the margin
    # every row begins at, so `Run 2 reached` read as a mark of its own and
    # attached one run's answer to the wrong mark.
    listing = MarkListingLabel()
    listing.set_listing(
        MarkListing(
            heading="MAC targets",
            rows=(
                "Fat 1.25 ×MAC – saturation probe · Run 1 not yet · Run 2 reached",
                "Alveolar 0.50 ×MAC · Run 1 reached · Run 2 not yet",
            ),
            empty_text=NO_MAC_TARGETS_TEXT,
        )
    )
    wrapped, below = listing.rows

    # Both dimensions follow the row, not a sidebar width in pixels, because
    # each was a bet on the font the host resolves for sans-serif (`PL-VCF0`).
    # The width is half the row's own one-line advance, so the row wraps under
    # any font. The height is the listing's height at that width, as the
    # sidebar's layout gives it: a bare window opens at the height its size
    # hint works out for a width of its own choosing, which under Inter at the
    # sidebar's narrow end, 300 px, was 66 px against the 81 px the wrap needs.
    width = wrapped.text_label.fontMetrics().horizontalAdvance(wrapped.text_label.text()) // 2
    listing.resize(width, listing.heightForWidth(width))
    listing.show()
    application.processEvents()

    continuation_x = wrapped.text_label.mapTo(listing, QPoint(0, 0)).x()
    next_row_x = below.bullet_label.mapTo(listing, QPoint(0, 0)).x()

    # The case is exercised only if the first row really does wrap here.
    assert wrapped.text_label.height() >= 2 * wrapped.text_label.fontMetrics().lineSpacing()
    assert below.bullet_label.text() == MARK_ROW_BULLET
    assert continuation_x > next_row_x
    assert wrapped.geometry().bottom() < below.geometry().top()


# The branch crosses 0.50 xMAC at 114.7 s, 547 steps after it opens at 60 s.
# A budget rather than "step until it stops": a test that fails by hanging
# reports nothing and costs a whole run to find out.
_BRANCH_STEP_BUDGET = 2000


def _halted_branch_view(application: QApplication) -> SimulationView:
    """A trunk paused below a marked height, and a branch that ran up through it.

    The trunk is paused at 60 s at 0.17 xMAC alveolar and never advances, so
    it is still running for a target at 0.50 xMAC. The branch is opened at
    that instant, its delivered concentration raised to the agent's ceiling,
    and stepped until the crossing halts it - at 114.7 s, which is where the
    offscreen reproduction on `PL-LHBY` put it.

    The time bookmark rides along for the second half of the same defect: at
    30 s it is behind the trunk's clock and before the branch's own opening
    instant, so the two runs answer it in opposite words.
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5)))
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))

    _take_fork(view, 60.0)

    branch = view.runs[1].controller
    branch.set_delivered_concentration_percent(
        branch.snapshot().max_delivered_concentration_percent
    )
    branch.start()

    for _ in range(_BRANCH_STEP_BUDGET):
        if not branch.snapshot().is_running:
            break

        branch.advance(SIMULATION_STEP_S)
    else:
        raise AssertionError(
            f"the branch ran {_BRANCH_STEP_BUDGET} steps without halting on the target; "
            f"it stands at {branch.snapshot().elapsed_s} s"
        )

    view.present(False)

    return view


def test_a_branch_halted_on_a_mark_says_so(application: QApplication) -> None:
    """`PL-LHBY`, the silent negative, end to end from the marks to the drawn row.

    The branch stops itself on a height the learner marked. Drawn from the
    reference run the row said nothing at all - the trunk was still running
    for that target - so the one on-screen indication that a run stopped
    where it was asked to existed for a lone run and vanished as soon as a
    second was drawn, leaving the halt indistinguishable from a Pause.

    Asserted on the run that halted *and* on the run that did not: naming
    only the branch would leave the trunk's silence to be read as the
    trunk having no answer rather than as its answer being "not yet".
    """

    view = _halted_branch_view(application)

    assert view.runs[1].snapshot().elapsed_s == pytest.approx(114.7)
    assert view.runs[1].is_running is False

    listed = view._bookmarks_panel.targets.text()

    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}" in listed
    assert f"{run_label(FIRST_RUN)} {MARK_STILL_RUNNING_TEXT}" in listed


def test_a_mark_the_branch_cannot_reach_is_not_drawn_as_the_trunk_left_it(
    application: QApplication,
) -> None:
    """`PL-LHBY`, the false positive, and the worse half of the pair.

    An instant the branch inherited but opened after read as the trunk's
    `passed`, so the screen asserted of the displayed branch something the
    model decides is false from `ResumePoint.fork.instant_s` alone.
    `MarkStanding.BEFORE_THIS_BRANCH` exists so that is not said, and no
    screen could reach it: the reference run is the trunk, and no instant
    stands before a trunk.
    """

    view = _halted_branch_view(application)

    listed = view._bookmarks_panel.times.text()

    assert listed.endswith(
        f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )
    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in listed


def test_a_failed_run_s_marks_do_not_stand_as_reachable(application: QApplication) -> None:
    """`PL-N3N5`, read as the adversarial review of `PL-LHBY` found it.

    One of two displayed runs is failed the way a raised step fails it -
    `RunView.halt` records the disposition, which is what the tick handler
    calls - and the whole screen is then read at one instant. The trunk's own
    panel said `Stopped - simulation error` while its clause on a mark it had
    not reached said `not yet`, which is `MarkStanding.STILL_RUNNING`
    asserting the run can still reach the mark, on a run
    `SimulationController.start` refuses to resume without a reset.

    The failed run is the trunk rather than the branch so that the *drawn*
    defect is reproduced and not only the standing behind it: the branch has
    something to say about both new marks, so the rows are attributed and the
    trunk's answer reaches the screen in words. Where the two runs agreed the
    row drew as silence instead, which is the same false claim made quietly.

    Both kinds are read, because a failure ends a clock and a height alike,
    and the trunk's inherited `passed` is read beside them: a failure stops a
    clock without taking it back, so the answers about what did happen stand.
    """

    view = _halted_branch_view(application)
    trunk = view.runs[0]
    # Marked after the fork and through the editor, so both runs hold them:
    # the set is the case's and `_apply_to_every_run` is what writes one. The
    # instant is ahead of the trunk's clock and behind the branch's, and fat
    # at 0.8 xMAC is out of reach of either run here, so each mark is left
    # outstanding on the trunk with the branch answering it.
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(90.0)
    dialog.add_time_button.click()
    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.FAT.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

    trunk.halt(_real_step_failure())
    view.present(False)

    assert trunk.controller.has_failed is True
    assert trunk._status_text.text() == STATUS_FAILED_TEXT

    said = MARK_STANDING_COMPARED_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]
    still_reachable = f"{run_label(FIRST_RUN)} {MARK_STILL_RUNNING_TEXT}"
    times = view._bookmarks_panel.times.text()
    targets = view._bookmarks_panel.targets.text()

    assert f"{run_label(FIRST_RUN)} {said}" in times
    assert f"{run_label(FIRST_RUN)} {said}" in targets
    assert still_reachable not in times
    assert still_reachable not in targets
    # The branch still answers for itself, and the trunk still reports what
    # it did reach before the failure.
    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in times
    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in times
    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}" in targets


def test_a_lone_run_states_a_mark_s_standing_without_naming_a_run(
    application: QApplication,
) -> None:
    # The other side of the same rule: an unattributed clause is a claim
    # about the case, and on one run it is one. A run name on every row of a
    # single-run panel would be the standing chrome
    # `.claude/rules/ui-reader.md` rules out, and it is what the dashboard
    # already refuses for the legend and the run headings.
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    _advance_to(controller, 60.0)
    # Marked behind the clock, so the run passes it without halting on it:
    # this test is about how the standing is attributed, not about the halt.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view.present(False)

    listed = view._bookmarks_panel.times.text()

    assert listed.endswith(MARK_STANDING_TEXT[MarkStanding.PASSED])
    assert run_label(FIRST_RUN) not in listed


def test_the_bookmark_panel_sits_outside_the_region_between_the_two_plots(
    application: QApplication,
) -> None:
    # `PL-F9TQ` governs what may stand between a chart heading and its plot.
    # The marks are the case's rather than either plot's, so they are a
    # section of their own below the Areas, in no View.
    view = _shown_view(application, SimulationController())
    page = _page_of(view)
    areas = view.layout_container
    marks = view._bookmarks_panel

    assert not areas.isAncestorOf(marks), "the marks sit inside an Area"
    assert page.isAncestorOf(marks)
    assert (
        marks.mapTo(page, marks.rect().topLeft()).y()
        >= areas.mapTo(page, areas.rect().bottomLeft()).y()
    ), "the marks are not below the Areas"


# ------------------------------------------------------------------ branching


def test_the_shipped_dashboard_opens_over_a_case_it_can_branch(application: QApplication) -> None:
    """`PL-VKJW`: every mechanism under v0.5.0's Goal had shipped and nothing called it.

    A dashboard handed loose controllers cannot branch and says so by not
    offering the control; one opened over a case offers it, from the trunk's
    own keyframes.
    """

    case = _branched_case()
    view = _case_view(application, case)

    assert view.case is case
    assert view.case.trunk is view.runs[0].controller
    assert view._fork_section.isHidden() is False
    assert view._fork_panel.take_button.isHidden() is False


def test_a_dashboard_over_loose_runs_offers_no_branch_control(application: QApplication) -> None:
    """A control that could only refuse is one presenting itself as working."""

    view = _shown_view(application, SimulationController())

    assert view.case is None
    assert view._fork_section.isHidden() is True


def test_a_dashboard_refuses_a_case_rooted_in_another_run() -> None:
    """Two curves on one axis assert one patient; a foreign case would misattribute it."""

    with pytest.raises(
        ValueError,
        match=re.escape(
            "a dashboard's case must be the one rooted in its first run, which is the "
            "trunk every branch of it is taken from"
        ),
    ):
        SimulationView((SimulationController(),), case=BranchedCase(SimulationController()))


def test_the_branch_control_offers_exactly_the_trunks_keyframes(application: QApplication) -> None:
    """`BranchedCase.fork_points_s`, rendered the way the clock renders time.

    Induction is offered rather than filtered out: a fork at zero is a second
    management of the whole case, and a case that has recorded nothing else
    would otherwise have an empty selector beside a live button.
    """

    case = _branched_case()
    view = _case_view(application, case)
    selector = view._fork_panel.point_selector
    offered = [selector.itemData(index) for index in range(selector.count())]
    labels = [selector.itemText(index) for index in range(selector.count())]

    assert case.fork_points_s == (0.0, 60.0)
    assert offered == list(case.fork_points_s)
    assert labels == [format_elapsed(instant_s) for instant_s in case.fork_points_s]


def test_taking_a_fork_adds_the_branch_to_the_dashboard(application: QApplication) -> None:
    """The run added after construction: the case gains a run and so does the display.

    `SimulationView` fixed its run set at construction until `PL-VKJW`, so a
    branch taken during a session had nowhere to be drawn. The branch is
    added last, leaving the run that happened in the first position, which
    is where the ×MAC ruler and the clinical references are read from.
    """

    case = _branched_case()
    view = _case_view(application, case)

    assert len(view.runs) == 1

    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert view.runs[0].controller is case.trunk
    assert view.runs[1].controller is case.branches[0]
    assert view.runs[1].controller.opened_from is not None
    assert view.runs[1].snapshot().elapsed_s == pytest.approx(60.0)
    assert view.runs[1].is_running is False


def test_taking_a_fork_redraws_the_chart_without_prompting(application: QApplication) -> None:
    """The press draws the frame the branch appears on, and nothing else has to ask for it.

    A fork is a discrete action, so it draws once and at once (`PL-R2YM`)
    rather than leaving the frame owed: both runs stand paused afterwards, so
    a frame left to the render tick would never be drawn. Nothing here
    presents after the press, so the frame read is the one the press drew,
    and a fork that added the run without redrawing fails on the one-run
    frame `_case_view` drew (`PL-624C`).

    The selection is narrowed, through the legend, to the pair the cap would
    draw first, so the second run leaves it as it stands.
    `test_a_fork_from_the_default_selection_draws_one_frame` takes the fork
    from a selection the second run reduces, which drew a second frame until
    `PL-B1R9`; between them a press draws once from either kind of selection.
    """

    case = _branched_case()
    view = _case_view(application, case)

    for quantity in _concentration(view).legend.shown[COMPARED_COMPARTMENT_CAP:]:
        _concentration(view).legend.set_compartment_shown(quantity, False)

    presented = view.presented_frames

    _take_fork(view, 60.0)

    assert view.presented_frames == presented + 1, "taking the branch did not draw it"

    frame = view._frame
    assert frame is not None
    assert len(frame.runs) == 2

    branch_times, _ = _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert branch_times, "the chart holds no curve for the branch"
    assert min(branch_times) == pytest.approx(60.0)


def test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis(application: QApplication) -> None:
    """One frame, both runs, and the branch's curve begins where it was taken.

    The frame read is the one the press drew, from the default selection
    rather than the narrowed one the test above takes the fork from. It used
    to present a frame itself first, which made every assertion below hold
    whether the fork redrew or not (`PL-624C`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    frame = view._frame
    assert frame is not None
    assert len(frame.runs) == 2

    trunk_times, _ = _concentration(view).chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    branch_times, _ = _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert min(trunk_times) == pytest.approx(0.0)
    assert min(branch_times) == pytest.approx(60.0)
    assert max(branch_times) <= max(trunk_times) + SIMULATION_STEP_S


@pytest.mark.parametrize("door", ["keyframe", "here", "mark"])
def test_a_fork_from_the_default_selection_draws_one_frame(
    application: QApplication, door: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One press, one frame, assembled once both runs know there are two, and telling both legends.

    The default selection is wider than `COMPARED_COMPARTMENT_CAP`, so the
    second run reduces it (`CompartmentSelection.with_run_count`), and the
    legend is shown the reduction. The reduction used to announce
    itself as a reader's change, and the dashboard drew a frame for it from
    inside `_rename_runs` - while the wash-in legend still counted one run and
    neither run had been named - before the press drew its own: two
    assemblies for one discrete action where `PL-R2YM` says one (`PL-B1R9`).
    Both legends are now told what a frame drew once it has drawn
    (`PL-G3K7`), so the frame is assembled with each run named and is what
    brings both legends to two runs.
    `test_taking_a_fork_redraws_the_chart_without_prompting` holds the count
    from a selection the cap leaves alone; this holds it from one the cap
    reduces, through every door a branch is taken by.
    """

    if door == "here":
        _, view = _halted_trunk_case(application)
    elif door == "mark":
        _, view, _ = _rewind_case(application)
    else:
        view = _case_view(application, _branched_case())

    assert len(_concentration(view).legend.shown) > COMPARED_COMPARTMENT_CAP, (
        "the default selection is inside the cap, so the press has nothing to reduce"
    )

    told: list[tuple[str, ...]] = []
    assemble = view._refresh_view

    def recording_assemble() -> None:
        told.append(tuple(run._run_name_text.text() for run in view.runs))
        assemble()

    monkeypatch.setattr(view, "_refresh_view", recording_assemble)
    presented = view.presented_frames

    if door == "here":
        view._fork_panel.here_button.click()
    elif door == "mark":
        _select_fork_entry(view, _BEHIND_MARK_LABEL)
        view._fork_panel.take_button.click()
    else:
        _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert len(_concentration(view).legend.shown) == COMPARED_COMPARTMENT_CAP, (
        "the cap reduced nothing"
    )
    assert view.presented_frames == presented + 1, "one press drew other than one frame"
    assert told == [(run_label(FIRST_RUN), run_label(SECOND_RUN))], (
        "the frame was assembled before the run set had been told it had grown"
    )
    assert _wash_in(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN)), (
        "the frame did not tell the wash-in legend"
    )


def test_the_run_added_after_construction_is_named_and_given_its_own_sections(
    application: QApplication,
) -> None:
    """Everything that reads the run count follows the addition, not the construction.

    The dashboard holds its compartment selection to the compared cap from
    this count, the legends name the runs from it, the panels carry the names the legend
    entries use, and each run has a section of setting controls of its own -
    so a second run adds one, and its readouts join the region (`PL-NWTM`).
    """

    view = _case_view(application, _branched_case())
    sections_before = len(_setting_sections(view))

    _take_fork(view, 60.0)
    _settle(application)

    assert len(_setting_sections(view)) == sections_before + 1
    assert view.unconditional_region.isAncestorOf(view.runs[1]._readout_row)
    assert _concentration(view).legend._run_count == 2
    assert _concentration(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN))
    assert _wash_in(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN))
    assert view.runs[0]._run_name_text.text() == run_label(FIRST_RUN)
    assert view.runs[1]._run_name_text.text() == run_label(SECOND_RUN)
    assert view.runs[1]._run_name_text.isHidden() is False


def test_the_wash_in_state_and_off_scale_lines_name_their_run(application: QApplication) -> None:
    """Both lines sit in the chart column the runs share, so each says whose value it is.

    Once a branch is drawn the column stacks one line per run, and the run
    names live in a different splitter section - so the only channel telling
    the two apart is stacking order, which nothing on screen declares. Read
    as the trunk's, the branch's F_A/F_I inverts the comparison the branch
    exists to teach, and its off-scale notice reports a clipped trace on a
    run that has none (`PL-25DD`).

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling, and the branch
    inherits the trunk's dial, so both runs draw a clipped circuit trace and
    both advisories are on screen at once - which is the case where a bare
    line is most easily taken for the other run's.

    No presentation is driven here beyond the one `_handle_fork` makes, so
    the names arrive on the frame the branch appears on rather than on some
    later tick.
    """

    trunk = SimulationController()
    trunk.start()
    trunk.set_delivered_concentration_percent(Percent(8.0))
    _advance_to(trunk, 600.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    trunk.pause()
    view = _case_view(application, BranchedCase(trunk))
    selector = view._fork_panel.point_selector
    _take_fork(view, selector.itemData(selector.count() - 1))
    _settle(application)

    assert len(view.runs) == 2

    for index, run in enumerate(view.runs):
        opening = f"{run_label(RUN_IDS[index])} — "
        assert run._wash_in_state_lines[0].text().startswith(opening)
        assert run._off_scale_lines[0].isHidden() is False
        assert run._off_scale_lines[0].text().startswith(opening)
        assert "Circuit" in run._off_scale_lines[0].text()


def test_a_lone_run_leaves_the_shared_chart_lines_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so the column carries no name.

    The rule the run panels and both legends already follow (`_rename_runs`),
    held here so the attribution `PL-25DD` adds does not become standing
    chrome on the display a learner opens.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._off_scale_lines[0].isHidden() is False
    assert run._off_scale_lines[0].text().startswith("Above the top of the plot:")
    assert run._wash_in_state_lines[0].text().startswith("Now: F_A/F_I =")
    assert run_label(FIRST_RUN) not in run._off_scale_lines[0].text()
    assert run_label(FIRST_RUN) not in run._wash_in_state_lines[0].text()


#: A dial position above every agent's calibrated vaporizer maximum, so the core
#: refuses it whichever agent the run is on. Driven through the handler because
#: the slider's own ceiling keeps it unreachable on the control.
_ABOVE_ANY_VAPORIZER_PERCENT = 50.0


def test_the_halt_and_refusal_banners_name_their_run(application: QApplication) -> None:
    """The notice column is shared, and all three banners assert something about a run.

    "Simulation stopped" read as the dashboard's says the case has stopped
    while the other run is still going, and "The simulation is unchanged and
    still running its previous setting" is false of the run it is not about -
    which is the misreading the hazard table's halted-versus-paused row
    exists to stop, arriving by attribution rather than by wording
    (`PL-TSZM`).

    One of each is driven at once, on different runs, because that is the
    case where the column holds two banners and neither names itself.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    assert len(view.runs) == 2

    trunk, branch = view.runs
    branch.controller.start()
    branch._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)
    trunk._halt_run(RuntimeError("the shared render path raised"))
    _settle(application)

    trunk_notice = trunk._notice_text.notice()
    branch_notice = branch._notice_text.notice()

    assert trunk_notice is not None
    assert trunk_notice.startswith(f"{run_label(FIRST_RUN)}: Simulation stopped")
    assert branch_notice is not None
    assert branch_notice.startswith(f"{run_label(SECOND_RUN)}: Setting refused")
    assert "The simulation is unchanged" in branch_notice


def test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped(
    application: QApplication,
) -> None:
    """`present_halt` has no frame by design, so the name cannot be read off one.

    It states a halt from the snapshot alone because the frame is what may
    have failed (`PL-25KS`), and `_halt_every_run` swallows the redraw that
    follows - so on a raise out of the shared render path this banner is the
    last one written. Taking the run count off the frame would drop the
    attribution in exactly that case (`PL-TSZM`).
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    for run in view.runs:
        run._frame = None

    view._halt_every_run(RuntimeError("the shared render path raised"))
    _settle(application)

    for index, run in enumerate(view.runs):
        notice = run._notice_text.notice()
        assert notice is not None
        assert notice.startswith(f"{run_label(RUN_IDS[index])}: Simulation stopped")


def test_a_banner_standing_when_a_branch_opens_is_named_from_that_frame(
    application: QApplication,
) -> None:
    """A refusal already on screen is about one run, and a fork puts a second beside it.

    "The simulation is unchanged and still running its previous setting" was
    true of the display while the trunk was alone and is false of the branch
    the moment it appears, so the name has to arrive on the frame the branch
    appears on rather than on some later tick (`PL-TSZM`).

    What delivers it is the presentation `_handle_fork` drives, which
    rewrites every run's banner through `_write_notice` after
    `_rename_runs` has named them - not a rewrite hung off `set_run_name`.
    That was written and removed: with the fork's own presentation and the
    Reset that drops a branch both already rewriting the banner, no scenario
    could tell it from its absence, and a guarantee nothing can fail is not
    one. This test is what holds the presentation in that role.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]
    trunk.controller.start()
    trunk._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)

    before = trunk._notice_text.notice()

    assert before is not None
    assert before.startswith("Setting refused")

    _take_fork(view, 60.0)
    _settle(application)

    after = trunk._notice_text.notice()

    assert after is not None
    assert after.startswith(f"{run_label(FIRST_RUN)}: Setting refused")


def test_a_lone_run_leaves_the_notice_banner_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so the banner is not named.

    The rule `_rename_runs` applies to the run panels and both legends, held
    here so the attribution does not become standing chrome on the display a
    learner opens.
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()

    run._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)

    notice = run._notice_text.notice()

    assert notice is not None
    assert notice.startswith("Setting refused")
    assert run_label(FIRST_RUN) not in notice


def test_the_sidebar_panels_name_the_run_they_record(application: QApplication) -> None:
    """Both panels sit in a column the runs share, so each heading says whose.

    Once a branch is drawn the sidebar stacks two accounting panels and the
    unconditional region's record column two control-change panels
    (`PL-NWTM`); before that one column stacked all four, and nothing on any
    of them said which run it recorded. Both carry a claim about one run: a
    mass-balance status with litres of equivalent pure agent gas, and a list
    of settings under the words "What was changed during this run". Read as
    the other run's, the second says the trunk received an intervention it
    never got (`PL-C3GS`).

    The trunk is given a setting change before the fork and the branch one
    after it, so the two control-change lists differ and misattributing
    either is a concrete wrong reading rather than a formal one.

    The attribution is asserted on the labels the panels hold rather than on
    freshly built ones, and each is then found under the shared column, which
    is what says the named heading is the heading on screen.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 120.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance_to(trunk, 600.0)
    trunk.pause()
    view = _case_view(application, BranchedCase(trunk))
    selector = view._fork_panel.point_selector
    _take_fork(view, selector.itemData(selector.count() - 1))
    _settle(application)

    assert len(view.runs) == 2

    branch = view.runs[1]
    branch.controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    view.present(False)
    columns = (_accounting(view), view._record_column.parentWidget())

    for index, run in enumerate(view.runs):
        name = run_label(RUN_IDS[index])
        headings = (
            run._accounting_panels[0]._accounting_heading_text,
            run._control_timeline_heading_text,
        )

        assert headings[0].text() == f"{ACCOUNTING_HEADING} — {name}"
        assert headings[1].text() == f"{CONTROL_TIMELINE_HEADING} — {name}"

        for heading, column in zip(headings, columns, strict=True):
            assert heading.isVisible(), "a panel heading naming the run is not on screen"
            assert column is not None and column.isAncestorOf(heading), (
                "the named heading is not in the shared column"
            )

    assert view.runs[0]._control_timeline_text.text() != branch._control_timeline_text.text()


def test_no_unconditional_value_sits_inside_the_layout_container(application: QApplication) -> None:
    """Every value `docs/MODEL.md` requires in every layout is in the region, outside the Areas.

    The layout container holds the Areas a reader resizes (`PL-W9P6`), so a
    value inside it is one a reader could close away once Areas can be
    closed (`PL-NWTM`). Held for both runs of a compared case,
    since the second run's widgets are placed an hour after the first's. The
    halt banner is hidden while nothing has halted, and is held to its place
    alone; every other value is on screen.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)
    required = unconditional_set(INHALED_AGENT).values

    assert len(view.runs) == 2
    assert len(required) == 14, "five invariant, eight per-substance and the record"

    for run in view.runs:
        widgets = run.unconditional_widgets()

        assert set(widgets) == set(required)

        for value in required:
            widget = widgets[value]

            assert not view.layout_container.isAncestorOf(widget), (
                f"{value.value} is inside the layout container"
            )
            assert view.unconditional_region.isAncestorOf(widget), (
                f"{value.value} is outside the unconditional region"
            )

            if value is not UnconditionalValue.HALT_REASON:
                assert widget.isVisible(), f"{value.value} is not on screen"


def test_the_readout_heading_states_the_dial_and_the_mac_it_divides_by(
    application: QApplication,
) -> None:
    """The region carries the delivered concentration in both units and the 1 MAC (`PL-NWTM`).

    Expected text is worked by hand: the dial opens at sevoflurane's own
    1 MAC, 2.0% (`data/agents/sevoflurane.json`), which is 1.00 ×MAC; moved
    to 3.0% it is 1.50 ×MAC.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._delivered_text.text() == "Delivered 2.00% (1.00 ×MAC)"
    assert run._one_mac_text.text() == "1 MAC sevoflurane = 2.0%"

    controller.set_delivered_concentration_percent(
        Percent(3.0, name="delivered_concentration_percent")
    )
    view.present(False)

    assert run._delivered_text.text() == "Delivered 3.00% (1.50 ×MAC)"
    assert run._delivered_text.isVisible()
    assert run._one_mac_text.isVisible()


@pytest.mark.parametrize("misplaced", ["missing", "in a splitter"])
def test_a_run_whose_region_lacks_a_declared_value_is_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, misplaced: str
) -> None:
    """The declaration decides what the region holds, so a run short of a value is not shown.

    Built with the 1 MAC statement taken out of the run's mapping, and with
    it pointed at a setting slider inside the splitter tree: a dashboard
    built either way would draw ×MAC numbers whose divisor a reader could
    close away.
    """

    original = RunView.unconditional_widgets

    def short_of_one_mac(run: RunView) -> dict[UnconditionalValue, QWidget]:
        widgets = dict(original(run))

        if misplaced == "missing":
            del widgets[UnconditionalValue.ONE_MAC]
        else:
            widgets[UnconditionalValue.ONE_MAC] = run._setting_controls[0]._fresh_gas_flow_slider

        return widgets

    monkeypatch.setattr(RunView, "unconditional_widgets", short_of_one_mac)

    with pytest.raises(RuntimeError, match="does not hold one_mac"):
        SimulationView((SimulationController(),))


def test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so neither heading gains a name.

    The rule `_rename_runs` already applies to the run panels and both
    legends, held here so `PL-C3GS`'s attribution does not become standing
    chrome on the display a learner opens.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 120.0)
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._accounting_panels[0]._accounting_heading_text.text() == ACCOUNTING_HEADING
    assert run._control_timeline_heading_text.text() == CONTROL_TIMELINE_HEADING
    assert run_label(FIRST_RUN) not in run._accounting_panels[0]._accounting_heading_text.text()
    assert run_label(FIRST_RUN) not in run._control_timeline_heading_text.text()


def test_dragging_the_border_beside_the_sidebar_changes_the_layout_model(
    application: QApplication,
) -> None:
    """A reader's drag of the one live border reaches the layout model, not only the widgets.

    The dashboard draws the chart panel and the sidebar as two Areas of one
    row (`PL-W9P6`). Dragging the border between them 100 px to the left
    leaves the chart panel's share of the row at its new width over the
    row's, as the pixels give it, and the sidebar wider by the same 100 px.
    """

    view = _shown_view(application, SimulationController())
    splitter = view.layout_container.findChild(QSplitter)
    assert splitter is not None, "the dashboard's Areas are not in a splitter"
    chart_px, sidebar_px = splitter.sizes()
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() - 100, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()

    tree = view.layout_container.model.windows[0].tree
    assert isinstance(tree, Split)
    assert splitter.sizes() == [chart_px - 100, sidebar_px + 100]
    assert tree.sizes[0] == pytest.approx((chart_px - 100) / (chart_px + sidebar_px), abs=1e-2)
    assert view.layout_container.frame(AreaId(1)).content is _concentration(view)


def _drag_area_border(application: QApplication, view: SimulationView, by_px: int) -> None:
    """Drag the border between the chart panel and the sidebar by `by_px`, as a mouse does."""

    splitter = view.layout_container.findChild(QSplitter)
    assert splitter is not None, "the dashboard's Areas are not in a splitter"
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() + by_px, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()


def test_resizing_one_chart_redraws_it_at_its_own_width(application: QApplication) -> None:
    """`PL-9LNF`: widening a chart's Area while paused redraws it, though the window kept its size.

    The frame on screen is sampled for the width it was drawn at (`PL-GS3R`).
    A drag of the Area border changes the chart's width and not the
    dashboard's, so a guard on the dashboard's own resize never fired: on
    `main` at `512fdaed` the tick after the drag drew nothing and the widened
    plot kept 2 px chords. Thirty minutes of history, so the frame has more
    instants than the narrowed plot has pixels and the chord is set by the
    columns rather than by the run.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    window_px = view.width()
    _drag_area_border(application, view, -400)
    view.present(False)
    narrowed_px = _concentration(view).chart.plot_width_px()
    presented = view.presented_frames

    _drag_area_border(application, view, 400)

    assert view.width() == window_px, "the drag resized the dashboard, not only the Area"
    assert _concentration(view).chart.plot_width_px() > narrowed_px + 300
    assert _widest_chord_px(view) > 1, "the drag did not widen the plot under the old frame"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _widest_chord_px(view) <= 1

    view.render_tick()

    assert view.presented_frames == presented + 1, "the tick kept drawing with nothing owed"


def test_narrowing_a_chart_owes_no_frame(application: QApplication) -> None:
    """A plot narrower than its frame's width draws chords closer than a pixel, and needs nothing.

    So only a widening is owed a frame (`resample_owed`); a tick after a
    narrowing drag draws nothing while paused, and no drawn chord is wider
    than a pixel.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    view.render_tick()
    presented = view.presented_frames

    _drag_area_border(application, view, -400)
    view.render_tick()

    assert view.presented_frames == presented
    assert _widest_chord_px(view) <= 1


def test_a_second_fork_is_refused_while_two_runs_are_shown(application: QApplication) -> None:
    """The display is capped at two and there is no run selector, so the way out is Reset.

    Refused visibly rather than silently: the control is hidden in the same
    form the transport hides the agent selector, and the reason stands where
    it stood. Replacing the shown branch while the first went on living
    inside `BranchedCase` would be state the screen does not carry.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    panel = view._fork_panel

    assert panel.take_button.isHidden() is True
    assert panel.take_button.isEnabled() is False
    assert panel.point_selector.isHidden() is True
    assert panel.point_selector.isEnabled() is False
    assert panel.lock_text.text() == comparing_fork_lock_text(COMPARED)
    assert panel.lock_text.isHidden() is False
    # The mode is not a warning: this interface has one alarm colour and a
    # comparison in progress is the dashboard working as intended.
    assert panel.notice.notice() is None

    view._handle_fork()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert panel.lock_text.text() == comparing_fork_lock_text(COMPARED)


def test_a_branch_is_offered_at_the_mark_the_run_is_standing_on(application: QApplication) -> None:
    """`PL-TYWQ`, and `ROADMAP.md`'s v0.5.0 Definition of done end to end.

    The one sequence the interface could not complete: mark the decision
    point, watch the run stop there, branch there. The branch opens at the
    instant the trunk halted on - not at the nearest keyframe, which is what a
    learner had to settle for - and it arrives through the same panel a
    control-event fork is taken from.

    The trunk is left standing on its halt, which is what makes this a
    comparison rather than an undo.
    """

    case, view = _halted_trunk_case(application)
    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    halted_s = halt.instant_s

    assert view._fork_panel.here_button.isHidden() is False
    assert halted_s not in case.fork_points_s

    view._fork_panel.here_button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    branch = case.branches[0]
    assert branch.snapshot().elapsed_s == pytest.approx(halted_s)
    assert view.runs[1].controller is branch
    # A mark adds no keyframe, so the trunk's keyframes are untouched by all
    # of this.
    assert case.fork_points_s == (0.0, 60.0)
    # And the trunk still stands where it stopped.
    assert case.trunk.snapshot().elapsed_s == pytest.approx(halted_s)
    assert view._fork_panel.notice.notice() is None


def test_the_fork_here_says_which_instant_it_will_open_the_branch_at(
    application: QApplication,
) -> None:
    """The label carries the halted instant, so a press is readable before it is made.

    A bare "Branch here" beside the permanent one would leave two identical
    buttons doing different things. The instant is the one the branch opens
    at rather than the one the learner marked: those differ whenever a mark
    lies inside a step, and naming the wrong one would be a correct control
    under a wrong label.
    """

    case, view = _halted_trunk_case(application)
    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None

    label = view._fork_panel.here_button.text()

    assert label == HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halt.instant_s))

    view._fork_panel.here_button.click()

    assert case.branches[0].snapshot().elapsed_s == pytest.approx(halt.instant_s)


def test_a_mark_inside_a_step_branches_where_the_run_stopped_not_where_it_was_marked(
    application: QApplication,
) -> None:
    """The safety-relevant half of the label, end to end (`PL-TYWQ`).

    A mark that does not land on the step grid halts the run at the step's
    end, so the instant a learner marked and the instant a branch can open at
    are two different numbers. The branch opens at the second - it is the only
    one the run holds state for - so the button has to say the second. Saying
    the first would be a correct control under a label naming a time nothing
    happens at, which `CLAUDE.md`'s safety-critical standard counts as a
    failure of the value rather than of its presentation.
    """

    marked_s = 80.05
    halted_s = 80.1
    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(marked_s), "mid-step"))
    case.trunk.start()
    _advance_to(case.trunk, halted_s)
    view.present(False)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    assert halt.instant_s == pytest.approx(halted_s)
    assert halt.instant_s != pytest.approx(marked_s)

    label = view._fork_panel.here_button.text()

    assert format_elapsed(halted_s) in label
    assert format_elapsed(marked_s) not in label

    view._fork_panel.here_button.click()

    assert case.branches[0].snapshot().elapsed_s == pytest.approx(halted_s)


def test_the_fork_here_is_on_the_panel_whenever_the_trunk_stops_and_off_it_while_it_goes(
    application: QApplication,
) -> None:
    """`PL-Y2SL`: paused anywhere, the control is there; going, it is absent rather than inert.

    There on the paused trunk, gone once it starts, back with the halt's own
    words when a mark stops it, gone again on the next step, and back with the
    plain words when the learner pauses. The selector does not follow it,
    which is the point of making this a second control: a list that gained
    and lost a row would change membership under a reader who had looked
    away, where a control that is either there or not is detectable on sight.
    The mark the run stopped on joins the selector when the clock reaches it,
    as a mark the trunk has passed (`PL-W4XQ`), and the halt's ending does not
    take it away again.
    """

    case = _branched_case()
    view = _case_view(application, case)
    button = view._fork_panel.here_button
    offered_before = list(_offered_fork_instants(view))
    paused_s = case.trunk.snapshot().elapsed_s

    assert button.isHidden() is False
    assert button.isEnabled() is True
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_s))

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_HALT_MARK_S)))
    case.trunk.start()
    view.present(False)

    assert button.isHidden() is True
    assert button.isEnabled() is False
    assert button.text() == ""

    _advance_to(case.trunk, _HALT_MARK_S)
    view.present(False)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    assert button.isHidden() is False
    assert button.isEnabled() is True
    assert button.text() == HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halt.instant_s))
    offered_on_the_halt = list(_offered_fork_instants(view))
    assert offered_on_the_halt == [*offered_before, halt.instant_s]

    case.trunk.start()
    case.trunk.advance(SIMULATION_STEP_S)
    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is None
    assert button.isHidden() is True
    assert button.isEnabled() is False
    assert list(_offered_fork_instants(view)) == offered_on_the_halt

    case.trunk.pause()
    view.present(False)
    paused_again_s = case.trunk.snapshot().elapsed_s

    assert button.isHidden() is False
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_again_s))
    assert list(_offered_fork_instants(view)) == offered_on_the_halt


def test_a_paused_trunk_is_branched_where_it_stands_from_the_panel(
    application: QApplication,
) -> None:
    """`PL-Y2SL` end to end: paused between keyframes, one press branches right there.

    The trunk stands at 120 s, which is neither a keyframe nor a mark, so no
    entry in the selector names it; the button does, and the branch it takes
    opens at that instant and is drawn beside the trunk, which stays where it
    stood.
    """

    case, view, _ = _rewind_case(application)
    paused_s = case.trunk.snapshot().elapsed_s
    button = view._fork_panel.here_button

    assert paused_s not in _offered_fork_instants(view)
    assert button.isHidden() is False
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_s))

    button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert case.branches[0].began_at_s == paused_s
    assert view.runs[1].controller is case.branches[0]
    assert case.trunk.snapshot().elapsed_s == paused_s
    assert view._fork_panel.notice.notice() is None


def test_the_fork_here_is_refused_with_the_rest_while_two_runs_are_shown(
    application: QApplication,
) -> None:
    """The cap is on branches, not on the door a branch came through.

    Taken through the transient control, the second fork has to be refused
    exactly as the permanent one is - the display is capped at two runs and
    there is no run selector - so the control goes off the panel rather than
    staying live to apologise on press. The guard behind it holds too, for a
    press that reaches it anyway.
    """

    case, view = _halted_trunk_case(application)
    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert case.trunk.snapshot().bookmark_halt is not None
    assert view._fork_panel.here_button.isHidden() is True
    assert view._fork_panel.here_button.isEnabled() is False
    assert view._fork_panel.here_button.text() == ""

    view._handle_here_fork()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert view._fork_panel.lock_text.text() == comparing_fork_lock_text(COMPARED)


def test_a_fork_here_the_case_refuses_is_reported_and_adds_no_run(
    application: QApplication,
) -> None:
    """The trunk can be started after the frame that drew the button, so the press re-asks.

    Where a running trunk stands moves with every step, so the case refuses
    a fork there rather than taking one a step or a tick from the instant
    the button named, and the reason reaches the notice instead of being
    swallowed - the panel's own frame is not proof that the fork is still
    there.
    """

    case, view = _halted_trunk_case(application)
    case.trunk.start()

    view._fork_panel.here_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = view._fork_panel.notice.notice()
    assert notice is not None
    # It names what is wrong rather than reporting a generic failure, so a
    # reader who pressed a button that was there a moment ago learns why.
    assert "is going" in notice


def test_a_failing_frame_on_a_paused_trunk_withdraws_branch_here(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A paused trunk whose frame fails stops offering a branch where it stands.

    "Branch here" is offered at every pause (`PL-Y2SL`), and the panel was
    redrawn only at the end of a frame, so with every frame failing the trunk
    read "Stopped - simulation error" beside a live "Branch here: 1m", and a
    press was refused by the case with the refusal lost to the next failing
    frame (`PL-MMNX`). The halt now restates the panel from the case, which
    offers no fork on a failed trunk.
    """

    case = _branched_case()
    view = _case_view(application, case)
    here = view._fork_panel.here_button
    assert here.isHidden() is False, "the paused trunk offers no branch here to withdraw"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert case.trunk.has_failed is True
    assert case.here_fork_point is None
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert here.isHidden() is True
    assert here.isEnabled() is False


def test_a_trunk_halted_by_a_failing_frame_offers_no_branch_at_all(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trunk halted by the shared frame offers no keyframe, no mark and no "Branch here".

    A branch opened there would be drawn by the same failing frame and halt
    on the next one, so each of the three could only fail (`PL-T2Q2`). Before
    this, the keyframe selector's Branch button stayed live and `fork_at`
    opened the branch. The case refuses the doors as well as the offer.
    """

    case = _branched_case()
    mark = TimeBookmark(CaseInstant(30.0), "check")
    case.trunk.add_time_bookmark(mark)
    view = _case_view(application, case)
    panel = view._fork_panel
    # Induction, the mark the trunk passed and its one setting change.
    assert panel.point_selector.count() == 3, "the trunk offers no keyframe or mark to withdraw"
    assert panel.here_button.isHidden() is False, "the paused trunk offers no branch here"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert panel.point_selector.count() == 0
    assert panel.point_selector.isHidden() is True
    assert panel.take_button.isHidden() is True
    assert panel.take_button.isEnabled() is False
    assert panel.here_button.isHidden() is True
    assert case.fork_points_s == ()
    assert case.mark_fork_points == ()

    with pytest.raises(SimulationConfigurationError, match="the frame this run is drawn in failed"):
        case.fork_at(CaseInstant(60.0))

    with pytest.raises(SimulationConfigurationError, match="the frame this run is drawn in failed"):
        case.fork_at_mark(mark)

    assert case.branches == ()


def test_a_trunk_failed_on_its_own_step_keeps_its_earlier_keyframes_branchable(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trunk whose own step failed keeps the keyframes it recorded, and a branch opens at one.

    Each keyframe is a state the run computed before the failure, and the
    frame still draws, so "go back and try something else" stays on offer
    (`PL-T2Q2`). Only the frame's failure withdraws it. The instants are the
    fixture's own: induction, and the setting change it made at 60 s.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = case.trunk

    def failing_advance(simulation_step_s: float) -> NoReturn:
        raise _real_step_failure()

    trunk.start()
    monkeypatch.setattr(trunk, "advance", failing_advance)

    _steps(view.runs[0], 1)

    assert trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert _offered_fork_instants(view) == (0.0, 60.0)
    assert view._fork_panel.take_button.isHidden() is False

    _take_fork(view, 60.0)

    assert len(case.branches) == 1
    assert len(view.runs) == 2
    opened_from = case.branches[0].opened_from
    assert opened_from is not None
    assert opened_from.fork.instant_s == 60.0


def test_a_fork_panel_the_case_cannot_restate_on_a_halt_offers_nothing(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A halt whose fork panel raises when restated withdraws the panel and still stands.

    The restatement runs inside the halt path, where a raise would escape the
    render path's guard into the toolkit and leave the halt's retry undone,
    so it is guarded, and a panel it cannot restate offers nothing rather
    than the last frame's offer (`PL-MMNX`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    assert view._fork_panel.point_selector.count() > 0

    def unanswerable(case: BranchedCase) -> NoReturn:
        raise RuntimeError("the case could not say where its trunk stands")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(BranchedCase, "here_fork_point", property(unanswerable))
    capfd.readouterr()

    view.present(False)

    assert "Traceback" not in capfd.readouterr().err
    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert view._fork_panel.here_button.isHidden() is True
    assert view._fork_panel.point_selector.count() == 0


def test_unmarking_the_mark_the_trunk_stopped_on_leaves_the_fork_here(
    application: QApplication,
) -> None:
    """Unmarking ends the halt and not the pause, so the control stays and drops the mark.

    The run stands where it stopped either way, and a learner who unmarks the
    instant they stopped on can still branch at it; what changes is that no
    mark stopped it there any more, so the label stops saying one did.
    """

    case, view = _halted_trunk_case(application)
    halted_s = case.trunk.snapshot().elapsed_s
    mark = case.trunk.snapshot().bookmarks.time_bookmarks[0]
    case.trunk.remove_time_bookmark(mark)
    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is None
    assert view._fork_panel.here_button.text() == HERE_FORK_LABEL_TEMPLATE.format(
        instant=format_elapsed(halted_s)
    )

    view._fork_panel.here_button.click()

    assert len(case.branches) == 1
    assert case.branches[0].began_at_s == halted_s


def test_a_branch_the_case_refuses_is_reported_and_adds_no_run(application: QApplication) -> None:
    """`resumed_at` refuses an instant that is not a keyframe rather than approximating.

    The control cannot offer such an instant - `fork_offer` builds it from
    `fork_points_s` - so an offer listing one is handed to the panel, the way
    a frame hands it the real one, to reach the guard behind it. A refusal
    leaves the case and the display untouched and says which instant was
    refused.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = view._fork_panel
    unkeyframed = ForkPoint(CaseInstant(30.0), format_elapsed(30.0), None)
    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0), unkeyframed.instant_s, CaseInstant(60.0)),
            marks=(),
            comparing=None,
            here=None,
        )
    )
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(30.0))

    assert panel.selected_point() == unkeyframed
    assert unkeyframed.instant_s not in case.fork_points_s

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = panel.notice.notice()
    assert notice is not None
    assert "30" in notice


def test_a_mark_branch_the_case_refuses_is_reported_and_adds_no_run(
    application: QApplication,
) -> None:
    """The mark door re-asks the case on the press, and its refusal reaches the notice.

    An entry outlives what it offers by the gap between a frame and a press,
    so `_handle_fork` hands the mark back rather than trusting the entry.
    Here the panel holds an entry for a mark the trunk does not hold - what an
    unmark landing in that gap leaves behind - and `fork_at_mark` refuses it,
    naming the instant, rather than branching anywhere near it.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = view._fork_panel
    unmarked = TimeBookmark(CaseInstant(30.0), "since removed")
    panel.set_offer(
        fork_offer(
            case.fork_points_s,
            marks=(MarkForkPoint(unmarked, CaseInstant(300 * 0.1)),),
            comparing=None,
            here=None,
        )
    )
    _select_fork_entry(view, f"{format_elapsed(30.0)}, on your mark")

    selected = panel.selected_point()
    assert selected is not None
    assert selected.mark == unmarked
    assert case.trunk.snapshot().bookmarks.time_bookmarks == ()

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = panel.notice.notice()
    assert notice is not None
    assert "no time bookmark stands at 30.0 s" in notice


def test_a_branch_control_with_nothing_selected_says_so(application: QApplication) -> None:
    """A press that cannot name an instant is reported rather than ignored."""

    view = _case_view(application, _branched_case())
    view._fork_panel.point_selector.clear()
    view._fork_panel.take_button.click()

    assert len(view.runs) == 1
    assert view._fork_panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_branch_shows_the_agent_chip_in_place_of_the_selector(application: QApplication) -> None:
    """`PL-QRD1`, the branch half: a branch carries the agent of the case it continues.

    `SimulationController.set_agent` refuses a branch outright (`PL-TFX5`),
    so a selector on its row would refuse every input it accepted. The chip
    says which lock is in force, and it is not the one a Pause would lift.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    branch = view.runs[1]

    assert branch._agent_dropdown.isHidden() is True
    assert branch._agent_dropdown.isEnabled() is False
    assert branch._running_agent_display.isHidden() is False
    assert branch._running_agent_lock_text.text() == BRANCH_AGENT_LOCK_TEXT


def test_the_trunks_selector_is_locked_while_two_runs_are_shown(application: QApplication) -> None:
    """`PL-QRD1`, the trunk half: `set_agent` succeeds on a trunk and destroys the case.

    With a branch displayed and the trunk paused, the trunk's selector was
    live. Choosing another agent restarted the trunk, left `BranchedCase`
    listing a branch of a run that no longer existed, and
    `assemble_chart_frame` then refused the frame over the shared MAC axis -
    so `_halt_every_run` failed both runs over an input to one of them. The
    switch is refused before it reaches the controller.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]

    assert trunk._agent_dropdown.isHidden() is False

    _take_fork(view, 60.0)

    assert trunk._agent_dropdown.isHidden() is True
    assert trunk._agent_dropdown.isEnabled() is False
    assert trunk._running_agent_lock_text.text() == COMPARING_AGENT_LOCK_TEXT
    assert trunk.snapshot().agent_id == "sevoflurane"

    trunk._reset_button.click()
    _settle(application)

    assert trunk._agent_dropdown.isHidden() is False
    assert trunk._running_agent_display.isHidden() is True


def test_resetting_the_trunk_ends_the_comparison(application: QApplication) -> None:
    """Reset is the way back to one run, and the case it leaves has no branches.

    The trunk has started over, so it never passed through the instant the
    branch was taken at: a branch left on the chart would be two curves
    asserting one patient under two managements while no longer being one.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    assert len(view.runs) == 2

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.case is not None
    assert view.case is not case
    assert view.case.trunk is view.runs[0].controller
    assert view.case.branches == ()
    assert _concentration(view).legend._run_count == 1
    assert view.runs[0]._run_name_text.isHidden() is True
    assert view._fork_panel.take_button.isHidden() is False
    assert view._fork_panel.lock_text.isHidden() is True
    assert view._fork_panel.notice.notice() is None
    # A branch just taken holds nothing, so the Reset asked nothing (`PL-W5WX`).
    assert view.runs[0]._reset_dialog is None


def test_a_refused_branch_does_not_survive_a_one_run_reset(application: QApplication) -> None:
    """`PL-75P5`: a refusal names an instant of the run the trunk's Reset has just ended.

    The one-run case is every case before a learner branches, and the guard
    that spares a one-run dashboard its layout work once returned before the
    refusal was cleared, so the banner went on reporting an instant the
    restarted run, standing at induction, does not hold.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = view._fork_panel
    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0), CaseInstant(30.0), CaseInstant(60.0)),
            marks=(),
            comparing=None,
            here=None,
        )
    )
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(30.0))
    panel.take_button.click()

    assert len(view.runs) == 1
    refusal = panel.notice.notice()
    assert refusal is not None
    assert "30" in refusal

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    assert view.runs[TRUNK_RUN_INDEX].snapshot().elapsed_s == 0.0
    assert view._fork_refusal is None
    assert panel.notice.notice() is None


def test_a_one_run_reset_leaves_a_case_with_no_branches(application: QApplication) -> None:
    """The case is a record of the trunk's run, so its Reset rebuilds it whatever is drawn.

    A branch the case keeps without the dashboard drawing it is what a fork
    whose drawing raised leaves (`PL-08SS`). Built here by forking the case
    directly, it must not outlive the trunk's Reset as a branch of a run that
    no longer exists, merely because one run was on screen.
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.fork_at(CaseInstant(60.0))

    assert len(view.runs) == 1
    assert len(case.branches) == 1

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    assert view.case is not None
    assert view.case is not case
    assert view.case.trunk is view.runs[TRUNK_RUN_INDEX].controller
    assert view.case.branches == ()


def test_resetting_a_branch_leaves_the_comparison_standing(application: QApplication) -> None:
    """A branch's Reset returns it to its fork; only the trunk's is a new case.

    The lock is asserted to be still there because that is the half a learner
    is surprised by (`PL-WG73`): the run they were trying to end has lost
    four steps of simulated case and the control they were sent to press is
    still refused, under the same sentence.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]
    branch._start_button.click()
    _steps(branch, 4)
    branch._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert view.case is case
    assert len(case.branches) == 1
    assert branch.snapshot().elapsed_s == pytest.approx(60.0)
    assert view._fork_panel.lock_text.isHidden() is False
    assert view._fork_panel.take_button.isHidden() is True


def _branch_holding_work(view: SimulationView, application: QApplication, work: str) -> RunView:
    """Take a branch at 60 s and give it one of the two kinds of work `has_recorded_run` reads.

    `elapsed` runs it four steps past its fork with nothing touched, and
    `change` records one fresh gas flow change at the fork with no time run.
    Either alone is work the trunk's Reset would discard.
    """

    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]

    if work == "elapsed":
        branch._start_button.click()
        _steps(branch, 4)
        branch._pause_button.click()
    else:
        _set_fresh_gas_flow(branch, 3.0)

    _settle(application)

    return branch


@pytest.mark.parametrize(
    ("work", "warning"),
    [
        (
            "elapsed",
            "Run 2 — branched at 1m and run to 1m0.4s, 0 recorded control changes — will be "
            "discarded along with its chart history. This cannot be undone.",
        ),
        (
            "change",
            "Run 2 — branched at 1m, 1 recorded control change — will be discarded along with "
            "its chart history. This cannot be undone.",
        ),
    ],
)
def test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work(
    application: QApplication, work: str, warning: str
) -> None:
    """`PL-W5WX`: the press is on Run 1, so Run 2's work is not discarded until the reader says so.

    Asked of both halves of `has_recorded_run`, because a question gated on
    either alone misses the other. The warning is a literal: four steps of
    0.1 s from the 60 s fork reach 1m0.4s on the case clock.
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, work)
    before = (branch.snapshot().elapsed_s, branch.controller.run_segments)

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    dialog = view.runs[TRUNK_RUN_INDEX]._reset_dialog
    assert dialog is not None
    assert dialog.isVisible() is True
    assert dialog.title_label.text() == "Reset Run 1 and discard Run 2?"
    assert dialog.body_labels[1].text() == warning
    assert len(view.runs) == 2
    assert view.case is case
    assert (branch.snapshot().elapsed_s, branch.controller.run_segments) == before
    assert view.runs[TRUNK_RUN_INDEX].snapshot().elapsed_s == pytest.approx(60.0)


def test_declining_the_trunks_reset_leaves_every_run_as_it_was(application: QApplication) -> None:
    """Keeping the branch keeps the trunk too: nothing is reset, and the comparison stands."""

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]
    branch_before = (branch.snapshot().elapsed_s, branch.controller.run_segments)
    trunk_before = (trunk.snapshot().elapsed_s, trunk.controller.run_segments)

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert dialog.keep_button.text() == "Keep Run 2"
    dialog.keep_button.click()
    _settle(application)

    assert trunk._reset_dialog is None
    assert len(view.runs) == 2
    assert view.case is case
    assert (branch.snapshot().elapsed_s, branch.controller.run_segments) == branch_before
    assert (trunk.snapshot().elapsed_s, trunk.controller.run_segments) == trunk_before


def test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch(
    application: QApplication,
) -> None:
    """Confirming does what the trunk's Reset did unasked before `PL-W5WX`."""

    case = _branched_case()
    view = _case_view(application, case)
    _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert dialog.discard_button.text() == "Reset and discard Run 2"
    dialog.discard_button.click()
    _settle(application)

    assert trunk._reset_dialog is None
    assert len(view.runs) == 1
    assert view.case is not None
    assert view.case is not case
    assert view.case.branches == ()
    assert trunk.snapshot().elapsed_s == 0.0


def _chart_span_in_viewport(view: SimulationView) -> tuple[int, int, int]:
    """The chart's top and bottom edges in the page's viewport, and the viewport's height."""

    scroll = view.findChild(QScrollArea)
    assert scroll is not None, "the dashboard has no scroll area"
    viewport = scroll.viewport()
    chart = _concentration(view).chart
    top = chart.mapTo(viewport, QPoint(0, 0)).y()

    return top, top + chart.height(), viewport.height()


@pytest.mark.parametrize("door", ["selector", "here"])
def test_taking_a_branch_leaves_the_concentration_chart_in_view(
    application: QApplication, door: str
) -> None:
    """`PL-562Z`: the chart the learner branched to compare on is wholly on screen afterwards.

    At 1600 x 1000 the branch's readouts push the chart down to about
    y 869-1229 of a 1000 px viewport, measured with this scroll removed on
    2026-10-18. Both branch controls are pressed, because both are ways to
    ask for the comparison.
    """

    view = _case_view(application, _branched_case(), width_px=1600)

    if door == "selector":
        _take_fork(view, 60.0)
    else:
        view._fork_panel.here_button.click()

    _settle(application)
    _settle(application)

    assert len(view.runs) == 2
    top, bottom, viewport_height = _chart_span_in_viewport(view)
    assert top >= 0
    assert bottom <= viewport_height


def test_the_page_stops_holding_the_chart_once_the_reader_scrolls(
    application: QApplication,
) -> None:
    """The scroll a branch makes is the dashboard's until the reader scrolls the page themselves.

    After that the reader owns the page, so a later change of layout - here
    a shorter window, which moves the chart - does not scroll it back.
    """

    view = _case_view(application, _branched_case(), width_px=1600)
    _take_fork(view, 60.0)
    _settle(application)
    scroll = view.findChild(QScrollArea)
    assert scroll is not None
    bar = scroll.verticalScrollBar()
    assert bar.value() > 0

    bar.triggerAction(QAbstractSlider.SliderAction.SliderToMinimum)
    view.resize(1600, 800)
    _settle(application)

    assert bar.value() == 0


def test_the_comparison_lock_names_the_run_whose_reset_ends_it(application: QApplication) -> None:
    """`PL-WG73` end to end: the words in the lock are on screen, on the button that works.

    `test_the_comparison_lock_names_a_control_the_learner_can_press` holds
    the sentence to what `run_label` and `RESET_LABEL` say; this holds that
    the runs those names address are the ones drawn, that each carries its
    name where a reader meets its Reset, and that the Reset the sentence
    sends them to is the one that lifts the lock. Neither half is worth
    anything alone - a name attributes a control only if the reader can find
    what it refers to.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)

    lock = view._fork_panel.lock_text.text()

    assert lock == comparing_fork_lock_text(COMPARED)

    for index, run in enumerate(view.runs):
        assert run._run_name_text.text() == run_label(RUN_IDS[index])
        assert run._run_name_text.isHidden() is False
        assert run._run_name_text.text() in lock
        assert run._reset_button.text() == RESET_LABEL
        assert run._reset_button.isHidden() is False

    # The run the way out is about, read off the sentence the way a learner
    # reads it rather than looked up by position: a lock naming both runs
    # correctly and pairing them with each other's outcomes would pass every
    # assertion above and still send the reader to the button that keeps the
    # mode.
    way_out, _, _ = lock.partition(";")
    named = [run for run in view.runs if run._run_name_text.text() in way_out]

    assert len(named) == 1
    assert named[0] is view.runs[TRUNK_RUN_INDEX]

    named[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view._fork_panel.lock_text.isHidden() is True
    assert view._fork_panel.take_button.isHidden() is False


def test_a_branch_added_while_the_dashboard_runs_gets_its_own_step_timer(
    application: QApplication,
) -> None:
    """`start_simulation_timer` started the runs that existed; this one did not.

    Without its own timer a branch would sit at its fork however often the
    learner pressed Start.
    """

    view = _case_view(application, _branched_case())

    _take_fork(view, 60.0)
    assert view.runs[1]._step_timer.isActive() is False

    view.runs[0]._reset_button.click()
    _settle(application)
    view.start_simulation_timer()

    try:
        _take_fork(view, 0.0)

        assert view.runs[1]._step_timer.isActive() is True
    finally:
        view.stop_timers()


def test_a_run_added_to_a_paused_dashboard_is_drawn_on_the_next_tick(
    application: QApplication,
) -> None:
    """`add_run` draws nothing, and the next render tick draws the run it added.

    A caller of the public method that did not present afterwards left the
    plot on the old run set while both legends already named the new one,
    because the tick drew only while a run ran or a frame was owed
    (`PL-0LG6`). The tick now reads the run set and the new run's unwritten
    record itself (`PL-X7D5`). A branch taken through the control still
    draws exactly once: its press draws the frame, and the tick after it
    finds nothing owed.
    """

    case = _branched_case()
    view = _case_view(application, case)
    presented = view.presented_frames

    view.add_run(case.fork_at(CaseInstant(60.0)))

    assert view.presented_frames == presented, "add_run drew a frame of its own"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert view._frame is not None
    assert len(view._frame.runs) == 2
    assert _concentration(view).chart.drawn_points(BRANCH_RUN_INDEX, RecordedQuantity.ALVEOLAR)[0]

    view.render_tick()

    assert view.presented_frames == presented + 1, "a frame drawn for nothing owed"

    taken = _case_view(application, _branched_case())
    presented = taken.presented_frames

    _take_fork(taken, 60.0)
    taken.render_tick()

    assert taken.presented_frames == presented + 1


def test_adding_a_third_run_is_refused(application: QApplication) -> None:
    """The cap is the display's, so it binds the public path as well as the control."""

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"2 runs are already displayed; at most {MAX_DISPLAYED_RUNS} may be displayed at once"
        ),
    ):
        view.add_run(SimulationController())


def test_adding_a_run_on_another_agent_is_refused(application: QApplication) -> None:
    """One ×MAC ruler cannot describe two agents, whenever the second run arrives."""

    view = _case_view(application, _branched_case())

    with pytest.raises(
        ValueError,
        match=re.escape(
            "every displayed run must be on the same agent, because they share one MAC axis "
            "and one set of clinical references; the dashboard is showing sevoflurane and "
            "this run is on desflurane"
        ),
    ):
        view.add_run(SimulationController(agent_id="desflurane"))


def test_a_mark_added_after_a_fork_reaches_both_runs(application: QApplication) -> None:
    """The marks are the case's, so the run added after construction is written too."""

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(300.0)
    dialog.add_time_button.click()

    marked = [run.snapshot().bookmarks.time_bookmarks for run in view.runs]

    assert len(marked) == 2
    assert marked[0] == marked[1]
    assert [bookmark.instant_s for bookmark in marked[0]][-1] == pytest.approx(300.0)


def test_resetting_a_case_less_dashboards_first_run_keeps_the_others(
    application: QApplication,
) -> None:
    """`PL-LQ19`: a dashboard with no case has no branches, so Reset drops nothing.

    The runs of a case-less dashboard are independent trunks - what the
    constructor admits and what the two-trunk tests build - so the first
    starting over says nothing about the second. Dropping it would destroy a
    recorded run over an input to another one, under the gesture a reader
    reaches for to start a single run again.
    """

    other = _paused_run_with_history()
    view = _shown_view(application, SimulationController(), other)

    assert view.case is None
    assert len(view.runs) == 2

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert view.runs[1].controller is other
    assert view.runs[1].snapshot().elapsed_s == pytest.approx(60.0)
    assert view.runs[1].snapshot().has_recorded_run is True


def test_add_run_refuses_a_run_the_case_never_sanctioned(application: QApplication) -> None:
    """`PL-K5NY`: two curves on one axis assert one patient, so a stranger is refused.

    Every guard but this one passed a fresh controller on the displayed
    agent: it was placed as "Run 2", drawn in the same frame against the same
    ×MAC ruler and named by `run_label` exactly as a branch is, while the
    case went on holding one run. `CLAUDE.md` names the correct number under
    the wrong patient context as a failure of the value.
    """

    case = _branched_case()
    view = _case_view(application, case)
    stranger = SimulationController()

    with pytest.raises(
        ValueError,
        match=re.escape(
            "a displayed run must be a branch of the case on the dashboard, because two "
            "curves on one axis assert one patient under two managements; this run is a "
            "trunk of its own and was never branched from this case"
        ),
    ):
        view.add_run(stranger)

    assert len(view.runs) == 1
    assert stranger not in case.runs


def test_add_run_refuses_a_branch_of_another_case(application: QApplication) -> None:
    """A run that is somebody else's branch is refused, and the message says which."""

    view = _case_view(application, _branched_case())
    elsewhere = BranchedCase(_paused_run_with_history())
    foreign = elsewhere.fork_at(CaseInstant(60.0))

    with pytest.raises(ValueError, match=re.escape("opened at 60.0 s but belongs to another case")):
        view.add_run(foreign)

    assert len(view.runs) == 1


def test_a_dashboard_with_no_case_cannot_gain_a_run(application: QApplication) -> None:
    """A second run is a branch of the first, and loose runs have no case to branch."""

    view = _shown_view(application, SimulationController())

    with pytest.raises(
        ValueError,
        match=re.escape("this dashboard holds no case, so it has no branches to display"),
    ):
        view.add_run(SimulationController())

    assert len(view.runs) == 1


def test_a_vanished_fork_instant_leaves_nothing_selected(application: QApplication) -> None:
    """`PL-J12Z`: a chosen instant that stops being a keyframe clears the control.

    Reachable without a reset. A keyframe collapses when a setting is
    returned to its previous value at the same instant, which is a learner
    changing their mind about a dial while paused. Falling back to the first
    entry would leave induction selected under a reader who had chosen a
    later decision point, and branch there on the next press.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = view._fork_panel

    assert case.fork_points_s == (0.0, 60.0)

    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))

    selected = panel.selected_point()
    assert selected is not None
    assert selected.instant_s == pytest.approx(60.0)

    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert case.fork_points_s == (0.0,)
    assert panel.selected_point() is None

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_fork_instant_still_offered_stays_selected_when_the_offer_grows(
    application: QApplication,
) -> None:
    """The other half of `PL-J12Z`: a rebuilt list keeps a choice it still offers.

    A running trunk adds a keyframe at each setting change, and the selector
    is rebuilt when one appears. `set_offer` finds the reader's choice by
    `ForkPoint` equality in the new list rather than with `findData`, which
    matches a `CaseInstant` only by identity, so an equal one built anew is
    found nowhere and the choice would be dropped (`PL-CN5S`).
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = view._fork_panel
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))

    trunk.start()
    _advance_to(trunk, 120.0)
    trunk.pause()
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert case.fork_points_s == (0.0, 60.0, 120.0)
    selected = panel.selected_point()
    assert selected is not None
    assert selected.instant_s == 60.0
    assert selected.mark is None


def test_a_cleared_fork_selection_stays_cleared_when_the_list_next_changes(
    application: QApplication,
) -> None:
    """`PL-J12Z`'s clear holds past the next rebuild, rather than lasting one frame.

    Qt selects the first entry of an emptied selector as soon as it is
    refilled, so a rebuild that set no index put *induction* under a reader
    whose choice had just been cleared - the substitution the clear exists to
    refuse, arriving one setting change later. Each mark the trunk's clock
    reaches is a rebuild too since `PL-W4XQ`, which makes that later change
    the common case rather than a rare one.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = view._fork_panel
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert panel.selected_point() is None

    trunk.start()
    _advance_to(trunk, 90.0)
    trunk.pause()
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    view.present(False)

    assert case.fork_points_s == (0.0, 90.0)
    assert panel.point_selector.count() == len(case.fork_points_s)
    assert panel.point_selector.currentIndex() == -1
    assert panel.selected_point() is None

    panel.take_button.click()

    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_mark_set_behind_the_trunk_s_clock_is_offered_and_branched_at(
    application: QApplication,
) -> None:
    """`PL-W4XQ` end to end: paused past a mark, a learner branches there from the selector.

    The mark was set after the clock had passed it, so no step crossed it,
    the trunk holds no keyframe there and the trunk is standing on no halt -
    the case the other two doors refuse. It is offered beside the control
    events, labelled with the instant the branch will open at rather than the
    one typed, and the branch opens there, while the trunk stays the case it
    was.
    """

    case, view, mark = _rewind_case(application)
    panel = view._fork_panel
    labels = [panel.point_selector.itemText(row) for row in range(panel.point_selector.count())]
    keyframes = case.fork_points_s

    assert case.trunk.snapshot().bookmark_halt is None
    assert _BEHIND_MARK_FORK_S not in keyframes
    assert labels == [
        format_elapsed(keyframes[0]),
        format_elapsed(keyframes[1]),
        _BEHIND_MARK_LABEL,
    ]
    assert format_elapsed(_BEHIND_MARK_S) not in _BEHIND_MARK_LABEL

    _select_fork_entry(view, _BEHIND_MARK_LABEL)

    selected = panel.selected_point()
    assert selected is not None
    assert selected.mark == mark
    assert selected.instant_s == _BEHIND_MARK_FORK_S

    panel.take_button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    branch = case.branches[0]
    assert view.runs[1].controller is branch
    assert branch.began_at_s == _BEHIND_MARK_FORK_S
    assert branch.snapshot().elapsed_s == _BEHIND_MARK_FORK_S
    assert panel.notice.notice() is None
    # The trunk is read and not written: no keyframe is recorded where it was
    # branched, and its clock stands where it was paused.
    assert case.fork_points_s == keyframes
    assert case.trunk.snapshot().elapsed_s == pytest.approx(_REWIND_PAUSE_S)


def test_a_mark_still_ahead_of_the_trunk_s_clock_is_not_offered(application: QApplication) -> None:
    """The case holds no state at a mark the clock has not reached, so nothing branches there.

    A branch there would be a prediction drawn as a run. The mark stops the
    running case when it is reached, and then joins the selector; until
    then the selector offers the control events and nothing else.
    """

    case, view, behind = _rewind_case(application)
    ahead = TimeBookmark(CaseInstant(600.0), "later")
    case.trunk.add_time_bookmark(ahead)
    view.present(False)

    selector = view._fork_panel.point_selector
    offered = [selector.itemData(row) for row in range(selector.count())]
    labels = [selector.itemText(row) for row in range(selector.count())]

    assert ahead in case.trunk.snapshot().bookmarks.time_bookmarks
    assert ahead.instant_s not in offered
    assert labels == [
        *(format_elapsed(instant_s) for instant_s in case.fork_points_s),
        _BEHIND_MARK_LABEL,
    ]
    assert [point.bookmark for point in case.mark_fork_points] == [behind]


def test_a_selected_mark_is_cleared_not_moved_when_the_learner_unmarks_it(
    application: QApplication,
) -> None:
    """`PL-J12Z` at the mark door: an entry the learner removes takes the selection with it.

    Unmarking is the mark's way of leaving the list, as a collapsed keyframe
    is a control event's. Moving the choice to a neighbour - induction, or
    the other mark beside it - would branch on the next press somewhere the
    learner did not choose, so the selector is left on nothing and the press
    says so.
    """

    case, view, mark = _rewind_case(application)
    later = TimeBookmark(CaseInstant(100.0))
    case.trunk.add_time_bookmark(later)
    view.present(False)
    panel = view._fork_panel
    _select_fork_entry(view, _BEHIND_MARK_LABEL)

    dialog = _opened_bookmark_dialog(view)
    dialog.time_list.setCurrentRow(case.trunk.snapshot().bookmarks.time_bookmarks.index(mark))
    dialog.remove_time_button.click()

    labels = [panel.point_selector.itemText(row) for row in range(panel.point_selector.count())]

    assert case.trunk.snapshot().bookmarks.time_bookmarks == (later,)
    assert _BEHIND_MARK_LABEL not in labels
    assert f"{format_elapsed(100.0)}, on your mark" in labels
    assert panel.point_selector.currentIndex() == -1
    assert panel.selected_point() is None

    panel.take_button.click()

    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_the_branch_selector_draws_its_widest_entry_whole(application: QApplication) -> None:
    """A mark's entry cut short would lose the words that say it is a mark.

    The selector is fixed in width (`theme.FORK_POINT_SELECTOR_WIDTH`) and its
    widest entry is a mark's late in the supported run, so the width is held
    against that entry in the font it is drawn in. The widest is found rather
    than assumed: the face spaces its digits proportionally, so the last
    step's 23h59m59.9s is not the widest reading. Hours, minutes and seconds
    vary independently, so the widest of each together is the widest clock
    `format_elapsed` can write, and it is offered through `fork_offer` and
    read back off the selector rather than measured as a bare string.
    """

    view = _case_view(application, _branched_case())
    panel = view._fork_panel
    metrics = panel.point_selector.fontMetrics()
    hours = max((f"{hour}h" for hour in range(10, 24)), key=metrics.horizontalAdvance)
    minutes = max((f"{minute}m" for minute in range(10, 60)), key=metrics.horizontalAdvance)
    seconds = max(
        (f"{whole}.{tenth}s" for whole in range(10, 60) for tenth in range(1, 10)),
        key=metrics.horizontalAdvance,
    )
    instant = CaseInstant(
        int(hours[:-1]) * SECONDS_PER_HOUR
        + int(minutes[:-1]) * SECONDS_PER_MINUTE
        + float(seconds[:-1])
    )

    assert format_elapsed(instant) == hours + minutes + seconds
    assert instant < MAXIMUM_ELAPSED_SIMULATION_TIME_S

    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0),),
            marks=(MarkForkPoint(TimeBookmark(instant), instant),),
            comparing=None,
            here=None,
        )
    )
    _select_fork_entry(view, f"{hours}{minutes}{seconds}, on your mark")
    option = QStyleOptionComboBox()
    panel.point_selector.initStyleOption(option)
    field = panel.point_selector.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox,
        option,
        QStyle.SubControl.SC_ComboBoxEditField,
        panel.point_selector,
    )

    assert metrics.horizontalAdvance(panel.point_selector.currentText()) <= field.width()


# --- one readout block at a laptop's width (`PL-F2YS`) -----------------------

#: The laptop reference `PL-J8K2` and `PL-84QX` measured the region at.
_LAPTOP_WIDTH_PX = 1366


def test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns(
    application: QApplication,
) -> None:
    """The record column takes the sidebar's share, so the readout row has room for seven.

    Asserted from the row's own reservation rather than from a pixel figure,
    so the test states the requirement on whatever font renders the panels:
    the row is as wide as seven panels need, and it seats all seven across.
    With the record at the box layout's 3:1 share the row was 3 px short of
    seven and opened on four (`PL-Z4K6`, `PL-J8K2` Q3).
    """

    view = _shown_view(application, SimulationController(), width_px=_LAPTOP_WIDTH_PX)
    _settle(application)
    row = view.runs[0]._readout_row

    assert row.width() >= row.width_for(len(READOUT_PANELS))
    assert row.columns() == len(READOUT_PANELS)


def test_two_runs_share_one_readout_block_whose_values_name_their_runs(
    application: QApplication,
) -> None:
    """Each compartment's panel carries both runs' values, and each value says whose.

    `docs/MODEL.md` § "Minimum displayed outputs" pairs the two values under
    one compartment name, so a second run adds lines to the block rather
    than a second row of seven panels. The names are restated as literals
    rather than read from `run_label`, which the legend also reads.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    trunk, branch = view.runs
    row = trunk._readout_row

    assert branch._readout_row.isHidden()
    assert row.columns() == len(READOUT_PANELS)

    for panel, compared in zip(row.panels, branch._readout_row.panels, strict=True):
        assert panel.isAncestorOf(compared.value_label), panel.name_label.text()
        assert panel.isAncestorOf(compared.secondary_label), panel.name_label.text()
        assert panel.name_label.text() == compared.name_label.text()
        assert panel.run_name_label.text() == "Run 1"
        assert compared.run_name_label.text() == "Run 2"
        assert panel.run_name_label.isVisible()
        assert compared.run_name_label.isVisible()


def test_dropping_a_branch_takes_its_values_out_of_the_shared_block(
    application: QApplication,
) -> None:
    """The trunk's Reset ends the comparison, and its panels go back to one run's values."""

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    labels_alone = [len(panel.findChildren(QLabel)) for panel in view.runs[0]._readout_row.panels]
    _take_fork(view, 60.0)
    _settle(application)

    view.runs[0]._reset_button.click()
    _settle(application)
    (trunk,) = view.runs

    assert [len(panel.findChildren(QLabel)) for panel in trunk._readout_row.panels] == labels_alone
    assert all(panel.run_name_label.isHidden() for panel in trunk._readout_row.panels)
    assert trunk.build_readout_section().isAncestorOf(trunk._delivered_text)
    assert trunk.build_transport_row().isAncestorOf(trunk._agent_header_badge)
    assert trunk._running_agent_display.maximumWidth() == AGENT_SELECTOR_WIDTH
    assert trunk._delivered_text.isVisible()
    assert trunk._agent_header_badge.isVisible()


def test_a_branch_taken_after_a_dropped_one_is_named_by_a_new_number(
    application: QApplication,
) -> None:
    """A run's name comes from its identity, so a later branch is never the dropped one's name.

    Named by drawing position, the second branch to stand beside the trunk was
    "Run 2" again, the same name as the branch the trunk's Reset dropped. A
    Workspace pinned to that dropped branch would then find a run of its name
    and show the new branch's values as if they were the old one's
    (`PL-7Z84`). The trunk keeps its identity through its own Reset.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    first_trunk, dropped_branch = (run.run_id for run in view.runs)

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)
    (restarted_at_s,) = _offered_fork_instants(view)
    _take_fork(view, restarted_at_s)
    _settle(application)
    trunk, branch = view.runs

    assert trunk.run_id == first_trunk
    assert branch.run_id not in (first_trunk, dropped_branch)
    assert [panel.run_name_label.text() for panel in trunk._readout_row.panels] == ["Run 1"] * len(
        trunk._readout_row.panels
    )
    assert [panel.run_name_label.text() for panel in branch._readout_row.panels] == ["Run 3"] * len(
        branch._readout_row.panels
    )
    assert view._fork_panel.lock_text.text() == comparing_fork_lock_text(
        ComparedRuns("Run 1", "Run 3")
    )
    assert _wash_in(view).legend._run_names == ("Run 1", "Run 3")


def test_two_compared_runs_take_one_line_each_above_one_shared_heading(
    application: QApplication,
) -> None:
    """Each compared run's controls and delivered concentration share one line, one control high.

    With two runs, each run's transport row and readout heading stood one
    above the other, and the four lines left the chart about 200 px on the
    1366 by 700 laptop reference (`PL-JG82`). Folded, a run's line carries
    its own delivered concentration, the agent chip lays its caption on the
    same line as the agent's name, and the values both runs share - the
    substance, the agent's 1 MAC and the version-and-model badge - are
    stated once, on the heading line above the paired readouts (`PL-QLZ5`).
    The playback-rate selector is the tallest control on a run's line, so it
    is the height one line is held to.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    trunk, branch = view.runs
    heading = trunk.build_readout_section()

    for run in view.runs:
        line = run.build_transport_row()

        assert line.isAncestorOf(run._delivered_text)
        assert run._delivered_text.isVisible()
        assert run._delivered_text.text() == "Delivered 2.00% (1.00 ×MAC)"
        assert run._running_agent_display.isVisible()
        assert line.height() <= run._playback_rate_dropdown.height(), "the line is two high"

    assert trunk._running_agent_display.width() == branch._running_agent_display.width()
    assert not branch.build_readout_section().isVisible()
    assert heading.isAncestorOf(trunk._agent_header_badge)
    assert trunk._agent_header_badge.isVisible()
    assert not branch._agent_header_badge.isVisible()
    assert trunk._compartment_substance_text.isVisible()
    assert trunk._one_mac_text.text() == "1 MAC sevoflurane = 2.0%"
    assert trunk._one_mac_text.isVisible()

    for value in (UnconditionalValue.ADMINISTERED_SUBSTANCE, UnconditionalValue.ONE_MAC):
        assert branch.unconditional_widgets()[value] is trunk.unconditional_widgets()[value]


# ------------------------------------------------- Views in the dashboard


def _copies_by_view(view: SimulationView) -> dict[str, tuple[QWidget, tuple[QWidget, ...]]]:
    """Each View that shows a run's surfaces, with the View and the copies it shows."""

    accounting = _accounting(view)
    concentration = _concentration(view)
    wash_in = _wash_in(view)

    return {
        "accounting": (accounting, accounting.copies),
        "off-scale": (concentration, concentration._off_scale.copies),
        "wash-in state": (wash_in, wash_in._states.copies),
    }


def test_each_view_places_one_copy_per_run_inside_itself(application: QApplication) -> None:
    """`PL-TH35`: a View shows its copies of the runs' surfaces in its own rectangle.

    Each run's line names the run (`PL-C3GS`), which another test reads off
    the run's own list of copies. That list cannot tell a copy placed in its
    View from one built and never placed, so this holds each copy to its View.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    assert len(view.runs) == 2

    for name, (shown_in, copies) in _copies_by_view(view).items():
        assert len(copies) == 2, f"{name}: {len(copies)} copies for 2 runs"

        for copy in copies:
            assert shown_in.isAncestorOf(copy), f"{name}: a copy is outside its View"

    for panel in _accounting(view).copies:
        assert panel.isVisible(), "an accounting panel is not shown"


def test_a_branch_dropped_while_frames_fail_leaves_no_copy_in_any_view(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A Reset that drops the branch takes its copies away even when no frame can be drawn.

    A View drops a run's copy when it is next refreshed, and with every frame
    failing it never is. The branch's accounting panel then stayed on screen
    with the status "Valid", beside the halted trunk, after the branch was
    gone. Each copy is now deleted with its run.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.runs[0].controller.has_failed is True

    for name, (_, copies) in _copies_by_view(view).items():
        assert len(copies) == 1, f"{name}: the dropped branch's copy is still shown"


def test_a_view_chosen_while_frames_fail_does_not_ask_again_every_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed frame is not retried on every render tick, for a View chosen after it either.

    A new View owed its first frame until one drew, so with every frame
    failing, each idle render tick assembled the frame again and halted every
    run again. The dashboard now records that the frame failed for these
    Views, and a View owes one again only once the Views change.
    """

    controller = _paused_run_with_history(60.0)
    view = _shown_view(application, controller)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    halts: list[Exception] = []
    halt = view._halt_every_run
    monkeypatch.setattr(view, "_halt_every_run", lambda error: (halts.append(error), halt(error)))

    view.layout_container.choose_view(AreaId(3), CONCENTRATION_CHART)
    chosen = len(halts)

    for _ in range(5):
        view.render_tick()

    assert chosen == 1, "the chosen View was not offered a frame at once"
    assert len(halts) == chosen, f"{len(halts) - chosen} idle ticks retried the failed frame"
