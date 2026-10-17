"""Unit tests for `layout/migrations.py`: the version, and the steps that read the ones before it.

`PL-SSQW` Q5 (project owner, 2026-09-27, ratified): a set document an older
build wrote is migrated in memory, one step per version, and the table is
empty at version 1 with the hook in place. These hold the hook to its
contract with a chain of the test's own, since the build's own is empty.
"""

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
    migrate,
    oldest_readable,
)


def renaming(old: str, new: str) -> Migration:
    def apply(body: dict[str, object]) -> dict[str, object]:
        return {new if key == old else key: value for key, value in body.items()}

    return Migration(1, apply)


def test_the_build_has_one_version_and_no_steps_yet() -> None:
    assert LAYOUT_SCHEMA_VERSION == 1
    assert MIGRATIONS == ()
    assert OLDEST_READABLE_VERSION == LAYOUT_SCHEMA_VERSION


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

    with pytest.raises(LayoutFormatError, match="reads versions from 1 to 1, and 0 is older"):
        migrate({}, 0)


def test_steps_apply_in_order_from_the_version_found_and_collect_what_was_lost() -> None:
    first = renaming("tabs", "workspaces")
    second = Migration(
        2, lambda body: {**body, "active": 0}, lossy="which tab was open was not kept"
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
        oldest_readable((renaming("a", "b"), Migration(3, dict)), 3)

    with pytest.raises(
        InvalidLayout,
        match="position 0 reads version 1, and the chain up to version 3 needs the step reading",
    ):
        migrate({}, 2, (renaming("a", "b"),), 3)


def test_a_step_that_returns_something_other_than_a_dict_is_refused() -> None:
    with pytest.raises(InvalidLayout, match="reading version 1 returned str, and a step returns"):
        migrate({}, 1, (Migration(1, lambda body: "oops"),), 2)  # type: ignore[arg-type,return-value]


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


def test_a_chain_whose_oldest_version_is_above_one_slices_from_the_version_found() -> None:
    steps = (
        Migration(2, lambda body: {**body, "two": True}),
        Migration(3, lambda body: {**body, "three": True}),
    )

    from_two = migrate({}, 2, steps, 4)
    from_three = migrate({}, 3, steps, 4)

    assert from_two.body == {"two": True, "three": True}
    assert from_three.body == {"three": True}

    with pytest.raises(LayoutFormatError, match="reads versions from 2 to 4, and 1 is older"):
        migrate({}, 1, steps, 4)
