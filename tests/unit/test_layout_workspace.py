"""Unit tests for `layout/workspace.py`: a Workspace, and the set of them.

`PL-WV9K` decided both (project owner, 2026-09-27, ratified): what a
Workspace carries beside its layout, and how the set behaves - ordered, one
active, never empty, names unique - with `ROADMAP.md` item 34's floor, that the
last Workspace cannot be removed, raised by the type rather than by a dialog.
These hold each refusal to a message that says which invariant it was, and
each operation to returning a new value and leaving the old one as it was.
"""

import math

import pytest

from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LastWorkspace,
    LayoutRefused,
    NotInLayout,
    NotInWorkspaceSet,
)
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import AreaId, Orientation, ViewKind
from anesthesia_sim.layout.workspace import (
    Origin,
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)

CHART = ViewKind("concentration_chart")
ACCOUNTING = ViewKind("agent_accounting")
ONE = AreaId(1)
TWO = AreaId(2)


def two_areas() -> LayoutModel:
    """One window, Area 1 showing the chart beside Area 2 showing the accounting."""

    layout, second = LayoutModel.single_area(CHART).split(ONE, Orientation.ROW, 0.5)

    return layout.set_view(second, ACCOUNTING)


def workspace(name: str, layout: LayoutModel | None = None) -> Workspace:
    return Workspace(WorkspaceName(name), Origin.mine(), layout or two_areas())


def a_set(*names: str, active: int = 0) -> WorkspaceSet:
    return WorkspaceSet(tuple(workspace(name) for name in names), active)


def names(workspaces: WorkspaceSet) -> list[str]:
    return [str(each.name) for each in workspaces.workspaces]


class TestWorkspaceName:
    def test_a_name_is_the_string_it_was_built_from(self) -> None:
        assert WorkspaceName("Induction") == "Induction"

    @pytest.mark.parametrize(
        ("name", "said"),
        [
            ("", "not empty"),
            (" Induction", "no leading or trailing whitespace"),
            ("Induction\n", "no leading or trailing whitespace"),
            ("Induc\ntion", "printing characters only"),
        ],
    )
    def test_a_name_a_tab_could_not_show_is_refused(self, name: str, said: str) -> None:
        with pytest.raises(InvalidLayout, match=said):
            WorkspaceName(name)

    def test_a_name_is_a_str(self) -> None:
        with pytest.raises(TypeError, match="not int"):
            WorkspaceName(1)  # type: ignore[arg-type]


class TestOrigin:
    def test_a_shipped_id_has_a_tag_syntax(self) -> None:
        assert ShippedWorkspaceId("big_picture_2") == "big_picture_2"

        with pytest.raises(InvalidLayout, match="not 'Default'"):
            ShippedWorkspaceId("Default")

        with pytest.raises(TypeError, match="not NoneType"):
            ShippedWorkspaceId(None)  # type: ignore[arg-type]

    def test_the_written_forms_round_trip(self) -> None:
        shipped = Origin.shipped(ShippedWorkspaceId("induction"))

        assert Origin.mine().written() == "mine"
        assert shipped.written() == "shipped:induction"
        assert Origin.from_written("mine") == Origin.mine()
        assert Origin.from_written("shipped:induction") == shipped
        assert shipped.is_shipped and not Origin.mine().is_shipped

    def test_another_written_form_is_refused(self) -> None:
        with pytest.raises(InvalidLayout, match="not 'theirs'"):
            Origin.from_written("theirs")

        with pytest.raises(InvalidLayout, match="not 'Default'"):
            Origin.from_written("shipped:Default")

        with pytest.raises(TypeError, match="an origin's shipped_id is a ShippedWorkspaceId"):
            Origin("default")  # type: ignore[arg-type]


class TestWorkspace:
    def test_each_field_is_of_its_type(self) -> None:
        with pytest.raises(TypeError, match="name is a WorkspaceName, not str"):
            Workspace("Default", Origin.mine(), two_areas())  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="origin is an Origin, not str"):
            Workspace(WorkspaceName("Default"), "mine", two_areas())  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="layout is a LayoutModel, not NoneType"):
            Workspace(WorkspaceName("Default"), Origin.mine(), None)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="view_state is a mapping, not list"):
            Workspace(WorkspaceName("Default"), Origin.mine(), two_areas(), [])  # type: ignore[arg-type]

    def test_view_state_names_areas_the_layout_holds_by_area_id(self) -> None:
        with pytest.raises(TypeError, match="keyed by AreaId, not int"):
            Workspace(WorkspaceName("Default"), Origin.mine(), two_areas(), {1: {}})  # type: ignore[dict-item]

        with pytest.raises(InvalidLayout, match="names Area 9, which the layout does not hold"):
            Workspace(WorkspaceName("Default"), Origin.mine(), two_areas(), {AreaId(9): {}})

        with pytest.raises(TypeError, match="keyed by ViewKind, not str"):
            Workspace(
                WorkspaceName("Default"),
                Origin.mine(),
                two_areas(),
                {ONE: {"concentration_chart": {}}},  # type: ignore[dict-item]
            )

    def test_a_view_state_is_a_json_object_the_workspace_never_reads(self) -> None:
        with pytest.raises(TypeError, match="is a mapping, not list"):
            Workspace(WorkspaceName("D"), Origin.mine(), two_areas(), {ONE: {CHART: []}})  # type: ignore[dict-item]

        with pytest.raises(TypeError, match="keyed by str at every depth, not int"):
            Workspace(WorkspaceName("D"), Origin.mine(), two_areas(), {ONE: {CHART: {1: 2}}})  # type: ignore[dict-item]

        with pytest.raises(TypeError, match="keyed by str at every depth, not bool"):
            Workspace(
                WorkspaceName("D"),
                Origin.mine(),
                two_areas(),
                {ONE: {CHART: {"a": [{"b": {True: 1}}]}}},
            )

        with pytest.raises(InvalidLayout, match="not JSON a file can hold"):
            Workspace(WorkspaceName("D"), Origin.mine(), two_areas(), {ONE: {CHART: {"a": {1}}}})

        with pytest.raises(InvalidLayout, match="not JSON a file can hold"):
            Workspace(
                WorkspaceName("D"), Origin.mine(), two_areas(), {ONE: {CHART: {"a": math.nan}}}
            )

    def test_the_state_is_held_as_a_private_copy_and_handed_out_as_one(self) -> None:
        handed: dict[str, object] = {"zoom": [0.0, 15.0], "series": ("vrg", "muscle")}
        kept = Workspace(WorkspaceName("D"), Origin.mine(), two_areas(), {ONE: {CHART: handed}})
        handed["zoom"] = [0.0, 60.0]

        copy = kept.state_of(ONE, CHART)

        assert copy == {"zoom": [0.0, 15.0], "series": ["vrg", "muscle"]}

        assert copy is not None
        series = copy["series"]
        assert isinstance(series, list)
        copy["zoom"] = []
        series.append("fat")

        assert kept.state_of(ONE, CHART) == {"zoom": [0.0, 15.0], "series": ["vrg", "muscle"]}

        with pytest.raises(TypeError):
            kept.view_state[TWO] = {}  # type: ignore[index]

        with pytest.raises(TypeError):
            kept.view_state[ONE][CHART] = {}  # type: ignore[index]

    def test_one_entry_is_kept_per_kind_per_area(self) -> None:
        start = workspace("Default")
        chart = start.with_view_state(ONE, CHART, {"zoom": 15})
        both = chart.with_view_state(ONE, ACCOUNTING, {"rows": "all"})
        replaced = both.with_view_state(ONE, CHART, {"zoom": 60})

        assert start.state_of(ONE, CHART) is None
        assert chart.state_of(ONE, CHART) == {"zoom": 15}
        assert both.state_of(ONE, ACCOUNTING) == {"rows": "all"}
        assert replaced.state_of(ONE, CHART) == {"zoom": 60}
        assert replaced.state_of(ONE, ACCOUNTING) == {"rows": "all"}
        assert start.view_state == {}

    def test_state_for_an_area_the_layout_does_not_hold_is_refused(self) -> None:
        with pytest.raises(NotInLayout):
            workspace("Default").with_view_state(AreaId(9), CHART, {})

    def test_a_new_layout_keeps_the_state_of_the_areas_it_still_holds(self) -> None:
        start = (
            workspace("Default")
            .with_view_state(ONE, CHART, {"zoom": 15})
            .with_view_state(TWO, ACCOUNTING, {"rows": "all"})
        )

        joined = start.with_layout(start.layout.join(ONE, TWO))

        assert [area.id for area in joined.layout.areas()] == [ONE]
        assert joined.state_of(ONE, CHART) == {"zoom": 15}
        assert TWO not in joined.view_state
        assert start.state_of(TWO, ACCOUNTING) == {"rows": "all"}

        with pytest.raises(TypeError, match="layout is a LayoutModel, not str"):
            start.with_layout("layout")  # type: ignore[arg-type]

    def test_renamed_and_as_mine_change_one_field(self) -> None:
        shipped = Workspace(
            WorkspaceName("Default"), Origin.shipped(ShippedWorkspaceId("default")), two_areas()
        )

        assert shipped.renamed(WorkspaceName("Mine")).name == "Mine"
        assert shipped.renamed(WorkspaceName("Mine")).origin == shipped.origin
        assert shipped.as_mine().origin == Origin.mine()
        assert shipped.as_mine().name == "Default"


class TestWorkspaceSetInvariants:
    def test_the_set_holds_at_least_one_workspace(self) -> None:
        with pytest.raises(InvalidLayout, match="at least one Workspace"):
            WorkspaceSet((), 0)

    def test_names_are_unique(self) -> None:
        with pytest.raises(InvalidLayout, match="two Workspaces are named 'Default'"):
            a_set("Default", "Induction", "Default")

    def test_the_active_position_is_in_the_set(self) -> None:
        with pytest.raises(
            InvalidLayout, match="active position is 2, and this set's positions run from 0 to 1"
        ):
            a_set("Default", "Induction", active=2)

        with pytest.raises(InvalidLayout, match="active position is -1"):
            a_set("Default", active=-1)

        with pytest.raises(TypeError, match="active position is an int, not bool"):
            a_set("Default", active=True)

    def test_each_field_is_of_its_type(self) -> None:
        with pytest.raises(TypeError, match="workspaces are a tuple, not list"):
            WorkspaceSet([workspace("Default")], 0)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="holds Workspaces, not str"):
            WorkspaceSet(("Default",), 0)  # type: ignore[arg-type]

    def test_current_is_the_active_workspace(self) -> None:
        assert a_set("Default", "Induction", active=1).current.name == "Induction"

    def test_position_of_finds_a_name(self) -> None:
        workspaces = a_set("Default", "Induction")

        assert workspaces.position_of(WorkspaceName("Induction")) == 1

        with pytest.raises(NotInWorkspaceSet, match="no Workspace in the set is named 'Other'"):
            workspaces.position_of(WorkspaceName("Other"))


class TestWorkspaceSetOperations:
    def test_add_appends_and_activates(self) -> None:
        start = a_set("Default")
        added = start.add(workspace("Induction"))

        assert names(added) == ["Default", "Induction"]
        assert added.active == 1
        assert names(start) == ["Default"]

    def test_add_at_a_position_inserts_there_up_to_one_past_the_end(self) -> None:
        start = a_set("Default", "Maintenance")

        assert names(start.add(workspace("Induction"), at=1)) == [
            "Default",
            "Induction",
            "Maintenance",
        ]
        assert names(start.add(workspace("Induction"), at=2)) == [
            "Default",
            "Maintenance",
            "Induction",
        ]

        with pytest.raises(NotInWorkspaceSet, match="no position 3: its positions run from 0 to 2"):
            start.add(workspace("Induction"), at=3)

    def test_add_refuses_a_taken_name(self) -> None:
        with pytest.raises(
            LayoutRefused, match="a Workspace named 'Default' is already in the set"
        ):
            a_set("Default").add(workspace("Default"))

        with pytest.raises(TypeError, match="holds Workspaces, not str"):
            a_set("Default").add("Induction")  # type: ignore[arg-type]

    def test_duplicate_copies_after_its_source_as_the_readers_own(self) -> None:
        shipped = WorkspaceSet(
            (
                Workspace(
                    WorkspaceName("Default"),
                    Origin.shipped(ShippedWorkspaceId("default")),
                    two_areas(),
                    {ONE: {CHART: {"zoom": 15}}},
                ),
                workspace("Maintenance"),
            ),
            0,
        )

        once = shipped.duplicate(0)
        twice = once.duplicate(0)

        assert names(once) == ["Default", "Default (copy)", "Maintenance"]
        assert once.active == 1
        assert once.current.origin == Origin.mine()
        assert once.current.state_of(ONE, CHART) == {"zoom": 15}
        assert names(twice) == ["Default", "Default (copy 2)", "Default (copy)", "Maintenance"]

    def test_rename_refuses_another_workspaces_name_and_allows_its_own(self) -> None:
        start = a_set("Default", "Induction")

        assert names(start.rename(1, WorkspaceName("Wash-in"))) == ["Default", "Wash-in"]
        assert names(start.rename(1, WorkspaceName("Induction"))) == ["Default", "Induction"]

        with pytest.raises(
            LayoutRefused, match="a Workspace named 'Default' is already in the set"
        ):
            start.rename(1, WorkspaceName("Default"))

        with pytest.raises(TypeError, match="name is a WorkspaceName, not str"):
            start.rename(1, "Wash-in")  # type: ignore[arg-type]

    def test_move_reorders_and_the_active_workspace_stays_active(self) -> None:
        start = a_set("Default", "Induction", "Maintenance", active=1)
        moved = start.move(2, 0)

        assert names(moved) == ["Maintenance", "Default", "Induction"]
        assert moved.current.name == "Induction"
        assert start.move(1, 1) == start

        with pytest.raises(NotInWorkspaceSet, match="no position 3"):
            start.move(0, 3)

    def test_the_last_workspace_cannot_be_removed(self) -> None:
        alone = a_set("Default")

        with pytest.raises(
            LastWorkspace, match="holds one Workspace, 'Default', and a reader always has one"
        ):
            alone.remove(0)

        assert names(alone) == ["Default"]

    def test_remove_keeps_the_active_workspace_or_hands_it_to_its_successor(self) -> None:
        start = a_set("Default", "Induction", "Maintenance", active=1)

        before = start.remove(0)
        itself = start.remove(1)
        after = start.remove(2)
        last = a_set("Default", "Induction", active=1).remove(1)

        assert (names(before), before.current.name) == (["Induction", "Maintenance"], "Induction")
        assert (names(itself), itself.current.name) == (["Default", "Maintenance"], "Maintenance")
        assert (names(after), after.current.name) == (["Default", "Induction"], "Induction")
        assert (names(last), last.current.name) == (["Default"], "Default")

    def test_activate_and_replace(self) -> None:
        start = a_set("Default", "Induction")
        activated = start.activate(1)
        edited = start.replace(0, workspace("Default").with_view_state(ONE, CHART, {"zoom": 60}))
        renamed = start.replace(0, workspace("Big picture"))

        assert activated.current.name == "Induction"
        assert edited.workspaces[0].state_of(ONE, CHART) == {"zoom": 60}
        assert edited.active == 0
        assert names(renamed) == ["Big picture", "Induction"]

        with pytest.raises(
            LayoutRefused, match="a Workspace named 'Induction' is already in the set"
        ):
            start.replace(0, workspace("Induction"))

        with pytest.raises(TypeError, match="holds Workspaces, not NoneType"):
            start.replace(0, None)  # type: ignore[arg-type]

    @pytest.mark.parametrize("index", [-1, 2, True])
    def test_a_position_the_set_does_not_hold_is_refused(self, index: int) -> None:
        start = a_set("Default", "Induction")
        expected = TypeError if isinstance(index, bool) else NotInWorkspaceSet

        for operation in (start.duplicate, start.remove, start.activate):
            with pytest.raises(expected):
                operation(index)


class TestWorkspaceSetMutationsFound:
    """Cases the first adversarial review's surviving mutations named (2026-10-17)."""

    def test_move_to_a_later_position_lands_there(self) -> None:
        start = a_set("Default", "Induction", "Maintenance")

        assert names(start.move(0, 1)) == ["Induction", "Default", "Maintenance"]
        assert names(start.move(0, 2)) == ["Induction", "Maintenance", "Default"]

    def test_the_third_duplicate_counts_on(self) -> None:
        thrice = a_set("Default").duplicate(0).duplicate(0).duplicate(0)

        assert names(thrice) == [
            "Default",
            "Default (copy 3)",
            "Default (copy 2)",
            "Default (copy)",
        ]

    def test_editing_another_workspace_leaves_the_active_one_active(self) -> None:
        start = a_set("Default", "Induction", active=0)

        assert start.rename(1, WorkspaceName("Wash-in")).active == 0
        assert start.replace(1, workspace("Wash-in")).active == 0

    def test_a_written_origin_is_matched_whole(self) -> None:
        with pytest.raises(InvalidLayout, match="not 'x shipped:default'"):
            Origin.from_written("x shipped:default")

        with pytest.raises(InvalidLayout, match="not 'default-x'"):
            ShippedWorkspaceId("default-x")

    def test_a_name_looked_up_is_a_workspace_name(self) -> None:
        with pytest.raises(TypeError, match="name is a WorkspaceName, not str"):
            a_set("Default").position_of("Default")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="name is a WorkspaceName, not str"):
            workspace("Default").renamed("Other")  # type: ignore[arg-type]
