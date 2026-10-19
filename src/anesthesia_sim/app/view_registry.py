"""The View registry: every View kind this build can draw, and every tag it has retired.

A saved layout names each Area's View by a kind tag (`layout.tree.ViewKind`).
The layout package treats that tag as opaque. It checks the tag's syntax and
keeps it unchanged, but holds no list of View kinds (`PL-R1WQ` Q1, project
owner, 2026-09-27, ratified). This module is the one list. The adapter,
`app/area_layout.py`, looks each Area's tag up here when it builds the widget
tree. A tag this build does not register gets the failure notice in that Area
and nothing else, and the model keeps the tag. So a layout saved under another
build loses nothing when it is saved again (`ROADMAP.md` § "v0.6.0 - the
layout is the reader's", Required scope entry 4).

**A tag is a string literal written once, below, beside its entry** (`PL-R1WQ`
Q3). It is never derived from a class name, a module path or a title. So
renaming a class, moving a module or rewording a title changes nothing a saved
file can see, and cannot set off the failure meant for a View that is really
missing.

**Renaming or removing a tag is a change to the saved file's meaning.** The old
tag goes into `RETIRED_TAGS`, with the version that retired it and, where the
View was renamed rather than removed, the tag it now has. A layout naming a
retired tag then gets a notice that says which of the two happened. A retired
tag is never registered again, for this View or any other. Blender keeps its
retired editor numbers reserved in `eSpace_Type` for the same reason: a saved
file's tag must never come to mean a different View (`PL-R1WQ` Q3).

**Some kinds must stay reachable in every layout** (`PL-50PZ`). `docs/MODEL.md`
§ "Minimum displayed outputs" lets a Workspace leave the agent accounting out,
but says it "must stay reachable in every layout, and must not be removable
from the application". `REQUIRED_REACHABLE` is that requirement as data. Each
kind it names must be registered, and its entry must carry
`required_reachable`; `required_kinds` checks both when this module is
imported, so a build that drops one fails at once. The View chooser in each
Area's header lists every registered kind whatever the Workspace names, so a
registered kind is reachable from every Workspace by construction.

**Each entry holds the factory that builds its View** (`PL-TH35`). The
adapter calls it with a `ViewContext` for every Area that shows the kind, so
any registered View can be built in any Area, any number of times. The shipped
entries name a View class from `app/views.py`, which is its own factory, so
this module imports the toolkit through it. The View's minimum size, which
the ratified entry also holds, is `PL-K285`'s.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.view_contract import ViewFactory
from anesthesia_sim.app.views import (
    AccountingView,
    ConcentrationView,
    ParameterControlsView,
    WashInView,
)
from anesthesia_sim.layout.tree import ViewKind

__all__ = [
    "AGENT_ACCOUNTING",
    "CHOOSE_A_VIEW",
    "CONCENTRATION_CHART",
    "MISSING_VIEW_TITLE",
    "PARAMETER_CONTROLS",
    "REGISTERED",
    "REQUIRED_REACHABLE",
    "RETIRED_TAGS",
    "WASH_IN",
    "RegisteredView",
    "RetiredTag",
    "missing_view_text",
    "registry",
    "rename_offer_text",
    "required_kinds",
    "retirements",
]

# The tags. Each is written here once and never changed; see the module
# docstring for what renaming one takes.
CONCENTRATION_CHART: Final = ViewKind("concentration_chart")
WASH_IN: Final = ViewKind("wash_in")
PARAMETER_CONTROLS: Final = ViewKind("parameter_controls")
AGENT_ACCOUNTING: Final = ViewKind("agent_accounting")

#: The first line of the notice an Area shows in place of a View this build
#: does not have (`PL-DB5G` Q2, project owner, 2026-10-11, ratified).
MISSING_VIEW_TITLE: Final = "This Area's View is not in this build."

#: What every Area notice tells the reader to do: the View chooser is the
#: first control of the Area's header, above the notice (`PL-DB5G` Q2).
CHOOSE_A_VIEW: Final = "Choose a View from the menu above."

# A release number as `pyproject.toml` writes it.
_VERSION: Final = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


@dataclass(frozen=True)
class RegisteredView:
    """One View kind this build can draw.

    Attributes:
        kind: The tag a saved layout names the View by.
        title: The View's name as a reader sees it.
        factory: Builds the View from its context, for each Area that shows
            the kind (`PL-TH35`).
        required_reachable: Whether `docs/MODEL.md` requires the View to stay
            reachable in every layout. `required_kinds` holds this to
            `REQUIRED_REACHABLE`.

    Raises:
        TypeError: `kind` is not a `ViewKind`, `title` is not a `str`,
            `factory` cannot be called, or `required_reachable` is not a
            `bool`.
        ValueError: `title` is empty or only spaces.
    """

    kind: ViewKind
    title: str
    factory: ViewFactory
    required_reachable: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ViewKind):
            raise TypeError(f"a View's kind is a ViewKind, not {type(self.kind).__name__}")

        if not isinstance(self.title, str):
            raise TypeError(f"a View's title is a str, not {type(self.title).__name__}")

        if not self.title.strip():
            raise ValueError(f"the View of kind {self.kind!r} has no title")

        if not callable(self.factory):
            raise TypeError(
                f"the View of kind {self.kind!r} has a factory that cannot be called: "
                f"{type(self.factory).__name__}"
            )

        if not isinstance(self.required_reachable, bool):
            raise TypeError(
                "whether a View must stay reachable is a bool, not "
                f"{type(self.required_reachable).__name__}"
            )


@dataclass(frozen=True)
class RetiredTag:
    """A tag no View has any more, and what became of the View that had it.

    Attributes:
        kind: The retired tag.
        version: The release that retired it, such as "0.7.0".
        successor: The tag the View has now, where it was renamed, or None
            where it was removed.

    Raises:
        TypeError: `kind` or `successor` is not a `ViewKind`, or `version` is
            not a `str`.
        ValueError: `version` is not a release number of three dot-separated
            whole numbers, or `successor` is `kind` itself.
    """

    kind: ViewKind
    version: str
    successor: ViewKind | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ViewKind):
            raise TypeError(f"a retired tag is a ViewKind, not {type(self.kind).__name__}")

        if not isinstance(self.version, str):
            raise TypeError(f"a release number is a str, not {type(self.version).__name__}")

        if _VERSION.fullmatch(self.version) is None:
            raise ValueError(
                f"the tag {self.kind!r} was retired in a release written as three "
                f"dot-separated whole numbers, not {self.version!r}"
            )

        if self.successor is not None and not isinstance(self.successor, ViewKind):
            raise TypeError(
                f"a successor tag is a ViewKind or None, not {type(self.successor).__name__}"
            )

        if self.successor == self.kind:
            raise ValueError(f"the tag {self.kind!r} cannot be renamed to itself")


def registry(*views: RegisteredView) -> Mapping[str, RegisteredView]:
    """A read-only registry of `views`, keyed by each one's tag.

    Raises:
        TypeError: an entry is not a `RegisteredView`.
        ValueError: two entries share a tag.
    """

    entries: dict[str, RegisteredView] = {}

    for view in views:
        if not isinstance(view, RegisteredView):
            raise TypeError(f"a registry holds RegisteredView entries, not {type(view).__name__}")

        if view.kind in entries:
            raise ValueError(f"two Views are registered under the tag {view.kind!r}")

        entries[view.kind] = view

    return MappingProxyType(entries)


def retirements(
    registered: Mapping[str, RegisteredView], *retired: RetiredTag
) -> Mapping[str, RetiredTag]:
    """A read-only table of `retired`, keyed by tag, checked against `registered`.

    Raises:
        TypeError: an entry is not a `RetiredTag`.
        ValueError: a tag is retired twice; a retired tag is registered,
            which would let a saved file's tag mean a different View; or a
            successor is not registered, which would send a reader to a View
            this build does not have.
    """

    entries: dict[str, RetiredTag] = {}

    for tag in retired:
        if not isinstance(tag, RetiredTag):
            raise TypeError(
                f"a retirement table holds RetiredTag entries, not {type(tag).__name__}"
            )

        if tag.kind in entries:
            raise ValueError(f"the tag {tag.kind!r} is retired twice")

        if tag.kind in registered:
            raise ValueError(
                f"the tag {tag.kind!r} is both retired and registered; a retired tag is never "
                "given to a View again"
            )

        if tag.successor is not None and tag.successor not in registered:
            raise ValueError(
                f"the tag {tag.kind!r} was renamed to {tag.successor!r}, which no View is "
                "registered under"
            )

        entries[tag.kind] = tag

    return MappingProxyType(entries)


def required_kinds(
    registered: Mapping[str, RegisteredView], *required: ViewKind
) -> tuple[ViewKind, ...]:
    """The kinds in `required`, once `registered` registers each as required to stay reachable.

    `docs/MODEL.md` requires some Views to stay reachable in every layout and
    not to be removable from the application. The chooser lists every
    registered kind, so what can make one unreachable is a build that no
    longer registers it. This check is run on the shipped registry when this
    module is imported, so such a build fails before it draws anything.

    Raises:
        TypeError: a kind is not a `ViewKind`.
        ValueError: a kind is named twice; a required kind is not registered,
            or its entry does not carry `required_reachable`; or an entry
            carries `required_reachable` and is not in `required`, so the
            flag and the requirement would disagree.
    """

    for kind in required:
        if not isinstance(kind, ViewKind):
            raise TypeError(f"a required View kind is a ViewKind, not {type(kind).__name__}")

    if len(set(required)) != len(required):
        raise ValueError("a View kind is required to stay reachable twice")

    for kind in required:
        if kind not in registered:
            raise ValueError(
                f"the View kind {kind!r} must stay reachable in every layout, and this build "
                "does not register it (docs/MODEL.md, Minimum displayed outputs)"
            )

        if not registered[kind].required_reachable:
            raise ValueError(
                f"the View kind {kind!r} must stay reachable in every layout, and its entry "
                "does not carry required_reachable"
            )

    flagged = [kind for kind, view in registered.items() if view.required_reachable]
    extra = [kind for kind in flagged if kind not in required]

    if extra:
        raise ValueError(
            f"the View kinds {extra!r} carry required_reachable, and no requirement names them"
        )

    return tuple(required)


#: Every View kind this build can draw, in the order the View chooser lists
#: them. The titles are placeholders.
REGISTERED: Final = registry(
    RegisteredView(CONCENTRATION_CHART, "Concentrations", ConcentrationView),
    RegisteredView(WASH_IN, "Wash-in", WashInView),
    RegisteredView(PARAMETER_CONTROLS, "Parameters", ParameterControlsView),
    RegisteredView(AGENT_ACCOUNTING, "Agent accounting", AccountingView, required_reachable=True),
)

#: The View kinds `docs/MODEL.md` § "Minimum displayed outputs" requires to
#: stay reachable in every layout: the agent accounting. Checked against
#: `REGISTERED` here, so a build that drops it fails on import.
REQUIRED_REACHABLE: Final = required_kinds(REGISTERED, AGENT_ACCOUNTING)

#: Every tag a View has had and no longer has. None has been retired yet.
RETIRED_TAGS: Final = retirements(REGISTERED)


def missing_view_text(
    kind: ViewKind,
    registered: Mapping[str, RegisteredView] = REGISTERED,
    retired: Mapping[str, RetiredTag] = RETIRED_TAGS,
) -> str:
    """The body of the notice an Area shows when its View kind is not in `registered`.

    The body names the saved tag, says what became of it, tells the reader
    to choose a View from the chooser above, and says that the tag is kept
    until they do. The wording is `PL-DB5G` Q2's.

    Raises:
        TypeError: `kind` is not a `ViewKind`.
        ValueError: `kind` is registered, so no notice is due.
    """

    if not isinstance(kind, ViewKind):
        raise TypeError(f"a View kind is a ViewKind, not {type(kind).__name__}")

    if kind in registered:
        raise ValueError(f"the View kind {kind!r} is registered, so its Area draws it")

    saved = f"It was saved as the View kind '{kind}'."
    tag = retired.get(kind)

    if tag is None:
        fate = "This build does not know it."
    elif tag.successor is None:
        fate = f"That View was removed in version {tag.version}."
    else:
        fate = (
            f"That View was renamed in version {tag.version}, and is now "
            f"'{registered[tag.successor].title}'."
        )

    return f"{saved} {fate} {CHOOSE_A_VIEW} The saved name is kept until you do."


def rename_offer_text(
    kind: ViewKind,
    registered: Mapping[str, RegisteredView] = REGISTERED,
    retired: Mapping[str, RetiredTag] = RETIRED_TAGS,
) -> str | None:
    """The label of the button that shows a renamed View under its new tag, or None.

    A saved tag whose View was renamed is offered the new tag explicitly and
    never mapped to it silently (`PL-R1WQ` Q3). A tag that was removed, or
    that this build does not know, has no offer. The wording is a placeholder.

    Raises:
        TypeError: `kind` is not a `ViewKind`.
        ValueError: `kind` is registered, so no notice is due.
    """

    if not isinstance(kind, ViewKind):
        raise TypeError(f"a View kind is a ViewKind, not {type(kind).__name__}")

    if kind in registered:
        raise ValueError(f"the View kind {kind!r} is registered, so its Area draws it")

    tag = retired.get(kind)

    if tag is None or tag.successor is None:
        return None

    return f"Show '{registered[tag.successor].title}'"
