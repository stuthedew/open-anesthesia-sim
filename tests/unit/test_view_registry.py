"""Unit tests for `app/view_registry.py`: the View kinds this build can draw.

`PL-R1WQ` requires each tag to be a literal written once beside its entry, so
renaming a class or a title cannot change what a saved layout means. These
tests pin each tag against the string that a saved file holds. They check that
every shipped Workspace names only registered kinds. They check the retirement
table against its two rules: a retired tag is never registered again, and a
renamed View's new tag is registered. The notice text is checked against
sentences written out here. Here each entry's factory is checked only for
being a factory. `tests/integration/test_view_contract.py` builds every
shipped View from it.
"""

import pytest

from anesthesia_sim.app.view_contract import View, ViewContext
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    REGISTERED,
    REQUIRED_REACHABLE,
    RETIRED_TAGS,
    WASH_IN,
    RegisteredView,
    RetiredTag,
    missing_view_text,
    registry,
    rename_offer_text,
    required_kinds,
    retirements,
    too_small_text,
    too_small_title,
)
from anesthesia_sim.layout.shipped import SHIPPED_WORKSPACE_IDS, shipped_workspace
from anesthesia_sim.layout.sizing import PixelSize
from anesthesia_sim.layout.tree import ViewKind

OLD = ViewKind("old_view")
NEW = ViewKind("new_view")
GONE = ViewKind("gone_view")


def _factory(context: ViewContext) -> View:
    raise AssertionError("a registry test builds no View")


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
        REGISTERED["other_view"] = RegisteredView(ViewKind("other_view"), "Other", _factory)  # type: ignore[index]


def test_every_registered_kind_has_a_factory() -> None:
    """`PL-R1WQ` Q4: a kind with nothing to build its View would draw an empty Area."""

    assert all(callable(entry.factory) for entry in REGISTERED.values())


def test_every_registered_kind_declares_a_minimum_a_reader_can_see() -> None:
    """`PL-K285` Q1: a View that holds nothing yet still needs this size, never none."""

    assert all(
        entry.minimum.width_px > 0 and entry.minimum.height_px > 0 for entry in REGISTERED.values()
    )


def test_an_entry_refuses_a_minimum_that_is_not_a_pixel_size() -> None:
    with pytest.raises(TypeError, match="declares a minimum that is not a PixelSize: tuple"):
        RegisteredView(OLD, "Old", _factory, minimum=(100, 100))  # type: ignore[arg-type]


# --- Building a registry and a retirement table ------------------------------------


def test_a_registry_refuses_two_views_under_one_tag() -> None:
    with pytest.raises(ValueError, match="two Views are registered under the tag 'old_view'"):
        registry(RegisteredView(OLD, "One", _factory), RegisteredView(OLD, "Two", _factory))


def test_a_registry_refuses_an_entry_of_another_type() -> None:
    with pytest.raises(TypeError, match="RegisteredView entries, not str"):
        registry("old_view")  # type: ignore[arg-type]


def test_an_entry_refuses_a_plain_string_kind_and_an_empty_title() -> None:
    """A plain `str` kind would skip the syntax check `ViewKind` makes."""

    with pytest.raises(TypeError, match="a View's kind is a ViewKind, not str"):
        RegisteredView("old_view", "Old", _factory)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="the View of kind 'old_view' has no title"):
        RegisteredView(OLD, "  ", _factory)


def test_a_retired_tag_is_never_registered_again() -> None:
    registered = registry(
        RegisteredView(OLD, "Old", _factory), RegisteredView(NEW, "New", _factory)
    )

    with pytest.raises(ValueError, match="'old_view' is both retired and registered"):
        retirements(registered, RetiredTag(OLD, "0.7.0", NEW))


def test_a_rename_must_name_a_registered_successor() -> None:
    registered = registry(RegisteredView(NEW, "New", _factory))

    with pytest.raises(ValueError, match="renamed to 'gone_view', which no View is registered"):
        retirements(registered, RetiredTag(OLD, "0.7.0", GONE))


def test_a_tag_is_retired_once() -> None:
    registered = registry(RegisteredView(NEW, "New", _factory))

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

_KEPT = "Choose a View from the menu above. The saved name is kept until you do."


def test_an_unknown_kind_is_named_and_said_to_be_unknown() -> None:
    assert missing_view_text(ViewKind("from_a_later_build")) == (
        "It was saved as the View kind 'from_a_later_build'. This build does not know it. " + _KEPT
    )


def test_a_removed_kind_names_the_release_that_removed_it() -> None:
    registered = registry(RegisteredView(NEW, "New", _factory))
    retired = retirements(registered, RetiredTag(GONE, "0.7.0"))

    assert missing_view_text(GONE, registered, retired) == (
        "It was saved as the View kind 'gone_view'. That View was removed in version 0.7.0. "
        + _KEPT
    )


def test_a_renamed_kind_names_the_release_and_the_view_it_became() -> None:
    """The notice says what the View is called now and maps nothing on the reader's behalf."""

    registered = registry(
        RegisteredView(NEW, "New view", _factory), RegisteredView(GONE, "Other", _factory)
    )
    retired = retirements(registered, RetiredTag(OLD, "0.8.1", NEW))

    assert missing_view_text(OLD, registered, retired) == (
        "It was saved as the View kind 'old_view'. That View was renamed in version 0.8.1, "
        "and is now 'New view'. " + _KEPT
    )


def test_a_registered_kind_has_no_notice() -> None:
    with pytest.raises(ValueError, match="'wash_in' is registered, so its Area draws it"):
        missing_view_text(WASH_IN)


# --- The kinds that must stay reachable --------------------------------------------


def test_the_agent_accounting_is_the_one_kind_that_must_stay_reachable() -> None:
    """`docs/MODEL.md` § "Minimum displayed outputs" names the agent accounting alone."""

    assert REQUIRED_REACHABLE == ("agent_accounting",)
    assert {tag for tag, entry in REGISTERED.items() if entry.required_reachable} == {
        "agent_accounting"
    }


def test_a_build_that_does_not_register_a_required_kind_fails() -> None:
    """The check the module runs on import refuses a registry that dropped the kind."""

    without = registry(RegisteredView(CONCENTRATION_CHART, "Concentrations", _factory))

    with pytest.raises(ValueError, match="'agent_accounting' must stay reachable in every layout"):
        required_kinds(without, AGENT_ACCOUNTING)


def test_a_required_kind_whose_entry_lacks_the_flag_fails() -> None:
    unflagged = registry(RegisteredView(AGENT_ACCOUNTING, "Agent accounting", _factory))

    with pytest.raises(ValueError, match="does not carry required_reachable"):
        required_kinds(unflagged, AGENT_ACCOUNTING)


def test_a_flag_no_requirement_names_fails() -> None:
    flagged = registry(
        RegisteredView(AGENT_ACCOUNTING, "Agent accounting", _factory, required_reachable=True),
        RegisteredView(WASH_IN, "Wash-in", _factory, required_reachable=True),
    )

    with pytest.raises(ValueError, match=r"\['wash_in'\] carry required_reachable"):
        required_kinds(flagged, AGENT_ACCOUNTING)


def test_a_required_kind_named_twice_or_as_a_plain_string_fails() -> None:
    flagged = registry(
        RegisteredView(AGENT_ACCOUNTING, "Agent accounting", _factory, required_reachable=True)
    )

    with pytest.raises(ValueError, match="required to stay reachable twice"):
        required_kinds(flagged, AGENT_ACCOUNTING, AGENT_ACCOUNTING)

    with pytest.raises(TypeError, match="a required View kind is a ViewKind"):
        required_kinds(flagged, "agent_accounting")  # type: ignore[arg-type]


def test_an_entry_refuses_a_factory_that_cannot_be_called() -> None:
    with pytest.raises(TypeError, match="has a factory that cannot be called: str"):
        RegisteredView(OLD, "Old", "ConcentrationView")  # type: ignore[arg-type]


def test_an_entry_refuses_a_flag_that_is_not_a_bool() -> None:
    with pytest.raises(TypeError, match="must stay reachable is a bool, not int"):
        RegisteredView(WASH_IN, "Wash-in", _factory, required_reachable=1)  # type: ignore[arg-type]


# --- The rename offer --------------------------------------------------------------


def test_a_renamed_kind_is_offered_its_new_title() -> None:
    registered = registry(
        RegisteredView(NEW, "New view", _factory), RegisteredView(GONE, "Other", _factory)
    )
    retired = retirements(registered, RetiredTag(OLD, "0.8.1", NEW))

    assert rename_offer_text(OLD, registered, retired) == "Show 'New view'"


def test_a_removed_or_unknown_kind_is_offered_nothing() -> None:
    registered = registry(RegisteredView(NEW, "New", _factory))
    retired = retirements(registered, RetiredTag(GONE, "0.7.0"))

    assert rename_offer_text(GONE, registered, retired) is None
    assert rename_offer_text(ViewKind("from_a_later_build"), registered, retired) is None


def test_a_registered_kind_is_offered_nothing_to_rename_to() -> None:
    with pytest.raises(ValueError, match="'wash_in' is registered"):
        rename_offer_text(WASH_IN)


# --- The too-small notice ------------------------------------------------------------


def test_the_too_small_notice_names_the_view_and_both_sizes() -> None:
    """`PL-DB5G` Q3's wording, with the need first and the Area's size second."""

    assert too_small_title("Wash-in") == "Too small for Wash-in."
    assert too_small_text(PixelSize(300, 246), PixelSize(212, 97)) == (
        "It needs at least 300 by 246 px; this Area is 212 by 97. Drag a border to enlarge it, "
        "or choose a smaller View from the menu above."
    )


def test_the_too_small_notice_refuses_a_size_that_is_not_a_pixel_size() -> None:
    with pytest.raises(TypeError, match="a size on screen is a PixelSize, not tuple"):
        too_small_text((300, 246), PixelSize(212, 97))  # type: ignore[arg-type]
