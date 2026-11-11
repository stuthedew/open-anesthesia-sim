"""The Views this build registers, each written to the View contract, in PySide6.

Each class here satisfies `app/view_contract.py`'s `View`, and its registry
entry in `app/view_registry.py` names the class as its factory. So any of them
can be built in any Area, any number of times, from a `ViewContext` alone.
Each one is drawn from the `ViewTick` that the adapter, `app/area_layout.py`,
hands it on every frame (`PL-TH35`).

- `ConcentrationView` is the concentration chart with its time-base control,
  captions, reference values, legend and advisories.
- `WashInView` is the F_A/F_I plot with its time-base control, captions,
  legend, per-run state lines and advisories.
- `AccountingView` is every displayed run's mass-balance panel. `docs/MODEL.md`
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
saved in its state (project owner, 2026-10-19, `PL-L59K`). So a chart writes
the lines that depend on its window, such as which traces are above the axis,
from its own frame, one line per run. A tick with no frame gives a chart
nothing to draw. The chart then leaves its plot, legend and captions as they
are, and only deletes the lines of the runs that the tick no longer names.

These classes compute nothing that a reader interprets. Every caption comes
from `app/dashboard_frame.py`, or for the schematic from
`app/compartment_schematic.py`, or for the agent cost View from
`app/agent_cost.py`. Every drawn value comes from the tick's frame or from
one of the tick's presentations.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import partial
from types import MappingProxyType
from typing import Final, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from anesthesia_sim.app.agent_cost import AGENT_COST_HEADING, UNIT_CHOICE_LABEL, UNIT_CHOICES
from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import ChartTimeBase, saved_time_base, saved_time_base_value
from anesthesia_sim.app.compartment_schematic import SCHEMATIC_HEADING
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    CHART_HEADING,
    INTERPRETATION_DISCLAIMER_TEXT,
    NO_CASE_TO_BRANCH_TEXT,
    NO_TRACES_SHOWN_TEXT,
    SETTING_CONTROLS_NOT_SHOWN_TEXT,
    TIME_BASE_LABEL,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WASH_IN_MODELLED_TEXT,
    SettingReadout,
    compared_panel_heading,
    compartment_cap_notice,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    off_scale_lines,
    run_label,
    time_axis_caption,
    unmarked_changes_lines,
    wash_in_state_lines,
)
from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import Preferences
from anesthesia_sim.app.qt_agent_cost import RunAgentCost
from anesthesia_sim.app.qt_agent_price import PriceEntry
from anesthesia_sim.app.qt_chart import (
    ConcentrationChart,
    TimeBaseSelector,
    TraceLegend,
    WashInChart,
    WashInLegend,
)
from anesthesia_sim.app.qt_schematic import RunSchematic
from anesthesia_sim.app.qt_widgets import BookmarksPanel, FocusedComboBox, ForkPanel, styled_label
from anesthesia_sim.app.run_presentation import NotBuilt, RunPresentation
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls
from anesthesia_sim.app.stylesheets import panel_stylesheet, selector_stylesheet
from anesthesia_sim.app.theme import (
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PAGE_SPACING,
    PANEL_PADDING,
    VIEW_HEADING_SPACING,
    VIEW_ROW_SPACING,
    WARNING,
)
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    UNREADABLE_STATE_TEXT,
    CaseSurfaces,
    FrameRequest,
    SavedState,
    ViewContext,
    ViewRequests,
    ViewTick,
    unreadable_state_text,
)
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

_CONCENTRATION_VIEW_NAME: Final = "concentrationView"
_WASH_IN_VIEW_NAME: Final = "washInView"
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

        for _, widget in kept:
            self._column.addWidget(widget)
            widget.show()

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

    These are the lines that a chart writes from its frame, such as which
    traces are above the axis. `show` takes a frame's runs and one entry for
    each run, and an entry of None hides that run's line. `drop_absent` takes
    the runs of a tick that has no frame. It deletes the line of each run
    that the tick does not name, and it leaves every other line as the last
    frame wrote it. So a dropped run's line never stays beside the runs still
    displayed, even while no frame can be drawn.
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


class _TimeWindow:
    """A chart View's own time window, with the control that sets it and its saved form.

    Each chart holds its window (project owner, 2026-10-19, `PL-L59K`). The
    window starts from the saved state, or from "Fit run" where none was
    saved. A reader's pick sets it and asks for a frame at once. The control
    shows the window that the plot last drew, so where a frame fails, the
    control goes on naming what is on the plot (`PL-G3K7`).

    Args:
        context: What the chart View is built from.

    Attributes:
        selector: The control that sets the window.
        time_base: The window the chart draws next, or None for "Fit run".
        notice_text: The notice to show because the saved state could not be
            read, or None.
    """

    _NOT_DRAWN: Final = object()

    def __init__(self, context: ViewContext) -> None:
        self.time_base, self.notice_text = _read_time_base(context.saved_state)
        self._drawn: object = self._NOT_DRAWN
        self._request_frame = context.requests.frame
        self.selector = TimeBaseSelector()
        self.selector.show_time_base(self.time_base)
        self.selector.time_base_requested.connect(self._choose)

    def request(self, width_px: float) -> FrameRequest:
        """Return the frame that the chart asks for: this window, sampled for `width_px`."""

        return FrameRequest(self.time_base, width_px)

    def drew(self, frame: ChartFrame) -> None:
        """Note the window `frame` was drawn at, and show it in the control."""

        drawn = None if frame.fitted else frame.time_base
        self._drawn = drawn
        self.selector.show_time_base(drawn)

    @property
    def owes_a_frame(self) -> bool:
        """Whether the window was changed since the chart last drew."""

        return self._drawn is self._NOT_DRAWN or self._drawn != self.time_base

    def saved_state(self) -> SavedState:
        return MappingProxyType(
            {
                STATE_VERSION_KEY: _CHART_STATE_VERSION,
                _TIME_BASE_KEY: saved_time_base_value(self.time_base),
            }
        )

    def _choose(self, time_base: ChartTimeBase | None) -> None:
        self.time_base = time_base
        self._request_frame()

        # A frame that drew has already shown the pick. One that failed drew
        # nothing, so the control goes back to the window still on the plot.
        if self._drawn is not self._NOT_DRAWN:
            self.selector.show_time_base(cast(ChartTimeBase | None, self._drawn))


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


def _bare_column(view: QWidget) -> QVBoxLayout:
    """Return a column with no margins, for a View whose rows are panels of their own."""

    column = QVBoxLayout(view)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(PAGE_SPACING)

    return column


class ConcentrationView(QWidget):
    """The concentration chart, with everything a reader needs to read it.

    The View holds the heading and the time-base control, the statement of
    the window shown, the 1 MAC and MAC-awake reference values, and the
    legend. It also holds advisories that appear only when they apply. Above
    the plot, a line for each run names that run's traces that are above the
    axis, and another says how many of its control changes in the window
    could not be marked. Then comes the plot itself. Everything above the
    plot is a label, a legend entry or a reference value rather than a
    sentence (`PL-6580`, `PL-F9TQ`).

    The time window is the View's own, set from its control and saved in its
    state (`PL-L59K`). The legend shows the dashboard's compartment selection
    and asks for a change through the context's requests, so two of these
    Views show the same compartments (`PL-VN6M`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The compartment legend.
        time_base_selector: The control that sets the window's width.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self._window = _TimeWindow(context)
        self.chart = ConcentrationChart()
        self.legend = TraceLegend()
        self.legend.compartment_requested.connect(context.requests.compartment)
        self.time_base_selector = self._window.selector
        self.time_axis_caption = styled_label("", color=MUTED)
        self.mac_reference_text = styled_label("", color=MUTED)
        self.mac_awake_reference_text = styled_label("", color=MUTED)
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
        self.state_notice = _state_notice(self._window.notice_text)
        self.off_scale = _RunLines(WARNING, italic=True)
        self.unmarked_changes = _RunLines(MUTED, italic=True)

        column = _panel_column(self, _CONCENTRATION_VIEW_NAME)
        heading = QHBoxLayout()
        heading.setSpacing(VIEW_HEADING_SPACING)
        heading.addWidget(styled_label(CHART_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(TIME_BASE_LABEL, color=MUTED))
        heading.addWidget(self.time_base_selector)
        column.addLayout(heading)
        column.addWidget(self.state_notice)
        column.addWidget(self.time_axis_caption)
        column.addWidget(self.mac_reference_text)
        column.addWidget(self.mac_awake_reference_text)
        column.addWidget(self.legend)
        column.addWidget(self.hidden_traces_text)
        column.addWidget(self.capped_traces_text)
        column.addWidget(self.off_scale.holder)
        column.addWidget(self.unmarked_changes.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, then write the legend, the control and the captions from it.

        The legend and the time-base control are told what the plot drew only
        after the plot has drawn it. So where drawing fails, they go on naming
        what is still on the plot (`PL-G3K7`). The MAC-awake line comes from
        the reference run, because the frame carries the band's edges and not
        the published fraction that they were drawn from.

        A tick with no frame draws nothing, and the View still owes its first
        frame after one. The lines of the runs that the tick no longer names
        are deleted, and everything else stays as the last frame wrote it.
        """

        frame = tick.frame

        if frame is None:
            self.off_scale.drop_absent(tick.runs)
            self.unmarked_changes.drop_absent(tick.runs)
            return

        self.chart.draw(frame)
        self._drawn = True
        self._window.drew(frame)
        # Show the run names before the selection. Then, when the legend is told
        # about a second run's curves, it already knows what that run is called
        # (`PL-7Z84`).
        self.legend.show_run_names(tuple(run.label for run in frame.runs))
        self.legend.show_selection(tick.selection)
        self.time_axis_caption.setText(time_axis_caption(frame))
        self.mac_reference_text.setText(mac_reference_caption(frame))
        self.mac_awake_reference_text.setText(mac_awake_caption(tick.snapshots[0]))
        self.hidden_traces_text.setHidden(not no_traces_shown(frame))
        cap_notice = compartment_cap_notice(frame)
        self.capped_traces_text.setText(cap_notice or "")
        self.capped_traces_text.setHidden(cap_notice is None)
        self.off_scale.show(tick.runs, off_scale_lines(frame))
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


class WashInView(QWidget):
    """The F_A/F_I plot, with its heading, its window, what it shows, its legend and lines per run.

    Its time window is its own, as the concentration chart's is (`PL-L59K`).
    Where both show the same window, the dashboard hands both the same frame,
    so the two plots draw the same instants (`PL-9LNF`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The plot's legend.
        time_base_selector: The control that sets the window's width.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self._window = _TimeWindow(context)
        self.chart = WashInChart()
        self.legend = WashInLegend()
        self.time_base_selector = self._window.selector
        self.time_axis_caption = styled_label("", color=MUTED)
        self.state_notice = _state_notice(self._window.notice_text)
        self.states = _RunLines(MUTED, italic=False)
        self.unmarked_changes = _RunLines(MUTED, italic=True)

        column = _panel_column(self, _WASH_IN_VIEW_NAME)
        heading = QHBoxLayout()
        heading.setSpacing(VIEW_HEADING_SPACING)
        heading.addWidget(styled_label(WASH_IN_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(TIME_BASE_LABEL, color=MUTED))
        heading.addWidget(self.time_base_selector)
        column.addLayout(heading)
        column.addWidget(self.state_notice)
        column.addWidget(self.time_axis_caption)
        column.addWidget(styled_label(WASH_IN_DENOMINATOR_TEXT, color=MUTED, wrap=True))
        column.addWidget(styled_label(WASH_IN_MODELLED_TEXT, color=MUTED))
        column.addWidget(self.legend)
        column.addWidget(self.states.holder)
        column.addWidget(self.unmarked_changes.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, then write the legend, the control and the lines from it.

        A tick with no frame draws nothing, and the View still owes its first
        frame after one. The lines of the runs that the tick no longer names
        are deleted, and everything else stays as the last frame wrote it.
        """

        frame = tick.frame

        if frame is None:
            self.states.drop_absent(tick.runs)
            self.unmarked_changes.drop_absent(tick.runs)
            return

        self.chart.draw(frame)
        self._drawn = True
        self._window.drew(frame)
        self.legend.show_run_names(tuple(run.label for run in frame.runs))
        self.time_axis_caption.setText(time_axis_caption(frame))
        self.states.show(tick.runs, wash_in_state_lines(frame, tick.snapshots))
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

    Each tick, with a frame or without one, shows one widget for each run
    that the tick names and writes each widget whole from that run's
    presentation. The View counts as drawn after either kind of tick.

    Args:
        context: What the View is built from.
        build: Builds one run's widget from the run's presentation.
        write: Writes one run's widget whole from the run's presentation.
    """

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

    Args:
        run_id: The run whose settings the dials show and ask to change.
        requests: How the View asks the dashboard for a change.

    Attributes:
        controls: The four dials, or None while they cannot be shown.
        not_shown_text: The line shown in the dials' place.
    """

    def __init__(self, run_id: RunId, requests: ViewRequests) -> None:
        super().__init__()
        self._run_id = run_id
        self._requests = requests
        self.controls: ParameterControls | None = None
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
        self._column.addWidget(self.not_shown_text)

    def show_dials(self, run: RunPresentation) -> None:
        """Write the four dials from `run.dials`, or delete them and show the line in their place.

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

        dials = run.dials

        if isinstance(dials, NotBuilt):
            if self.controls is not None:
                self._column.removeWidget(self.controls)
                self.controls.setParent(None)
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


class _CasePanelView[W: QWidget](QWidget):
    """A View that shows one copy of a panel of the case, built on the View's first tick.

    The panel belongs to the case and to no run, so the View shows one copy
    whatever the number of runs displayed. The dashboard writes the copy on
    every frame and restates it on a halt (`view_contract.CaseSurfaces`).
    Where the dashboard has no such panel to give, the View shows a line that
    says why (`PL-TH35` Q6).

    The rows sit in a scroll area of the View's own. An Area may be shorter
    than a long mark name needs once the name wraps, and narrower than the
    branch control's row of buttons. The View then scrolls, and no row is
    clipped. Step 2 of `PL-CBYS` is to move this scroll into the container,
    for every View.
    """

    def __init__(
        self,
        context: ViewContext,
        object_name: str,
        build: Callable[[CaseSurfaces], W | None],
        absent_text: str,
    ) -> None:
        super().__init__()
        self._build = build
        self._panel: W | None = None
        self._drawn = False
        self.state_notice = _state_notice_for(context)
        self.absent_notice = styled_label(absent_text, color=MUTED, wrap=True)
        self.absent_notice.setHidden(True)
        body = QWidget()
        self._column = QVBoxLayout(body)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.setSpacing(VIEW_ROW_SPACING)
        self._column.addWidget(self.state_notice)
        self._column.addWidget(self.absent_notice)
        self._column.addStretch(1)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(body)
        _panel_column(self, object_name).addWidget(self.scroll_area)

    @property
    def panel(self) -> W | None:
        """The View's copy of the panel, or None before the first tick and where there is none."""

        return self._panel

    def refresh(self, tick: ViewTick) -> None:
        """Build the copy on the first tick. The dashboard writes its values from then on."""

        if self._drawn:
            return

        self._panel = self._build(tick.case)

        if self._panel is None:
            self.absent_notice.setHidden(False)
        else:
            # The copy goes below the state notice and above the stretch.
            self._column.insertWidget(1, self._panel)
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


class BookmarksView(_CasePanelView[BookmarksPanel]):
    """The case's marked instants and marked heights, with the button that opens their editor.

    Every Area that shows this View lists the same marks, because the marks
    belong to the case (`PL-9YPR`).

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        # Every dashboard has marks to list, so the line for an absent panel is never shown.
        super().__init__(
            context, _BOOKMARKS_VIEW_NAME, lambda case: case.build_bookmarks_panel(), ""
        )


class BranchView(_CasePanelView[ForkPanel]):
    """Where a learner opens a branch of the case: the point to open it at, and the buttons.

    The selected point belongs to the case, so every Area that shows this
    View shows the same selection, and a copy built after a switch of
    Workspace shows it too (`PL-9YPR`). Where the dashboard holds no case, the
    View shows `dashboard_frame.NO_CASE_TO_BRANCH_TEXT` and no control.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__(
            context,
            _BRANCH_VIEW_NAME,
            lambda case: case.build_branch_control(),
            NO_CASE_TO_BRANCH_TEXT,
        )


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
    The form starts on the first displayed run's agent, which it reads from
    that run's presentation. So a form opened while no frame can be drawn
    names the agent that the run holds. The project ships no price, so until
    the reader sets one, each panel says that no cost is shown and why.

    Args:
        context: What the View is built from.
    """

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
