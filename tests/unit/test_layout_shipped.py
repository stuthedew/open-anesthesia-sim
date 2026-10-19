"""Unit tests for `layout/shipped.py`: the Workspaces shipped under `data/workspaces/`.

`PL-KXTL` ships three Workspaces as validated, versioned JSON, read by the
reader a reader's own `workspaces.json` goes through. These hold the shipped
files to what they say they are: one Workspace each, of the current version,
naming its own file's id, written in the form the writer produces. They also
check what each arrangement shows: none holds the accounting View (project
owner, 2026-09-16), and the default gives the chart the window's full height
beside the parameter controls, the composition the pixel budget was set for
(`PL-84QX`). The refusals run against a directory of the test's own.
"""

import json
from importlib.resources import files
from pathlib import Path

import pytest

from anesthesia_sim.app.chart_time_base import saved_time_base, time_base_for_span
from anesthesia_sim.layout import shipped as shipped_module
from anesthesia_sim.layout.exceptions import ShippedWorkspaceError
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.serialization import workspace_set_to_json
from anesthesia_sim.layout.shipped import (
    SHIPPED_WORKSPACE_IDS,
    SHIPPED_WORKSPACES_PACKAGE,
    shipped_workspace,
    shipped_workspaces,
)
from anesthesia_sim.layout.store import Source, WorkspaceStore
from anesthesia_sim.layout.tree import Area, Orientation, Split, ViewKind
from anesthesia_sim.layout.workspace import (
    Origin,
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)

CHART = ViewKind("concentration_chart")
WASH_IN = ViewKind("wash_in")
PARAMETERS = ViewKind("parameter_controls")
ACCOUNTING = ViewKind("agent_accounting")
DEFAULT = ShippedWorkspaceId("default")


def shipped_text(shipped_id: ShippedWorkspaceId) -> str:
    return files(SHIPPED_WORKSPACES_PACKAGE).joinpath(f"{shipped_id}.json").read_text("utf-8")


def copy_of_the_shipped_files(directory: Path) -> Path:
    """`directory` holding a copy of every shipped file, for a test to break one of."""

    directory.mkdir()

    for shipped_id in SHIPPED_WORKSPACE_IDS:
        (directory / f"{shipped_id}.json").write_text(shipped_text(shipped_id), encoding="utf-8")

    return directory


def a_document(workspace: Workspace) -> str:
    return workspace_set_to_json(WorkspaceSet((workspace,), 0))


def test_three_workspaces_ship_in_tab_order_with_the_default_active() -> None:
    workspaces = shipped_workspaces()

    assert [str(workspace.name) for workspace in workspaces.workspaces] == [
        "Default",
        "Induction",
        "Maintenance",
    ]
    assert [workspace.origin for workspace in workspaces.workspaces] == [
        Origin.shipped(ShippedWorkspaceId("default")),
        Origin.shipped(ShippedWorkspaceId("induction")),
        Origin.shipped(ShippedWorkspaceId("maintenance")),
    ]
    assert workspaces.active == 0


@pytest.mark.parametrize("shipped_id", SHIPPED_WORKSPACE_IDS)
def test_each_shipped_file_is_exactly_what_the_writer_writes_at_this_version(
    shipped_id: ShippedWorkspaceId,
) -> None:
    text = shipped_text(shipped_id)
    workspace = shipped_workspace(shipped_id)

    assert json.loads(text)["schema_version"] == LAYOUT_SCHEMA_VERSION
    assert a_document(workspace) == text


@pytest.mark.parametrize("shipped_id", SHIPPED_WORKSPACE_IDS)
def test_no_shipped_workspace_holds_the_accounting_view(shipped_id: ShippedWorkspaceId) -> None:
    kinds = {area.view for area in shipped_workspace(shipped_id).layout.areas()}

    assert ACCOUNTING not in kinds
    assert CHART in kinds
    assert PARAMETERS in kinds


def test_the_default_gives_the_chart_the_full_height_beside_the_parameter_controls() -> None:
    tree = shipped_workspace(DEFAULT).layout.windows[0].tree

    assert isinstance(tree, Split)
    assert tree.orientation is Orientation.ROW
    assert [child.view for child in tree.children if isinstance(child, Area)] == [CHART, PARAMETERS]


def test_induction_and_maintenance_show_the_wash_in_chart() -> None:
    for shipped_id in (ShippedWorkspaceId("induction"), ShippedWorkspaceId("maintenance")):
        kinds = [area.view for area in shipped_workspace(shipped_id).layout.areas()]

        assert kinds == [CHART, WASH_IN, PARAMETERS]


def test_induction_opens_its_concentration_chart_on_the_15_minute_window() -> None:
    """The induction chart's zoom is its own saved window, the 15-minute time base (`PL-L59K`).

    The 15-minute window follows the run. So the first 15 minutes fill the
    chart, and the current values stay on it afterwards.
    `tests/integration/test_view_contract.py` builds the chart from this state.
    """

    induction = shipped_workspace(ShippedWorkspaceId("induction"))
    chart_area = next(area.id for area in induction.layout.areas() if area.view == CHART)

    assert dict(induction.view_state) == {
        chart_area: {CHART: {"state_version": 2, "time_base_s": 900.0}}
    }
    assert saved_time_base(induction.view_state[chart_area][CHART]["time_base_s"]) == (
        time_base_for_span(15 * 60.0)
    )


def test_only_induction_ships_a_saved_view_state() -> None:
    for shipped_id in SHIPPED_WORKSPACE_IDS:
        if shipped_id != ShippedWorkspaceId("induction"):
            assert dict(shipped_workspace(shipped_id).view_state) == {}, shipped_id


def test_a_first_run_shows_the_shipped_set_and_it_survives_a_save_and_a_reload(
    tmp_path: Path,
) -> None:
    shipped = shipped_workspaces()
    store = WorkspaceStore(tmp_path)

    first = store.load(shipped)
    store.save(first.workspaces)
    reloaded = WorkspaceStore(tmp_path).load(shipped)

    assert first.source is Source.SHIPPED
    assert reloaded.source is Source.FILE
    assert reloaded.workspaces == shipped


def test_resetting_an_edited_shipped_workspace_restores_its_file() -> None:
    shipped = shipped_workspaces()
    edited = shipped.replace(
        0,
        shipped.current.with_layout(LayoutModel.single_area(CHART)).renamed(WorkspaceName("Mine")),
    )

    reset = edited.replace(0, shipped_workspace(DEFAULT))

    assert reset == shipped


def test_an_id_nothing_ships_is_refused() -> None:
    with pytest.raises(ShippedWorkspaceError, match=r"no Workspace is shipped as 'surgery'"):
        shipped_workspace(ShippedWorkspaceId("surgery"))


def test_an_id_that_is_not_a_shipped_workspace_id_is_a_type_error() -> None:
    with pytest.raises(TypeError, match="ShippedWorkspaceId, not str"):
        shipped_workspace("default")  # type: ignore[arg-type]


def test_a_file_whose_workspace_names_another_id_is_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    induction = shipped_workspace(ShippedWorkspaceId("induction"))
    (directory / "default.json").write_text(a_document(induction), encoding="utf-8")

    with pytest.raises(
        ShippedWorkspaceError,
        match=r"default\.json holds a Workspace whose origin is 'shipped:induction'.*"
        r"'shipped:default'",
    ):
        shipped_workspace(DEFAULT, directory)


def test_a_file_holding_the_readers_own_workspace_is_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    (directory / "default.json").write_text(
        a_document(shipped_workspace(DEFAULT).as_mine()), encoding="utf-8"
    )

    with pytest.raises(ShippedWorkspaceError, match=r"origin is 'mine'"):
        shipped_workspace(DEFAULT, directory)


def test_a_file_holding_two_workspaces_is_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    default = shipped_workspace(DEFAULT)
    two = WorkspaceSet((default, default.renamed(WorkspaceName("Second"))), 0)
    (directory / "default.json").write_text(workspace_set_to_json(two), encoding="utf-8")

    with pytest.raises(ShippedWorkspaceError, match=r"default\.json holds one Workspace, not 2"):
        shipped_workspace(DEFAULT, directory)


def test_a_file_that_does_not_read_is_refused_naming_the_file_and_the_place(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    document = json.loads(shipped_text(DEFAULT))
    document["workspaces"][0]["layout"]["windows"][0]["tree"]["sizes"] = [0.75, 0.75]
    (directory / "default.json").write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(
        ShippedWorkspaceError, match=r"default\.json is not a Workspace set document: .*sum to one"
    ):
        shipped_workspace(DEFAULT, directory)


def test_a_missing_file_is_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    (directory / "maintenance.json").unlink()

    with pytest.raises(ShippedWorkspaceError, match=r"maintenance\.json could not be read"):
        shipped_workspaces(directory)


def test_a_file_at_another_schema_version_is_refused_rather_than_migrated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    monkeypatch.setattr(shipped_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1)

    with pytest.raises(
        ShippedWorkspaceError,
        match=rf"default\.json is written at schema version {LAYOUT_SCHEMA_VERSION}, "
        r".*never migrated",
    ):
        shipped_workspace(DEFAULT, directory)


def test_a_json_file_no_id_names_is_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    (directory / "surgery.json").write_text(shipped_text(DEFAULT), encoding="utf-8")

    with pytest.raises(ShippedWorkspaceError, match=r"surgery\.json .* is named by no shipped"):
        shipped_workspaces(directory)


def test_two_shipped_workspaces_of_one_name_are_refused(tmp_path: Path) -> None:
    directory = copy_of_the_shipped_files(tmp_path / "shipped")
    induction = shipped_workspace(ShippedWorkspaceId("induction"))
    (directory / "induction.json").write_text(
        a_document(induction.renamed(WorkspaceName("Default"))), encoding="utf-8"
    )

    with pytest.raises(ShippedWorkspaceError, match=r"do not form a set: two Workspaces"):
        shipped_workspaces(directory)
