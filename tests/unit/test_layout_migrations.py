"""Unit tests for `layout/migrations.py`: the version, and the steps that read the ones before it.

`PL-SSQW` Q5 (project owner, 2026-09-27, ratified): a set document an older
build wrote is migrated in memory, one step per version. Most of these hold the
hook to its contract with a chain of the test's own. The build's own chain has
one step, which `PL-7Z84` added with `pinned_run` at version 2.
"""

import json

import pytest

from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    UnsupportedSchemaVersion,
)
from anesthesia_sim.layout.migrations import (
    LAYOUT_SCHEMA_VERSION,
    MIGRATIONS,
    OLDEST_READABLE_VERSION,
    Migration,
    SchemaVersion,
    migrate,
    oldest_readable,
)


def renaming(old: str, new: str) -> Migration:
    def apply(body: dict[str, object]) -> dict[str, object]:
        return {new if key == old else key: value for key, value in body.items()}

    return Migration(SchemaVersion(1), apply)


def test_the_build_writes_version_two_and_reads_version_one_through_one_step() -> None:
    assert LAYOUT_SCHEMA_VERSION == 2
    assert tuple(step.reads for step in MIGRATIONS) == (1,)
    assert OLDEST_READABLE_VERSION == 1


def test_version_one_workspaces_are_read_unpinned_and_nothing_is_lost() -> None:
    """`PL-7Z84`: no run could be pinned before version 2, so version 1 Workspaces are unpinned."""

    layout = {"next_area_id": 2, "windows": [{"tree": {"area": 1, "view": "concentration_chart"}}]}
    workspace = {"name": "Mine", "origin": "mine", "layout": layout, "view_state": {}}
    other = {**workspace, "name": "Other"}
    body: dict[str, object] = {"active": 1, "workspaces": [workspace, other]}

    migrated = migrate(body, 1)

    assert migrated.body == {
        "active": 1,
        "workspaces": [{**workspace, "pinned_run": None}, {**other, "pinned_run": None}],
    }
    assert migrated.lossy == ()
    assert "pinned_run" not in workspace


def test_a_version_one_workspace_holding_a_pin_is_refused_rather_than_read_as_one() -> None:
    pinned = {"name": "Mine", "pinned_run": {"session": "0" * 32, "number": 1}}

    with pytest.raises(
        LayoutFormatError,
        match=r"workspaces\[1\]: has 'pinned_run', which schema version 1 does not",
    ):
        migrate({"active": 0, "workspaces": [{"name": "First"}, pinned]}, 1)


def test_a_version_one_body_of_the_wrong_shape_is_left_for_the_reader_to_name() -> None:
    for body in ({"active": 0}, {"workspaces": "none"}, {"workspaces": [3]}):
        assert migrate(json.loads(json.dumps(body)), 1).body == body


def test_a_body_at_the_current_version_passes_through_unchanged() -> None:
    body: dict[str, object] = {"active": 0, "workspaces": []}

    migrated = migrate(body, LAYOUT_SCHEMA_VERSION)

    assert migrated.body == body
    assert migrated.lossy == ()


def test_a_newer_version_is_refused_as_newer_and_an_older_one_with_no_step_as_unreadable() -> None:
    with pytest.raises(UnsupportedSchemaVersion) as newer:
        migrate({}, LAYOUT_SCHEMA_VERSION + 1)

    assert (newer.value.found, newer.value.supported) == (
        LAYOUT_SCHEMA_VERSION + 1,
        LAYOUT_SCHEMA_VERSION,
    )

    with pytest.raises(LayoutFormatError, match="reads versions from 1 to 2, and 0 is older"):
        migrate({}, 0)


def test_steps_apply_in_order_from_the_version_found_and_collect_what_was_lost() -> None:
    first = renaming("tabs", "workspaces")
    second = Migration(
        SchemaVersion(2),
        lambda body: {**body, "active": 0},
        lossy="which tab was open was not kept",
    )
    steps = (first, second)

    from_one = migrate({"tabs": []}, 1, steps, 3)
    from_two = migrate({"workspaces": []}, 2, steps, 3)
    current = migrate({"workspaces": [], "active": 1}, 3, steps, 3)

    assert from_one.body == {"workspaces": [], "active": 0}
    assert from_one.lossy == ("which tab was open was not kept",)
    assert from_two.body == {"workspaces": [], "active": 0}
    assert from_two.lossy == ("which tab was open was not kept",)
    assert current.body == {"workspaces": [], "active": 1}
    assert current.lossy == ()


def test_a_chain_with_a_gap_is_refused_when_it_is_built() -> None:
    assert oldest_readable((renaming("a", "b"), Migration(2, dict)), 3) == 1

    with pytest.raises(
        InvalidLayout,
        match="position 1 reads version 3, and the chain up to version 3 needs the step reading",
    ):
        oldest_readable((renaming("a", "b"), Migration(SchemaVersion(3), dict)), 3)

    with pytest.raises(
        InvalidLayout,
        match="position 0 reads version 1, and the chain up to version 3 needs the step reading",
    ):
        migrate({}, 2, (renaming("a", "b"),), 3)


def test_a_step_that_returns_something_other_than_a_dict_is_refused() -> None:
    with pytest.raises(InvalidLayout, match="reading version 1 returned str, and a step returns"):
        migrate({}, 1, (Migration(SchemaVersion(1), lambda body: "oops"),), 2)  # type: ignore[arg-type,return-value]


def test_a_step_says_which_version_it_reads_and_what_it_loses() -> None:
    with pytest.raises(InvalidLayout, match="counts from 1, not 0"):
        Migration(0, dict)

    with pytest.raises(InvalidLayout, match="says what it loses"):
        Migration(1, dict, lossy="")

    with pytest.raises(TypeError, match="not bool"):
        Migration(True, dict)

    with pytest.raises(TypeError, match="apply is callable, not str"):
        Migration(1, "rename")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="lossy is a str or None, not bool"):
        Migration(1, dict, lossy=True)  # type: ignore[arg-type]


def test_a_schema_version_is_checked_once_and_a_step_builds_through_it() -> None:
    """`PL-8JV2`: `SchemaVersion` checks the version rule once, and builds each step's version.

    Before `SchemaVersion` existed, `Migration`, the reader's `_check_version`
    and `oldest_readable` each held their own copy of the rule or had none, and
    a bare `int` reached the store.
    """

    assert SchemaVersion(1) == 1
    assert f"{SchemaVersion(2)}" == "2"
    assert json.dumps({"schema_version": SchemaVersion(2)}) == '{"schema_version": 2}'

    for value in (0, -1):
        with pytest.raises(InvalidLayout, match=f"a schema version counts from 1, not {value}"):
            SchemaVersion(value)

    for value in (True, 1.0, "1"):
        with pytest.raises(TypeError, match="a schema version is an int"):
            SchemaVersion(value)

    built = Migration(1, dict)  # type: ignore[arg-type]

    assert isinstance(built.reads, SchemaVersion)
    assert built.reads == 1

    assert isinstance(LAYOUT_SCHEMA_VERSION, SchemaVersion)
    assert isinstance(OLDEST_READABLE_VERSION, SchemaVersion)
    assert all(isinstance(step.reads, SchemaVersion) for step in MIGRATIONS)


def test_a_chain_longer_than_the_versions_before_the_current_one_is_refused() -> None:
    steps = (renaming("a", "b"), Migration(SchemaVersion(2), dict))

    with pytest.raises(InvalidLayout, match="a schema version counts from 1, not 0"):
        oldest_readable(steps, SchemaVersion(2))


def test_a_chain_whose_oldest_version_is_above_one_slices_from_the_version_found() -> None:
    steps = (
        Migration(SchemaVersion(2), lambda body: {**body, "two": True}),
        Migration(SchemaVersion(3), lambda body: {**body, "three": True}),
    )

    from_two = migrate({}, 2, steps, 4)
    from_three = migrate({}, 3, steps, 4)

    assert from_two.body == {"two": True, "three": True}
    assert from_three.body == {"three": True}

    with pytest.raises(LayoutFormatError, match="reads versions from 2 to 4, and 1 is older"):
        migrate({}, 1, steps, 4)
