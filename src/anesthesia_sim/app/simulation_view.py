"""The dashboard: what every displayed run shares, in PySide6.

`SimulationView` is the shared half of the dashboard along `PL-B9PY`'s seam.
It holds what two runs cannot each have their own of - the concentration
chart, the wash-in plot, the compartment legend and the selection it shows,
the time base and its caption, the two clinical reference lines - and one
`RunView` per run for everything else.

**The unconditional region is outside the splitters** (`PL-NWTM`). Each run's
transport row, its notice banner, its readouts and its control-change record
sit in a band across the top of the page, and the use disclaimer in a line
across its foot. `docs/MODEL.md` § "Minimum displayed outputs" requires those
values on screen in every Workspace, and `app/unconditional_set.py` declares
which they are; `_place_run` refuses a run whose declared values the band does
not hold. Under the band, each run's setting controls stand at their own
height, and under them the Areas: the chart panel beside the sidebar, drawn
from a layout model by `app/area_layout.py`, so a reader can drag the border
between them (`PL-W9P6`). The Areas are the layout container. Nothing in the
band has an ancestor among them, so no split, join or close can reach it.

**One frame, both charts, then every run.** `_refresh_view` reads one
snapshot per run, assembles one `ChartFrame` through `app/chart_frame.py`,
draws both plots from it, writes the captions from it and only then
refreshes each run against it, so the readouts, the traces and the
sentences beside them are one instant of one run (decision D2). Every claim
in a caption is `app/dashboard_frame.py`'s; this class formats nothing and
decides nothing a reader interprets.

**Two cadences, kept apart** (decision D7). Each run's own timer steps it;
this view's render timer draws, and only while a run is running or a frame
is owed: by a coalesced slider change (`PL-R2YM`), by a change to the run
set, or by a run whose record differs from what its view last wrote
(`PL-X7D5`). A frame that cannot be drawn halts every run, because a raise
out of the shared render path is attributable to none of them. No wall
clock is read anywhere.

**The legend is a frame widget** (`PL-G3K7`). It is handed the selection a
frame was assembled from once both plots have drawn it, so its boxes name
the curves on the plot even where the frame a click asked for fails.

**Hover is the chart's** (decision D6): `qt_chart` answers whenever the
pointer is over a drawn point, running or paused, and the dashboard adds
nothing to it.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Final

from PySide6.QtCore import Qt, QTimer, Signal
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

from anesthesia_sim.app.area_layout import AreaLayout
from anesthesia_sim.app.chart_frame import ChartFrame, RunInput, assemble_chart_frame
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    ChartTimeBase,
    time_base_for_span,
)
from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
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
    TRUNK_RUN_INDEX,
    USE_DISCLAIMER_TEXT,
    WASH_IN_DENOMINATOR_TEXT,
    WASH_IN_HEADING,
    WASH_IN_MODELLED_TEXT,
    BranchAtStake,
    NewCaseQuestion,
    RunMarks,
    bookmark_panel,
    branch_at_stake,
    comparing_fork_lock_text,
    compartment_cap_notice,
    fork_offer,
    mac_awake_caption,
    mac_reference_caption,
    no_traces_shown,
    refused_setting_notice,
    run_label,
    time_axis_caption,
    trunk_reset_question,
)
from anesthesia_sim.app.formatting import format_time_base, mac_multiple
from anesthesia_sim.app.qt_chart import ConcentrationChart, TraceLegend, WashInChart, WashInLegend
from anesthesia_sim.app.qt_widgets import BookmarkDialog, BookmarksPanel, ForkPanel, styled_label
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.stylesheets import (
    foreground_stylesheet,
    page_stylesheet,
    panel_stylesheet,
    scroll_area_stylesheet,
    selector_stylesheet,
)
from anesthesia_sim.app.theme import (
    GRIDLINE,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PAGE_PADDING,
    PAGE_SPACING,
    PANEL_PADDING,
    SECTION_DIVIDER_HEIGHT,
    TIME_BASE_SELECTOR_WIDTH,
    WARNING,
)
from anesthesia_sim.app.unconditional_set import INHALED_AGENT, unconditional_set, window_region
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING, CONCENTRATION_CHART
from anesthesia_sim.core.concentration import fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND
from anesthesia_sim.layout.model import MAIN_WINDOW, LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window

#: The unconditional region gives the run rows three parts of its width and
#: the control-change records one, the proportion the Flet build's 9:3 grid
#: columns gave the chart panel and the sidebar below them.
_CHART_COLUMN_STRETCH: Final = 3
_SIDEBAR_STRETCH: Final = 1

#: The dashboard's Areas: the chart panel beside the sidebar, in one row
#: (`PL-W9P6`). The chart panel still holds the wash-in plot, the marks and the
#: branch control under the concentration plot, until each is a View of its
#: own (`PL-TH35`, `PL-9LNF`), so it carries the tag of the View it leads with.
#: The sidebar's 0.18 gives it about the 228 px it had beside the charts in a
#: 1366 px window before the row was an Area layout, when it stood at its own
#: minimum width at every window size. A placeholder until the
#: shipped Workspaces replace this layout.
_DASHBOARD_LAYOUT: Final = LayoutModel(
    (
        Window(
            Split(
                Orientation.ROW,
                (0.82, 0.18),
                (Area(AreaId(1), CONCENTRATION_CHART), Area(AreaId(2), AGENT_ACCOUNTING)),
            )
        ),
    ),
    AreaId(3),
)

#: Spare height goes to the plots. The setting sections are held to their own
#: height by a vertical policy that can shrink but not grow, so a taller
#: window lengthens the traces rather than opening blank space under a row of
#: sliders.
_FIXED_SECTION_POLICY: Final = QSizePolicy.Policy.Maximum

#: Object names the page and the chart panel are styled through.
_PAGE_NAME: Final = "dashboardPage"
_REGION_NAME: Final = "unconditionalRegion"
_RECORD_COLUMN_NAME: Final = "controlRecordColumn"
_CHART_COLUMN_NAME: Final = "chartColumn"


def _fixed_height(section: QWidget) -> QWidget:
    """Hold a section to its own height, so spare height goes to the plots."""

    section.setSizePolicy(section.sizePolicy().horizontalPolicy(), _FIXED_SECTION_POLICY)

    return section


def _within(widget: QWidget, ancestor: QWidget) -> bool:
    """Whether `ancestor` is `widget` or one of the widgets it sits inside."""

    current: QWidget | None = widget

    while current is not None:
        if current is ancestor:
            return True

        current = current.parentWidget()

    return False


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
            widgets must stay in front of - the record column and the sidebar.

    Returns:
        The holder, already placed.
    """

    holder = QWidget()
    # The holder's own spacing is the shared layout's, so a run whose widgets
    # sit inside one is laid out exactly as it would have been laid out
    # directly: a run's panels keep the gap the column gives them.
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
        parameters: The run's setting controls, a section of the settings
            column above the Areas, held to its own height. A height a reader
            could drag is a fraction of the window in the layout model, so the
            controls join the Areas as a View of their own,
            `parameter_controls`, once the View contract exists (`PL-TH35`).
        placed: Every widget this run put into a shared layout, the section
            included. Removing the run is deleting these.
    """

    parameters: QWidget
    placed: tuple[QWidget, ...]


class SimulationView(QWidget):
    """The dashboard over one or two runs on one agent.

    Attributes:
        presented_frames: How many frames `_refresh_view` has drawn. What
            the tests count instead of the Flet build's page updates, and
            what the coalescing rule (`PL-R2YM`) is about.
    """

    compartment_selection_changed = Signal(object)
    """Emitted with the selection a frame was assembled from, once both plots have drawn it.

    Not when the selection is set, by a reader's request or a change to the
    run set: a frame that then failed left the legend naming curves the plot
    was not drawing (`PL-G3K7`). Every legend showing this view's selection
    is connected to it rather than called, so one that has been closed is
    simply no longer told, and a second is told the same (`PL-VN6M`).
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
        # Which compartments both runs are drawn with: this view's, handed to
        # the legend and to every frame, so neither is read back from the
        # other and closing the legend takes nothing with it (`PL-VN6M`).
        self._compartment_selection = INITIAL_COMPARTMENT_SELECTION
        self._frame: ChartFrame | None = None
        self._render_pending = False
        # How many runs the last frame attempted was drawn over; `render_tick`
        # draws when the run set has changed since (`PL-0LG6`).
        self._drawn_run_count = 0
        self.presented_frames = 0
        # Whether the page is holding the concentration chart in view, from
        # a branch taken until the reader scrolls the page themselves
        # (`_keep_chart_in_view`, `PL-562Z`).
        self._chart_view_owed = False

        self._concentration_chart = ConcentrationChart()
        self._wash_in_chart = WashInChart()
        self._legend = TraceLegend()
        self.compartment_selection_changed.connect(self._legend.show_selection)
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
        # `.claude/rules/ui-reader.md`'s own test: it says why boxes the
        # reader checked have come unchecked, which no label, unit or axis
        # title can carry.
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
        self._fork_panel.here_button.clicked.connect(self._handle_here_fork)

        self._chart_column = self._build_chart_column()
        self._build_page()

        for controller in controllers:
            self._place_run(controller)

        self._time_base_dropdown.currentIndexChanged.connect(self._handle_time_base_change)
        self._legend.compartment_requested.connect(self._handle_compartment_request)

        self._render_timer = QTimer(self)
        self._render_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._render_timer.setInterval(round(RENDER_INTERVAL_S * MILLISECONDS_PER_SECOND))
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

    @property
    def compartment_selection(self) -> CompartmentSelection:
        """The compartments the chart draws, which the legend shows and asks to change."""

        return self._compartment_selection

    # -------------------------------------------------------------- layout

    def _build_page(self) -> None:
        """Lay the dashboard out, top to bottom, inside a scrolling page.

        The unconditional region comes first: per run the transport row, the
        notice banner and the readouts, with every run's control-change
        record in a column to their right (`PL-J8K2` Q1 and Q3). The notice
        banners sit under the transport rows and above every displayed
        value, so a halted run is read before the values it explains. Under
        the region come the setting controls of each run, each at its own
        height, and then the Areas, the chart panel beside the sidebar, which
        take the spare height. The Areas are drawn from `_DASHBOARD_LAYOUT`
        by the adapter, so a reader can drag the border between them. The use
        disclaimer is the page's last line.

        No run is placed here. Every layout a run contributes to is kept, so
        that `_place_run` can fill them in the same order whether it is
        called at construction or when a learner takes a branch: a page laid
        out over the run set it happened to be built with could not gain a
        run without being rebuilt.
        """

        page = QWidget()
        page.setObjectName(_PAGE_NAME)
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        page.setStyleSheet(page_stylesheet(_PAGE_NAME))
        column = QVBoxLayout(page)
        column.setContentsMargins(PAGE_PADDING, PAGE_PADDING, PAGE_PADDING, PAGE_PADDING)
        column.setSpacing(PAGE_SPACING)

        column.addWidget(self._build_unconditional_region())

        settings = QWidget()
        self._settings_column = _spaced_column(settings, PAGE_SPACING)
        column.addWidget(settings)

        self._sidebar = QWidget()
        self._sidebar_column = _spaced_column(self._sidebar, PAGE_SPACING)
        self._sidebar_column.addStretch(1)

        self._areas = AreaLayout(_DASHBOARD_LAYOUT, self._area_view)
        column.addWidget(self._areas, 1)
        column.addWidget(styled_label(USE_DISCLAIMER_TEXT, color=WARNING, bold=True, wrap=True))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(scroll_area_stylesheet())
        scroll.setWidget(page)
        # `actionTriggered` fires for the reader's own scrolling - wheel,
        # keys, the bar - and not for a scroll this view makes, so it is
        # what tells the view to stop holding the chart in view.
        scroll.verticalScrollBar().actionTriggered.connect(self._release_chart_view)
        # The page's height changes with each pass of layout that moves the
        # chart, so the bar's range changing is when to follow it.
        scroll.verticalScrollBar().rangeChanged.connect(self._follow_chart)
        self._page_scroll = scroll
        outer = _spaced_column(self, 0)
        outer.addWidget(scroll)

    def _build_unconditional_region(self) -> QWidget:
        """Build the band that holds every run's unconditional values, empty of runs.

        Its left column stacks every run's transport row, then every
        notice banner, then every readout section; its right column holds
        every run's control-change record, scrolling within itself so a long
        record never makes the band taller than the rows beside it
        (`PL-J8K2` Q3). The two columns take the band's width in the
        proportion the charts and the sidebar take theirs. A box layout gives
        the record more than the splitter gives the sidebar: about 300 px at
        a 1366 px window, against the sidebar's 228, where today's record
        lines are cut off. The exact width, and whether the seven readouts
        stand in one row beside it at that width, are `PL-F2YS`'s. Nothing new is
        drawn around the region (`PL-J8K2` Q4).

        Returns:
            The region, which `unconditional_region` names.
        """

        region = QWidget()
        region.setObjectName(_REGION_NAME)
        row = QHBoxLayout(region)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(PAGE_SPACING)

        run_rows = QWidget()
        run_column = _spaced_column(run_rows, PAGE_SPACING)

        transport_rows = QWidget()
        self._transport_column = _spaced_column(transport_rows, PAGE_SPACING)
        run_column.addWidget(transport_rows)

        notices = QWidget()
        self._notice_column = _spaced_column(notices, PAGE_SPACING)
        run_column.addWidget(notices)

        readouts = QWidget()
        self._readout_column = _spaced_column(readouts, PAGE_SPACING)
        run_column.addWidget(readouts)

        records = QWidget()
        records.setObjectName(_RECORD_COLUMN_NAME)
        records.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        records.setStyleSheet(page_stylesheet(_RECORD_COLUMN_NAME))
        self._record_column = _spaced_column(records, PAGE_SPACING)
        self._record_column.addStretch(1)
        record_scroll = QScrollArea()
        record_scroll.setWidgetResizable(True)
        record_scroll.setFrameShape(QFrame.Shape.NoFrame)
        record_scroll.setStyleSheet(scroll_area_stylesheet())
        record_scroll.setWidget(records)
        # As tall as the run rows beside it and no taller: an ignored height
        # gives the band the left column's height, and the record scrolls.
        record_scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)

        row.addWidget(run_rows, _CHART_COLUMN_STRETCH)
        row.addWidget(record_scroll, _SIDEBAR_STRETCH)
        self._unconditional_region = region

        return region

    @property
    def unconditional_region(self) -> QWidget:
        """The band holding every run's unconditional values, outside every splitter."""

        return self._unconditional_region

    @property
    def layout_container(self) -> AreaLayout:
        """The Areas: the widget tree the adapter draws from the layout model.

        The widget no unconditional value may have as an ancestor, since a
        reader can resize what is in it and, once the area system is built
        out, close it (`PL-W9P6`). Its `model` is the layout drawn now, after
        every drag the reader has made.
        """

        return self._areas

    def _area_view(self, area: Area) -> QWidget:
        """The widget `area` draws: the chart panel, or the sidebar of accounting panels.

        Raises:
            LookupError: `area` names a registered View kind the dashboard
                does not draw as a View of its own yet, such as the wash-in
                plot. `_DASHBOARD_LAYOUT` names only these two, so this is a
                defect in that layout rather than a reader's file. A kind the
                registry does not hold never reaches here: the adapter draws
                its failure notice instead.
        """

        views = {CONCENTRATION_CHART: self._chart_column, AGENT_ACCOUNTING: self._sidebar}

        if area.view not in views:
            raise LookupError(f"the dashboard draws no View of the kind {area.view!r}")

        return views[area.view]

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
        panel.setStyleSheet(panel_stylesheet(_CHART_COLUMN_NAME))
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
            run.ask_before_reset(self._trunk_reset_question)

        run.presentation_requested.connect(self.present)
        parameters = _fixed_height(run.build_parameter_controls())
        placed = (
            _holder(self._transport_column, (run.build_transport_row(),)),
            _holder(self._notice_column, (run.build_notice(),)),
            _holder(self._readout_column, (run.build_readout_section(),)),
            _holder(self._record_column, (run.build_control_record(),), before_stretch=True),
            _holder(self._sidebar_column, (run.build_accounting_panel(),), before_stretch=True),
            _holder(self._off_scale_column, (run.build_off_scale_notice(),)),
            _holder(self._wash_in_state_column, (run.build_wash_in_state(),)),
            parameters,
        )
        self._settings_column.addWidget(parameters)
        self._require_unconditional_values(run)
        self._runs = (*self._runs, run)
        self._slots = (*self._slots, _RunSlots(parameters, placed))
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

        **The case and a standing fork refusal answer to the run that ended,
        not to how many runs are drawn**, so both are cleared on every trunk
        Reset, a one-run one included. A refusal names an instant of the run
        that has just started over, so it goes as the setting refusal
        `RunView._reset_now` clears does (`PL-75P5`). The case is a record
        of the trunk's run rather than of the display, so it is rebuilt
        whatever is on screen: a branch it kept but never drew, which
        `PL-08SS`'s fork leaves, would otherwise outlive the run it was taken
        from. Only the layout waits for a second run to drop.
        """

        if self._case is None:
            return

        self._case = BranchedCase(self._runs[0].controller)
        self._fork_refusal = None
        self._chart_view_owed = False

        if len(self._runs) == 1:
            return

        dropped = tuple(zip(self._runs[1:], self._slots[1:], strict=True))
        self._runs = self._runs[:1]
        self._slots = self._slots[:1]

        for run, slots in dropped:
            self._remove_run(run, slots)

        self._rename_runs()

    def _trunk_reset_question(self) -> NewCaseQuestion | None:
        """What the trunk's Reset must ask, or None where it discards no branch's work.

        The trunk's Reset drops every branch drawn beside it
        (`_handle_case_restarted`), and a branch is not the run the reader
        pressed Reset on. So the press asks first wherever a drawn branch
        holds elapsed time or a recorded control change (`PL-W5WX`). A
        dashboard with no case drops nothing on a Reset, so it asks nothing.
        """

        if self._case is None:
            return None

        branches = (
            self._branch_at_stake(index, run)
            for index, run in enumerate(self._runs)
            if index != TRUNK_RUN_INDEX
        )
        at_stake = tuple(branch for branch in branches if branch is not None)

        if not at_stake:
            return None

        return trunk_reset_question(run_label(TRUNK_RUN_INDEX), at_stake)

    @staticmethod
    def _branch_at_stake(index: int, run: RunView) -> BranchAtStake | None:
        """What discarding the branch drawn at `index` would lose, or None where it holds nothing.

        A branch whose snapshot refuses a value still holds work, so it is
        stated from what its controller can say without one: its fork and
        its recorded control changes (`branch_at_stake`). The refusal is
        not handled here. It is the branch's own halt, which its own frame
        states.
        """

        try:
            snapshot: SimulationSnapshot | None = run.snapshot()
        except Exception:
            snapshot = None

        record = run.controller.record() if snapshot is None else snapshot

        return branch_at_stake(
            run_label(index), run.controller.began_at_s, snapshot, len(run.adjustments(record))
        )

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

    def _require_unconditional_values(self, run: RunView) -> None:
        """Refuse a run whose unconditional values are not all inside the region.

        The run's set is read from `app/unconditional_set.py`, so the
        declaration rather than this method decides what the region must
        hold. The region is the main window's, so it owes what
        `window_region` returns for the main window of the layout the Areas
        draw. Every agent this build loads is an inhaled agent, so every run
        owes `INHALED_AGENT`'s tier.

        Args:
            run: The run just placed.

        Raises:
            RuntimeError: A declared value has no widget, or its widget is
                outside the region or inside the layout container. Either is
                a layout that could take a value `docs/MODEL.md` requires
                off the screen, so the dashboard is not built.
        """

        widgets = run.unconditional_widgets()
        misplaced = []

        owed = window_region(
            unconditional_set(INHALED_AGENT), MAIN_WINDOW, len(self._areas.model.windows)
        )

        for value in owed:
            widget = widgets.get(value)

            if widget is None or not _within(widget, self._unconditional_region):
                misplaced.append(value.value)
            elif _within(widget, self._areas):
                misplaced.append(value.value)

        if misplaced:
            raise RuntimeError(
                "the unconditional region does not hold "
                f"{', '.join(misplaced)}, which docs/MODEL.md requires on screen in every "
                "layout (app/unconditional_set.py)"
            )

    def _rename_runs(self) -> None:
        """Hold the compartment selection to the run count, and tell every run.

        Said on every change to the run set rather than once at
        construction. A lone run is given no name, having nothing to be told
        apart from; two runs are named by `run_label`, which is what the
        legend entries call them. The same count decides whether an agent
        selector may be used at all, because two runs share one MAC axis,
        and whether the compartment selection is held to the cap
        (`CompartmentSelection.with_run_count`). Neither legend is told here:
        each names the curves a drawn frame drew, so each hears of the new
        run set from the frame the change owes (`PL-G3K7`, `PL-0LG6`).

        **It draws nothing, and nothing it calls may** (`PL-B1R9`). A frame
        assembled before the last of these has been told is drawn from a run
        set half told that it has changed, so the frame the change owes is
        drawn by whatever changed the run set, once this returns: the press
        that took a branch, the Reset that dropped one, `main()` after the
        window is shown, or the render tick, which draws whenever the run
        count differs from the one the last frame was drawn over (`PL-0LG6`).
        """

        comparing = len(self._runs) > 1
        self._compartment_selection = self._compartment_selection.with_run_count(len(self._runs))

        for index, run in enumerate(self._runs):
            run.set_run_name(run_label(index) if comparing else None)
            run.set_comparing(comparing)

    # ----------------------------------------------------------- branching

    def _handle_fork(self) -> None:
        """Take the branch the panel is set to, and draw it beside the trunk.

        The selector holds two of the three doors, and the point it answers
        with says which: a recorded control event is taken through
        `BranchedCase.fork_at` at its instant, and a mark the trunk has passed
        through `fork_at_mark` with the mark itself (`PL-W4XQ`), so where a
        mark's branch opens is found by the case from the mark rather than
        handed over as a float. Either refusal reaches the notice rather than
        being swallowed: a press is not proof that what the frame offered is
        still there.

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

        point = self._fork_panel.selected_point()

        if point is None:
            self._fork_refusal = FORK_NOTHING_SELECTED_TEXT
            self.present(False)

            return

        try:
            branch = (
                case.fork_at(point.instant_s)
                if point.mark is None
                else case.fork_at_mark(point.mark)
            )
        except SimulationConfigurationError as error:
            self._fork_refusal = refused_setting_notice(error)
            self.present(False)

            return

        self._show_branch(branch)

    def _handle_here_fork(self) -> None:
        """Take the branch where the trunk is paused, stopped on a mark or not.

        The third door (`PL-Y2SL`), and the sequence `docs/ARCHITECTURE.md`
        § "How a learner takes one" describes: a learner pauses at the
        decision point, or a mark stops the run there, and this is how they
        branch there. It names no instant - `BranchedCase.fork_here` forks
        where the trunk stands - so the one thing a caller could get wrong is
        not expressible here.

        Guarded rather than trusted, for the reason `_handle_fork` is. The cap
        is checked here too, so refusing a second branch is a property of the
        dashboard rather than of a hidden widget; and where the trunk stands
        is re-read by the case on the press, because the trunk can be started
        between the frame that drew the button and the press, so the button's
        own frame is not proof that the fork is still there. `fork_here`
        raising is that check, and its reason goes to the notice rather than
        being swallowed.
        """

        case = self._case

        if case is None:
            return

        if len(self._runs) >= MAX_DISPLAYED_RUNS:
            self._fork_refusal = comparing_fork_lock_text()
            self.present(False)

            return

        try:
            branch = case.fork_here()
        except SimulationConfigurationError as error:
            self._fork_refusal = refused_setting_notice(error)
            self.present(False)

            return

        self._show_branch(branch)

    def _show_branch(self, branch: SimulationController) -> None:
        """Draw a branch just taken beside the trunk, and bring the chart comparing them into view.

        Both branch controls end here. The new run's readouts are laid out
        above the chart, so without the scroll the chart the learner branched
        to compare on falls mostly below the fold (`PL-562Z`).
        """

        self._fork_refusal = None
        self.add_run(branch)
        self.present(False)
        self._keep_chart_in_view()

    def _keep_chart_in_view(self) -> None:
        """Scroll the page to the concentration chart, and keep it there until the reader scrolls.

        The new run's widgets reach their final size over several passes of
        layout after the press returns, and each pass moves the chart. So
        the scroll is made now and again each time the page's height changes
        (`_follow_chart`), until the reader scrolls the page themselves or the
        trunk's Reset ends the comparison. It scrolls as little as Qt's
        `ensureWidgetVisible` needs to, so nothing moves where the chart is
        already in view. The scroll goes when v0.6.0's tiled layout replaces
        the scrolling page.
        """

        self._chart_view_owed = True
        self._page_scroll.ensureWidgetVisible(self._concentration_chart, 0, 0)

    def _release_chart_view(self) -> None:
        """Stop holding the chart in view, because the reader has scrolled the page."""

        self._chart_view_owed = False

    def _follow_chart(self) -> None:
        """Bring the chart back into view after a pass of layout, while the page is holding it."""

        if self._chart_view_owed:
            self._page_scroll.ensureWidgetVisible(self._concentration_chart, 0, 0)

    def _restate_fork_panel(self) -> None:
        """Restate both branch controls from the case on a halt, and offer nothing if that raises.

        `_refresh_fork_panel` is otherwise called only at the end of a frame,
        so a halt whose frame failed left "Branch here" live over a trunk
        every other control said had failed, and a press was refused with the
        refusal lost to the next failing frame (`PL-MMNX`). The case answers
        from the trunk's own state, so the restatement needs no frame. On a
        trunk whose frame failed it offers nothing (`PL-T2Q2`).

        Guarded, because it runs inside the halt path, where a raise would
        escape the render path's own guard into the toolkit. A case whose
        answers raise is given an offer of nothing rather than left with the
        last frame's.
        """

        try:
            self._refresh_fork_panel()
        except Exception:
            self._fork_panel.set_offer(
                fork_offer(
                    (),
                    marks=(),
                    comparing=len(self._runs) > 1,
                    here=None,
                    refusal=self._fork_refusal,
                )
            )

    def _refresh_fork_panel(self) -> None:
        """Redraw both branch controls from the trunk's state this tick.

        The points offered are the trunk's own - its keyframes and the marks
        its clock has passed - so a running case adds one every time a
        setting changes or the clock reaches a mark, and the panel has to
        follow; it keeps the reader's selection where that point is still
        offered. The fork at the paused point follows the same tick: it
        appears on the frame the trunk stops on and is gone on the first frame
        drawn after it starts.

        **The paused point and the marks are read from the trunk rather than
        from the displayed runs.** `BranchedCase.fork_here` and `fork_at_mark`
        fork the trunk and refuse a branch outright, so a panel drawn from a
        *branch's* paused point or marks would offer a fork the case cannot
        take - a control that can only apologise, which
        `.claude/rules/expert-review.md` prefers to prevent. The trunk is the
        first displayed run today, but that is an invariant of how the
        dashboard is built rather than one this method needs, and asking the
        case costs one reading of the marks' standings a frame.
        """

        if self._case is None:
            return

        self._fork_panel.set_offer(
            fork_offer(
                self._case.fork_points_s,
                marks=self._case.mark_fork_points,
                comparing=len(self._runs) > 1,
                here=self._case.here_fork_point,
                refusal=self._fork_refusal,
            )
        )

    def _section_divider(self) -> QFrame:
        """The rule between two sections of the chart column."""

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(SECTION_DIVIDER_HEIGHT)
        divider.setStyleSheet(foreground_stylesheet(GRIDLINE))

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

        A frame is owed when a change asked for one (`present(True)`), when
        the run set differs from the one the last frame was drawn over, and
        when a run's record differs from the one its view last wrote
        (`RunView.owes_a_frame`). The last two are read from the runs rather
        than asked for by whatever changed them, so a run that stops itself
        inside its own step tick is redrawn within one tick (`PL-T995`), a
        run added without a frame is drawn on the next (`PL-0LG6`), and a
        path added later is covered without being named (`PL-X7D5`).

        The pending flag is cleared before the frame is drawn, so a frame
        that raises cannot leave the change that asked for it owed forever;
        the run count and each run's record are stored where they are
        written, the halt included, so neither can either.
        """

        if (
            not any(run.is_running for run in self._runs)
            and not self._render_pending
            and len(self._runs) == self._drawn_run_count
            and not any(run.owes_a_frame for run in self._runs)
        ):
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
        not the published fraction it was drawn from. Both legends are told
        what the frame drew once both plots have drawn it, and not before,
        so where the frame fails they go on naming the curves still on the
        plot (`PL-G3K7`).

        Raises:
            ValueError: If the runs have come to be on different agents
                since construction (`assemble_chart_frame`).
        """

        # Stored before anything can raise: a frame that fails over a new run
        # set is answered by the halt it raises, and is not retried every tick.
        self._drawn_run_count = len(self._runs)
        selection = self._compartment_selection
        snapshots = tuple(run.snapshot() for run in self._runs)
        inputs = tuple(
            RunInput(run_label(index), run.controller, snapshot, run.adjustments(snapshot))
            for index, (run, snapshot) in enumerate(zip(self._runs, snapshots, strict=True))
        )
        frame = assemble_chart_frame(
            inputs,
            self._time_base,
            selection.shown,
            plot_width_px=max(
                self._concentration_chart.plot_width_px(), self._wash_in_chart.plot_width_px()
            ),
        )
        self._concentration_chart.draw(frame)
        self._wash_in_chart.draw(frame)
        self.compartment_selection_changed.emit(selection)
        self._wash_in_legend.set_run_count(len(frame.runs))
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
        """Make one change to every displayed run, or have the first of them refuse it.

        The marks are the case's, so a mark added to one run and refused by
        another would leave two runs of one case answering different
        questions - which is exactly the state this panel exists to prevent.
        The loop writes run by run and stops at the first refusal, with no
        second phase: every `BookmarkSet` operation is a pure function of the
        set and the mark, the displayed runs hold equal sets, and nothing
        interleaves with a synchronous loop, so either every run accepts or
        the first run refuses and none has changed. The equal sets carry
        that, and `_refresh_bookmarks` halts the dashboard on the frame they
        stop being equal (`PL-LHBY`). A write computed against copies and
        committed only once every run had accepted was described here and
        never built; it is not built now either, because it would guard an
        invariant the frame already refuses louder, and the fuzz `PL-RBMK`
        records found no divergence.

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

    def _handle_compartment_request(self, quantity: RecordedQuantity, shown: bool) -> None:
        """Answer a reader's click in the legend: change the selection and draw at once.

        The legend only asks (`PL-VN6M`). The frame drawn next is assembled
        from the selection this leaves - a click over the two-compartment cap
        included, where the selection rather than the legend decides which
        compartment makes room - and the legend's boxes are written from the
        same selection once that frame has drawn (`_refresh_view`). Where the
        frame fails, nothing writes them, and the legend puts the clicked box
        back to the selection it last showed, which is the frame still on
        the plot (`PL-G3K7`).
        """

        self._compartment_selection = self._compartment_selection.with_compartment(quantity, shown)
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
        run stops. Each run states its halt from its controller's record,
        which builds no compartment value, before the frame is attempted,
        because the frame is what just failed and may fail again for the
        same cause - two runs that have come to be on different agents, say,
        or a snapshot whose own values refuse - and a halt presented only
        through it would never be seen (`PL-25KS`, `PL-7DJK`). The branch
        controls are restated from the case for the same reason
        (`_restate_fork_panel`, `PL-MMNX`). The trunk records that its frame
        failed, so the case then offers no branch at all: one opened now would
        be drawn by the same frame and halt on it (`PL-T2Q2`). A presentation
        that fails afterwards cannot unwind the halt.
        """

        for run in self._runs:
            run.halt(error, in_frame=True)

        for run in self._runs:
            run.present_halt()

        self._restate_fork_panel()

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
