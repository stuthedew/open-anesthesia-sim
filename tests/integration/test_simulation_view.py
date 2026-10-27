"""The dashboard, driven headless against real runs.

`app/run_view.py` and `app/simulation_view.py` are the half of the dashboard
that uses the toolkit. `app/dashboard_frame.py` settles every string and every
per-tick claim without a toolkit, and `tests/unit/test_dashboard_frame.py`
tests that half. These tests cover the other half, against real
`SimulationController`s, under the `offscreen` platform that
`tests/conftest.py` selects. They check that the widgets say what the frame
said, and that a control a reader moves changes the run it belongs to and no
other. They check that the two timer slots keep the stepping and the drawing
separate. They also check that a refusal is shown as a notice, while an
exception raised by the run halts it.

The tests were ported claim by claim from the Flet suite that this file
replaces (`PL-25KS`). Each surviving test keeps its name where a closed item's
verify line greps for it. Flet's own mechanism is not carried over: the
wire-protocol patch counts, the per-point tooltip objects and the control
identity across frames. The one count that survives is
`SimulationView.presented_frames`, because the coalescing rule (`PL-R2YM`) is
about that count.

The dashboard is shown at one fixed size before its first presentation. A
frame is assembled from the plot's laid-out width, and a widget with no size
has no pixels for the hover to measure against.
"""

import ast
import importlib
import inspect
import re
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import cache, partial
from typing import Any, Final, NoReturn

import pytest
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPalette, QShortcut
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
    QScrollBar,
    QSplitter,
    QStyle,
    QStyleOptionComboBox,
    QWidget,
)

from anesthesia_sim.app import control_timeline as control_timeline_module
from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app import theme
from anesthesia_sim.app.area_layout import AreaLayout
from anesthesia_sim.app.bookmarks import MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    HOVER_INSTANT_RESOLUTION_S,
    format_trace_hover,
)
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    ChartTimeBase,
    time_base_for_span,
)
from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment, group_adjustments
from anesthesia_sim.app.controller import (
    BranchedCase,
    MarkForkPoint,
    RunSettings,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_FAILED_TEXT,
    ACCOUNTING_HEADING,
    ACCOUNTING_REJECTED_DETAIL_TEXT,
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
    WITHHELD_CONCENTRATION_TEXT,
    WITHHELD_MAC_MULTIPLE_TEXT,
    ComparedRuns,
    ForkPoint,
    MarkListing,
    accounting,
    comparing_fork_lock_text,
    delivered_line,
    fork_offer,
    halt_notice,
    new_case_question,
    notice,
    readouts,
    run_label,
    setting_readouts,
    slider_position,
    substance_heading,
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
from anesthesia_sim.app.halt_gate import halt_gate, passes_halt_gate
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_chart import TraceLegend
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
    PAGE_SPACING,
    PANEL,
    WARNING,
)
from anesthesia_sim.app.unconditional_set import (
    INHALED_AGENT,
    UnconditionalValue,
    unconditional_set,
)
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    WASH_IN,
)
from anesthesia_sim.app.views import (
    AccountingView,
    ConcentrationView,
    ParameterControlsView,
    WashInView,
)
from anesthesia_sim.app.wash_in import read_wash_in
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core import supported_ranges as supported_ranges_module
from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import (
    Fraction,
    MacMultiple,
    MacPercent,
    Percent,
    fraction_from_percent,
)
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
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
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: One Workspace that holds every View this build registers. Each test then
#: finds the View it reads, whichever Workspace is shipped first. The
#: parameter controls run across the top. Under them, the concentration chart
#: sits over the F_A/F_I plot, beside the accounting. That was the dashboard's
#: layout before it began opening on the shipped Workspaces (`PL-2KXB`).
_EVERY_VIEW = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Every View"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.COLUMN,
                            (0.25, 0.75),
                            (
                                Area(AreaId(4), PARAMETER_CONTROLS),
                                Split(
                                    Orientation.ROW,
                                    (0.82, 0.18),
                                    (
                                        Split(
                                            Orientation.COLUMN,
                                            (0.55, 0.45),
                                            (
                                                Area(AreaId(1), CONCENTRATION_CHART),
                                                Area(AreaId(3), WASH_IN),
                                            ),
                                        ),
                                        Area(AreaId(2), AGENT_ACCOUNTING),
                                    ),
                                ),
                            ),
                        )
                    ),
                ),
                AreaId(5),
            ),
        ),
    ),
    0,
)

# The identities that a dashboard gives the first runs it places, in order.
# They render as "Run 1", "Run 2" and "Run 3". A run is named from its identity,
# not from where it is drawn (`PL-7Z84`).
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


#: The dashboards that `_shown_view` built and has not yet deleted. A view left
#: to the garbage collector is deleted whenever a collection happens to run.
#: That can be inside a later test's `show()`, or at interpreter shutdown after
#: Qt's own statics have gone. Either one is a fatal error rather than a test
#: failure. So each view is kept here and deleted deliberately, before the next
#: dashboard is shown. `_torn_down_views` deletes the last one. Each time, the
#: event loop is still able to deliver the deferred deletion. The views are
#: deleted one at a time rather than all at the end, because draining a hundred
#: deferred deletions in one call took twenty seconds, and one takes twenty
#: milliseconds.
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
    view = SimulationView(controllers, case=case, workspaces=_EVERY_VIEW)
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
    """The whole page the dashboard lays itself out on.

    It holds the unconditional region at the top, the scrolling middle and
    the use disclaimer at the foot (`PL-NNML`).
    """

    page = view.findChild(QWidget, "dashboardPage")
    assert page is not None, "the dashboard has no page"

    return page


def _middle_of(view: SimulationView) -> tuple[QScrollArea, QWidget]:
    """The scroll area between the region and the disclaimer, and the middle it scrolls."""

    scroll = view.findChild(QScrollArea)
    assert scroll is not None, "the dashboard has no scroll area"
    middle = scroll.widget()
    assert middle is not None, "the scroll area holds no middle"

    return scroll, middle


def _record_panels(run: RunView) -> tuple[QWidget, QWidget]:
    """The accounting and control-change panels a run placed on the page, in that order.

    The accounting panel is in the sidebar beside the charts, and the
    control-change panel is in the unconditional region (`PL-NWTM`). Each panel
    is found through the heading placed in it, not through the build methods.
    So the tests below measure what the page holds, whatever those methods
    return. A second call to the method that built both panels used to build
    new panels with no parent and move the run's live labels into them
    (`PL-N67T`).
    """

    accounting = run._accounting_panels[0]._accounting_heading_text.parentWidget()
    timeline = run._control_timeline_heading_text.parentWidget()
    assert accounting is not None and timeline is not None, "a sidebar heading is in no panel"

    return accounting, timeline


def _setting_sections(view: SimulationView) -> list[QWidget]:
    """Each run's setting controls, in the first Area that shows the parameter controls."""

    controls = next(
        v for v in view.layout_container.views() if isinstance(v, ParameterControlsView)
    )

    return list(controls.copies)


def _steps(run: RunView, ticks: int) -> None:
    for _ in range(ticks):
        run.step_tick()


def _read_the_alveolar_quotient_as(monkeypatch: pytest.MonkeyPatch, quotient: float) -> None:
    """Make every alveolar compartment return `quotient` as its partial-pressure fraction.

    This is the one remaining way to get a quotient outside 0 to 1. No
    supported setting produces one (`core/concentration.py`). Since `PL-544D`,
    an amount larger than the capacity is refused when it is written. So the
    quotient that every alveolar compartment returns is replaced directly, for
    the snapshot and the stepper alike, instead of being produced through the
    stored amount.
    """

    monkeypatch.setattr(
        AlveolarCompartment, "partial_pressure_fraction", property(lambda compartment: quotient)
    )


def _readout_value(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].value_label.text()


def _readout_secondary(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].secondary_label.text()


def _drag(control: ParameterSlider, value: float, decimals: int) -> None:
    """Move a slider the way a reader's drag moves it, through the QSlider itself.

    The move goes through the control that the run actually holds and the
    signal it actually wired. So the tests check the wiring as well as the
    effect. A handler bound to the wrong run is exactly the mistake that a
    comparison of two runs has to guard against.
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


def _chosen_time_base(view: SimulationView) -> ChartTimeBase | None:
    """The window the concentration chart draws next, None for "Fit run"."""

    request = _concentration(view).frame_request()
    assert request is not None

    return request.time_base


def _select_time_base(view: SimulationView, key: str) -> None:
    combo = _concentration(view).time_base_selector
    index = combo.findData(key)
    assert index >= 0, f"the time-base control does not offer {key!r}"
    combo.setCurrentIndex(index)


def _set_trace_shown(
    application: QApplication, view: SimulationView, quantity: RecordedQuantity, shown: bool
) -> None:
    """Check or uncheck one compartment in the legend, as a reader clicking would.

    The change goes through the box, which is the route a click takes. The
    legend makes a request, and the dashboard's decision is what both the
    boxes and the chart then show (`PL-VN6M`). Once the two-compartment cap is
    in force, that decision keeps what was just asked for and drops the
    oldest selection.
    """

    _concentration(view).legend.set_compartment_shown(quantity, shown)
    application.processEvents()


def _paused_run_with_history(elapsed_s: float = 60.0) -> SimulationController:
    """A real, paused run holding both elapsed time and a recorded input.

    The run has both on purpose. `SimulationSnapshot.has_recorded_run` checks
    the two together, and a fixture that carried only one would leave the
    other untested by every test built on it.
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
    a keyframe at induction and another at `elapsed_s`. Those two instants are
    what `BranchedCase.fork_points_s` offers, and they are the only two
    instants at which `resumed_at` will open a branch.
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

    `findData` returns the first entry at that instant. Where a mark is also
    set at the same instant, that entry is the recorded control event, because
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
# 120 s. So a mark between the two lies behind the trunk's clock, at an instant
# for which the trunk holds no keyframe. That is the case `PL-W4XQ` asked for,
# and only a branch taken at a mark can open there.
_REWIND_CHANGE_S = 30.0
_REWIND_PAUSE_S = 120.0

# The mark set behind that clock, inside a step. The clock first reaches 75.05 s
# at the step ending at 751 x 0.1 s, so a branch taken there opens at a
# different instant from the one typed. The expected instant is written as the
# product the clock forms, not read from the controller, so that the test
# compares the two values instead of copying one.
_BEHIND_MARK_S = 75.05
_BEHIND_MARK_FORK_S = 751 * 0.1

# What the selector says for that mark, restated rather than built from
# `MARK_FORK_LABEL_TEMPLATE`, so an edit to the template cannot move both sides
# of an assertion at once.
_BEHIND_MARK_LABEL = f"{format_elapsed(_BEHIND_MARK_FORK_S)}, on your mark"


def _rewind_case(application: QApplication) -> tuple[BranchedCase, SimulationView, TimeBookmark]:
    """A case whose trunk is paused past a setting change, marked behind its clock.

    This is the owner's sequence at the scale of minutes. A learner paused at
    3 h marks 1 h, to go back and try something else there. The mark is set
    after the clock has passed it, so no step crossed it and the trunk never
    halted on it. The frame is drawn afterwards, so the panel is the one a
    learner would be looking at.
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
        # A combo reports no change when the same item is chosen again. A
        # reader who opens and closes it on the running agent still triggers
        # the handler, so the helper calls the handler directly.
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
    """Every string the dashboard holds, hidden ones included, to check what is never said."""

    return set(view.interface_strings())


def _visible_strings(view: SimulationView) -> set[str]:
    """The strings a reader can see now, to check what the reader is told (`PL-904Y`)."""

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
    tied to what `core/` does. If the core stopped raising a
    `SimulationNumericalError` here, this helper would fail, instead of letting
    the interface tests pass against an invented error. The failure is
    injected, because the exact propagator cannot carry a compartment out of
    range on its own (`PL-GS5X`). The injected failure stands in for the case
    that the guard still protects against.
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

    Each tissue's perfusion fraction is multiplied by `cardiac_output_l_min`
    divided by the patient's output, and written past the tissue's own guard.
    The patient keeps its output. A run's definition opens on a settings
    record, and that record then refuses the tissue flows, because they no
    longer sum to the output. It refuses them at the next step and at Reset
    (`PL-M4M0`), and no setting repairs them. No guarded write can produce
    this record now. Every flow is formed from the output (`PL-HQF5`), and a
    fraction is written once (`PL-Z0HN`). Before those changes, a tissue's
    `set_blood_flow` could produce it, and a cardiac output change repaired
    it. `_with_the_tissue_fractions_put_back` stands in for that repair.
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
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 0"),
    ):
        SimulationView(())


def test_a_dashboard_refuses_more_runs_than_may_be_displayed() -> None:
    """`ROADMAP.md` limits the comparison to two runs, for the reason below.

    With three runs, no visual channel is left to tell one run from another.
    Colour and line style carry the compartment, and line width has only two
    levels. A third curve would be drawn with nothing to identify it.
    """

    assert MAX_DISPLAYED_RUNS == 2

    with pytest.raises(
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 3"),
    ):
        SimulationView(tuple(SimulationController() for _ in range(MAX_DISPLAYED_RUNS + 1)))


def test_a_dashboard_refuses_two_runs_on_different_agents() -> None:
    """One ×MAC ruler and one set of references cannot describe two agents.

    With two agents on one chart, one run's traces would be read against the
    other agent's divisor. That gives a correct number under the wrong label,
    which `CLAUDE.md`'s standard treats as a failure of the value.
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

    `PL-DHBX`: a button that declares no foreground is drawn in the colour of
    Qt's palette `ButtonText` role. That role follows the host appearance
    rather than this interface. Under macOS Dark it went near-white, while
    every surface around it kept this light theme's colours. Both states are
    checked because the defect arrived twice. Declaring `:enabled` alone still
    left the *unavailable* button invisible on the project owner's screen.

    `transport_button_stylesheet` carries the colours. This test checks that
    `RunView` applies them, which a test of the helper alone would not catch.
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
    """Each button acts on the run through its own click, and draws its own frame."""

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
    """Running is drawn in the accent colour and Paused in muted, so word and colour agree."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert MUTED in run._status_text.styleSheet()

    run._start_button.click()

    assert ACCENT_TEXT in run._status_text.styleSheet()
    assert MUTED not in run._status_text.styleSheet()


# ------------------------------------------------------------ the sliders


def test_the_integer_sliders_span_the_supported_input_ranges(application: QApplication) -> None:
    """The ranges are read from the constructed controls, not from module constants."""

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

    The model treats that value as a fraction of one atmosphere, and the
    second assertion checks that magnitude.
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
    """Without the boundary, two turns of one dial would be recorded as one adjustment.

    Each slider's press is wired to the boundary, so a second act on the
    same control after a press is a second adjustment. The test observes this
    through the controller rather than by inspecting the connection, because
    PySide6 does not expose the connection.
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
    """One drag is one mark and one entry, however many settings the model was stepped under."""

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
    """Isoflurane's vaporizer stops at 5%, so 50% must be refused, and 150% is not a percent.

    The test calls the handler rather than dragging the slider, because the
    slider's own maximum makes both values unreachable on the control. That is
    exactly why the handler needs its own test. The two values are refused in
    different places. The circuit refuses 50% against the vaporizer maximum,
    and `Percent` refuses 150% when the handler builds it. So the handler
    builds the `Percent` inside the setting it applies, and names it. If the
    `Percent` were built before, its refusal would escape the handler, and no
    banner would say that the setting was refused (`PL-4R3W`).
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
    """No setting slot may let an exception raised by the core reach Qt's dispatcher.

    The sliders' own bounds make a negative flow unreachable in the running
    app. That is exactly why the guard needs its own test: under PySide6, an
    exception that escapes a slot is lost rather than shown.
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
    """`PL-V6M0`: an execution error is not a refusal and must not be shown as one."""

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
    """`PL-YK2V`: an exception from outside the project's hierarchy still halts the run."""

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

    The view beside the dial must still update at once, because it has to
    agree with the snapshot the moment the setting is applied (`PL-018`).
    The presentation waits: the chart assembly, the drawing and the captions.
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
    """A refused change is the one state whose frame the coalescing rule may not defer.

    A refused setting is the only case where the dial on screen and the
    simulation disagree. Waiting even one tick there leaves a control showing
    a setting that the run is not using.
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
    """The same fault in reverse: a notice left up after it stopped being true."""

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
    """The limit on deferring a frame still applies when a reader pauses, changes and resumes.

    While the run is paused there is no run to draw, but a dial can still move.
    So the tick draws a frame for a change that is owed one, and stops drawing
    once that frame is drawn.
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

    The number of steps a tick takes is set by the reader's playback setting,
    not by how long the tick took. So when a host wakes the tick late, the run
    falls behind the wall clock and stays behind.
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
    time. Nothing after the exception runs, in this tick or the next.
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
    """A discrete action presents through a signal, and Qt prints and drops a slot's exception.

    So the immediate presentation guards itself, as the render tick does.
    Without that guard, a frame that could not be drawn for a playback change
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
    """The frame is the shared render path, so a halt caused by its exception cannot wait for it.

    Every controller is failed. A reader has to see the status word and the
    banner that say so, and neither needs a frame. When one run's refresh
    raises on every attempt, the halt's own presentation raises too, and the
    exception is swallowed. Before `present_halt`, both status words went on
    showing the state from before the exception, with no banner under either.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    def failing_refresh(snapshot: object) -> None:
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
# These tests drive the run through the dashboard's own timers and the Start
# button. A test that steps the controller and presents by hand would draw the
# very frame that this path never asked for.

#: How long a real-timer test waits for its condition before it fails rather
#: than hangs. It is ample beside the half second of play that each test needs.
_REAL_TIMER_BUDGET_S = 10.0

#: Half a second of 1x play past the 60 s at which `_branched_case` pauses, so
#: the step timer reaches it in five ticks.
_TIMED_STOP_S = 60.5


def _render_ticks(view: SimulationView) -> list[None]:
    """A list the dashboard's render timer appends to each time it fires, after `render_tick`."""

    fired: list[None] = []
    view._render_timer.timeout.connect(lambda: fired.append(None))

    return fired


def _run_the_timers_until(condition: Callable[[], bool], what: str) -> None:
    """Let the dashboard's own timers fire until `condition` is true, or fail naming `what`."""

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

    The halt changes the run's record, and the tick compares that record with
    what the run's view last wrote (`PL-X7D5`). Before that change, the tick
    drew only while a run was running or a frame was owed. So until the
    learner pressed something, the screen showed "Running" with Pause offered,
    the clock one step short, and no offer to branch where the run stood
    (`PL-T995`).
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
    """The other stop that `step_tick` makes without an exception is drawn the same way.

    `SimulationController.advance` halts a run on the step that lands it on
    the supported run length, and raises nothing. So `RunView._halt_run`, the
    one branch of `step_tick` that asked for a frame, is never reached
    (`PL-T995`). The span is shortened to end half a second past the trunk's
    pause. The timers would take a day to reach the real span, and stepping a
    run to one step short of it takes about 27 s. `maximum_step_count` is the
    one count from which the controller and the core both read the span, so
    the two agree on the shortened span. Where a run stops on the real span is
    tested by
    `test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step`.
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
    """The halt stores the record it shows, so the comparison does not halt the run on every tick.

    A frame that raises halts every run, and the screen then shows the halt.
    If a run's record were stored only where a frame is drawn, the failed run
    would differ from its view's record on every later tick. The tick would
    then assemble, fail and halt again five times a second for as long as the
    dashboard stayed open (`PL-X7D5`). The two attempts are the tick's own
    attempt and the one retry that `SimulationView._halt_every_run` makes.
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
    """A halt shown from a fresh snapshot is not shown at all when the snapshot itself refused.

    `snapshot()` builds every compartment's fraction. So an alveolar quotient
    above 1 refuses the snapshot and, through it, the frame. The test gets
    that quotient by replacing what the compartment returns. No supported
    setting produces one (`core/concentration.py`), and since `PL-544D` a
    write larger than the capacity is refused. Before `PL-7DJK`,
    `present_halt` read a fresh snapshot for the status word, the transport
    and the banner. So the same refusal escaped the render tick, with the
    controller failed and the screen showing "Running", Pause offered and no
    banner. The three are now written from `SimulationController.record()`,
    which builds no compartment value. The banner says that no frame of the
    stopped run could be drawn, not that a step was rolled back.
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
    """A pick on a run halted by its own snapshot gets that halt, not an exception Qt prints.

    Inside a slot, `_handle_agent_change` reads the snapshot to choose between
    doing nothing, starting a new case and asking a question. On a run whose
    snapshot refuses (`PL-7DJK`), the read raised there. So the toolkit
    printed the traceback, and the pick was accepted with nothing on screen
    responding to it. No dialog appeared, and the selector named an agent
    that the run does not use (`PL-V2HC`). Now the exception from the read
    halts the run, and the halt is restated. That is the halt the run is
    already in, and the controller keeps its first reason. The selector is
    put back to the running agent, which the controller names because the
    snapshot cannot. Reset is still the way out that the banner names.
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
    """A dragged slider's immediate labels come from the snapshot, so its refusal halts the run.

    After a coalesced change, `_apply_setting` rewrites this run's own labels from a
    snapshot that it reads after applying the setting. Before `PL-HJKN`, that read
    happened outside the `try` block that applied the setting. So on a paused run whose
    snapshot refuses (`PL-7DJK`), the drag was accepted and the read raised an exception
    that escaped the slot. The dial moved, and the status word showed "Paused" over a
    run that no frame could draw. The toolkit printed an error, but nothing on screen
    reported it (`PL-V2HC`). The read now halts the run and shows the halt from the
    controller's status. In this test, the read is the first place where the halt is
    shown, because a paused run draws no frame that could refuse.
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

    `_apply_setting` applies the setting. Then the snapshot read that would
    rewrite the labels halts the run instead, and no frame is drawn. The
    value label is written only through `set_setting`. So it kept the value
    from before the drag, beside a dial set at the new value: "2.0 L/min"
    beside a dial at 4.0, with the circuit holding 4.0, until Reset
    (`PL-85LJ`, found at `PL-V2HC`'s review). The halt now writes every dial
    from `SimulationController.record()`, which builds no compartment value,
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

    `present_halt` writes the dials through `dashboard_frame.setting_readouts`.
    That function raises for a control that can offer no setting, such as a
    fresh gas flow range narrower than the dial's 0.1 L/min step. No shipped
    machine declares such a range. The circuit does not refuse one when it is
    built: `_require_the_two_flow_claims_overlap` in `core/circuit.py`
    refuses only an empty overlap, so a narrow range reaches
    `setting_readouts`. When the dials were written before the banner, that
    exception left the halt half shown: the status word and the transport
    were written, but no banner was. The exception also escaped the slot
    (found at `PL-85LJ`'s review). The dials now come last, so the three
    signs of the halt are on screen before the exception. The exception
    still escapes rather than being hidden.
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
    """Stand in for `assemble_chart_frame` in a test where every frame must fail."""

    raise RuntimeError("this frame could not be assembled")


def test_a_halt_after_an_agent_change_names_one_agent(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run halted on the first frame after an agent change names that agent everywhere.

    A run that has recorded nothing switches agent at once on a pick, so the
    frame that follows is the first to show the new agent. When that frame
    fails, `present_halt` is the only writer. It used to write the dials but
    nothing of the agent's identity. The screen showed "Delivered desflurane"
    under a subtitle, a chip and a heading that still named sevoflurane, in
    sevoflurane's colours (`PL-1YDD`). `present_halt` now writes every
    identity widget from the controller's record.
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


def test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-6RJ0`: every ×MAC number on screen was divided by the 1 MAC the line states.

    A halt writes the 1 MAC line and the delivered line from the controller's
    record, while only a frame writes the cards. So a halt on the first frame
    after an agent change left the cards holding sevoflurane's multiples,
    divided by 2.0%. Before `PL-6RJ0`, the 1 MAC line above them stated
    desflurane's 6.0%. Its first fix wrote the line together with the cards,
    so the line then stated sevoflurane's 2.0% beside a delivered line divided
    by 6.0%. The line now
    follows the record on both the frame path and the halt path, and the halt
    withholds the cards' multiples.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    drawn = controller.snapshot()
    sevoflurane_line = format_mac_reference(drawn.agent_display_name, drawn.agent_mac_percent)
    cards_before = [panel.value_label.text() for panel in run._readout_row.panels]

    assert run._one_mac_text.text() == sevoflurane_line

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    _select_agent(run, "desflurane")

    record = controller.record()
    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    assert run._one_mac_text.text() == format_mac_reference(
        record.agent_display_name, record.agent_mac_percent
    )
    assert run._one_mac_text.text() == "1 MAC desflurane = 6.0%"
    # The clock keeps the last frame's instant. No card keeps sevoflurane's percent
    # under the desflurane heading, or its multiple under desflurane's 1 MAC (`PL-J5GC`).
    clock = run_view_module._CLOCK_PANEL_INDEX
    assert run._readout_row.panels[clock].value_label.text() == cards_before[clock]

    for index, panel in enumerate(run._readout_row.panels):
        if index != clock:
            assert panel.value_label.text() == "\u2014%"
            assert panel.secondary_label.text() == "\u2014 \u00d7MAC"

    monkeypatch.undo()
    view_frame = run._readout_row.panels
    run.refresh(controller.snapshot())

    assert all(panel.secondary_label.text() != "\u2014 \u00d7MAC" for panel in view_frame), (
        "the first frame that draws writes every card's multiple again"
    )


def test_a_halt_on_the_first_frame_still_states_the_1_mac_line(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-6RJ0`: the 1 MAC line is an unconditional value, so the halt path writes it too.

    The cards were built from the run's first snapshot. Their multiples were
    therefore divided by the MAC of the run's own agent, and the cards keep them.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._one_mac_text.setText("")
    monkeypatch.setattr(controller, "_failure_reason", "the first frame failed")

    run.present_halt()

    record = controller.record()
    assert run._one_mac_text.text() == format_mac_reference(
        record.agent_display_name, record.agent_mac_percent
    )
    assert all(
        panel.secondary_label.text() != "\u2014 \u00d7MAC" for panel in run._readout_row.panels
    )


def test_a_drag_that_halts_the_run_lists_the_record_the_run_holds(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control-change panel of a run halted by a drag lists the changes the run holds.

    `_paused_run_with_history` leaves the fresh gas flow change it records
    open, so dragging the dial back to where it started takes that change off
    the record. On a run whose snapshot refuses, the drag halts the run and
    no frame is drawn. The panel then went on listing the change that the run
    no longer held (`PL-DTJQ`). The halt now writes the panel from the
    controller's record. It writes no undrawn marks, because no frame was
    drawn.
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


#: The widget attributes of a `RunView` that may show different content on a
#: run drawn by a frame and on the same run halted with every frame failing.
#: Each is mapped to the reason it may differ. The test below requires every
#: other widget attribute, including one added later, to show the same content
#: on both runs. That requirement makes `RunView._write_statement` the one
#: writer of a run's state, rather than a list that somebody has to maintain.
#: A widget left out of `_write_statement` still shows the last frame's run on
#: a halt, and the test fails there (`PL-X7D5`).
#:
#: The list is checked in both directions, as `FOREGROUND_NOT_DECLARED` is. An
#: entry that names no widget attribute fails. So does an entry whose widget
#: shows the same content on the two runs, because nothing then needs the
#: exemption. The accounting panel's status and detail lines are frame
#: widgets, but they are not listed. Both runs below show "Valid" there, so
#: the comparison checks them like any other widget.
FRAME_WIDGETS: dict[str, str] = {
    "_readout_row": (
        "the readouts and the clock they were read with, from the compartment "
        "values of the snapshot a frame drew from. The clock stays with its "
        "readouts, so no row pairs one instant's clock with another's values. "
        "The playback line under the clock is run state, and the test below "
        "compares it on its own (`PL-P58M`)."
    ),
    "_accounting_panels[0]._agent_amounts_text": (
        "the accounting panel's amounts, which are the snapshot's mass balance "
        "and so compartment values."
    ),
    "_notice_text": (
        "the banner. `_write_statement` writes it on both paths, worded for "
        "whether a frame drew: `halt_notice` says no frame of the stopped run "
        "has, and `notice` says the values shown are the last completed step. "
        "The test below holds each to its own wording."
    ),
}


def _widget_attributes(run: RunView) -> dict[str, QWidget]:
    """Every widget a `RunView` holds as an attribute, by name, and each widget of a tuple.

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
    """One widget attribute as a reader sees it, with each widget under it that no attribute names.

    A combo box's popup is left out. It belongs to the toolkit, and it shows
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
    """A halt shows the run on every widget a frame would, by default rather than by a list.

    The run is drawn. Then, with every frame failing, it is changed in every
    way that a run-state widget shows, so the halt is the only writer of what
    the screen says. The changes are a new agent, which is a new case with no
    control changes, the delivered dial renamed, and the run failed by the
    frame. That screen is compared, widget attribute by widget attribute, with
    the same run once a frame draws it. It is one state, written once by
    `present_halt` and once by `refresh`. Before `_write_statement`, the halt
    wrote four widgets and a dial row. The agent identity and the
    control-change panel went on showing the run that the last frame drew
    (`PL-1YDD`, `PL-DTJQ`, `PL-X7D5`).

    Every widget attribute is compared unless `FRAME_WIDGETS` names it. So a
    widget added to `RunView` later is checked here without being listed.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert _concentration(view).off_scale.lines[0].isHidden() is False, (
        "no trace is above the axis to go stale"
    )
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    # The playback line is in `_readout_row`, which `FRAME_WIDGETS` exempts,
    # so it is compared on its own below (`PL-P58M`).
    run._playback_rate_dropdown.setCurrentIndex(run._playback_rate_dropdown.findData(5))
    halted_playback_line = run._playback_rate_text.text()
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
    assert halted_playback_line == run._playback_rate_text.text() == format_playback_rate(5)


#: The groups of run-screen widgets that state one value together with the
#: labels, divisors and verdicts that qualify it. Each group lists its members
#: by the names `_widget_attributes` gives them. The test below requires every
#: member of a group to describe one step of the run: the step that each
#: scenario names for that group (`PL-J5GC`).
#:
#: In the readouts group, `_readout_row` stands for its six compartment cards,
#: each with its percent and its ×MAC line. The heading names the substance of
#: those cards, and the 1 MAC line states the divisor of their ×MAC lines. The
#: clock card is not a member. `ReadoutRow.set_readouts` writes it in the same
#: call as the cards, and on a halt the banner says which frame it shows.
VALUE_GROUPS: dict[str, tuple[str, ...]] = {
    "readouts": ("_readout_row", "_compartment_substance_text", "_one_mac_text"),
    "settings": (
        "_setting_controls[0]._fresh_gas_flow_slider",
        "_setting_controls[0]._delivered_concentration_slider",
        "_setting_controls[0]._alveolar_ventilation_slider",
        "_setting_controls[0]._cardiac_output_slider",
        "_delivered_text",
    ),
    "accounting": (
        "_accounting_panels[0]._agent_accounting_status_text",
        "_accounting_panels[0]._agent_accounting_detail_text",
        "_accounting_panels[0]._agent_amounts_text",
    ),
}

_NAMES_THE_AGENT = (
    "names the run's agent. `_write_statement` writes it from the same record as "
    "`_compartment_substance_text`, and the test above holds it to that record"
)
_HOLDS_OTHER_WIDGETS = "holds other widgets, and each of them is listed under its own name"
_STATES_THE_RECORD = (
    "states the run's record or status, which the test above holds to the record on both paths"
)

#: Every other widget attribute of a `RunView`, each with the reason it is in no
#: group. The two tables together are checked against `_widget_attributes` in
#: both directions, as `FRAME_WIDGETS` is. So a widget added to `RunView` later
#: fails the test below until it is put in a group or listed here.
UNGROUPED_WIDGETS: dict[str, str] = {
    "_run_name_text": "names the run while a second run is drawn, from `set_run_name`",
    "_status_text": _STATES_THE_RECORD,
    "_notice_text": (
        "the banner, which says which step the values on screen describe. `notice` and "
        "`halt_notice` word it, and their own tests check the wording"
    ),
    "_subtitle_text": _NAMES_THE_AGENT,
    "_agent_header_badge": _NAMES_THE_AGENT,
    "_agent_dropdown": _NAMES_THE_AGENT,
    "_running_agent_text": _NAMES_THE_AGENT,
    "_running_agent_display": _HOLDS_OTHER_WIDGETS,
    "_running_agent_lock_text": "says why the agent cannot be changed, and states no value",
    "_start_button": _STATES_THE_RECORD,
    "_pause_button": _STATES_THE_RECORD,
    "_reset_button": _STATES_THE_RECORD,
    "_playback_rate_dropdown": "the playback rate, a setting of the view, not of the run",
    "_interpretation_text": "a standing disclaimer, the same on every run",
    "_setting_controls[0]": _HOLDS_OTHER_WIDGETS,
    "_accounting_panels[0]": _HOLDS_OTHER_WIDGETS,
    "_accounting_panels[0]._accounting_heading_text": (
        "the panel's heading, which names the run while a second run is drawn"
    ),
    "_control_timeline_heading_text": "a standing heading",
    "_control_timeline_text": _STATES_THE_RECORD,
    "_control_timeline_overflow_text": _STATES_THE_RECORD,
    "_transport_row": _HOLDS_OTHER_WIDGETS,
    "_readout_section": _HOLDS_OTHER_WIDGETS,
    "_control_record_panel": _HOLDS_OTHER_WIDGETS,
}

#: What a reader sees of each group in `VALUE_GROUPS`, member by member, or
#: `None` for a group that a scenario does not check.
_GroupReadings = dict[str, dict[str, object] | None]


def _shown_readouts(run: RunView) -> dict[str, object]:
    shown: dict[str, object] = {
        "heading": run._compartment_substance_text.text(),
        "1 MAC": run._one_mac_text.text(),
    }

    for index, panel in enumerate(run._readout_row.panels):
        if index != _CLOCK_INDEX:
            shown[f"card {index}"] = (panel.value_label.text(), panel.secondary_label.text())

    return shown


def _shown_settings(run: RunView) -> dict[str, object]:
    shown: dict[str, object] = {
        f"dial {index}": (
            slider.name_label.text(),
            slider.qualifier_label.text(),
            slider.slider.minimum(),
            slider.slider.maximum(),
            slider.slider.value(),
            slider.value_label.text(),
            slider.secondary_label.text(),
        )
        for index, slider in enumerate(run._setting_controls[0].sliders)
    }
    shown["delivered line"] = run._delivered_text.text()

    return shown


def _shown_accounting(run: RunView) -> dict[str, object]:
    panel = run._accounting_panels[0]

    return {
        "verdict": panel._agent_accounting_status_text.text(),
        "detail": panel._agent_accounting_detail_text.text(),
        "amounts": panel._agent_amounts_text.text(),
    }


_SHOWN_GROUPS: Final[Mapping[str, Callable[[RunView], dict[str, object]]]] = {
    "readouts": _shown_readouts,
    "settings": _shown_settings,
    "accounting": _shown_accounting,
}


def _readouts_of(step: RunSettings, *, cards_withheld: bool = False) -> dict[str, object]:
    """The readouts group as one step states it, built by the functions the view calls.

    Args:
        step: The step whose agent the heading and the 1 MAC line name. Unless
            the cards are withheld, it is a snapshot, and the cards show its values.
        cards_withheld: True where the scenario requires every card to withhold its
            values, because no frame has been drawn for `step`'s agent.
    """

    expected: dict[str, object] = {
        "heading": substance_heading(step),
        "1 MAC": format_mac_reference(step.agent_display_name, step.agent_mac_percent),
    }

    if cards_withheld:
        cards = [(WITHHELD_CONCENTRATION_TEXT, WITHHELD_MAC_MULTIPLE_TEXT)] * len(READOUT_PANELS)
    else:
        assert isinstance(step, SimulationSnapshot)
        cards = [
            (readout.value, readout.secondary) for readout in readouts(step, DEFAULT_PLAYBACK_RATE)
        ]

    for index, card in enumerate(cards):
        if index != _CLOCK_INDEX:
            expected[f"card {index}"] = card

    return expected


def _settings_of(step: RunSettings) -> dict[str, object]:
    """The settings group as one step states it, built by the functions the view calls."""

    settings = setting_readouts(step)
    expected: dict[str, object] = {
        f"dial {index}": (
            setting.name,
            setting.qualifier,
            slider_position(setting.minimum, setting.decimals),
            slider_position(setting.maximum, setting.decimals),
            slider_position(setting.value, setting.decimals),
            setting.value_text,
            setting.secondary,
        )
        for index, setting in enumerate(settings)
    }
    (delivered,) = (setting for setting in settings if setting.control is ControlInput.DELIVERED)
    expected["delivered line"] = delivered_line(delivered)

    return expected


def _accounting_of(step: SimulationSnapshot) -> dict[str, object]:
    """The accounting group as one completed step states it."""

    shown = accounting(step)

    return {"verdict": shown.status.text, "detail": shown.detail, "amounts": shown.amounts}


def _rejected_accounting_of(step: SimulationSnapshot) -> dict[str, object]:
    """The accounting group for a step whose accounting check failed and was rolled back.

    Args:
        step: The rejected step, taken by a run whose check passes it. Its totals are
            the totals the rejected step's check judged.
    """

    return {
        "verdict": ACCOUNTING_FAILED_TEXT,
        "detail": ACCOUNTING_REJECTED_DETAIL_TEXT,
        "amounts": accounting(step).amounts,
    }


def _fresh_run(
    seconds: float, agent_id: str = "sevoflurane", **settings: Any
) -> SimulationController:
    """A run built directly with `settings` and stepped for `seconds`, then paused.

    Each scenario below takes the step it expects from such a run, built without the
    control or the failure that the scenario exercises (`.claude/rules/test-oracles.md`
    rule 2).
    """

    controller = SimulationController(agent_id, **settings)
    controller.start()
    _advance(controller, seconds)
    controller.pause()

    return controller


def _reject_the_next_accounting_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make the next step's accounting check fail on that step's own totals, once.

    For one call, `require_valid_agent_accounting` runs the real check with its
    verdict turned to failed. So the step raises the real
    `AgentSimulationValidationError`, built by the real code from the totals of the
    step that the core then rolls back. No supported setting makes the accounting
    fail, which is why the failure is injected.
    """

    real_require = AgentSimulationValidator.require_valid_agent_accounting
    real_check = AgentSimulationValidator.check_agent_accounting
    armed = [True]

    def failed_check(
        validator: AgentSimulationValidator, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        return replace(real_check(validator, currently_stored_agent_l), passes_validation=False)

    def require_once(
        validator: AgentSimulationValidator, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        if not armed:
            return real_require(validator, currently_stored_agent_l)

        armed.clear()

        with pytest.MonkeyPatch.context() as once:
            once.setattr(AgentSimulationValidator, "check_agent_accounting", failed_check)
            return real_require(validator, currently_stored_agent_l)

    monkeypatch.setattr(AgentSimulationValidator, "require_valid_agent_accounting", require_once)


def _no_setting(settings: object) -> NoReturn:
    """Stand in for `setting_readouts` in a test where no dial can be written."""

    raise ValueError("this control can offer no setting")


def _a_drawn_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run that a frame drew. Every group describes the step that the frame drew."""

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    run = _shown_view(application, controller).runs[0]
    step = _fresh_run(600.0, delivered_concentration_percent=Percent(8.0)).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _accounting_of(step),
    }


def _a_halt_after_an_agent_change(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run whose agent changed when no frame could be drawn (`PL-6RJ0`).

    The heading, the 1 MAC line and the dials describe the new case, and the cards
    withhold the old agent's values. The accounting panel still describes the last
    frame drawn. Nothing in it names an agent, and the banner says that the values
    on screen are the last frame drawn.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").record()
    drawn = _fresh_run(600.0, delivered_concentration_percent=Percent(8.0)).snapshot()

    return run, {
        "readouts": _readouts_of(new_case, cards_withheld=True),
        "settings": _settings_of(new_case),
        "accounting": _accounting_of(drawn),
    }


def _a_dial_write_refused_after_the_cards(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A frame that wrote the cards for a new agent, then could not write the dials.

    `refresh` writes the cards before `_write_statement`, and `setting_readouts`
    raises last, from `_write_settings`. Before `PL-6RJ0`, the 1 MAC line was
    written there too, so it went on naming the old agent above the new agent's
    cards. The settings group is not checked here. `setting_readouts` refuses every
    state in this scenario, so no dial can be written from any state, and the banner
    names the refusal.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(run_view_module, "setting_readouts", _no_setting)

    _select_agent(run, "desflurane")

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").snapshot()

    return run, {
        "readouts": _readouts_of(new_case),
        "settings": None,
        "accounting": _accounting_of(new_case),
    }


def _an_accounting_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run halted because a step's accounting check failed (`PL-HF4B`).

    The core rolls the step back. So the readouts and the dials describe the last
    completed step, and the accounting panel describes the rejected step: its
    verdict and the totals that the verdict judged.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    completed = _fresh_run(300.0)
    rejected = _fresh_run(300.0)
    rejected.start()
    rejected.advance(SIMULATION_STEP_S)
    _reject_the_next_accounting_check(monkeypatch)

    _steps(run, 1)

    assert controller.has_failed is True
    step = completed.snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _rejected_accounting_of(rejected.snapshot()),
    }


_ONE_STATE_SCENARIOS: Final[
    Mapping[str, Callable[[QApplication, pytest.MonkeyPatch], tuple[RunView, _GroupReadings]]]
] = {
    "drawn frame": _a_drawn_frame,
    "halt after an agent change": _a_halt_after_an_agent_change,
    "dial write refused after the cards": _a_dial_write_refused_after_the_cards,
    "accounting halt": _an_accounting_halt,
}


@pytest.mark.parametrize("scenario", list(_ONE_STATE_SCENARIOS))
def test_every_value_and_its_qualifiers_on_screen_come_from_one_state(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    """Each value on the run screen and what qualifies it describe one step of the run.

    Every widget has one writer since `PL-X7D5` and `PL-WM5P`, and the test above
    compares each widget on a halted screen with itself on a drawn one. Two widgets
    that disagree on one screen pass that test. A ×MAC number divided by another
    agent's 1 MAC (`PL-6RJ0`), a dial showing a setting no step ran under
    (`PL-3B34`) and a "Valid" verdict beside a banner that reports a failed check
    (`PL-HF4B`) each did.

    So each scenario names, for each group in `VALUE_GROUPS`, the step that all of
    the group's members must describe. It takes that step from a run built without
    the control or failure under test, and builds each member's text from it with
    the function the view calls. Those functions are not under test here. The step
    each group is written from is (`PL-J5GC`).
    """

    run, expected = _ONE_STATE_SCENARIOS[scenario](application, monkeypatch)
    attributes = _widget_attributes(run)
    grouped = [member for members in VALUE_GROUPS.values() for member in members]

    assert sorted(set(grouped) & set(UNGROUPED_WIDGETS)) == [], (
        "these widgets are in a group and also listed as in none - keep one"
    )
    assert sorted(set(attributes) - set(grouped) - set(UNGROUPED_WIDGETS)) == [], (
        "these widgets are in no group and not listed in UNGROUPED_WIDGETS: put each in "
        "the group whose value it states or qualifies, or list it with the reason it is "
        "in none"
    )
    assert sorted((set(grouped) | set(UNGROUPED_WIDGETS)) - set(attributes)) == [], (
        "these entries name a widget RunView no longer holds - remove them"
    )
    assert sorted(expected) == sorted(VALUE_GROUPS)

    checked = [group for group, readings in expected.items() if readings is not None]
    shown = {group: _SHOWN_GROUPS[group](run) for group in checked}

    assert shown == {group: expected[group] for group in checked}


def test_a_halted_run_shows_the_new_playback_rate(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-P58M`: a halted run shows one playback rate, the one the reader just chose.

    The clock's second line sits in the readout row. A halt does not write
    that row, because its readouts are compartment values that only a frame
    can state. Until `PL-P58M`, a rate chosen on a halted run reached the
    dropdown but not the clock, so the screen showed 5x in one place and 1x
    in the other.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)

    assert controller.has_failed is True
    assert run._playback_rate_text.text() == format_playback_rate(1)

    dropdown = run._playback_rate_dropdown
    dropdown.setCurrentIndex(dropdown.findData(5))

    assert dropdown.currentText() == format_playback_rate(5)
    assert run._playback_rate_text.text() == format_playback_rate(5)


def test_a_confirmation_answered_after_the_snapshot_refuses_restates_the_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A confirmation answered after the snapshot rejects a value shows the halt, not a refusal.

    The question is asked from a snapshot read when the selector was used.
    By the time the reader answers, the run's snapshot may reject a value.
    `set_agent` carries the settings over from the snapshot. So without the
    gate, the exception from `set_agent` reached `_apply_setting` as a refused
    setting. It was recorded in `_rejected_setting_notice`, even though the run
    had halted for the same reason (`PL-V2HC`, found at review).
    `_start_new_case` now reads the snapshot first, outside `_apply_setting`,
    and the dialog's gated slot halts the run for the exception (`PL-HJKN`).
    The test checks that the halt is shown, nothing is recorded as refused, the
    dialog is gone and the run keeps its agent.
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
    leave the flows that way (`_with_stale_tissue_flows`). Before `PL-M4M0`,
    the refusal escaped the Reset slot after `pause()` had run and the state
    had been cleared. So the run was left half reset. The compartments and
    the clock were at zero, the old definition and timeline were kept, no
    failure was recorded, and `case_restarted` was never emitted. Meanwhile
    the screen showed "Running" and offered Pause. The core now refuses
    before it clears anything, and the view halts the run on the refusal.
    The refusal is recorded as the failure and shown by the status word, the
    transport and the banner. The banner's way out says that no setting can
    repair the refusal, instead of naming the Reset that was just refused
    (`PL-01GY`). Nothing changed, so the frame that follows draws the run
    where it was.
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

    The first press records the refusal as the failure. So on the second
    press the run already has a recorded reason, but that reason is this same
    refusal. The exit text that repeats the refusal is meant for a run that
    failed for some other reason. Stated twice, the one refusal looked like
    two faults (`PL-M4M0`).
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
    correct. The values on screen are the last completed step before that
    first failure stopped the run. So the refusal is stated where it can be,
    in the way out, which says that Reset was refused and why (`PL-M4M0`).
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
    once. So the reader is sent to a Reset that will succeed, not to a
    setting already changed. A setting that the stale record refuses leaves
    the exit on the banner (`PL-M4M0`). Until `PL-HQF5`, the cardiac output
    change itself repaired the stale flows. No setting repairs a fraction
    written past its guard, so the test puts the fractions back first.
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
    and shows that the record is still refused. The exit is still on the
    banner, and the next Reset is refused again. The expected sentence is
    written here as a literal rather than read from the constant.
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
    """A setting the run never recorded halts the run before chart and readouts differ (`PL-XRN8`).

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
    them before the branch is put back there (`PL-M4M0`). The comparison stays
    open, and the trunk is untouched. The way out is the one every run has,
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
    comparison open. So a banner that named a new case pointed at a control
    the screen had hidden. The only control left enabled was the trunk's
    Reset, the one just refused (`PL-M4M0`). The exit names closing and
    reopening the application instead (`PL-01GY`). Once the record builds
    again, the trunk's Reset succeeds and ends the comparison, as the fork
    panel says it does.
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

    This is the one way to get a drawn fraction outside 0 to 1, because no
    supported setting computes one (`core/concentration.py`). A drawn window
    is an evaluation of the closed form. So the value is written into the
    window that the controller returns, not into any compartment.
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

    Values used to be built as the toolkit converted them, trace by trace.
    Then a column refused in the muscle trace left the circuit, alveolar,
    mixed venous and vessel-rich traces redrawn from the failed frame. The
    muscle and fat traces were left on the frame before it. So six traces
    showed two instants, under a banner that blamed a step that never failed
    (`PL-7DJK`). Now `assemble_chart_frame` refuses before a frame exists.
    The run halts, the halt names the compartment, and no trace moves. The
    value used here is the one that reproduced the defect.
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
    so the halt it causes can never be drawn as a frame. Each run still says
    that it stopped, and why, from its own snapshot.
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

    A frame is assembled for the width it is drawn on, so the frame on screen
    is right for that width only. On a paused run with no frame owed, nothing
    would redraw after a resize. The columns drawn for the narrow plot would
    then stay on the wide plot, at twice the chord.
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
    """A view control stays enabled while the run's own controls are locked."""

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
    built, before any layout places them. So each is built with the view as
    its parent. A parentless one shown at that point opened a window of its
    own beside the dashboard (`PL-25KS`).
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
    # The selector shows the agent that is actually running, not the one
    # being offered, for as long as the question is open.
    assert run._agent_dropdown.currentData() == before.agent_id


def test_an_open_new_case_question_follows_a_running_run(application: QApplication) -> None:
    """`PL-WM5P`: the question states what the new case discards as the run stands now.

    The run is not paused while the question is open, so a running run goes
    on stepping. Before the fix, the question was written only once, when it
    opened, so its figure for the run time about to be discarded fell behind
    the clock.
    """

    controller = _paused_run_with_history(60.0)
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    opened_warning = dialog.body_labels[1].text()

    _advance_to(controller, 120.0)
    view.present(False)
    snapshot = controller.snapshot()
    question = new_case_question(snapshot, "Desflurane", len(run.adjustments(snapshot)))

    assert dialog.body_labels[1].text() == question.body[1] != opened_warning
    assert format_elapsed(snapshot.elapsed_s) in dialog.body_labels[1].text()
    assert [label.text() for label in dialog.body_labels] == list(question.body)


def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched(
    application: QApplication,
) -> None:
    """Declining costs nothing: the run, its history and the selector stay as they were."""

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
        "circuit_volume_l": CompartmentVolume(4.5),
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

    That report reaches the branch that handles a decline. Without the guard
    in `_resolve_new_case`, that branch would undo the case that had just
    started.
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

    The dialog is deleted once its `finished` signal has been read. Otherwise
    every confirmation ever asked would stay a child of the run, with its
    title in `interface_strings` and its widgets in every walk of the tree
    (`PL-25KS`).
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

    A second selection while the question is open is reverted and gets no
    dialog. Before the guard, it opened a second dialog and changed the
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

    The line appears once, beside the values it qualifies, rather than at the
    foot of the page, where a repeated disclaimer stops being read.
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

    The test goes through the dashboard rather than the bare chart, so the
    readout comes from the shipped composition. It checks against the frame
    the dashboard drew, so the readout is the state at which the run was
    evaluated, not a position between two states. A drawn instant belongs to
    a grid column rather than to a step. So the time the readout states is
    the instant rounded to the hover's own resolution, not the column's raw
    time.
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
    """A plot missing all six is a blank panel, and a blank panel looks like a failure."""

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

    # `present` turns an exception into a halt rather than letting it escape.
    # So the count is what tells a drawn frame apart from a refused one.
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

    The test checks this on one run, and then on two runs. With two runs the
    click goes over the cap, and the selection, not the legend, decides
    which compartment makes room.
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

    A click used to set the selection, hand it to the legend and then ask for
    a frame. So when that frame failed to assemble, the boxes showed the new
    selection over a plot still drawing the old one: fat was unchecked beside
    a fat trace (`PL-G3K7`). The legend is now given the selection that a
    frame was assembled from, once both plots have drawn that frame. A box
    whose request nobody acts on goes back to the selection the legend last
    showed.
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
    line = _concentration(view).off_scale.lines[0]

    assert line.isHidden() is False
    assert "Circuit" in line.text()
    assert "Alveolar" not in line.text()
    assert "readouts above" in line.text()

    _set_trace_shown(application, view, RecordedQuantity.CIRCUIT, False)

    assert line.isHidden() is True


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
    assert _chosen_time_base(view) is None
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
        assert _chosen_time_base(view) == time_base_for_span(time_base.span_s)


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


def test_the_two_plots_share_one_frame_while_they_show_the_same_window(
    application: QApplication,
) -> None:
    """Each plot owns its window (`PL-L59K`), and plots at one window draw one frame (`PL-9LNF`)."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    wash_in = _wash_in(view)

    for key in (FIT_RUN_KEY, "900.0", "43200.0"):
        _select_time_base(view, key)
        wash_in.time_base_selector.setCurrentIndex(wash_in.time_base_selector.findData(key))

        assert wash_in.chart.frame is _concentration(view).chart.frame

    _select_time_base(view, "900.0")
    frame = wash_in.chart.frame

    assert frame is not None
    assert frame is not _concentration(view).chart.frame
    assert frame.time_base == time_base_for_span(43200.0)
    assert format_time_base(43200.0) in wash_in.time_axis_caption.text()


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


def test_a_window_pick_whose_frame_fails_leaves_the_control_on_the_window_drawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control names the window on the plot, not one that never drew (`PL-G3K7`, `PL-L59K`)."""

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_time_base(view, "900.0")

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.fitted is True
    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY


def test_a_frame_is_assembled_and_checked_with_no_chart_shown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Assembling a frame checks the runs, so a frame is assembled whatever the Areas hold.

    This is `PL-L59K`. With every chart replaced, no View asks for a window. A
    frame is still assembled at "Fit run". So a run state that the assembly
    rejects still halts every run, rather than going unnoticed until a chart
    is shown again.
    """

    view = _shown_view(application, _paused_run_with_history(60.0))

    for area in (AreaId(1), AreaId(3)):
        view.layout_container.choose_view(area, PARAMETER_CONTROLS)

    _settle(application)
    assert view.layout_container.frame_requests() == {}
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert all(run.controller.has_failed for run in view.runs)


def test_a_chart_s_window_returns_with_the_chart_after_its_area_shows_another_view(
    application: QApplication,
) -> None:
    """A chart's window is the View's own state, saved when the reader replaces it (`PL-L59K`).

    The time-base control sits in the chart View. So a reader closes the
    control only by choosing another View for the chart's Area. Meanwhile the
    F_A/F_I plot keeps its own window. A concentration chart brought back to
    that Area shows the window that the reader chose.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    _select_time_base(view, "1800.0")

    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)
    view.present(False)

    frame = _wash_in(view).chart.frame
    assert frame is not None
    assert frame.fitted is True

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"
    assert format_time_base(1800.0) in _concentration(view).time_axis_caption.text()


def test_reset_leaves_the_selected_time_base_alone(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    _select_time_base(view, "1800.0")
    view.runs[0]._reset_button.click()

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"


def test_the_mac_axis_and_references_follow_the_agent(application: QApplication) -> None:
    """The divisor line, the 1 MAC line and the right axis are the running agent's."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart = _concentration(view).chart

    assert _concentration(view).mac_reference_text.text() == format_mac_reference(
        "Sevoflurane", MacPercent(2.0)
    )
    assert chart.one_mac_line() == 2.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(6.0)

    _select_agent(view.runs[0], "desflurane")
    # Read from desflurane's own file, not from the switched run's snapshot,
    # which would agree with a band the switch failed to rebuild (`PL-JPS2`).
    mac_awake = load_agent_parameters("desflurane").mac_awake

    assert _concentration(view).mac_reference_text.text() == format_mac_reference(
        "Desflurane", MacPercent(6.0)
    )
    assert _concentration(view).mac_awake_reference_text.text() == format_mac_awake_reference(
        "Desflurane",
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=MacPercent(6.0),
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
    """`PL-DR1Z`: the mark is drawn at the change's instant on both plots."""

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
    assert format_wash_in_ratio(last_ratio) in _wash_in(view).states.lines[0].text()


# ------------------------------------------- the whole interface, walked


def test_the_page_leaves_the_application_name_to_the_window_title(
    application: QApplication,
) -> None:
    """The page no longer restates the name the window's title bar carries (`PL-J8K2` Q2).

    `PL-HK75` put the name on screen from `app_metadata`. The name is now in
    the title bar, and `test_bootstrap` checks that the window title shows
    it. The in-page title row cost 44 px that the chart cannot spare on a
    laptop (`PL-84QX`).
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

    The two state advisories are exempt, and the walk skips them by identity.
    They are empty here and show text only when they apply. That is the
    distinction this test draws: a message at the moment of need is not a
    standing paragraph.
    """

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None,
        _concentration(view).chart,
        skip=(
            _concentration(view).hidden_traces_text,
            *_concentration(view).off_scale.lines,
            *_concentration(view).unmarked_changes.lines,
        ),
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
        None,
        _wash_in(view).chart,
        skip=(*_wash_in(view).states.lines, *_wash_in(view).unmarked_changes.lines),
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

    A readout of the form "time to wake-up: 14 min" looks like a per-patient
    prediction that this model does not support, and no surrounding
    disclaimer undoes that.
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
#: declares no foreground, mapped to the reason it is allowed not to.
#: `tools/contrast_check.py` reads this mapping and counts its entries in its
#: report line. That tool measures declared pairs, so a control that declares
#: nothing is absent from its numerator *and* its denominator, and looks
#: covered there. What nothing measures has to be stated somewhere, and this
#: is the place.
#:
#: A name here is a claim about a kind, not an excuse for one. The test below
#: fails on an entry that names a kind the dashboard no longer builds, and on
#: an entry whose kind has since been given a foreground. So an entry cannot
#: outlive the reason beside it.
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
    "_CornerZone": (
        "an Area's corner, where a drag splits or joins it. It draws no text: "
        "nothing at rest, and while the pointer is in its Area a grip of three "
        "strokes in MUTED, which `tools/contrast_check.py` measures against "
        "PANEL (PL-30L5)."
    ),
    "_LayoutOverlay": (
        "what a corner drag shows before release, drawn over the Areas. It "
        "draws no text: a split line or a joined Area's outline in PRIMARY or "
        "WARNING, and a MUTED tint, each measured against PANEL by "
        "`tools/contrast_check.py` (PL-30L5)."
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

#: A foreground colour that nothing in this interface declares, installed on
#: the application palette before the dashboard is built. A control that
#: declares no colour of its own resolves to this one. That makes
#: "undeclared" a value to read rather than an absence to infer. It also
#: stops a host whose own default happened to match a theme colour from
#: making the walk prove nothing.
_ALIEN_FOREGROUND = "#FF00FF"

#: The palette roles in which a control on this dashboard draws its content.
#: All of them are changed together, because `QWidget.foregroundRole` differs
#: by control: WindowText for a label, ButtonText for a button and Text for a
#: list. A role left at the platform's value would be treated as declared.
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

#: The Qt classes that paint a string of their own. Each must declare a
#: foreground, whatever it is painting today. A label built empty and filled
#: on the first frame draws text just as one built with its string does, and a
#: check that read `text()` would pass the label while it was empty.
_TEXT_CONTROLS = (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
)

#: The frame shapes whose lines Qt draws in the foreground role. A `NoFrame`
#: frame draws no line at all, and the style draws a `StyledPanel` from its
#: bevel roles. So neither shape says anything about a foreground. That is
#: what keeps every panel and column container out of the walk without
#: naming one.
_PLAIN_LINE_SHAPES = (
    QFrame.Shape.Box,
    QFrame.Shape.Panel,
    QFrame.Shape.WinPanel,
    QFrame.Shape.HLine,
    QFrame.Shape.VLine,
)


def _declared_colours() -> frozenset[str]:
    """Every colour `app/theme.py` declares, including both agent pairs.

    The colours are read from the module rather than listed here.
    `contrast_check`'s `check_colors_live_in_the_theme` requires every colour
    to be declared there, so the module holds the complete set by
    construction.
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

    The function asks three questions in order, because asking them in
    another order gives wrong results. A text control is included whatever it
    inherits from. `QLabel` is a `QFrame`, so asking the frame question first
    would drop every label on the dashboard. A frame that is not a plain line
    is a container or is drawn by the style. So it is excluded unless its
    class paints below `QFrame`. That rule keeps `MetricPanel`, `QSplitter`
    and the panels out of the walk. It still keeps `PlotWidget`, which is a
    `QGraphicsView` and paints its own scene. Every other widget is included
    exactly when its class overrides `paintEvent`. That is the decidable form
    of "draws something nobody else declares".
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

    The palette is set on the application rather than on a widget. That is
    the same reason `tests/integration/test_dark_appearance.py` sets a host
    appearance there: a palette assigned to the widget under test would
    overwrite the declaration being tested instead of exercising it. The
    dashboard is built inside the fixture's scope, so that every stylesheet
    resolves against this palette. The views are deleted before the original
    palette is restored, because the modules in this tree share one
    `QApplication`.
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

    `tools/contrast_check.py` measures the pairs that somebody wrote down. A
    control that writes none adds to neither side of its count. So its report
    line is the same whether the interface is covered or has three invisible
    controls on it. That was the state in which the project owner found
    `PL-DHBX`, on his own screen. That tool cannot answer the question this
    test asks, and the question needs a built tree rather than an `ast` walk.
    Qt, not the source, decides which widget a stylesheet actually applies to.

    So every foreground role is set to a colour this interface never uses,
    the dashboard is built under it, and each content-painting widget is asked
    what colour it resolves to. A declared control returns its own colour.
    Qt folds a stylesheet's `color` into the widget's palette when it polishes
    the widget. Qt also passes the colour down from an ancestor's stylesheet,
    exactly as it would on screen. That is why no rule here has to parse CSS
    or decide which selector applied to which widget.
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

    This test keeps the list from becoming a comment that nobody checks, in the
    same way that `tools/contrast_check.py` checks `KNOWN_SHORTFALLS`. An entry for a
    kind the dashboard stopped building fails here. So does an entry for a
    kind that has since been given a foreground. Neither stays on as an
    exemption that nothing needs. Both directions matter to the count that
    the report line prints, because the count is the size of this mapping. An
    entry that has stopped being true overstates what nothing measures, just
    as a missing entry understates it.
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

    The readout row reports a one-column minimum and the legend rows wrap.
    So the page's minimum width is well inside the window, and the scroll
    area never widens it. The chart column alone asks for less than a
    thousand pixels.

    The record panels measured are the ones the page holds, as the test below
    proves. They used to come from a second build of the panels, and those
    panels had no parent. `mapTo(page, ...)` assumes that the page is an
    ancestor and checks nothing. So the last two assertions compared
    coordinates that were never on the page, and they could not fail
    (`PL-JS0X`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    scroll, middle = _middle_of(view)
    page = _page_of(view)

    assert middle.minimumSizeHint().width() <= scroll.viewport().width()
    assert middle.width() == scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert page.width() <= view.width()
    assert _concentration(view).minimumSizeHint().width() < 1000

    for slider in view.runs[0]._setting_controls[0].sliders:
        right_edge = slider.mapTo(page, slider.rect().bottomRight()).x()

        assert right_edge <= page.width(), "a setting control is laid beyond the page"

    for panel in _record_panels(view.runs[0]):
        assert page.isAncestorOf(panel), "a record panel measured is not on the page"
        assert panel.mapTo(page, panel.rect().bottomRight()).x() <= page.width()


def test_the_sidebar_panels_measured_are_the_ones_the_page_holds(application: QApplication) -> None:
    """Each panel the width test measures is the page's only panel of its kind, and is shown.

    Each panel is matched against the page's own children by the object name
    that scopes the panel's stylesheet. So a rebuilt panel fails here. So does
    a widget that might come to sit between the heading and the panel. The
    second build of the panels, which this check replaced, also moved the
    run's live labels out of the column that the earlier assertions had
    measured (`PL-JS0X`, `PL-N67T`).
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

    The method that built both panels used to build two new panels on every
    call and lay the run's own labels into them. A layout takes a widget from
    wherever it sits. So a second call moved the accounting status, its
    amounts and the control changes into panels with no parent, and they
    vanished from the sidebar a learner was reading (`PL-N67T`). Each label
    must be on screen and in its shared column before the call as well as
    after it, so the test cannot pass on a column that never showed them. The
    overflow line is hidden while nothing overflows, so the test checks only
    that it is in its column. Since `PL-NWTM`, the accounting panel is in the
    sidebar and the control-change panel is in the unconditional region's
    record column. Since `PL-9LNF`, the accounting panel may sit in an Area.
    So a second call builds a second copy for another Area and leaves the
    first where it is. The control-change panel stays in the region, so the
    placed one is returned.
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

    Each of the three methods used to lay the run's live widgets into a new
    container on every call. So a second call took the Start button, the
    substance heading and the fresh gas flow slider off screen, and dropping
    its result deleted them (`PL-KZR1`). The check works like the sidebar's
    test above (`PL-N67T`). Every widget must be on the page before the call
    as well as after it, and each shown widget must stay shown, so the test
    cannot pass on a row that never showed them. Each case names a widget
    that has to be shown to begin with. The lone run's name and the agent
    chip are hidden in this state, so the test checks only that they are on
    the page. The setting controls are not among the cases, because since
    `PL-9LNF` a second call builds a second copy for another Area
    (`tests/integration/test_run_surfaces.py`).
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
    """The unconditional region keeps its own height, and the Areas take the rest.

    At the fixed test size, the page is taller than the window, so there is no
    spare height. From the first frame on, the Areas then have the height they
    ask for, which is their size hint. Before `PL-PHPZ`, the page laid out the
    Areas from a hint read before the Views had drawn. So the Areas' height
    depended on when the page was laid out.

    A window has spare height once it is tall enough for the scrolling middle to
    show all of its content. Every extra pixel of height makes the Areas taller,
    while the region that holds the readouts keeps its height. The test measures
    the readout section inside the region, where the section has been since
    `PL-NWTM`. The setting controls have been a View in an Area since `PL-2KXB`,
    so they take their share of the Areas' height.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart_row = view.layout_container
    readout_section = view.unconditional_region
    scroll, middle = _middle_of(view)

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() >= chart_row.minimumSizeHint().height()
    assert chart_row.height() == chart_row.sizeHint().height()

    settled_chart_row_height = chart_row.height()
    spare = 400
    hidden = max(0, middle.sizeHint().height() - scroll.viewport().height())
    view.resize(_WINDOW_WIDTH_PX, view.height() + hidden + spare)
    application.processEvents()

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert chart_row.height() >= settled_chart_row_height + spare - 2
    assert chart_row.height() > chart_row.sizeHint().height()

    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    application.processEvents()


def test_the_page_takes_the_height_the_areas_ask_for_after_the_views_draw(
    application: QApplication,
) -> None:
    """`PL-PHPZ`: the Areas are as tall as their size hint straight after the first frame.

    The setting controls sit in an Area above the charts. They build their
    per-run copies on their first frame, which changes the Areas' size hint.
    Before the fix, the page kept the hint that it read before that frame. So
    after the frame the Areas were 62 px shorter than their hint, and 45 px
    taller once the event loop had run. The expected height is the Areas' own
    size hint, not a height that the page worked out.
    """

    view = _shown_view(application, SimulationController())
    areas = view.layout_container

    assert areas.height() == areas.sizeHint().height()
    application.processEvents()
    assert areas.height() == areas.sizeHint().height()


# ------------------------------------------------------------- two runs


def test_two_run_views_drive_two_controllers(application: QApplication) -> None:
    """`PL-B9PY`: two runs, two controllers, and neither shows the other's numbers.

    A regression here would look like one branch's readouts shown over the
    other branch's numbers. That is the wrong-patient-context failure that
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
    reaches exactly twice every compartment at every instant. So a line that
    carries the wrong run's values is visible in the drawn points, rather
    than having to be inferred.
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
    # The check covers every compartment that the cap leaves drawn, because
    # "each run draws its own values" has to be true for each of them. The
    # cap itself has its own test, for `PL-8PSW`.
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
    # One of the two compartments that the cap leaves drawn. So the test
    # checks that the selection applies to both runs, not that the cap
    # removes a trace.
    quantity = RecordedQuantity.ALVEOLAR

    _set_trace_shown(application, view, quantity, False)

    assert chart.drawn_points(0, quantity) == ((), ())
    assert chart.drawn_points(1, quantity) == ((), ())

    _set_trace_shown(application, view, quantity, True)

    assert chart.drawn_points(0, quantity)[0]
    assert chart.drawn_points(1, quantity)[0]


def test_two_runs_cap_the_chart_at_two_compartments_and_say_so(application: QApplication) -> None:
    """`PL-8PSW`: the cap limits the selection, the boxes agree with it, and it is stated.

    The cap is what frees the line width to carry the run. So it is the half
    of the encoding that must stay true whatever a reader does. That includes
    checking a third compartment, which takes the oldest selection off rather
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
    # With two runs, the selection is reduced from six compartments to the top
    # two of the compartment table.
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
    """An exception from one run's step says nothing about the other run."""

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
    """The render loop draws every run, so an exception from it belongs to no single run."""

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

    The hedge and wake-time tests guarantee only what the walk reaches. The
    plots' axis titles and the legend boxes' accessible names are standing
    text that a reader or a screen reader meets, so both are on the walk
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
    words. This test checks that the dashboard places them where a reader
    meets them, at the foot of the page. So the string on which the project's
    regulatory posture rests cannot silently leave the screen.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT

    view = _shown_view(application, SimulationController())

    assert USE_DISCLAIMER_TEXT in view.visible_strings()


@pytest.mark.parametrize("height_px", [700, 900, 1100])
@pytest.mark.parametrize("workspace", ["Default", "Induction", "Maintenance"])
def test_the_region_and_the_use_disclaimer_stay_in_the_viewport(
    application: QApplication, workspace: str, height_px: int
) -> None:
    """The region and the use disclaimer stay in view, however the page scrolls (`PL-NNML`).

    The whole page used to scroll. Measured offscreen on 2026-10-20 at
    1366 px wide, it was 1087 px tall in the Default Workspace and 1505 px in
    Induction and Maintenance. So at these window heights the disclaimer at
    its foot was below the visible part, and scrolling down to it moved the
    region off the top. Now only the part between them scrolls. The test
    checks the window in three states: when it opens, when the scrolling part
    is scrolled to its end, and after a branch is taken, which scrolls to the
    chart. The disclaimer is found by its text, so the test also runs against
    the code before the fix.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT
    from anesthesia_sim.layout.shipped import shipped_workspaces

    case = _branched_case()
    _delete_shown_views(application)
    view = SimulationView((case.trunk,), case=case, workspaces=shipped_workspaces())
    _SHOWN_VIEWS.append(view)
    view.resize(_LAPTOP_WIDTH_PX, height_px)
    view.show()
    application.processEvents()
    view.present(False)
    view.tab_strip.activate(view.workspaces.position_of(WorkspaceName(workspace)))
    _settle(application)
    (disclaimer,) = (
        label for label in view.findChildren(QLabel) if label.text() == USE_DISCLAIMER_TEXT
    )

    def assert_in_view(step: str) -> None:
        window = view.rect()

        for name, widget in (("region", view.unconditional_region), ("disclaimer", disclaimer)):
            placed = QRect(widget.mapTo(view, QPoint(0, 0)), widget.size())
            assert widget.isVisible(), f"{step}: the {name} is hidden"
            assert window.contains(placed), (
                f"{step}: the {name} at {placed} is not inside the {window} window"
            )

    assert_in_view("on opening")

    bar = view._page_scroll.verticalScrollBar()
    bar.setValue(bar.maximum())
    application.processEvents()
    assert_in_view("scrolled to the end")

    _take_fork(view, 60.0)
    _settle(application)
    assert len(view.runs) == 2
    assert_in_view("after taking a branch")


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
    """Being in the tree and being visible to the reader are two different things (`PL-904Y`).

    The no-traces advisory stays hidden until every trace is off, and a combo
    shows only its current entry. Both strings are in the tree, so a test
    that a string is never said still reaches them. Neither is shown to the
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
# These tests cover the editing path end to end: a form filled in, a mark
# reaching both runs, and the listing a reader sees.
# `tests/unit/test_bookmarks.py` tests what a mark refuses, and
# `tests/unit/test_dashboard_frame.py` tests what a row says. These tests
# check that the dialog is wired to every run rather than to one (`PL-LPLD`).


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
    # No compartment exceeds the delivered concentration, and the vaporizer
    # limits that. So no run of this agent could cross a target above it. The
    # control refuses such a target rather than reporting it afterwards.
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
    # The marks belong to the case. Writing to every run makes it impossible
    # to compare two runs at two different heights because a learner typed
    # one of them twice.
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

    `bookmark_panel` reads the reference run's mark *set*, and every run's
    standings against that set. So a branch whose set had drifted from the
    trunk's no longer quietly draws the trunk's answer. Instead
    `BookmarkStandings` refuses the lookup, `present` catches the refusal, and
    the whole dashboard halts. That is the right direction under `CLAUDE.md`'s
    safety-critical standard, and it makes the invariant matter in a way it
    did not before.

    The three tests that check the invariant build two separate trunks. That
    is a configuration `main()` cannot produce, because it opens one trunk and
    a `BranchedCase`. This test walks through the real configuration: a fork,
    then an add and a removal from the dashboard. `_branch_from` copies the
    set at the fork, and `_apply_to_every_run` has to keep the two sets in
    step afterwards.
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
    # two runs have drifted apart. This checks that they have not, which is
    # the invariant that the write-to-every-run path exists for.
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
    # stays. A reused name would give two marks the same name, so the name is
    # cleared.
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
    # When the rows were joined into one label, the first row's continuation
    # began at the same margin as every row. So `Run 2 reached` looked like a
    # mark of its own, and attached one run's answer to the wrong mark.
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

    # Both dimensions are taken from the row, not from a sidebar width in
    # pixels. A fixed width was a bet on the font that the host resolves for
    # sans-serif (`PL-VCF0`). The width is half the row's own one-line advance,
    # so the row wraps under any font. The height is the listing's height at
    # that width, as the sidebar's layout gives it. A bare window opens at the
    # height its size hint works out for a width of its own choosing. Under
    # Inter at the sidebar's narrow end, 300 px, that was 66 px, against the
    # 81 px that the wrap needs.
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
    that instant, and its delivered concentration is raised to the agent's
    maximum. It is then stepped until the crossing halts it, at 114.7 s,
    which is where the offscreen reproduction on `PL-LHBY` put the halt.

    The time bookmark is added for the second half of the same defect. At
    30 s it is behind the trunk's clock and before the branch's own opening
    instant, so the two runs describe it in opposite words.
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

    The branch stops itself on a height the learner marked. When the row was
    drawn from the reference run, it said nothing at all, because the trunk
    was still running for that target. So the one on-screen sign that a run
    stopped where it was asked to existed for a lone run. It vanished as soon
    as a second run was drawn, and the halt then looked the same as a Pause.

    The test checks the run that halted *and* the run that did not. If only
    the branch were named, the trunk's silence could be read as the trunk
    having no answer, rather than as its answer being "not yet".
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

    The branch inherits an instant but opens after it. That instant used to
    show the trunk's `passed`. So the screen claimed something about the
    displayed branch that the model shows to be false from
    `ResumePoint.fork.instant_s` alone. `MarkStanding.BEFORE_THIS_BRANCH`
    exists so that this is not said, but no screen could show it. The
    reference run is the trunk, and no instant comes before a trunk.
    """

    view = _halted_branch_view(application)

    listed = view._bookmarks_panel.times.text()

    assert listed.endswith(
        f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )
    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in listed


def test_a_failed_run_s_marks_do_not_stand_as_reachable(application: QApplication) -> None:
    """`PL-N3N5`, read as the adversarial review of `PL-LHBY` found it.

    One of two displayed runs is failed the way a step that raised fails it.
    `RunView.halt` records the disposition, and the tick handler calls that
    method. The whole screen is then read at one instant. The trunk's own
    panel said `Stopped - simulation error`, while its clause on a mark it had
    not reached said `not yet`. That is `MarkStanding.STILL_RUNNING`, which
    claims the run can still reach the mark. But `SimulationController.start`
    refuses to resume that run without a reset.

    The failed run is the trunk rather than the branch, so that the test
    reproduces the *drawn* defect and not only the standing behind it. The
    branch has something to say about both new marks, so the rows are
    attributed, and the trunk's answer reaches the screen in words. Where the
    two runs agreed, the row was drawn as silence instead, which made the same
    false claim quietly.

    Both kinds of mark are checked, because a failure ends a clock and a
    height alike. The trunk's inherited `passed` is checked beside them. A
    failure stops a clock without taking it back, so the answers about what
    did happen still apply.
    """

    view = _halted_branch_view(application)
    trunk = view.runs[0]
    # The marks are added after the fork and through the editor, so both runs
    # hold them. The set belongs to the case, and `_apply_to_every_run` is
    # what writes a mark. The instant is ahead of the trunk's clock and behind
    # the branch's. Fat at 0.8 xMAC is out of reach of either run here. So
    # each mark is left outstanding on the trunk, while the branch has an
    # answer for it.
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
    # The other side of the same rule: a clause that names no run is a claim
    # about the case, and with one run that claim is true. A run name on every
    # row of a single-run panel would be the standing chrome that
    # `.claude/rules/ui-reader.md` rules out. The dashboard already refuses
    # such names for the legend and the run headings.
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
    # `PL-F9TQ` governs what may sit between a chart heading and its plot.
    # The marks belong to the case rather than to either plot, so they are a
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

    A dashboard given loose controllers cannot branch, and shows this by not
    offering the control. A dashboard opened over a case offers the control,
    at the trunk's own keyframes.
    """

    case = _branched_case()
    view = _case_view(application, case)

    assert view.case is case
    assert view.case.trunk is view.runs[0].controller
    assert view._fork_section.isHidden() is False
    assert view._fork_panel.take_button.isHidden() is False


def test_a_dashboard_over_loose_runs_offers_no_branch_control(application: QApplication) -> None:
    """A control that could only refuse would present itself as working."""

    view = _shown_view(application, SimulationController())

    assert view.case is None
    assert view._fork_section.isHidden() is True


def test_a_dashboard_refuses_a_case_rooted_in_another_run() -> None:
    """Two curves on one axis claim one patient, so a foreign case would misattribute it."""

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

    A fork is a discrete action, so it draws once and at once (`PL-R2YM`),
    rather than leaving the frame owed. Both runs are paused afterwards, so a
    frame left to the render tick would never be drawn. Nothing here presents
    after the press, so the frame read is the one the press drew. A fork that
    added the run without redrawing fails on the one-run frame that
    `_case_view` drew (`PL-624C`).

    The selection is narrowed, through the legend, to the pair that the cap
    would draw first, so the second run leaves it unchanged.
    `test_a_fork_from_the_default_selection_draws_one_frame` takes the fork
    from a selection that the second run reduces, which drew a second frame
    until `PL-B1R9`. Together the two tests show that a press draws once from
    either kind of selection.
    """

    case = _branched_case()
    view = _case_view(application, case)

    for quantity in _concentration(view).legend.shown[COMPARED_COMPARTMENT_CAP:]:
        _concentration(view).legend.set_compartment_shown(quantity, False)

    presented = view.presented_frames

    _take_fork(view, 60.0)

    assert view.presented_frames == presented + 1, "taking the branch did not draw it"

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert len(frame.runs) == 2

    branch_times, _ = _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert branch_times, "the chart holds no curve for the branch"
    assert min(branch_times) == pytest.approx(60.0)


def test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis(application: QApplication) -> None:
    """One frame, both runs, and the branch's curve begins where it was taken.

    The frame read is the one the press drew, from the default selection
    rather than the narrowed one the test above takes the fork from. It used
    to present a frame itself first, which made every assertion below pass
    whether the fork redrew or not (`PL-624C`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    frame = _concentration(view).chart.frame
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
    """One press draws one frame, assembled once both runs know there are two, for both legends.

    The default selection is wider than `COMPARED_COMPARTMENT_CAP`, so the
    second run reduces it (`CompartmentSelection.with_run_count`), and the
    legend is shown the reduction. The reduction used to announce itself as a
    reader's change. The dashboard then drew a frame for it from inside
    `_rename_runs`, before the press drew its own frame. At that point the
    wash-in legend still counted one run, and neither run had been named.
    That made two assemblies for one discrete action, where `PL-R2YM` says
    one (`PL-B1R9`). Both legends are now told what a frame drew once it has
    been drawn (`PL-G3K7`). So the frame is assembled with each run named, and
    that frame is what brings both legends to two runs.
    `test_taking_a_fork_redraws_the_chart_without_prompting` checks the count
    from a selection that the cap leaves alone. This test checks it from a
    selection that the cap reduces, through every way a branch can be taken.
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

    The dashboard uses this count to limit its compartment selection to the
    compared cap, and the legends name the runs from it. The panels carry the
    names that the legend entries use. Each run has a section of setting
    controls of its own, so a second run adds one, and its readouts join the
    region (`PL-NWTM`).
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

    Once a branch is drawn, the column stacks one line per run, and the run
    names are in a different splitter section. So the only thing that tells
    the two lines apart is their stacking order, which nothing on screen
    declares. If the branch's F_A/F_I were read as the trunk's, it would
    invert the comparison the branch exists to teach. Its off-scale notice
    would report a clipped trace on a run that has none (`PL-25DD`).

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling, and the branch
    inherits the trunk's dial. So both runs draw a clipped circuit trace, and
    both advisories are on screen at once. That is the case in which a line
    with no name is most easily taken for the other run's.

    The test drives no presentation beyond the one that `_handle_fork`
    makes. So the names arrive on the frame the branch appears on, not on
    some later tick.
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

    states = _wash_in(view).states.lines
    off_scale = _concentration(view).off_scale.lines
    assert len(states) == len(off_scale) == 2

    for index in range(len(view.runs)):
        opening = f"{run_label(RUN_IDS[index])} — "
        assert states[index].text().startswith(opening)
        assert off_scale[index].isHidden() is False
        assert off_scale[index].text().startswith(opening)
        assert "Circuit" in off_scale[index].text()


def test_a_lone_run_leaves_the_shared_chart_lines_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so the column carries no name.

    The run panels and both legends already follow this rule (`_rename_runs`).
    The test checks it here, so that the attribution `PL-25DD` adds does not
    become standing chrome on the display a learner opens.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    off_scale = _concentration(view).off_scale.lines[0]
    state = _wash_in(view).states.lines[0]

    assert off_scale.isHidden() is False
    assert off_scale.text().startswith("Above the top of the plot:")
    assert state.text().startswith("Now: F_A/F_I =")
    assert run_label(FIRST_RUN) not in off_scale.text()
    assert run_label(FIRST_RUN) not in state.text()


#: A dial position above every agent's calibrated vaporizer maximum, so the core
#: refuses it whichever agent the run is on. Tests drive it through the handler,
#: because the slider's own maximum makes it unreachable on the control.
_ABOVE_ANY_VAPORIZER_PERCENT = 50.0


def test_the_halt_and_refusal_banners_name_their_run(application: QApplication) -> None:
    """The notice column is shared, and all three banners assert something about a run.

    Read as a message about the whole dashboard, "Simulation stopped" says
    that the case has stopped while the other run is still going. "The
    simulation is unchanged and still running its previous setting" is false
    of the run it is not about. That is the misreading that the hazard table's
    halted-versus-paused row exists to prevent, arriving through attribution
    rather than through wording (`PL-TSZM`).

    The test drives one of each at once, on different runs. That is the case
    in which the column holds two banners and neither names its run.
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

    It shows a halt from the snapshot alone, because the frame is what may
    have failed (`PL-25KS`). `_halt_every_run` swallows the redraw that
    follows. So when the shared render path raises, this banner is the last
    one written. Taking the run count from the frame would drop the
    attribution in exactly that case (`PL-TSZM`).
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    for run in view.runs:
        run._presented = False

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
    true of the display while the trunk was alone. It is false of the branch
    the moment the branch appears. So the name has to arrive on the frame the
    branch appears on, not on some later tick (`PL-TSZM`).

    The presentation that `_handle_fork` drives delivers the name. It
    rewrites every run's banner through `_write_notice` after `_rename_runs`
    has named the runs. A rewrite attached to `set_run_name` would not be the
    mechanism. Such a rewrite was written and then removed. The fork's own
    presentation and the Reset that drops a branch both already rewrite the
    banner. So no scenario could tell that rewrite from its absence, and a
    guarantee that nothing can make fail is not a guarantee. This test is
    what keeps the presentation in that role.
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

    `_rename_runs` applies this rule to the run panels and both legends. The
    test checks it here, so that the attribution does not become standing
    chrome on the display a learner opens.
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()

    run._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)

    notice = run._notice_text.notice()

    assert notice is not None
    assert notice.startswith("Setting refused")
    assert run_label(FIRST_RUN) not in notice


@pytest.mark.parametrize("compared", [False, True], ids=["one run", "two runs"])
def test_hidden_notice_banners_take_no_height(application: QApplication, compared: bool) -> None:
    """A banner with nothing to say takes no room, and a shown one sits under the transport rows.

    The unconditional region, the band of required values that no Workspace
    can remove, has little height to spare on a laptop screen. So every
    pixel it spends on a hidden banner is a pixel the concentration chart
    loses (`PL-T91K`). The expected gaps are the theme's page spacing, not a
    value read from the layout under test. With two runs, only the branch's
    banner is shown. The hidden trunk banner ahead of it must not push it
    down. The branch's banner sits where the trunk's banner would, so only
    its words say which run it belongs to (`PL-TSZM`).
    """

    if compared:
        view = _case_view(application, _branched_case())
        _take_fork(view, 60.0)
    else:
        view = _shown_view(application, SimulationController(agent_id="isoflurane"))

    _settle(application)
    transports = view._transport_column.parentWidget()
    readouts = view._readout_column.parentWidget()
    banners = [run._notice_text for run in view.runs]

    assert len(banners) == (2 if compared else 1)
    assert all(banner.isHidden() for banner in banners)
    assert readouts.y() == transports.geometry().bottom() + 1 + PAGE_SPACING

    run = view.runs[-1]
    run.controller.start()
    run._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)
    _settle(application)
    shown = banners[-1]

    assert shown.isVisible()
    assert shown.y() == transports.geometry().bottom() + 1 + PAGE_SPACING
    assert readouts.y() == shown.geometry().bottom() + 1 + PAGE_SPACING


def test_the_sidebar_panels_name_the_run_they_record(application: QApplication) -> None:
    """Both panels sit in a column the runs share, so each heading says whose.

    Once a branch is drawn, the sidebar stacks two accounting panels, and the
    unconditional region's record column stacks two control-change panels
    (`PL-NWTM`). Before that change, one column stacked all four, and nothing
    on any of them said which run it recorded. Both kinds of panel carry a
    claim about one run. One is a mass-balance status with litres of
    equivalent pure agent gas. The other is a list of settings under the
    words "What was changed during this run". If the second were read as the
    other run's, it would say that the trunk received an intervention it
    never got (`PL-C3GS`).

    The trunk is given a setting change before the fork, and the branch is
    given one after it. So the two control-change lists differ, and
    misattributing either list is a concrete wrong reading rather than a
    formal one.

    The test checks the attribution on the labels that the panels hold, not
    on freshly built ones. Each label is then found under the shared column,
    which shows that the named heading is the heading on screen.
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

    The layout container holds the Areas that a reader resizes (`PL-W9P6`).
    So a reader could close away a value inside it once Areas can be closed
    (`PL-NWTM`). The test checks both runs of a compared case, because the
    second run's widgets are placed an hour after the first's. The halt
    banner is hidden while nothing has halted, so the test checks only its
    place. Every other value must be on screen.
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

    The expected text is worked out by hand. The dial opens at sevoflurane's
    own 1 MAC, 2.0% (`data/agents/sevoflurane.json`), which is 1.00 ×MAC.
    Moved to 3.0%, it is 1.50 ×MAC.
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
    """The declaration decides what the region holds, so a run lacking a value is not shown.

    The test builds the dashboard in two ways. In the first, the 1 MAC
    statement is taken out of the run's mapping. In the second, the mapping
    points the statement at the first View inside the splitter tree. A
    dashboard built either way would draw ×MAC numbers whose divisor a reader
    could close away.
    """

    original = RunView.unconditional_widgets
    build_areas = AreaLayout.__init__
    built: list[AreaLayout] = []

    def recorded(areas: AreaLayout, *args: Any, **kwargs: Any) -> None:
        build_areas(areas, *args, **kwargs)
        built.append(areas)

    def short_of_one_mac(run: RunView) -> dict[UnconditionalValue, QWidget]:
        widgets = dict(original(run))

        if misplaced == "missing":
            del widgets[UnconditionalValue.ONE_MAC]
        else:
            widgets[UnconditionalValue.ONE_MAC] = built[-1].views()[0]

        return widgets

    monkeypatch.setattr(AreaLayout, "__init__", recorded)
    monkeypatch.setattr(RunView, "unconditional_widgets", short_of_one_mac)

    with pytest.raises(RuntimeError, match="does not hold one_mac"):
        SimulationView((SimulationController(),))


def test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so neither heading gains a name.

    `_rename_runs` already applies this rule to the run panels and both
    legends. The test checks it here, so that `PL-C3GS`'s attribution does not
    become standing chrome on the display a learner opens.
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
    """A reader's drag of a border updates the layout model, not only the widgets.

    `_EVERY_VIEW` draws the chart panel and the sidebar as two Areas of one
    row (`PL-W9P6`), under the parameter controls' Area. The test drags the
    border between them 100 px to the left. The chart panel's share of the row
    then equals its new pixel width divided by the row's width, and the
    sidebar is wider by the same 100 px.
    """

    view = _shown_view(application, SimulationController())
    splitter = _sidebar_splitter(view)
    chart_px, sidebar_px = splitter.sizes()
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() - 100, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()

    column = view.layout_container.model.windows[0].tree
    assert isinstance(column, Split)
    tree = column.children[1]
    assert isinstance(tree, Split)
    assert splitter.sizes() == [chart_px - 100, sidebar_px + 100]
    assert tree.sizes[0] == pytest.approx((chart_px - 100) / (chart_px + sidebar_px), abs=1e-2)
    assert view.layout_container.frame(AreaId(1)).content is _concentration(view)


def test_splitting_and_closing_the_chart_area_leaves_the_unconditional_values_where_they_were(
    application: QApplication,
) -> None:
    """The Area menu changes only the Areas, so the region above them is untouched (`PL-2KXB`).

    The new half of a split builds a second concentration chart, and the
    first Area keeps its own. Closing the new half gives its place back.
    """

    from anesthesia_sim.app.area_layout import CLOSE_AREA_LABEL, SPLIT_STACKED_LABEL

    view = _shown_view(application, SimulationController())
    areas = view.layout_container
    before = areas.model
    region = view.unconditional_region
    first_chart = _concentration(view)
    shown_before = _visible_strings(view)

    (split,) = [op for op in areas.operations(AreaId(1)) if op.label == SPLIT_STACKED_LABEL]
    areas.perform(split)
    _settle(application)
    (new_area,) = [area.id for area in areas.model.areas() if area not in before.areas()]

    charts = [v for v in areas.views() if isinstance(v, ConcentrationView)]
    assert areas.frame(AreaId(1)).content is first_chart
    assert len(charts) == 2 and areas.frame(new_area).content in charts
    assert view.unconditional_region is region
    assert not areas.isAncestorOf(region)

    (close,) = [op for op in areas.operations(new_area) if op.label == CLOSE_AREA_LABEL]
    areas.perform(close)
    _settle(application)

    # The split and the close each rescale the sizes, so they come back
    # equal only to rounding.
    assert areas.model.areas() == before.areas()
    assert _visible_strings(view) == shown_before


def _sidebar_splitter(view: SimulationView) -> QSplitter:
    """The splitter whose one border lies between the chart panel and the sidebar.

    It is the only row in `_EVERY_VIEW`, under the parameter controls' Area.
    """

    (splitter,) = (
        splitter
        for splitter in view.layout_container.findChildren(QSplitter)
        if splitter.orientation() == Qt.Orientation.Horizontal
    )

    return splitter


def _drag_area_border(application: QApplication, view: SimulationView, by_px: int) -> None:
    """Drag the border between the chart panel and the sidebar by `by_px`, as a mouse does."""

    splitter = _sidebar_splitter(view)
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
    A drag of the Area border changes the chart's width but not the
    dashboard's, so a guard on the dashboard's own resize never fired. On
    `main` at `512fdaed`, the tick after the drag drew nothing, and the
    widened plot kept 2 px chords. The run has thirty minutes of history. So
    the frame has more instants than the narrowed plot has pixels, and the
    columns, not the run, set the chord.
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

    So only a widening is owed a frame (`resample_owed`). While the run is
    paused, a tick after a narrowing drag draws nothing, and no drawn chord
    is wider than a pixel.
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

    The fork is refused visibly rather than silently. The control is hidden
    in the same way that the transport hides the agent selector, and the
    reason stays where it was, even after a press. Replacing the shown branch while
    the first branch went on living inside `BranchedCase` would create state
    that the screen does not show.
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

    This is the one sequence that the interface could not complete: mark the
    decision point, watch the run stop there, and branch there. The branch
    opens at the instant on which the trunk halted. It does not open at the
    nearest keyframe, which is what a learner used to have to settle for. It
    arrives through the same panel from which a control-event fork is taken.

    The trunk is left on its halt, which makes this a comparison rather than
    an undo.
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

    A bare "Branch here" beside the permanent button would leave two
    identical buttons doing different things. The instant is the one at which
    the branch opens, not the one the learner marked. Those differ whenever a
    mark lies inside a step, and naming the wrong one would put a correct
    control under a wrong label.
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
    end. So the instant a learner marked and the instant at which a branch
    can open are two different numbers. The branch opens at the second one,
    because it is the only one for which the run holds state. So the button
    has to show the second one. Showing the first would put a correct control
    under a label naming a time at which nothing happens.
    `CLAUDE.md`'s safety-critical standard counts that as a failure of the
    value rather than of its presentation.
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
    """`PL-Y2SL`: the control is shown on any pause, and while running it is absent, not inert.

    The control is there on the paused trunk and gone once the trunk starts.
    It comes back with the halt's own words when a mark stops the trunk, goes
    again on the next step, and comes back with the plain words when the
    learner pauses. The selector does not follow it, which is the point of
    making this a second control. A list that gained and lost a row would
    change its entries under a reader who had looked away. A control that is
    either there or not can be noticed on sight. The mark the run stopped on
    joins the selector when the clock reaches it, as a mark the trunk has
    passed (`PL-W4XQ`). The end of the halt does not take it away again.
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

    The trunk is at 120 s, which is neither a keyframe nor a mark, so no
    entry in the selector names it. The button names it. The branch that the
    button takes opens at that instant and is drawn beside the trunk. The
    trunk stays where it was.
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
    """The cap applies to branches, whichever control a branch is taken through.

    A second fork taken through the transient control has to be refused
    exactly as one through the permanent control is. The display is capped at
    two runs, and there is no run selector. So the control goes off the panel
    rather than staying enabled only to apologise when pressed. The guard
    behind it still applies, for a press that reaches it anyway.
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

    The position of a running trunk moves with every step. So the case
    refuses a fork there, rather than taking one a step or a tick away from
    the instant the button named. The reason reaches the notice instead of
    being swallowed. The panel's own frame does not prove that the fork is
    still available.
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
    redrawn only at the end of a frame. So with every frame failing, the
    trunk showed "Stopped - simulation error" beside an enabled "Branch
    here: 1m". A press was refused by the case, and the next failing frame
    lost the refusal (`PL-MMNX`). The halt now redraws the panel from the
    case, which offers no fork on a failed trunk.
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
    this, the keyframe selector's Branch button stayed enabled and `fork_at`
    opened the branch. The case now refuses every way of opening a branch,
    as well as withdrawing the offer.
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

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
        case.fork_at(CaseInstant(60.0))

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
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

    The restatement runs inside the halt path. There, an exception would
    escape the render path's guard into the toolkit and leave the halt's
    retry undone. So the restatement is guarded. A panel that it cannot
    restate offers nothing, rather than the last frame's offer (`PL-MMNX`).
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


def test_a_failing_frame_withdraws_the_last_frames_bookmark_standings(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If every frame fails, the bookmark panel stops listing an unreachable mark as still to come.

    The bookmark panel used to be redrawn only from the snapshots in a
    frame that drew. When every frame failed, the panel kept the standings from the last
    frame that drew. So a mark ahead of the clock was still listed as to come, beside
    "Stopped - simulation error". That row tells a learner to wait for a mark that the
    failed run will never reach (`PL-YHR3`). Now, when the run halts, the panel is redrawn
    from each run's own record of its marks. That redraw does not need a frame.

    The test writes the expected row as a literal string. It copies the panel's wording for
    a mark that a failed run can no longer reach. The test then lets frames draw again and
    checks that a frame of the same failed run shows the same row. That shows the redraw at
    the halt and the redraw from a frame agree.
    """

    controller = _paused_run_with_history()
    # Ahead of the paused clock, so the run has not reached it yet.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    ahead = view._bookmarks_panel.times.text()
    assert ahead == "10m – check", "the mark is not listed as still to come"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    halted = view._bookmarks_panel.times.text()
    assert halted == "10m – check · not reached before the simulation error"

    monkeypatch.undo()
    view.present(False)

    assert view._bookmarks_panel.times.text() == halted


def test_a_failing_frame_restates_each_displayed_run_s_own_bookmark_standings(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When a trunk and its branch halt, the panel gives each run its own standing, not the trunk's.

    The branch ran up through a marked height of 0.50 xMAC alveolar that the
    trunk never reached. When every frame fails, both runs stop. The branch has
    still reached the mark, but the trunk now cannot reach it. So the mark's row
    names both runs. Suppose the halt gave every run the standings of the
    reference run, which here is the trunk. The two runs would then agree, so the
    panel would draw the row without naming either run (`PL-YHR3`).
    """

    view = _halted_branch_view(application)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert all(run.controller.has_failed for run in view.runs)
    targets = view._bookmarks_panel.targets.text()
    failed = MARK_STANDING_COMPARED_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]
    reached = MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]

    assert f"{run_label(FIRST_RUN)} {failed}" in targets
    assert f"{run_label(SECOND_RUN)} {reached}" in targets


def test_a_bookmark_panel_that_cannot_be_restated_on_a_halt_lists_no_standing(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """If restating the bookmark panel raises, the halt hides both listings and still takes effect.

    The restatement runs inside the halt path, where an exception would escape
    the render path's guard and reach the toolkit. So the restatement is guarded, as
    the fork panel's restatement is (`PL-MMNX`). A panel that cannot be restated
    shows no standing at all, rather than the last frame's standings (`PL-YHR3`).
    The next frame that draws shows both listings again.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    panel = view._bookmarks_panel
    assert panel.times.isHidden() is False

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)
    capfd.readouterr()

    view.present(False)

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert panel.times.isHidden() is True
    assert panel.targets.isHidden() is True

    monkeypatch.undo()
    view.present(False)

    assert panel.times.isHidden() is False
    assert panel.targets.isHidden() is False


#: The containers whose controls a halt leaves unchanged, each with the reason. The test
#: below requires every other control on the dashboard, including one added later, to sit
#: in one of two places. One is a `RunView`, which restates its own widgets (`PL-X7D5`).
#: The other is a panel that `SimulationView.halt_restatements` lists. A control in
#: neither keeps offering its action over a run that every other control says has failed,
#: as the branch panel did (`PL-MMNX`) and the bookmark panel did (`PL-YHR3`). The keys
#: are class names, because the dashboard builds each kind of container once per Area or
#: once per dashboard.
#:
#: The test also checks the other direction. An entry that matches no control on the
#: built dashboard fails the test, because nothing then needs the exemption.
NOT_RESTATED_ON_A_HALT: dict[str, str] = {
    "WorkspaceTabs": (
        "the Workspace tabs choose and rename layouts. A layout is the reader's "
        "arrangement of Areas, so it acts on no run."
    ),
    "ViewChooser": ("an Area's View chooser picks what the Area shows, which acts on no run."),
    "TimeBaseSelector": (
        "a chart's time base is the chart's own drawing setting. It touches no "
        "simulation state, and it is never disabled (`PL-012`)."
    ),
    "TraceLegend": (
        "the legend's boxes ask the dashboard which compartments to draw. The "
        "selection is the dashboard's display state and acts on no run (`PL-VN6M`)."
    ),
}

#: The widget types a reader acts through. A scroll bar is left out: it moves
#: the widget that holds it, and that widget's own container is what is checked.
_CONTROL_TYPES = (
    QAbstractButton,
    QComboBox,
    QAbstractSlider,
    QAbstractSpinBox,
    QLineEdit,
    QAbstractItemView,
)


def _controls(root: QWidget) -> list[QWidget]:
    """Every control under `root` that a reader can act through, except a combo box's popup."""

    found: list[QWidget] = []

    for widget in root.findChildren(QWidget):
        if not isinstance(widget, _CONTROL_TYPES) or isinstance(widget, QScrollBar):
            continue

        ancestor = widget.parentWidget()

        while ancestor is not None and not isinstance(ancestor, QComboBox):
            ancestor = ancestor.parentWidget()

        if ancestor is None:
            found.append(widget)

    return found


def _ancestry(widget: QWidget) -> list[QWidget]:
    """The widget and every widget above it, nearest first."""

    chain: list[QWidget] = []
    current: QWidget | None = widget

    while current is not None:
        chain.append(current)
        current = current.parentWidget()

    return chain


#: Each entry is a callback that a view connects to a signal or passes to another call without
#: the halt gate. Its key is the view class's name and the callback's source text, and its value
#: is the reason the callback does not need the gate. Qt or a view calls every callback not
#: listed here from the event loop, so an exception raised inside it is lost unless it passes
#: the gate (`PL-HJKN`). The test fails on an entry if its callback is no longer connected or
#: passed on, or if the callback now passes the gate, so the list stays accurate.
_HANDED_OUT_WITHOUT_THE_HALT_GATE: Final[dict[tuple[str, str], str]] = {
    ("RunView", "dialog.deleteLater"): (
        "it is Qt's own slot, which deletes the dialog once it closes, and it reads no run"
    ),
    ("SimulationView", "self._trunk_reset_question"): (
        "it returns the question that the trunk's Reset asks, and the trunk's own gated "
        "Reset slot calls it"
    ),
    ("SimulationView", "self._open_runs"): (
        "it returns the open runs' identities to the tab strip, and it reads no snapshot"
    ),
    ("SimulationView", "self._restate_fork_panel"): (
        "it runs inside the halt path, which a gate would enter again, and HaltRestatement "
        "requires that it not raise"
    ),
    ("SimulationView", "self._restate_bookmark_panel"): (
        "it runs inside the halt path, which a gate would enter again, and HaltRestatement "
        "requires that it not raise"
    ),
    ("SimulationView", "lambda: self.workspaces"): (
        "it returns the Workspaces as the Areas draw them, for the tab strip to duplicate "
        "or save, and it reads no run"
    ),
}


def _own_method(node: ast.expr, view_class: type) -> str | None:
    """Return `<name>` when `node` is `self.<name>` for a method of `view_class`, else None.

    A property does not count as a method, because `self.<name>` then gives the property's
    value, not a method.
    """

    if not (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return None

    member = inspect.getattr_static(view_class, node.attr, None)

    if member is None or isinstance(member, property) or not callable(member):
        return None

    return node.attr


#: This set names the calls that take a slot as a positional argument after the first one,
#: as `QTimer.singleShot(msec, slot)`, `QShortcut(key, parent, slot)` and
#: `QMenu.addAction(text, slot)` do. The check treats those arguments as it treats a slot
#: passed to `.connect` (coverage review of `PL-HJKN`).
_CALLS_THAT_TAKE_A_SLOT: Final = frozenset({"singleShot", "callLater", "addAction", "QShortcut"})


@cache
def _qt_signal_names() -> frozenset[str]:
    """Return the name of every signal that a class in QtCore, QtGui or QtWidgets declares.

    PySide6 lets a constructor connect a signal. A keyword argument named after the signal
    connects that signal to the argument's value, as in `QPushButton("Pause", clicked=slot)`.
    So a keyword argument with a signal's name passes a slot.
    """

    return frozenset(
        name
        for module in (QtCore, QtGui, QtWidgets)
        for _, member in inspect.getmembers(module, inspect.isclass)
        for name, value in vars(member).items()
        if isinstance(value, QtCore.Signal)
    )


def _elements(node: ast.expr) -> Iterator[ast.expr]:
    """Yield `node`, or each element of it when it is a tuple, list, set, dict or starred value."""

    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for element in node.elts:
            yield from _elements(element)
    elif isinstance(node, ast.Dict):
        for value in node.values:
            yield from _elements(value)
    elif isinstance(node, ast.Starred):
        yield from _elements(node.value)
    else:
        yield node


def _callback_bypass(
    callback: ast.expr,
    view_class: type,
    local_functions: set[str],
    *,
    position: str,
    run_at_once: bool,
) -> str | None:
    """Return why `callback` bypasses the halt gate, or None if it does not.

    `position` says how the call takes `callback`. It is "connect" for the argument of
    `.connect`. It is "slot" for a positional argument after the first of a call named in
    `_CALLS_THAT_TAKE_A_SLOT`, and for the value of a keyword argument named after a signal.
    It is "argument" for any other argument. `run_at_once` is True when the call is to one
    of the view's own methods. Such a method runs the callback at once, inside the slot
    that makes the call.

    A method of the view passes the gate when it is gated, in any position. A lambda or a
    local function bypasses the gate in every position, unless one of the view's own methods
    runs it at once. In the "connect" and "slot" positions, every other callback bypasses
    the gate too. That includes a slot of another object, such as `run.controller.pause`,
    and a slot reached through an attribute of the view, such as `self.controller.pause`.
    In the "slot" position, though, a name, a constant, a call or one of the view's own
    attributes is a value and not a callback. An example is the parent widget that
    `QShortcut` takes. In the "argument" position, anything else is a value too. This
    function returns None for a value.
    """

    method = _own_method(callback, view_class)

    if method is not None:
        gated = passes_halt_gate(inspect.getattr_static(view_class, method))

        return None if gated else f"{method} does not pass the gate"

    local = isinstance(callback, ast.Lambda) or (
        isinstance(callback, ast.Name) and callback.id in local_functions
    )

    if position == "argument":
        if local and not run_at_once:
            return "a lambda or a local function that the callee may call from the event loop"

        return None

    if local:
        return "a lambda or a local function, which cannot pass the gate"

    if position == "connect" and isinstance(callback, ast.Name):
        return "a function named bare, which cannot pass the gate"

    held_by_the_view = (
        isinstance(callback, ast.Attribute)
        and isinstance(callback.value, ast.Name)
        and callback.value.id == "self"
    )

    if position == "slot" and (
        held_by_the_view or isinstance(callback, (ast.Name, ast.Constant, ast.Call))
    ):
        return None

    names_self = any(
        isinstance(node, ast.Name) and node.id == "self" for node in ast.walk(callback)
    )

    if names_self:
        return "a slot reached through the view that is not its own method"

    return "a slot of another object, which may read or change a run outside the gate"


def _unwrapped_partial(node: ast.expr) -> ast.expr:
    """Return the function that `node` wraps when it is a `partial` call, or `node` itself."""

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "partial"
        and node.args
    ):
        return node.args[0]

    return node


@dataclass(frozen=True)
class _HaltGateReading:
    """What `_halt_gate_bypasses` found in one view's source."""

    #: Each call that passes on a callback bypassing the gate, or each method that overrides
    #: Qt's own without the gate, as its source text and why.
    bypasses: list[tuple[str, str]]
    #: Each key of the exemptions whose callback passes the gate, so the entry is stale.
    exempt_but_gated: list[tuple[str, str]]
    #: Each key of the exemptions whose callback the source passes on.
    exemptions_handed_out: set[tuple[str, str]]
    #: How many `.connect` calls the source makes.
    connections: int


def _halt_gate_bypasses(
    view_class: type, exemptions: Mapping[tuple[str, str], str]
) -> _HaltGateReading:
    """Find each call in `view_class`'s source whose callback bypasses the halt gate.

    The source holds every connection the class makes, including the ones it makes when it
    later builds a dialog. A `partial` in a slot position is treated as the method that it
    wraps. A method that overrides one of Qt's own, such as `keyPressEvent`, is called by
    Qt directly, so it must pass the gate too. Each key in `exemptions` pairs the class's
    name with the callback's source text, or with `def <name>` for such a method. A callback
    listed there is not reported as a bypass, but its entry is reported as stale when the
    callback passes the gate.

    The check reads only the class's own source. It cannot see a slot that a function
    outside the class connects, or a callback held in a variable before it is passed on.
    """

    (class_node,) = ast.parse(inspect.getsource(view_class)).body
    assert isinstance(class_node, ast.ClassDef), f"{view_class.__name__}'s source is not a class"
    methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
    local_functions = {
        node.name
        for method in methods
        for node in ast.walk(method)
        if isinstance(node, ast.FunctionDef) and node is not method
    }
    qt_bases = [base for base in view_class.__mro__ if base.__module__.startswith("PySide6")]
    judged: list[tuple[str, str, str | None]] = []

    for method in methods:
        if not method.name.startswith("__") and any(
            hasattr(base, method.name) for base in qt_bases
        ):
            gated = passes_halt_gate(inspect.getattr_static(view_class, method.name))
            reason = None if gated else "it overrides a Qt method, which Qt calls directly"
            judged.append((f"def {method.name}", f"def {method.name}", reason))

    connections = 0

    for call in (node for node in ast.walk(class_node) if isinstance(node, ast.Call)):
        if isinstance(call.func, ast.Attribute):
            called: str | None = call.func.attr
        else:
            called = call.func.id if isinstance(call.func, ast.Name) else None

        if called == "disconnect":
            continue

        positioned: list[tuple[ast.expr, str]]

        if called == "connect":
            connections += 1
            (slot,) = call.args
            positioned = [(_unwrapped_partial(slot), "connect")]
        else:
            slots = call.args[1:] if called in _CALLS_THAT_TAKE_A_SLOT else []
            passed = [(argument, any(argument is slot for slot in slots)) for argument in call.args]
            passed += [
                (keyword.value, keyword.arg in _qt_signal_names()) for keyword in call.keywords
            ]
            positioned = []

            for value, takes_a_slot in passed:
                if takes_a_slot:
                    positioned.append((_unwrapped_partial(value), "slot"))
                else:
                    positioned.extend((element, "argument") for element in _elements(value))

        run_at_once = _own_method(call.func, view_class) is not None

        for callback, position in positioned:
            reason = _callback_bypass(
                callback, view_class, local_functions, position=position, run_at_once=run_at_once
            )
            judged.append((ast.unparse(call), ast.unparse(callback), reason))

    bypasses: list[tuple[str, str]] = []
    exempt_but_gated: list[tuple[str, str]] = []
    exemptions_handed_out: set[tuple[str, str]] = set()

    for text, callback_text, reason in judged:
        key = (view_class.__name__, callback_text)

        if key in exemptions:
            exemptions_handed_out.add(key)

            if reason is None:
                exempt_but_gated.append(key)
        elif reason is not None:
            bypasses.append((text, reason))

    return _HaltGateReading(bypasses, exempt_but_gated, exemptions_handed_out, connections)


def test_every_slot_that_touches_a_run_passes_the_halt_gate() -> None:
    """Every slot that `RunView` and `SimulationView` connect or hand out passes the halt gate.

    A slot that reads or changes a run can raise, for example on a run whose snapshot
    refuses a value. PySide6 prints an exception raised inside a slot and carries on, so the
    run still said "Paused", and no halt appeared on screen. Each slot used to be wrapped in
    a `try` by hand, and six were found without one, each in a separate review: `PL-YK2V`,
    `PL-7DJK`, `PL-V2HC`, `PL-08SS`, `PL-F2T2` and `PL-M3M2`. Every slot now passes through
    `app/halt_gate.py`'s `halt_gate`, and this test makes each new slot pass through it too
    (`PL-HJKN`).

    The test parses each class's source, and `_callback_bypass` decides which callbacks
    bypass the gate. The test fails on any such callback unless it is listed in
    `_HANDED_OUT_WITHOUT_THE_HALT_GATE` with the reason it does not need the gate.
    `test_the_halt_gate_check_finds_each_way_around_the_gate` shows that the check
    catches each kind of bypass.
    """

    bypasses: list[str] = []
    exempt_but_gated: list[tuple[str, str]] = []
    exemptions_handed_out: set[tuple[str, str]] = set()

    for view_class in (RunView, SimulationView):
        reading = _halt_gate_bypasses(view_class, _HANDED_OUT_WITHOUT_THE_HALT_GATE)
        bypasses.extend(f"{view_class.__name__}: {call}: {why}" for call, why in reading.bypasses)
        exempt_but_gated.extend(reading.exempt_but_gated)
        exemptions_handed_out |= reading.exemptions_handed_out

        assert reading.connections > 0, f"no connection found in {view_class.__name__}'s source"

    stale = set(_HANDED_OUT_WITHOUT_THE_HALT_GATE) - exemptions_handed_out

    assert not bypasses, "slots that bypass the halt gate:\n" + "\n".join(bypasses)
    assert not exempt_but_gated, f"exempt callbacks that pass the gate: {exempt_but_gated}"
    assert not stale, f"exempt callbacks that are no longer handed out: {sorted(stale)}"


class _ViewWiredAroundTheGate(QWidget):
    """A view that passes on callbacks in every shape the halt gate check must judge.

    It is never built, and `_wire` is never called. The check reads its source.
    """

    controller: Any

    def halt_for_slot(self, error: Exception) -> None:
        raise AssertionError("the view is never built")

    @halt_gate
    def _gated(self) -> None:
        pass

    @halt_gate
    def _gated_with_one(self, value: int) -> None:
        pass

    def _ungated(self) -> None:
        pass

    def _run_now(self, action: Callable[[], None]) -> None:
        action()

    def _register(self, actions: tuple[Callable[[], None], ...]) -> None:
        pass

    @halt_gate
    def showEvent(self, event: Any) -> None:
        pass

    def keyPressEvent(self, event: Any) -> None:
        self.controller.pause()

    def _wire(self, button: Any, run: Any, timer: Any, menu: Any, key: Any) -> None:
        def local() -> None:
            self._gated()

        button.clicked.connect(self._gated)
        button.clicked.connect(partial(self._gated_with_one, 1))
        button.clicked.connect(_bare_function)
        button.clicked.connect(run.controller.pause)
        button.clicked.connect(self._ungated)
        button.clicked.connect(lambda: self._gated())
        button.clicked.connect(local)
        button.clicked.connect(self.controller.pause)
        self._run_now(lambda: self._ungated())
        self._run_now(local)
        timer.singleShot(0, self._gated)
        timer.singleShot(0, self._ungated)
        timer.singleShot(0, lambda: self._gated())
        timer.singleShot(0, local)
        QShortcut(key, self, self._gated)
        QShortcut(key, self, self.controller.pause)
        menu.addAction("Pause", run.controller.pause)
        timer.singleShot(0, run.controller.pause)
        type(button)("Pause", clicked=self._gated)
        type(button)("Pause", clicked=run.controller.pause)
        self._run_now(*(self._ungated,))
        self._register((self._gated, self._ungated))


def _bare_function() -> None:
    """A module-level function that `_ViewWiredAroundTheGate` connects by its bare name."""


def test_the_halt_gate_check_finds_each_way_around_the_gate() -> None:
    """The check reports each callback in `_ViewWiredAroundTheGate` that bypasses the gate.

    The expected list below was written by hand from that class's source. Four kinds of
    callback pass the gate. They are a gated method in any position, a `partial` of a gated
    method, a gated override of a Qt method, and a lambda or a local function that one of
    the view's own methods runs at once. An exempt callback is not reported while it
    bypasses the gate. Once the gate covers it, its entry is reported as stale (blind
    review of `PL-HJKN`).
    """

    reading = _halt_gate_bypasses(_ViewWiredAroundTheGate, {})

    assert [call for call, _ in reading.bypasses] == [
        "def keyPressEvent",
        "button.clicked.connect(_bare_function)",
        "button.clicked.connect(run.controller.pause)",
        "button.clicked.connect(self._ungated)",
        "button.clicked.connect(lambda: self._gated())",
        "button.clicked.connect(local)",
        "button.clicked.connect(self.controller.pause)",
        "timer.singleShot(0, self._ungated)",
        "timer.singleShot(0, lambda: self._gated())",
        "timer.singleShot(0, local)",
        "QShortcut(key, self, self.controller.pause)",
        "menu.addAction('Pause', run.controller.pause)",
        "timer.singleShot(0, run.controller.pause)",
        "type(button)('Pause', clicked=run.controller.pause)",
        "self._run_now(*(self._ungated,))",
        "self._register((self._gated, self._ungated))",
    ]
    assert reading.exempt_but_gated == []
    assert reading.exemptions_handed_out == set()
    assert reading.connections == 8

    exempt = ("_ViewWiredAroundTheGate", "run.controller.pause")
    gated = ("_ViewWiredAroundTheGate", "self._gated")
    override = ("_ViewWiredAroundTheGate", "def keyPressEvent")
    reading = _halt_gate_bypasses(
        _ViewWiredAroundTheGate, {exempt: "a test", gated: "a test", override: "a test"}
    )
    reported = [call for call, _ in reading.bypasses]

    assert "button.clicked.connect(run.controller.pause)" not in reported
    assert "def keyPressEvent" not in reported
    assert reading.exempt_but_gated == [gated] * 5
    assert reading.exemptions_handed_out == {exempt, gated, override}


def test_a_raise_in_a_slot_that_no_try_guarded_halts_its_run(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exception in the Pause slot, which no hand-written `try` guarded, now halts the run.

    Before the halt gate (`PL-HJKN`), PySide6 printed the exception and carried on. The run
    kept showing that it was running, and nothing on screen said that it had failed. The
    halt gate now halts the run.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._start_button.click()
    assert run._pause_button.isEnabled() is True, "the started run offers no Pause to press"

    def refuse() -> None:
        raise RuntimeError("the pause could not be recorded")

    monkeypatch.setattr(controller, "pause", refuse)
    run._pause_button.click()

    assert controller.has_failed is True
    assert controller.snapshot().failure_reason == ("RuntimeError: the pause could not be recorded")
    assert run._status_text.text() == STATUS_FAILED_TEXT


def test_a_dashboard_slot_that_raises_withdraws_branching_and_names_the_dashboard(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exception in a dashboard slot halts every run, and the refusal names the dashboard.

    Through the halt gate, every slot of `SimulationView` that raises now halts every run,
    as a frame that fails does. One such slot is Edit on the marks panel, which raises when
    the editor cannot be built. The branch panel's refusal used to say "the frame this run
    is drawn in failed", although no frame had failed (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)

    def refuse(*args: object, **kwargs: object) -> NoReturn:
        raise RuntimeError("the marks editor could not be built")

    monkeypatch.setattr(simulation_view_module, "BookmarkDialog", refuse)
    view._bookmarks_panel.edit_button.click()

    assert [run.controller.has_failed for run in view.runs] == [True] * len(view.runs)
    assert case.trunk.fork_refusal == (
        "the dashboard this run is drawn in failed (RuntimeError: the marks editor could not "
        "be built), and a branch would be drawn by the same dashboard and could fail the same "
        "way; reset the run first"
    )


def test_a_halt_whose_dials_cannot_be_written_still_withdraws_branch_here(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt asks for a frame even if the dials cannot be written, so "Branch here" is withdrawn.

    `present_halt` raises once it has shown the halt, when a fresh gas flow range is narrower
    than the dial's step (`PL-M3M2`). `_halt_run` used to ask for no frame then, and the
    dashboard restates its branch panel only when it draws. So "Branch here" kept offering
    the halted trunk. Every slot of a run reaches this path through the halt gate, including
    `_handle_adjustment_start`, which no `try` guarded before (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]
    here = view._fork_panel.here_button
    assert here.isHidden() is False, "the paused trunk offers no Branch here to withdraw"
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    def refuse() -> None:
        raise RuntimeError("the adjustment could not be recorded")

    monkeypatch.setattr(case.trunk, "begin_control_adjustment", refuse)

    with pytest.raises(ValueError, match="can offer no setting"):
        trunk._handle_adjustment_start()

    assert case.trunk.has_failed is True
    assert here.isHidden() is True


def test_a_new_case_question_that_cannot_be_built_leaves_the_selector_working_after_reset(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failure to build the new-case question halts the run, and Reset frees the selector.

    `_confirm_new_case` used to record the pending agent before it built the question. When
    building the question raised an exception, the gate halted the run, but the pending agent
    was not cleared. So the selector put back every later pick, even after the Reset that the
    halt names as the way out (blind review of `PL-HJKN`).
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]
    running = controller.agent_id
    other = next(agent for agent in ("desflurane", "isoflurane", "sevoflurane") if agent != running)

    def refuse(*args: object, **kwargs: object) -> NoReturn:
        raise RuntimeError("the question could not be built")

    monkeypatch.setattr(run_view_module, "new_case_question", refuse)
    _select_agent(run, other)

    assert controller.has_failed is True
    assert run._agent_dropdown.currentData() == running

    monkeypatch.undo()
    run._reset_button.click()
    _select_agent(run, other)

    assert controller.agent_id == other


def test_a_refused_reset_whose_halt_cannot_write_its_dials_halts_the_run_once(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A refused Reset halts its run once, for the refusal, even when showing the halt raises.

    `_reset_now` used to halt the run itself, inside the gated Reset slot. Showing that halt
    raised for a fresh gas flow range narrower than the dial's step (`PL-M3M2`). The gate
    then caught the dial's exception and halted the run a second time, for that exception
    (blind review of `PL-HJKN`).
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    halted_for: list[str] = []
    halt_for_slot = RunView.halt_for_slot

    def recording(self: RunView, error: Exception) -> None:
        halted_for.append(type(error).__name__)
        halt_for_slot(self, error)

    monkeypatch.setattr(RunView, "halt_for_slot", recording)
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    with pytest.raises(ValueError, match="can offer no setting"):
        run._handle_reset()

    assert halted_for == ["SimulationConfigurationError"]
    assert controller.has_failed is True


def test_a_slot_that_raises_inside_the_halt_does_not_start_the_halt_again(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If a slot that the halt's own frame sets off raises, it does not halt every run again.

    Halting every run ends by drawing a frame. Laying that frame out emits `rangeChanged`,
    which calls `_follow_chart`. Before this change, when `_follow_chart` raised, its gate
    started the halt again inside the halt already under way. One exception started the halt
    21 times, nested 6 deep (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    depth = 0
    deepest = 0
    halt_every_run = SimulationView._halt_every_run

    def tracking(self: SimulationView, error: BaseException) -> None:
        nonlocal depth, deepest
        depth += 1
        deepest = max(deepest, depth)

        try:
            halt_every_run(self, error)
        finally:
            depth -= 1

    def refuse(self: SimulationView) -> NoReturn:
        raise RuntimeError("the chart is gone")

    monkeypatch.setattr(SimulationView, "_halt_every_run", tracking)
    view._chart_view_owed = True
    monkeypatch.setattr(SimulationView, "_chart_in_view", refuse)
    _take_fork(view, 60.0)
    _settle(application)

    assert deepest == 1
    assert [run.controller.has_failed for run in view.runs] == [True] * len(view.runs)


def test_every_dashboard_control_is_restated_on_a_halt(application: QApplication) -> None:
    """Every control on the dashboard is restated by a halt, or is named with why it need not be.

    A `RunView` restates its own widgets on a halt, and `PL-X7D5`'s guard enforces that by
    default. The dashboard's own panels sit outside every run. Each one used to be restated
    by hand in `_halt_every_run`, so a panel added later was restated only if someone
    remembered to add it there (`PL-5JTH`). This test builds the dashboard with every panel
    that holds a control. It gives the view a case, so that the branch panel is offered,
    adds a mark, and opens the marks editor. It then fails on any control that no run
    holds, that no `halt_restatements` panel holds, and that no container in
    `NOT_RESTATED_ON_A_HALT` holds.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    _opened_bookmark_dialog(view)
    run_widgets = {id(widget) for run in view.runs for widget in _widget_attributes(run).values()}
    restated = {
        id(panel) for restatement in view.halt_restatements() for panel in restatement.panels
    }
    exemptions_used: set[str] = set()
    unrestated: list[str] = []

    for control in _controls(view):
        chain = _ancestry(control)

        if any(id(widget) in run_widgets or id(widget) in restated for widget in chain):
            continue

        exempt = next(
            (type(w).__name__ for w in chain if type(w).__name__ in NOT_RESTATED_ON_A_HALT), None
        )

        if exempt is not None:
            exemptions_used.add(exempt)
            continue

        unrestated.append(" < ".join(type(widget).__name__ for widget in chain[:6]))

    assert view._bookmark_dialog is not None
    assert sorted(set(unrestated)) == [], (
        "these controls are in no RunView and in no panel a halt restates: add their panel "
        "to SimulationView.halt_restatements, or name its container in "
        "NOT_RESTATED_ON_A_HALT with the reason a halt need not restate it"
    )
    assert sorted(set(NOT_RESTATED_ON_A_HALT) - exemptions_used) == [], (
        "these exemptions match no control on the dashboard now - remove the entry"
    )


#: The widget types outside every run that may show differently on a halted
#: dashboard and on the same dashboard once a frame draws it. Each type maps to
#: the reason that only a frame can state it. The test below checks this list
#: in both directions, as it checks `FRAME_WIDGETS`: an unlisted difference
#: fails, and so does an entry that no longer differs (`PL-WM5P`).
SURFACE_FRAME_WIDGETS: dict[str, str] = {
    "QScrollBar": (
        "the page's scroll bar follows the height the frame lays the page out at, "
        "which is layout and states nothing about a run."
    )
}


def _run_widget_ids(view: SimulationView) -> set[int]:
    """Every widget a run holds, wherever its copies are placed, and every widget under each."""

    held: set[int] = set()

    for run in view.runs:
        for widget in (run, *_widget_attributes(run).values()):
            held.add(id(widget))
            held.update(id(child) for child in widget.findChildren(QWidget))

    return held


def _surface_widgets(view: SimulationView) -> dict[str, list[QWidget]]:
    """Every widget in the window that no run holds, grouped by its type and the five above it."""

    held = _run_widget_ids(view)
    surfaces: dict[str, list[QWidget]] = {}

    for widget in view.window().findChildren(QWidget):
        if id(widget) in held:
            continue

        chain = " < ".join(type(w).__name__ for w in _ancestry(widget)[:6])
        surfaces.setdefault(chain, []).append(widget)

    return surfaces


def _surface_states(view: SimulationView) -> dict[str, list[tuple[object, ...]]]:
    """Return what a reader sees of every widget outside the runs, read afresh.

    The window is walked again on each call. So a row that a frame adds, such
    as a newly listed mark, shows up as a difference rather than as a widget
    that nobody compares.
    """

    return {
        chain: [_widget_state(widget) for widget in widgets]
        for chain, widgets in _surface_widgets(view).items()
    }


def test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt states the run on every panel outside the runs, found by a walk rather than a list.

    `test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one`
    checks that each `RunView` has one writer of its run state (`PL-X7D5`).
    The branch panel, the marks panel, the marks editor and every Area's
    header sit outside the runs, and the halt restates them through
    `halt_restatements` (`PL-5JTH`). `test_every_dashboard_control_is_restated_on_a_halt`
    checks that each control is in a restated panel, but not what the panel
    then says. This test checks what it says. The run is drawn, and the
    branch panel is given a refusal. The refusal comes before the halt,
    because a halted trunk disables the branch controls. Then, while every
    frame fails, the test changes what the other panels state: it adds a
    mark and changes the playback rate. Finally it compares the halted
    screen, widget by widget, with the same dashboard once a frame draws it.
    So a panel that only a frame writes fails this test even though no list
    names it (`PL-WM5P`).
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    _opened_bookmark_dialog(view)
    view.present(False)
    view._fork_panel.point_selector.clear()
    view._fork_panel.take_button.click()
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "later"))
    trunk = view.runs[0]
    trunk._playback_rate_dropdown.setCurrentIndex(trunk._playback_rate_dropdown.findData(5))
    view.present(False)

    assert case.trunk.has_failed is True
    assert view._fork_panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT

    halted = _surface_states(view)

    monkeypatch.undo()
    view.present(False)

    drawn = _surface_states(view)
    differing = {
        chain.partition(" < ")[0]
        for chain in set(halted) | set(drawn)
        if halted.get(chain) != drawn.get(chain)
    }

    assert len(halted) > 20, "the walk found too few widgets to be reading the window"
    assert sorted(differing - set(SURFACE_FRAME_WIDGETS)) == [], (
        "these widgets outside every run read differently on a halted dashboard and on the "
        "same dashboard drawn: restate them from SimulationView.halt_restatements, or name "
        "their type in SURFACE_FRAME_WIDGETS with the reason only a frame can state them"
    )
    assert sorted(set(SURFACE_FRAME_WIDGETS) - differing) == [], (
        "these widgets read alike on a halted dashboard and a drawn one now, so their "
        "exemption is stale - remove the entry"
    )


def test_the_surface_guard_fails_on_a_panel_only_a_frame_writes(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The guard above catches a panel that a halt leaves as the last frame drew it.

    The marks panel's restatement is switched off here. The mark added while
    frames fail is then listed on the drawn dashboard and not on the halted
    one, which is the stale state the guard exists to catch.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    view.present(False)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(view, "_restate_bookmark_panel", lambda: None)

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "later"))
    view.present(False)
    halted = _surface_states(view)

    monkeypatch.undo()
    view.present(False)

    drawn = _surface_states(view)
    differing = {
        chain for chain in set(halted) | set(drawn) if halted.get(chain) != drawn.get(chain)
    }

    assert any("MarkListingLabel" in chain for chain in differing)


def test_a_dial_write_that_refuses_on_a_halt_still_restates_every_panel(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run whose dials cannot be written on a halt still lets the halt restate every panel.

    `present_halt` writes the dials last and raises when `setting_readouts`
    cannot build them, as `test_a_halt_is_stated_before_its_dials_are_written`
    shows for one run. `_halt_every_run` used to call it in a bare loop. So the
    exception left the halt path before the branch panel and the bookmark panel
    were restated. "Branch here" stayed enabled over a failed trunk, and a mark
    ahead of the clock still showed as still to come (`PL-TLH4`). The exception
    now waits until the panels are restated and the frame is tried. The test
    checks the bookmark row against the literal text of a mark that a failed run
    cannot reach, as `test_a_failing_frame_withdraws_the_last_frames_bookmark_standings`
    does.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _case_view(application, case)
    here = view._fork_panel.here_button
    assert here.isHidden() is False, "the paused trunk offers no branch here to withdraw"
    assert view._bookmarks_panel.times.text() == "10m – check"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    with pytest.raises(ValueError, match="can offer no setting"):
        view.present(False)

    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert here.isHidden() is True
    assert view._fork_panel.point_selector.count() == 0
    assert view._bookmarks_panel.times.text() == (
        "10m – check · not reached before the simulation error"
    )


def test_a_withdrawn_bookmark_panel_withdraws_the_open_dialog(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt that withdraws the bookmark panel withdraws the editor's lists and Remove buttons too.

    The editor lists the same rows as the panel beside the chart. A halt that could not
    work out the marks' standings used to hide the panel but leave the open editor
    listing the last frame's rows. The editor then still showed the mark ahead of the
    clock as still to come, and its Remove button still worked on that row (`PL-F5KT`).
    The next frame that is drawn shows both again.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    withdrawn = (
        dialog.time_list,
        dialog.remove_time_button,
        dialog.target_list,
        dialog.remove_target_button,
    )
    assert dialog.time_list.count() == 1
    assert not any(widget.isHidden() for widget in withdrawn)

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)

    view.present(False)

    assert controller.has_failed is True
    assert view._bookmarks_panel.times.isHidden() is True
    assert all(widget.isHidden() for widget in withdrawn)

    monkeypatch.undo()
    view.present(False)

    assert not any(widget.isHidden() for widget in withdrawn)


#: A mark name long enough that its row wraps in the bookmark panel at any
#: width the page allows.
_WRAPPING_MARK_NAME = "a mark name long enough to wrap " * 10


@pytest.mark.parametrize("height_px", [450, 1000])
def test_a_wrapped_mark_row_is_never_clipped(application: QApplication, height_px: int) -> None:
    """A mark row that wraps gets the height its lines need in a narrow window (`PL-KX97`).

    The row's name is long enough to wrap at the page's narrowest width, so
    the row under test does wrap. The expected height is the label's own
    `heightForWidth`, not a value read from the layout under test. A short
    window must scroll the page rather than squeeze the row.
    """

    case = BranchedCase(SimulationController())
    case.trunk.add_mac_target(
        MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5), _WRAPPING_MARK_NAME)
    )
    view = _case_view(application, case, width_px=700)
    view.resize(700, height_px)
    application.processEvents()
    view.present(False)
    application.processEvents()
    rows = [
        label
        for label in view._bookmarks_panel.findChildren(QLabel)
        if label.isVisible() and label.wordWrap() and _WRAPPING_MARK_NAME.strip() in label.text()
    ]

    assert rows

    for row in rows:
        needed_px = row.heightForWidth(row.width())

        assert needed_px > row.fontMetrics().height(), "the row does not wrap"
        assert needed_px <= row.height()


@pytest.mark.parametrize("door", ["take", "here"])
def test_a_fork_on_a_run_whose_snapshot_refuses_keeps_no_branch(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    door: str,
) -> None:
    """A fork on a trunk whose snapshot raises ends in the halt, and the case keeps no branch.

    The case used to keep the branch before `add_run` read its snapshot to draw it. On a
    run whose snapshot rejects a value (`PL-7DJK`), that read raised out of the slot. The
    press showed nothing and left a branch that was kept but never drawn. A second press
    kept a second one (`PL-08SS`). Both fork handlers now read the trunk's snapshot first,
    through the halt.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    if door == "take":
        _take_fork(view, 60.0)
    else:
        view._fork_panel.here_button.click()

    assert "Traceback" not in capfd.readouterr().err
    assert case.branches == ()
    assert len(view.runs) == 1
    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT


@pytest.mark.parametrize("kind", ["time", "target"])
def test_removing_a_mark_on_a_run_whose_snapshot_refuses_restates_the_halt(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    kind: str,
) -> None:
    """Pressing Remove in the marks editor on a run whose snapshot raises shows the halt.

    Both remove handlers read the reference run's snapshot to find the selected mark.
    They used to read it outside the code that halts the run on an error. So on a run
    whose snapshot rejects a value, the press raised out of the slot. The button did
    nothing, and nothing on screen said why (`PL-F2T2`). The read now goes through the
    halt, so the run shows as stopped and the mark stays where it was.
    """

    controller = _paused_run_with_history()
    time_mark = TimeBookmark(CaseInstant(30.0), "check")
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    controller.add_time_bookmark(time_mark)
    controller.add_mac_target(target)
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    listing, remove = (
        (dialog.time_list, dialog.remove_time_button)
        if kind == "time"
        else (dialog.target_list, dialog.remove_target_button)
    )
    listing.setCurrentRow(0)
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    remove.click()

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert controller.bookmarks.time_bookmarks == (time_mark,)
    assert controller.bookmarks.mac_targets == (target,)


def test_a_drag_whose_readouts_refuse_halts_the_run(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A dial whose readouts cannot be built after a drag halts the run, and says so on screen.

    After a dragged dial is applied, the run's own labels are rewritten at once from a
    snapshot. `setting_readouts` raises there for a control that can offer no setting.
    Only the apply step was inside the guard. So the exception escaped the slot, and the
    run still showed "Paused" with no banner (`PL-M3M2`). The exception now halts the run
    first. The dial write in the halt raises again, and that second exception still
    reaches the console.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]

    def no_setting(settings: object) -> NoReturn:
        raise ValueError("this control can offer no setting")

    monkeypatch.setattr(run_view_module, "setting_readouts", no_setting)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert run._start_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "can offer no setting" in notice


def test_unmarking_the_mark_the_trunk_stopped_on_leaves_the_fork_here(
    application: QApplication,
) -> None:
    """Unmarking ends the halt and not the pause, so the control stays and drops the mark.

    The run stays where it stopped either way, and a learner who unmarks the
    instant they stopped on can still branch at it. What changes is that no
    mark stopped the run there any more, so the label stops saying one did.
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

    The control cannot offer such an instant, because `fork_offer` builds the
    offer from `fork_points_s`. So the test hands the panel an offer that
    lists one, the way a frame hands it the real offer, to reach the guard
    behind it. A refusal leaves the case and the display untouched and says
    which instant was refused.
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
    """A branch taken at a mark asks the case again on the press, and a refusal reaches the notice.

    An entry can outlive what it offers, by the gap between a frame and a
    press. So `_handle_fork` hands the mark back to the case rather than
    trusting the entry. Here the panel holds an entry for a mark that the
    trunk does not hold. An unmark that lands in that gap leaves such an
    entry behind. `fork_at_mark` refuses it and names the instant, rather
    than branching anywhere near it.
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


def test_an_agent_change_clears_the_fork_refusal_notice(application: QApplication) -> None:
    """`PL-BM6X`: an agent change clears a branch-panel notice about the case it ended.

    An agent change on the trunk starts a new case, as Reset does. Until
    `PL-BM6X`, only Reset told the dashboard so, and the branch panel went on
    saying "Select an instant to branch at" about a case no longer on screen.
    Both ways of changing the agent are checked: a run that has recorded
    something asks first, and one that has recorded nothing switches at once.
    """

    view = _case_view(application, _branched_case())
    trunk = view.runs[0]
    view._fork_panel.point_selector.clear()
    view._fork_panel.take_button.click()

    assert view._fork_panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT

    _select_agent(trunk, "desflurane")
    dialog = trunk._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert trunk.controller.agent_id == "desflurane"
    assert view._fork_panel.notice.notice() is None

    view._fork_panel.point_selector.clear()
    view._fork_panel.take_button.click()

    assert view._fork_panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT
    assert trunk.controller.snapshot().has_recorded_run is False

    _select_agent(trunk, "isoflurane")

    assert trunk._new_case_dialog is None
    assert trunk.controller.agent_id == "isoflurane"
    assert view._fork_panel.notice.notice() is None


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
    enabled. Choosing another agent restarted the trunk and left
    `BranchedCase` listing a branch of a run that no longer existed.
    `assemble_chart_frame` then refused the frame over the shared MAC axis.
    So `_halt_every_run` failed both runs over an input to one of them. The
    switch is now refused before it reaches the controller.
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

    The trunk has started over, so it never passed through the instant at
    which the branch was taken. A branch left on the chart would show two
    curves claiming one patient under two managements, when they no longer
    describe one patient.
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

    The one-run case is every case before a learner branches. The guard that
    spares a one-run dashboard its layout work once returned before the
    refusal was cleared. So the banner went on reporting an instant that the
    restarted run does not hold, since that run is back at induction.
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

    A fork whose drawing raised leaves a branch that the case keeps but the
    dashboard does not draw (`PL-08SS`). The test builds such a branch by
    forking the case directly. It must not outlive the trunk's Reset as a
    branch of a run that no longer exists, merely because one run was on
    screen.
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
    """A branch's Reset returns it to its fork, and only the trunk's Reset starts a new case.

    The test checks that the lock is still there, because that is the part
    that surprises a learner (`PL-WG73`). The run they were trying to end has
    lost four steps of simulated case, and the control they were sent to
    press is still refused, under the same sentence.
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
    """Take a branch at 60 s and give it one of the two kinds of work `has_recorded_run` checks.

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

    The test covers both halves of `has_recorded_run`, because a question
    that checked only one half would miss the other. The warning is a
    literal: four steps of 0.1 s from the 60 s fork reach 1m0.4s on the case
    clock.
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


def test_an_open_trunk_reset_question_follows_a_running_branch(application: QApplication) -> None:
    """`PL-WM5P`: the Reset question names the branch work as it stands now, not when asked.

    Reset stays enabled while the runs step, so a branch goes on running
    while the trunk's question is open. The test compares the warning with a
    literal string: four steps of 0.1 s from the 60 s fork reach 1m0.4s, and
    four more reach 1m0.8s.
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]
    branch._start_button.click()

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert "run to 1m0.4s" in dialog.body_labels[1].text()

    _steps(branch, 4)
    view.present(False)

    assert dialog.body_labels[1].text() == (
        "Run 2 — branched at 1m and run to 1m0.8s, 0 recorded control changes — will be "
        "discarded along with its chart history. This cannot be undone."
    )
    assert dialog.title_label.text() == "Reset Run 1 and discard Run 2?"


def test_declining_the_trunks_reset_leaves_every_run_as_it_was(application: QApplication) -> None:
    """Keeping the branch keeps the trunk too: nothing is reset, and the comparison stays open."""

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

    After that the reader owns the page. So a later change of layout does not
    scroll the page back. Here that change is a shorter window, which moves
    the chart.
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

    `test_the_comparison_lock_names_a_control_the_learner_can_press` checks
    the sentence against what `run_label` and `RESET_LABEL` say. This test
    checks that the runs those names refer to are the ones drawn, and that
    each carries its name where a reader meets its Reset. It also checks that
    the Reset the sentence sends the reader to is the one that lifts the
    lock. Neither half is worth anything alone, because a name attributes a
    control only if the reader can find what it refers to.
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

    # Find the run that the way out is about by reading the sentence as a
    # learner reads it, not by looking it up by position. A lock that named
    # both runs correctly but paired each with the other's outcome would pass
    # every assertion above. It would still send the reader to the button
    # that keeps the mode.
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
    """`start_simulation_timer` started the runs that existed then, and this one did not exist.

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
    because the tick drew only while a run was running or a frame was owed
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
    assert _concentration(view).chart.frame is not None
    assert len(_concentration(view).chart.frame.runs) == 2
    assert _concentration(view).chart.drawn_points(BRANCH_RUN_INDEX, RecordedQuantity.ALVEOLAR)[0]

    view.render_tick()

    assert view.presented_frames == presented + 1, "a frame drawn for nothing owed"

    taken = _case_view(application, _branched_case())
    presented = taken.presented_frames

    _take_fork(taken, 60.0)
    taken.render_tick()

    assert taken.presented_frames == presented + 1


def test_adding_a_third_run_is_refused(application: QApplication) -> None:
    """The cap belongs to the display, so it applies to the public method as well as the control."""

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)

    with pytest.raises(
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 3"),
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
    """The marks belong to the case, so the run added after construction is written too."""

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

    The runs of a case-less dashboard are independent trunks. The constructor
    accepts them, and the two-trunk tests build them. So the first run
    starting over says nothing about the second. Dropping the second would
    destroy a recorded run over an input to another one, through the action
    a reader uses to start a single run again.
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
    """`PL-K5NY`: two curves on one axis claim one patient, so a stranger is refused.

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

    This state is reachable without a reset. A keyframe collapses when a setting is
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
    """`PL-J12Z`'s cleared selection lasts past the next rebuild, not for only one frame.

    Qt selects the first entry of an emptied selector as soon as it is
    refilled. So a rebuild that set no index put *induction* under a reader
    whose choice had just been cleared. That is the substitution the clear
    exists to refuse, arriving one setting change later. Since `PL-W4XQ`,
    each mark the trunk's clock reaches also causes a rebuild. That makes the
    later change the common case rather than a rare one.
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

    The mark was set after the clock had passed it. So no step crossed it,
    the trunk holds no keyframe there, and the trunk is not on a halt. The
    other two ways of taking a branch refuse this case. The mark is offered
    beside the control events. It is labelled with the instant at which the
    branch will open, not the instant typed. The branch opens there, and the
    trunk stays as it was.
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
    # branched, and its clock stays where it was paused.
    assert case.fork_points_s == keyframes
    assert case.trunk.snapshot().elapsed_s == pytest.approx(_REWIND_PAUSE_S)


def test_a_mark_still_ahead_of_the_trunk_s_clock_is_not_offered(application: QApplication) -> None:
    """The case holds no state at a mark the clock has not reached, so nothing branches there.

    A branch there would be a prediction drawn as a run. The mark stops the
    running case when it is reached, and then joins the selector. Until then
    the selector offers the control events and nothing else.
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
    """`PL-J12Z` for marks: an entry the learner removes takes the selection with it.

    Unmarking is how a mark leaves the list, as a collapsed keyframe is how a
    control event leaves it. Moving the choice to a neighbour, such as
    induction or the other mark beside it, would make the next press branch
    somewhere the learner did not choose. So the selector is left on nothing,
    and the press says so.
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


def _widest_mark_entry_fits(application: QApplication) -> tuple[int, int]:
    """Give a dashboard's selector its widest mark entry and measure that entry against the field.

    The widest entry is found here rather than taken from
    `widest_fork_point_label`, so the test does not check that function
    against its own result. The font spaces its digits proportionally, so
    23h59m59.9s, the reading at the last step, is not the widest reading.
    Hours, minutes and seconds vary independently, so the widest value of
    each, put together, is the widest clock reading that `format_elapsed`
    can write. The test passes the entry through `fork_offer` and reads it
    back from the selector, rather than measuring it as a bare string.

    Returns:
        The entry's advance, its drawn width, and the width of the
        selector's text field. Both are in pixels, in the font the selector
        is drawn in.
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

    return metrics.horizontalAdvance(panel.point_selector.currentText()), field.width()


def test_the_branch_selector_draws_its_widest_entry_whole(application: QApplication) -> None:
    """A mark's entry cut short would lose the words that say it is a mark.

    The selector has a fixed width. Its widest entry is the entry for a mark
    late in the supported run. So the test checks that the width fits that
    entry, in the font the selector is drawn in.
    """

    entry_px, field_px = _widest_mark_entry_fits(application)

    assert entry_px <= field_px


def test_the_branch_selector_fits_its_widest_entry_in_a_wider_face(
    application: QApplication,
) -> None:
    """The width still fits in a face and size that the container does not draw in (`PL-NC0D`).

    The application sets no font of its own, so the selector draws in the
    platform's default face and size. In DejaVu Sans at 16 px, the widest
    entry needs 228 px. The fixed 230 px width that this replaced left a
    text field of only 196 px, so the words "on your mark" were cut. The
    width is now measured from the selector's own font when it is built.
    """

    previous = application.font()
    wider = QFont("DejaVu Sans")
    wider.setPixelSize(16)
    application.setFont(wider)

    try:
        entry_px, field_px = _widest_mark_entry_fits(application)
    finally:
        application.setFont(previous)

    assert entry_px <= field_px


# --- one readout block at a laptop's width (`PL-F2YS`) -----------------------

#: The laptop reference width at which `PL-J8K2` and `PL-84QX` measured the region.
_LAPTOP_WIDTH_PX = 1366


def test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns(
    application: QApplication,
) -> None:
    """The record column takes the sidebar's share, so the readout row has room for seven.

    The test checks against the width the row itself reserves, not a pixel
    figure. So it states the requirement for whatever font renders the
    panels: the row is as wide as seven panels need, and it seats all seven
    across. With the record at the box layout's 3:1 share, the row was 3 px
    short of seven and opened on four (`PL-Z4K6`, `PL-J8K2` Q3).
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

    With two runs, each run's transport row and readout heading used to sit
    one above the other. The four lines left the chart about 200 px on the
    1366 by 700 laptop reference (`PL-JG82`). Now the rows are folded
    together. A run's line carries its own delivered concentration, and the
    agent chip puts its caption on the same line as the agent's name. The
    values both runs share are stated once, on the heading line above the
    paired readouts (`PL-QLZ5`). Those values are the substance, the agent's
    1 MAC and the version-and-model badge. The playback-rate selector is the
    tallest control on a run's line, so its height is the limit for one line.
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
        "off-scale": (concentration, concentration.off_scale.lines),
        "wash-in state": (wash_in, wash_in.states.lines),
    }


def test_each_view_places_one_copy_per_run_inside_itself(application: QApplication) -> None:
    """`PL-TH35`: a View shows its copies of the runs' surfaces in its own rectangle.

    Each run's line names the run (`PL-C3GS`), which another test reads off
    the run's own list of copies. That list cannot tell a copy placed in its
    View from one built and never placed. So this test checks that each copy
    is inside its View.
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
