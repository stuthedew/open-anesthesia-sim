"""The Views this build registers, each written to the View contract, in PySide6.

Each class here satisfies `app/view_contract.py`'s `View`, and its registry
entry in `app/view_registry.py` names the class as its factory. So any of them
can be built in any Area, any number of times, from a `ViewContext` alone.
Each one is drawn from the `ViewTick` the adapter hands it on every frame
(`PL-TH35`).

- `ConcentrationView` is the concentration chart with its time-base control,
  captions, reference values, legend and advisories.
- `WashInView` is the F_A/F_I plot with its captions, legend and per-run state
  lines.
- `AccountingView` is every displayed run's mass-balance panel. `docs/MODEL.md`
  § "Minimum displayed outputs" requires it to stay reachable in every layout,
  which the registry enforces.
- `ParameterControlsView` is every displayed run's setting controls.

A View that shows a run's own surfaces asks the run for a copy of each, and
the run updates every copy it has built (`app/run_surfaces.py`, `PL-9LNF`). So
two Views of one kind show the same values, and closing one View takes nothing
with it.

These classes compute nothing that a reader interprets. Every caption comes
from `app/dashboard_frame.py`, and every drawn value comes from the frame.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from types import MappingProxyType
from typing import Final

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

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
    time_axis_caption,
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
)
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    RunSurfaces,
    SavedState,
    ViewContext,
    ViewTick,
    unreadable_state_text,
)

__all__ = ["AccountingView", "ConcentrationView", "ParameterControlsView", "WashInView"]

#: The version of the saved state of every View in this module. None of these
#: Views has a setting of its own yet, so each saves its version and nothing
#: else. The time base and the compartment selection are shared state, which
#: the dashboard owns (`PL-VN6M`, `PL-9LNF`).
_STATE_VERSION: Final = 1

_CONCENTRATION_VIEW_NAME: Final = "concentrationView"
_WASH_IN_VIEW_NAME: Final = "washInView"


class _RunCopies:
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

    def __init__(self, build: Callable[[RunSurfaces], QWidget], spacing: int) -> None:
        self._build = build
        self.holder = QWidget()
        self._column = QVBoxLayout(self.holder)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.setSpacing(spacing)
        self._copies: list[tuple[RunSurfaces, QWidget]] = []

    @property
    def copies(self) -> tuple[QWidget, ...]:
        """The copies shown now, one per displayed run, in drawing order."""

        return tuple(copy for _, copy in self._copies)

    def follow(self, runs: tuple[RunSurfaces, ...]) -> None:
        """Show one copy for each of `runs`, in their order."""

        held = [run for run, _ in self._copies]

        if len(held) == len(runs) and all(a is b for a, b in zip(held, runs, strict=True)):
            return

        kept: list[tuple[RunSurfaces, QWidget]] = []

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

    def _built_for(self, run: RunSurfaces) -> QWidget:
        """A new copy for `run`, deleted with the run and forgotten once Qt destroys it."""

        copy = self._build(run)

        if isinstance(run, QObject):
            run.destroyed.connect(copy.deleteLater)

        copy.destroyed.connect(partial(self._forget, copy))

        return copy

    def _forget(self, copy: QWidget, *_destroyed: object) -> None:
        self._copies = [(run, kept) for run, kept in self._copies if kept is not copy]


def _state_notice(context: ViewContext) -> QLabel:
    """The line a View shows while it is drawn with defaults because its saved state was unreadable.

    Conditional text: hidden unless the saved state could not be read (Q4).
    """

    text = unreadable_state_text(context.saved_state, _STATE_VERSION)
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
    legend. It also holds two advisories that appear only when they apply.
    Above the plot, a line for each run names that run's traces. Then comes
    the plot itself. Everything above the plot is a label, a legend entry or a
    reference value rather than a sentence (`PL-6580`, `PL-F9TQ`).

    The time-base control and the legend show the dashboard's time base and
    compartment selection, and ask for a change through the context's
    requests. Neither holds the value, so two of these Views show the same
    window and the same compartments (`PL-VN6M`, `PL-9LNF`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The compartment legend.
        time_base_selector: The control that asks for the window's width.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self.chart = ConcentrationChart()
        self.legend = TraceLegend()
        self.legend.compartment_requested.connect(context.requests.compartment)
        self.time_base_selector = TimeBaseSelector()
        self.time_base_selector.time_base_requested.connect(context.requests.time_base)
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
        self.state_notice = _state_notice(context)
        self._off_scale = _RunCopies(lambda run: run.build_off_scale_notice(), VIEW_ROW_SPACING)

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
        column.addWidget(self._off_scale.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, then write the legend, the control and the captions from it.

        The legend and the time-base control are told what the plot drew only
        after the plot has drawn it. So where drawing fails, they go on naming
        what is still on the plot (`PL-G3K7`). The MAC-awake line comes from
        the reference run, because the frame carries the band's edges and not
        the published fraction that they were drawn from.
        """

        self._off_scale.follow(tick.runs)
        frame = tick.frame
        self.chart.draw(frame)
        self._drawn = True
        # The names before the selection, so a legend told of a second run's
        # curves already knows what that run is called (`PL-7Z84`).
        self.legend.show_run_names(tuple(run.label for run in frame.runs))
        self.legend.show_selection(tick.selection)
        self.time_base_selector.show_time_base(tick.time_base)
        self.time_axis_caption.setText(time_axis_caption(frame))
        self.mac_reference_text.setText(mac_reference_caption(frame))
        self.mac_awake_reference_text.setText(mac_awake_caption(tick.snapshots[0]))
        self.hidden_traces_text.setHidden(not no_traces_shown(frame))
        cap_notice = compartment_cap_notice(frame)
        self.capped_traces_text.setText(cap_notice or "")
        self.capped_traces_text.setHidden(cap_notice is None)

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn or self.chart.owes_a_frame

    def frame_width_px(self) -> float | None:
        return self.chart.plot_width_px()

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return self.chart.axis_titles()


class WashInView(QWidget):
    """The F_A/F_I plot, with its heading, what it shows, its legend and a state line per run.

    It draws the frame the concentration chart draws, so where both are shown
    the two plots share their instants and their window (`ViewTick.frame`).

    Args:
        context: What the View is built from.

    Attributes:
        chart: The plot.
        legend: The plot's legend.
    """

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self._drawn = False
        self.chart = WashInChart()
        self.legend = WashInLegend()
        self.state_notice = _state_notice(context)
        self._states = _RunCopies(lambda run: run.build_wash_in_state(), VIEW_ROW_SPACING)

        column = _panel_column(self, _WASH_IN_VIEW_NAME)
        column.addWidget(styled_label(WASH_IN_HEADING, color=INK, bold=True, wrap=True))
        column.addWidget(self.state_notice)
        column.addWidget(styled_label(WASH_IN_DENOMINATOR_TEXT, color=MUTED, wrap=True))
        column.addWidget(styled_label(WASH_IN_MODELLED_TEXT, color=MUTED))
        column.addWidget(self.legend)
        column.addWidget(self._states.holder)
        column.addWidget(self.chart, 1)

    def refresh(self, tick: ViewTick) -> None:
        """Draw the tick's frame, and give the legend the number of runs it drew."""

        self._states.follow(tick.runs)
        self.chart.draw(tick.frame)
        self._drawn = True
        self.legend.show_run_names(tuple(run.label for run in tick.frame.runs))

    @property
    def owes_a_frame(self) -> bool:
        return not self._drawn or self.chart.owes_a_frame

    def frame_width_px(self) -> float | None:
        return self.chart.plot_width_px()

    def save_state(self) -> SavedState:
        return _saved_state()

    def painted_strings(self) -> tuple[str, ...]:
        return self.chart.axis_titles()


class _RunSurfaceView(QWidget):
    """A View that shows one copy of a run surface per displayed run, one above the next."""

    def __init__(self, context: ViewContext, build: Callable[[RunSurfaces], QWidget]) -> None:
        super().__init__()
        self._drawn = False
        self.state_notice = _state_notice(context)
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

    def frame_width_px(self) -> float | None:
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
