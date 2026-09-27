---
id: PL-SSQW
title: Decide the saved-workspace file - where it lives, how it is written, what a first run with no file does, and what a build does with a schema_version it does not support
priority: P2
effort: M
status: blocked
classes: planning
feature: interface-areas
blocked-by: PL-1FT6
touches: docs/ARCHITECTURE.md
added: 2026-09-16
recurrences: 2026-09-20 PL-ZW0J
---

**Problem.** Decide the saved-workspace file - where it lives, how it is written, what a first run with no file does, and what a build does with a schema_version it does not support

**Problem.** `PL-C842` settled that the `LayoutModel` serializes to versioned JSON, and `ROADMAP.md` item 34 makes a workspace the learner's "to customize and save rather than a fixed set shipped with the application". Nothing says what the version number *does*. Three cases are open and they want different answers: a file written by an **older** build after the schema changes; a file written by a **newer** build, which a learner reaches by upgrading and rolling back, or by copying a workspace between machines; and a file at the supported version whose tree is structurally invalid — a pane with two views, a split whose sizes do not match its children, a truncated write. The only precedent in the tree is `src/anesthesia_sim/core/parameters.py:278`, whose `_validate_schema_version` supports exactly one version and raises `unsupported schema_version: {value}; expected {SUPPORTED_SCHEMA_VERSION}` for everything else. That is correct for the shipped agent, patient and machine data files, which travel with the code and can never be ahead of it. Transplanted to a file the learner wrote, it deletes work that cannot be regenerated, which is why the rule has to be decided rather than inherited.

**Why it matters.** A missing policy is not a neutral state: it resolves, at the first `from_dict`, into whatever the implementing session found natural, and the two natural answers are both the failure shape this project has already refused twice. Ignoring an unrecognised version and reading the file anyway is `QSplitter.restoreState()` returning `True` on a mismatched tree — "a plausible-looking wrong layout" rather than a failure. Refusing everything is the shipped-data rule applied to user data, and it discards the learner's induction and maintenance workspaces on an upgrade with no way back. Blender's own answer covers only the newer-file case and covers it at file level, so the precedent runs out here exactly as `docs/interface-provenance.md` records. The migration half is the part that expires: once a build has written v1 into a learner's profile, a v2 that cannot read it is a decision already taken.

**Done when.** A written policy in `docs/ARCHITECTURE.md` (or the layout module's own docstring, wherever the format is specified) answers all three cases by name — older, newer, and invalid-at-the-supported-version — saying for each whether the file is migrated, refused, or set aside and replaced by a default, and what the learner is told. Migration, where it is the answer, names who owns the migrating code and whether the pre-migration file is kept. The policy is exercised by unit tests over `LayoutModel.from_dict` alone, with no `QApplication`, including a fixture file one version ahead of the build.

*Basis (lens `persistence`).* `PL-C842`'s recommendation fixes the format and not its policy: "**`LayoutModel`** - pure Python, no Qt import. A tree of `Split(orientation, children, sizes)` and `Pane(pane_id, view_kind)`, with `split`, `join`, `resize`, `swap`, and versioned JSON serialization" (docs/items/PL-C842-decide-whether-the-layout-container-sits-behind.md, § "RECOMMENDATION 2026-09-16"). The one behaviour Blender supplies for the same case is recorded as insufficient: its forward-compatibility notice is "a **file-level** one: it says data may have been lost, never that this pane is now showing something other than what was saved" (docs/interface-provenance.md, § "Persistence, and what happens when an editor is missing").

**Problem.** Every decided piece of the persistence story assumes a file and none of them says where it is or how it gets there. `PL-CNJ1` measured the current position on 2026-09-15: a grep for `.write_text`, `.write_bytes`, `open(..., "w"/"a"/"x")`, `.mkdir(`, `json.dump`, `csv.writer`, `QSettings` and `QStandardPaths` across `src/` "returns zero hits", and the shipped data files are read through `importlib.resources` (`src/anesthesia_sim/core/parameters.py:733`). So the application has no user-data directory, no write path and no convention for one. Four things are undecided: the per-platform location of the learner's workspaces; the write discipline, where a truncate-in-place save interrupted mid-run leaves a partial JSON the next launch has to classify; what a first run with no file does, and whether the shipped defaults live in the tree beside `src/anesthesia_sim/data/` as validated JSON; and how tests exercise saving without writing outside `tmp_path`, which is the standard `PL-CNJ1` established.

**Why it matters.** This is the decision that is cheapest before any code exists and awkward afterwards, because the path a build ships becomes the path a learner's saved layouts are already at. It also feeds two decisions already taken. Item 34 copies Blender's refusal to delete the last workspace — "a floor it enforces structurally rather than by warning" — which needs a shipped set that can be restored and therefore a location for it. And a torn write is the third case in the schema-version policy: without an atomic replace, the loader meets truncated files routinely rather than never, which changes what that policy has to be lenient about. Writing outside the tree for the first time also touches packaging and the import boundary that `tools/import_boundary_check.py` already polices.

**Done when.** The layout module's documented interface names the workspace directory and how it is resolved per platform, including the override a test or a headless run uses; the save path is an atomic write; the behaviour with no file, an unreadable file and an unwritable directory is specified and tested; the shipped default workspaces have a home in the tree as validated versioned JSON like every other shipped parameter; and `docs/ARCHITECTURE.md` records that the application now writes user state, so the next session does not re-derive `PL-CNJ1`'s "writes nothing" measurement as still true.

*Basis (lens `persistence`).* `ROADMAP.md` planned-milestone item 34 requires "task-oriented layout presets the learner can switch between, customize and save", and `PL-C842` assumes a shipped set alongside them: "Shipped default workspaces would be binary blobs in a tree where every other shipped parameter is a validated, versioned JSON file" (docs/items/PL-C842-decide-whether-the-layout-container-sits-behind.md).

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Two of
them are learner-visible (the newer-file answer, and what an invalid file
does) and are the owner's to take; the rest are architecture under the
delegated call and are taken here unless the owner objects.

**Q1. Where the file lives, per platform.**
**Recommendation:** the directory Qt reports for
`QStandardPaths.AppDataLocation`, resolved **once, in `app/main.py`**, after
`main` sets the organization and application names it does not set today
(`src/anesthesia_sim/app_metadata.py` already holds `APP_AUTHOR` and
`APP_BUNDLE_ID`, neither read by `main`). Qt's own table, read at the source
(`src/corelib/io/qstandardpaths.cpp`, qt/qtbase, 2026-09-27): macOS
`~/Library/Application Support/<App>`, Windows `%APPDATA%\<Org>\<App>`
(Roaming), Linux `~/.local/share/<App>`. Roaming rather than Local on Windows
because the file is machine-independent by design (`PL-HJPY`: sizes are
fractions, no window geometry). **The layout package never resolves a path:**
its store takes a directory, `WorkspaceStore(directory: Path)`, so a test
passes `tmp_path` and a headless run passes whatever it likes, which keeps
`PL-CNJ1`'s standard. One environment override, `ANESTHESIA_SIM_USER_DIR`,
read in `main.py` only, for a headless or portable run. *Alternatives
refused:* a `platformdirs` dependency (a third package for a table Qt already
carries, and it disagrees with Qt on macOS's config directory); a hand-rolled
table (the same table, maintained twice). Blender's version-numbered
directory (`BKE_appdir_folder_id_ex(BLENDER_USER_CONFIG)` in
`source/blender/blenkernel/intern/appdir.cc`) is **not** adopted: Blender
separates each release's config because its preferences are not forward
compatible, and this file carries a `schema_version` for exactly that job.

**Q2. One file or one per Workspace.** **Recommendation: one file,
`workspaces.json`, holding the whole `WorkspaceSet`** - order, active tab,
the last-Workspace floor - as one document, because the invariants are
properties of the set (never empty, one active, names unique) and a directory
of files cannot state them. Per-Workspace files are refused for that reason;
export of one Workspace, if ever wanted, is a later item.

**Q3. Write discipline.** **Recommendation: atomic replace with one previous
generation.** Write `workspaces.json.tmp` in the same directory, `flush()`
then `os.fsync()`, `os.replace()` over the target (atomic on POSIX and, unlike
`os.rename()`, allowed to replace an existing file on Windows; CPython
`Doc/library/os.rst`, read 2026-09-27), fsync the directory on POSIX, and
remove the temp file on any failure. Before the replace, rename the current
file to `workspaces.json.previous`, so one prior generation survives a bad
write of the new one. Blender's `writefile.cc` does the same dance (writes
`<file>@`, `BLI_rename_overwrite`, `remove()` on failure, `do_history()` for
the `.blend1` copies). The file is written only by the reader's own action - "Save as default"
and the reset actions (`PL-WV9K` Q3 and Q4, project owner 2026-09-27) - so a
torn file arrives only through a crash mid-replace, which the OS guarantees
leaves either file whole. [The recommendation here was a debounced automatic
save; superseded 2026-09-27 by the owner's explicit save.]

**Q4. First run, and the shipped defaults' home.** **Recommendation:** no
file means the shipped set is loaded from
`src/anesthesia_sim/data/workspaces/*.json` (`PL-KXTL` carries their
content), validated by the same `from_dict` as a learner's file, and
**nothing is written until the first "Save as default"**; the directory is
created on the first write. A first run leaves no trace, and a learner who
never saves a default never has a file to migrate.

**Q5. The schema-version policy: three cases by name.**

- *Older than supported.* **Recommendation: migrate in memory, one step per
  version, in `layout/migrations.py`, owned by the layout package** and added
  in the same change as the bump that needs it; at version 1 the table of
  steps is empty and the hook exists so the first bump has somewhere to go.
  The migrated set is written at the next save, and the pre-migration file is
  kept once as `workspaces.v<N>.json`. The learner is told only when a step is
  lossy (a step declares whether it is), never for a clean one.
- *Newer than supported.* **Recommendation (learner-visible, owner's
  call): refuse it, touch nothing, show the shipped defaults, and make
  persistence read-only for the session**, with a persistent notice in the
  interface naming the file's path, its version and this build's. The file
  the newer build wrote is the learner's work, and a roll-back that
  overwrote it would be the deletion this item exists to refuse.
  *Alternative recorded:* set it aside under a dated name and start fresh
  with persistence on; refused because it moves the learner's file without
  being asked, for the benefit of a session that can equally run read-only.
- *Invalid at the supported version.* **Recommendation:** `from_dict`
  raises `LayoutFormatError` naming the invariant that failed (an Area with
  two Views, sizes that do not match children, truncated JSON, an empty
  window list); the store sets the file aside as
  `workspaces.invalid-<UTC timestamp>.json`, loads `workspaces.json.previous`
  if it validates and the shipped defaults otherwise, says so visibly, and
  persistence continues, because the set-aside file is untouched evidence
  and the next save cannot damage it. **An unknown View kind is not a file
  error**: it is `PL-R1WQ`'s per-Area failure state, and the file loads.

**Q6. Unreadable file, unwritable directory.** Unreadable (permissions,
I/O error): treated as the newer-file case - defaults, notice, read-only
session - since nothing can be known about it. Unwritable directory: the
session continues, and "Save as default" reports the failure and why where
it was invoked, since the reader asked for that write.

**Q7. Tests.** All policy cases are unit tests over `from_dict` and the
store against `tmp_path` with no `QApplication`, including a fixture one
version ahead of the build, a truncated file, a `.previous` that rescues an
invalid current file, and a read-only directory (skipped where the test runs
as root, which cannot be denied a write).

**Q8. The record.** `docs/ARCHITECTURE.md` gains a short "user state" entry
naming the file, the directory rule and the policy above, replacing
`PL-CNJ1`'s "writes nothing" as the current measurement, and
`tools/import_boundary_check.py` is told the layout package may import
`os`/`json`/`pathlib` and nothing from Qt.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names), including the learner-visible
newer-file answer (refuse, touch nothing, read-only session with a notice).
The one decision the owner specified otherwise is `PL-WV9K` Q4: layouts are
written by an explicit "Save as default" action, never automatically, so Q3,
Q4 and Q6 above were reworded to match on the same day. A migrated older file
(Q5) is therefore rewritten at the reader's next "Save as default", not
before, and the pre-migration copy is kept at that moment. **Open on
2026-09-27:** whether reopening also restores the last state automatically
(`PL-WV9K` § "Answers 2026-09-27", reading B, recommended there); if so, the
file gains a last-state section written automatically and atomically on
change, and the wording of Q3, Q4 and Q6 applies to the default section
only.
