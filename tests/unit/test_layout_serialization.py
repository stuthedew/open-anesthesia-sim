"""Unit tests for `layout/serialization.py`, the layout as JSON.

`PL-SSQW` Q5 decided what reading a layout owes its reader (project owner,
2026-09-27, ratified): an invalid layout raises `LayoutFormatError` naming the
invariant that failed and where, nothing is repaired, and a document from a
newer build is refused as newer rather than as invalid, because the two are
answered differently. These hold each named failure to a refusal that says
which it was. The file around a layout - where it lives, what is set aside,
which generation is loaded - is `PL-SSQW`'s store and is not built yet.
"""

import json

import pytest

from anesthesia_sim.layout.exceptions import LayoutFormatError, UnsupportedSchemaVersion
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.serialization import (
    LAYOUT_SCHEMA_VERSION,
    layout_from_dict,
    layout_from_json,
    layout_to_dict,
    layout_to_json,
)
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, Window


def document(**changes: object) -> dict[str, object]:
    """A valid two-Area document, with any top-level field replaced."""

    written: dict[str, object] = {
        "schema_version": 1,
        "next_area_id": 3,
        "windows": [
            {
                "tree": {
                    "split": "row",
                    "sizes": [0.7, 0.3],
                    "children": [
                        {"area": 1, "view": "concentration_chart"},
                        {"area": 2, "view": "agent_accounting"},
                    ],
                }
            }
        ],
    }
    written.update(changes)

    return written


def with_tree(tree: object, next_area_id: int = 3) -> str:
    return json.dumps(document(next_area_id=next_area_id, windows=[{"tree": tree}]))


def refused(text: str) -> str:
    """The message reading `text` is refused with."""

    with pytest.raises(LayoutFormatError) as raised:
        layout_from_json(text)

    return str(raised.value)


def test_the_written_form_is_the_decided_shape() -> None:
    """`PL-HJPY` Q5's illustration, with a split named a row rather than horizontal."""

    model = LayoutModel(
        (
            Window(
                Split(
                    Orientation.ROW,
                    (0.7, 0.3),
                    (
                        Area(AreaId(1), ViewKind("concentration_chart")),
                        Area(AreaId(2), ViewKind("agent_accounting")),
                    ),
                )
            ),
        ),
        AreaId(3),
    )

    assert json.loads(layout_to_json(model)) == document()
    assert layout_from_json(json.dumps(document())) == model
    assert layout_to_json(model).endswith("}\n")


def test_the_body_carries_no_version_and_the_document_carries_one() -> None:
    """A Workspace holds the body under its file's one version, so a body never holds its own."""

    body = layout_to_dict(layout_from_json(json.dumps(document())))

    assert "schema_version" not in body

    with pytest.raises(LayoutFormatError, match="'schema_version', which the schema does not"):
        layout_from_dict({**body, "schema_version": 1})


def test_a_document_from_a_newer_build_is_refused_as_newer_before_its_body_is_read() -> None:
    """`PL-SSQW` Q5: a newer file is the reader's own work, refused whole and left untouched.

    Its body may follow rules this build does not know - here a key this
    schema lacks - and it is still reported as newer, never as invalid.
    """

    newer = json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1, "workspace_tabs": []})

    with pytest.raises(UnsupportedSchemaVersion) as raised:
        layout_from_json(newer)

    assert (raised.value.found, raised.value.supported) == (2, 1)
    assert "versions up to 1" in str(raised.value)


def test_a_version_that_is_not_a_whole_number_from_one_is_a_format_error() -> None:
    for version, named in ((0, "counts from 1"), (-3, "counts from 1"), ("1", "whole number")):
        assert named in refused(json.dumps(document(schema_version=version)))

    assert "whole number, not true or false" in refused(json.dumps(document(schema_version=True)))
    assert "missing 'schema_version'" in refused(json.dumps({"next_area_id": 3, "windows": []}))


def test_text_that_is_not_json_is_refused_as_such() -> None:
    whole = json.dumps(document())

    assert "not JSON this build can read" in refused(whole[: len(whole) // 2])
    assert "not JSON this build can read" in refused("")
    assert "a layout document is an object, not a list" in refused("[]")

    with pytest.raises(TypeError, match="read from a str"):
        layout_from_json(whole.encode())  # type: ignore[arg-type]


def test_a_key_given_twice_is_refused_rather_than_resolved() -> None:
    """`json` keeps the last of two equal keys silently; which was meant cannot be known."""

    twice = '{"schema_version": 1, "next_area_id": 2, "next_area_id": 3, "windows": []}'

    assert "'next_area_id' is given twice" in refused(twice)


def test_non_finite_numbers_are_refused_by_name() -> None:
    for constant in ("NaN", "Infinity", "-Infinity"):
        text = with_tree({"split": "row", "sizes": [0.5, 0.5], "children": []}).replace(
            "[0.5, 0.5]", f"[{constant}, 0.5]"
        )

        assert f"{constant} is not a number a layout holds" in refused(text)


def test_each_invariant_is_refused_by_name_and_place() -> None:
    """`PL-SSQW` Q5's examples and the rest: the message says what broke and where."""

    one = {"area": 1, "view": "concentration_chart"}
    two = {"area": 2, "view": "concentration_chart"}
    cases: list[tuple[object, str]] = [
        ({"split": "row", "sizes": [1.0], "children": [one]}, "windows[0].tree: a split holds two"),
        (
            {"split": "row", "sizes": [0.5, 0.25, 0.25], "children": [one, two]},
            "windows[0].tree: a split's sizes are one per child",
        ),
        (
            {"split": "row", "sizes": [0.5, 0.25], "children": [one, two]},
            "windows[0].tree: a split's sizes sum to one",
        ),
        (
            {"split": "row", "sizes": [1, 0.5], "children": [one, two]},
            "sizes[0]: a size is a fraction",
        ),
        (
            {"split": "horizontal", "sizes": [0.5, 0.5], "children": [one, two]},
            'windows[0].tree.split: a split is "row" or "column", not \'horizontal\'',
        ),
        (
            {
                "split": "row",
                "sizes": [0.5, 0.5],
                "children": [
                    one,
                    {
                        "split": "column",
                        "sizes": [0.5, 0.25],
                        "children": [two, {"area": 3, "view": "wash_in"}],
                    },
                ],
            },
            "windows[0].tree.children[1]: a split's sizes sum to one",
        ),
        (
            {
                "split": "row",
                "sizes": [0.5, 0.5],
                "children": [
                    one,
                    {
                        "split": "row",
                        "sizes": [0.5, 0.5],
                        "children": [two, {"area": 3, "view": "wash_in"}],
                    },
                ],
            },
            "windows[0].tree: a row split never holds another row split",
        ),
        ({"area": 1, "view": "concentration_chart", "views": []}, "has 'views', which the schema"),
        ({"area": 1, "split": "row"}, "names both"),
        ({"view": "concentration_chart"}, "names neither"),
        ({"area": 1}, "is missing 'view'"),
        ({"area": True, "view": "concentration_chart"}, "an Area id is a whole number, not true"),
        ({"area": 1.0, "view": "concentration_chart"}, "an Area id is a whole number, not 1.0"),
        ({"area": 0, "view": "concentration_chart"}, "an Area id is a whole number from 1"),
        ({"area": 1, "view": "Concentration Chart"}, ".view: a View kind is a tag"),
        ({"area": 1, "view": 7}, ".view: a View kind is a string, not a number"),
        ([one], "windows[0].tree: a node is an object"),
    ]

    for tree, named in cases:
        assert named in refused(with_tree(tree)), tree


def test_the_layouts_own_invariants_are_refused_by_name() -> None:
    """No window, a shared id, a counter at or below an id in use: `PL-HJPY`'s three."""

    one = {"tree": {"area": 1, "view": "concentration_chart"}}

    assert "at least one window" in refused(json.dumps(document(windows=[])))
    assert "two Areas hold the id 1" in refused(json.dumps(document(windows=[one, one])))
    assert "next_area_id is 1 and an Area already holds the id 1" in refused(
        json.dumps(document(next_area_id=1, windows=[one]))
    )
    assert "windows: a layout's windows are a list" in refused(json.dumps(document(windows={})))
    assert "windows[0]: a window is an object" in refused(json.dumps(document(windows=[[]])))


def test_a_view_kind_no_view_is_registered_under_loads() -> None:
    """`PL-SSQW` Q5: an unknown kind is the registry's to report in its Area, not a file error."""

    model = layout_from_json(with_tree({"area": 1, "view": "retired_view"}, next_area_id=2))

    assert [area.view for area in model.unknown_kinds({"concentration_chart"})] == ["retired_view"]
    assert json.loads(layout_to_json(model))["windows"][0]["tree"]["view"] == "retired_view"


def test_a_document_nested_past_what_can_be_read_is_refused_rather_than_crashing() -> None:
    """No screen shows a layout nested this deep; reading one says so instead of overflowing."""

    tree: object = {"area": 1, "view": "concentration_chart"}

    for depth in range(4000):
        tree = {
            "split": "row" if depth % 2 else "column",
            "sizes": [0.5, 0.5],
            "children": [tree, {"area": depth + 2, "view": "concentration_chart"}],
        }

    assert "nested more deeply than can be read" in refused(with_tree(tree, next_area_id=5000))


def test_an_integer_too_long_to_read_is_a_format_error() -> None:
    """Python refuses to read an int of more than 4,300 digits; that is a refusal, not an escape."""

    text = json.dumps(document()).replace('"next_area_id": 3', '"next_area_id": ' + "9" * 5000)

    assert "not JSON this build can read" in refused(text)
