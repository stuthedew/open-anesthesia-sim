"""The Views this build registers, each written to the View contract, in PySide6.

Each class here satisfies `app/view_contract.py`'s `View`, and its registry
entry in `app/view_registry.py` names the class as its factory. So any of them
can be built in any Area, any number of times, from a `ViewContext` alone.
Each one is drawn from the `ViewTick` that the adapter, `app/area_layout.py`,
hands it on every frame (`PL-TH35`).

- `ConcentrationView` is the concentration chart with its time-base control,
  legend and advisories. The legend states the 1 MAC and MAC-awake values,
  and the time axis's title states the window shown.
- `WashInView` is the F_A/F_I plot with its time-base control, captions,
  legend, per-run state lines and advisories. Its time axis's title states
  the window shown too.
- `AccountingView` is every displayed run's mass-balance panel. `docs/INTERFACE.md`
  § "Minimum displayed outputs" requires it to stay reachable in every layout,
  which the registry enforces.
- `ParameterControlsView` is every displayed run's setting controls.
- `CompartmentSchematicView` is every displayed run's compartment schematic:
  six containers filled to their tensions, each labelled with its name,
  tension and amount (`PL-RNYV`).
- `AgentCostView` is every displayed run's delivered agent, in millilitres of
  liquid equivalent or litres of vapour, as the reader's preferences say
  (`PL-B396`).

A View that shows a run's values builds its own widget for each displayed run.
On every tick it writes each widget whole from that run's `RunPresentation`
(`app/run_presentation.py`, `PL-RF2S`). A tick names every displayed run, on a
drawn frame and on a halt alike. So two Views of one kind show the same
values, a View chosen while no frame can be drawn still shows the runs, and
closing a View takes nothing with it. A widget belongs to the run whose
`run_id` its presentation carries, and it is deleted on the first tick that no
longer names that run.

Each chart View holds its own time window, set from its own control and
saved in its state (`PL-L59K`). So a chart writes the lines that depend on its
window, such as which traces are above the axis, from its own frame, one line
per run. On a tick that draws no frame, the tick gives each chart the last
frame drawn for its window as kept or as withheld (`run_presentation.ShownFrame`).
A chart that already shows the kept frame changes nothing. A chart that does
not yet show it, such as one chosen while no frame can be drawn, draws it,
unless the frame was sampled for a narrower plot. A withheld frame empties the
plot, the clinical references, the axis labels and the lines, and says why
(`dashboard_frame.WITHHELD_FRAME_TEXT`, `PL-RF2S`). So does a chart that holds
no frame and is handed none, and a kept frame too coarse for its plot
(`_withholds`).

These classes compute nothing that a reader interprets. Every caption comes
from `app/dashboard_frame.py`, or for the schematic from
`app/compartment_schematic.py`, or for the agent cost View from
`app/agent_cost.py`. Every drawn value comes from the tick's frame or from
one of the tick's presentations.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from functools import partial
from types import MappingProxyType
from typing import Final, cast

from PySide6.QtCore import QSignalBlocker, QSize, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.agent_cost import AGENT_COST_HEADING, UNIT_CHOICE_LABEL, UNIT_CHOICES
from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import (
    ChartTimeBase,
    ChartWindow,
    earlier_start_s,
    gridline_at_or_before,
    later_start_s,
    saved_time_base,
    saved_time_base_value,
)
from anesthesia_sim.app.compartment_schematic import SCHEMATIC_HEADING
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    CHART_CEILING_LABEL,
    CHART_HEADING,
    EARLIER_WINDOW_NAME,
    EARLIER_WINDOW_TEXT,
    FOLLOW_RUN_TEXT,
    INTERPRETATION_DISCLAIMER_TEXT,
    LATER_WINDOW_NAME,
    LATER_WINDOW_TEXT,
    NO_CASE_TO_BRANCH_TEXT,
    NO_TRACES_SHOWN_TEXT,
    SETTING_CONTROLS_NOT_SHOWN_TEXT,
    TIME_BASE_LABEL,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WITHHELD_FRAME_TEXT,
    WITHHELD_REFERENCE_TEXT,
    SettingReadout,
    compared_panel_heading,
    compartment_cap_notice,
    held_window_notice,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    off_scale_lines,
    run_label,
    time_axis_caption,
    unmarked_changes_lines,
    wash_in_state_lines,
)
from anesthesia_sim.app.formatting import AgentAmountUnit, ChartCeiling
from anesthesia_sim.app.preferences import Preferences
from anesthesia_sim.app.qt_agent_cost import RunAgentCost
from anesthesia_sim.app.qt_agent_price import PriceEntry, RefusedEntriesDiscard
from anesthesia_sim.app.qt_chart import (
    ChartCeilingSelector,
    ConcentrationChart,
    TimeBaseSelector,
    TraceLegend,
    WashInChart,
    WashInLegend,
)
from anesthesia_sim.app.qt_schematic import RunSchematic
from anesthesia_sim.app.qt_widgets import (
    BookmarksPanel,
    FocusedComboBox,
    FocusRing,
    ForkPanel,
    MarkButton,
    MarkEntry,
    styled_label,
)
from anesthesia_sim.app.run_presentation import (
    NotBuilt,
    RunPresentation,
    ShownFrame,
    ValuesStanding,
)
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls
from anesthesia_sim.app.stylesheets import (
    clear_scroll_area_stylesheet,
    panel_stylesheet,
    selector_stylesheet,
    transport_button_stylesheet,
)
from anesthesia_sim.app.theme import (
    CHART_KEY_LEAST_HEIGHT,
    CONTROL_BORDER_WIDTH,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PAGE_SPACING,
    PANEL_PADDING,
    PANEL_RADIUS,
    VIEW_HEADING_SPACING,
    VIEW_ROW_SPACING,
    WARNING,
)
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    UNREADABLE_STATE_TEXT,
    BranchPresentation,
    CasePresentation,
    FrameRequest,
    MarksPresentation,
    SavedState,
    ViewContext,
    ViewRequests,
    ViewScope,
    ViewTick,
    unreadable_state_text,
)
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.layout.run_identity import RunId

__all__ = [
    "AccountingView",
    "AgentCostView",
    "BookmarksView",
    "BranchView",
    "CompartmentSchematicView",
    "ConcentrationView",
    "ParameterControlsView",
    "WashInView",
]

#: The saved-state version for the Views here that have no setting of their
#: own, which are the accounting View, the setting controls View, the
#: compartment schematic, the agent cost View, the bookmarks View and the branch
#: View. The agent cost View's unit
#: is the reader's preference, not the View's own setting (`PL-B396`). Each of
#: them saves only this version and nothing else.
_STATE_VERSION: Final = 1

#: The version of a chart View's saved state. Version 2 added the chart's
#: time window under `_TIME_BASE_KEY` (`PL-L59K`). Version 1 held no setting,
#: so a chart treats a version 1 state as the default window and loses nothing.
_CHART_STATE_VERSION: Final = 2
_SETTINGLESS_CHART_STATE_VERSION: Final = 1

#: The key under which a chart saves its window, in the form
#: `chart_time_base.saved_time_base_value` writes.
_TIME_BASE_KEY: Final = "time_base_s"

#: The key under which the concentration chart saves the top of its axis, as
#: its value in MAC (`PL-K1VH`). It sits in the chart's version 2 state beside
#: the window. A state saved before the key existed has none, and the chart
#: then opens at the standard top, which is the top it always had.
_CEILING_KEY: Final = "ceiling_mac"

_CONCENTRATION_VIEW_NAME: Final = "concentrationView"
_WASH_IN_VIEW_NAME: Final = "washInView"
_WASH_IN_PINNED_ROW_NAME: Final = "washInPinnedRow"
_SCHEMATIC_VIEW_NAME: Final = "compartmentSchematicView"
_AGENT_COST_VIEW_NAME: Final = "agentCostView"
_BOOKMARKS_VIEW_NAME: Final = "bookmarksView"
_BRANCH_VIEW_NAME: Final = "branchView"


class _RunWidgets[W: QWidget]:
    """One widget per displayed run, in drawing order, in a column of their own.

    A View calls `follow` with each tick's runs. A run still displayed keeps
    its widget, a new run gets one built, and the widget of a run no longer
    displayed is deleted. A run's widget is found by the run's `run_id`. So a
    branch taken or removed changes only its own widget, and a slider being
    dragged in another run's widget is not rebuilt under the pointer.

    Args:
        build: Builds the widget for a run that has none, from the run's
            presentation in the tick that first names it.
        spacing: The gap between two runs' widgets, in pixels.
    """

    def __init__(self, build: Callable[[RunPresentation], W], spacing: int) -> None:
        self._build = build
        self.holder = QWidget()
        self._column = QVBoxLayout(self.holder)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.setSpacing(spacing)
        self._widgets: list[tuple[RunId, W]] = []

    @property
    def widgets(self) -> tuple[W, ...]:
        """The widgets shown now, one per displayed run, in drawing order."""

        return tuple(widget for _, widget in self._widgets)

    def follow(self, runs: tuple[RunPresentation, ...]) -> None:
        """Show one widget for each of `runs`, in their order."""

        if [run_id for run_id, _ in self._widgets] == [run.run_id for run in runs]:
            return

        kept: list[tuple[RunId, W]] = []

        for run in runs:
            held = next((widget for owner, widget in self._widgets if owner == run.run_id), None)
            kept.append((run.run_id, self._build(run) if held is None else held))

        for _, widget in self._widgets:
            self._column.removeWidget(widget)

            if not any(widget is still for _, still in kept):
                widget.hide()
                widget.deleteLater()

        # Raising each widget in turn also puts the widget tree's children in
        # drawing order (https://doc.qt.io/qt-6/qobject.html#children). A
        # widget built again would otherwise sit after the later runs' widgets
        # in the tree, which is the order Tab reads (`PL-B45W`).
        for _, widget in kept:
            self._column.addWidget(widget)
            widget.show()
            widget.raise_()

        self._widgets = kept

    def drop_absent(self, runs: tuple[RunPresentation, ...]) -> None:
        """Delete the widget of each run that `runs` does not name, and change nothing else."""

        named = {run.run_id for run in runs}

        for run_id, widget in self._widgets:
            if run_id not in named:
                self._column.removeWidget(widget)
                widget.hide()
                widget.deleteLater()

        self._widgets = [(run_id, widget) for run_id, widget in self._widgets if run_id in named]


class _RunLines:
    """One conditional line per displayed run, written from a chart's own frame.

    One such line says which traces are above the axis. `show` takes a
    frame's runs and one entry for each run, and an entry of None hides that
    run's line. `drop_absent` takes the runs of a tick that has no frame. It
    deletes the line of each run that the tick does not name, and it leaves
    every other line as the last frame wrote it. So a dropped run's line
    never stays beside the runs still displayed, even while no frame can be
    drawn.
    """

    def __init__(self, color: str, *, italic: bool) -> None:
        self._lines = _RunWidgets(
            lambda _run: styled_label(
                "", color=color, size_px=METRIC_QUALIFIER_SIZE, italic=italic, wrap=True
            ),
            VIEW_ROW_SPACING,
        )
        self.holder = self._lines.holder

    @property
    def lines(self) -> tuple[QLabel, ...]:
        """The line shown for each displayed run, in drawing order."""

        return self._lines.widgets

    def show(self, runs: tuple[RunPresentation, ...], texts: Sequence[str | None]) -> None:
        """Write one line for each of `runs`, hiding each line whose entry is None.

        Raises:
            ValueError: If there is not one entry for each run.
        """

        if len(texts) != len(runs):
            raise ValueError(f"{len(texts)} line(s) were given for {len(runs)} run(s)")

        self._lines.follow(runs)

        for line, text in zip(self._lines.widgets, texts, strict=True):
            line.setText(text or "")
            line.setHidden(text is None)

    def drop_absent(self, runs: tuple[RunPresentation, ...]) -> None:
        """Delete the line of each run that `runs` does not name."""

        self._lines.drop_absent(runs)


def _read_time_base(saved: object) -> tuple[ChartTimeBase | None, str | None]:
    """Return the window that a chart's saved state holds, and a notice if it could not be read.

    When nothing was saved, or the state is version 1, which held no setting,
    the result is the default window, "Fit run". A version 2 state holds its
    window under `_TIME_BASE_KEY`. For anything else, the function returns the
    default window with `UNREADABLE_STATE_TEXT`, so the chart says that it is
    not showing what was saved (Q4).
    """

    if (
        isinstance(saved, Mapping)
        and saved.keys() == {STATE_VERSION_KEY}
        and type(saved[STATE_VERSION_KEY]) is int
        and saved[STATE_VERSION_KEY] == _SETTINGLESS_CHART_STATE_VERSION
    ):
        return None, None

    notice = unreadable_state_text(saved, _CHART_STATE_VERSION)

    if notice is not None or not isinstance(saved, Mapping):
        return None, notice

    try:
        return saved_time_base(saved.get(_TIME_BASE_KEY)), None
    except ValueError:
        return None, UNREADABLE_STATE_TEXT


def _read_ceiling(saved: object) -> tuple[ChartCeiling, str | None]:
    """Return the axis top a concentration chart saved, and a notice if it could not be read.

    A state with no `_CEILING_KEY` gives the standard top. A value that is not
    one of `ChartCeiling`'s tops gives the standard top with
    `UNREADABLE_STATE_TEXT`, so the chart says that it is not showing what was
    saved (Q4). A state that `_read_time_base` cannot read is that function's
    to report, so it gives the standard top and no second notice.
    """

    if (
        not isinstance(saved, Mapping)
        or _CEILING_KEY not in saved
        or unreadable_state_text(saved, _CHART_STATE_VERSION) is not None
    ):
        return ChartCeiling.STANDARD, None

    value = saved[_CEILING_KEY]

    # `type` rather than `isinstance`, so that True does not pass for 1.
    if type(value) not in (int, float):
        return ChartCeiling.STANDARD, UNREADABLE_STATE_TEXT

    try:
        return ChartCeiling(value), None
    except ValueError:
        return ChartCeiling.STANDARD, UNREADABLE_STATE_TEXT


class _TimeWindow:
    """A chart View's own time window, with the controls that set and move it, and its saved form.

    Each chart holds its window (project owner, 2026-10-19, `PL-L59K`). The
    window starts from the saved state, or from "Fit run" where none was
    saved. A reader's pick sets it and asks for a frame at once. The control
    shows the window that the plot last drew, so where a frame fails, the
    control goes on naming what is on the plot (`PL-G3K7`).

    At a chosen width, the arrows either side of the selector move the window
    one gridline earlier or later (`PL-Z7LY`). A window moved earlier holds
    still while the run goes on, and `held_row` says so and offers one click
    back to following the run. A step later that reaches the run's own window
    follows the run again (`chart_time_base.later_start_s`). So does "Fit
    run", which shows the whole run, and a Reset or an agent change, which
    takes the run back before the held window (`chart_time_base.held_window`).
    The held edge is not saved, so a chart that is built again follows the
    run, and a reopened layout never opens on a stale window.

    Args:
        context: What the chart View is built from.

    Attributes:
        selector: The control that sets the window's width.
        control: The selector between the two arrows, as one item for a row.
        held_row: The line that says what a held window shows and where the
            run is now, with the button that follows the run again. It is
            hidden while the window follows the run.
        time_base: The width the chart draws next, or None for "Fit run".
        held_start_s: The held window's left edge the chart draws next, or
            None while it follows the run.
        notice_text: The notice to show because the saved state could not be
            read, or None.
    """

    _NOT_DRAWN: Final = object()

    def __init__(self, context: ViewContext) -> None:
        self.time_base, self.notice_text = _read_time_base(context.saved_state)
        self.held_start_s: CaseInstant | None = None
        self._drawn: object = self._NOT_DRAWN
        self._frame: ChartFrame | None = None
        self._request_frame = context.requests.frame
        self.selector = TimeBaseSelector()
        self.selector.show_time_base(self.time_base)
        self.selector.time_base_requested.connect(self._choose)
        self.earlier_button = _step_button(EARLIER_WINDOW_TEXT, EARLIER_WINDOW_NAME)
        self.earlier_button.clicked.connect(self._step_earlier)
        self.later_button = _step_button(LATER_WINDOW_TEXT, LATER_WINDOW_NAME)
        self.later_button.clicked.connect(self._step_later)
        self.follow_button = _step_button(FOLLOW_RUN_TEXT, FOLLOW_RUN_TEXT)
        self.follow_button.clicked.connect(self._follow)
        self.control = QWidget()
        steps = QHBoxLayout(self.control)
        steps.setContentsMargins(0, 0, 0, 0)
        steps.setSpacing(VIEW_HEADING_SPACING)
        steps.addWidget(self.earlier_button)
        steps.addWidget(self.selector)
        steps.addWidget(self.later_button)
        # The line is conditional text: it shows only while the reader holds
        # the window, when the plot shows the past and every readout shows
        # the present. It is the stale-state misreading that `CLAUDE.md`'s
        # safety standard names, so it is drawn in the warning colour, as the
        # line naming traces above the axis is.
        self.held_text = styled_label(
            "", color=WARNING, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self.held_row = QWidget()
        held = QHBoxLayout(self.held_row)
        held.setContentsMargins(0, 0, 0, 0)
        held.setSpacing(VIEW_HEADING_SPACING)
        held.addWidget(self.held_text, 1)
        held.addWidget(self.follow_button)
        self.held_row.setHidden(True)
        self._show_steps(None)

    def request(self, width_px: float) -> FrameRequest:
        """Return the frame that the chart asks for: this window, sampled for `width_px`."""

        return FrameRequest(self._window(), width_px)

    def drew(self, frame: ChartFrame) -> None:
        """Note the window `frame` was drawn at, and show it in the controls.

        A frame that follows the run ends a hold, so a held window that a
        Reset or a step later brought up to the run is not held again later.
        """

        self.held_start_s = frame.held_start_s
        drawn = ChartWindow(None if frame.fitted else frame.time_base, frame.held_start_s)
        self._drawn = drawn
        self._frame = frame
        self.selector.show_time_base(drawn.time_base)
        self._show_steps(frame)

    @property
    def owes_a_frame(self) -> bool:
        """Whether the window was changed since the chart last drew."""

        return self._drawn is self._NOT_DRAWN or self._drawn != self._window()

    def saved_state(self) -> SavedState:
        return MappingProxyType(
            {
                STATE_VERSION_KEY: _CHART_STATE_VERSION,
                _TIME_BASE_KEY: saved_time_base_value(self.time_base),
            }
        )

    def _window(self) -> ChartWindow:
        return ChartWindow(self.time_base, None if self.time_base is None else self.held_start_s)

    def withheld(self) -> None:
        """Forget the drawn window when the chart's frame is withheld, and offer nothing.

        A withheld chart shows no window, so a held line naming one, and an
        arrow stepping from it, would describe a plot that is no longer on
        screen.
        """

        self._frame = None
        self._show_steps(None)

    def _show_steps(self, frame: ChartFrame | None) -> None:
        """Offer each step that the drawn window allows, and say whether it is held.

        Neither arrow moves a fitted window, which already shows the whole
        run, or a preview's, which is centred on the run's reach while a
        drag is held. Nothing lies before a window that starts at zero, and
        nothing after one that follows the run.

        A control that stops being offered while it has the keyboard focus
        hands the focus to the time-base selector. Otherwise Qt would move it
        to the next control in the page, and a keyboard user pressing the
        same key again would act on a control they did not choose.
        """

        movable = (
            frame is not None
            and not frame.fitted
            and not any(run.preview is not None for run in frame.runs)
        )
        notice = None if frame is None else held_window_notice(frame)
        offered = (
            (self.earlier_button, movable and frame is not None and frame.start_s > 0.0),
            (self.later_button, movable and frame is not None and frame.held),
            (self.follow_button, notice is not None),
        )

        if any(button.hasFocus() and not shown for button, shown in offered):
            self.selector.setFocus(Qt.FocusReason.OtherFocusReason)

        self.earlier_button.setEnabled(offered[0][1])
        self.later_button.setEnabled(offered[1][1])
        self.held_text.setText(notice or "")
        self.held_row.setHidden(notice is None)

    def _choose(self, time_base: ChartTimeBase | None) -> None:
        self.time_base = time_base

        # A held window keeps its place at another width, moved back onto
        # that width's gridlines so both edges stay on labelled times.
        if time_base is not None and self.held_start_s is not None:
            self.held_start_s = gridline_at_or_before(time_base, self.held_start_s)

        self._request_frame()

        # A frame that drew has already shown the pick. One that failed drew
        # nothing, so the control goes back to the window still on the plot.
        if self._drawn is not self._NOT_DRAWN:
            self.selector.show_time_base(cast(ChartWindow, self._drawn).time_base)

    def _step_earlier(self) -> None:
        if self._frame is None or self._frame.start_s <= 0.0:
            return

        self.held_start_s = earlier_start_s(self._frame.time_base, self._frame.start_s)
        self._request_frame()

    def _step_later(self) -> None:
        if self._frame is None or not self._frame.held:
            return

        frame = self._frame
        self.held_start_s = later_start_s(frame.time_base, frame.start_s, frame.newest_instant_s)
        self._request_frame()

    def _follow(self) -> None:
        self.held_start_s = None
        self._request_frame()


def _step_button(text: str, name: str) -> QPushButton:
    """Return a button that moves or releases a chart's window, named for what it does.

    It is drawn as the run controls are, so its label stays readable under
    a dark host appearance and when it is unavailable (`PL-DHBX`), and it
    shows a ring while it has the keyboard focus (`PL-63FQ`).
    """

    button = QPushButton(text)
    button.setAccessibleName(name)
    button.setToolTip(name)
    button.setStyleSheet(transport_button_stylesheet())
    FocusRing(button, radius=PANEL_RADIUS, inset=CONTROL_BORDER_WIDTH)

    return button


def _state_notice_for(context: ViewContext) -> QLabel:
    """Return `_state_notice` for a View whose saved state holds only its version."""

    return _state_notice(unreadable_state_text(context.saved_state, _STATE_VERSION))


def _state_notice(text: str | None) -> QLabel:
    """Return the line a View shows while drawn with defaults because its saved state is unreadable.

    The line is conditional text. It is hidden unless the saved state could
    not be read (Q4).
    """

    notice = styled_label(
        text or "", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
    )
    notice.setHidden(text is None)

    return notice


def _saved_state() -> SavedState:
    return MappingProxyType({STATE_VERSION_KEY: _STATE_VERSION})


def _panel_column(view: QWidget, object_name: str) -> QVBoxLayout:
    """Give `view` the panel surface, and return the column its rows go in."""

    view.setObjectName(object_name)
    view.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    view.setStyleSheet(panel_stylesheet(object_name))
    column = QVBoxLayout(view)
    column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
    column.setSpacing(VIEW_ROW_SPACING)

    return column


def _labelled_control(label: str, control: QWidget) -> QWidget:
    """Return `control` with its muted label before it, as one item that a row wraps whole."""

    item = QWidget()
    pair = QHBoxLayout(item)
    pair.setContentsMargins(0, 0, 0, 0)
    pair.setSpacing(VIEW_HEADING_SPACING)
    pair.addWidget(styled_label(label, color=MUTED))
    pair.addWidget(control)

    return item


def _panel_row(label: QLabel, object_name: str) -> QWidget:
    """Return a row that holds `label` on the panel surface, inset by the panel's padding.

    A View's pinned row sits outside the View's own panel, between the Area's
    header and the box that scrolls the View. This gives the row the same
    surface and the same left edge as the panel's text below it.
    """

    row = QWidget()
    row.setObjectName(object_name)
    row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    row.setStyleSheet(panel_stylesheet(object_name))
    line = QHBoxLayout(row)
    line.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, 0)
    line.addWidget(label)

    return row


def _bare_column(view: QWidget) -> QVBoxLayout:
    """Return a column with no margins, for a View whose rows are panels of their own."""

    column = QVBoxLayout(view)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(PAGE_SPACING)

    return column


class _KeyScroll(QScrollArea):
    """Holds the rows a reader reads a plot with, and scrolls them where the View is too short.

    The rows are the lines that qualify a chart View's plot, and its legend.
    The box asks for the height that the rows need at the width the box has,
    and takes no more. In a View too short for the rows
    and the plot, the box is squeezed to `theme.CHART_KEY_LEAST_HEIGHT`. The
    reader then scrolls the rows inside the box, and the plot keeps its place
    under them (`PL-CBYS`).

    Args:
        rows: The rows, in the order they are read.
    """

    def __init__(self, rows: Sequence[QWidget]) -> None:
        super().__init__()
        self._body = QWidget()
        column = QVBoxLayout(self._body)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)

        for row in rows:
            column.addWidget(row)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumHeight(CHART_KEY_LEAST_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # The box paints nothing of its own, so the View's panel shows behind
        # the rows. `setWidget` would otherwise fill the rows' background from
        # the palette.
        self.setStyleSheet(clear_scroll_area_stylesheet())
        self.viewport().setAutoFillBackground(False)
        self.setWidget(self._body)
        self._body.setAutoFillBackground(False)
        FocusRing(self)

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """The widest row's least width with the scroll bar beside it, and the box's least height.

        The box never scrolls sideways, so a View narrower than its widest row
        would cut that row off at the right. A `QScrollArea`'s own least width
        counts only its scroll bar, and the View's least width, which sets the
        Area's, would then leave out every row in the box (`PL-CBYS`).
        """

        least = super().minimumSizeHint()
        width = self._body.minimumSizeHint().width() + self.verticalScrollBar().sizeHint().width()

        return QSize(max(least.width(), width), least.height())

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """The rows' width, and the height the rows need at the width the box has."""

        hint = self._body.sizeHint()
        height = self._body.heightForWidth(self.viewport().width())

        return QSize(hint.width(), hint.height() if height < 0 else height)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        # The height that the rows need depends on the box's width.
        self.updateGeometry()


def _withholds(shown: ShownFrame | None, drawn: ChartFrame | None, width_px: float) -> bool:
    """Whether a chart shows the withheld state on this tick: an empty plot that says why.

    A withheld frame is always withheld. A kept frame is withheld from a
    chart in two more cases (blind review of `PL-RF2S`, pass 3):

    1. No frame was kept for the chart's window, and the chart holds no
       frame, as when it was chosen during a halt. Left as built, it would
       show a 1 MAC line and band at 0 and default numbers under its axis
       titles.
    2. The chart does not show the kept frame yet, and that frame was
       sampled for a narrower plot than this one. Drawn here, its chords
       would be wider than a pixel (`PL-GS3R`). The frame sampled while no
       chart is shown is the narrowest.

    A chart that holds a frame and is handed no kept frame for its window
    keeps its plot, and its control names the window that plot shows
    (`PL-G3K7`).

    Args:
        shown: The tick's frame for the chart's window, or None.
        drawn: The frame the chart's plot was drawn from, or None. A chart
            at a top other than the standard one draws a copy of that frame.
        width_px: The width of the chart's plot, in logical pixels.
    """

    if shown is None or shown.standing is ValuesStanding.DRAWN:
        return False

    if shown.standing is ValuesStanding.WITHHELD:
        return True

    if shown.frame is None:
        return drawn is None

    return shown.frame is not drawn and width_px > shown.frame.plot_width_px


def _frame_to_draw(shown: ShownFrame | None, drawn: ChartFrame | None) -> ChartFrame | None:
    """Return the frame a chart must draw from `shown`, or None where it draws nothing.

    A frame drawn this tick is always drawn. A kept frame is drawn only by a
    chart that does not already show it, such as one chosen while no frame
    can be drawn. So a dial dragged between two render ticks, which hands
    every View the runs with no frame, leaves the plots as they are until the
    render tick draws (`PL-018`, `PL-R2YM`).

    Args:
        shown: The tick's frame for the chart's window.
        drawn: The frame the chart shows now, or None.
    """

    if shown is None or shown.frame is None:
        return None

    if shown.standing is ValuesStanding.KEPT and shown.frame is drawn:
        return None

    return shown.frame


def _withheld_frame_notice() -> QLabel:
    """Return the line a chart shows, hidden until its frame is withheld."""

    notice = styled_label(
        WITHHELD_FRAME_TEXT, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
    )
    notice.setHidden(True)

    return notice


def _shown_run_names(runs: tuple[RunPresentation, ...]) -> tuple[str, ...]:
    """Return what each of `runs` is called in a chart's legend, from its identity."""

    return tuple(run_label(run.run_id) for run in runs)


class ConcentrationView(QWidget):
    """The concentration chart, with everything a reader needs to read it.

    The View holds the heading, the time-base and axis-top controls, and the
    legend.
    The legend's entries for the 1 MAC line and the MAC-awake band state
    their values, and the time axis's title states the window shown
    (`PL-K4CZ`). It also
    holds advisories that appear only when they apply. Above the plot, a
    line for each run names that run's traces that are above the axis, and
    another says how many of its control changes in the window could not be
    marked. Then comes the plot itself. Everything above the
    plot is a label, a legend entry or a reference value rather than a
    sentence (`PL-6580`, `PL-F9TQ`).

    In an Area too short for all of that, the plot shrinks to
    `theme.CHART_LEAST_HEIGHT`. The legend then scrolls in a box of its own
    above the plot
    (`_KeyScroll`). The advisories stay outside the box, so a reader sees one
    as soon as it applies (`PL-CBYS`).

    The time window is the View's own, set from its control and saved in its
    state (`PL-L59K`). So is the top of the axis, which the reader chooses
    from `ChartCeiling` (`PL-K1VH`). The dashboard assembles each frame at the
    standard top, so that every chart showing one window shares its frame,
    and this View draws it at its own top. The legend shows the dashboard's compartment selection
    and asks for a change through the context's requests, so two of these
    Views show the same compartments (`PL-VN6M`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The compartment legend.
        time_base_selector: The control that sets the window's width.
        ceiling_selector: The control that sets the top of the axis.
    """

    scope = ViewScope.RUNS

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self._window = _TimeWindow(context)
        self._ceiling, ceiling_notice = _read_ceiling(context.saved_state)
        # The top that the plot shows now, and the frame it was drawn from
        # before this View set its top. A kept frame is drawn again only when
        # it is not that frame, or when the reader has chosen another top.
        self._drawn_ceiling: ChartCeiling | None = None
        self._source: ChartFrame | None = None
        self._request_frame = context.requests.frame
        self.ceiling_selector = ChartCeilingSelector()
        self.ceiling_selector.show_ceiling(self._ceiling)
        self.ceiling_selector.ceiling_requested.connect(self._choose_ceiling)
        self.chart = ConcentrationChart()
        self.legend = TraceLegend()
        self.legend.compartment_requested.connect(context.requests.compartment)
        self.time_base_selector = self._window.selector
        self.hidden_traces_text = styled_label(
            NO_TRACES_SHOWN_TEXT, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self.hidden_traces_text.setHidden(True)
        # This text appears only when it applies. It passes the test in
        # `.claude/rules/ui-reader.md` for when text may be a sentence. It says
        # why boxes that the reader checked have become unchecked, and no
        # label, unit or axis title can say that.
        self.capped_traces_text = styled_label(
            "", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self.capped_traces_text.setHidden(True)
        self.state_notice = _state_notice(self._window.notice_text or ceiling_notice)
        self.withheld_text = _withheld_frame_notice()
        self.off_scale = _RunLines(WARNING, italic=True)
        self.unmarked_changes = _RunLines(MUTED, italic=True)

        column = _panel_column(self, _CONCENTRATION_VIEW_NAME)
        column.addWidget(styled_label(CHART_HEADING, color=INK, bold=True, wrap=True))
        # The controls take a row of their own under the heading. Beside the
        # heading they would wrap it onto a second line at 1366 by 768, and
        # the View would grow taller than the Induction Workspace has room for.
        controls = QHBoxLayout()
        controls.setSpacing(VIEW_HEADING_SPACING)
        controls.addWidget(_labelled_control(TIME_BASE_LABEL, self._window.control))
        controls.addWidget(_labelled_control(CHART_CEILING_LABEL, self.ceiling_selector))
        controls.addStretch(1)
        column.addLayout(controls)
        column.addWidget(self._window.held_row)
        column.addWidget(self.state_notice)
        column.addWidget(_KeyScroll((self.legend,)))
        column.addWidget(self.withheld_text)
        column.addWidget(self.hidden_traces_text)
        column.addWidget(self.capped_traces_text)
        column.addWidget(self.off_scale.holder)
        column.addWidget(self.unmarked_changes.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, then write the legend, the control and the captions from it.

        The legend and the time-base control are told what the plot drew only
        after the plot has drawn it. So where drawing fails, they go on naming
        what is still on the plot (`PL-G3K7`). The 1 MAC line's and the
        MAC-awake band's entries are written from the frame that placed them.

        A kept frame that the plot already shows changes nothing, apart from
        deleting the lines of runs that the tick no longer names. A withheld
        frame empties the plot and the references, deletes every run's
        lines, names the runs the tick holds now, and shows why
        (`run_presentation.shown_without_a_frame`). A kept frame is withheld
        in the same way in the cases that `_withholds` names.
        """

        shown = tick.frame

        # At a top other than the standard one the plot holds a copy of the
        # shared frame, so whether the plot already shows the kept frame is
        # read from the frame the copy was made from.
        if _withholds(shown, self._source, self.chart.plot_width_px()):
            self._withhold(tick)
            return

        source = _frame_to_draw(
            shown, self._source if self._drawn_ceiling is self._ceiling else None
        )

        if source is None or shown is None:
            self.off_scale.drop_absent(tick.runs)
            self.unmarked_changes.drop_absent(tick.runs)
            return

        # A frame at this View's top already is drawn as it is, so Views at the
        # standard top still share one frame object with the other charts.
        frame = (
            source if source.ceiling is self._ceiling else replace(source, ceiling=self._ceiling)
        )
        self.chart.draw(frame)
        self._drawn = True
        self._source = source
        self._drawn_ceiling = self._ceiling
        self.ceiling_selector.show_ceiling(self._ceiling)
        self._window.drew(frame)
        self.withheld_text.setHidden(True)
        # Show the run names before the selection. Then, when the legend is told
        # about a second run's curves, it already knows what that run is called
        # (`PL-7Z84`).
        self.legend.show_run_names(tuple(run.label for run in frame.runs))
        self.legend.show_selection(shown.selection)
        self.chart.show_time_window(time_axis_caption(frame))
        self.legend.show_references(mac_reference_caption(frame), mac_awake_caption(frame))
        self.hidden_traces_text.setHidden(not no_traces_shown(frame))
        cap_notice = compartment_cap_notice(frame)
        self.capped_traces_text.setText(cap_notice or "")
        self.capped_traces_text.setHidden(cap_notice is None)
        self.off_scale.show(tick.runs, off_scale_lines(frame))
        self.unmarked_changes.show(tick.runs, unmarked_changes_lines(frame))

    def _withhold(self, tick: ViewTick) -> None:
        """Empty the plot, the references and the lines, and say why."""

        self.chart.withhold()
        self._window.withheld()
        self._source = None
        self.withheld_text.setHidden(False)
        self.legend.show_run_names(_shown_run_names(tick.runs))
        self.legend.show_selection(tick.selection)
        self.legend.show_references(WITHHELD_REFERENCE_TEXT, WITHHELD_REFERENCE_TEXT)
        self.hidden_traces_text.setHidden(True)
        self.capped_traces_text.setHidden(True)
        self.off_scale.drop_absent(())
        self.unmarked_changes.drop_absent(())

    def _choose_ceiling(self, ceiling: ChartCeiling) -> None:
        self._ceiling = ceiling
        self._request_frame()

        # A frame that drew has already shown the pick. One that failed drew
        # nothing, so the control goes back to the top still on the plot.
        if self._drawn_ceiling is not None:
            self.ceiling_selector.show_ceiling(self._drawn_ceiling)

    @property
    def owes_a_frame(self) -> bool:
        return (
            not self._drawn
            or self.chart.owes_a_frame
            or self._window.owes_a_frame
            or self._drawn_ceiling is not self._ceiling
        )

    def frame_request(self) -> FrameRequest | None:
        return self._window.request(self.chart.plot_width_px())

    def save_state(self) -> SavedState:
        return MappingProxyType({**self._window.saved_state(), _CEILING_KEY: self._ceiling.value})

    def painted_strings(self) -> tuple[str, ...]:
        return self.chart.axis_titles()


class WashInView(QWidget):
    """The F_A/F_I plot, with its heading, its window, what it shows, its legend and lines per run.

    In an Area too short for all of it, the plot shrinks to
    `theme.WASH_IN_CHART_LEAST_HEIGHT`, and the rows from the line that says
    what the plot shows to the legend scroll in a box above the plot, as the concentration
    chart's do (`_KeyScroll`). The line that says its values are model
    outputs is the View's `pinned_row`: its Area shows it above the box that scrolls the View, so
    the words are on screen wherever any part of the plot is (`PL-26BZ`).

    Its time window is its own, as the concentration chart's is (`PL-L59K`).
    Where both show the same window, the dashboard hands both the same frame,
    so the two plots draw the same instants (`PL-9LNF`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The plot's legend.
        modelled_label: The line that says the plot's values are model
            outputs, not measurements.
        pinned_row: The row that holds `modelled_label`, which the View's
            Area keeps on screen above the View's scroll box.
        time_base_selector: The control that sets the window's width.
    """

    scope = ViewScope.RUNS

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self._window = _TimeWindow(context)
        self.chart = WashInChart()
        self.legend = WashInLegend()
        self.time_base_selector = self._window.selector
        self.state_notice = _state_notice(self._window.notice_text)
        self.withheld_text = _withheld_frame_notice()
        self.states = _RunLines(MUTED, italic=False)
        self.unmarked_changes = _RunLines(MUTED, italic=True)

        column = _panel_column(self, _WASH_IN_VIEW_NAME)
        heading = QHBoxLayout()
        heading.setSpacing(VIEW_HEADING_SPACING)
        heading.addWidget(styled_label(WASH_IN_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(TIME_BASE_LABEL, color=MUTED))
        heading.addWidget(self._window.control)
        column.addLayout(heading)
        column.addWidget(self._window.held_row)
        column.addWidget(self.state_notice)
        # The safety standard requires the plot to say it is modelled
        # (`PL-F9TQ`). The View's Area keeps the row above the box that
        # scrolls the View, so the words are on screen wherever any part of
        # the plot is (`PL-26BZ`). The words are the ones every other View
        # uses for the same fact, and the row is drawn on the panel surface so
        # it reads as part of this View (`PL-T8DF`).
        self.modelled_label = styled_label(INTERPRETATION_DISCLAIMER_TEXT, color=MUTED)
        self.pinned_row = _panel_row(self.modelled_label, _WASH_IN_PINNED_ROW_NAME)
        column.addWidget(
            _KeyScroll(
                (styled_label(WASH_IN_DENOMINATOR_TEXT, color=MUTED, wrap=True), self.legend)
            )
        )
        column.addWidget(self.withheld_text)
        column.addWidget(self.states.holder)
        column.addWidget(self.unmarked_changes.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, then write the legend, the control and the lines from it.

        A kept frame and a withheld one are handled as `ConcentrationView.refresh`
        handles them. Each run's state line is written from the frame alone,
        which holds that run's reading beside its name (`wash_in_state_lines`).
        """

        shown = tick.frame

        if _withholds(shown, self.chart.frame, self.chart.plot_width_px()):
            self.chart.withhold()
            self._window.withheld()
            self.withheld_text.setHidden(False)

            if tick.runs:
                self.legend.show_run_names(_shown_run_names(tick.runs))

            self.states.drop_absent(())
            self.unmarked_changes.drop_absent(())
            return

        frame = _frame_to_draw(shown, self.chart.frame)

        if frame is None:
            self.states.drop_absent(tick.runs)
            self.unmarked_changes.drop_absent(tick.runs)
            return

        self.chart.draw(frame)
        self._drawn = True
        self._window.drew(frame)
        self.withheld_text.setHidden(True)
        self.legend.show_run_names(tuple(run.label for run in frame.runs))
        self.chart.show_time_window(time_axis_caption(frame))
        self.states.show(tick.runs, wash_in_state_lines(frame))
        self.unmarked_changes.show(tick.runs, unmarked_changes_lines(frame))

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn or self.chart.owes_a_frame or self._window.owes_a_frame

    def frame_request(self) -> FrameRequest | None:
        return self._window.request(self.chart.plot_width_px())

    def save_state(self) -> SavedState:
        return self._window.saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return self.chart.axis_titles()


class _RunPanelsView[W: QWidget](QWidget):
    """A View that shows one widget per displayed run, one above the next, with no frame.

    On every tick, with a frame or without one, the View shows one widget
    for each run that the tick names, and writes each widget whole from
    that run's presentation. It counts as drawn after either kind of tick.

    Args:
        context: What the View is built from.
        build: Builds one run's widget from the run's presentation.
        write: Writes one run's widget whole from the run's presentation.
    """

    scope = ViewScope.RUNS

    def __init__(
        self,
        context: ViewContext,
        build: Callable[[RunPresentation], W],
        write: Callable[[W, RunPresentation], None],
    ) -> None:
        super().__init__()
        self._write = write
        self._drawn = False
        self.state_notice = _state_notice_for(context)
        self._run_widgets = _RunWidgets(build, PAGE_SPACING)
        column = _bare_column(self)
        column.addWidget(self.state_notice)
        column.addWidget(self._run_widgets.holder)
        column.addStretch(1)

    def refresh(self, tick: ViewTick) -> None:
        """Show one widget for each run in the tick, and write each from its run's presentation."""

        self._run_widgets.follow(tick.runs)

        for widget, run in zip(self._run_widgets.widgets, tick.runs, strict=True):
            self._write(widget, run)

        self._drawn = True

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn

    def frame_request(self) -> FrameRequest | None:
        return None

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return ()


def _accounting_heading(run: RunPresentation) -> str:
    """Return the accounting panel's heading for `run`, naming the run while runs are compared."""

    return compared_panel_heading(ACCOUNTING_HEADING, run.name)


def _write_accounting(panel: AccountingPanel, run: RunPresentation) -> None:
    """Write one run's accounting panel whole: its heading, then its verdict and amounts."""

    panel.show_heading(_accounting_heading(run))
    panel.show_accounting(run.values.accounting)


class AccountingView(_RunPanelsView[AccountingPanel]):
    """Every displayed run's mass-balance panel, one above the next.

    Each panel is written from its run's presentation on every tick: the
    accounting from `RunValues.accounting`, and the heading from the run's
    name. So the panel shows the same step as the run's readouts, and it
    withholds its verdict and amounts whenever the readouts are withheld.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__(
            context,
            lambda run: AccountingPanel(run.values.accounting, _accounting_heading(run)),
            _write_accounting,
        )

    @property
    def panels(self) -> tuple[AccountingPanel, ...]:
        """The panel shown for each displayed run, in drawing order."""

        return self._run_widgets.widgets


class RunDials(QWidget):
    """One run's place in the setting controls View: its four dials, or a line in their place.

    The dials are written from `RunPresentation.dials`, the run's settings in
    force. Where those cannot be built (`run_presentation.NotBuilt`), the
    dials are deleted and one line says that the run's setting controls
    cannot be shown. A hidden dial would still hold the setting of the run
    before a Reset or an agent change, so no dial is kept (`PL-SV2Q`). The
    dials are built again on the first tick whose presentation holds them.

    A moved dial asks the dashboard for the change through the View's
    requests, naming this run by its `run_id`. So the row refuses to show
    another run's presentation. Its dials would then show one run's settings
    and change another's.

    While runs are compared, a line above the dials names the run, with the
    name that the chart's legend and the other panels use. A lone run is not
    named. The name is written from the presentation on every tick, so it
    changes with the run set (`PL-CPF2`).

    Args:
        run_id: The run whose settings the dials show and ask to change.
        requests: How the View asks the dashboard for a change.

    Attributes:
        name_text: The run's name, hidden while one run is drawn.
        controls: The four dials, or None while they cannot be shown.
        not_shown_text: The line shown in the dials' place.
    """

    def __init__(self, run_id: RunId, requests: ViewRequests) -> None:
        super().__init__()
        self._run_id = run_id
        self._requests = requests
        self.controls: ParameterControls | None = None
        self.name_text = styled_label("", color=INK, bold=True)
        self.name_text.setHidden(True)
        self.not_shown_text = styled_label(
            SETTING_CONTROLS_NOT_SHOWN_TEXT,
            color=MUTED,
            size_px=METRIC_QUALIFIER_SIZE,
            italic=True,
            wrap=True,
        )
        self.not_shown_text.setHidden(True)
        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.addWidget(self.name_text)
        self._column.addWidget(self.not_shown_text)

    def show_dials(self, run: RunPresentation) -> None:
        """Write the run's name, then the four dials from `run.dials` or the line in their place.

        Args:
            run: The presentation of the run that this row was built for.

        Raises:
            ValueError: If `run` is another run's presentation. Nothing is
                written.
        """

        if run.run_id != self._run_id:
            raise ValueError(
                f"a presentation built for {run_label(run.run_id)} was given to the dials of "
                f"{run_label(self._run_id)}: each row of dials shows the run it was built for"
            )

        self.name_text.setText(run.name or "")
        self.name_text.setHidden(run.name is None)
        dials = run.dials

        if isinstance(dials, NotBuilt):
            if self.controls is not None:
                self._column.removeWidget(self.controls)
                # The dials stay in this row until Qt deletes them. Taken out
                # with `setParent(None)`, they became a window of their own,
                # which Qt showed and gave the keyboard focus (`PL-81YL`).
                self.controls.hide()
                self.controls.deleteLater()
                self.controls = None

            self.not_shown_text.setHidden(False)

            return

        if self.controls is None:
            self.controls = self._built(dials)
            self._column.addWidget(self.controls)
            # Qt shows a widget added to a visible parent only on a later pass
            # of the event loop. The Area reads what this row needs before
            # then, so the dials are shown now.
            self.controls.show()
        else:
            self.controls.show_settings(dials)

        self.not_shown_text.setHidden(True)

    def _built(self, dials: tuple[SettingReadout, ...]) -> ParameterControls:
        """Build the four dials showing `dials`, each asking for a change to this run."""

        controls = ParameterControls(dials)
        controls.adjustment_started.connect(partial(self._requests.adjustment_start, self._run_id))
        controls.setting_requested.connect(partial(self._requests.setting, self._run_id))
        controls.preview_requested.connect(partial(self._requests.preview, self._run_id))
        controls.preview_ended.connect(partial(self._requests.preview_end, self._run_id))

        return controls


class ParameterControlsView(_RunPanelsView[RunDials]):
    """Every displayed run's setting controls, one row of four per run.

    Moving a slider here asks the dashboard to change that run's setting.
    The next tick then shows the setting in force on every setting controls
    View, in whichever Areas show one. A run whose setting controls cannot
    be built has one line in place of its row (`RunDials`).

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        requests = context.requests
        super().__init__(context, lambda run: RunDials(run.run_id, requests), RunDials.show_dials)

    @property
    def rows(self) -> tuple[RunDials, ...]:
        """Each displayed run's dials, or the line in their place, in drawing order."""

        return self._run_widgets.widgets


class _CasePanelView[W: QWidget, S](QWidget):
    """A View that shows one copy of a panel of the case, written whole from every tick.

    The panel belongs to the case and to no run, so the View shows one copy
    whatever the number of runs displayed, and whatever run a Workspace is
    pinned to (`PL-1D3Z`). The View builds its copy on the first tick that
    holds the panel's values, and writes it from each tick after that, with a
    frame or without one (`view_contract.CasePresentation`). Where the tick
    holds no such panel, the View shows a line that says why (`PL-TH35` Q6).

    An Area may be shorter than a long mark name needs once the name wraps,
    and narrower than the branch control's row of buttons. The Area then
    scrolls the View, as it does every View, and no row is clipped
    (`area_layout.ViewScroll`, `PL-CBYS`).
    """

    scope = ViewScope.CASE

    def __init__(self, context: ViewContext, object_name: str, absent_text: str) -> None:
        super().__init__()
        self._requests = context.requests
        self._panel: W | None = None
        self._drawn = False
        self.state_notice = _state_notice_for(context)
        self.absent_notice = styled_label(absent_text, color=MUTED, wrap=True)
        self.absent_notice.setHidden(True)
        self._column = _panel_column(self, object_name)
        self._column.addWidget(self.state_notice)
        self._column.addWidget(self.absent_notice)
        self._column.addStretch(1)

    @property
    def panel(self) -> W | None:
        """The View's copy of the panel, or None before the first tick and where there is none."""

        return self._panel

    def _shown(self, case: CasePresentation) -> S | None:
        """The values of this View's panel in `case`, or None where the case holds no such panel."""

        raise NotImplementedError

    def _built(self) -> W:
        """Build the copy, with each of its controls asking the dashboard for its action."""

        raise NotImplementedError

    def _write(self, panel: W, shown: S) -> None:
        """Write the whole copy from `shown`."""

        raise NotImplementedError

    def refresh(self, tick: ViewTick) -> None:
        """Write the copy from the tick's case, building it on the first tick that holds it."""

        shown = self._shown(tick.case)
        self.absent_notice.setHidden(shown is not None)

        if shown is None:
            if self._panel is not None:
                self._panel.hide()
        else:
            if self._panel is None:
                self._panel = self._built()
                # The copy goes below the state notice and above the stretch.
                self._column.insertWidget(1, self._panel)

            self._write(self._panel, shown)
            self._panel.show()

        self._drawn = True

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn

    def frame_request(self) -> FrameRequest | None:
        return None

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return ()


class BookmarksView(_CasePanelView[BookmarksPanel, MarksPresentation]):
    """The case's marked instants and marked heights, with the forms that add and remove them.

    Every Area that shows this View lists the same marks, because the marks
    belong to the case (`PL-9YPR`). The marks are edited here rather than in a
    window, so no window opens over the readouts while a run plays (`PL-CHX0`).
    Every copy of the forms shows the same entry, because the dashboard keeps
    it and hands it in every tick (`MarkEntry`). A press of a button sends the
    copy's entry with the request, and the dashboard makes the edit.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        # Every dashboard has marks to list, so the line for an absent panel is never shown.
        super().__init__(context, _BOOKMARKS_VIEW_NAME, "")
        # The entry that the last tick handed this View, so that a tick
        # rewrites the forms only when the dashboard's entry has changed.
        self._entry_written: MarkEntry | None = None

    def _shown(self, case: CasePresentation) -> MarksPresentation:
        return case.marks

    def _built(self) -> BookmarksPanel:
        panel = BookmarksPanel()
        editor = panel.editor

        for button, pressed in (
            (MarkButton.ADD_TIME, editor.add_time_button),
            (MarkButton.REMOVE_TIME, editor.remove_time_button),
            (MarkButton.ADD_TARGET, editor.add_target_button),
            (MarkButton.REMOVE_TARGET, editor.remove_target_button),
        ):
            pressed.clicked.connect(partial(self._ask_for_edit, button))

        editor.entry_edited.connect(self._report_entry)

        return panel

    def _ask_for_edit(self, button: MarkButton) -> None:
        if self._panel is not None:
            self._requests.mark_edit(button, self._panel.editor.entry())

    def _report_entry(self) -> None:
        if self._panel is not None:
            self._requests.mark_entry(self._panel.editor.entry())

    def _write(self, panel: BookmarksPanel, shown: MarksPresentation) -> None:
        """Write the lists, the height bound, the entry and the refusal from one tick.

        The editor's signals are blocked while the tick is written, so that
        a bound that holds the height control down is not mistaken for the
        reader editing it. The dashboard works out the same held entry itself
        (`MarkEntry.kept_through`).

        The forms are rewritten only when the dashboard's entry differs both
        from the entry last handed here and from what the forms hold. Writing a
        field moves its cursor, so the copy the reader is typing in is never
        rewritten with its own entry. The selected rows are written on every
        tick, because a refill of a list can leave a copy built while the
        lists were hidden with no row selected.
        """

        editor = panel.editor

        with QSignalBlocker(editor):
            if shown.panel is None:
                panel.withdraw()
            else:
                panel.set_panel(shown.panel)

            if shown.reachable_height_mac is not None:
                editor.set_reachable_height(shown.reachable_height_mac)

            entry = shown.entry

            if entry is not None:
                if entry != self._entry_written and entry != editor.entry():
                    editor.set_entry(entry)
                else:
                    editor.select_rows(entry)

            self._entry_written = entry
            editor.show_refusal(shown.refusal)


class BranchView(_CasePanelView[ForkPanel, BranchPresentation]):
    """Where a learner opens a branch of the case: the point to open it at, and the buttons.

    The selected point belongs to the case, so every Area that shows this
    View shows the same selection, and a copy built after a switch of
    Workspace shows it too (`PL-9YPR`). Where the dashboard holds no case, the
    View shows `dashboard_frame.NO_CASE_TO_BRANCH_TEXT` and no control.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__(context, _BRANCH_VIEW_NAME, NO_CASE_TO_BRANCH_TEXT)

    def _shown(self, case: CasePresentation) -> BranchPresentation | None:
        return case.branch

    def _built(self) -> ForkPanel:
        panel = ForkPanel()
        requests = self._requests
        panel.take_button.clicked.connect(requests.branch)
        panel.here_button.clicked.connect(requests.branch_here)
        panel.point_selector.currentIndexChanged.connect(self._report_point)

        return panel

    def _report_point(self) -> None:
        if self._panel is not None:
            self._requests.branch_point(self._panel.selected_point())

    def _write(self, panel: ForkPanel, shown: BranchPresentation) -> None:
        """Write the offer and the selected point. Before the first frame there is no offer."""

        if shown.offer is not None:
            panel.set_offer(shown.offer, shown.selected)


class CompartmentSchematicView(QWidget):
    """Every displayed run's compartment schematic, one above the next (`PL-RNYV`).

    Each schematic draws the circuit, the alveoli, venous blood and the three
    tissue groups as containers. Each container is filled to its tension on
    the concentration chart's scale, and labelled with its name, its tension
    and its amount of agent vapour. Each schematic is written from its run's
    presentation on every tick: the drawing from `RunValues.schematic`, and
    the name from the run's name. That presentation also holds the run's
    readouts. So the schematic shows the same step as the readouts, and it
    is withheld whenever they are. The View asks for no chart frame.
    The statement that its values are model outputs, not measurements, appears
    once, in the View's heading, because every value the View shows is a model
    output.

    Args:
        context: What the View is built from.
    """

    scope = ViewScope.RUNS

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self.state_notice = _state_notice_for(context)
        self._schematics = _RunWidgets(
            lambda run: RunSchematic(run.values.schematic, run.name), PAGE_SPACING
        )
        column = _panel_column(self, _SCHEMATIC_VIEW_NAME)
        heading = QHBoxLayout()
        heading.setSpacing(VIEW_HEADING_SPACING)
        heading.addWidget(styled_label(SCHEMATIC_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(INTERPRETATION_DISCLAIMER_TEXT, color=MUTED))
        column.addWidget(self.state_notice)
        column.addLayout(heading)
        column.addWidget(self._schematics.holder)
        column.addStretch(1)

    @property
    def schematics(self) -> tuple[RunSchematic, ...]:
        """The schematic shown for each displayed run, in drawing order."""

        return self._schematics.widgets

    def refresh(self, tick: ViewTick) -> None:
        """Show one schematic for each run in the tick, written from that run's presentation.

        A tick with no frame is drawn as a tick with one is, and the View
        counts as drawn after either.
        """

        self._schematics.follow(tick.runs)

        for schematic, run in zip(self._schematics.widgets, tick.runs, strict=True):
            schematic.show_name(run.name)
            schematic.show_schematic(run.values.schematic)

        self._drawn = True

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn

    def frame_request(self) -> FrameRequest | None:
        return None

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return tuple(
            text
            for schematic in self._schematics.widgets
            for text in schematic.canvas.painted_strings()
        )


class AgentCostView(QWidget):
    """Every displayed run's delivered agent, in the unit the reader chose, and its cost.

    By default the amount is in millilitres of liquid equivalent, and the
    reader can choose litres of vapour instead. The unit is printed on every
    amount, so the choice is never a hidden mode. The unit is the reader's
    preference, not this View's own setting. So the selector shows the unit
    that each tick's preferences hold, and asks the dashboard for a change
    through `ViewRequests.agent_cost_unit`. Every agent cost View shows the
    same unit, and the choice survives a restart (`app/preferences.py`).

    Each run's panel is written from its run's presentation on every tick:
    the delivered agent from `RunValues.delivered`, the name from the run's
    name, and the unit and prices from the tick's preferences. That
    presentation also holds the run's readouts. So the panel shows the same
    step as the readouts, and it is withheld whenever they are. The View
    asks for no chart frame. The heading says that the values are model
    outputs, not measurements. Under it, a notice tells the reader when a
    preference was refused or will not be kept (`PL-B396`).

    Each panel also shows the delivered agent's cost at the reader's price for
    the run's agent. Beside the cost, it shows the figures that were
    multiplied to give it, and where the price came from (`PL-1P15`). Under
    the panels, a form lets the reader set or remove that price. The form
    sends the request to the dashboard through `ViewRequests.agent_price`.
    Under the notice that names the refused entries of the preferences file,
    the View offers to discard them (`RefusedEntriesDiscard`, `PL-7KXN`).
    The form starts on the first displayed run's agent, which it reads from
    that run's presentation. So a form opened while no frame can be drawn
    names the agent that the run holds. The project ships no price, so until
    the reader sets one, each panel says that no cost is shown and why.

    Args:
        context: What the View is built from.
    """

    scope = ViewScope.RUNS

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self._requests = context.requests
        self.state_notice = _state_notice_for(context)
        self._panels = _RunWidgets(
            lambda run: RunAgentCost(run.values.delivered, run.name), PAGE_SPACING
        )
        # The unit the panels were last drawn in, or None before the first tick.
        self._drawn_unit: AgentAmountUnit | None = None
        self.unit_selector = FocusedComboBox()
        self.unit_selector.setStyleSheet(selector_stylesheet())

        for unit, name in UNIT_CHOICES:
            self.unit_selector.addItem(name, userData=unit)

        # `activated` is emitted only for a reader's pick, so showing the unit
        # in force on each tick never reads as a request.
        self.unit_selector.activated.connect(self._handle_pick)
        self.unit_label = styled_label(UNIT_CHOICE_LABEL, color=INK)
        # Until a tick has drawn the panels, the selector has no unit in force
        # to show, so it is hidden rather than showing the default.
        self.unit_label.setHidden(True)
        self.unit_selector.setHidden(True)
        self.preferences_notice = styled_label(
            "", color=WARNING, size_px=METRIC_QUALIFIER_SIZE, wrap=True
        )
        self.preferences_notice.setHidden(True)
        self.refused_discard = RefusedEntriesDiscard(context.requests.refused_entries_discard)
        column = _panel_column(self, _AGENT_COST_VIEW_NAME)
        heading = QHBoxLayout()
        heading.setSpacing(VIEW_HEADING_SPACING)
        heading.addWidget(styled_label(AGENT_COST_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(INTERPRETATION_DISCLAIMER_TEXT, color=MUTED))
        choice = QHBoxLayout()
        choice.setSpacing(VIEW_HEADING_SPACING)
        choice.addWidget(self.unit_label)
        choice.addWidget(self.unit_selector)
        choice.addStretch(1)
        column.addWidget(self.state_notice)
        column.addLayout(heading)
        column.addLayout(choice)
        column.addWidget(self.preferences_notice)
        column.addWidget(self.refused_discard)
        column.addWidget(self._panels.holder)
        self.price_entry = PriceEntry(context.requests.agent_price)
        column.addWidget(self.price_entry)
        column.addStretch(1)

    @property
    def panels(self) -> tuple[RunAgentCost, ...]:
        """The panel shown for each displayed run, in drawing order."""

        return self._panels.widgets

    def refresh(self, tick: ViewTick) -> None:
        """Show one panel for each run in the tick, in the unit the tick's preferences hold.

        Each panel is written from its run's presentation and the tick's
        preferences. A tick with no frame is drawn as a tick with one is,
        and the View counts as drawn after either.

        Raises:
            ValueError: If the preferences hold a unit that the selector does
                not offer. The two read the same list, so that is a defect.
        """

        self._panels.follow(tick.runs)
        preferences: Preferences = tick.preferences.preferences
        unit = preferences.agent_cost_unit
        index = self.unit_selector.findData(unit)

        if index < 0:
            raise ValueError(f"the agent cost View does not offer {unit.value}")

        for panel, run in zip(self._panels.widgets, tick.runs, strict=True):
            panel.show_name(run.name)
            panel.show_delivered(run.values.delivered)
            panel.show_preferences(preferences)

        self.unit_selector.setCurrentIndex(index)
        self.unit_label.setHidden(False)
        self.unit_selector.setHidden(False)
        self._drawn_unit = unit

        self.price_entry.show_prices(
            preferences, tick.runs[0].statement.agent_id if tick.runs else None
        )
        notice = tick.preferences.notice
        self.preferences_notice.setText(notice or "")
        self.preferences_notice.setHidden(notice is None)
        self.refused_discard.show_offer(preferences.holds_refused_entries)
        self._drawn = True

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn

    def frame_request(self) -> FrameRequest | None:
        return None

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return ()

    def _handle_pick(self, index: int) -> None:
        """Ask for the unit the reader picked. The next tick shows it on every agent cost View.

        The selector is first put back to the unit the panels were drawn in.
        Only a tick that draws the panels moves it. So where no tick follows
        the pick, the selector never names a unit that no value on screen is
        shown in.
        """

        if self._drawn_unit is not None:
            self.unit_selector.setCurrentIndex(self.unit_selector.findData(self._drawn_unit))

        self._requests.agent_cost_unit(UNIT_CHOICES[index][0])
