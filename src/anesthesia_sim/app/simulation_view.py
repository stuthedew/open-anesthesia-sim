"""The dashboard: what every displayed run shares, in PySide6.

`SimulationView` is the shared half of the dashboard along `PL-B9PY`'s seam.
It holds what two runs cannot each have their own of - the concentration
chart, the wash-in plot, the compartment legend, the time base and its
caption, the two clinical reference lines - and one `RunView` per run for
everything else. Every surface is an independent widget inside nested
splitters whose handles are inert (`PL-25KS`), so a later item can let a
reader resize them by enabling the handles.

**One frame, both charts, then every run.** `_refresh_view` reads one
snapshot per run, assembles one `ChartFrame` through `app/chart_frame.py`,
draws both plots from it, writes the captions from it and only then
refreshes each run against it, so the readouts, the traces and the
sentences beside them are one instant of one run (decision D2). Every claim
in a caption is `app/dashboard_frame.py`'s; this class formats nothing and
decides nothing a reader interprets.

**Two cadences, kept apart** (decision D7). Each run's own timer steps it;
this view's render timer draws, and only while a run is running or a
coalesced slider change has left a frame owed (`PL-R2YM`). A frame that
cannot be drawn halts every run, because a raise out of the shared render
path is attributable to none of them. No wall clock is read anywhere.

**Hover is the chart's** (decision D6): `qt_chart` answers whenever the
pointer is over a drawn point, running or paused, and the dashboard adds
nothing to it.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Final

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.chart_frame import ChartFrame, RunInput, assemble_chart_frame
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    ChartTimeBase,
    time_base_for_span,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    CHART_HEADING,
    FIT_RUN_LABEL,
    MAX_DISPLAYED_RUNS,
    NO_TRACES_SHOWN_TEXT,
    RENDER_INTERVAL_S,
    TIME_BASE_LABEL,
    USE_DISCLAIMER_TEXT,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WASH_IN_MODELLED_TEXT,
    compartment_cap_notice,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    run_label,
    time_axis_caption,
)
from anesthesia_sim.app.formatting import format_time_base
from anesthesia_sim.app.qt_chart import ConcentrationChart, TraceLegend, WashInChart, WashInLegend
from anesthesia_sim.app.qt_widgets import inert_splitter, selector_stylesheet, styled_label
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.theme import (
    APP_TITLE_SIZE,
    BACKGROUND,
    GRIDLINE,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PAGE_PADDING,
    PANEL,
    PANEL_PADDING,
    PANEL_RADIUS,
    SECTION_DIVIDER_HEIGHT,
    TIME_BASE_SELECTOR_WIDTH,
    WARNING,
)
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME

#: Milliseconds per second, for the timer interval `RENDER_INTERVAL_S` states
#: in seconds.
_MILLISECONDS_PER_SECOND: Final = 1000

#: The chart column takes three parts of the width beside the sidebar's one,
#: the proportion the Flet build's 9:3 grid columns gave the same two panels.
_CHART_COLUMN_STRETCH: Final = 3
_SIDEBAR_STRETCH: Final = 1

#: Spare height goes to the plots. The readout and setting sections are held
#: to their own height by a vertical policy that can shrink but not grow, so
#: a taller window lengthens the traces rather than opening blank space above
#: and below a row of readouts. A splitter stretch factor would not do it: Qt
#: multiplies a section's opening size by the factor, and only above one.
_FIXED_SECTION_POLICY: Final = QSizePolicy.Policy.Maximum

#: Object names the page and the chart panel are styled through.
_PAGE_NAME: Final = "dashboardPage"
_CHART_COLUMN_NAME: Final = "chartColumn"


def _spaced_column(widget: QWidget, spacing: int) -> QVBoxLayout:
    """A vertical layout on `widget` with no margins and the given spacing."""

    column = QVBoxLayout(widget)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(spacing)

    return column


class SimulationView(QWidget):
    """The dashboard over one or two runs on one agent.

    Attributes:
        presented_frames: How many frames `_refresh_view` has drawn. What
            the tests count instead of the Flet build's page updates, and
            what the coalescing rule (`PL-R2YM`) is about.
    """

    def __init__(
        self, controllers: Sequence[SimulationController], parent: QWidget | None = None
    ) -> None:
        """Build the dashboard over `controllers`, one `RunView` each, drawing nothing yet.

        The first presentation happens after `show()` and a settled layout,
        because a frame is assembled from the plot's laid-out width:
        `main.py` calls `present(False)` after the window is shown.

        Args:
            controllers: The runs, in drawing order; the first is the
                reference run for the MAC ruler and the clinical references.
            parent: The Qt parent.

        Raises:
            ValueError: If no run is given, if more than
                `MAX_DISPLAYED_RUNS` are, or if the runs are not all on one
                agent. One ×MAC ruler, one MAC-awake band and one 1 MAC line
                are drawn across a chart every run shares, and all three are
                the agent's own published values; two agents on one axis
                would have one run's traces read against the other's
                divisor - a correct number under the wrong label, which
                `CLAUDE.md`'s safety-critical standard treats as a failure
                of the value.
        """

        if not controllers:
            raise ValueError("a dashboard displays at least one run; none was given")

        if len(controllers) > MAX_DISPLAYED_RUNS:
            raise ValueError(
                f"{len(controllers)} runs given; at most {MAX_DISPLAYED_RUNS} may be "
                f"displayed at once"
            )

        agent_ids = {controller.snapshot().agent_id for controller in controllers}

        if len(agent_ids) > 1:
            raise ValueError(
                "every displayed run must be on the same agent, because they share one MAC "
                f"axis and one set of clinical references; given {', '.join(sorted(agent_ids))}"
            )

        super().__init__(parent)
        self._runs = tuple(RunView(controller, self) for controller in controllers)
        self._time_base: ChartTimeBase | None = None
        self._frame: ChartFrame | None = None
        self._render_pending = False
        self.presented_frames = 0

        self._concentration_chart = ConcentrationChart()
        self._wash_in_chart = WashInChart()
        self._legend = TraceLegend()
        self._wash_in_legend = WashInLegend()
        self._time_base_dropdown = QComboBox()
        self._time_base_dropdown.setFixedWidth(TIME_BASE_SELECTOR_WIDTH)
        self._time_base_dropdown.setStyleSheet(selector_stylesheet())
        self._time_base_dropdown.addItem(FIT_RUN_LABEL, userData=FIT_RUN_KEY)

        for time_base in SELECTABLE_TIME_BASES:
            self._time_base_dropdown.addItem(
                format_time_base(time_base.span_s), userData=str(time_base.span_s)
            )

        self._time_axis_caption = styled_label("", color=MUTED)
        self._mac_reference_text = styled_label("", color=MUTED)
        self._mac_awake_reference_text = styled_label("", color=MUTED)
        self._hidden_traces_text = styled_label(
            NO_TRACES_SHOWN_TEXT, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self._hidden_traces_text.setHidden(True)
        # Conditional text, and it earns a sentence on
        # `.claude/rules/ui-reader.md`'s own test: it is the one state in
        # which the legend's checked boxes and the plot's curves disagree by
        # design, and no label, unit or axis title can carry that.
        self._capped_traces_text = styled_label(
            "", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self._capped_traces_text.setHidden(True)

        # Said once, at construction, because the count cannot change while a
        # dashboard is alive - `controllers` is what it was built over. Both
        # legends need it to name the runs and the chart legend needs it to
        # hold the compartment selection to `COMPARED_COMPARTMENT_CAP`.
        self._legend.set_run_count(len(self._runs))
        self._wash_in_legend.set_run_count(len(self._runs))

        for index, run in enumerate(self._runs):
            run.set_run_name(run_label(index) if len(self._runs) > 1 else None)

        self._chart_column = self._build_chart_column()
        self._build_page()

        for run in self._runs:
            run.presentation_requested.connect(self.present)

        self._time_base_dropdown.currentIndexChanged.connect(self._handle_time_base_change)
        self._legend.visibility_changed.connect(self._handle_trace_visibility_change)

        self._render_timer = QTimer(self)
        self._render_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._render_timer.setInterval(round(RENDER_INTERVAL_S * _MILLISECONDS_PER_SECOND))
        self._render_timer.timeout.connect(self.render_tick)

    @property
    def runs(self) -> tuple[RunView, ...]:
        """The displayed runs, in the order given."""

        return self._runs

    # -------------------------------------------------------------- layout

    def _build_page(self) -> None:
        """Lay the dashboard out, top to bottom, inside a scrolling page.

        The notice banners sit under the transport rows and above every
        displayed value, so a halted run is read before the values it
        explains. The three sections below them - readouts, settings, and
        the charts beside the sidebar - are splitter sections, and only the
        last of them takes spare height.
        """

        page = QWidget()
        page.setObjectName(_PAGE_NAME)
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        page.setStyleSheet(f"QWidget#{_PAGE_NAME} {{ background-color: {BACKGROUND}; }}")
        column = QVBoxLayout(page)
        column.setContentsMargins(PAGE_PADDING, PAGE_PADDING, PAGE_PADDING, PAGE_PADDING)
        column.setSpacing(12)

        header = QWidget()
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(12)
        header_row.addWidget(
            styled_label(APP_DISPLAY_NAME, color=INK, size_px=APP_TITLE_SIZE, bold=True)
        )

        for run in self._runs:
            header_row.addWidget(run.build_header_badge())

        header_row.addStretch(1)
        column.addWidget(header)

        for run in self._runs:
            column.addWidget(run.build_transport_row())

        for run in self._runs:
            column.addWidget(run.build_notice())

        sidebar = QWidget()
        sidebar_column = _spaced_column(sidebar, 12)

        for run in self._runs:
            for panel in run.build_sidebar_panels():
                sidebar_column.addWidget(panel)

        sidebar_column.addStretch(1)

        charts_and_sidebar = inert_splitter(
            Qt.Orientation.Horizontal, (self._chart_column, sidebar)
        )
        charts_and_sidebar.setStretchFactor(0, _CHART_COLUMN_STRETCH)
        charts_and_sidebar.setStretchFactor(1, _SIDEBAR_STRETCH)

        sections: list[QWidget] = [run.build_readout_section() for run in self._runs]
        sections.extend(run.build_parameter_controls() for run in self._runs)

        for section in sections:
            section.setSizePolicy(section.sizePolicy().horizontalPolicy(), _FIXED_SECTION_POLICY)

        sections.append(charts_and_sidebar)
        column.addWidget(inert_splitter(Qt.Orientation.Vertical, sections), 1)
        column.addWidget(styled_label(USE_DISCLAIMER_TEXT, color=WARNING, bold=True, wrap=True))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {BACKGROUND}; }}")
        scroll.setWidget(page)
        outer = _spaced_column(self, 0)
        outer.addWidget(scroll)

    def _build_chart_column(self) -> QWidget:
        """The chart panel: heading and time base, captions, legend, advisories, both plots.

        Everything above each plot is a label, a legend entry or a reference
        value rather than a sentence (`PL-6580`, `PL-F9TQ`); the two
        advisories - no trace drawn, a trace above the axis - speak only when
        they apply. A compartment's legend entry stays on screen when its
        trace is unchecked and keeps its line-style words while it is off
        (`PL-YTX9`). Both charts are direct children of this widget, in
        this order, so a walk of its layout reads the panel as a reader
        does.
        """

        panel = QWidget()
        panel.setObjectName(_CHART_COLUMN_NAME)
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        panel.setStyleSheet(
            f"QWidget#{_CHART_COLUMN_NAME} {{ background-color: {PANEL}; "
            f"border-radius: {PANEL_RADIUS}px; }}"
        )
        column = QVBoxLayout(panel)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.setSpacing(6)

        heading = QHBoxLayout()
        heading.setSpacing(8)
        heading.addWidget(styled_label(CHART_HEADING, color=INK, bold=True, wrap=True), 1)
        heading.addWidget(styled_label(TIME_BASE_LABEL, color=MUTED))
        heading.addWidget(self._time_base_dropdown)
        column.addLayout(heading)
        column.addWidget(self._time_axis_caption)
        column.addWidget(self._mac_reference_text)
        column.addWidget(self._mac_awake_reference_text)
        column.addWidget(self._legend)
        column.addWidget(self._hidden_traces_text)
        column.addWidget(self._capped_traces_text)

        for run in self._runs:
            column.addWidget(run.build_off_scale_notice())

        column.addWidget(self._concentration_chart)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(SECTION_DIVIDER_HEIGHT)
        divider.setStyleSheet(f"color: {GRIDLINE};")
        column.addWidget(divider)

        column.addWidget(styled_label(WASH_IN_HEADING, color=INK, bold=True, wrap=True))
        column.addWidget(styled_label(WASH_IN_DENOMINATOR_TEXT, color=MUTED, wrap=True))
        column.addWidget(styled_label(WASH_IN_MODELLED_TEXT, color=MUTED))
        column.addWidget(self._wash_in_legend)

        for run in self._runs:
            column.addWidget(run.build_wash_in_state())

        column.addWidget(self._wash_in_chart)

        return panel

    # ---------------------------------------------------------- presenting

    def present(self, coalesce: bool) -> None:
        """Draw a frame now, or leave it to the render tick; halt every run if drawing fails.

        Guarded as `render_tick` is, because the discrete actions reach
        here through a signal, and a raise inside a slot is printed by the
        toolkit and otherwise lost: without the guard a frame that could
        not be drawn for a Start or a Reset would leave every run running
        behind a display that had stopped.

        A frame drawn now discharges one owed, so drawing at once clears the
        pending flag first: the resize `show()` delivers owes a frame, and
        the first presentation that follows it is that frame.

        Args:
            coalesce: True to mark a frame owed and let the render tick draw
                it, as a dragged slider does; False to draw at once, as every
                discrete action does (`PL-R2YM`).
        """

        if coalesce:
            self._render_pending = True
            return

        self._render_pending = False

        try:
            self._refresh_view()
        except Exception as error:
            self._halt_every_run(error)

    def render_tick(self) -> None:
        """Draw a frame if a run is running or one is owed; halt every run if drawing fails.

        The pending flag is cleared before the frame is drawn, so a frame
        that raises cannot leave the change that asked for it owed forever.
        """

        if not any(run.is_running for run in self._runs) and not self._render_pending:
            return

        self._render_pending = False

        try:
            self._refresh_view()
        except Exception as error:
            self._halt_every_run(error)

    def _refresh_view(self) -> None:
        """Read every run once, assemble one frame, draw both plots, then refresh every run.

        The frame is assembled for the wider of the two plots, so neither
        draws a chord wider than a pixel (`PL-GS3R`). The MAC-awake line is
        the reference run's, because the frame carries the band's edges and
        not the published fraction it was drawn from.

        Raises:
            ValueError: If the runs have come to be on different agents
                since construction (`assemble_chart_frame`).
        """

        snapshots = tuple(run.snapshot() for run in self._runs)
        inputs = tuple(
            RunInput(run_label(index), run.controller, snapshot, run.adjustments(snapshot))
            for index, (run, snapshot) in enumerate(zip(self._runs, snapshots, strict=True))
        )
        frame = assemble_chart_frame(
            inputs,
            self._time_base,
            self._legend.shown,
            plot_width_px=max(
                self._concentration_chart.plot_width_px(), self._wash_in_chart.plot_width_px()
            ),
        )
        self._concentration_chart.draw(frame)
        self._wash_in_chart.draw(frame)
        self._time_axis_caption.setText(time_axis_caption(frame))
        self._mac_reference_text.setText(mac_reference_caption(frame))
        self._mac_awake_reference_text.setText(mac_awake_caption(snapshots[0]))
        self._hidden_traces_text.setHidden(not no_traces_shown(frame))
        cap_notice = compartment_cap_notice(frame)
        self._capped_traces_text.setText(cap_notice or "")
        self._capped_traces_text.setHidden(cap_notice is None)

        for index, (run, snapshot) in enumerate(zip(self._runs, snapshots, strict=True)):
            run.refresh(snapshot, frame, index)

        self._frame = frame
        self.presented_frames += 1

    def _handle_time_base_change(self, index: int) -> None:
        """Take the width the reader chose and draw it at once.

        Touches no simulation state: the time base is a view control, never
        disabled, and Reset leaves it alone (`PL-012`).

        Raises:
            ValueError: If the control offers a width not on the ladder
                (`time_base_for_span`) - a divergence between the two tables
                is a defect to surface.
        """

        key = self._time_base_dropdown.itemData(index)

        if key is None:
            return

        self._time_base = None if key == FIT_RUN_KEY else time_base_for_span(float(key))
        self.present(False)

    def _handle_trace_visibility_change(self) -> None:
        """Redraw at once when a compartment is shown or hidden, so legend and plot agree."""

        self.present(False)

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        """Owe the render tick one frame from the new width.

        A frame is assembled for the plot width it is drawn on, one column
        per pixel, so the frame on screen is only right for the width it
        was drawn at: after a resize while paused, with nothing running and
        nothing owed, the columns drawn for the old width would stand on
        the new one at a chord wider than a pixel (`PL-GS3R`, `PL-25KS`).
        """

        super().resizeEvent(event)
        self._render_pending = True

    def _halt_every_run(self, error: BaseException) -> None:
        """Stop every run for a raise out of the shared render path, say so, then try to draw.

        A raise the render loop meets is attributable to no run, so every
        run stops. Each run states its halt from its own snapshot before the
        frame is attempted, because the frame is what just failed and may
        fail again for the same cause - two runs that have come to be on
        different agents, say - and a halt presented only through it would
        never be seen (`PL-25KS`). A presentation that fails afterwards
        cannot unwind the halt.
        """

        for run in self._runs:
            run.halt(error)

        for run in self._runs:
            run.present_halt()

        try:
            self._refresh_view()
        except Exception:
            pass

    # -------------------------------------------------------------- timing

    def start_simulation_timer(self) -> None:
        """Start every run's step timer and the render timer."""

        for run in self._runs:
            run.start_simulation_timer()

        self._render_timer.start()

    def stop_timers(self) -> None:
        """Stop every run's step timer and the render timer, as a test's teardown does."""

        for run in self._runs:
            run.stop_timers()

        self._render_timer.stop()

    # ------------------------------------------------------------- reading

    def interface_strings(self) -> tuple[str, ...]:
        """Every string a reader can see on the dashboard, hidden widgets included.

        Every label, every button and the name assistive technology
        announces for it, every entry of every combo, every window title, and
        the titles on both plots' axes - so a whole-interface test holds one
        definition of "on screen" rather than each walking the tree its own
        way. The hover readout is not standing text and is held by the chart's
        own tests.
        """

        return tuple(self._interface_strings())

    def _interface_strings(self) -> Iterator[str]:
        yield self.window().windowTitle()
        yield from self._concentration_chart.axis_titles()
        yield from self._wash_in_chart.axis_titles()

        for widget in (self, *self.findChildren(QWidget)):
            if isinstance(widget, QDialog):
                yield widget.windowTitle()

            if isinstance(widget, QLabel | QAbstractButton):
                yield widget.text()

            if isinstance(widget, QAbstractButton) and widget.accessibleName():
                yield widget.accessibleName()
            elif isinstance(widget, QComboBox):
                yield from (widget.itemText(index) for index in range(widget.count()))
