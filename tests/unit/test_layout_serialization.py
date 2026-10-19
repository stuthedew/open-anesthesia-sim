"""Unit tests for `layout/serialization.py`, the layout as JSON.

`PL-SSQW` Q5 decided what reading a layout owes its reader (project owner,
2026-09-27, ratified): an invalid layout raises `LayoutFormatError` naming the
invariant that failed and where, nothing is repaired, and a document from a
newer build is refused as newer rather than as invalid, because the two are
answered differently. These hold each named failure to a refusal that says
which it was. The Workspace set document - the one file the application
writes, holding every Workspace with its layout and each View's saved state -
is read by the same rules, and its tests are below the layout's. The file
around it is `layout/store.py`'s, tested in `test_layout_store.py`.
"""

import inspect
import json
import sys
from collections.abc import Callable

import pytest

from anesthesia_sim.layout import migrations
from anesthesia_sim.layout import serialization as serialization_module
from anesthesia_sim.layout.exceptions import LayoutFormatError, UnsupportedSchemaVersion
from anesthesia_sim.layout.migrations import Migrated
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.serialization import (
    LAYOUT_SCHEMA_VERSION,
    layout_from_dict,
    layout_from_json,
    layout_to_dict,
    layout_to_json,
    workspace_from_dict,
    workspace_set_from_dict,
    workspace_set_from_json,
    workspace_set_to_dict,
    workspace_set_to_json,
    workspace_to_dict,
)
from anesthesia_sim.layout.tree import (
    TREE_DEPTH_MAXIMUM,
    Area,
    AreaId,
    Orientation,
    Split,
    ViewKind,
    Window,
)
from anesthesia_sim.layout.workspace import (
    Origin,
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)


def document(**changes: object) -> dict[str, object]:
    """A valid two-Area document, with any top-level field replaced."""

    written: dict[str, object] = {
        "schema_version": LAYOUT_SCHEMA_VERSION,
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


def nested_tree(depth: int) -> dict[str, object]:
    """A written tree whose deepest split sits `depth` deep, first child of first child down.

    Areas 1 to `depth` + 1, so the layout's counter is `depth` + 2.
    """

    def leaf(number: int) -> dict[str, object]:
        return {"area": number, "view": "concentration_chart"}

    tree: dict[str, object] = {"split": "row", "sizes": [0.5, 0.5], "children": [leaf(1), leaf(2)]}

    for level in range(1, depth):
        tree = {
            "split": "column" if level % 2 else "row",
            "sizes": [0.5, 0.5],
            "children": [tree, leaf(level + 2)],
        }

    return tree


def deep_in_the_stack[T](call: Callable[[], T], headroom: int) -> T:
    """`call()`, made where only about `headroom` frames are left before the recursion limit."""

    standing = 0
    frame = inspect.currentframe()

    while frame is not None:
        standing += 1
        frame = frame.f_back

    def descend(remaining: int) -> T:
        return call() if remaining <= 0 else descend(remaining - 1)

    return descend(sys.getrecursionlimit() - standing - headroom)


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

    assert (raised.value.found, raised.value.supported) == (3, 2)
    assert "versions up to 2" in str(raised.value)


def test_a_newer_document_is_refused_as_newer_whatever_its_other_fields_hold() -> None:
    """`PL-SSQW` Q5: no rule of this build's is applied to a newer body, its parse's included.

    `NaN`, a key given twice and a whole number longer than Python reads are
    each this build's to refuse, and a newer build may write any of them.
    Each was once refused by the parse, before the version was read, so the
    document was reported invalid rather than newer.
    """

    newer = LAYOUT_SCHEMA_VERSION + 1
    fields = (
        '"zoom": NaN',
        '"tabs": [{"pinned": -Infinity}]',
        '"tabs": {"name": "a", "name": "b"}',
        '"zoom": 1, "zoom": 2',
        '"count": ' + "9" * 5000,
    )

    for field in fields:
        with pytest.raises(UnsupportedSchemaVersion) as raised:
            layout_from_json(f'{{"schema_version": {newer}, {field}}}')

        assert raised.value.found == newer, field


def test_a_version_given_twice_or_too_long_to_read_is_a_format_error() -> None:
    """Which version wrote these cannot be known, so neither is read as newer, or as anything."""

    twice = refused('{"schema_version": 2, "schema_version": 2, "zoom": NaN}')
    too_long = refused('{"schema_version": ' + "9" * 5000 + "}")

    assert (
        "the document: the key 'schema_version' is given twice, so which version wrote it "
        "cannot be known"
    ) in twice
    assert "schema_version: a whole number of 5,000 digits is longer than this build reads" in (
        too_long
    )


def test_a_version_that_is_not_a_whole_number_from_one_is_a_format_error() -> None:
    for version, named in ((0, "counts from 1"), (-3, "counts from 1"), ("1", "whole number")):
        assert named in refused(json.dumps(document(schema_version=version)))

    assert "whole number, not true or false" in refused(json.dumps(document(schema_version=True)))
    assert "missing 'schema_version'" in refused(json.dumps({"next_area_id": 3, "windows": []}))
    assert "schema_version: a schema version is a whole number, not 1.0" in refused(
        json.dumps(document(schema_version=1.0))
    )


def test_text_that_is_not_json_is_refused_as_such() -> None:
    whole = json.dumps(document())

    assert "not JSON this build can read" in refused(whole[: len(whole) // 2])
    assert "not JSON this build can read" in refused("")
    assert "a layout document is an object, not a list" in refused("[]")

    with pytest.raises(TypeError, match="read from a str"):
        layout_from_json(whole.encode())  # type: ignore[arg-type]


def test_a_key_given_twice_is_refused_rather_than_resolved() -> None:
    """`json` keeps the last of two equal keys silently; which was meant cannot be known."""

    twice = (
        f'{{"schema_version": {LAYOUT_SCHEMA_VERSION}, "next_area_id": 2, "next_area_id": 3, '
        '"windows": []}'
    )
    nested = with_tree({"area": 1, "view": "concentration_chart"}).replace(
        '"area": 1', '"area": 1, "area": 1'
    )

    assert "'next_area_id' is given twice" in refused(twice)
    assert "the document: the key 'next_area_id' is given twice" in refused(twice)
    assert "windows[0].tree: the key 'area' is given twice" in refused(nested)


def test_non_finite_numbers_are_refused_by_name() -> None:
    for constant in ("NaN", "Infinity", "-Infinity"):
        text = with_tree({"split": "row", "sizes": [0.5, 0.5], "children": []}).replace(
            "[0.5, 0.5]", f"[{constant}, 0.5]"
        )

        assert f"{constant} is not a number a layout holds" in refused(text)
        assert f"windows[0].tree.sizes[0]: {constant} is not" in refused(text)

    # A key that is not a name is written as an index, so the place still reads as a path.
    unnamed = json.dumps(document()).replace('"windows"', '"zoom level": NaN, "windows"')

    assert "['zoom level']: NaN is not a number a layout holds" in refused(unnamed)


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
            {"split": "row", "sizes": 5, "children": [one, two]},
            "windows[0].tree.sizes: a split's sizes are a list, not a number",
        ),
        (
            {"split": "row", "sizes": [0.5, 0.5], "children": 5},
            "windows[0].tree.children: a split's children are a list, not a number",
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


def test_a_tree_nested_past_the_depth_maximum_is_refused_with_its_path() -> None:
    """`TREE_DEPTH_MAXIMUM`, checked before the reader recurses past it, naming the split's place.

    The deepest tree the model holds reads back; one split deeper is refused
    at the first split past the maximum, before anything below it is read.
    """

    deepest = layout_from_json(with_tree(nested_tree(TREE_DEPTH_MAXIMUM), TREE_DEPTH_MAXIMUM + 2))
    place = "windows[0].tree" + ".children[0]" * TREE_DEPTH_MAXIMUM

    assert len(deepest.areas()) == TREE_DEPTH_MAXIMUM + 1
    assert layout_from_json(layout_to_json(deepest)) == deepest
    assert (
        f"{place}: the tree is nested more deeply than can be read: this split sits "
        f"{TREE_DEPTH_MAXIMUM + 1} deep, and a split sits at most {TREE_DEPTH_MAXIMUM} deep"
    ) in refused(with_tree(nested_tree(TREE_DEPTH_MAXIMUM + 1), TREE_DEPTH_MAXIMUM + 3))


def test_whether_a_document_reads_does_not_depend_on_where_its_caller_stands() -> None:
    """The reader recurses no deeper than the maximum, so where its caller stands cannot matter.

    Unbounded, a tree 300 splits deep - one the model itself could build and
    write - read from the top of the stack and was refused as nested too
    deeply when the same text was read 150 frames short of the recursion
    limit. Now it is refused for its depth from both, and the deepest tree
    the model holds reads from both.
    """

    accepted = with_tree(nested_tree(TREE_DEPTH_MAXIMUM), TREE_DEPTH_MAXIMUM + 2)
    too_deep = with_tree(nested_tree(300), 302)

    assert deep_in_the_stack(lambda: layout_from_json(accepted), 150) == layout_from_json(accepted)
    assert deep_in_the_stack(lambda: refused(too_deep), 150) == refused(too_deep)
    assert f"this split sits {TREE_DEPTH_MAXIMUM + 1} deep" in refused(too_deep)


def test_a_caller_that_leaves_the_reader_too_little_stack_is_told_so() -> None:
    """The backstop: a `RecursionError` the maximum cannot prevent is refused, naming its cause.

    Reading a tree at the maximum takes about a hundred frames. A caller that
    leaves thirty runs the reader out of stack, and is refused by name rather
    than handed the `RecursionError`.
    """

    body = layout_to_dict(
        layout_from_json(with_tree(nested_tree(TREE_DEPTH_MAXIMUM), TREE_DEPTH_MAXIMUM + 2))
    )

    with pytest.raises(LayoutFormatError, match="the stack ran out while it was being read"):
        deep_in_the_stack(lambda: layout_from_dict(body), 30)


def test_text_nested_past_what_the_parser_holds_is_refused_as_unreadable() -> None:
    """A million brackets deep, `json` runs out of stack, and that is a format error.

    No version can be read from text the parser cannot finish, so a document
    claiming a newer version is refused the same way: the one case the
    newer-version rule cannot reach, which the module docstring names.
    """

    brackets = "[" * 10**6 + "]" * 10**6

    for text in (brackets, '{"schema_version": 2, "zoom": ' + brackets + "}"):
        assert "the document is nested more deeply than can be read" in refused(text)


def test_an_integer_too_long_to_read_is_a_format_error() -> None:
    """Python refuses to read an int of more than 4,300 digits; that is a refusal, not an escape."""

    text = json.dumps(document()).replace('"next_area_id": 3', '"next_area_id": ' + "9" * 5000)

    assert "not JSON this build can read" in refused(text)
    assert "next_area_id: a whole number of 5,000 digits is longer than this build reads" in (
        refused(text)
    )


# The Workspace set document, `PL-SSQW` Q2's one file.


def workspace_body(**changes: object) -> dict[str, object]:
    """A valid Workspace body over the two-Area layout, with any field replaced."""

    written: dict[str, object] = {
        "name": "Default",
        "origin": "shipped:default",
        "layout": {key: value for key, value in document().items() if key != "schema_version"},
        "view_state": {"1": {"concentration_chart": {"zoom_s": [0.0, 900.0]}}},
        "pinned_run": None,
    }
    written.update(changes)

    return written


def set_document(*workspaces: dict[str, object], active: int = 0, **changes: object) -> str:
    written: dict[str, object] = {
        "schema_version": LAYOUT_SCHEMA_VERSION,
        "active": active,
        "workspaces": list(workspaces) or [workspace_body()],
    }
    written.update(changes)

    return json.dumps(written)


def refused_set(text: str) -> str:
    with pytest.raises(LayoutFormatError) as raised:
        workspace_set_from_json(text)

    return str(raised.value)


PINNED = RunId(SessionToken("0123456789abcdef0123456789abcdef"), 2)


def the_set() -> WorkspaceSet:
    chart = ViewKind("concentration_chart")
    layout = (
        LayoutModel.single_area(chart)
        .split(AreaId(1), Orientation.ROW, 0.7)[0]
        .set_view(AreaId(2), ViewKind("agent_accounting"))
    )
    default = Workspace(
        WorkspaceName("Default"),
        Origin.shipped(ShippedWorkspaceId("default")),
        layout,
        {AreaId(1): {chart: {"zoom_s": [0.0, 900.0]}}, AreaId(2): {}},
    )
    induction = Workspace(
        WorkspaceName("Induction"), Origin.mine(), LayoutModel.single_area(chart), pinned_run=PINNED
    )

    return WorkspaceSet((default, induction), 1)


class TestWorkspaceSetDocument:
    def test_the_version_is_the_migrations_modules(self) -> None:
        assert LAYOUT_SCHEMA_VERSION is migrations.LAYOUT_SCHEMA_VERSION

    def test_a_set_round_trips_through_its_document(self) -> None:
        text = workspace_set_to_json(the_set())
        read = workspace_set_from_json(text)

        assert read.workspaces == the_set()
        assert read.written_at == LAYOUT_SCHEMA_VERSION
        assert read.lossy == ()
        assert workspace_set_to_json(read.workspaces) == text
        assert text.endswith("\n")
        assert workspace_set_from_dict(workspace_set_to_dict(the_set())) == the_set()

    def test_the_document_has_the_illustrated_shape(self) -> None:
        written = json.loads(workspace_set_to_json(the_set()))

        assert written["schema_version"] == LAYOUT_SCHEMA_VERSION
        assert written["active"] == 1
        assert [each["name"] for each in written["workspaces"]] == ["Default", "Induction"]
        assert written["workspaces"][0]["origin"] == "shipped:default"
        assert written["workspaces"][1]["origin"] == "mine"
        assert written["workspaces"][0]["layout"]["next_area_id"] == 3
        assert written["workspaces"][0]["view_state"] == {
            "1": {"concentration_chart": {"zoom_s": [0.0, 900.0]}},
            "2": {},
        }
        assert written["workspaces"][1]["view_state"] == {}
        assert written["workspaces"][0]["pinned_run"] is None
        assert written["workspaces"][1]["pinned_run"] == {
            "session": "0123456789abcdef0123456789abcdef",
            "number": 2,
        }

    @pytest.mark.parametrize(
        ("pinned_run", "said"),
        [
            ("Run 2", "workspaces[0].pinned_run: a pinned run is an object, not a string"),
            ({"number": 2}, "workspaces[0].pinned_run: is missing 'session'"),
            (
                {"session": "0" * 32, "number": 2, "name": "Run 2"},
                "workspaces[0].pinned_run: has 'name', which the schema does not",
            ),
            (
                {"session": 7, "number": 2},
                "workspaces[0].pinned_run.session: a run's session is a string, not a number",
            ),
            (
                {"session": "0" * 32, "number": 2.0},
                "workspaces[0].pinned_run.number: a run's number is a whole number, not 2.0",
            ),
            (
                {"session": "0" * 32, "number": True},
                "workspaces[0].pinned_run.number: a run's number is a whole number, not true",
            ),
            (
                {"session": "0" * 32, "number": 0},
                "workspaces[0].pinned_run: runs are numbered from 1, not 0",
            ),
            (
                {"session": "ABC", "number": 1},
                "workspaces[0].pinned_run: a session token is 32 lowercase hexadecimal digits",
            ),
        ],
    )
    def test_a_pin_that_is_not_a_run_identity_is_refused_by_name_and_place(
        self, pinned_run: object, said: str
    ) -> None:
        assert said in refused_set(set_document(workspace_body(pinned_run=pinned_run)))

    def test_a_workspace_without_a_pinned_run_field_is_refused_at_version_two(self) -> None:
        body = {key: value for key, value in workspace_body().items() if key != "pinned_run"}

        assert "workspaces[0]: is missing 'pinned_run'" in refused_set(set_document(body))

    def test_a_version_one_document_is_read_with_every_workspace_unpinned(self) -> None:
        body = {key: value for key, value in workspace_body().items() if key != "pinned_run"}
        read = workspace_set_from_json(set_document(body, schema_version=1))

        assert read.written_at == 1
        assert read.lossy == ()
        assert read.workspaces.current.pinned_run is None

    def test_a_body_is_written_and_read_without_a_version(self) -> None:
        body = workspace_to_dict(the_set().workspaces[0])

        assert "schema_version" not in body
        assert workspace_from_dict(body) == the_set().workspaces[0]

        with pytest.raises(TypeError, match="not str"):
            workspace_to_dict("Default")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="not tuple"):
            workspace_set_to_dict(())  # type: ignore[arg-type]

    def test_a_newer_document_is_refused_as_newer_whatever_it_holds(self) -> None:
        with pytest.raises(UnsupportedSchemaVersion) as raised:
            workspace_set_from_json(
                json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1, "tabs": "anything"})
            )

        assert (raised.value.found, raised.value.supported) == (
            LAYOUT_SCHEMA_VERSION + 1,
            LAYOUT_SCHEMA_VERSION,
        )

    @pytest.mark.parametrize(
        ("text", "said"),
        [
            ("[]", "the document: a Workspace set document is an object, not a list"),
            (set_document(schema_version=0), "schema_version: a schema version counts from 1"),
            (
                set_document(active=True),
                "active: the active Workspace's position is a whole number, not true or false",
            ),
            (
                set_document(active=2),
                "the Workspace set: the active position is 2, and this set's positions run from 0",
            ),
            (
                set_document(workspaces={}),
                "workspaces: a set's Workspaces are a list, not an object",
            ),
            (
                set_document(workspaces=[]),
                "the Workspace set: a Workspace set holds at least one Workspace",
            ),
            (
                set_document(workspace_body(), workspace_body()),
                "the Workspace set: two Workspaces are named 'Default'",
            ),
            (
                set_document(workspace_body(name="")),
                "workspaces[0].name: a Workspace name is not empty",
            ),
            (
                set_document(workspace_body(name=1)),
                "workspaces[0].name: a Workspace's name is a string, not a number",
            ),
            (
                set_document(workspace_body(origin="theirs")),
                "workspaces[0].origin: an origin is written 'mine' or 'shipped:'",
            ),
            (
                set_document(workspace_body(origin=None)),
                "workspaces[0].origin: a Workspace's origin is a string, not null",
            ),
            (
                set_document(workspace_body(colour="red")),
                "workspaces[0]: has 'colour', which the schema does not",
            ),
            (
                set_document(workspace_body(layout=[])),
                "workspaces[0].layout: a layout is an object, not a list",
            ),
            (
                set_document(workspace_body(view_state=[])),
                "workspaces[0].view_state: a Workspace's view_state is an object keyed by Area id",
            ),
            (
                set_document(workspace_body(view_state={"one": {}})),
                "workspaces[0].view_state.one: view_state is keyed by Area id, a whole number",
            ),
            (
                set_document(workspace_body(view_state={"0": {}})),
                "workspaces[0].view_state['0']: an Area id is a whole number from 1",
            ),
            (
                set_document(workspace_body(view_state={"01": {}})),
                "workspaces[0].view_state['01']: view_state is keyed by Area id, a whole number "
                "written as a string of digits with no sign and no leading zero, not '01'",
            ),
            (
                set_document(workspace_body(view_state={"\uff11": {}})),
                "view_state is keyed by Area id, a whole number written as a string of digits",
            ),
            (
                set_document(workspace_body(view_state={"1" * 5000: {}})),
                "view_state is keyed by Area id, a whole number written as a string of digits",
            ),
            (
                set_document(workspace_body(view_state={"9": {}})),
                "workspaces[0]: view_state names Area 9, which the layout does not hold",
            ),
            (
                set_document(workspace_body(view_state={"1": []})),
                "workspaces[0].view_state['1']: an Area's saved state is an object keyed by View",
            ),
            (
                set_document(workspace_body(view_state={"1": {"Chart": {}}})),
                "workspaces[0].view_state['1'].Chart: a View kind is a tag",
            ),
            (
                set_document(workspace_body(view_state={"1": {"concentration_chart": 3}})),
                "workspaces[0].view_state['1'].concentration_chart: a View's saved state is an",
            ),
        ],
    )
    def test_each_way_a_set_document_fails_is_refused_by_name_and_place(
        self, text: str, said: str
    ) -> None:
        assert said in refused_set(text)

    def test_a_layout_inside_a_workspace_is_placed_from_the_workspace(self) -> None:
        layout = {key: value for key, value in document().items() if key != "schema_version"}
        layout["windows"][0]["tree"]["children"][1]["view"] = "Agent"  # type: ignore[index]

        bad_view = refused_set(set_document(workspace_body(layout=layout)))

        layout["windows"][0]["tree"]["children"][1]["view"] = "agent_accounting"  # type: ignore[index]
        layout["next_area_id"] = 2

        bad_counter = refused_set(set_document(workspace_body(layout=layout)))

        assert bad_view.startswith(
            "workspaces[0].layout.windows[0].tree.children[1].view: a View kind is a tag"
        )
        assert bad_counter.startswith(
            "workspaces[0].layout: next_area_id is 2 and an Area already holds the id 2"
        )

    def test_a_key_given_twice_anywhere_in_the_document_is_refused_where_it_stands(self) -> None:
        text = set_document().replace('"active": 0', '"active": 0, "active": 1')

        assert "the document: the key 'active' is given twice" in refused_set(text)

    def test_a_body_with_a_key_that_is_not_a_string_is_refused_by_name(self) -> None:
        with pytest.raises(
            LayoutFormatError, match="keyed by Area id written as a string, not a number"
        ):
            workspace_from_dict(workspace_body(view_state={1: {}}))

    def test_the_written_body_shares_nothing_with_the_workspace(self) -> None:
        workspace = the_set().workspaces[0]
        written = workspace_to_dict(workspace)
        zoom = written["view_state"]["1"]["concentration_chart"]["zoom_s"]  # type: ignore[index]
        zoom.append(1800.0)

        assert workspace.state_of(AreaId(1), ViewKind("concentration_chart")) == {
            "zoom_s": [0.0, 900.0]
        }

    def test_a_set_document_is_read_from_text(self) -> None:
        with pytest.raises(
            TypeError, match="a Workspace set document is read from a str, not dict"
        ):
            workspace_set_from_json({})  # type: ignore[arg-type]


class TestVersionPlumbing:
    """The parts a version bump will lean on, exercised with the version patched or a step faked."""

    def test_the_written_text_is_the_same_whatever_order_the_state_was_given_in(self) -> None:
        chart = ViewKind("concentration_chart")
        accounting = ViewKind("agent_accounting")
        layout = (
            LayoutModel.single_area(chart)
            .split(AreaId(1), Orientation.ROW, 0.5)[0]
            .set_view(AreaId(2), accounting)
        )
        ordered = Workspace(
            WorkspaceName("D"),
            Origin.mine(),
            layout,
            {AreaId(1): {accounting: {"a": 1}, chart: {"b": 2}}, AreaId(2): {}},
        )
        reversed_in = Workspace(
            WorkspaceName("D"),
            Origin.mine(),
            layout,
            {AreaId(2): {}, AreaId(1): {chart: {"b": 2}, accounting: {"a": 1}}},
        )

        assert workspace_set_to_json(WorkspaceSet((ordered,), 0)) == workspace_set_to_json(
            WorkspaceSet((reversed_in,), 0)
        )
        assert list(workspace_to_dict(reversed_in)["view_state"]) == ["1", "2"]  # type: ignore[call-overload]

    def test_a_lossy_migration_reaches_the_reader_with_the_version_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_migrate(body: dict[str, object], written_at: int) -> Migrated:
            return Migrated(body, ("which tab was open was not kept",))

        monkeypatch.setattr(serialization_module, "migrate", fake_migrate)

        read = workspace_set_from_json(workspace_set_to_json(the_set()))

        assert read.workspaces == the_set()
        assert read.written_at == LAYOUT_SCHEMA_VERSION
        assert read.lossy == ("which tab was open was not kept",)

    def test_a_single_layout_document_is_read_at_the_current_version_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            serialization_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1
        )

        assert (
            f"schema_version: a document holding one layout on its own is read at version "
            f"{LAYOUT_SCHEMA_VERSION + 1} only, and this one was written at {LAYOUT_SCHEMA_VERSION}"
        ) in refused(json.dumps(document()))
