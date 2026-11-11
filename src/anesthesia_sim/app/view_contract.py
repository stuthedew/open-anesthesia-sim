"""Define the View contract, which says what every View implements and what it is given.

An Area holds one View, and any View can occupy any Area (`ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", Required scope entry 5). That works
only if every View presents the same small contract. The adapter,
`app/area_layout.py`, can then build, draw and save any View without knowing
which kind it holds. This module is that contract. `PL-TH35` designed it, and
the project owner ratified each answer on 2026-09-27. The question numbers
below refer to that item's questions.

**What a View is.** A View is a `QWidget` that satisfies the `View` protocol
below. Its registry entry's factory builds it from a `ViewContext`
(`app/view_registry.py`). The adapter is the only caller of the protocol's
members, and `tests/integration/test_view_contract.py` enforces that rule.
Every member must have a call site in the adapter, and every registered kind
must build a View that satisfies the protocol. A member that nothing calls is
deleted rather than kept for later. For comparison, Blender's editor table
carries two hooks that no editor implements and a field that no editor
assigns, and nothing in its design reports either problem
(`docs/interface-provenance.md` § "Prune the contract").

**What a View is given, and what it is not** (Q2, Q7). A View is handed a
`ViewContext` when it is built and a `ViewTick` on every frame. It receives no
parent, no splitter, no controller and no reference to the Area it sits in.
So it cannot reach another Area or the dashboard, and the same class can be
built any number of times against the same runs (Q8). A View may hold state
of its own, such as how it draws. State that the rest of the dashboard draws
from, such as the compartment selection, is shown to the View in each tick.
The View asks for a change to it through `ViewContext.requests`, and never
holds the value itself.

**A chart's time window is its own** (project owner, 2026-10-19, ratified,
over one shared window saved per Workspace; `PL-L59K`). Q2 and Q7 made the
time base shared state, which every chart showed. `ROADMAP.md` § "v0.6.0 -
the layout is the reader's", Required scope entry 11, puts the window in each
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

**The case's panels are shown as copies too** (`PL-9YPR`). The bookmarks and
the branch control belong to the case, and no run owns them. A View that shows
one asks `ViewTick.case` for a copy of its own on its first tick. The
dashboard then writes every live copy on each frame, as a run writes the
copies of its own surfaces. So two Areas can show the bookmarks at once, and
neither View holds the case.

**What a View is drawn from** (Q3). Each View states which frame it draws,
through `View.frame_request`. The request gives the window and the plot width
that the frame must be sampled for. The dashboard assembles one `ChartFrame`
per distinct window on each tick, sampled for the widest plot that asks for
that window. So no plot draws a chord, the straight line between two samples,
wider than a pixel (`PL-GS3R`). Two charts at the same window also draw the
same instants (`PL-9LNF`). The adapter hands each View the frame for its own
window in its `ViewTick`. A View that draws no frame returns None from
`frame_request`, and its tick carries no frame.

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
are left to `PL-2KXB`, and they build on `save_state` as it stands here.

**What a View owes when there is nothing to draw** (Q6). The View shows text
in its rectangle that states what is absent, and never leaves it blank. The
charts' advisories, such as `dashboard_frame.NO_TRACES_SHOWN_TEXT`, are the
pattern.

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
itself in less than it asked for, and is never clipped. Where a Workspace
pins a View to one run, that binding is left to `PL-7Z84`. Until then, every
View draws every displayed run.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, Protocol, runtime_checkable

from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import ChartTimeBase
from anesthesia_sim.app.compartment_selection import CompartmentSelection
from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import AgentPrice, Preferences
from anesthesia_sim.app.qt_agent_cost import RunAgentCost
from anesthesia_sim.app.qt_schematic import RunSchematic
from anesthesia_sim.app.qt_widgets import BookmarksPanel, ForkPanel
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls

__all__ = [
    "STATE_VERSION_KEY",
    "UNREADABLE_STATE_TEXT",
    "CaseSurfaces",
    "FrameRequest",
    "PreferencesInForce",
    "RunSurfaces",
    "SavedState",
    "View",
    "ViewContext",
    "ViewFactory",
    "ViewRequests",
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


class RunSurfaces(Protocol):
    """The parts of one displayed run that a View may show, each built as a new copy.

    `RunView` satisfies this protocol. Each method builds a new copy that
    shows what the run shows now. From then on, the run updates every live
    copy (`app/run_surfaces.py`, `PL-9LNF`). A View holds the copies and
    never the run's controller.
    """

    def build_parameter_controls(self) -> ParameterControls: ...

    def build_accounting_panel(self) -> AccountingPanel: ...

    def build_compartment_schematic(self) -> RunSchematic: ...

    def build_agent_cost(self) -> RunAgentCost: ...


class CaseSurfaces(Protocol):
    """The panels of the displayed case that a View may show, each built as a new copy.

    `SimulationView` satisfies this protocol. Each method builds a new copy
    that shows what the case shows now. From then on, the dashboard writes
    every live copy on each frame, and restates it on a halt (`PL-9YPR`). A
    View holds the copy and never the case.
    """

    def build_bookmarks_panel(self) -> BookmarksPanel:
        """Build a copy of the two lists of marks, with the button that opens their editor."""
        ...

    def build_branch_control(self) -> ForkPanel | None:
        """Build a copy of the branch control, or None where the dashboard holds no case.

        A dashboard that was handed loose runs has no case to branch, so a
        control there could only refuse.
        """
        ...


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
        agent_price: Asks for the reader's price for the given agent to become
            the given one, or to be removed when it is None.
    """

    frame: Callable[[], None]
    compartment: Callable[[RecordedQuantity, bool], None]
    agent_cost_unit: Callable[[AgentAmountUnit], None]
    agent_price: Callable[[str, AgentPrice | None], None]


@dataclass(frozen=True, slots=True)
class FrameRequest:
    """Which frame a View draws: its time window, and the plot width to sample it for.

    Attributes:
        time_base: The window's width, or None for "Fit run".
        width_px: The plot's width in logical pixels.
    """

    time_base: ChartTimeBase | None
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
    """

    preferences: Preferences
    notice: str | None


@dataclass(frozen=True, slots=True)
class ViewTick:
    """What one View is shown on one frame.

    Attributes:
        frame: The chart frame assembled for the window this View asked for
            through `View.frame_request`, over every displayed run. None for
            a View that asked for none.
        snapshots: Each displayed run's snapshot, in drawing order. Every
            frame of the tick was assembled from these same snapshots.
        runs: Each displayed run's surfaces, in the same order.
        selection: The compartment selection every frame was assembled from.
        preferences: The reader's preferences, and any notice about them.
        case: The displayed case's panels, which no run owns.
    """

    frame: ChartFrame | None
    snapshots: tuple[SimulationSnapshot, ...]
    runs: tuple[RunSurfaces, ...]
    selection: CompartmentSelection
    preferences: PreferencesInForce
    case: CaseSurfaces


@runtime_checkable
class View(Protocol):
    """The members every View implements. The adapter is their only caller.

    A View is also a `QWidget`. The adapter refuses a factory that returns
    anything else.
    """

    def refresh(self, tick: ViewTick) -> None:
        """Draw `tick`. The adapter calls this method on every frame the dashboard draws.

        Raises:
            Exception: Whatever drawing the frame raises. The dashboard then
                halts every run, because a failure in the shared drawing path
                belongs to no single run.
        """
        ...

    @property
    def owes_a_frame(self) -> bool:
        """Whether this View needs a frame although nothing in the runs changed.

        It is True before the View's first frame. It is also True for a chart
        that is now wider than the width its last frame was sampled for
        (`PL-9LNF`), and for a chart whose window has changed since it last
        drew (`PL-L59K`).
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
