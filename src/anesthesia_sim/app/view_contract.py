"""Define the View contract, which says what every View implements and what it is given.

An Area holds one View, and any View can occupy any Area (`ROADMAP.md`
§ "Completed: v0.6.0 - the layout is the reader's", Required scope entry 5).
That works only if every View presents the same small contract. The adapter,
`app/area_layout.py`, can then build, draw and save any View without knowing
which kind it holds. This module is that contract. It was designed in an item
(`PL-TH35`) as answers to numbered questions, and the project owner ratified
each answer on 2026-09-27. The question numbers below, such as Q2, refer to
those questions.

**What a View is.** A View is a `QWidget` that satisfies the `View` protocol
below. Its registry entry's factory builds it from a `ViewContext`
(`app/view_registry.py`). The adapter is the only caller of the protocol's
members, and `tests/integration/test_view_contract.py` enforces that rule.
Every member must have a call site in the adapter, and every registered kind
must build a View that satisfies the protocol. A member that nothing calls is
deleted rather than kept for later. For comparison, Blender's editor table
carries two hooks that no editor implements and a field that no editor
assigns, and nothing in its design reports either problem
(`docs/interface-provenance.md`, the entry "Prune the contract of a View
instead of letting it grow").

**What a View is given, and what it is not** (Q2, Q7). A View is handed a
`ViewContext` when it is built and a `ViewTick` on every frame. It receives no
parent, no splitter, no controller and no reference to the Area it sits in.
So it cannot reach another Area or the dashboard, and the same class can be
built any number of times against the same runs (Q8). A View may hold state
of its own, such as how it draws. State that the rest of the dashboard draws
from, such as the compartment selection, is shown to the View in each tick.
The View asks for a change to it through `ViewContext.requests`, and never
holds the value itself. A request to change a run's setting names the run by
its `run_id` (`ViewRequests`).

**A tick names every displayed run, with a frame or without one** (`PL-RF2S`).
`ViewTick.runs` holds one `RunPresentation` for each displayed run
(`app/run_presentation.py`). It is everything that the run's panel shows at
that moment. A View that shows a run's values builds its own widget for each
run and writes the whole widget from that run's presentation on every tick. It
finds a run's widget by `RunPresentation.run_id`, and it deletes the widget of
a run that the tick no longer names.

A run's name travels in its presentation with its values (`RunPresentation.name`).
A View writes the name and the values of one run from one presentation, in
one call, so it has no way to pair one run's name with another run's number.
The tick carries no run's snapshot. A value that every displayed run shares
is read from the frame, which refuses runs that disagree on it
(`chart_frame.assemble_chart_frame`).

The dashboard also hands every View a tick when no frame can be drawn: on a
halt, and at once after a dial is dragged. Its presentations hold the values
of the last frame that drew, or withhold them when the run has started over
since that frame. Each chart is given the last frame drawn for its window,
kept while every run is still the one it drew, and withheld otherwise
(`run_presentation.ShownFrame`). A chart draws a withheld frame as an empty
plot with the reason.

Every View is handed a tick with no frame, even when a View before it in
reading order raises on that tick. The first exception is raised once the last
View has been handed the tick. A tick with a frame stops at the first View that
raises, and the halt that follows hands every View a tick with no frame.

**A chart's time window is its own** (project owner, 2026-10-19, ratified,
over one shared window saved per Workspace; `PL-L59K`). Q2 and Q7 made the
time base shared state, which every chart showed. `ROADMAP.md` § "Completed:
v0.6.0 - the layout is the reader's", Required scope entry 11, puts the window in each
View's own state instead, so that one chart can be zoomed to the first minutes
while another shows the whole run. So a chart View holds its window, sets it
from its own control and saves it. It asks for a frame at once through
`ViewRequests.frame` when the reader changes it. An opt-in sync of windows
between charts is left to a later item, `PL-1RFZ`.

**The reader's preferences are shared state too** (`PL-B396`). The agent cost
View shows the delivered agent in the unit that the reader's preferences hold.
A preference belongs to the reader, not to a View or a layout (`PL-MQHN`), so
two agent cost Views always show the same unit. The dashboard holds the
preferences and saves them (`app/preferences.py`). Each tick shows them to
every View in `ViewTick.preferences`, and a View asks for a change through
`ViewRequests.agent_cost_unit` or `ViewRequests.agent_price` (`PL-1P15`).

The top of the MAC axis is one of the preferences too (`PL-7LZ7`). Every
concentration chart and every compartment schematic draws a tension against
it, so two Views cannot disagree about whether a tension is off the scale.
The dashboard assembles each frame and builds each run's schematic at that
top, and a View asks for another through `ViewRequests.chart_ceiling`.

**A tick carries the case's panels as values** (`PL-9YPR`, `PL-RF2S`). The
bookmarks and the branch control belong to the case, and no run owns them.
`ViewTick.case` holds what they show: the marks with each run's standing, the
editor's entry and refusal, and the branch offer with its selected point
(`CasePresentation`). A View that shows one builds its own widgets and writes
them whole from the tick, on a tick with a frame and on one without. It asks
for an edit of the marks, a selected point or a branch through `ViewRequests`.
So two Areas can show the bookmarks at once, and neither View holds the case.

**A View says whether it shows the runs or the case** (`PL-1D3Z`).
`View.scope` is `ViewScope.RUNS` for a View that draws the displayed runs and
`ViewScope.CASE` for one that draws only the case. A Workspace pinned to a run
draws that run alone in each View of the runs, and names it in their Area
headers. A View of the case shows the whole case whatever the pin, and its
Area header names no run. While the pinned run is not open, the Areas of the
runs say so in place of their Views, and the Views of the case are still
handed a tick, which names no run.

**What a View is drawn from** (Q3). Each View states which frame it draws,
through `View.frame_request`. The request gives the window and the plot width
that the frame must be sampled for. The dashboard assembles one `ChartFrame`
per distinct window on each tick, sampled for the widest plot that asks for
that window. A chord is the straight line between two samples. Sampling for
the widest plot means that no plot draws a chord wider than a pixel
(`PL-GS3R`). Two charts at the same window also draw the same instants
(`PL-9LNF`). The adapter hands each View the frame for its own window in its
`ViewTick`. A View that draws no frame returns None from `frame_request`, and
its tick carries no frame.

**What a View saves** (Q4). `View.save_state` returns the View's own drawing
settings as a JSON-shaped mapping that carries `STATE_VERSION_KEY`. The View
owns that version. The layout layer stores the mapping under the Area's id and
the View's kind (`layout/workspace.py`'s `view_state`) and never reads inside
it. A View handed saved state it cannot read starts from its defaults and says
so in its rectangle, through `unreadable_state_text`. A View silently drawn
with defaults would be the stale-state failure that `CLAUDE.md`'s display
standard names.

**What a split, a swap and a change of View do to the state** (Q10). When the
reader replaces a View through the chooser, the View's state is saved under
its Area and kind. When that kind returns to that Area, its View is built from
the saved state again. A split gives the new Area a copy of the source View's
state, and a swap moves each instance with its state. Splitting and swapping
(`PL-2KXB`) build on `save_state` as it stands here.

**What a View must do when there is nothing to draw** (Q6). It must show text
in its rectangle that states what is absent, and never leave it blank. The
charts' advisories, such as `dashboard_frame.NO_TRACES_SHOWN_TEXT`, are the
pattern.

**A View is told the name of the Area that holds it** (`PL-XV64`). A
screen-reader user hears only a control's name, so two copies of one View
would otherwise offer two controls with the same name. The container works
out each Area's name, an `AreaName`, after every change of the layout, and
hands it to the View through `View.name_controls`. A View names each control
beside its plot with that name, such as "Time base, Concentrations 2", and
each plot picture while another Area shows the same kind of View. A form
whose copies each keep what was typed in them is named in the same way, such
as the agent cost View's price form. Every other control keeps its name,
because each of its copies acts on the same shared state, and the W3C's ARIA
Authoring Practices Guide lets controls that are "actually identical" share a
name.

**What is not the View's.** The container draws the Area's header, with the
View's title and the chooser (Q11, `app/area_layout.py`). No View is barred
from an Area that a reader can close, because the values that must always be
on screen are in the unconditional region and never in a View (Q9,
`PL-NWTM`).

**A View is never drawn below the size it needs** (`PL-K285`, project owner,
2026-09-27, ratified). The size is a constraint, not a request. It is the
larger of the minimum its registry entry declares and the View widget's own
minimum size hint (`app/view_registry.py`). The container holds the Area at
that size wherever the layout can give it. Where the layout cannot, the
container hides the View and shows a notice stating the size the View needs
and the size the Area has (`layout/sizing.py`). So a View never has to draw
itself in less than it asked for, and is never clipped. A Workspace that
pins a run draws that run alone, in every one of its Views of the runs
(`PL-7Z84`). Every other Workspace's Views draw every displayed run.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final, Protocol, runtime_checkable

from anesthesia_sim.app.chart_time_base import ChartWindow
from anesthesia_sim.app.compartment_selection import CompartmentSelection
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.dashboard_frame import BookmarkPanel, ForkOffer, ForkPoint
from anesthesia_sim.app.formatting import AgentAmountUnit, ChartCeiling
from anesthesia_sim.app.preferences import AgentPrice, Preferences
from anesthesia_sim.app.qt_widgets import DialInput, MarkButton, MarkEntry, MarkRefusal, MarkUndo
from anesthesia_sim.app.run_presentation import RunPresentation, ShownFrame
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.layout.run_identity import RunId

__all__ = [
    "STATE_VERSION_KEY",
    "UNREADABLE_STATE_TEXT",
    "AreaName",
    "BranchPresentation",
    "CasePresentation",
    "FrameRequest",
    "MarksPresentation",
    "PreferencesInForce",
    "SavedState",
    "View",
    "ViewContext",
    "ViewFactory",
    "ViewRequests",
    "ViewScope",
    "ViewTick",
    "unreadable_state_text",
]

type SavedState = Mapping[str, object]
"""A View's saved settings: a JSON-shaped mapping that carries `STATE_VERSION_KEY`."""

#: The key under which every View's saved state records the version of its
#: own format.
STATE_VERSION_KEY: Final = "state_version"

#: What a View shows when the saved state it was built from could not be read.
#: A placeholder.
UNREADABLE_STATE_TEXT: Final = (
    "This View's saved settings could not be read, so it shows its default settings."
)


class ViewScope(Enum):
    """What a View shows: the displayed runs, or the case that no run owns (`PL-1D3Z`)."""

    RUNS = "runs"
    CASE = "case"


@dataclass(frozen=True, slots=True)
class AreaName:
    """What a screen reader calls an Area: its View's title, and its number where the title repeats.

    Where two or more Areas in the window show the same kind of View, each is
    numbered among them, as VS Code numbers its editor groups:
    "Concentrations 1" and "Concentrations 2" (`PL-XV64`). The left or upper
    part of each split, with every Area inside it, is counted before the next
    part. An Area that is the only one of its kind has no number, and its name
    is the title alone.

    Attributes:
        title: The View's title, as the Area's View chooser shows it.
        number: The Area's place among the Areas that show the same kind of
            View, counted from 1, or None where no other Area shows that kind.

    Raises:
        ValueError: `title` is empty, or `number` is less than 1.
        TypeError: `number` is not an `int`, or is a `bool`.
    """

    title: str
    number: int | None = None

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("an Area's name needs its View's title, and the title given is empty")

        if self.number is None:
            return

        if isinstance(self.number, bool) or not isinstance(self.number, int):
            raise TypeError(f"an Area's number is an int, not {type(self.number).__name__}")

        if self.number < 1:
            raise ValueError(f"an Area's number counts from 1, and {self.number} was given")

    @property
    def text(self) -> str:
        """The name a screen reader says, such as "Concentrations 2" or "Wash-in"."""

        return self.title if self.number is None else f"{self.title} {self.number}"

    @property
    def among_copies(self) -> str | None:
        """The name where another Area shows the same kind of View, or None where none does.

        A control whose label no other kind of View shows adds this to its
        name, so that it is told apart from the same control in a copy of its
        View, and keeps its own name while its View is drawn once.
        """

        return None if self.number is None else self.text


@dataclass(frozen=True, slots=True)
class MarksPresentation:
    """What every copy of the bookmarks panel shows on one tick.

    Attributes:
        panel: Both lists of marks, with each run's standing on each mark.
            None before the first frame has listed them, and while a halt
            could not work out the standings. The lists are then hidden,
            because a row from an earlier frame would say that a mark is
            still to come on a run that has failed (`PL-YHR3`).
        reachable_height_mac: The highest mark the height control accepts,
            as a multiple of the agent's 1 MAC, or None before the first
            frame.
        entry: What the reader entered in the editor's forms, and the rows
            selected in its lists, or None before the reader entered
            anything. Every copy shows this one entry (`PL-CHX0`).
        refusal: Why the reader's last edit was refused, or None.
        undo: The removal that an Undo would reverse, or None where there is
            none to offer (`PL-5GX4`).
    """

    panel: BookmarkPanel | None
    reachable_height_mac: float | None
    entry: MarkEntry | None
    refusal: MarkRefusal | None
    undo: MarkUndo | None


@dataclass(frozen=True, slots=True)
class BranchPresentation:
    """What every copy of the branch control shows on one tick.

    Attributes:
        offer: The points at which a branch may be opened, and why none may
            be, or None before the first frame.
        selected: The point shown as selected in every copy, or None for no
            point (`dashboard_frame.kept_fork_selection`).
    """

    offer: ForkOffer | None
    selected: ForkPoint | None


@dataclass(frozen=True, slots=True)
class CasePresentation:
    """What the case's panels show on one tick. No run owns either panel.

    Attributes:
        marks: The bookmarks panel.
        branch: The branch control, or None where the dashboard was handed
            loose runs. It then has no case to branch, so a control could
            only refuse.
    """

    marks: MarksPresentation
    branch: BranchPresentation | None


@dataclass(frozen=True, slots=True)
class ViewRequests:
    """How a View asks the dashboard for a change or for a frame.

    A control over shared state shows the value that each tick carries, and
    calls one of these to change it. It never stores the value (Q7, `PL-VN6M`).

    Attributes:
        frame: Asks for a frame at once, after the View changed a drawing
            setting of its own, such as its time window.
        compartment: Asks for one compartment's trace to be shown or hidden.
        agent_cost_unit: Asks for the agent cost View's unit to become the
            given one, in the reader's preferences.
        chart_ceiling: Asks for the top of the MAC axis, which every
            concentration chart and schematic draws against, to become the
            given one, in the reader's preferences.
        agent_price: Asks for the reader's price for the given agent to become
            the given one, or to be removed when it is None.
        refused_entries_discard: Asks for every entry of the preferences file
            that was refused when the file was read to be discarded.
        adjustment_start: Says that the reader began an input on a dial of
            the given run, so the changes that follow are one new adjustment.
        setting: Asks for the given run's setting on the given control to
            become the given value, and says which kind of input applied it
            (`DialInput`). The run applies it or refuses it, and the next
            tick shows the setting in force.
        preview: Says where a held dial of the given run stands, so the
            charts can preview that value (`PL-5B1N`).
        preview_end: Says that the held dial of the given run was released.
        mark_entry: Says that the reader changed the entry in a copy of the
            marks editor, so that every other copy shows it too.
        mark_edit: Asks for the mark that the given Add button adds, with
            the entry of the copy whose button the reader pressed. The case
            adds it to every run or refuses it, and the next tick shows the
            marks and any refusal.
        mark_remove: Asks for the mark in the given row to be removed, from
            the list that the given Remove button belongs to. The case
            removes it from every run or refuses it, and the next tick shows
            the marks and any refusal.
        mark_undo: Asks for the last removal to be undone. The case puts the
            mark back in every run, and the next tick shows it.
        branch_point: Says that the reader selected the given point in a
            copy of the branch control, or no point.
        branch: Asks for a branch at the selected point.
        branch_here: Asks for a branch where the trunk is paused.
    """

    frame: Callable[[], None]
    compartment: Callable[[RecordedQuantity, bool], None]
    agent_cost_unit: Callable[[AgentAmountUnit], None]
    chart_ceiling: Callable[[ChartCeiling], None]
    agent_price: Callable[[str, AgentPrice | None], None]
    refused_entries_discard: Callable[[], None]
    adjustment_start: Callable[[RunId], None]
    setting: Callable[[RunId, ControlInput, float, DialInput], None]
    preview: Callable[[RunId, ControlInput, float], None]
    preview_end: Callable[[RunId], None]
    mark_entry: Callable[[MarkEntry], None]
    mark_edit: Callable[[MarkButton, MarkEntry], None]
    mark_remove: Callable[[MarkButton, int], None]
    mark_undo: Callable[[], None]
    branch_point: Callable[[ForkPoint | None], None]
    branch: Callable[[], None]
    branch_here: Callable[[], None]


@dataclass(frozen=True, slots=True)
class FrameRequest:
    """Which frame a View draws: its time window, and the plot width to sample it for.

    Attributes:
        window: The window's width, and where the reader holds it, if they do.
        width_px: The plot's width in logical pixels.
    """

    window: ChartWindow
    width_px: float


@dataclass(frozen=True, slots=True)
class ViewContext:
    """Everything a View is built from. A View is given nothing else (Q2).

    Attributes:
        requests: How the View asks for a change to shared state.
        saved_state: The state the layout layer kept for this Area and kind,
            or None when the View is built there for the first time.
    """

    requests: ViewRequests
    saved_state: SavedState | None = None


@dataclass(frozen=True, slots=True)
class PreferencesInForce:
    """The reader's preferences in force this session, and what the reader is told about them.

    Attributes:
        preferences: The preferences every View is drawn with.
        notice: Why a preference was refused, could not be read or will not
            be saved, or None when there is nothing to tell the reader.
        chart_ceiling_unsaved: Whether the reader picked the axis top in force
            this session and the application could not save it. Every chart
            and schematic then says so under its axis top control
            (`preferences.chart_ceiling_notice`, `PL-GWSY`).
    """

    preferences: Preferences
    notice: str | None
    chart_ceiling_unsaved: bool


@dataclass(frozen=True, slots=True)
class ViewTick:
    """What one View is shown on one tick, whether or not a frame was drawn for it.

    Attributes:
        frame: The chart frame for the window this View asked for through
            `View.frame_request`, over every displayed run: drawn this tick,
            kept from the last tick that drew, or withheld. None for a View
            that asked for none.
        runs: What each run that the View shows displays on this tick, in
            drawing order. On a tick with a frame, each was built from the
            snapshot that the frame was assembled from. Empty on a tick
            handed only to the Views of the case while the Workspace is
            pinned to a run that is not open.
        selection: The compartment selection every frame was assembled from.
        preferences: The reader's preferences, and any notice about them.
        case: What the case's panels show, which no run owns.
    """

    frame: ShownFrame | None
    runs: tuple[RunPresentation, ...]
    selection: CompartmentSelection
    preferences: PreferencesInForce
    case: CasePresentation


@runtime_checkable
class View(Protocol):
    """The members every View implements. The adapter is their only caller.

    A View is also a `QWidget`. The adapter refuses a factory that returns
    anything else.
    """

    @property
    def scope(self) -> ViewScope:
        """Whether this View shows the displayed runs or the case (`PL-1D3Z`)."""
        ...

    def refresh(self, tick: ViewTick) -> None:
        """Draw `tick`.

        The adapter calls this method on every frame the dashboard draws. It
        also calls it with a tick that carries no frame, when the dashboard
        shows the runs without drawing one.

        Raises:
            Exception: Whatever drawing the tick raises. On a tick with a
                frame, the dashboard then halts every run, because a failure
                in the shared drawing path belongs to no single run.
        """
        ...

    @property
    def owes_a_frame(self) -> bool:
        """Whether this View needs a frame although nothing in the runs changed.

        It is True before the View's first tick, or for a chart before its
        first frame. It is also True for a chart that is now wider than the
        width its last frame was sampled for (`PL-9LNF`), and for a chart
        whose window has changed since it last drew (`PL-L59K`).
        """
        ...

    def frame_request(self) -> FrameRequest | None:
        """The frame this View draws on the next tick, or None where it draws none."""
        ...

    def save_state(self) -> SavedState:
        """The View's own settings, to be stored under its Area and kind (Q4)."""
        ...

    def painted_strings(self) -> tuple[str, ...]:
        """The text this View paints without a label or a button, such as a plot's axis titles.

        A whole-interface test reads every label and button from the widget
        tree, so this is the text such a walk cannot find.
        """
        ...

    def name_controls(self, area: AreaName) -> None:
        """Name with `area` each control that two copies of this View would otherwise share.

        `area` is the name of the Area that holds the View. The adapter calls
        this method each time it builds the Areas again, which is after every
        split, join, swap, close or change of View, because each can change an
        Area's number (`PL-XV64`). The View names its controls at once, rather
        than at its next frame. A View whose controls all act on shared state does
        nothing, because two copies of such a control are the same control.
        The method only writes names and must raise nothing: the adapter calls
        it outside the guard that keeps a View that fails to build inside its
        own Area.
        """
        ...


type ViewFactory = Callable[[ViewContext], View]
"""Builds a View of one kind from its context. A View class is its own factory."""


def unreadable_state_text(saved: object, version: int) -> str | None:
    """The notice a View shows when it cannot read `saved`, or None when it can.

    A View can read saved state that is None, or a mapping whose
    `STATE_VERSION_KEY` is `version`. Anything else, such as a mapping from an
    older or a newer build, or one with no version at all, is unreadable. The
    View then starts from its defaults and shows the notice (Q4).

    Raises:
        TypeError: `version` is not an `int`, or is a `bool`.
    """

    if isinstance(version, bool) or not isinstance(version, int):
        raise TypeError(f"a saved-state version is an int, not {type(version).__name__}")

    if saved is None:
        return None

    if not isinstance(saved, Mapping):
        return UNREADABLE_STATE_TEXT

    found = saved.get(STATE_VERSION_KEY)

    # `type` rather than `isinstance`, so neither True nor 1.0 passes for 1.
    if type(found) is not int or found != version:
        return UNREADABLE_STATE_TEXT

    return None
