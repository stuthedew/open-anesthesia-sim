"""The Views this build registers, each written to the View contract, in PySide6.

Each class here satisfies `app/view_contract.py`'s `View`, and its registry
entry in `app/view_registry.py` names the class as its factory. So any of them
can be built in any Area, any number of times, from a `ViewContext` alone.
Each one is drawn from the `ViewTick` the adapter hands it on every frame
(`PL-TH35`).

- `ConcentrationView` is the concentration chart with its time-base control,
  captions, reference values, legend and advisories.
- `WashInView` is the F_A/F_I plot with its time-base control, captions,
  legend, per-run state lines and advisories.
- `AccountingView` is every displayed run's mass-balance panel. `docs/MODEL.md`
  § "Minimum displayed outputs" requires it to stay reachable in every layout,
  which the registry enforces.
- `ParameterControlsView` is every displayed run's setting controls.

A View that shows a run's own surfaces asks the run for a copy of each, and
the run updates every copy it has built (`app/run_surfaces.py`, `PL-9LNF`). So
two Views of one kind show the same values, and closing one View takes nothing
with it.

Each chart View holds its own time window, set from its own control and
saved in its state (project owner, 2026-10-19, `PL-L59K`). So a chart writes
the lines that depend on its window, such as which traces are above the axis,
from its own frame, one line per run, rather than showing a copy from the run.

These classes compute nothing that a reader interprets. Every caption comes
from `app/dashboard_frame.py`, and every drawn value comes from the frame.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import partial
from types import MappingProxyType
from typing import Final

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import ChartTimeBase, saved_time_base, saved_time_base_value
from anesthesia_sim.app.dashboard_frame import (
    CHART_HEADING,
    NO_TRACES_SHOWN_TEXT,
    TIME_BASE_LABEL,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WASH_IN_MODELLED_TEXT,
    compartment_cap_notice,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    off_scale_lines,
    time_axis_caption,
    unmarked_changes_lines,
    wash_in_state_lines,
)
from anesthesia_sim.app.qt_chart import (
    ConcentrationChart,
    TimeBaseSelector,
    TraceLegend,
    WashInChart,
    WashInLegend,
)
from anesthesia_sim.app.qt_widgets import styled_label
from anesthesia_sim.app.stylesheets import panel_stylesheet
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
    FrameRequest,
    RunSurfaces,
    SavedState,
    ViewContext,
    ViewTick,
    unreadable_state_text,
)

__all__ = ["AccountingView", "ConcentrationView", "ParameterControlsView", "WashInView"]

#: The version of the saved state of the Views here that have no setting of
#: their own: the accounting and the setting controls. Each saves its version
#: and nothing else.
_STATE_VERSION: Final = 1

#: The version of a chart View's saved state. Version 2 added the chart's
#: time window under `_TIME_BASE_KEY` (`PL-L59K`). Version 1 held no setting,
#: so a chart reads it as the default window and loses nothing.
_CHART_STATE_VERSION: Final = 2
_SETTINGLESS_CHART_STATE_VERSION: Final = 1

#: The key under which a chart saves its window, in the form
#: `chart_time_base.saved_time_base_value` writes.
_TIME_BASE_KEY: Final = "time_base_s"

_CONCENTRATION_VIEW_NAME: Final = "concentrationView"
_WASH_IN_VIEW_NAME: Final = "washInView"


class _RunCopies[W: QWidget]:
    """One copy of a run surface per displayed run, in drawing order, in a column of their own.

    A View calls `follow` with each tick's runs. A run still displayed keeps
    its copy, a new run gets one built, and the copy of a run no longer
    displayed is deleted. So a branch taken or removed changes only its own
    copy, and a slider being dragged in another run's copy is not rebuilt
    under the pointer.

    A copy is also deleted when its run is. A run removed while frames are
    failing never reaches `follow` again, and its copy would otherwise go on
    showing that run's last values beside the runs still displayed.
    """

    def __init__(self, build: Callable[[RunSurfaces], W], spacing: int) -> None:
        self._build = build
        self.holder = QWidget()
        self._column = QVBoxLayout(self.holder)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.setSpacing(spacing)
        self._copies: list[tuple[RunSurfaces, W]] = []

    @property
    def copies(self) -> tuple[W, ...]:
        """The copies shown now, one per displayed run, in drawing order."""

        return tuple(copy for _, copy in self._copies)

    def follow(self, runs: tuple[RunSurfaces, ...]) -> None:
        """Show one copy for each of `runs`, in their order."""

        held = [run for run, _ in self._copies]

        if len(held) == len(runs) and all(a is b for a, b in zip(held, runs, strict=True)):
            return

        kept: list[tuple[RunSurfaces, W]] = []

        for run in runs:
            copy = next((copy for owner, copy in self._copies if owner is run), None)
            kept.append((run, self._built_for(run) if copy is None else copy))

        for _, copy in self._copies:
            self._column.removeWidget(copy)

            if not any(copy is still for _, still in kept):
                copy.hide()
                copy.deleteLater()

        for _, copy in kept:
            self._column.addWidget(copy)
            copy.show()

        self._copies = kept

    def _built_for(self, run: RunSurfaces) -> W:
        """A new copy for `run`, deleted with the run and forgotten once Qt destroys it."""

        copy = self._build(run)

        if isinstance(run, QObject):
            run.destroyed.connect(copy.deleteLater)

        copy.destroyed.connect(partial(self._forget, copy))

        return copy

    def _forget(self, copy: W, *_destroyed: object) -> None:
        self._copies = [(run, kept) for run, kept in self._copies if kept is not copy]


class _RunLines:
    """One conditional line per displayed run, written from a chart's own frame.

    The lines a chart writes from its frame, such as which traces are above
    the axis. `show` takes the tick's runs and one entry per run, and an entry
    of None hides that run's line. Each line is a `_RunCopies` copy, so it is
    deleted with its run even while no frame can be drawn, and a dropped run's
    line never stays beside the runs still displayed.
    """

    def __init__(self, color: str, *, italic: bool) -> None:
        self._copies = _RunCopies(
            lambda _run: styled_label(
                "", color=color, size_px=METRIC_QUALIFIER_SIZE, italic=italic, wrap=True
            ),
            VIEW_ROW_SPACING,
        )
        self.holder = self._copies.holder

    @property
    def lines(self) -> tuple[QLabel, ...]:
        """The line shown for each displayed run, in drawing order."""

        return self._copies.copies

    def show(self, runs: tuple[RunSurfaces, ...], texts: Sequence[str | None]) -> None:
        """Write one line for each of `runs`, hiding each line whose entry is None.

        Raises:
            ValueError: If there is not one entry for each run.
        """

        if len(texts) != len(runs):
            raise ValueError(f"{len(texts)} line(s) were given for {len(runs)} run(s)")

        self._copies.follow(runs)

        for line, text in zip(self._copies.copies, texts, strict=True):
            line.setText(text or "")
            line.setHidden(text is None)


def _read_time_base(saved: object) -> tuple[ChartTimeBase | None, str | None]:
    """The window a chart's saved state holds, and the notice to show if it could not be read.

    None saved, or a version 1 state, which held no setting, is the default
    window, "Fit run". A version 2 state holds its window under
    `_TIME_BASE_KEY`. Anything else starts the chart from the default window
    and returns `UNREADABLE_STATE_TEXT`, so the chart says it is not showing
    what was saved (Q4).
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
    """A chart View's own time window: the control that sets it, and its saved form.

    Each chart holds its window (project owner, 2026-10-19, `PL-L59K`). The
    window starts from the saved state, or from "Fit run" where none was
    saved. A reader's pick sets it and asks for a frame at once. The control
    shows the window that the plot last drew, so where a frame fails, the
    control goes on naming what is on the plot (`PL-G3K7`).

    Args:
        context: What the chart View is built from.

    Attributes:
        selector: The control that sets the window.
        time_base: The window the chart draws next, None for "Fit run".
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
        """The frame the chart asks for: this window, sampled for `width_px`."""

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


def _state_notice_for(context: ViewContext) -> QLabel:
    """`_state_notice` for a View whose saved state holds its version and nothing else."""

    return _state_notice(unreadable_state_text(context.saved_state, _STATE_VERSION))


def _state_notice(text: str | None) -> QLabel:
    """The line a View shows while it is drawn with defaults because its saved state was unreadable.

    Conditional text: hidden unless the saved state could not be read (Q4).
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
    """A column with no margins, for a View whose rows are panels of their own."""

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

        Raises:
            ValueError: If the tick carries no frame. This View always asks
                for one.
        """

        frame = _frame_of(tick)
        self.chart.draw(frame)
        self._drawn = True
        self._window.drew(frame)
        # The names before the selection, so a legend told of a second run's
        # curves already knows what that run is called (`PL-7Z84`).
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

        Raises:
            ValueError: If the tick carries no frame. This View always asks
                for one.
        """

        frame = _frame_of(tick)
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


def _frame_of(tick: ViewTick) -> ChartFrame:
    """The frame a chart View asked for, which every tick handed to it carries.

    Raises:
        ValueError: If the tick carries no frame. The adapter hands a frame
            to every View that asks for one, so a tick without one means
            the adapter and the View disagree.
    """

    if tick.frame is None:
        raise ValueError("a chart View was handed a tick without the frame it asked for")

    return tick.frame


class _RunSurfaceView(QWidget):
    """A View that shows one copy of a run surface per displayed run, one above the next."""

    def __init__(self, context: ViewContext, build: Callable[[RunSurfaces], QWidget]) -> None:
        super().__init__()
        self._drawn = False
        self.state_notice = _state_notice_for(context)
        self._copies = _RunCopies(build, PAGE_SPACING)
        column = _bare_column(self)
        column.addWidget(self.state_notice)
        column.addWidget(self._copies.holder)
        column.addStretch(1)

    @property
    def copies(self) -> tuple[QWidget, ...]:
        """The copy shown for each displayed run, in drawing order."""

        return self._copies.copies

    def refresh(self, tick: ViewTick) -> None:
        """Show one copy for each run in the tick. The runs write the copies' values."""

        self._copies.follow(tick.runs)
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


class AccountingView(_RunSurfaceView):
    """Every displayed run's mass-balance panel, one above the next.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__(context, lambda run: run.build_accounting_panel())


class ParameterControlsView(_RunSurfaceView):
    """Every displayed run's setting controls, one row of four per run.

    A slider moved here sets the run. The run then shows the setting in force
    on every copy, including the copy above the Areas.

    Args:
        context: What the View is built from.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__(context, lambda run: run.build_parameter_controls())
