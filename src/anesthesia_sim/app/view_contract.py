"""The View contract: what every View implements, and what it is given.

An Area holds one View, and any View can occupy any Area (`ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", Required scope entry 5). That holds
only if every View presents the same small contract, so the adapter,
`app/area_layout.py`, can build, draw and save any of them without knowing
which kind it holds. This module is that contract. `PL-TH35` designed it, and
the project owner ratified each answer on 2026-09-27. The question numbers
below are that item's.

**What a View is.** A View is a `QWidget` that satisfies the `View` protocol
below. Its registry entry's factory builds it from a `ViewContext`
(`app/view_registry.py`). The adapter is the only caller of the protocol's
members, and `tests/integration/test_view_contract.py` holds the contract to
that. Every member must have a call site in the adapter, and every registered
kind must build a View that satisfies the protocol. A member nothing calls is
deleted rather than kept for later. Blender's editor table carries two hooks
that no editor implements and a field that no editor assigns, and nothing in
its design reports either (`docs/interface-provenance.md` § "Prune the
contract").

**What a View is given, and what it is not** (Q2, Q7). A View is handed a
`ViewContext` when it is built and a `ViewTick` on every frame. It receives no
parent, no splitter, no controller and no reference to the Area it sits in.
So it cannot reach another Area or the dashboard, and the same class can be
built any number of times against the same runs (Q8). A View may hold state
of its own, such as how it draws. State that the rest of the dashboard draws
from, such as the time base or the compartment selection, is shown to the
View in each tick. The View asks for a change to it through
`ViewContext.requests`, and never holds the value itself.

**What a View is drawn from** (Q3). The dashboard assembles one `ChartFrame`
per tick and the adapter hands it to every View in the `ViewTick`. The frame
is sampled for the widest plot that any View asks for through
`View.frame_width_px`, so no plot draws a chord wider than a pixel
(`PL-GS3R`). One frame serves every plot, so the concentration chart and the
F_A/F_I plot draw the same instants (`PL-9LNF`). That replaces Q3's own
sketch, in which each chart pulled a frame at its own width: two charts of
different widths would then draw different instants, and the frame would be
assembled once per chart on every tick. A View that draws no frame returns
None from `frame_width_px`.

**What a View saves** (Q4). `View.save_state` returns the View's own drawing
settings as a JSON-shaped mapping that carries `STATE_VERSION_KEY`. The View
owns that version. The layout layer stores the mapping under the Area's id and
the View's kind (`layout/workspace.py`'s `view_state`) and never reads inside
it. A View handed saved state it cannot read starts from its defaults and says
so in its rectangle, through `unreadable_state_text`. A View silently drawn
with defaults would be the stale-state failure that `CLAUDE.md`'s display
standard names.

**What a split, a swap and a change of View do to the state** (Q10). A View
that the reader replaces through the chooser has its state saved under its
Area and kind. When that kind returns to that Area, it is built from the saved
state again. A split gives the new Area a copy of the source View's state, and
a swap moves each instance with its state. Those two operations are
`PL-2KXB`'s, and they build on `save_state` as it is here.

**What a View owes when there is nothing to draw** (Q6). Text that states
what is absent, in the View's rectangle, and never a blank. The charts'
advisories, such as `dashboard_frame.NO_TRACES_SHOWN_TEXT`, are the pattern.

**What is not the View's.** The Area's header, with the View's title and the
chooser, is drawn by the container (Q11, `app/area_layout.py`). No View is
barred from an Area a reader can close, because the values that must always
be on screen are in the unconditional region and never in a View (Q9,
`PL-NWTM`). A View's minimum size, and what an Area does when it cannot be
given it, are `PL-K285`'s. The run a View is bound to, where a Workspace pins
one, is `PL-7Z84`'s. Until then every View draws every displayed run.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final, Protocol, runtime_checkable

from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import ChartTimeBase
from anesthesia_sim.app.compartment_selection import CompartmentSelection
from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_surfaces import (
    AccountingPanel,
    OffScaleLine,
    ParameterControls,
    WashInStateLine,
)

__all__ = [
    "STATE_VERSION_KEY",
    "UNREADABLE_STATE_TEXT",
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

    `RunView` satisfies it. Each method builds another copy that shows what the
    run shows now, and the run writes every live copy from then on
    (`app/run_surfaces.py`, `PL-9LNF`). A View holds the copies and never the
    run's controller.
    """

    def build_parameter_controls(self) -> ParameterControls: ...

    def build_accounting_panel(self) -> AccountingPanel: ...

    def build_off_scale_notice(self) -> OffScaleLine: ...

    def build_wash_in_state(self) -> WashInStateLine: ...


@dataclass(frozen=True, slots=True)
class ViewRequests:
    """How a View asks the dashboard to change the state that every View draws from.

    A control over shared state shows the value in each tick and calls one of
    these. It never stores the value (Q7, `PL-VN6M`).

    Attributes:
        time_base: Asks for the chart window's width, or None for "Fit run".
        compartment: Asks for one compartment's trace to be shown or hidden.
    """

    time_base: Callable[[ChartTimeBase | None], None]
    compartment: Callable[[RecordedQuantity, bool], None]


@dataclass(frozen=True, slots=True)
class ViewContext:
    """What a View is built from, and the only thing (Q2).

    Attributes:
        requests: How the View asks for a change to shared state.
        saved_state: The state the layout layer kept for this Area and kind,
            or None when the View is built there for the first time.
    """

    requests: ViewRequests
    saved_state: SavedState | None = None


@dataclass(frozen=True, slots=True)
class ViewTick:
    """What every View is shown on one frame.

    Attributes:
        frame: The chart frame assembled for this tick, over every displayed
            run, sampled for the widest plot any View asked for.
        snapshots: Each displayed run's snapshot, in drawing order. The frame
            was assembled from these same reads.
        runs: Each displayed run's surfaces, in the same order.
        time_base: The time base the frame was drawn at, None for "Fit run".
        selection: The compartment selection the frame was assembled from.
    """

    frame: ChartFrame
    snapshots: tuple[SimulationSnapshot, ...]
    runs: tuple[RunSurfaces, ...]
    time_base: ChartTimeBase | None
    selection: CompartmentSelection


@runtime_checkable
class View(Protocol):
    """The members every View implements. The adapter is their only caller.

    A View is also a `QWidget`. The adapter refuses a factory that returns
    anything else.
    """

    def refresh(self, tick: ViewTick) -> None:
        """Draw `tick`. The adapter calls it on every frame the dashboard draws.

        Raises:
            Exception: whatever drawing the frame raises. The dashboard halts
                every run on it, because a failure in the shared drawing path
                belongs to no single run.
        """
        ...

    @property
    def owes_a_frame(self) -> bool:
        """Whether this View needs a frame although nothing in the runs changed.

        True before the View's first frame, and for a chart that has grown
        wider than the frame it drew was sampled for (`PL-9LNF`).
        """
        ...

    def frame_width_px(self) -> float | None:
        """The plot width this View needs its frame sampled for, or None where it draws none."""
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
