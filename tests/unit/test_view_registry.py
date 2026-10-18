"""Unit tests for `app/view_registry.py`: the View kinds this build can draw.

`PL-R1WQ` holds each tag as a literal written once beside its entry, so a
rename of a class or a title cannot change what a saved layout means. These
tests pin each tag against the string a saved file holds, check that every
shipped Workspace names only registered kinds, and hold the retirement table
to its two rules: a retired tag is never registered again, and a renamed
View's new tag is registered. The notice text is checked against sentences
written out here. The module imports no toolkit, so these run with no display.
"""

import subprocess
import sys

import pytest

from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    REGISTERED,
    RETIRED_TAGS,
    WASH_IN,
    RegisteredView,
    RetiredTag,
    missing_view_text,
    registry,
    retirements,
)
from anesthesia_sim.layout.shipped import SHIPPED_WORKSPACE_IDS, shipped_workspace
from anesthesia_sim.layout.tree import ViewKind

OLD = ViewKind("old_view")
NEW = ViewKind("new_view")
GONE = ViewKind("gone_view")


# --- The shipped registry ---------------------------------------------------------


def test_each_tag_is_the_string_a_saved_file_holds() -> None:
    """Changing one of these strings changes what every saved layout means."""

    assert [CONCENTRATION_CHART, WASH_IN, PARAMETER_CONTROLS, AGENT_ACCOUNTING] == [
        "concentration_chart",
        "wash_in",
        "parameter_controls",
        "agent_accounting",
    ]
    assert set(REGISTERED) == {
        "concentration_chart",
        "wash_in",
        "parameter_controls",
        "agent_accounting",
    }


def test_each_entry_is_keyed_by_its_own_tag() -> None:
    assert all(entry.kind == tag for tag, entry in REGISTERED.items())


def test_every_shipped_workspace_names_only_registered_kinds() -> None:
    """A tag change that forgets the shipped files fails here, not on a reader's screen."""

    named = set()

    for shipped_id in SHIPPED_WORKSPACE_IDS:
        layout = shipped_workspace(shipped_id).layout
        assert layout.unknown_kinds(REGISTERED.keys()) == (), shipped_id
        named |= {area.view for area in layout.areas()}

    # The check above would pass over files that named no View at all.
    assert named == {"concentration_chart", "wash_in", "parameter_controls"}


def test_no_retired_tag_is_registered() -> None:
    assert set(RETIRED_TAGS).isdisjoint(REGISTERED)


def test_the_registry_cannot_be_changed_at_run_time() -> None:
    with pytest.raises(TypeError):
        REGISTERED["other_view"] = RegisteredView(ViewKind("other_view"), "Other")  # type: ignore[index]


def test_importing_the_registry_loads_no_toolkit() -> None:
    """The registry is read by tests and by a headless check, so it must not need a display."""

    probe = (
        "import sys\n"
        "import anesthesia_sim.app.view_registry\n"
        "loaded = sorted(name for name in sys.modules "
        "if name.split('.')[0] in {'PySide6', 'pyqtgraph', 'shiboken6'})\n"
        "print(loaded)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "[]"


# --- Building a registry and a retirement table ------------------------------------


def test_a_registry_refuses_two_views_under_one_tag() -> None:
    with pytest.raises(ValueError, match="two Views are registered under the tag 'old_view'"):
        registry(RegisteredView(OLD, "One"), RegisteredView(OLD, "Two"))


def test_a_registry_refuses_an_entry_of_another_type() -> None:
    with pytest.raises(TypeError, match="RegisteredView entries, not str"):
        registry("old_view")  # type: ignore[arg-type]


def test_an_entry_refuses_a_plain_string_kind_and_an_empty_title() -> None:
    """A plain `str` kind would skip the syntax check `ViewKind` makes."""

    with pytest.raises(TypeError, match="a View's kind is a ViewKind, not str"):
        RegisteredView("old_view", "Old")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="the View of kind 'old_view' has no title"):
        RegisteredView(OLD, "  ")


def test_a_retired_tag_is_never_registered_again() -> None:
    registered = registry(RegisteredView(OLD, "Old"), RegisteredView(NEW, "New"))

    with pytest.raises(ValueError, match="'old_view' is both retired and registered"):
        retirements(registered, RetiredTag(OLD, "0.7.0", NEW))


def test_a_rename_must_name_a_registered_successor() -> None:
    registered = registry(RegisteredView(NEW, "New"))

    with pytest.raises(ValueError, match="renamed to 'gone_view', which no View is registered"):
        retirements(registered, RetiredTag(OLD, "0.7.0", GONE))


def test_a_tag_is_retired_once() -> None:
    registered = registry(RegisteredView(NEW, "New"))

    with pytest.raises(ValueError, match="'old_view' is retired twice"):
        retirements(registered, RetiredTag(OLD, "0.7.0", NEW), RetiredTag(OLD, "0.8.0"))


@pytest.mark.parametrize("version", ["0.7", "v0.7.0", "0.7.0-beta", ""])
def test_a_retirement_names_a_release_number(version: str) -> None:
    with pytest.raises(ValueError, match="three dot-separated whole numbers"):
        RetiredTag(OLD, version)


def test_a_tag_cannot_be_renamed_to_itself() -> None:
    with pytest.raises(ValueError, match="'old_view' cannot be renamed to itself"):
        RetiredTag(OLD, "0.7.0", OLD)


# --- The notice's text -----------------------------------------------------------

_KEPT = "The saved name is kept, so saving this layout loses nothing."


def test_an_unknown_kind_is_named_and_said_to_be_unknown() -> None:
    assert missing_view_text(ViewKind("from_a_later_build")) == (
        "It was saved as the View kind 'from_a_later_build'. This build does not know it. " + _KEPT
    )


def test_a_removed_kind_names_the_release_that_removed_it() -> None:
    registered = registry(RegisteredView(NEW, "New"))
    retired = retirements(registered, RetiredTag(GONE, "0.7.0"))

    assert missing_view_text(GONE, registered, retired) == (
        "It was saved as the View kind 'gone_view'. That View was removed in version 0.7.0. "
        + _KEPT
    )


def test_a_renamed_kind_names_the_release_and_the_view_it_became() -> None:
    """The notice says what the View is called now and maps nothing on the reader's behalf."""

    registered = registry(RegisteredView(NEW, "New view"), RegisteredView(GONE, "Other"))
    retired = retirements(registered, RetiredTag(OLD, "0.8.1", NEW))

    assert missing_view_text(OLD, registered, retired) == (
        "It was saved as the View kind 'old_view'. That View was renamed in version 0.8.1, "
        "and is now 'New view'. " + _KEPT
    )


def test_a_registered_kind_has_no_notice() -> None:
    with pytest.raises(ValueError, match="'wash_in' is registered, so its Area draws it"):
        missing_view_text(WASH_IN)
