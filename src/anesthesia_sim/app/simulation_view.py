"""The shared part of the dashboard, which every displayed run uses, in PySide6.

`PL-B9PY` divided the dashboard into a part that all runs share and a part
for each run. `SimulationView` is the shared part. It holds what two runs
cannot each have a copy of: the compartment selection, the time base, the
Areas and the Views in them, the marks and the branch control. It also holds
one `RunView` per run, and each `RunView` holds everything else for its run.
`app/area_layout.py` builds the Views through the View registry, each from
the View contract's context (`app/view_contract.py`, `PL-TH35`). So this class
names no View, except to keep the concentration chart in view after a branch.

**The unconditional region is outside the splitters** (`PL-NWTM`). The
unconditional region holds the values that must be on screen at all times.
Each run's transport row, its notice banner, its readouts and its
control-change record sit in a band across the top of the page. The use
disclaimer sits in a line across the foot of the page. `docs/MODEL.md`
§ "Minimum displayed outputs" requires those values on screen in every
Workspace, and `app/unconditional_set.py` declares which values they are.
`_place_run` rejects a run when the band does not hold every value that the
run declares. Under the band is the Workspace tab strip, and under the strip
are the Areas of the current Workspace (`PL-2KXB`). `app/area_layout.py`
draws the Areas from that Workspace's layout model, so a reader can drag the
borders between them (`PL-W9P6`). The Areas are the layout container. No
widget in the band sits inside an Area, so no split, join or close of an Area
and no Workspace switch can affect the band.

**The dashboard owns the Workspaces** (`PL-2KXB`). It holds the
`WorkspaceSet` and opens on its current Workspace. When the tab strip hands it
a set whose current Workspace differs from the drawn one, it switches the
Areas. A switch changes which Views are drawn and never touches a run
(`PL-WV9K` Q6). A Workspace pinned to a run draws that run alone, with the
run's name on every Area's header. If the pinned run is not open, every Area
says so in place of its Views.

**One read, every View, then every run.** `_refresh_view` reads one
snapshot per run and assembles one `ChartFrame` through `app/chart_frame.py`
for each time window a View asks for. Each chart's window is its own
(`PL-L59K`). `_refresh_view` hands each View the frame for its window, and
only then refreshes each run from the same snapshot. So the readouts, the
traces and the sentences beside them all show one instant of one run
(decision D2). Every claim in a caption comes from `app/dashboard_frame.py`.
This class formats nothing, and it decides nothing that a reader interprets.

**Two cadences, kept apart** (decision D7). Each run's own timer steps that
run. This view's render timer draws, but only while a run is running or a
frame is owed, meaning a redraw is due. A frame is owed after a coalesced
slider change (`PL-R2YM`), after a change to the run set, or when a run's
record differs from what its view last wrote (`PL-X7D5`). A frame that cannot
be drawn halts every run, because an exception raised in the shared drawing
path cannot be attributed to any one run. No wall clock is read anywhere.

**The legend is a frame widget** (`PL-G3K7`). The legend's View hands it the
selection that a frame was assembled from, but only after the plot has drawn
that frame. So the legend's boxes name the curves on the plot, even when the
frame that a click asked for fails.

**Hover belongs to the chart** (decision D6). `qt_chart` shows its hover
readout whenever the pointer is over a drawn point, whether the run is running
or paused. The dashboard adds nothing to it.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, replace
from functools import partial
from typing import Final

from PySide6.QtCore import Qt, QTimer, Signal
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
from anesthesia_sim.app.chart_frame import RunInput, assemble_chart_frame
from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
)
from anesthesia_sim.app.controller import BranchedCase, SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    FORK_NOTHING_SELECTED_TEXT,
    MAX_DISPLAYED_RUNS,
    REMOVE_NOTHING_SELECTED_TEXT,
    RENDER_INTERVAL_S,
    TRUNK_RUN_INDEX,
    USE_DISCLAIMER_TEXT,
    BranchAtStake,
    ComparedRuns,
    NewCaseQuestion,
    RunMarks,
    bookmark_panel,
    branch_at_stake,
    comparing_fork_lock_text,
    fork_offer,
    refused_setting_notice,
    run_label,
    trunk_reset_question,
)
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.qt_widgets import BookmarkDialog, BookmarksPanel, ForkPanel, styled_label
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.stylesheets import (
    foreground_stylesheet,
    page_stylesheet,
    panel_stylesheet,
    scroll_area_stylesheet,
)
from anesthesia_sim.app.theme import (
    GRIDLINE,
    PAGE_PADDING,
    PAGE_SPACING,
    PANEL_PADDING,
    SECTION_DIVIDER_HEIGHT,
    VIEW_ROW_SPACING,
    WARNING,
)
from anesthesia_sim.app.unconditional_set import INHALED_AGENT, unconditional_set, window_region
from anesthesia_sim.app.view_contract import ViewRequests
from anesthesia_sim.app.views import ConcentrationView
from anesthesia_sim.app.workspace_tabs import WorkspaceTabs
from anesthesia_sim.core.concentration import fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND
from anesthesia_sim.layout.model import MAIN_WINDOW
from anesthesia_sim.layout.run_identity import RunId, RunIdentities
from anesthesia_sim.layout.shipped import shipped_workspaces
from anesthesia_sim.layout.workspace import PinnedRunAbsent, WorkspaceSet

#: The fractions of the unconditional region's width that the run rows and
#: the control-change records take. They match the shares that the charts and
#: the accounting sidebar had before the dashboard opened on the shipped
#: Workspaces, and that split is the width `PL-J8K2` Q3 gave the records. In a
#: window 1366 px wide, the run rows' share of 0.82 leaves room for all seven
#: panels in one run's readout row (`PL-F2YS`). A box layout's stretch factor
#: is a whole number, so each share is given in hundredths.
_RUN_ROWS_STRETCH: Final = 82
_RECORD_COLUMN_STRETCH: Final = 18

#: Object names the page and the case's controls are styled through.
_PAGE_NAME: Final = "dashboardPage"
_REGION_NAME: Final = "unconditionalRegion"
_RECORD_COLUMN_NAME: Final = "controlRecordColumn"
_CASE_SECTION_NAME: Final = "caseSection"


def _within(widget: QWidget, ancestor: QWidget) -> bool:
    """Whether `ancestor` is `widget` or one of the widgets it sits inside."""

    current: QWidget | None = widget

    while current is not None:
        if current is ancestor:
            return True

        current = current.parentWidget()

    return False


@dataclass(frozen=True, slots=True)
class InterfaceText:
    """One string the dashboard holds, and whether a reader can see it now (`PL-904Y`)."""

    text: str
    visible: bool


def _seen_by_reader(widget: QWidget) -> bool:
    """Whether a reader can see `widget` now, scrolling aside.

    The widget and every widget it sits inside are shown, its window is shown
    and not minimized, and it has an area to draw in. A widget scrolled out
    of view still counts as seen, because the reader reaches it by scrolling
    without opening, choosing or switching anything. A View that no Area
    draws has no shown window, so it is not seen.
    """

    return (
        widget.isVisible()
        and not widget.window().isMinimized()
        and widget.width() > 0
        and widget.height() > 0
    )


def _widget_text(widget: QWidget) -> Iterator[InterfaceText]:
    """The strings `widget` draws itself, not those of the widgets inside it."""

    seen = _seen_by_reader(widget)

    if isinstance(widget, QDialog):
        yield InterfaceText(widget.windowTitle(), seen)

    if isinstance(widget, QLabel | QAbstractButton):
        yield InterfaceText(widget.text(), seen)

    if isinstance(widget, QAbstractButton) and widget.accessibleName():
        yield InterfaceText(widget.accessibleName(), seen)
    elif isinstance(widget, QComboBox):
        current = widget.currentIndex()

        for index in range(widget.count()):
            yield InterfaceText(widget.itemText(index), seen and index == current)


def _spaced_column(widget: QWidget, spacing: int) -> QVBoxLayout:
    """A vertical layout on `widget` with no margins and the given spacing."""

    column = QVBoxLayout(widget)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(spacing)

    return column


def _holder(
    layout: QBoxLayout, widgets: Sequence[QWidget], *, before_stretch: bool = False
) -> QWidget:
    """Wrap one run's widgets for a shared layout, so that they can be taken out again.

    The run's widgets go into a holder rather than straight into the layout,
    because the dashboard's run set changes while the dashboard is alive. A
    run added after construction has to land in the same place in each of
    these layouts that it would have had at construction. A run taken off has
    to leave nothing behind. With one holder per run per layout, each of
    those is a single insertion or a single deletion. The holder's own layout
    has no margins, so the holder itself is invisible.

    Args:
        layout: The shared layout to add the holder to.
        widgets: This run's widgets for that layout, in order.
        before_stretch: True where the layout ends in a stretch and the run's
            widgets must stay in front of it, as in the record column.

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
    """Where one displayed run's widgets sit among the layouts that every run shares.

    A run's setting controls are not among them. They are shown by the
    `parameter_controls` View, which builds copies of its own in whichever
    Areas show it (`PL-TH35`, `PL-2KXB`).

    Attributes:
        placed: Every widget that this run put into a shared layout. For any
            run after the first, it also holds the readings that the run put
            into the first run's readout panels. Removing the run means
            deleting these widgets.
    """

    placed: tuple[QWidget, ...]


class SimulationView(QWidget):
    """The dashboard over one or two runs on one agent.

    Attributes:
        presented_frames: How many frames `_refresh_view` has drawn. What
            the tests count instead of the Flet build's page updates, and
            what the coalescing rule (`PL-R2YM`) is about.
    """

    compartment_selection_changed = Signal(object)
    """Emitted with the selection a frame was assembled from, once every View has drawn it.

    It is not emitted when the selection is set, whether by a reader's request
    or by a change to the run set. When it was emitted at that point, a frame
    that then failed left the legend naming curves that the plot was not
    drawing (`PL-G3K7`). Every View is handed the same selection in its
    `ViewTick`. A legend outside the Areas connects to this signal, so a
    legend that has been closed simply stops receiving it (`PL-VN6M`).
    """

    def __init__(
        self,
        controllers: Sequence[SimulationController],
        parent: QWidget | None = None,
        *,
        case: BranchedCase | None = None,
        run_identities: RunIdentities | None = None,
        workspaces: WorkspaceSet | None = None,
    ) -> None:
        """Build the dashboard with one `RunView` for each of `controllers`, and draw nothing yet.

        The dashboard is first presented after `show()`, once the layout has
        settled, because a frame is assembled from the plot's laid-out width.
        `main.py` calls `present(False)` after the window is shown.

        Args:
            controllers: The runs, in drawing order. The first is the
                reference run for the MAC ruler and the clinical references.
            parent: The Qt parent.
            case: The case whose trunk is the first run, if there is one. The
                branch control offers instants from this case and takes
                branches through it. Without a case the branch control is not
                shown. A dashboard given controllers that belong to no case
                has nothing to branch, and a control that could only refuse
                would present itself as working. When a case is given, it must
                be the case rooted in `controllers[0]`. Two runs drawn on one
                axis claim to be one patient under two managements. A case
                with some other trunk would attach that claim to the wrong run.
            run_identities: The source from which each placed run takes its
                identity. A test passes its own to pin a run by an identity it
                knows.
            workspaces: The Workspaces the tab strip offers, opened on the
                current one. By default, the shipped Workspaces.

        Raises:
            ValueError: If no run is given, if more than
                `MAX_DISPLAYED_RUNS` are, if the runs are not all on one
                agent, or if `case` is not rooted in the first of them. The
                runs must share one agent because one ×MAC ruler, one
                MAC-awake band and one 1 MAC line are drawn across the chart
                that every run shares. All three are the agent's own published
                values. With two agents on one axis, one run's traces would be
                read against the other agent's divisor. That is a correct
                number under the wrong label, which `CLAUDE.md`'s
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
        # Where every run this dashboard places takes its identity, so no
        # number is given out twice in the session and a dropped branch's is
        # never a later branch's (`PL-7Z84`).
        self._run_identities = RunIdentities() if run_identities is None else run_identities
        # The reader's Workspaces, including the current one that the Areas
        # draw. Here the current Workspace's layout and View states are the
        # ones it had when it was last drawn. The `workspaces` property reads
        # the live ones from the Areas (`PL-2KXB`).
        self._workspaces = shipped_workspaces() if workspaces is None else workspaces
        self._runs: tuple[RunView, ...] = ()
        self._slots: tuple[_RunSlots, ...] = ()
        # Why the branch last asked for was not taken, or None. Held across
        # ticks for the reason `RunView._rejected_setting_notice` is: a
        # refusal written into the panel and then overwritten by the next
        # render tick would be gone before a reader could read it.
        self._fork_refusal: str | None = None
        # The compartments that both runs are drawn with. This view owns the
        # selection and hands it to the legend and to every frame. So neither
        # reads it back from the other, and closing the legend loses nothing
        # (`PL-VN6M`).
        self._compartment_selection = INITIAL_COMPARTMENT_SELECTION
        self._render_pending = False
        # How many runs the last frame attempted was drawn over; `render_tick`
        # draws when the run set has changed since (`PL-0LG6`).
        self._drawn_run_count = 0
        # The Views the last frame was attempted for, and whether it failed.
        # A View owes a frame only while it has not been offered one, so a
        # frame that failed for these Views is not retried every tick.
        self._offered_views: tuple[QWidget, ...] = ()
        self._frame_failed = False
        self.presented_frames = 0
        # Whether the page is holding the concentration chart in view, from
        # a branch taken until the reader scrolls the page themselves
        # (`_keep_chart_in_view`, `PL-562Z`).
        self._chart_view_owed = False

        # The marks belong to the *case* and not to any one run. That is why
        # they are built here beside the Areas rather than in `RunView`
        # (`docs/ARCHITECTURE.md` § "Where new code belongs": a control shared
        # between runs must not be duplicated into each). Every run holds its
        # own copy of the marks, and this code is the only thing that writes
        # them, so the copies stay equal by construction. The arrangement exists
        # to make one failure impossible: two runs compared at two different
        # heights because a learner typed one of them twice.
        self._bookmarks_panel = BookmarksPanel()
        self._bookmark_dialog: BookmarkDialog | None = None
        self._bookmarks_panel.edit_button.clicked.connect(self._open_bookmark_dialog)

        # Where a branch is taken. Beside the marks for the reason they are
        # here at all: both offer instants of the *case*, so neither belongs
        # inside a `RunView`.
        self._fork_panel = ForkPanel()
        self._fork_panel.take_button.clicked.connect(self._handle_fork)
        self._fork_panel.here_button.clicked.connect(self._handle_here_fork)

        self._build_page()

        for controller in controllers:
            self._place_run(controller)

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

        The unconditional region comes first. For each run it holds the
        transport row, the notice banner and the readouts, and every run's
        control-change record sits in a column to their right (`PL-J8K2` Q1
        and Q3). The notice banners sit under the transport rows and above
        every displayed value. So a reader sees a halted run's notice before
        the values that the notice explains. Under the region comes the
        Workspace tab strip, directly above the Areas it switches (`PL-QW1Z`
        Q1). Then come the Areas, which take the spare height.
        `app/area_layout.py` draws them from the current Workspace's layout. It
        builds each Area's View through the View registry, from the state the
        Workspace keeps for it (`PL-TH35`). So a reader can drag the borders
        between the Areas and choose any View for any Area. Under the Areas
        come the case's controls, the marks and the branch control. The use
        disclaimer is the page's last line.

        No run is placed here. Instead, every layout that a run adds widgets
        to is kept, so that `_place_run` can fill the layouts in the same
        order at construction and when a learner takes a branch. A page laid
        out for the run set it was first built with could not gain a run
        without being rebuilt.
        """

        page = QWidget()
        page.setObjectName(_PAGE_NAME)
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        page.setStyleSheet(page_stylesheet(_PAGE_NAME))
        column = QVBoxLayout(page)
        column.setContentsMargins(PAGE_PADDING, PAGE_PADDING, PAGE_PADDING, PAGE_PADDING)
        column.setSpacing(PAGE_SPACING)

        column.addWidget(self._build_unconditional_region())

        self._tabs = WorkspaceTabs(
            self._workspaces, self._change_workspaces, self._open_runs, live=lambda: self.workspaces
        )
        requests = ViewRequests(self._handle_frame_request, self._handle_compartment_request)
        current = self._workspaces.current
        self._areas = AreaLayout(current.layout, requests, states=current.view_state)
        self._areas.views_changed.connect(partial(self.present, False))
        # The strip and the Areas sit together, with no page spacing between
        # them, so the strip reads as the Areas' own.
        workspace = QWidget()
        workspace_column = _spaced_column(workspace, 0)
        workspace_column.addWidget(self._tabs)
        workspace_column.addWidget(self._areas, 1)
        column.addWidget(workspace, 1)
        column.addWidget(self._build_case_section())
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
        """Build the band that holds every run's unconditional values, with no runs in it yet.

        The band's left column stacks every run's transport row, then every
        notice banner, then the first run's readout section. A later run's
        readouts join the first run's panels (`RunView.show_readings_of`).
        While runs are compared, each run's delivered concentration sits on
        its own transport row. So a later run's readout section is not shown
        (`PL-QLZ5`). The band's right column holds every run's control-change
        record. That column scrolls within itself, so a long record never
        makes the band taller than the rows beside it (`PL-J8K2` Q3). The two
        columns split the band's width in the same shares as the charts and
        the sidebar split the Areas' width. So one run's seven readouts stand
        in one row in a 1366 px window (`PL-F2YS`). Nothing new is drawn
        around the region (`PL-J8K2` Q4).

        Returns:
            The region. `unconditional_region` gives access to this widget.
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

        row.addWidget(run_rows, _RUN_ROWS_STRETCH)
        row.addWidget(record_scroll, _RECORD_COLUMN_STRETCH)
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

    @property
    def tab_strip(self) -> WorkspaceTabs:
        """The Workspace tab strip above the Areas."""

        return self._tabs

    @property
    def workspaces(self) -> WorkspaceSet:
        """The reader's Workspaces, with the current one as the Areas draw it now.

        The current Workspace carries the layout after every drag and the
        state of every View drawn. So when the reader duplicates, leaves or
        saves a Workspace, the result matches what the reader sees
        (`PL-2KXB`).
        """

        current = self._workspaces.current
        drawn = replace(current, layout=self._areas.model, view_state=self._areas.view_states())

        return self._workspaces.replace(self._workspaces.active, drawn)

    def _open_runs(self) -> tuple[RunId, ...]:
        """The identities of the runs open now, in drawing order."""

        return tuple(run.run_id for run in self._runs)

    def _change_workspaces(self, workspaces: WorkspaceSet) -> None:
        """Take the tab strip's new set, and switch the Areas if its current Workspace differs.

        A switch draws the incoming Workspace's layout, builds each View from
        the state the Workspace kept for it, and leaves every run as it was
        (`PL-WV9K` Q6). Some changes keep the current Workspace's layout and
        Views, such as a rename or a pin. Such a change keeps the drawn Views
        and only draws a new frame, because a pin changes which runs the Views
        show.
        """

        drawn = self.workspaces.current
        current = workspaces.current
        self._workspaces = workspaces

        if (current.layout, current.view_state) != (drawn.layout, drawn.view_state):
            self._areas.load(current.layout, current.view_state)
        else:
            self.present(False)

        self._tabs.show_set(workspaces)

    def _build_case_section(self) -> QWidget:
        """Build the case's controls under the Areas: first the marks, then the branch control.

        Neither is a View, because neither belongs to a plot. Both deal with
        instants of the case rather than of any one run or plot. So neither
        sits inside a `RunView` or an Area. Where they sit is a placeholder
        (`PL-TH35`).
        """

        panel = QWidget()
        panel.setObjectName(_CASE_SECTION_NAME)
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        panel.setStyleSheet(panel_stylesheet(_CASE_SECTION_NAME))
        column = QVBoxLayout(panel)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.setSpacing(VIEW_ROW_SPACING)

        # The marks get a section of their own. They are not placed inside the
        # concentration chart's View, although they are most often read
        # against that chart. There are two reasons, and the second is the
        # stronger. First, the marks belong to the case rather than to either
        # plot, so nesting them in one plot's chrome would say otherwise.
        # Second, `PL-F9TQ` limits what may stand between a chart heading and
        # its plot. A control placed there would restart the build-up of
        # items there that `PL-F9TQ` stopped.
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

        run = RunView(controller, self, run_id=self._run_identities.mint())

        if not self._runs:
            # Only the first run's restart is a new case: a branch's Reset
            # returns it to the fork it opened at, which leaves the case and
            # every other run of it standing.
            run.case_restarted.connect(self._handle_case_restarted)
            run.ask_before_reset(self._trunk_reset_question)

        run.presentation_requested.connect(self.present)
        readout_section = _holder(self._readout_column, (run.build_readout_section(),))
        placed: tuple[QWidget, ...] = (
            _holder(self._transport_column, (run.build_transport_row(),)),
            _holder(self._notice_column, (run.build_notice(),)),
            readout_section,
            _holder(self._record_column, (run.build_control_record(),), before_stretch=True),
        )
        # A later run's readouts join the first run's panels, so two runs
        # read as one block of seven (`PL-F2YS`); they leave with the run.
        # The first run's heading then states the substance and 1 MAC the
        # runs share, and the later run's delivered concentration moves to its
        # transport row, so its readout section has nothing left to show and
        # takes no height (`PL-QLZ5`).
        if self._runs:
            placed = (*placed, *self._runs[0].show_readings_of(run))
            readout_section.setHidden(True)

        self._require_unconditional_values(run)
        self._runs = (*self._runs, run)
        self._slots = (*self._slots, _RunSlots(placed))
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
            self._branch_at_stake(run)
            for index, run in enumerate(self._runs)
            if index != TRUNK_RUN_INDEX
        )
        at_stake = tuple(branch for branch in branches if branch is not None)

        if not at_stake:
            return None

        return trunk_reset_question(run_label(self._runs[TRUNK_RUN_INDEX].run_id), at_stake)

    @staticmethod
    def _branch_at_stake(run: RunView) -> BranchAtStake | None:
        """What discarding this drawn branch would lose, or None where it holds nothing.

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
            run_label(run.run_id), run.controller.began_at_s, snapshot, len(run.adjustments(record))
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
        apart from. Two runs are named by `run_label` from each run's
        identity, which is what the legend entries call them. `docs/MODEL.md`
        names a value's run whenever another run is drawn anywhere. Every run
        is drawn in this dashboard until a run can be drawn elsewhere, so that
        moment is the one at which this dashboard holds more than one run
        (`PL-7Z84`). The same count decides whether an agent
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

        for run in self._runs:
            run.set_run_name(run_label(run.run_id) if comparing else None)
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

        compared = self._compared_runs()

        if compared is not None:
            # `MAX_DISPLAYED_RUNS` is two, so a second run on the chart is the cap.
            self._fork_refusal = comparing_fork_lock_text(compared)
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

        compared = self._compared_runs()

        if compared is not None:
            # `MAX_DISPLAYED_RUNS` is two, so a second run on the chart is the cap.
            self._fork_refusal = comparing_fork_lock_text(compared)
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
        """Draw a branch just taken beside the trunk, and bring the charts comparing them into view.

        Both branch controls finish by calling this method. The new run's
        readouts are laid out above the chart. So without the scroll, most of
        the chart that the learner branched in order to compare would fall
        below the visible part of the page (`PL-562Z`).
        """

        self._fork_refusal = None
        self.add_run(branch)
        self.present(False)
        self._keep_chart_in_view()

    def _keep_chart_in_view(self) -> None:
        """Scroll the page to the concentration chart, and keep it there until the reader scrolls.

        The chart is the plot of the first Area that shows a concentration
        chart View, or the Areas themselves where no Area does
        (`_chart_in_view`). After the press returns, the new run's widgets
        reach their final size over several layout passes, and each pass
        moves the chart. So the page scrolls once now, and once more each time
        the page's height changes (`_follow_chart`). This continues until the
        reader scrolls the page themselves or the trunk's Reset ends the
        comparison. Each scroll goes only as far as Qt's `ensureWidgetVisible`
        needs, so nothing moves when the chart is already in view. This
        scrolling will be removed when v0.6.0's tiled layout replaces the
        scrolling page.
        """

        self._chart_view_owed = True
        self._page_scroll.ensureWidgetVisible(self._chart_in_view(), 0, 0)

    def _chart_in_view(self) -> QWidget:
        """The plot that `_keep_chart_in_view` keeps on screen, or the Areas where none is shown."""

        return next(
            (view.chart for view in self._areas.views() if isinstance(view, ConcentrationView)),
            self._areas,
        )

    def _release_chart_view(self) -> None:
        """Stop holding the chart in view, because the reader has scrolled the page."""

        self._chart_view_owed = False

    def _follow_chart(self) -> None:
        """Bring the chart back into view after a pass of layout, while the page is holding it."""

        if self._chart_view_owed:
            self._page_scroll.ensureWidgetVisible(self._chart_in_view(), 0, 0)

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
                    comparing=self._compared_runs(),
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
                comparing=self._compared_runs(),
                here=self._case.here_fork_point,
                refusal=self._fork_refusal,
            )
        )

    def _compared_runs(self) -> ComparedRuns | None:
        """What the trunk and its branch are called while both are drawn, or None while one is."""

        if len(self._runs) < MAX_DISPLAYED_RUNS:
            return None

        trunk, branch = self._runs

        return ComparedRuns(run_label(trunk.run_id), run_label(branch.run_id))

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
        pending flag first.

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
        """Draw a frame when one is owed or a run is running, and halt all runs if drawing fails.

        A frame is owed in four cases: when a change asked for one
        (`present(True)`), when the run set differs from the one the last frame
        was drawn over, when a run's record differs from the one its view last
        wrote (`RunView.owes_a_frame`), and when a View owes one
        (`View.owes_a_frame`). A View owes a frame until it has been offered
        its first, or when it is a chart wider than the frame it drew was
        sampled for. The last three cases are read from the runs and the Views. They
        are not asked for by whatever changed them. That design has these
        effects:

        - A run that stops itself inside its own step tick is redrawn within
          one tick (`PL-T995`).
        - A run added without a frame is drawn on the next tick (`PL-0LG6`).
        - A View that a reader chooses for an Area is drawn at once, through
          `AreaLayout.views_changed`, and on the next tick if nothing has drawn
          it yet (`PL-TH35`).
        - A chart whose Area a reader widens is redrawn, although the window
          kept its size (`PL-9LNF`).
        - A path added later is covered without being named (`PL-X7D5`).

        The pending flag is cleared before the frame is drawn. So a frame
        that raises cannot leave the change that asked for it owed forever.
        The run count and each run's record are stored where they are written,
        including in the halt, so neither of them can leave a frame owed
        forever either.
        """

        if (
            not any(run.is_running for run in self._runs)
            and not self._render_pending
            and len(self._runs) == self._drawn_run_count
            and not any(run.owes_a_frame for run in self._runs)
            and not self._views_owe_a_frame()
        ):
            return

        self._render_pending = False

        try:
            self._refresh_view()
        except Exception as error:
            self._halt_every_run(error)

    def _views_owe_a_frame(self) -> bool:
        """Whether a View owes a frame that has not already failed for the same Views.

        A View chosen while every frame fails, or a chart widened then, would
        otherwise owe a frame on every tick. Each tick would assemble the
        frame again and halt every run again.
        """

        if self._frame_failed and self._areas.views() == self._offered_views:
            return False

        return self._areas.owes_a_frame

    def _refresh_view(self) -> None:
        """Read every run once, assemble a frame per window, draw each View, then refresh each run.

        Each chart View asks for its own window (`PL-L59K`). The dashboard
        assembles one frame for each distinct window, sampled for the widest
        plot that asks for it. So no plot draws a chord wider than a pixel
        (`PL-GS3R`). A chord is the straight line drawn between two
        neighbouring samples. Charts at the same window share one frame,
        rather than each having a frame at its own width. The two plots'
        widths differ by about 53 px at every application-window width
        measured. So a frame for each plot would mean two assemblies on every
        tick, and two plots at the same window would not draw the same
        instants (`PL-9LNF`). The adapter hands each View the frame for its
        window in its `ViewTick` (`PL-TH35`). Each legend is told what its
        plot drew only after the plot has drawn it. So where the frame fails,
        the legend goes on naming the curves still on the plot (`PL-G3K7`).

        **A pinned Workspace draws its run alone** (`PL-WV9K` Q6). Its Views
        are handed frames assembled from the pinned run only, and the run's
        name is on every Area. Where the pinned run is not open, no View is
        drawn and every Area says so. Either way, a frame is still assembled
        over every open run for each window, so its checks still run. Each run
        is refreshed from its own snapshot, so a pin never changes a readout.

        Raises:
            ValueError: If the runs have come to use different agents since
                construction (`assemble_chart_frame`).
        """

        # Stored before anything can raise: a frame that fails over a new run
        # set, or for new Views, is answered by the halt it raises, and is not
        # retried every tick.
        self._drawn_run_count = len(self._runs)
        self._offered_views = self._areas.views()
        self._frame_failed = True
        selection = self._compartment_selection
        snapshots = tuple(run.snapshot() for run in self._runs)
        inputs = tuple(
            RunInput(run_label(run.run_id), run.controller, snapshot, run.adjustments(snapshot))
            for run, snapshot in zip(self._runs, snapshots, strict=True)
        )
        # With no chart shown, one frame is still assembled, at "Fit run" and
        # the narrowest sampling. Its checks therefore still run, such as the
        # check for runs that have come to use different agents, and they halt
        # the runs whatever the Areas hold.
        requests = self._areas.frame_requests() or {None: 0.0}
        frames = {
            time_base: assemble_chart_frame(
                inputs, time_base, selection.shown, plot_width_px=width_px
            )
            for time_base, width_px in requests.items()
        }
        shown = self._workspaces.current.shown_runs(self._open_runs())

        if isinstance(shown, PinnedRunAbsent):
            self._areas.show_pin(run_label(shown.pinned), absent=True)
        else:
            pinned = self._workspaces.current.pinned_run
            self._areas.show_pin(None if pinned is None else run_label(pinned), absent=False)
            drawn = [i for i, run in enumerate(self._runs) if run.run_id in shown]
            view_frames = frames

            if len(drawn) < len(self._runs):
                view_frames = {
                    time_base: assemble_chart_frame(
                        tuple(inputs[i] for i in drawn),
                        time_base,
                        selection.shown,
                        plot_width_px=width_px,
                    )
                    for time_base, width_px in requests.items()
                }

            self._areas.refresh(
                view_frames,
                tuple(snapshots[i] for i in drawn),
                tuple(self._runs[i] for i in drawn),
                selection,
            )

        self._frame_failed = False
        self.compartment_selection_changed.emit(selection)

        for run, snapshot in zip(self._runs, snapshots, strict=True):
            run.refresh(snapshot)

        self._refresh_bookmarks(snapshots)
        self._refresh_fork_panel()
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
                RunMarks(run_label(run.run_id), snapshot.bookmark_standings)
                for run, snapshot in zip(self._runs, snapshots, strict=True)
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

    def _handle_frame_request(self) -> None:
        """Draw at once for a View that changed its own drawing setting, such as its window.

        A chart's window is the chart's own (`PL-L59K`). Changing it touches
        no simulation state. The time base is a view control. It is never
        disabled, and Reset leaves it alone (`PL-012`).
        """

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

    def interface_text(self) -> tuple[InterfaceText, ...]:
        """Every string the dashboard holds, each marked with whether a reader can see it now.

        This is the one definition of "on screen" that the whole-interface
        tests assert through (`PL-904Y`). It covers every label and every
        button, the name that assistive technology announces for each, every
        entry of every combo box, every window and dialog title, and the text
        that every View paints itself, such as its plot's axis titles
        (`View.painted_strings`). The hover readout is not standing text. The
        chart's own tests check it.

        It walks the window, and a dialog the dashboard opens is a child of
        it, so the walk reaches that too. Every View the dashboard holds is
        in the window, because the adapter deletes a View that no Area draws
        any more and keeps only its saved state (`PL-TH35`). So no string
        can move out of the walk's reach while it is still held. A window
        broken out of the main one (`ROADMAP.md` planned-milestone item 34,
        not yet built) is to be added to this walk when it is built.

        A string is visible where `_seen_by_reader` holds for the widget
        that draws it. Of a combo's entries, only the current one is visible:
        the rest are a click away and not on screen. A widget hidden until
        its condition holds and a window that is minimized are held and not
        visible.
        """

        return tuple(self._interface_text())

    def interface_strings(self) -> tuple[str, ...]:
        """Every string the dashboard holds, whether or not a reader can see it now.

        Use it to show that something is never said anywhere, since a hidden
        string can be shown at any moment. To show that a reader is told
        something, use `visible_strings`.
        """

        return tuple(text.text for text in self._interface_text())

    def visible_strings(self) -> tuple[str, ...]:
        """The strings a reader can see now, in every window the dashboard owns.

        Use it to show that a reader is told something. A string in a hidden
        widget is not among them.
        """

        return tuple(text.text for text in self._interface_text() if text.visible)

    def _interface_text(self) -> Iterator[InterfaceText]:
        window = self.window()
        yield InterfaceText(window.windowTitle(), _seen_by_reader(window))

        for view, text in self._areas.painted_strings():
            yield InterfaceText(text, _seen_by_reader(view))

        for widget in (self, *self.findChildren(QWidget)):
            yield from _widget_text(widget)
