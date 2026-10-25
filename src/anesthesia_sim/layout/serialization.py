"""A layout as JSON, both as the body inside a Workspace and as a document on its own.

**The shape comes from `PL-HJPY` Q5**, which illustrated it and left the
schema to this build:

    {"schema_version": 2,
     "next_area_id": 3,
     "windows": [{"tree": {"split": "row", "sizes": [0.7, 0.3],
                           "children": [{"area": 1, "view": "concentration_chart"},
                                        {"area": 2, "view": "agent_accounting"}]}}]}

It departs from the illustration in one word: a split is `"row"` or `"column"`
rather than `"horizontal"`, for the reason that `layout/tree.py` gives. Each
window is an object that contains its tree, rather than the bare tree, so a
field that a window gains later is a new field rather than a change of shape.

**The body carries no version, but a document does.** `layout_to_dict` and
`layout_from_dict` write and read the layout alone, which is `next_area_id` and
`windows`. A Workspace stores that body under `"layout"`, beside its own
fields, in the one document that the application writes (`PL-SSQW` Q2):

    {"schema_version": 2,
     "active": 0,
     "workspaces": [{"name": "Default",
                     "origin": "shipped:default",
                     "layout": {"next_area_id": 3, "windows": [...]},
                     "view_state": {"1": {"concentration_chart": {...}}},
                     "pinned_run": null}]}

`workspace_set_to_json` and `workspace_set_from_json` write and read that
document, which contains a whole `WorkspaceSet`. The order of the Workspaces,
which one is active, and the rule that the set is never empty are properties of
the set, which a directory of files could not state. `workspace_to_dict` and
`workspace_from_dict` write and read one Workspace's body. `layout_to_json` and
`layout_from_json` write and read a document that contains one layout on its
own, with `schema_version` beside the body. A body never carries a version of
its own, so a document that contains several bodies has one version.

`view_state` is keyed first by Area id and then by View kind. The Area id is
written as a JSON object key, which is a string: the digits alone, as `str`
writes the number. Each entry is the JSON object that the View handed over,
stored and written as that JSON (`PL-WV9K` Q1). `pinned_run` is `null`, or
the pinned run's identity as `{"session": "<32 hex digits>", "number": 2}`
(`PL-7Z84`).

**Reading rejects an invalid document, and says what it rejected** (`PL-SSQW`
Q5, ratified). Every way in which a document can fail to describe a valid
layout raises `LayoutFormatError`. The error names the invariant and where it
broke, such as `windows[0].tree.children[1]`. Nothing is repaired, rescaled or
dropped. Reading is strict throughout, because nothing this code writes needs
leniency, and anything else deserves a person's review. Each of these is
rejected by name: a key the schema does not have, a key given twice, `NaN` or
`Infinity`, a fraction where a whole number belongs or the reverse, `true`
where a number belongs, and a tree nested deeper than `TREE_DEPTH_MAXIMUM`.
**A View kind under which no View is registered is not among them.** A tag
with the right syntax loads, and the View registry reports it in its own Area
(`LayoutModel.unknown_kinds`).

**The JSON parse itself rejects nothing.** A key given twice, `NaN` or
`Infinity`, and a whole number longer than Python is set to read are kept in
place. They are rejected only once the version has been read. A parse hook
that rejected one of them would not know where in the document the value was,
so its error could not name the place. It would also reject a newer document
as invalid before that document's version had been read.

**Versions.** `LAYOUT_SCHEMA_VERSION` is defined in `layout/migrations.py`,
together with the steps that read the versions before it. It is 2, the version
that added `pinned_run`. A document from a newer build raises
`UnsupportedSchemaVersion`, whatever else it contains. No rule of this build is
applied to anything in it except its `schema_version`, since its body is free
to follow rules that this build does not know. A document that claims a
version less than 1 is a format error. So is text from which no version can be
read: text that is not JSON, or JSON nested deeper than the parser's stack
allows. On Python 3.14 with an 8 MB stack, that limit was measured between
50,000 and 100,000 levels on 2026-10-12. A set document from an older build is
migrated, step by step, before it is read. A document that contains one layout
on its own is read at the current version only, because the only documents of
that shape ship with the build that wrote them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    UnsupportedSchemaVersion,
)
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION, SchemaVersion, migrate
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import (
    AREA_ID_MAXIMUM,
    TREE_DEPTH_MAXIMUM,
    Area,
    AreaId,
    Node,
    Orientation,
    Split,
    ViewKind,
    Window,
)
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

__all__ = [
    "LAYOUT_SCHEMA_VERSION",
    "ReadWorkspaceSet",
    "layout_from_dict",
    "layout_from_json",
    "layout_to_dict",
    "layout_to_json",
    "workspace_from_dict",
    "workspace_set_from_dict",
    "workspace_set_from_json",
    "workspace_set_to_dict",
    "workspace_set_to_json",
    "workspace_to_dict",
]

# How far each level of a written document is indented.
_INDENT: Final = 2


@dataclass(frozen=True, slots=True)
class _NonFinite:
    """`NaN`, `Infinity` or `-Infinity` as written, kept by the parse, rejected later in place."""

    written: str


@dataclass(frozen=True, slots=True)
class _LongInteger:
    """A whole number longer than Python is set to read, kept by the parse as its digit count."""

    digits: int


class _RepeatedKeys(dict[str, object]):
    """An object that gives a key more than once, which the parse keeps with its repeated keys."""

    __slots__ = ("repeated",)

    def __init__(self, read: dict[str, object], repeated: tuple[str, ...]) -> None:
        super().__init__(read)
        self.repeated = repeated


def layout_to_dict(model: LayoutModel) -> dict[str, object]:
    """Return the layout's body as plain values for `json.dumps` and `layout_from_dict`.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
    """

    if not isinstance(model, LayoutModel):
        raise TypeError(f"a layout is a LayoutModel, not {type(model).__name__}")

    return {
        "next_area_id": int(model.next_area_id),
        "windows": [{"tree": _node_to_dict(window.tree)} for window in model.windows],
    }


def layout_to_json(model: LayoutModel) -> str:
    """Return a document of the layout on its own, at `LAYOUT_SCHEMA_VERSION`, ending in a newline.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
    """

    document = {"schema_version": LAYOUT_SCHEMA_VERSION, **layout_to_dict(model)}

    return json.dumps(document, indent=_INDENT, allow_nan=False) + "\n"


def layout_from_dict(body: object) -> LayoutModel:
    """Read a layout's body, as `layout_to_dict` writes it.

    Raises:
        LayoutFormatError: the body does not describe a valid layout. A tree
            nested deeper than `TREE_DEPTH_MAXIMUM` is one of the ways it can
            fail. The message names the invariant and where in the body it
            broke.
    """

    try:
        return _read_layout(body)
    except RecursionError:
        # This is a backstop. The reader goes no deeper than the depth maximum,
        # at three frames per level. So this point is reached only when a caller
        # has left the reader less stack than that.
        raise LayoutFormatError(
            f"the layout: the stack ran out while it was being read, though no tree is read "
            f"deeper than {TREE_DEPTH_MAXIMUM} splits: its caller left too little of it"
        ) from None


def layout_from_json(text: str) -> LayoutModel:
    """Read a document that contains one layout, as `layout_to_json` writes it.

    The text is parsed once, by hooks that reject nothing, and its
    `schema_version` is read before any other rule of this build is applied to
    it. Only after that are the values that the parse kept rejected in place: a
    key given twice, `NaN` or `Infinity`, and a whole number too long to read.
    Then the body is read.

    Raises:
        TypeError: `text` is not a `str`.
        UnsupportedSchemaVersion: a newer build wrote the document. Nothing in
            it except its `schema_version` is checked against this build's
            rules, so it is reported as newer whatever its other fields contain.
        LayoutFormatError: no version can be read, because the text is not
            JSON or is JSON nested deeper than the parser's stack allows. Also
            raised when its `schema_version` is missing, given twice, or not a
            whole number from 1, or when it does not describe a valid layout.
            The message names the invariant and where it broke.
    """

    document, version = _parse(text, "a layout document")
    _check_version(version)

    if version != LAYOUT_SCHEMA_VERSION:
        raise LayoutFormatError(
            f"schema_version: a document holding one layout on its own is read at version "
            f"{LAYOUT_SCHEMA_VERSION} only, and this one was written at {version}; the file a "
            "reader saves is a Workspace set document, which is migrated"
        )

    _refuse_kept(document)

    return layout_from_dict(_body_of(document))


def workspace_to_dict(workspace: Workspace) -> dict[str, object]:
    """Return a Workspace's body as plain values for `json.dumps` and `workspace_from_dict`.

    Raises:
        TypeError: `workspace` is not a `Workspace`.
    """

    if not isinstance(workspace, Workspace):
        raise TypeError(f"a Workspace is a Workspace, not {type(workspace).__name__}")

    return {
        "name": str(workspace.name),
        "origin": workspace.origin.written(),
        "layout": layout_to_dict(workspace.layout),
        "view_state": {
            str(int(area_id)): {
                str(kind): json.loads(json.dumps(dict(state)))
                for kind, state in sorted(kinds.items())
            }
            for area_id, kinds in sorted(workspace.view_state.items())
        },
        "pinned_run": _run_id_to_dict(workspace.pinned_run),
    }


def workspace_from_dict(body: object, where: str = "the Workspace") -> Workspace:
    """Read a Workspace's body, as `workspace_to_dict` writes it, found at `where`.

    Raises:
        LayoutFormatError: the body does not describe a valid Workspace. It
            may have a name that a tab could not show, or an origin in neither
            written form, or a layout that cannot be read. Its `view_state`
            may be keyed by anything other than an Area in the layout and a
            View kind, or may contain anything other than an object for each
            kind. Its `pinned_run` may be neither `null` nor a run identity.
            The message names the invariant and where it broke.
    """

    fields = _fields(
        body, where, "a Workspace", ("name", "origin", "layout", "view_state", "pinned_run")
    )
    name = fields["name"]
    origin = fields["origin"]

    if not isinstance(name, str):
        raise LayoutFormatError(
            f"{where}.name: a Workspace's name is a string, not {_json_kind(name)}"
        )

    if not isinstance(origin, str):
        raise LayoutFormatError(
            f"{where}.origin: a Workspace's origin is a string, not {_json_kind(origin)}"
        )

    try:
        read_name = WorkspaceName(name)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}.name: {error}") from None

    try:
        read_origin = Origin.from_written(origin)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}.origin: {error}") from None

    layout = _read_layout(fields["layout"], f"{where}.layout", f"{where}.layout")
    view_state = _read_view_state(fields["view_state"], f"{where}.view_state")
    pinned_run = _read_run_id(fields["pinned_run"], f"{where}.pinned_run")

    try:
        return Workspace(read_name, read_origin, layout, view_state, pinned_run)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}: {error}") from None


def workspace_set_to_dict(workspaces: WorkspaceSet) -> dict[str, object]:
    """Return a set's body as plain values for `json.dumps` and `workspace_set_from_dict`.

    Raises:
        TypeError: `workspaces` is not a `WorkspaceSet`.
    """

    if not isinstance(workspaces, WorkspaceSet):
        raise TypeError(f"a Workspace set is a WorkspaceSet, not {type(workspaces).__name__}")

    return {
        "active": workspaces.active,
        "workspaces": [workspace_to_dict(workspace) for workspace in workspaces.workspaces],
    }


def workspace_set_from_dict(body: object) -> WorkspaceSet:
    """Read a set's body, as `workspace_set_to_dict` writes it.

    Raises:
        LayoutFormatError: the body does not describe a valid set. It may
            have no Workspaces, two Workspaces with one name, an active
            position outside the set, or a Workspace that cannot be read. The
            message names the invariant and where in the body it broke.
    """

    fields = _fields(body, "the Workspace set", "a Workspace set", ("active", "workspaces"))
    active = fields["active"]
    workspaces = fields["workspaces"]

    if isinstance(active, bool) or not isinstance(active, int):
        raise LayoutFormatError(
            f"active: the active Workspace's position is a whole number, not {_json_value(active)}"
        )

    if not isinstance(workspaces, list):
        raise LayoutFormatError(
            f"workspaces: a set's Workspaces are a list, not {_json_kind(workspaces)}"
        )

    read = tuple(
        workspace_from_dict(workspace, f"workspaces[{index}]")
        for index, workspace in enumerate(workspaces)
    )

    try:
        return WorkspaceSet(read, active)
    except InvalidLayout as error:
        raise LayoutFormatError(f"the Workspace set: {error}") from None


def workspace_set_to_json(workspaces: WorkspaceSet) -> str:
    """Return the document for `workspaces`, at `LAYOUT_SCHEMA_VERSION`, ending in a newline.

    Raises:
        TypeError: `workspaces` is not a `WorkspaceSet`.
    """

    document = {"schema_version": LAYOUT_SCHEMA_VERSION, **workspace_set_to_dict(workspaces)}

    return json.dumps(document, indent=_INDENT, allow_nan=False) + "\n"


@dataclass(frozen=True, slots=True)
class ReadWorkspaceSet:
    """A set document as read: the set, the version it was written at, and what was lost."""

    workspaces: WorkspaceSet
    written_at: SchemaVersion
    lossy: tuple[str, ...]


def workspace_set_from_json(text: str) -> ReadWorkspaceSet:
    """Read a set document, as `workspace_set_to_json` writes it, migrating an older one first.

    The text is parsed once, by hooks that reject nothing, and its
    `schema_version` is read before any other rule of this build is applied to
    it. A document written at an older version is migrated to this version by
    the steps in `layout/migrations.py`. `lossy` carries what each lossy step
    says it could not keep. `written_at` is the version found, so that the
    store knows to keep the pre-migration file.

    Raises:
        TypeError: `text` is not a `str`.
        UnsupportedSchemaVersion: a newer build wrote the document. Nothing in
            it except its `schema_version` is checked against this build's
            rules.
        LayoutFormatError: no version can be read, because the text is not
            JSON or is JSON nested deeper than the parser's stack allows. Also
            raised when its `schema_version` is missing, given twice, not a
            whole number from 1, or older than any step reads, or when it does
            not describe a valid set. The message names the invariant and
            where it broke.
    """

    document, version = _parse(text, "a Workspace set document")
    _check_version(version)
    _refuse_kept(document)

    migrated = migrate(_body_of(document), version)

    return ReadWorkspaceSet(workspace_set_from_dict(migrated.body), version, migrated.lossy)


def _parse(text: str, noun: str) -> tuple[dict[str, object], SchemaVersion]:
    """Parse `text` as a document, an object with a `schema_version`, and return it and the version.

    Raises:
        TypeError: `text` is not a `str`.
        LayoutFormatError: the text is not JSON, is nested deeper than the
            parser reads, is not an object, or has no version that can be
            read. `noun` names the kind of document that the message asked for.
    """

    if not isinstance(text, str):
        raise TypeError(f"{noun} is read from a str, not {type(text).__name__}")

    try:
        document = json.loads(
            text, object_pairs_hook=_object, parse_constant=_NonFinite, parse_int=_whole_number
        )
    except RecursionError:
        raise LayoutFormatError("the document is nested more deeply than can be read") from None
    except ValueError as error:
        raise LayoutFormatError(f"the document is not JSON this build can read: {error}") from None

    if not isinstance(document, dict):
        raise LayoutFormatError(f"the document: {noun} is an object, not {_json_kind(document)}")

    return document, _read_version(document)


def _check_version(version: SchemaVersion) -> None:
    """Refuse a version newer than this build reads.

    A version less than 1 is never built, because `_read_version` rejects it.

    Raises:
        UnsupportedSchemaVersion: `version` is greater than `LAYOUT_SCHEMA_VERSION`.
    """

    if version > LAYOUT_SCHEMA_VERSION:
        raise UnsupportedSchemaVersion(version, LAYOUT_SCHEMA_VERSION)


def _body_of(document: dict[str, object]) -> dict[str, object]:
    """Return the document without its `schema_version`: the body that its shape's reader reads."""

    return {key: value for key, value in document.items() if key != "schema_version"}


def _read_view_state(value: object, where: str) -> dict[AreaId, dict[ViewKind, dict[str, object]]]:
    """Read the `view_state` at `where`: Area id keys as JSON wrote them, View kind keys, objects.

    Whether each Area is in the layout is checked by the Workspace, and
    `workspace_from_dict` reports a failure at the Workspace.
    """

    if not isinstance(value, dict):
        raise LayoutFormatError(
            f"{where}: a Workspace's view_state is an object keyed by Area id, not "
            f"{_json_kind(value)}"
        )

    read: dict[AreaId, dict[ViewKind, dict[str, object]]] = {}

    for key, kinds in value.items():
        if not isinstance(key, str):
            raise LayoutFormatError(
                f"{where}: view_state is keyed by Area id written as a string, not "
                f"{_json_kind(key)}"
            )

        place = _member(where, key)

        if not _is_written_area_id(key):
            raise LayoutFormatError(
                f"{place}: view_state is keyed by Area id, a whole number written as a string "
                f"of digits with no sign and no leading zero, not {key!r}"
            )

        area_id = _read_area_id(int(key), place)

        if not isinstance(kinds, dict):
            raise LayoutFormatError(
                f"{place}: an Area's saved state is an object keyed by View kind, not "
                f"{_json_kind(kinds)}"
            )

        states: dict[ViewKind, dict[str, object]] = {}

        for tag, state in kinds.items():
            try:
                kind = ViewKind(tag)
            except InvalidLayout as error:
                raise LayoutFormatError(f"{_member(place, tag)}: {error}") from None

            if not isinstance(state, dict):
                raise LayoutFormatError(
                    f"{_member(place, tag)}: a View's saved state is an object, not "
                    f"{_json_kind(state)}"
                )

            states[kind] = dict(state)

        read[area_id] = states

    return read


def _node_to_dict(node: Node) -> dict[str, object]:
    if isinstance(node, Area):
        return {"area": int(node.id), "view": str(node.view)}

    return {
        "split": node.orientation.value,
        "sizes": list(node.sizes),
        "children": [_node_to_dict(child) for child in node.children],
    }


def _read_layout(body: object, where: str = "the layout", at: str = "") -> LayoutModel:
    """Read the layout at `where`, naming its members under `at` in an error message.

    `at` is empty for a document, so an error then names each member by its key alone.
    """

    fields = _fields(body, where, "a layout", ("next_area_id", "windows"))
    next_area_id = _read_area_id(fields["next_area_id"], _member(at, "next_area_id"))
    windows = fields["windows"]

    if not isinstance(windows, list):
        raise LayoutFormatError(
            f"{_member(at, 'windows')}: a layout's windows are a list, not {_json_kind(windows)}"
        )

    read = tuple(
        _read_window(window, f"{_member(at, 'windows')}[{index}]")
        for index, window in enumerate(windows)
    )

    try:
        return LayoutModel(read, next_area_id)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}: {error}") from None


def _read_window(value: object, where: str) -> Window:
    fields = _fields(value, where, "a window", ("tree",))

    return Window(_read_node(fields["tree"], f"{where}.tree", 0))


def _read_node(value: object, where: str, enclosing: int) -> Node:
    """Read the node at `where`, which sits inside `enclosing` splits.

    A split deeper than `TREE_DEPTH_MAXIMUM` is refused before its children
    are read. So the reader recurses no deeper than the maximum, however deep
    the document goes.
    """

    if not isinstance(value, dict):
        raise LayoutFormatError(
            f"{where}: a node is an object naming an Area or a split, not {_json_kind(value)}"
        )

    if "area" in value and "split" in value:
        raise LayoutFormatError(f"{where}: a node is an Area or a split, and this one names both")

    if "area" in value:
        fields = _fields(value, where, "an Area", ("area", "view"))
        view = fields["view"]

        if not isinstance(view, str):
            raise LayoutFormatError(
                f"{where}.view: a View kind is a string, not {_json_kind(view)}"
            )

        try:
            kind = ViewKind(view)
        except InvalidLayout as error:
            raise LayoutFormatError(f"{where}.view: {error}") from None

        return Area(_read_area_id(fields["area"], f"{where}.area"), kind)

    if "split" in value:
        if enclosing >= TREE_DEPTH_MAXIMUM:
            raise LayoutFormatError(
                f"{where}: the tree is nested more deeply than can be read: this split sits "
                f"{enclosing + 1} deep, and a split sits at most {TREE_DEPTH_MAXIMUM} deep in a "
                "window's tree"
            )

        fields = _fields(value, where, "a split", ("split", "sizes", "children"))

        return _read_split(fields, where, enclosing + 1)

    raise LayoutFormatError(
        f'{where}: a node names an Area with "area" or a split with "split", and this one '
        "names neither"
    )


def _read_split(fields: dict[str, object], where: str, depth: int) -> Split:
    """Read the split at `where`, which sits `depth` deep, so its children sit inside that many."""

    orientation = fields["split"]
    sizes = fields["sizes"]
    children = fields["children"]

    if orientation not in [member.value for member in Orientation]:
        raise LayoutFormatError(
            f'{where}.split: a split is "row" or "column", not {_json_value(orientation)}'
        )

    if not isinstance(sizes, list):
        raise LayoutFormatError(
            f"{where}.sizes: a split's sizes are a list, not {_json_kind(sizes)}"
        )

    for index, size in enumerate(sizes):
        if not isinstance(size, float):
            raise LayoutFormatError(
                f"{where}.sizes[{index}]: a size is a fraction written with a decimal point, "
                f"not {_json_value(size)}"
            )

    if not isinstance(children, list):
        raise LayoutFormatError(
            f"{where}.children: a split's children are a list, not {_json_kind(children)}"
        )

    read = tuple(
        _read_node(child, f"{where}.children[{index}]", depth)
        for index, child in enumerate(children)
    )

    try:
        return Split(Orientation(orientation), tuple(sizes), read)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}: {error}") from None


def _run_id_to_dict(run: RunId | None) -> dict[str, object] | None:
    """Return a pinned run as a file stores it: `null`, or its session and its number."""

    if run is None:
        return None

    return {"session": str(run.session), "number": run.number}


def _read_run_id(value: object, where: str) -> RunId | None:
    """Read a pinned run, as `_run_id_to_dict` writes it: `null`, or a session and a number."""

    if value is None:
        return None

    fields = _fields(value, where, "a pinned run", ("session", "number"))
    session = fields["session"]
    number = fields["number"]

    if not isinstance(session, str):
        raise LayoutFormatError(
            f"{where}.session: a run's session is a string, not {_json_kind(session)}"
        )

    if isinstance(number, bool) or not isinstance(number, int):
        raise LayoutFormatError(
            f"{where}.number: a run's number is a whole number, not {_json_value(number)}"
        )

    try:
        return RunId(SessionToken(session), number)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}: {error}") from None


def _read_area_id(value: object, where: str) -> AreaId:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LayoutFormatError(f"{where}: an Area id is a whole number, not {_json_value(value)}")

    try:
        return AreaId(value)
    except InvalidLayout as error:
        raise LayoutFormatError(f"{where}: {error}") from None


def _fields(value: object, where: str, noun: str, keys: tuple[str, ...]) -> dict[str, object]:
    """Return `value` as an object with exactly `keys`, none missing and none extra."""

    if not isinstance(value, dict):
        raise LayoutFormatError(f"{where}: {noun} is an object, not {_json_kind(value)}")

    missing = [key for key in keys if key not in value]
    unknown = sorted(str(key) for key in value if key not in keys)

    if missing:
        raise LayoutFormatError(f"{where}: is missing {', '.join(map(repr, missing))}")

    if unknown:
        raise LayoutFormatError(
            f"{where}: has {', '.join(map(repr, unknown))}, which the schema does not; it "
            f"holds {', '.join(map(repr, keys))}"
        )

    return dict(value)


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Return an object's pairs as a dict, noting a repeated key rather than silently keeping one.

    Which of two values was meant cannot be known, so the key is refused. The
    refusal happens later, where the object's place in the document is known,
    and not here, where it is not.
    """

    read = dict(pairs)

    if len(read) == len(pairs):
        return read

    seen: set[str] = set()
    repeated: list[str] = []

    for key, _ in pairs:
        if key in seen and key not in repeated:
            repeated.append(key)

        seen.add(key)

    return _RepeatedKeys(read, tuple(repeated))


def _whole_number(digits: str) -> int | _LongInteger:
    """Return a JSON integer as Python reads it, or its length when it is too long for Python.

    Python refuses to convert a decimal string of more than
    `sys.get_int_max_str_digits()` digits. That limit guards against a
    conversion whose cost grows with the square of the length, and Python's
    error names no place in the document. So the length is kept instead, and
    the number is refused later, in place.
    """

    try:
        return int(digits)
    except ValueError:
        return _LongInteger(len(digits.lstrip("-")))


def _read_version(document: dict[str, object]) -> SchemaVersion:
    """Read the document's `schema_version` before any other rule of this build applies.

    This is where the package builds a `SchemaVersion` from a file. So it is
    the one place where the rule that a version counts from 1 is applied to a
    document.

    Raises:
        LayoutFormatError: `schema_version` is missing, given twice, not a
            whole number this build can read, or less than 1. The message
            names the value.
    """

    if isinstance(document, _RepeatedKeys) and "schema_version" in document.repeated:
        raise LayoutFormatError(
            "the document: the key 'schema_version' is given twice, so which version wrote it "
            "cannot be known"
        )

    if "schema_version" not in document:
        raise LayoutFormatError("the document: is missing 'schema_version'")

    version = document["schema_version"]

    if isinstance(version, _LongInteger):
        raise LayoutFormatError(
            f"schema_version: {_json_value(version)} is longer than this build reads, so which "
            "version wrote the document cannot be known"
        )

    if isinstance(version, bool) or not isinstance(version, int):
        raise LayoutFormatError(
            f"schema_version: a schema version is a whole number, not {_json_value(version)}"
        )

    try:
        return SchemaVersion(version)
    except InvalidLayout as error:
        raise LayoutFormatError(f"schema_version: {error}") from None


def _refuse_kept(document: dict[str, object]) -> None:
    """Refuse the first value that the parse kept rather than rejected, naming where it is.

    The document is walked in reading order with a list rather than by
    recursion, so a document nested as deep as the parser reads is walked
    without a `RecursionError`.

    Raises:
        LayoutFormatError: an object gives a key twice, a number is `NaN` or
            `Infinity`, or a whole number is longer than this build reads.
    """

    pending: list[tuple[str, object]] = [("", document)]

    while pending:
        where, value = pending.pop()

        if isinstance(value, _RepeatedKeys):
            raise LayoutFormatError(
                f"{where or 'the document'}: the key {value.repeated[0]!r} is given twice, so "
                "which value was meant cannot be known"
            )

        if isinstance(value, _NonFinite):
            raise LayoutFormatError(f"{where}: {value.written} is not a number a layout holds")

        if isinstance(value, _LongInteger):
            raise LayoutFormatError(
                f"{where}: {_json_value(value)} is longer than this build reads, so the "
                "document is not JSON this build can read"
            )

        if isinstance(value, dict):
            pending.extend(reversed([(_member(where, key), item) for key, item in value.items()]))
        elif isinstance(value, list):
            pending.extend(
                reversed([(f"{where}[{index}]", item) for index, item in enumerate(value)])
            )


def _is_written_area_id(key: str) -> bool:
    """Whether `key` is an Area id as `workspace_to_dict` writes one: exactly `str` of the number.

    The key must be ASCII digits only, because `str.isdecimal` accepts the
    digits of every script and `int` reads them. It must be no longer than
    the largest id, which keeps `int` within the digit limit beyond which it
    refuses to convert. And it must have no leading zero, so that each id has
    one key and two keys cannot name one Area.
    """

    return (
        key.isascii()
        and key.isdecimal()
        and len(key) <= len(str(AREA_ID_MAXIMUM))
        and str(int(key)) == key
    )


def _member(where: str, key: str) -> str:
    """Return the place of `key`'s value in the object at `where`, as an error names it."""

    if not key.isidentifier():
        return f"{where}[{key!r}]"

    return f"{where}.{key}" if where else key


def _json_kind(value: object) -> str:
    """Return the kind of a parsed JSON value, in JSON's words."""

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true or false"

    if isinstance(value, int | float | _NonFinite | _LongInteger):
        return "a number"

    if isinstance(value, str):
        return "a string"

    if isinstance(value, list):
        return "a list"

    if isinstance(value, dict):
        return "an object"

    return type(value).__name__


def _json_value(value: object) -> str:
    """Return a parsed JSON value as an error names it: a number or string itself, else its kind."""

    if isinstance(value, bool) or value is None:
        return _json_kind(value)

    if isinstance(value, int | float | str):
        return shown(value)

    if isinstance(value, _NonFinite):
        return value.written

    if isinstance(value, _LongInteger):
        return f"a whole number of {value.digits:,} digits"

    return _json_kind(value)
