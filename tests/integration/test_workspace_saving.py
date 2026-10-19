"""Tests of saving, restoring and resetting Workspaces, run headless.

`PL-DWHG` wires `layout/store.py` into the application. `app/main.py` loads
the reader's Workspaces at launch through `open_workspaces`, and the Layout
menu offers "Save as default", "Restore shipped Workspaces" and "Reset all
layouts", as `PL-WV9K` § "Answers 2026-09-27" decided. Every test that has a
store gives it a directory under `tmp_path`, so nothing is written outside
it. The expected sets are built here from the shipped set and the set
operations, never read back from the strip under test. The keyboard path to
each entry is in `tests/integration/test_layout_keyboard.py`.
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.area_layout import SPLIT_SIDE_BY_SIDE_LABEL
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.main import open_workspaces
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.workspace_tabs import (
    RESET_ALL_LABEL,
    RESTORE_SHIPPED_LABEL,
    SAVE_AS_DEFAULT_LABEL,
    WorkspaceTabs,
    default_operations,
    restore_shipped,
    save_entry,
)
from anesthesia_sim.layout.exceptions import LayoutRefused, ShippedWorkspaceError
from anesthesia_sim.layout.serialization import workspace_set_to_json
from anesthesia_sim.layout.shipped import shipped_workspace, shipped_workspaces
from anesthesia_sim.layout.store import (
    USER_DIRECTORY_VARIABLE,
    WORKSPACES_FILE_NAME,
    Source,
    WorkspaceStore,
)
from anesthesia_sim.layout.workspace import ShippedWorkspaceId, WorkspaceName, WorkspaceSet


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _names(workspaces: WorkspaceSet) -> list[str]:
    return [workspace.name for workspace in workspaces.workspaces]


def _strip(
    workspaces: WorkspaceSet, store: WorkspaceStore | None = None, notice: str | None = None
) -> tuple[WorkspaceTabs, list[WorkspaceSet]]:
    """A strip over `workspaces` whose owner applies each change, and the changes it made."""

    made: list[WorkspaceSet] = []

    def change(workspaces: WorkspaceSet) -> None:
        made.append(workspaces)
        strip.show_set(workspaces)

    strip = WorkspaceTabs(workspaces, change, lambda: (), store=store, notice=notice)
    strip.resize(900, 80)
    strip.show()

    return strip, made


def _menu_entry(strip: WorkspaceTabs, label: str) -> tuple[bool, str]:
    """Whether the Layout menu's entry `label` is enabled, and its tooltip."""

    strip.layout_menu.fill()
    action = next(a for a in strip.layout_menu.menu().actions() if a.text() == label)

    return action.isEnabled(), action.toolTip()


def test_a_first_launch_opens_the_shipped_set_and_writes_nothing(tmp_path: Path) -> None:
    launch = open_workspaces(str(tmp_path / "data"), {})

    assert launch.workspaces == shipped_workspaces()
    assert launch.store is not None
    assert launch.store.directory == tmp_path / "data"
    assert launch.notice is None
    assert list(tmp_path.iterdir()) == []


def test_the_override_names_the_directory_the_launch_reads(tmp_path: Path) -> None:
    saved = shipped_workspaces().duplicate(1)
    (tmp_path / WORKSPACES_FILE_NAME).write_text(workspace_set_to_json(saved), encoding="utf-8")

    launch = open_workspaces("", {USER_DIRECTORY_VARIABLE: str(tmp_path)})

    assert launch.workspaces == saved
    assert launch.notice is None


def test_no_directory_opens_the_shipped_set_with_no_store_and_says_why(
    application: QApplication,
) -> None:
    launch = open_workspaces("", {})

    assert launch.workspaces == shipped_workspaces()
    assert launch.store is None
    assert launch.notice is not None
    assert USER_DIRECTORY_VARIABLE in launch.notice
    assert "nothing will be saved" in launch.notice

    strip, _made = _strip(launch.workspaces, launch.store, launch.notice)
    enabled, tooltip = _menu_entry(strip, SAVE_AS_DEFAULT_LABEL)
    assert not enabled
    assert USER_DIRECTORY_VARIABLE in tooltip
    assert strip.notice_label.isVisible()
    assert USER_DIRECTORY_VARIABLE in strip.notice_label.text()
    strip.close()


def test_without_a_store_save_is_shown_unavailable(application: QApplication) -> None:
    """A dashboard a test builds has no store, so it can never write a file."""

    strip, _made = _strip(shipped_workspaces())

    enabled, tooltip = _menu_entry(strip, SAVE_AS_DEFAULT_LABEL)

    assert not enabled
    assert tooltip == "Not available: this session has no folder to save Workspaces in."
    assert not strip.notice_label.isVisible()
    strip.close()


def test_save_writes_the_whole_set_and_the_next_launch_opens_on_it(
    application: QApplication, tmp_path: Path
) -> None:
    store = WorkspaceStore(tmp_path)
    loaded = store.load(shipped_workspaces())
    edited = loaded.workspaces.duplicate(0).rename(1, WorkspaceName("Mine")).activate(3)
    strip, _made = _strip(edited, store)

    entry = strip.save_entry()
    assert entry.question is not None
    assert entry.question.text == (
        "Save these 4 Workspaces as the default that opens at each launch? They are saved in "
        f"{tmp_path / WORKSPACES_FILE_NAME}."
    )
    assert entry.question.keep_label == "Cancel"
    strip.save_as_default(entry)
    question = strip.question
    assert question is not None
    question.keep_button.click()
    assert list(tmp_path.iterdir()) == []

    strip.save_as_default(strip.save_entry())
    question = strip.question
    assert question is not None
    question.proceed_button.click()

    assert strip.notice_label.isVisible()
    assert strip.notice_label.text() == (
        f"Saved 4 Workspaces as the default, in {tmp_path / WORKSPACES_FILE_NAME}."
    )
    launch = open_workspaces(str(tmp_path), {})
    assert launch.workspaces == edited
    assert _names(launch.workspaces) == ["Default", "Mine", "Induction", "Maintenance"]
    assert launch.workspaces.current.name == "Maintenance"
    assert launch.notice is None

    replacing = save_entry(launch.store, launch.workspaces)
    assert replacing.question is not None
    assert "They replace the default saved in" in replacing.question.text
    strip.close()


def test_save_is_unavailable_with_the_stores_reason_in_a_read_only_session(
    application: QApplication, tmp_path: Path
) -> None:
    """A file a newer build wrote turns saving off, and the file is left as it was."""

    document = json.loads(workspace_set_to_json(shipped_workspaces()))
    document["schema_version"] = 999
    written = json.dumps(document)
    (tmp_path / WORKSPACES_FILE_NAME).write_text(written, encoding="utf-8")
    store = WorkspaceStore(tmp_path)
    loaded = store.load(shipped_workspaces())
    assert not loaded.writable
    assert loaded.notice is not None

    strip, _made = _strip(loaded.workspaces, store, loaded.notice)
    enabled, tooltip = _menu_entry(strip, SAVE_AS_DEFAULT_LABEL)

    assert not enabled
    assert "schema version 999 by a newer build" in tooltip
    assert strip.notice_label.isVisible()
    assert "schema version 999 by a newer build" in strip.notice_label.text()
    strip.save_as_default(strip.save_entry())
    assert strip.question is None
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == written
    strip.close()


def test_a_save_the_operating_system_refuses_is_reported_under_the_tabs(
    application: QApplication, tmp_path: Path
) -> None:
    """The directory cannot be made, so the save names the path and the session goes on."""

    (tmp_path / "blocker").write_text("not a directory", encoding="utf-8")
    store = WorkspaceStore(tmp_path / "blocker" / "data")
    loaded = store.load(shipped_workspaces())
    assert loaded.writable
    strip, _made = _strip(loaded.workspaces, store)

    strip.save_as_default(strip.save_entry())
    question = strip.question
    assert question is not None
    question.accept()

    text = strip.notice_label.text()
    assert text.startswith("The Workspaces were not saved: could not create the directory")
    assert str(tmp_path / "blocker" / "data") in text
    assert strip.notice_label.isVisible()
    strip.dismiss_notice()
    assert not strip.notice_label.isVisible()
    assert not strip.dismiss_button.isVisible()
    strip.close()


def test_restore_puts_back_each_deleted_shipped_workspace_in_the_shipped_order() -> None:
    """Default and Maintenance deleted around Induction, and the reader's own tab kept current."""

    shipped = shipped_workspaces()
    mine = shipped.duplicate(1).rename(2, WorkspaceName("Mine"))
    assert _names(mine) == ["Default", "Induction", "Mine", "Maintenance"]
    deleted = mine.remove(3).remove(0)
    deleted = deleted.activate(deleted.position_of(WorkspaceName("Mine")))
    assert _names(deleted) == ["Induction", "Mine"]

    restored = restore_shipped(deleted, shipped)

    assert _names(restored) == ["Default", "Induction", "Maintenance", "Mine"]
    assert restored.current.name == "Mine"
    assert restored.workspaces[0] == shipped_workspace(ShippedWorkspaceId("default"))
    assert restored.workspaces[2] == shipped_workspace(ShippedWorkspaceId("maintenance"))
    assert restored.workspaces[1] == deleted.workspaces[0]
    assert restored.workspaces[3] == deleted.workspaces[1]


def test_restore_keeps_a_renamed_shipped_workspace_and_puts_back_only_the_deleted() -> None:
    shipped = shipped_workspaces()
    renamed = shipped.rename(1, WorkspaceName("My induction")).remove(2)

    restored = restore_shipped(renamed, shipped)

    assert _names(restored) == ["Default", "My induction", "Maintenance"]
    assert restored.active == 0


def test_restore_with_every_shipped_workspace_deleted_puts_them_first() -> None:
    shipped = shipped_workspaces()
    only_mine = shipped.duplicate(0).remove(0).remove(1).remove(1)
    assert _names(only_mine) == ["Default (copy)"]

    restored = restore_shipped(only_mine, shipped)

    assert _names(restored) == ["Default", "Induction", "Maintenance", "Default (copy)"]
    assert restored.current.name == "Default (copy)"


def test_restore_is_unavailable_when_nothing_was_deleted_or_a_name_is_taken() -> None:
    shipped = shipped_workspaces()

    restore, _reset = default_operations(shipped.duplicate(0), lambda: shipped)
    assert restore.label == RESTORE_SHIPPED_LABEL
    assert not restore.available
    assert restore.refusal == "Not available: every shipped Workspace is already here."

    taken = shipped.duplicate(0).remove(2)
    taken = taken.rename(
        taken.position_of(WorkspaceName("Default (copy)")), WorkspaceName("Induction")
    )
    with pytest.raises(LayoutRefused, match="Induction"):
        restore_shipped(taken, shipped)
    restore, _reset = default_operations(taken, lambda: shipped)
    assert not restore.available
    assert restore.refusal is not None
    assert restore.refusal.startswith("Not available: a Workspace named 'Induction'")


def test_reset_all_asks_first_replaces_the_set_and_writes_nothing(
    application: QApplication, tmp_path: Path
) -> None:
    store = WorkspaceStore(tmp_path)
    loaded = store.load(shipped_workspaces())
    edited = loaded.workspaces.duplicate(0).remove(1)
    strip, made = _strip(edited, store)

    _restore, reset = default_operations(strip.workspaces)
    assert reset.label == RESET_ALL_LABEL
    assert reset.question is not None
    assert reset.question.text == (
        "Replace every Workspace with the shipped ones? Your own Workspaces and your changes to "
        "the shipped ones are removed. The saved default is not changed until you save again."
    )
    strip.choose(reset)
    question = strip.question
    assert question is not None
    question.keep_button.click()
    assert made == []

    strip.choose(reset)
    question = strip.question
    assert question is not None
    question.proceed_button.click()

    assert made == [shipped_workspaces()]
    assert list(tmp_path.iterdir()) == []
    strip.close()


def test_a_shipped_set_that_does_not_read_shows_both_entries_unavailable() -> None:
    def broken() -> WorkspaceSet:
        raise ShippedWorkspaceError("anesthesia_sim.data.workspaces/default.json could not be read")

    restore, reset = default_operations(shipped_workspaces(), broken)

    for entry in (restore, reset):
        assert not entry.available
        assert entry.refusal == (
            "Not available: anesthesia_sim.data.workspaces/default.json could not be read"
        )


def test_the_dashboard_saves_what_the_areas_draw(application: QApplication, tmp_path: Path) -> None:
    """A dragged layout reaches the file, since the strip saves the dashboard's live set."""

    store = WorkspaceStore(tmp_path)
    loaded = store.load(shipped_workspaces())
    view = SimulationView((SimulationController(),), workspaces=loaded.workspaces, store=store)
    view.resize(1400, 1000)
    view.show()
    view.present(False)

    try:
        first = view.layout_container.model.areas()[0].id
        before = len(view.layout_container.model.areas())
        split = next(
            operation
            for operation in view.layout_container.operations(first)
            if operation.label == SPLIT_SIDE_BY_SIDE_LABEL
        )
        assert split.available
        view.layout_container.perform(split)
        expected = view.workspaces
        assert len(expected.current.layout.areas()) == before + 1

        strip = view.tab_strip
        strip.save_as_default(strip.save_entry())
        question = strip.question
        assert question is not None
        question.accept()

        reloaded = WorkspaceStore(tmp_path).load(shipped_workspaces())
        assert reloaded.source is Source.FILE
        assert reloaded.workspaces == expected
        assert len(reloaded.workspaces.current.layout.areas()) == before + 1
    finally:
        view.stop_timers()
        view.close()
        view.deleteLater()
        application.processEvents()
