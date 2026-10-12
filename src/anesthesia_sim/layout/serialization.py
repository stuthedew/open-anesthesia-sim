"""A layout as JSON: the body a Workspace holds, and a document holding one on its own.

**The shape is `PL-HJPY` Q5's**, which illustrated it and left the schema to
this build:

    {"schema_version": 1,
     "next_area_id": 3,
     "windows": [{"tree": {"split": "row", "sizes": [0.7, 0.3],
                           "children": [{"area": 1, "view": "concentration_chart"},
                                        {"area": 2, "view": "agent_accounting"}]}}]}

It departs from the illustration in one word: a split is `"row"` or `"column"`
rather than `"horizontal"`, for the reason `layout/tree.py` gives. Each window
is an object holding its tree rather than the bare tree, so a field a window
gains later is a field rather than a change of shape.

**The body carries no version; a document does.** `layout_to_dict` and
`layout_from_dict` write and read the layout alone - `next_area_id` and
`windows` - which is what a Workspace object holds beside its own fields in
`PL-HJPY`'s file, under the one `schema_version` at the top of that file
(`PL-SSQW` Q2). `layout_to_json` and `layout_from_json` write and read a
document holding one layout on its own, with `schema_version` beside the body.
A body never carries a version of its own, so a file holding several has one.

**Reading refuses, and says what it refused** (`PL-SSQW` Q5, ratified). Every
way a document can fail to describe a valid layout raises `LayoutFormatError`
naming the invariant and where it broke - `windows[0].tree.children[1]` - and
nothing is repaired, rescaled or dropped. It is strict throughout, because
nothing this code writes needs leniency and anything else deserves a person's
reading: a key the schema does not have, a key given twice, `NaN` or
`Infinity`, a fraction where a whole number belongs or the reverse, and `true`
where a number belongs are each refused by name. **A View kind no View is
registered under is not among them**: a tag of the right syntax loads, and is
the registry's to report in its own Area (`LayoutModel.unknown_kinds`).

**Versions.** `LAYOUT_SCHEMA_VERSION` is 1, the only version there has been. A
document from a newer build raises `UnsupportedSchemaVersion` before anything
else in it is read, since its body is free to follow rules this build does not
know; one claiming a version below 1 is a format error. When the version first
rises, `PL-SSQW` Q5 puts the step that reads the old one in
`layout/migrations.py`, in the same change.
"""

from __future__ import annotations

import json
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    UnsupportedSchemaVersion,
)
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind, Window

__all__ = [
    "LAYOUT_SCHEMA_VERSION",
    "layout_from_dict",
    "layout_from_json",
    "layout_to_dict",
    "layout_to_json",
]

# The version of the layout's serialized form this build writes, and the
# newest it reads. Raised by the change that alters the shape, together with
# the migration that reads the version before it (`PL-SSQW` Q5).
LAYOUT_SCHEMA_VERSION: Final = 1

# How far each level of a written document is indented.
_INDENT: Final = 2


def layout_to_dict(model: LayoutModel) -> dict[str, object]:
    """The layout's body: plain values `json.dumps` writes and `layout_from_dict` reads back.

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
    """A document holding the layout on its own, at `LAYOUT_SCHEMA_VERSION`, ending in a newline.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
    """

    document = {"schema_version": LAYOUT_SCHEMA_VERSION, **layout_to_dict(model)}

    return json.dumps(document, indent=_INDENT, allow_nan=False) + "\n"


def layout_from_dict(body: object) -> LayoutModel:
    """Read a layout's body, as `layout_to_dict` writes it.

    Raises:
        LayoutFormatError: the body does not describe a valid layout; the
            message names the invariant and where in the body it broke.
    """

    try:
        return _read_layout(body)
    except RecursionError:
        raise LayoutFormatError(
            "the layout is nested more deeply than can be read, which no layout a screen "
            "shows comes near"
        ) from None


def layout_from_json(text: str) -> LayoutModel:
    """Read a document holding one layout, as `layout_to_json` writes it.

    Raises:
        TypeError: `text` is not a `str`.
        UnsupportedSchemaVersion: a newer build wrote the document. Nothing
            past its `schema_version` is read.
        LayoutFormatError: the text is not JSON, or does not describe a valid
            layout; the message names the invariant and where it broke.
    """

    if not isinstance(text, str):
        raise TypeError(f"a layout document is read from a str, not {type(text).__name__}")

    try:
        document = json.loads(
            text, object_pairs_hook=_object_without_repeats, parse_constant=_refuse_constant
        )
    except RecursionError:
        raise LayoutFormatError("the document is nested more deeply than can be read") from None
    except ValueError as error:
        raise LayoutFormatError(f"the document is not JSON this build can read: {error}") from None

    if not isinstance(document, dict):
        raise LayoutFormatError(
            f"the document: a layout document is an object, not {_json_kind(document)}"
        )

    if "schema_version" not in document:
        raise LayoutFormatError("the document: is missing 'schema_version'")

    version = document["schema_version"]

    if isinstance(version, bool) or not isinstance(version, int):
        raise LayoutFormatError(
            f"schema_version: a schema version is a whole number, not {_json_kind(version)}"
        )

    if version > LAYOUT_SCHEMA_VERSION:
        raise UnsupportedSchemaVersion(version, LAYOUT_SCHEMA_VERSION)

    if version < 1:
        raise LayoutFormatError(
            f"schema_version: a schema version counts from 1, not {shown(version)}"
        )

    return layout_from_dict(
        {key: value for key, value in document.items() if key != "schema_version"}
    )


def _node_to_dict(node: Node) -> dict[str, object]:
    if isinstance(node, Area):
        return {"area": int(node.id), "view": str(node.view)}

    return {
        "split": node.orientation.value,
        "sizes": list(node.sizes),
        "children": [_node_to_dict(child) for child in node.children],
    }


def _read_layout(body: object) -> LayoutModel:
    fields = _fields(body, "the layout", "a layout", ("next_area_id", "windows"))
    next_area_id = _read_area_id(fields["next_area_id"], "next_area_id")
    windows = fields["windows"]

    if not isinstance(windows, list):
        raise LayoutFormatError(
            f"windows: a layout's windows are a list, not {_json_kind(windows)}"
        )

    read = tuple(_read_window(window, f"windows[{index}]") for index, window in enumerate(windows))

    try:
        return LayoutModel(read, next_area_id)
    except InvalidLayout as error:
        raise LayoutFormatError(f"the layout: {error}") from None


def _read_window(value: object, where: str) -> Window:
    fields = _fields(value, where, "a window", ("tree",))

    return Window(_read_node(fields["tree"], f"{where}.tree"))


def _read_node(value: object, where: str) -> Node:
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
        fields = _fields(value, where, "a split", ("split", "sizes", "children"))

        return _read_split(fields, where)

    raise LayoutFormatError(
        f'{where}: a node names an Area with "area" or a split with "split", and this one '
        "names neither"
    )


def _read_split(fields: dict[str, object], where: str) -> Split:
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
        _read_node(child, f"{where}.children[{index}]") for index, child in enumerate(children)
    )

    try:
        return Split(Orientation(orientation), tuple(sizes), read)
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
    """`value` as an object holding exactly `keys`: none missing, none the schema lacks."""

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


def _object_without_repeats(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """An object's pairs as a dict, refusing a key given twice rather than keeping the last."""

    read: dict[str, object] = {}

    for key, value in pairs:
        if key in read:
            raise LayoutFormatError(
                f"the key {key!r} is given twice in one object, so which value was meant "
                "cannot be known"
            )

        read[key] = value

    return read


def _refuse_constant(name: str) -> object:
    raise LayoutFormatError(f"{name} is not a number a layout holds")


def _json_kind(value: object) -> str:
    """What a parsed JSON value is, in JSON's words."""

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true or false"

    if isinstance(value, int | float):
        return "a number"

    if isinstance(value, str):
        return "a string"

    if isinstance(value, list):
        return "a list"

    if isinstance(value, dict):
        return "an object"

    return type(value).__name__


def _json_value(value: object) -> str:
    """A parsed JSON value as a refusal names it: a number or a string itself, the rest by kind."""

    if isinstance(value, bool) or value is None:
        return _json_kind(value)

    if isinstance(value, int | float | str):
        return shown(value)

    return _json_kind(value)
