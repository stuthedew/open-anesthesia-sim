"""Shared constants and helpers for the dashboard's integration tests in this directory.

The tests were one file, `tests/integration/test_simulation_view.py`, until `PL-1FPR` split them by
the behaviour each checks. This module holds what more than one of the new files uses. Its
description of the whole suite follows.

The dashboard, driven headless against real runs.

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

import re
from collections.abc import Sequence
from typing import Any, Final, NoReturn

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSlider,
    QApplication,
    QComboBox,
    QLabel,
    QLayout,
    QScrollArea,
    QWidget,
)

from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.chart_time_base import ChartTimeBase
from anesthesia_sim.app.controller import BranchedCase, SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    SIMULATION_STEP_S,
    WITHHELD_ACCOUNTING,
    ComparedRuns,
    accounting,
    run_label,
    slider_position,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_elapsed,
)
from anesthesia_sim.app.qt_widgets import BookmarkDialog, BookmarksPanel, ForkPanel, ParameterSlider
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    AGENT_COST,
    BOOKMARKS,
    BRANCH,
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    WASH_IN,
)
from anesthesia_sim.app.views import (
    AccountingView,
    BookmarksView,
    BranchView,
    ConcentrationView,
    ParameterControlsView,
    RunDials,
    WashInView,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood_flow import PerfusionFraction
from anesthesia_sim.core.concentration import Fraction, MacMultiple
from anesthesia_sim.core.exceptions import SimulationNumericalError
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: One Workspace that holds each View these tests read. Each test then
#: finds the View it reads, whichever Workspace is shipped first. The
#: parameter controls run across the top. Under them, the concentration chart
#: sits over the F_A/F_I plot, beside the accounting. That was the dashboard's
#: layout before it began opening on the shipped Workspaces (`PL-2KXB`). The
#: bookmarks and the branch control share the row at the foot, where that
#: layout had them before they became Views (`PL-9YPR`).
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
                            (0.2, 0.6, 0.2),
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
                                Split(
                                    Orientation.ROW,
                                    (0.5, 0.5),
                                    (Area(AreaId(5), BOOKMARKS), Area(AreaId(6), BRANCH)),
                                ),
                            ),
                        )
                    ),
                ),
                AreaId(7),
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
#: Any spelling of end-tidal not followed by the hedge, anywhere on screen,
#: and the abbreviations that clinicians and anesthesia monitors use for it
#: (`PL-86VL`). "ET" and "FET" count at the start of a word unless another
#: capital follows, so "ET2.1%" and "ETsevo" count and "FETCH" does not. "Et"
#: counts unless a small letter follows, so "Et1.8", "EtSevo" and "EtAA" count
#: and "Etc" does not. A small "et" counts only when a capital or a digit
#: follows, as in "etSev", so that "et" inside a word such as "Reset" is not one.
# regex: a search through free interface text for a word and its capitalised
# abbreviations, where whether a letter follows decides the match. No parser
# reads this text, and a string method cannot test the following letter.
_UNHEDGED_END_TIDAL = re.compile(
    r"(?i:end[\s-]?tidal)(?!-equivalent)|\bF?ET(?![A-Z])|\bEt(?![a-z])|\bet(?=[A-Z0-9])"
)

#: A word that negates a wake-up phrase. It hedges the phrase only when it
#: stands in the phrase's own clause and among the few words just before it,
#: because a negation's reach is short and ends at the end of its clause, as
#: NegEx ends it at the end of the sentence (`PL-86VL`). "Modelled, not
#: measured, predicted wake" is therefore not hedged: the "not" belongs to
#: "measured".
_NEGATIONS = frozenset({"not", "never", "no", "cannot"})

#: How many words before a wake-up phrase a negation may stand and still
#: govern it. "does not predict a time to wake" puts "not" three words before
#: the phrase. Four allows one more word, such as an adverb, and no more.
_NEGATION_REACH_WORDS = 4

#: Where a clause ends: a sentence's end, a semicolon, a colon, a comma, a dash
#: or a new line. Each is turned into a new line, and the text is split there.
_CLAUSE_ENDS_TO_NEW_LINE = str.maketrans(dict.fromkeys(".;:!?,\u2014\u2013", "\n"))

#: Phrases that would state a time to wake up as a prediction for this patient.
_WAKE_PREDICTIONS = (
    "time to wake",
    "time to awaken",
    "wake-up time",
    "wakeup time",
    "emergence time",
    "time to emergence",
    "predicted wake",
    "will wake",
)


def _unhedged_wake_predictions(text: str) -> list[str]:
    """Each wake-up prediction in `text` with no negation just before it in its own clause."""

    found: list[str] = []

    clauses = text.lower().replace(" - ", "\n").translate(_CLAUSE_ENDS_TO_NEW_LINE).split("\n")

    for clause in clauses:
        for phrase in _WAKE_PREDICTIONS:
            start = clause.find(phrase)
            while start != -1:
                words_before = clause[:start].split()[-_NEGATION_REACH_WORDS:]
                if _NEGATIONS.isdisjoint(word.strip("'\"()") for word in words_before):
                    found.append(phrase)
                start = clause.find(phrase, start + 1)

    return found


#: The index of each readout panel in the row, from the table the widgets are
#: built from, so a test names a compartment rather than a column number.
_READOUT_INDEX = {panel.quantity: index for index, panel in enumerate(READOUT_PANELS)}
_CLOCK_INDEX = _READOUT_INDEX[None]


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


# ------------------------------------------------------------------ helpers


def _fork_panel(view: SimulationView) -> ForkPanel:
    """The branch control in the dashboard's first Area that shows the branch View."""

    panel = next(v for v in view.layout_container.views() if isinstance(v, BranchView)).panel
    assert panel is not None, "the branch View holds no control: the dashboard has no case"

    return panel


def _marks_panel(view: SimulationView) -> BookmarksPanel:
    """The lists of marks in the dashboard's first Area that shows the bookmarks View."""

    panel = next(v for v in view.layout_container.views() if isinstance(v, BookmarksView)).panel
    assert panel is not None, "the bookmarks View has not drawn its first frame"

    return panel


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
    workspaces: WorkspaceSet = _EVERY_VIEW,
) -> SimulationView:
    """A dashboard over these runs, shown at the fixed size and presented once.

    The order is the one `main.py` follows: show, let the layout settle, then
    present, because the first frame reads the plot's laid-out width.
    """

    _delete_shown_views(application)
    view = SimulationView(controllers, case=case, workspaces=workspaces)
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


def _dashboard_of(run: RunView) -> SimulationView:
    """The dashboard that holds `run`."""

    dashboard = run.parent()
    assert isinstance(dashboard, SimulationView), "the run is on no dashboard"

    return dashboard


def _setting_controls(view: SimulationView) -> ParameterControlsView:
    """The setting controls View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, ParameterControlsView))


def _setting_row(run: RunView) -> RunDials:
    """A run's place in the first setting controls View of the dashboard that holds the run."""

    dashboard = _dashboard_of(run)

    return _setting_controls(dashboard).rows[dashboard.runs.index(run)]


def _dials(run: RunView) -> ParameterControls:
    """A run's four dials, in the first setting controls View of the dashboard that holds the run.

    A run holds no dial of its own. Each setting controls View builds the
    dials of every displayed run, and writes them from the run's
    presentation on every tick (`PL-RF2S`).
    """

    controls = _setting_row(run).controls
    assert controls is not None, "the View shows no dials for this run"

    return controls


def _accounting_panel(run: RunView) -> AccountingPanel:
    """A run's accounting panel, in the first accounting View of the run's dashboard."""

    dashboard = _dashboard_of(run)

    return _accounting(dashboard).panels[dashboard.runs.index(run)]


def _record_panels(run: RunView) -> tuple[QWidget, QWidget]:
    """The accounting and control-change panels of a run on the page, in that order.

    The accounting panel is in the sidebar beside the charts, where the
    accounting View builds it. The control-change panel is in the
    unconditional region (`PL-NWTM`). The control-change panel is found
    through the heading placed in it, not through the run's build method. So
    the tests below measure what the page holds, whatever that method
    returns. A second call to the method that built both panels used to build
    new panels with no parent and move the run's live labels into them
    (`PL-N67T`).
    """

    timeline = run._control_timeline_heading_text.parentWidget()
    assert timeline is not None, "the control-change heading is in no panel"

    return _accounting_panel(run), timeline


def _setting_sections(view: SimulationView) -> list[QWidget]:
    """Each run's setting controls, in the first Area that shows the parameter controls."""

    return list(_setting_controls(view).rows)


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
    comparison of two runs has to guard against. The thumb is pressed, moved
    and released, so the value is applied at the release as a reader's drag
    applies it (`PL-5B1N`).
    """

    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(slider_position(value, decimals))
    control.slider.setSliderDown(False)


def _set_fresh_gas_flow(run: RunView, flow_l_min: float) -> None:
    _drag(_dials(run)._fresh_gas_flow_slider, flow_l_min, FLOW_DISPLAY_DECIMALS)


def _set_delivered_percent(run: RunView, percent: float) -> None:
    _drag(_dials(run)._delivered_concentration_slider, percent, CONCENTRATION_DISPLAY_DECIMALS)


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

    selector = _fork_panel(view).point_selector

    return tuple(float(selector.itemData(index)) for index in range(selector.count()))


def _take_fork(view: SimulationView, instant_s: float) -> None:
    """Choose an offered instant in the branch control and press its button.

    `findData` returns the first entry at that instant. Where a mark is also
    set at the same instant, that entry is the recorded control event, because
    `fork_offer` lists the control event first.
    """

    panel = _fork_panel(view)
    index = panel.point_selector.findData(instant_s)
    assert index >= 0, f"the branch control does not offer {instant_s} s"
    panel.point_selector.setCurrentIndex(index)
    panel.take_button.click()


def _select_fork_entry(view: SimulationView, label: str) -> None:
    """Choose the branch control's entry that reads `label`, as a reader picks it by its words."""

    selector = _fork_panel(view).point_selector
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
        object.__setattr__(
            tissue, "perfusion_fraction", PerfusionFraction(tissue.perfusion_fraction * scale)
        )


def _with_the_tissue_fractions_put_back(controller: SimulationController) -> None:
    """Write back the reference adult's perfusion fractions, past the tissues' guard.

    The fractions are typed from `data/patients/reference_adult.json`. With
    them back, the settings record no longer refuses the tissue flows.
    """

    for tissue, fraction in zip(
        controller._state.uptake_system.patient.tissues, (0.76, 0.18, 0.06), strict=True
    ):
        object.__setattr__(tissue, "perfusion_fraction", PerfusionFraction(fraction))


def _failing_assembly(*args: object, **kwargs: object) -> NoReturn:
    """Stand in for `assemble_chart_frame` in a test where every frame must fail."""

    raise RuntimeError("this frame could not be assembled")


#: The names `_widget_attributes` gives a run's dials, the line shown in their
#: place and its accounting panel, which the Views of the run's dashboard hold.
_SETTING_CONTROLS: Final = "<setting controls>"
_NO_SETTING_CONTROLS_LINE: Final = "<setting row>.not_shown_text"
_ACCOUNTING_PANEL: Final = "<accounting panel>"


def _widget_attributes(run: RunView) -> dict[str, QWidget]:
    """Every widget a `RunView` holds as an attribute, by name, and each widget of a tuple.

    The run's four dials and its accounting panel are included too, each with
    every widget it holds. The run does not hold them. The first setting
    controls View and the first accounting View of the run's dashboard build
    them (`PL-RF2S`). They are named `<setting controls>` and
    `<accounting panel>`, so the lists below keep checking them. The dials
    are left out while the View shows none for the run. The line that the
    View shows in their place is always included, hidden or not.
    """

    widgets: dict[str, QWidget] = {}

    for name, value in vars(run).items():
        if isinstance(value, QWidget):
            widgets[name] = value
        elif isinstance(value, tuple) and value and all(isinstance(v, QWidget) for v in value):
            widgets.update({f"{name}[{index}]": item for index, item in enumerate(value)})

    panels: dict[str, QWidget | None] = {
        _SETTING_CONTROLS: _setting_row(run).controls,
        _ACCOUNTING_PANEL: _accounting_panel(run),
    }

    widgets[_NO_SETTING_CONTROLS_LINE] = _setting_row(run).not_shown_text

    for name, panel in panels.items():
        if panel is None:
            continue

        widgets[name] = panel
        widgets.update(
            {
                f"{name}.{inner}": item
                for inner, item in vars(panel).items()
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


def _accounting_reading(panel: AccountingPanel) -> dict[str, object]:
    return {
        "verdict": panel._agent_accounting_status_text.text(),
        "detail": panel._agent_accounting_detail_text.text(),
        "amounts": panel._agent_amounts_text.text(),
    }


def _accounting_of(step: SimulationSnapshot) -> dict[str, object]:
    """The accounting group as one completed step states it."""

    shown = accounting(step)

    return {"verdict": shown.status.text, "detail": shown.detail, "amounts": shown.amounts}


def _withheld_accounting() -> dict[str, object]:
    """The accounting group while it withholds the last frame's verdict and amounts."""

    return {
        "verdict": WITHHELD_ACCOUNTING.status.text,
        "detail": WITHHELD_ACCOUNTING.detail,
        "amounts": WITHHELD_ACCOUNTING.amounts,
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


def _no_setting(settings: object) -> NoReturn:
    """Stand in for `setting_readouts` in a test where no dial can be written."""

    raise ValueError("this control can offer no setting")


# How a stopped run states a dial that it refused (`PL-3B34`). This is written as
# a literal rather than read from the controller or `dashboard_frame`, so a change
# to the wording fails here.
_REFUSED_ON_A_STOPPED_RUN_TEMPLATE: Final = (
    "Setting refused — the {setting} setting cannot be changed on a stopped run, "
    "because no step will run under a new one"
)
_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN: Final = _REFUSED_ON_A_STOPPED_RUN_TEMPLATE.format(
    setting="cardiac output"
)


# --------------------------------------------------------------- bookmarks
#
# These tests cover the editing path end to end: a form filled in, a mark
# reaching both runs, and the listing a reader sees.
# `tests/unit/test_bookmarks.py` tests what a mark refuses, and
# `tests/unit/test_dashboard_frame.py` tests what a row says. These tests
# check that the dialog is wired to every run rather than to one (`PL-LPLD`).


def _opened_bookmark_dialog(view: SimulationView) -> BookmarkDialog:
    """The editor, opened the way the button opens it."""

    _marks_panel(view).edit_button.click()
    dialog = view._bookmark_dialog

    assert dialog is not None

    return dialog


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


# --- one readout block at a laptop's width (`PL-F2YS`) -----------------------

#: The laptop reference width at which `PL-J8K2` and `PL-84QX` measured the region.
_LAPTOP_WIDTH_PX = 1366


# ------------------------------------------------- Views in the dashboard

#: One Workspace that holds the three Views which name a run on each run's
#: panel: the accounting, the compartment schematic and the agent cost.
_RUN_PANEL_VIEWS = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Run panels"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.ROW,
                            (0.3, 0.4, 0.3),
                            (
                                Area(AreaId(1), AGENT_ACCOUNTING),
                                Area(AreaId(2), COMPARTMENT_SCHEMATIC),
                                Area(AreaId(3), AGENT_COST),
                            ),
                        )
                    ),
                ),
                AreaId(4),
            ),
        ),
    ),
    0,
)


def _dial_readings(row: RunDials) -> list[tuple[str, int]]:
    """Each dial of one run in a setting controls View: its value label and its thumb's place."""

    controls = row.controls
    assert controls is not None, "the View shows no dials for this run"

    return [
        (dial.value_label.text(), dial.slider.sliderPosition())
        for dial in controls.findChildren(ParameterSlider)
    ]
