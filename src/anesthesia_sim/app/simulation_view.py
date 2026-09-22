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

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Final

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
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
from anesthesia_sim.app.controller import BranchedCase, SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    CHART_HEADING,
    FIT_RUN_LABEL,
    FORK_NOTHING_SELECTED_TEXT,
    MAX_DISPLAYED_RUNS,
    NO_TRACES_SHOWN_TEXT,
    REMOVE_NOTHING_SELECTED_TEXT,
    RENDER_INTERVAL_S,
    TIME_BASE_LABEL,
    USE_DISCLAIMER_TEXT,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WASH_IN_MODELLED_TEXT,
    RunMarks,
    bookmark_panel,
    comparing_fork_lock_text,
    compartment_cap_notice,
    fork_offer,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    refused_setting_notice,
    run_label,
    time_axis_caption,
)
from anesthesia_sim.app.formatting import format_time_base, mac_multiple
from anesthesia_sim.app.qt_chart import ConcentrationChart, TraceLegend, WashInChart, WashInLegend
from anesthesia_sim.app.qt_widgets import (
    BookmarkDialog,
    BookmarksPanel,
    ForkPanel,
    freeze_splitter_handles,
    inert_splitter,
    selector_stylesheet,
    styled_label,
)
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
from anesthesia_sim.core.concentration import fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError

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


def _fixed_height(section: QWidget) -> QWidget:
    """Hold a splitter section to its own height, so spare height goes to the plots."""

    section.setSizePolicy(section.sizePolicy().horizontalPolicy(), _FIXED_SECTION_POLICY)

    return section


def _spaced_column(widget: QWidget, spacing: int) -> QVBoxLayout:
    """A vertical layout on `widget` with no margins and the given spacing."""

    column = QVBoxLayout(widget)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(spacing)

    return column


def _holder(
    layout: QBoxLayout, widgets: Sequence[QWidget], *, before_stretch: bool = False
) -> QWidget:
    """One run's contribution to a shared layout, wrapped so it can be taken out again.

    A holder rather than the widgets themselves, because the dashboard's run
    set changes while it is alive: a run added after construction has to land
    in the same place in each of these layouts that it would have had at
    construction, and a run taken off has to leave nothing behind. One holder
    per run per layout makes both of those a single insertion and a single
    deletion. Its own layout has no margins, so it is invisible.

    Args:
        layout: The shared layout to add it to.
        widgets: This run's widgets for that layout, in order.
        before_stretch: True where the layout ends in a stretch the run's
            widgets must stay in front of - the header row and the sidebar.

    Returns:
        The holder, already placed.
    """

    holder = QWidget()
    # The holder's own spacing is the shared layout's, so a run whose widgets
    # sit inside one is laid out exactly as it would have been laid out
    # directly: the two sidebar panels keep the gap the column gives them.
    column = _spaced_column(holder, layout.spacing())

    for widget in widgets:
        column.addWidget(widget)

    if before_stretch:
        layout.insertWidget(layout.count() - 1, holder)
    else:
        layout.addWidget(holder)

    return holder


@dataclass(frozen=True, slots=True)
class _RunSlots:
    """Where one displayed run's widgets sit among the layouts every run shares.

    Attributes:
        readouts: The run's readout section, which is a section of the
            vertical splitter in its own right rather than a holder inside
            one - `PL-25KS` makes every surface an independent splitter
            section so that a later item can let a reader resize them, and
            merging two runs' readouts into one section would take a
            boundary away.
        parameters: Its setting controls, the same.
        placed: Every widget this run put into a shared layout, the two
            sections included. Removing the run is deleting these.
    """

    readouts: QWidget
    parameters: QWidget
    placed: tuple[QWidget, ...]


class SimulationView(QWidget):
    """The dashboard over one or two runs on one agent.

    Attributes:
        presented_frames: How many frames `_refresh_view` has drawn. What
            the tests count instead of the Flet build's page updates, and
            what the coalescing rule (`PL-R2YM`) is about.
    """

    def __init__(
        self,
        controllers: Sequence[SimulationController],
        parent: QWidget | None = None,
        *,
        case: BranchedCase | None = None,
    ) -> None:
        """Build the dashboard over `controllers`, one `RunView` each, drawing nothing yet.

        The first presentation happens after `show()` and a settled layout,
        because a frame is assembled from the plot's laid-out width:
        `main.py` calls `present(False)` after the window is shown.

        Args:
            controllers: The runs, in drawing order; the first is the
                reference run for the MAC ruler and the clinical references.
            parent: The Qt parent.
            case: The case the first run is the trunk of, where there is one.
                It is what the branch control offers instants from and takes
                branches through, and without it that control is not shown -
                a dashboard handed loose controllers has no case to branch,
                and a control that could only refuse is one presenting itself
                as working. Given, it must be the case rooted in
                `controllers[0]`: two runs drawn on one axis assert they are
                one patient under two managements, and a case naming some
                other trunk would put that assertion on the wrong run.

        Raises:
            ValueError: If no run is given, if more than
                `MAX_DISPLAYED_RUNS` are, if the runs are not all on one
                agent, or if `case` is not rooted in the first of them. One
                ×MAC ruler, one MAC-awake band and one 1 MAC line are drawn
                across a chart every run shares, and all three are the
                agent's own published values; two agents on one axis would
                have one run's traces read against the other's divisor - a
                correct number under the wrong label, which `CLAUDE.md`'s
                safety-critical standard treats as a failure of the value.
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

        if case is not None and case.trunk is not controllers[0]:
            raise ValueError(
                "a dashboard's case must be the one rooted in its first run, which is the "
                "trunk every branch of it is taken from"
            )

        super().__init__(parent)
        self._case = case
        self._runs: tuple[RunView, ...] = ()
        self._slots: tuple[_RunSlots, ...] = ()
        # Why the branch last asked for was not taken, or None. Held across
        # ticks for the reason `RunView._rejected_setting_notice` is: a
        # refusal written into the panel and then overwritten by the next
        # render tick would be gone before a reader could read it.
        self._fork_refusal: str | None = None
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

        # The marks are the *case's* and not any one run's, which is why they
        # are built here beside the chart rather than in `RunView`
        # (`docs/ARCHITECTURE.md` § "Where new code belongs": a control shared
        # between runs must not be duplicated into each). Every run holds its
        # own copy and this is the only thing that writes them, so the copies
        # stay equal by construction - and two runs compared at two different
        # heights, because a learner typed one of them twice, is the failure
        # that arrangement exists to make unreachable.
        self._bookmarks_panel = BookmarksPanel()
        self._bookmark_dialog: BookmarkDialog | None = None
        self._bookmarks_panel.edit_button.clicked.connect(self._open_bookmark_dialog)

        # Where a branch is taken. Beside the marks for the reason they are
        # here at all: both offer instants of the *case*, so neither belongs
        # inside a `RunView`.
        self._fork_panel = ForkPanel()
        self._fork_panel.take_button.clicked.connect(self._handle_fork)
        self._fork_panel.halt_button.clicked.connect(self._handle_halt_fork)

        self._chart_column = self._build_chart_column()
        self._build_page()

        for controller in controllers:
            self._place_run(controller)

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

    @property
    def case(self) -> BranchedCase | None:
        """The case being displayed, or None where the dashboard was handed loose runs.

        Its trunk is always `runs[0]`'s controller. It is replaced rather
        than mutated when the trunk starts over, so a reader of this
        property holds the case the dashboard is showing rather than one it
        used to show.
        """

        return self._case

    # -------------------------------------------------------------- layout

    def _build_page(self) -> None:
        """Lay the dashboard out, top to bottom, inside a scrolling page.

        The notice banners sit under the transport rows and above every
        displayed value, so a halted run is read before the values it
        explains. The sections below them - one readout section and one
        settings section per run, then the charts beside the sidebar - are
        splitter sections, and only the last of them takes spare height.

        No run is placed here. Every layout a run contributes to is kept, so
        that `_place_run` can fill them in the same order whether it is
        called at construction or when a learner takes a branch: a page laid
        out over the run set it happened to be built with could not gain a
        run without being rebuilt.
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
        header_row.addStretch(1)
        self._header_row = header_row
        column.addWidget(header)

        transport_rows = QWidget()
        self._transport_column = _spaced_column(transport_rows, 12)
        column.addWidget(transport_rows)

        notices = QWidget()
        self._notice_column = _spaced_column(notices, 12)
        column.addWidget(notices)

        sidebar = QWidget()
        self._sidebar_column = _spaced_column(sidebar, 12)
        self._sidebar_column.addStretch(1)

        self._charts_and_sidebar = inert_splitter(
            Qt.Orientation.Horizontal, (self._chart_column, sidebar)
        )
        self._charts_and_sidebar.setStretchFactor(0, _CHART_COLUMN_STRETCH)
        self._charts_and_sidebar.setStretchFactor(1, _SIDEBAR_STRETCH)

        self._sections = inert_splitter(Qt.Orientation.Vertical, (self._charts_and_sidebar,))
        column.addWidget(self._sections, 1)
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
        off_scale_notices = QWidget()
        self._off_scale_column = _spaced_column(off_scale_notices, column.spacing())
        column.addWidget(off_scale_notices)
        column.addWidget(self._concentration_chart)
        column.addWidget(self._section_divider())

        column.addWidget(styled_label(WASH_IN_HEADING, color=INK, bold=True, wrap=True))
        column.addWidget(styled_label(WASH_IN_DENOMINATOR_TEXT, color=MUTED, wrap=True))
        column.addWidget(styled_label(WASH_IN_MODELLED_TEXT, color=MUTED))
        column.addWidget(self._wash_in_legend)
        wash_in_states = QWidget()
        self._wash_in_state_column = _spaced_column(wash_in_states, column.spacing())
        column.addWidget(wash_in_states)
        column.addWidget(self._wash_in_chart)

        # A section of its own, below both plots, rather than under the
        # concentration chart it is most often read against. Two reasons, and
        # the second is the stronger: the marks are the case's rather than
        # either plot's, so nesting them in one plot's chrome would say
        # otherwise; and `PL-F9TQ` governs what may stand between a chart
        # heading and its plot, which is the accretion a control placed there
        # would resume.
        column.addWidget(self._section_divider())
        column.addWidget(self._bookmarks_panel)

        # And the branch control below them, for the same reason and one
        # more: a learner marks the decision point and then forks there, so
        # the two controls are read in that order. Hidden as a whole where
        # the dashboard holds no case, divider included, so a dashboard that
        # cannot branch shows no seam where the control would have been.
        self._fork_section = QWidget()
        fork_column = _spaced_column(self._fork_section, column.spacing())
        fork_column.addWidget(self._section_divider())
        fork_column.addWidget(self._fork_panel)
        self._fork_section.setHidden(self._case is None)
        column.addWidget(self._fork_section)

        return panel

    # ------------------------------------------------------------ the runs

    def _place_run(self, controller: SimulationController) -> RunView:
        """Build a view for `controller` and put its widgets in each shared layout.

        The one path a run reaches the dashboard by, whether it is one of
        the runs the dashboard was built over or a branch taken from it an
        hour later. Everything that depends on how many runs there are -
        both legends' run counts, the names the runs are called by, and
        whether an agent selector may be used - is rewritten afterwards from
        the new set rather than assumed from the old one.

        Args:
            controller: The run to display, already checked against the
                runs already shown.

        Returns:
            The view built for it.
        """

        run = RunView(controller, self)

        if not self._runs:
            # Only the first run's restart is a new case: a branch's Reset
            # returns it to the fork it opened at, which leaves the case and
            # every other run of it standing.
            run.case_restarted.connect(self._handle_case_restarted)

        run.presentation_requested.connect(self.present)
        readouts = _fixed_height(run.build_readout_section())
        parameters = _fixed_height(run.build_parameter_controls())
        placed = (
            _holder(self._header_row, (run.build_header_badge(),), before_stretch=True),
            _holder(self._transport_column, (run.build_transport_row(),)),
            _holder(self._notice_column, (run.build_notice(),)),
            _holder(self._sidebar_column, run.build_sidebar_panels(), before_stretch=True),
            _holder(self._off_scale_column, (run.build_off_scale_notice(),)),
            _holder(self._wash_in_state_column, (run.build_wash_in_state(),)),
            readouts,
            parameters,
        )
        self._runs = (*self._runs, run)
        self._slots = (*self._slots, _RunSlots(readouts, parameters, placed))
        self._restack_sections()
        self._rename_runs()

        return run

    def add_run(self, controller: SimulationController) -> RunView:
        """Draw a second run beside the one already shown, from the next frame on.

        What a fork opens into, and the reason the dashboard's run set is not
        fixed at construction. The new run is drawn last, so the run that
        happened keeps the first position and every reference the chart takes
        from the reference run - the ×MAC ruler, the MAC-awake band - goes on
        being taken from it.

        Args:
            controller: The run to add: a branch of this dashboard's own case.

        Returns:
            The view built for it.

        Raises:
            ValueError: If the dashboard holds no case, if it already displays
                `MAX_DISPLAYED_RUNS` runs, if `controller` is on another
                agent, or if `controller` is not a branch of this case. The
                last is the one that matters and the one a caller is most
                likely to get wrong: two curves on one axis assert that they
                are one patient under two managements, and nothing about a
                stranger run makes that true. It would be drawn against the
                same ×MAC ruler and named by `run_label` exactly as a branch
                is, so the wrong claim would arrive wearing a correct chart -
                which `CLAUDE.md`'s safety-critical standard treats as a
                failure of the value rather than of its presentation.

                A branch carries the agent and the cap of the case it
                continues, so the first three are unreachable through the
                branch control. They are reachable through this method, which
                is public.
        """

        if self._case is None:
            raise ValueError(
                "this dashboard holds no case, so it has no branches to display; a second run "
                "is a branch of the first, and a dashboard built over loose runs has no case "
                "to take one from"
            )

        if len(self._runs) >= MAX_DISPLAYED_RUNS:
            raise ValueError(
                f"{len(self._runs)} runs are already displayed; at most {MAX_DISPLAYED_RUNS} "
                "may be displayed at once"
            )

        agent_id = controller.snapshot().agent_id
        displayed = self._runs[0].snapshot().agent_id

        if agent_id != displayed:
            raise ValueError(
                "every displayed run must be on the same agent, because they share one MAC "
                f"axis and one set of clinical references; the dashboard is showing "
                f"{displayed} and this run is on {agent_id}"
            )

        if controller not in self._case.branches:
            opened_from = controller.opened_from

            raise ValueError(
                "a displayed run must be a branch of the case on the dashboard, because two "
                "curves on one axis assert one patient under two managements; this run "
                + (
                    f"opened at {opened_from.fork.instant_s} s but belongs to another case"
                    if opened_from is not None
                    else "is a trunk of its own and was never branched from this case"
                )
            )

        run = self._place_run(controller)

        if self._render_timer.isActive():
            # The dashboard is already running its cadences, so this run owes
            # its own step timer; `start_simulation_timer` started the timers
            # of the runs that were there at the time and cannot start one
            # that did not exist. A timer on a paused run takes no step.
            run.start_simulation_timer()

        return run

    def _handle_case_restarted(self) -> None:
        """Take every branch off the dashboard, because the run they were taken from has ended.

        A branch is a second management of a case from an instant the trunk
        passed through. Once the trunk has started over it never passed
        through that instant, so a branch drawn beside it is two curves
        asserting one patient under two managements while no longer being
        one - and `BranchedCase` would go on listing a branch of a run that
        no longer exists. The case is rebuilt on the restarted trunk, which
        is exactly what it now is: a case with no branches.

        **A dashboard with no case has no branches, and this does nothing to
        it.** Its runs are independent trunks - what the constructor admits
        and what the two-trunk tests build - so the first run starting over
        says nothing about the second, and dropping it would destroy a
        recorded run over an input to another one. Reset is the gesture a
        reader reaches for to start one run again, which is precisely the
        wrong place to put a surprise (`PL-LQ19`).
        """

        if self._case is None or len(self._runs) == 1:
            return

        dropped = tuple(zip(self._runs[1:], self._slots[1:], strict=True))
        self._runs = self._runs[:1]
        self._slots = self._slots[:1]

        for run, slots in dropped:
            self._remove_run(run, slots)

        if self._case is not None:
            self._case = BranchedCase(self._runs[0].controller)

        self._fork_refusal = None
        self._restack_sections()
        self._rename_runs()

    def _remove_run(self, run: RunView, slots: _RunSlots) -> None:
        """Stop a run's timer, take its widgets out of every shared layout, and delete both.

        The caller has already taken `run` out of `self._runs`, because the
        widgets deleted here are ones the view would write on its next
        refresh.

        Args:
            run: The view to remove.
            slots: Where its widgets were placed.
        """

        run.stop_timers()
        run.presentation_requested.disconnect(self.present)

        for widget in slots.placed:
            widget.setParent(None)
            widget.deleteLater()

        run.setParent(None)
        run.deleteLater()

    def _restack_sections(self) -> None:
        """Order the vertical splitter: every run's readouts, every run's settings, the charts.

        Both runs' readouts stand together and both runs' settings stand
        together, so a reader compares like against like down one column.
        `QSplitter.addWidget` moves a section it already holds, so re-adding
        every section in order is the whole of the reordering; the handles
        are frozen again because Qt enables the one it creates with a new
        section.
        """

        for slots in self._slots:
            self._sections.addWidget(slots.readouts)

        for slots in self._slots:
            self._sections.addWidget(slots.parameters)

        self._sections.addWidget(self._charts_and_sidebar)
        freeze_splitter_handles(self._sections)

    def _rename_runs(self) -> None:
        """Tell both legends and every run how many runs there now are.

        Said on every change to the run set rather than once at
        construction. A lone run is given no name, having nothing to be told
        apart from; two runs are named by `run_label`, which is what the
        legend entries call them. The same count decides whether an agent
        selector may be used at all, because two runs share one MAC axis.
        """

        comparing = len(self._runs) > 1
        self._legend.set_run_count(len(self._runs))
        self._wash_in_legend.set_run_count(len(self._runs))

        for index, run in enumerate(self._runs):
            run.set_run_name(run_label(index) if comparing else None)
            run.set_comparing(comparing)

    # ----------------------------------------------------------- branching

    def _handle_fork(self) -> None:
        """Take the branch the panel is set to, and draw it beside the trunk.

        Refused rather than obeyed while a comparison is already shown. The
        display is capped at two runs and no run selector exists yet, so a
        second branch could only replace the one on screen while the first
        went on living inside `BranchedCase` - hidden state of exactly the
        kind this interface refuses elsewhere. The control is not offered
        then; this check is what makes that a property of the dashboard
        rather than of the widget that happens to be hidden.
        """

        case = self._case

        if case is None:
            return

        if len(self._runs) >= MAX_DISPLAYED_RUNS:
            self._fork_refusal = comparing_fork_lock_text()
            self.present(False)

            return

        instant_s = self._fork_panel.selected_instant_s()

        if instant_s is None:
            self._fork_refusal = FORK_NOTHING_SELECTED_TEXT
            self.present(False)

            return

        try:
            branch = case.fork_at(instant_s)
        except SimulationConfigurationError as error:
            self._fork_refusal = refused_setting_notice(error)
            self.present(False)

            return

        self._fork_refusal = None
        self.add_run(branch)
        self.present(False)

    def _handle_halt_fork(self) -> None:
        """Take the branch at the bookmark halt the trunk is standing on.

        The second door (`PL-TYWQ`), and the sequence `docs/ARCHITECTURE.md`
        § "How a learner takes one" describes: a learner marks the decision
        point, the run stops there, and this is how they branch there. It
        names no instant - `BranchedCase.fork_at_halt` forks where the trunk
        stands - so the one thing a caller could get wrong is not expressible
        here.

        Guarded rather than trusted, for the reason `_handle_fork` is. The cap
        is checked here too, so refusing a second branch is a property of the
        dashboard rather than of a hidden widget; and the halt itself is
        re-read by the case on the press, because a halt can be cleared by
        something other than a step - unmarking the instant the run is halted
        on clears it - so the button's own frame is not proof that the fork is
        still there. `fork_at_halt` raising is that check, and its reason goes
        to the notice rather than being swallowed.
        """

        case = self._case

        if case is None:
            return

        if len(self._runs) >= MAX_DISPLAYED_RUNS:
            self._fork_refusal = comparing_fork_lock_text()
            self.present(False)

            return

        try:
            branch = case.fork_at_halt()
        except SimulationConfigurationError as error:
            self._fork_refusal = refused_setting_notice(error)
            self.present(False)

            return

        self._fork_refusal = None
        self.add_run(branch)
        self.present(False)

    def _refresh_fork_panel(self) -> None:
        """Redraw both branch controls from the trunk's state this tick.

        The instants offered are the trunk's own, so a running case adds one
        every time a setting changes and the panel has to follow; it keeps
        the reader's selection where that instant still exists. The halt fork
        follows the same tick: it appears on the frame the trunk halts on a
        mark and is gone on the frame after it steps.

        **The halt is read from the trunk rather than from the displayed
        runs.** `BranchedCase.fork_at_halt` forks the trunk and refuses a
        branch outright, so a panel drawn from a *branch's* halt would offer a
        fork the case cannot take - a control that can only apologise, which
        `.claude/rules/expert-review.md` prefers to prevent. The trunk is the
        first displayed run today, but that is an invariant of how the
        dashboard is built rather than one this method needs, and asking the
        case costs one snapshot a frame.
        """

        if self._case is None:
            return

        self._fork_panel.set_offer(
            fork_offer(
                self._case.fork_points_s,
                comparing=len(self._runs) > 1,
                halt=self._case.trunk.snapshot().bookmark_halt,
                refusal=self._fork_refusal,
            )
        )

    def _section_divider(self) -> QFrame:
        """The rule between two sections of the chart column."""

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(SECTION_DIVIDER_HEIGHT)
        divider.setStyleSheet(f"color: {GRIDLINE};")

        return divider

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

        self._refresh_bookmarks(snapshots)
        self._refresh_fork_panel()
        self._frame = frame
        self.presented_frames += 1

    # -------------------------------------------------------------- bookmarks

    def _refresh_bookmarks(self, snapshots: Sequence[SimulationSnapshot]) -> None:
        """Redraw both collections from every run, and rebound the height control.

        The *set* of marks is the reference run's, and reading one run for it
        is correct rather than a simplification: `_apply_to_every_run` is the
        only thing that writes a mark, so every displayed run carries the same
        set, and `test_every_displayed_run_carries_the_same_marks` is what
        holds that.

        **Their standings are not, and are read from every run** (`PL-LHBY`,
        `PL-4KZD`). A standing is computed from the run's own clock, its own
        opening instant and its own halts, so the runs answer one mark
        differently as soon as a branch is drawn. Passing the whole tick's
        snapshots rather than a chosen one is what keeps the choice from
        being made here at all: there is no reference run to pick.

        The height control keeps reading the reference run, and that read is
        sound where the rows' was not: it is bounded by the *agent's*
        published maximum delivered concentration over the agent's MAC, both
        settled at construction, and two displayed runs are locked to one
        agent (`COMPARING_AGENT_LOCK_TEXT`, `BRANCH_AGENT_LOCK_TEXT`, and
        `assemble_chart_frame` refusing a frame whose runs disagree). A run's
        own delivered setting moves what it will reach, not what it may be
        asked to reach. `PL-GHMB` is the item that assumed otherwise, and it
        was dropped on the measurement.

        Args:
            snapshots: Every displayed run's snapshot for this tick, in
                drawing order - the same reads the frame was assembled from.

        Raises:
            ValueError: If no run is given, which `bookmark_panel` refuses
                rather than drawing the case's marks under standings nobody
                answered. Unreachable from here - the constructor refuses an
                empty run set and `_handle_case_restarted` truncates to the
                trunk - so it is the contract rather than a live path.
            SimulationConfigurationError: If a displayed run's standings were
                computed for a mark set that does not hold one of the
                reference run's marks. `_apply_to_every_run` writes a mark to
                every displayed run and `_branch_from` copies the trunk's set
                at the fork, so the sets agree by construction; reading every
                run makes that invariant load-bearing, and a divergence now
                halts the dashboard through `present` rather than quietly
                drawing the reference run's answer, which is the direction
                `CLAUDE.md`'s safety-critical standard asks for.
        """

        reference = snapshots[0]
        panel = bookmark_panel(
            reference.bookmarks,
            tuple(
                RunMarks(run_label(index), snapshot.bookmark_standings)
                for index, snapshot in enumerate(snapshots)
            ),
        )
        self._bookmarks_panel.set_panel(panel)

        if self._bookmark_dialog is None:
            return

        self._bookmark_dialog.set_panel(panel)
        self._bookmark_dialog.set_reachable_height(
            mac_multiple(
                fraction_from_percent(reference.max_delivered_concentration_percent),
                reference.agent_mac_percent,
            )
        )

    def _open_bookmark_dialog(self) -> None:
        """Show the editor, building it the first time it is asked for.

        One dialog for the life of the dashboard rather than one per opening,
        so a reader who closes it and opens it again finds their selection
        where they left it. Non-modal and `open()` rather than `exec()`, for
        the reasons `BookmarkDialog` states.
        """

        if self._bookmark_dialog is None:
            dialog = BookmarkDialog(self)
            dialog.add_time_button.clicked.connect(self._add_time_bookmark)
            dialog.remove_time_button.clicked.connect(self._remove_time_bookmark)
            dialog.add_target_button.clicked.connect(self._add_mac_target)
            dialog.remove_target_button.clicked.connect(self._remove_mac_target)
            self._bookmark_dialog = dialog

        self.present(False)
        self._bookmark_dialog.open()

    def _apply_to_every_run(self, edit: Callable[[SimulationController], None]) -> None:
        """Make one change to every displayed run, or to none of them.

        The marks are the case's, so a mark added to one run and refused by
        another would leave two runs of one case answering different
        questions - which is exactly the state this panel exists to prevent.
        `BookmarkSet` is a value and every operation on it returns a new one,
        so the edits are computed against copies first and written only once
        all of them have been accepted.

        Args:
            edit: What to do to one run.
        """

        self._bookmarks_notice(None)

        try:
            for run in self._runs:
                edit(run.controller)
        except SimulationConfigurationError as error:
            self._bookmarks_notice(refused_setting_notice(error))

        self.present(False)

    def _bookmarks_notice(self, text: str | None) -> None:
        """Say why an edit was refused, in the dialog the reader is looking at."""

        if self._bookmark_dialog is not None:
            self._bookmark_dialog.notice.set_notice(text)

    def _add_time_bookmark(self) -> None:
        """Mark the instant the form describes, on every run."""

        dialog = self._bookmark_dialog

        if dialog is None:
            return

        try:
            bookmark = dialog.entered_time_bookmark()
        except SimulationConfigurationError as error:
            self._bookmarks_notice(refused_setting_notice(error))

            return

        self._apply_to_every_run(lambda run: run.add_time_bookmark(bookmark))
        dialog.clear_entry()

    def _remove_time_bookmark(self) -> None:
        """Unmark the selected instant, on every run."""

        dialog = self._bookmark_dialog

        if dialog is None:
            return

        marks = self._runs[0].snapshot().bookmarks.time_bookmarks
        index = dialog.selected_time_index()

        if not 0 <= index < len(marks):
            self._bookmarks_notice(REMOVE_NOTHING_SELECTED_TEXT)

            return

        selected = marks[index]
        self._apply_to_every_run(lambda run: run.remove_time_bookmark(selected))

    def _add_mac_target(self) -> None:
        """Mark the height the form describes, on every run."""

        dialog = self._bookmark_dialog

        if dialog is None:
            return

        try:
            target = dialog.entered_mac_target()
        except SimulationConfigurationError as error:
            self._bookmarks_notice(refused_setting_notice(error))

            return

        self._apply_to_every_run(lambda run: run.add_mac_target(target))
        dialog.clear_entry()

    def _remove_mac_target(self) -> None:
        """Unmark the selected height, on every run."""

        dialog = self._bookmark_dialog

        if dialog is None:
            return

        marks = self._runs[0].snapshot().bookmarks.mac_targets
        index = dialog.selected_target_index()

        if not 0 <= index < len(marks):
            self._bookmarks_notice(REMOVE_NOTHING_SELECTED_TEXT)

            return

        selected = marks[index]
        self._apply_to_every_run(lambda run: run.remove_mac_target(selected))

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
