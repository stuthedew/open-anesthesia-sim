"""Unit tests for `layout/store.py`: the file a reader's Workspaces are saved to.

`PL-SSQW` (project owner, 2026-09-27, ratified) decided how the file behaves.
It decided where the file lives, and that the file is written atomically and
only when the reader asks. It decided that a first run leaves no trace. It
also decided what a launch does with a file that an older build wrote, a file
that a newer build wrote, and a file that is invalid at a version this build
reads. Every case runs against `tmp_path` with no `QApplication`. Each case
checks that the store reports what it did. The store gives a notice where
something happened and none where nothing did. It turns saving off exactly
where a save would touch a newer build's file.
"""

import json
import os
import shutil
import stat
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Self

import pytest

from anesthesia_sim.layout import serialization as serialization_module
from anesthesia_sim.layout import store as store_module
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LayoutFormatError,
    LayoutRefused,
    WorkspaceFileError,
)
from anesthesia_sim.layout.migrations import LAYOUT_SCHEMA_VERSION, Migrated, SchemaVersion
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.serialization import workspace_set_from_json, workspace_set_to_json
from anesthesia_sim.layout.store import (
    PENDING_FILE_NAME,
    PREVIOUS_FILE_NAME,
    USER_DIRECTORY_VARIABLE,
    WORKSPACES_FILE_NAME,
    Source,
    WorkspaceStore,
    kept_file_name,
    set_aside_file_name,
    user_data_directory,
)
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
MOMENT = datetime(2026, 10, 17, 5, 0, 0, tzinfo=UTC)
STAMP = "20261017T050000Z"

SHIPPED = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Default"),
            Origin.shipped(ShippedWorkspaceId("default")),
            LayoutModel.single_area(CHART),
        ),
    ),
    0,
)

MINE = WorkspaceSet(
    (
        SHIPPED.workspaces[0],
        Workspace(
            WorkspaceName("Induction"),
            Origin.mine(),
            LayoutModel.single_area(CHART)
            .split(AreaId(1), Orientation.ROW, 0.5)[0]
            .set_view(AreaId(2), ACCOUNTING),
            {AreaId(1): {CHART: {"zoom_s": [0.0, 900.0]}}},
        ),
    ),
    1,
)

LATER = MINE.rename(1, WorkspaceName("Wash-in"))


def a_store(directory: Path) -> WorkspaceStore:
    return WorkspaceStore(directory, clock=lambda: MOMENT)


def saved(directory: Path, workspaces: WorkspaceSet) -> WorkspaceStore:
    """Return a store whose directory already holds `workspaces` as the reader's default."""

    store = a_store(directory)
    store.load(SHIPPED)
    store.save(workspaces)

    return store


def entries(directory: Path) -> list[str]:
    return sorted(path.name for path in directory.iterdir()) if directory.exists() else []


def test_a_first_run_shows_the_shipped_set_and_writes_nothing(tmp_path: Path) -> None:
    directory = tmp_path / "state"

    loaded = a_store(directory).load(SHIPPED)

    assert loaded.workspaces == SHIPPED
    assert loaded.source is Source.SHIPPED
    assert loaded.writable
    assert loaded.notice is None
    assert loaded.set_aside is None
    assert loaded.written_at is None
    assert not directory.exists()


def test_save_writes_the_file_atomically_and_keeps_one_previous_generation(tmp_path: Path) -> None:
    directory = tmp_path / "state"
    store = a_store(directory)
    store.load(SHIPPED)

    path = store.save(MINE)

    assert path == directory / WORKSPACES_FILE_NAME
    assert entries(directory) == [WORKSPACES_FILE_NAME]
    assert workspace_set_from_json(path.read_text(encoding="utf-8")).workspaces == MINE

    store.save(LATER)

    assert entries(directory) == [WORKSPACES_FILE_NAME, PREVIOUS_FILE_NAME]
    assert (directory / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )
    assert path.read_text(encoding="utf-8") == workspace_set_to_json(LATER)

    reloaded = a_store(directory).load(SHIPPED)

    assert reloaded.workspaces == LATER
    assert reloaded.source is Source.FILE
    assert reloaded.notice is None
    assert reloaded.written_at == LAYOUT_SCHEMA_VERSION


def test_save_before_load_is_refused(tmp_path: Path) -> None:
    with pytest.raises(LayoutRefused, match="nothing has been loaded"):
        a_store(tmp_path).save(MINE)

    with pytest.raises(TypeError, match="not list"):
        a_store(tmp_path).save([])  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="not str"):
        WorkspaceStore("state")  # type: ignore[arg-type]


def test_a_newer_file_is_left_untouched_and_the_session_saves_nothing(tmp_path: Path) -> None:
    path = tmp_path / WORKSPACES_FILE_NAME
    newer = json.dumps(
        {"schema_version": LAYOUT_SCHEMA_VERSION + 1, "anything": ["a newer build's"]}
    )
    path.write_text(newer, encoding="utf-8")
    store = a_store(tmp_path)

    loaded = store.load(SHIPPED)

    assert loaded.workspaces == SHIPPED
    assert loaded.source is Source.SHIPPED
    assert not loaded.writable
    assert loaded.notice is not None
    assert str(path) in loaded.notice
    assert f"schema version {LAYOUT_SCHEMA_VERSION + 1}" in loaded.notice
    assert f"versions up to {LAYOUT_SCHEMA_VERSION}" in loaded.notice

    with pytest.raises(LayoutRefused, match="saving is off for this session"):
        store.save(MINE)

    assert path.read_text(encoding="utf-8") == newer
    assert entries(tmp_path) == [WORKSPACES_FILE_NAME]


def test_an_invalid_file_is_set_aside_and_the_previous_generation_is_rescued(
    tmp_path: Path,
) -> None:
    saved(tmp_path, MINE).save(LATER)
    path = tmp_path / WORKSPACES_FILE_NAME
    path.write_text('{"schema_version": 1, "active": 0, "workspaces": []}', encoding="utf-8")
    store = a_store(tmp_path)

    loaded = store.load(SHIPPED)

    set_aside = tmp_path / f"workspaces.invalid-{STAMP}.json"
    assert loaded.workspaces == MINE
    assert loaded.source is Source.PREVIOUS
    assert loaded.writable
    assert loaded.set_aside == set_aside
    assert loaded.notice is not None
    assert "at least one Workspace" in loaded.notice
    assert str(set_aside) in loaded.notice and str(tmp_path / PREVIOUS_FILE_NAME) in loaded.notice
    assert (
        set_aside.read_text(encoding="utf-8")
        == '{"schema_version": 1, "active": 0, "workspaces": []}'
    )
    assert not path.exists()

    store.save(LATER)

    assert path.read_text(encoding="utf-8") == workspace_set_to_json(LATER)
    assert (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )
    assert set_aside.exists()


def test_an_invalid_file_with_no_previous_generation_falls_back_to_the_shipped_set(
    tmp_path: Path,
) -> None:
    (tmp_path / WORKSPACES_FILE_NAME).write_text(
        workspace_set_to_json(MINE)[:-40], encoding="utf-8"
    )

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.workspaces == SHIPPED
    assert loaded.source is Source.SHIPPED
    assert loaded.writable
    assert loaded.notice is not None
    assert "not JSON this build can read" in loaded.notice
    assert "the shipped Workspaces are shown" in loaded.notice
    assert entries(tmp_path) == [f"workspaces.invalid-{STAMP}.json"]


def test_two_files_set_aside_in_one_second_get_distinct_names(tmp_path: Path) -> None:
    (tmp_path / f"workspaces.invalid-{STAMP}.json").write_text("earlier", encoding="utf-8")
    (tmp_path / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.set_aside == tmp_path / f"workspaces.invalid-{STAMP}-1.json"
    assert loaded.set_aside.read_text(encoding="utf-8") == "not json"
    assert (tmp_path / f"workspaces.invalid-{STAMP}.json").read_text(encoding="utf-8") == "earlier"


def test_a_missing_current_file_with_a_previous_generation_rescues_it_and_says_so(
    tmp_path: Path,
) -> None:
    saved(tmp_path, MINE).save(LATER)
    (tmp_path / WORKSPACES_FILE_NAME).unlink()

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.workspaces == MINE
    assert loaded.source is Source.PREVIOUS
    assert loaded.writable
    assert loaded.notice is not None
    assert "Save as default" in loaded.notice
    assert entries(tmp_path) == [PREVIOUS_FILE_NAME]


def test_a_previous_generation_a_newer_build_wrote_turns_saving_off(tmp_path: Path) -> None:
    newer = json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1})
    (tmp_path / PREVIOUS_FILE_NAME).write_text(newer, encoding="utf-8")

    without_current = a_store(tmp_path).load(SHIPPED)

    (tmp_path / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")

    with_invalid_current = a_store(tmp_path).load(SHIPPED)

    assert (without_current.workspaces, without_current.writable) == (SHIPPED, False)
    assert without_current.notice == (
        f"there is no {tmp_path / WORKSPACES_FILE_NAME}, and {tmp_path / PREVIOUS_FILE_NAME} "
        f"was written at schema version {LAYOUT_SCHEMA_VERSION + 1} by a newer build, which "
        "the second save from this build would overwrite; the shipped Workspaces are shown "
        "and nothing will be saved this session"
    )
    assert with_invalid_current.workspaces == SHIPPED
    assert not with_invalid_current.writable
    assert with_invalid_current.set_aside is not None
    assert (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == newer


def test_an_invalid_previous_generation_is_left_where_it_is_and_named(tmp_path: Path) -> None:
    (tmp_path / PREVIOUS_FILE_NAME).write_text("also not json", encoding="utf-8")
    (tmp_path / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")

    with_invalid_current = a_store(tmp_path).load(SHIPPED)

    (tmp_path / loaded_name(with_invalid_current)).unlink()

    without_current = a_store(tmp_path).load(SHIPPED)

    for loaded in (with_invalid_current, without_current):
        assert (loaded.workspaces, loaded.source, loaded.writable) == (
            SHIPPED,
            Source.SHIPPED,
            True,
        )
        assert loaded.notice is not None
        assert f"{tmp_path / PREVIOUS_FILE_NAME} could not be used" in loaded.notice
        assert "left where it is" in loaded.notice

    assert (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == "also not json"


def loaded_name(loaded: store_module.Loaded) -> str:
    assert loaded.set_aside is not None

    return loaded.set_aside.name


def test_a_valid_file_beside_a_previous_generation_a_newer_build_wrote_turns_saving_off(
    tmp_path: Path,
) -> None:
    saved(tmp_path, MINE)
    newer = json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1})
    (tmp_path / PREVIOUS_FILE_NAME).write_text(newer, encoding="utf-8")
    store = a_store(tmp_path)

    loaded = store.load(SHIPPED)

    assert (loaded.workspaces, loaded.source, loaded.writable) == (MINE, Source.FILE, False)
    assert loaded.notice is not None
    assert str(tmp_path / PREVIOUS_FILE_NAME) in loaded.notice

    with pytest.raises(LayoutRefused, match="saving is off"):
        store.save(LATER)

    assert (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == newer


def test_a_failed_replace_leaves_the_current_file_and_removes_the_temporary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = saved(tmp_path, MINE)

    real_replace = os.replace

    def refuse_the_current_file(source: str, target: str) -> None:
        if Path(target).name == WORKSPACES_FILE_NAME:
            raise PermissionError(13, "refused for the test", target)

        real_replace(source, target)

    monkeypatch.setattr(os, "replace", refuse_the_current_file)

    with pytest.raises(WorkspaceFileError, match="could not replace") as raised:
        store.save(LATER)

    assert raised.value.path == tmp_path / WORKSPACES_FILE_NAME
    assert entries(tmp_path) == [WORKSPACES_FILE_NAME, PREVIOUS_FILE_NAME]
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )
    assert a_store(tmp_path).load(SHIPPED).workspaces == MINE


def test_a_previous_generation_that_cannot_be_written_is_the_path_the_error_names(
    tmp_path: Path,
) -> None:
    store = saved(tmp_path, MINE)
    (tmp_path / PREVIOUS_FILE_NAME).mkdir()

    with pytest.raises(WorkspaceFileError, match="could not copy the previous generation to"):
        store.save(LATER)

    try:
        store.save(LATER)
    except WorkspaceFileError as error:
        assert error.path == tmp_path / PREVIOUS_FILE_NAME

    assert entries(tmp_path) == [WORKSPACES_FILE_NAME, PREVIOUS_FILE_NAME]
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )


def test_a_directory_that_refuses_to_sync_has_still_saved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = saved(tmp_path, MINE)
    real_fsync = os.fsync

    def refuse(descriptor: int) -> None:
        raise OSError(22, "Invalid argument")

    monkeypatch.setattr(os, "fsync", refuse)

    with pytest.raises(WorkspaceFileError, match="could not write"):
        store.save(LATER)

    def refuse_directories(descriptor: int) -> None:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(22, "Invalid argument")

        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)

    assert store.save(LATER) == tmp_path / WORKSPACES_FILE_NAME
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        LATER
    )
    assert a_store(tmp_path).load(SHIPPED).workspaces == LATER


def test_a_file_that_is_not_utf8_is_invalid_and_set_aside(tmp_path: Path) -> None:
    (tmp_path / WORKSPACES_FILE_NAME).write_bytes(b"\xff\xfe not text")

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.source is Source.SHIPPED
    assert loaded.writable
    assert loaded.set_aside is not None
    assert loaded.set_aside.read_bytes() == b"\xff\xfe not text"


def test_an_unreadable_file_turns_saving_off_and_is_left_as_it_is(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The test injects a permission error instead of setting mode bits, which root ignores."""

    path = tmp_path / WORKSPACES_FILE_NAME
    text = workspace_set_to_json(MINE)
    path.write_text(text, encoding="utf-8")
    real_read_text = Path.read_text

    def refuse_the_current_file(self: Path, *arguments: object, **options: object) -> str:
        if self.name == WORKSPACES_FILE_NAME:
            raise PermissionError(13, "Permission denied", str(self))

        return real_read_text(self, *arguments, **options)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "read_text", refuse_the_current_file)
    store = a_store(tmp_path)

    loaded = store.load(SHIPPED)

    assert (loaded.workspaces, loaded.source, loaded.writable) == (SHIPPED, Source.SHIPPED, False)
    assert loaded.notice is not None
    assert "could not be read" in loaded.notice and "Permission denied" in loaded.notice

    with pytest.raises(LayoutRefused, match="saving is off"):
        store.save(MINE)

    assert entries(tmp_path) == [WORKSPACES_FILE_NAME]
    assert real_read_text(path, encoding="utf-8") == text


def test_an_unwritable_directory_is_reported_at_save_and_leaves_nothing_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The test injects a refused write instead of setting mode bits, which root ignores."""

    store = saved(tmp_path, MINE)
    pending = tmp_path / PENDING_FILE_NAME

    def refuse(path: Path, text: str) -> None:
        raise PermissionError(13, "Permission denied", str(path))

    monkeypatch.setattr(store_module, "_write_synced", refuse)

    with pytest.raises(WorkspaceFileError, match="could not write") as raised:
        store.save(LATER)

    assert raised.value.path == pending
    assert isinstance(raised.value.error, PermissionError)
    assert entries(tmp_path) == [WORKSPACES_FILE_NAME]
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )


def test_a_directory_that_cannot_be_created_is_reported_at_save(tmp_path: Path) -> None:
    blocking_file = tmp_path / "state"
    blocking_file.write_text("a file where the directory should go", encoding="utf-8")
    store = a_store(blocking_file / "inside")
    store.load(SHIPPED)

    with pytest.raises(WorkspaceFileError, match="could not create the directory") as raised:
        store.save(MINE)

    assert raised.value.path == blocking_file / "inside"


def test_the_pre_migration_file_is_kept_once_at_the_first_save(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved(tmp_path, MINE)
    monkeypatch.setattr(store_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1)
    store = a_store(tmp_path)
    loaded = store.load(SHIPPED)

    assert loaded.written_at == LAYOUT_SCHEMA_VERSION

    store.save(LATER)
    kept = tmp_path / kept_file_name(LAYOUT_SCHEMA_VERSION)

    assert kept.read_text(encoding="utf-8") == workspace_set_to_json(MINE)

    store.save(MINE)

    assert kept.read_text(encoding="utf-8") == workspace_set_to_json(MINE)
    assert entries(tmp_path) == [WORKSPACES_FILE_NAME, PREVIOUS_FILE_NAME, kept.name]


def test_a_file_name_cannot_name_a_version_or_an_attempt_that_does_not_exist() -> None:
    """Before `PL-8JV2`, a version or an attempt that cannot exist still produced a file name.

    `kept_file_name(True)` wrote `workspaces.vTrue.json`, and attempt -1 put a `--` in the name.
    """

    with pytest.raises(TypeError, match="a schema version is an int, not bool"):
        kept_file_name(True)  # type: ignore[arg-type]

    with pytest.raises(InvalidLayout, match="a schema version counts from 1, not 0"):
        kept_file_name(0)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="an attempt counts from 0, not -1"):
        set_aside_file_name(MOMENT, -1)

    with pytest.raises(TypeError, match="an attempt is an int, not bool"):
        set_aside_file_name(MOMENT, True)

    assert kept_file_name(SchemaVersion(2)) == "workspaces.v2.json"


def test_the_file_names_are_the_documented_ones() -> None:
    assert set_aside_file_name(MOMENT) == f"workspaces.invalid-{STAMP}.json"
    assert set_aside_file_name(MOMENT, 2) == f"workspaces.invalid-{STAMP}-2.json"
    assert (
        set_aside_file_name(datetime(2026, 10, 17, 0, 0, tzinfo=UTC).astimezone())
        == "workspaces.invalid-20261017T000000Z.json"
    )
    assert kept_file_name(1) == "workspaces.v1.json"
    assert (PREVIOUS_FILE_NAME, PENDING_FILE_NAME) == (
        "workspaces.json.previous",
        "workspaces.json.tmp",
    )


def test_the_user_directory_is_the_override_where_set_and_the_platforms_otherwise(
    tmp_path: Path,
) -> None:
    assert user_data_directory("/platform/app", {}) == Path("/platform/app")
    assert user_data_directory("/platform/app", {USER_DIRECTORY_VARIABLE: ""}) == Path(
        "/platform/app"
    )
    assert (
        user_data_directory("/platform/app", {USER_DIRECTORY_VARIABLE: str(tmp_path)}) == tmp_path
    )
    assert user_data_directory("", {USER_DIRECTORY_VARIABLE: str(tmp_path)}) == tmp_path

    with pytest.raises(
        LayoutRefused,
        match=f"no application data location and {USER_DIRECTORY_VARIABLE} is unset or empty",
    ):
        user_data_directory("", {})


def test_a_first_save_creates_every_missing_level_of_the_directory(tmp_path: Path) -> None:
    directory = tmp_path / "Open Anesthesia Simulator" / "state"
    store = a_store(directory)
    store.load(SHIPPED)

    assert store.save(MINE) == directory / WORKSPACES_FILE_NAME
    assert store.directory == directory
    assert a_store(directory).load(SHIPPED).workspaces == MINE


def test_a_lossy_migration_is_told_to_the_reader_at_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved(tmp_path, MINE)

    def fake_migrate(body: dict[str, object], written_at: int) -> Migrated:
        return Migrated(body, ("which tab was open was not kept",))

    monkeypatch.setattr(serialization_module, "migrate", fake_migrate)

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.workspaces == MINE
    assert loaded.notice is not None
    assert "which tab was open was not kept" in loaded.notice
    assert f"written at schema version {LAYOUT_SCHEMA_VERSION}" in loaded.notice


def test_a_rescued_previous_generation_an_older_build_wrote_is_kept_at_the_first_save(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved(tmp_path, MINE).save(LATER)
    (tmp_path / WORKSPACES_FILE_NAME).unlink()
    previous_text = (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8")
    monkeypatch.setattr(store_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1)
    store = a_store(tmp_path)

    loaded = store.load(SHIPPED)

    assert (loaded.source, loaded.written_at) == (Source.PREVIOUS, LAYOUT_SCHEMA_VERSION)

    store.save(LATER)

    assert (tmp_path / kept_file_name(LAYOUT_SCHEMA_VERSION)).read_text(
        encoding="utf-8"
    ) == previous_text
    assert (tmp_path / PREVIOUS_FILE_NAME).read_text(encoding="utf-8") == previous_text


def test_a_pre_migration_copy_that_cannot_be_written_is_the_path_the_error_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    saved(tmp_path, MINE)
    monkeypatch.setattr(store_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1)
    kept = tmp_path / kept_file_name(LAYOUT_SCHEMA_VERSION)
    real_copyfile = shutil.copyfile

    def refuse_the_kept_copy(source: Path, target: Path, **options: object) -> Path:
        if Path(target).name == kept.name:
            raise PermissionError(13, "Permission denied", str(target))

        return real_copyfile(source, target, **options)  # type: ignore[arg-type]

    monkeypatch.setattr(shutil, "copyfile", refuse_the_kept_copy)
    store = a_store(tmp_path)
    store.load(SHIPPED)

    with pytest.raises(
        WorkspaceFileError, match="could not keep the pre-migration file as"
    ) as raised:
        store.save(LATER)

    assert raised.value.path == kept
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        MINE
    )


def test_a_previous_generation_that_is_not_text_is_named_in_the_notice(tmp_path: Path) -> None:
    (tmp_path / PREVIOUS_FILE_NAME).write_bytes(b"\xff\xfe")

    loaded = a_store(tmp_path).load(SHIPPED)

    assert (loaded.workspaces, loaded.writable) == (SHIPPED, True)
    assert loaded.notice is not None
    assert "could not be used (it is not UTF-8 text" in loaded.notice


def test_a_set_aside_name_is_written_in_utc_whatever_zone_the_clock_gives() -> None:
    central = datetime(2026, 10, 17, 0, 0, tzinfo=timezone(timedelta(hours=-5)))

    assert set_aside_file_name(central) == f"workspaces.invalid-{STAMP}.json"


def decided(loaded: store_module.Loaded) -> tuple[object, ...]:
    """Return every field of a launch's result except its notice, in the order `Loaded` has them."""

    return (loaded.workspaces, loaded.source, loaded.writable, loaded.set_aside, loaded.written_at)


def test_an_invalid_file_that_cannot_be_set_aside_turns_saving_off_and_is_left_as_it_is(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An invalid file that stays in place would be overwritten by a save, so saving is off.

    The shipped set is shown, and the file is not touched. The notice gives the
    reason the file was refused and the reason it could not be moved. The test
    makes the rename fail itself, instead of setting mode bits, which root
    ignores.
    """

    path = tmp_path / WORKSPACES_FILE_NAME
    path.write_text("not json", encoding="utf-8")
    refusal = PermissionError(13, "Permission denied", str(path))

    def refuse(source: object, target: object) -> None:
        raise refusal

    monkeypatch.setattr(os, "rename", refuse)

    with pytest.raises(LayoutFormatError) as invalid:
        workspace_set_from_json("not json")

    store = a_store(tmp_path)
    loaded = store.load(SHIPPED)

    assert loaded == store_module.Loaded(
        SHIPPED,
        Source.SHIPPED,
        False,
        f"{path} is not a Workspace file this build reads ({invalid.value}), and could not be "
        f"set aside ({refusal}), so the shipped Workspaces are shown and nothing will be saved "
        "this session; the file is left as it is",
        None,
        None,
    )

    with pytest.raises(LayoutRefused, match="saving is off for this session"):
        store.save(MINE)

    assert entries(tmp_path) == [WORKSPACES_FILE_NAME]
    assert path.read_text(encoding="utf-8") == "not json"


def test_a_file_that_is_not_utf8_text_shows_the_shipped_set_and_says_why(tmp_path: Path) -> None:
    """A file that is not UTF-8 text is set aside, and the notice says why the shipped set is shown.

    The reason in the notice is the one that Python's own UTF-8 decoder gives
    for the same bytes.
    """

    written = b"\xff\xfe not text"
    path = tmp_path / WORKSPACES_FILE_NAME
    path.write_bytes(written)

    with pytest.raises(UnicodeDecodeError) as undecodable:
        written.decode("utf-8")

    loaded = a_store(tmp_path).load(SHIPPED)

    set_aside = tmp_path / f"workspaces.invalid-{STAMP}.json"
    assert loaded == store_module.Loaded(
        SHIPPED,
        Source.SHIPPED,
        True,
        f"{path} is not a Workspace file this build reads (the file is not UTF-8 text: "
        f"{undecodable.value}); it was set aside unchanged as {set_aside}, and the shipped "
        "Workspaces are shown",
        set_aside,
        None,
    )


def test_the_notice_for_a_rescued_previous_generation_says_only_what_happened(
    tmp_path: Path,
) -> None:
    """When no migration step lost anything, the notice says which file is shown and no more.

    The previous generation is rescued in two cases: when there is no current
    file, and when the current file was set aside. Each result also gives the
    version that the previous generation was written at. A save needs that
    version to keep a pre-migration copy of a file that an older build wrote.
    """

    missing = tmp_path / "missing"
    saved(missing, MINE).save(LATER)
    (missing / WORKSPACES_FILE_NAME).unlink()
    invalid = tmp_path / "invalid"
    saved(invalid, MINE).save(LATER)
    (invalid / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")

    with pytest.raises(LayoutFormatError) as refused:
        workspace_set_from_json("not json")

    without_current = a_store(missing).load(SHIPPED)
    with_invalid_current = a_store(invalid).load(SHIPPED)

    set_aside = invalid / f"workspaces.invalid-{STAMP}.json"
    assert without_current == store_module.Loaded(
        MINE,
        Source.PREVIOUS,
        True,
        f"there is no {missing / WORKSPACES_FILE_NAME}, so the previous default, "
        f'{missing / PREVIOUS_FILE_NAME}, is shown; "Save as default" keeps it',
        None,
        LAYOUT_SCHEMA_VERSION,
    )
    assert with_invalid_current == store_module.Loaded(
        MINE,
        Source.PREVIOUS,
        True,
        f"{invalid / WORKSPACES_FILE_NAME} is not a Workspace file this build reads "
        f"({refused.value}); it was set aside unchanged as {set_aside}, and the previous "
        f"default, {invalid / PREVIOUS_FILE_NAME}, is shown",
        set_aside,
        LAYOUT_SCHEMA_VERSION,
    )


def test_a_lossy_migration_is_told_to_the_reader_whichever_file_is_shown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every notice about a migrated file ends with what each lossy step could not keep.

    The test covers the three launches that show a migrated file with a notice
    of their own: a previous generation rescued because there is no current
    file, one rescued because the current file was set aside, and a current
    file shown beside a previous generation that a newer build wrote. Two lossy
    steps show that their sentences are joined in order, separated by a space.
    """

    missing = tmp_path / "missing"
    saved(missing, MINE).save(LATER)
    (missing / WORKSPACES_FILE_NAME).unlink()
    invalid = tmp_path / "invalid"
    saved(invalid, MINE).save(LATER)
    (invalid / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")
    beside_newer = tmp_path / "beside_newer"
    saved(beside_newer, MINE)
    (beside_newer / PREVIOUS_FILE_NAME).write_text(
        json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1}), encoding="utf-8"
    )

    def fake_migrate(body: dict[str, object], written_at: int) -> Migrated:
        return Migrated(body, ("Which tab was open was not kept.", "Each chart's zoom was reset."))

    monkeypatch.setattr(serialization_module, "migrate", fake_migrate)

    told = (
        f"; the saved Workspaces were written at schema version {LAYOUT_SCHEMA_VERSION} and were "
        f"brought to version {LAYOUT_SCHEMA_VERSION}: Which tab was open was not kept. Each "
        "chart's zoom was reset."
    )

    for directory in (missing, invalid, beside_newer):
        notice = a_store(directory).load(SHIPPED).notice

        assert notice is not None and notice.endswith(told), directory.name


def test_each_launch_that_finds_a_newer_builds_file_names_it_and_turns_saving_off(
    tmp_path: Path,
) -> None:
    """A newer build's file, current or previous, turns saving off and is named in the notice.

    A save from this build would overwrite that file, which is the reader's work.
    The shipped set is shown in every case but one. A valid current file beside a
    newer previous generation is shown as written, with the version it was
    written at.
    """

    newer = json.dumps({"schema_version": LAYOUT_SCHEMA_VERSION + 1})
    current_newer = tmp_path / "current_newer"
    current_newer.mkdir()
    (current_newer / WORKSPACES_FILE_NAME).write_text(newer, encoding="utf-8")
    previous_newer = tmp_path / "previous_newer"
    previous_newer.mkdir()
    (previous_newer / PREVIOUS_FILE_NAME).write_text(newer, encoding="utf-8")
    invalid_current = tmp_path / "invalid_current"
    invalid_current.mkdir()
    (invalid_current / PREVIOUS_FILE_NAME).write_text(newer, encoding="utf-8")
    (invalid_current / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")
    valid_current = tmp_path / "valid_current"
    saved(valid_current, MINE)
    (valid_current / PREVIOUS_FILE_NAME).write_text(newer, encoding="utf-8")
    cases = (
        (current_newer, WORKSPACES_FILE_NAME, (SHIPPED, Source.SHIPPED, False, None, None)),
        (previous_newer, PREVIOUS_FILE_NAME, (SHIPPED, Source.SHIPPED, False, None, None)),
        (
            invalid_current,
            PREVIOUS_FILE_NAME,
            (
                SHIPPED,
                Source.SHIPPED,
                False,
                invalid_current / f"workspaces.invalid-{STAMP}.json",
                None,
            ),
        ),
        (
            valid_current,
            PREVIOUS_FILE_NAME,
            (MINE, Source.FILE, False, None, LAYOUT_SCHEMA_VERSION),
        ),
    )

    for directory, newer_file, expected in cases:
        loaded = a_store(directory).load(SHIPPED)

        assert decided(loaded) == expected, directory.name
        assert loaded.notice is not None, directory.name
        assert (
            f"{directory / newer_file} was written at schema version {LAYOUT_SCHEMA_VERSION + 1} "
            "by a newer build"
        ) in loaded.notice, directory.name


def test_a_store_given_no_clock_names_a_set_aside_file_for_the_moment_it_was_set_aside(
    tmp_path: Path,
) -> None:
    """The application builds its store without a clock, so the store reads the time itself.

    The set-aside file's name must give one of the UTC seconds that passed
    while the file was loaded.
    """

    (tmp_path / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")
    before = datetime.now(UTC).replace(microsecond=0)

    loaded = WorkspaceStore(tmp_path).load(SHIPPED)

    after = datetime.now(UTC)
    seconds = range(int((after - before).total_seconds()) + 1)
    assert loaded.set_aside is not None
    assert loaded.set_aside.name in {
        f"workspaces.invalid-{before + timedelta(seconds=second):%Y%m%dT%H%M%SZ}.json"
        for second in seconds
    }


#: A zone five hours behind UTC, as New York's is in winter.
FIVE_HOURS_BEHIND_UTC = timezone(timedelta(hours=-5))


class MomentOnAMachineFiveHoursBehindUtc(datetime):
    """A moment read on a machine whose own zone is five hours behind UTC.

    A `datetime` converts to the machine's own zone when `astimezone` is
    called with no zone. In that case this stand-in converts to five hours
    behind UTC, as such a machine does. Changing the process's real zone needs
    `time.tzset`, which Windows lacks, so the stand-in lets the test run on
    every platform.
    """

    def astimezone(self, tz: tzinfo | None = None) -> Self:
        return super().astimezone(FIVE_HOURS_BEHIND_UTC if tz is None else tz)


def test_a_set_aside_name_is_written_in_utc_whatever_the_machines_own_zone_is() -> None:
    """A machine five hours behind UTC still names the file for the UTC time.

    The test first checks that the stand-in moves the moment five hours
    behind UTC where no zone is named, so a name written in the machine's own
    zone would fail it.
    """

    moment = MomentOnAMachineFiveHoursBehindUtc.fromtimestamp(MOMENT.timestamp(), UTC)

    assert moment.astimezone().utcoffset() == timedelta(hours=-5)
    assert set_aside_file_name(moment) == f"workspaces.invalid-{STAMP}.json"


def test_three_files_set_aside_in_one_second_get_three_distinct_names(tmp_path: Path) -> None:
    """With two names in that second already taken, the third file is numbered 2.

    With only one earlier file, a store that always tried the number 1 next
    would pass too.
    """

    first = tmp_path / f"workspaces.invalid-{STAMP}.json"
    second = tmp_path / f"workspaces.invalid-{STAMP}-1.json"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    (tmp_path / WORKSPACES_FILE_NAME).write_text("third", encoding="utf-8")

    loaded = a_store(tmp_path).load(SHIPPED)

    assert loaded.set_aside == tmp_path / f"workspaces.invalid-{STAMP}-2.json"
    assert loaded.set_aside.read_text(encoding="utf-8") == "third"
    assert (first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8")) == (
        "first",
        "second",
    )


def test_a_pre_migration_copy_that_already_exists_is_never_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pre-migration file is kept once, so a copy already in place is left as it is.

    The current file can be at the older version while its copy exists. That
    happens, for example, when the reader puts back an older file by hand.
    """

    saved(tmp_path, MINE)
    monkeypatch.setattr(store_module, "LAYOUT_SCHEMA_VERSION", LAYOUT_SCHEMA_VERSION + 1)
    kept = tmp_path / kept_file_name(LAYOUT_SCHEMA_VERSION)
    kept.write_text("the copy an earlier save kept", encoding="utf-8")
    store = a_store(tmp_path)
    store.load(SHIPPED)

    store.save(LATER)

    assert kept.read_text(encoding="utf-8") == "the copy an earlier save kept"
    assert (tmp_path / WORKSPACES_FILE_NAME).read_text(encoding="utf-8") == workspace_set_to_json(
        LATER
    )


def test_after_a_save_the_store_reports_the_saved_set_as_the_file_it_shows(tmp_path: Path) -> None:
    """`loaded` after a save describes the file just written, at this build's version.

    Nothing is left to tell the reader, and saving stays on. The path that an
    invalid file was set aside to at launch is still given.
    """

    (tmp_path / WORKSPACES_FILE_NAME).write_text("not json", encoding="utf-8")
    store = a_store(tmp_path)
    store.load(SHIPPED)

    store.save(MINE)

    assert store.loaded == store_module.Loaded(
        MINE,
        Source.FILE,
        True,
        None,
        tmp_path / f"workspaces.invalid-{STAMP}.json",
        LAYOUT_SCHEMA_VERSION,
    )
